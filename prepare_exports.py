"""Regenerate CSV/ARFF course-tool inputs and a reproducible benchmark report."""
import json
import hashlib
from core import ROOT, DATA_PATH, read_workbook, regression_experiment, arff_text, summary_table, DEFAULT_FEATURES


def main():
    # All output files are project-local; the input workbook is never modified.
    out=ROOT/'exports'
    out.mkdir(exist_ok=True)
    sheets,labels=read_workbook()
    df=sheets['Merged_Dataset']
    df.to_csv(out/'merged_clean.csv',index=False)
    summary_table(df,DEFAULT_FEATURES).to_csv(out/'descriptive_statistics.csv',index=False)
    result=regression_experiment(df,['LBXHGB'])
    for split in ['train','test']:
        # Excluding the respondent ID prevents it becoming a spurious predictor.
        frame=result[split][['LBXHGB','LBXHCT']]
        frame.to_csv(out/f'{split}.csv',index=False)
        (out/f'{split}.arff').write_text(arff_text(frame),encoding='utf-8')
        result[split][['SEQN']].to_csv(out/f'{split}_ids.csv',index=False)
    result['metrics'].to_csv(out/'python_metrics.csv',index=False)
    result['predictions'].to_csv(out/'holdout_predictions.csv',index=False)
    # CBC data with missing values is useful for the Weka preprocessing exercises.
    cbc=df[['LBXWBCSI','LBXRBCSI','LBXHGB','LBXHCT','LBXMCVSI','LBXPLTSI']]
    (out/'cbc_exploration.arff').write_text(arff_text(cbc,'cbc_exploration'),encoding='utf-8')
    cbc.to_csv(out/'cbc_exploration.csv',index=False)
    manifest={'source_sha256':hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
        'rows':{k:len(v) for k,v in sheets.items()},'columns':len(df.columns),
        'urine_acr_observed':int(df.URDACT.notna().sum()),'hemoglobin_observed':int(df.LBXHGB.notna().sum()),
        'complete_rows':int(df.notna().all(axis=1).sum()),
        'split_seed':42,'train_rows':len(result['train']),'test_rows':len(result['test']),
        'missing_hematocrit':int(df.LBXHCT.isna().sum()),'eligible_estimates':len(result['missing']),
        'python_metrics':result['metrics'].to_dict('records'),
        'rapidminer_execution':'Not executed; import process and run locally',
        'weka_execution':'Not executed; use supplied ARFF train/test pair'}
    (out/'benchmark.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    main()
