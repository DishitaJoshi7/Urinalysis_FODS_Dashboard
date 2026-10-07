"""Join the user's laboratory workbook to public NHANES diabetes data and evaluate classifiers."""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (roc_auc_score, average_precision_score, accuracy_score,
    balanced_accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, brier_score_loss)
from core import ROOT, DATA_PATH, read_workbook

# Whitelisting features prevents questionnaire answers or IDs leaking the target.
TARGET = 'DIABETES_REPORTED'
DEMOGRAPHIC = ['RIDAGEYR', 'SEX_FEMALE', 'BMXBMI']
LAB_FEATURES = ['URDACT', 'URXUCR', 'LBXWBCSI', 'LBXHGB', 'LBXPLTSI', 'LBXRDW', 'LBXMCVSI']
FEATURES = DEMOGRAPHIC + LAB_FEATURES
STATUS_LABELS = {1: 'Reported diabetes', 0: 'No reported diabetes'}
LABELS = {'RIDAGEYR':'Age (years; 80 means 80+)', 'RIAGENDR':'Recorded sex (1 male, 2 female)',
    'SEX_FEMALE':'Recorded sex (0 male, 1 female)', 'BMXBMI':'Body mass index (kg/m²)',
    'DIQ010':'Doctor-told diabetes response code', TARGET:'Reported diabetes (0 no, 1 yes)',
    'STATUS':'Reported diabetes status', 'SDMVSTRA':'Survey stratum', 'SDMVPSU':'Survey PSU',
    'WTMEC2YR':'Two-year examination weight'}


def derive_target(response):
    """Code 1 is positive, code 2 negative; borderline/unknown are not forced negative."""
    return response.map({1: 1, 2: 0})


def load_diabetes():
    """Left-join on unique SEQN; original laboratory measurements are never overwritten."""
    sheets, labels = read_workbook()
    base = sheets['Merged_Dataset']
    joined = base.copy()
    fields = {'DIQ_J':['DIQ010'],
        'DEMO_J':['RIDAGEYR','RIAGENDR','WTMEC2YR','SDMVSTRA','SDMVPSU'],
        'BMX_J':['BMXBMI']}
    audit = []
    for name, columns in fields.items():
        frame = pd.read_sas(ROOT/'data'/'nhanes'/f'{name}.xpt',format='xport')[['SEQN']+columns]
        if not frame.SEQN.is_unique or frame.SEQN.isna().any():
            raise ValueError(f'{name}: invalid respondent identifiers.')
        frame.SEQN = frame.SEQN.astype('int64')
        matched = base.SEQN.isin(frame.SEQN)
        audit.append({'Source':name,'Source rows':len(frame),'Matched IDs':int(matched.sum()),
                      'Unmatched lab IDs':int((~matched).sum())})
        joined = joined.merge(frame,on='SEQN',how='left',validate='one_to_one')
    joined['SEX_FEMALE'] = joined.RIAGENDR.map({1:0.,2:1.})
    joined[TARGET] = derive_target(joined.DIQ010)
    joined['STATUS'] = joined[TARGET].map(STATUS_LABELS).fillna('Excluded / unclassified')
    adults = joined.loc[joined.RIDAGEYR.ge(20)].copy()
    eligible = adults.loc[adults[TARGET].notna()].copy()
    eligible[TARGET] = eligible[TARGET].astype(int)
    flow = pd.DataFrame([
        ('Original matched laboratory respondents',len(base)),
        ('Excluded: age below 20 or unavailable',len(joined)-len(adults)),
        ('Adults aged 20+',len(adults)),
        ('Excluded adults: borderline response',int(adults.DIQ010.eq(3).sum())),
        ('Excluded adults: refused / unknown / missing response',int((~adults.DIQ010.isin([1,2,3])).sum())),
        ('Eligible adults with yes/no response',len(eligible)),
        ('Reported diabetes',int(eligible[TARGET].sum())),
        ('No reported diabetes',int(eligible[TARGET].eq(0).sum()))],columns=['Cohort step','Records'])
    labels.update(LABELS)
    # Full source joins retain weights for auditing, but this project uses unweighted sample analysis.
    return dict(eligible=eligible,joined=joined,sheets=sheets,labels=labels,
                join_audit=pd.DataFrame(audit),flow=flow)


def split_cohort(df):
    """Freeze stratified 60/20/20 splits before fitting any imputers or scalers."""
    train_val, test = train_test_split(df,test_size=.2,stratify=df[TARGET],random_state=42)
    train, validation = train_test_split(train_val,test_size=.25,stratify=train_val[TARGET],random_state=42)
    return {'train':train.copy(),'validation':validation.copy(),'test':test.copy()}


def build_pipeline(estimator):
    """Preprocessing is learned only on training rows and reused for validation/test."""
    return Pipeline([('imputer',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),
        ('scaler',StandardScaler()),('classifier',estimator)])


def evaluate(y, scores, threshold):
    """Positive class is the reported-diabetes response, not a clinical diagnosis."""
    prediction = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y,prediction,labels=[0,1]).ravel()
    return {'ROC AUC':roc_auc_score(y,scores),'Average precision':average_precision_score(y,scores),
        'Accuracy':accuracy_score(y,prediction),'Balanced accuracy':balanced_accuracy_score(y,prediction),
        'Precision':precision_score(y,prediction,zero_division=0),
        'Recall':recall_score(y,prediction,zero_division=0),'F1':f1_score(y,prediction,zero_division=0),
        'Specificity':tn/(tn+fp),'Brier score':brier_score_loss(y,scores),
        'Threshold':float(threshold),'TN':int(tn),'FP':int(fp),'FN':int(fn),'TP':int(tp)}


def train_models(df):
    """Choose model by validation AP, choose thresholds on validation, then evaluate test once.

    No fitting or threshold optimization occurs on test labels. The returned fitted
    models remain training-only models, so profile scores use the evaluated model.
    """
    splits = split_cohort(df)
    train, val, test = [splits[s] for s in ['train','validation','test']]
    specifications = {
        'Class-prior baseline': (DEMOGRAPHIC,DummyClassifier(strategy='prior')),
        'Demographics logistic': (DEMOGRAPHIC,LogisticRegression(max_iter=2000,C=.3,class_weight='balanced',random_state=42)),
        'Labs + demographics logistic': (FEATURES,LogisticRegression(max_iter=2000,C=.3,class_weight='balanced',random_state=42)),
        'Labs + demographics forest': (FEATURES,RandomForestClassifier(n_estimators=180,max_depth=6,
            min_samples_leaf=12,class_weight='balanced_subsample',random_state=42,n_jobs=1))}
    fitted, validation_rows, test_rows, thresholds, predictions = {}, [], [], {}, []
    for name,(features,estimator) in specifications.items():
        pipeline = build_pipeline(estimator).fit(train[features],train[TARGET])
        val_scores = pipeline.predict_proba(val[features])[:,1]
        # Fixed threshold candidates are selected with validation balanced accuracy.
        candidates = np.arange(.05,.96,.01)
        if name == 'Class-prior baseline':
            threshold = .5
        else:
            quality = [balanced_accuracy_score(val[TARGET],val_scores >= t) for t in candidates]
            threshold = float(candidates[int(np.argmax(quality))])
        thresholds[name] = threshold
        fitted[name] = {'pipeline':pipeline,'features':features}
        validation_rows.append({'Model':name,**evaluate(val[TARGET],val_scores,threshold)})
    validation_metrics = pd.DataFrame(validation_rows)
    # The baseline is a comparator, not a deployable choice; the winner is frozen before test scoring.
    winner = validation_metrics[validation_metrics.Model!='Class-prior baseline'].sort_values(
        'Average precision',ascending=False,kind='stable').iloc[0].Model
    for name,info in fitted.items():
        scores = info['pipeline'].predict_proba(test[info['features']])[:,1]
        test_rows.append({'Model':name,**evaluate(test[TARGET],scores,thresholds[name])})
        frame = test[['SEQN',TARGET]].copy()
        frame['Model'] = name
        frame['Score'] = scores
        frame['Predicted'] = (scores >= thresholds[name]).astype(int)
        predictions.append(frame)
    return dict(models=fitted,splits=splits,validation_metrics=validation_metrics,
        test_metrics=pd.DataFrame(test_rows),winner=winner,thresholds=thresholds,
        predictions=pd.concat(predictions,ignore_index=True))


def classification_arff(df,features):
    """Nominal class prevents Weka from accidentally treating this as regression."""
    lines=['@RELATION nhanes_reported_diabetes','']
    lines += [f'@ATTRIBUTE {c} NUMERIC' for c in features]
    lines += ['@ATTRIBUTE DIABETES_REPORTED {no,yes}','','@DATA']
    for _,row in df.iterrows():
        values=['?' if pd.isna(row[c]) else f'{float(row[c]):.12g}' for c in features]
        values.append('yes' if row[TARGET]==1 else 'no')
        lines.append(','.join(values))
    return '\n'.join(lines)+'\n'


def export_results(data,result):
    """Save reproducible results, original-feature splits, and training-only imputed tool inputs."""
    out=ROOT/'exports'/'diabetes'
    out.mkdir(parents=True,exist_ok=True)
    result['test_metrics'].to_csv(out/'test_metrics.csv',index=False)
    result['validation_metrics'].to_csv(out/'validation_metrics.csv',index=False)
    result['predictions'].to_csv(out/'test_predictions.csv',index=False)
    data['join_audit'].to_csv(out/'join_audit.csv',index=False)
    data['flow'].to_csv(out/'cohort_flow.csv',index=False)
    data['eligible'].to_csv(out/'adult_diabetes_dataset.csv',index=False)
    # External tools receive an optional already-imputed variant fit using train medians only.
    median = result['splits']['train'][FEATURES].median()
    median.rename('Training median').to_csv(out/'training_medians.csv')
    for split,frame in result['splits'].items():
        frame[FEATURES+[TARGET]].to_csv(out/f'{split}_raw.csv',index=False)
        frame[['SEQN']].to_csv(out/f'{split}_ids.csv',index=False)
        complete = frame[FEATURES+[TARGET]].copy()
        complete[FEATURES] = complete[FEATURES].fillna(median)
        (out/f'{split}.arff').write_text(classification_arff(complete,FEATURES),encoding='utf-8')
        complete[TARGET] = complete[TARGET].map({0:'no',1:'yes'})
        complete.to_csv(out/f'{split}.csv',index=False)
    manifest = {'task':'Classify self-reported doctor-told diabetes in adults aged 20+',
        'label':'DIQ010: 1=yes, 2=no; all other responses excluded',
        'features':FEATURES,'seed':42,'split_rows':{k:len(v) for k,v in result['splits'].items()},
        'split_positive_counts':{k:int(v[TARGET].sum()) for k,v in result['splits'].items()},
        'winner':result['winner'],'selection':'Highest validation average precision',
        'threshold_selection':'Maximum validation balanced accuracy over 0.05..0.95 in 0.01 increments',
        'thresholds':result['thresholds'],'test_metrics':result['test_metrics'].to_dict('records'),
        'workbook_sha256':hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
        'external_tools':'Prepared only; RapidMiner and Weka have not been executed',
        'population':'Unweighted analytic sample; not nationally representative prevalence',
        'limitations':['Self-report is not confirmed disease','No future incidence outcome',
            'Laboratory measurements may reflect existing disease or treatment','No external clinical validation',
            'Model scores are not calibrated clinical probabilities']}
    (out/'benchmark.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest
