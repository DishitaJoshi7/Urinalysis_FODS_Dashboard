"""Frozen validation-selected classifiers, test metrics, and error analysis."""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import roc_curve,precision_recall_curve
from sklearn.calibration import calibration_curve
from diabetes import TARGET
from diabetes_ui import get_models,source_version
from charts import canvas,sns,PALETTE
from ui import plot,table,csv_button

st.caption('FIXED EVALUATION · Full eligible adult cohort · Stratified 60% train / 20% validation / 20% test')
st.markdown('The classifier is selected by **validation average precision**. Decision thresholds are selected on validation data and frozen before test evaluation.')
result=get_models(source_version())
metrics=result['test_metrics']
winner=result['winner']
st.success('Validation-selected model: '+winner)
selected=st.selectbox('Inspect evaluated model',metrics.Model.tolist(),index=metrics.Model.tolist().index(winner))
row=metrics.set_index('Model').loc[selected]
with st.container(horizontal=True):
    st.metric('Test ROC AUC',f'{row["ROC AUC"]:.3f}',border=True)
    st.metric('Test average precision',f'{row["Average precision"]:.3f}',border=True)
    st.metric('Test recall',f'{row.Recall:.1%}',border=True)
    st.metric('Test precision',f'{row.Precision:.1%}',border=True)
table(metrics.drop(columns=['TN','FP','FN','TP']).round(4),'Held-out classifier performance')
csv_button(metrics,'Download held-out metrics','diabetes_test_metrics')
st.caption('Accuracy alone is misleading for this imbalanced sample. Average precision summarizes the precision–recall curve. '
    'A positive classification is a prediction of the survey response. Many positive classifications may be false positives.')

pred=result['predictions'].loc[lambda x:x.Model.eq(selected)]
left,right=st.columns(2)
with left,st.container(border=True):
    st.subheader('Confusion matrix')
    fig,ax=canvas(6,4)
    matrix=np.array([[row.TN,row.FP],[row.FN,row.TP]],dtype=int)
    sns.heatmap(matrix,annot=True,fmt='d',cmap='Blues',cbar=False,ax=ax,
        xticklabels=['No reported diabetes','Reported diabetes'],yticklabels=['No reported diabetes','Reported diabetes'])
    ax.set(xlabel='Predicted response class',ylabel='Observed response class')
    plot(fig,'Test confusion matrix for '+selected,'diabetes_confusion')
    st.caption(f'Frozen threshold: {row.Threshold:.2f}. False positives: {int(row.FP)}; false negatives: {int(row.FN)}.')
with right,st.container(border=True):
    st.subheader('ROC curves')
    fig,ax=canvas(6,4)
    for i,(name,group) in enumerate(result['predictions'].groupby('Model',sort=False)):
        fpr,tpr,_=roc_curve(group[TARGET],group.Score)
        ax.plot(fpr,tpr,label=name,color=PALETTE[i])
    ax.plot([0,1],[0,1],'--',color='grey',lw=1)
    ax.set(xlabel='False positive rate',ylabel='True positive rate')
    ax.legend(fontsize=7,frameon=False)
    plot(fig,'Test ROC curves for all models','diabetes_roc')

left,right=st.columns(2)
with left:
    st.subheader('Precision–recall curves')
    fig,ax=canvas(6,4)
    for i,(name,group) in enumerate(result['predictions'].groupby('Model',sort=False)):
        # A constant-score baseline has only one operating point; do not draw a
        # misleading diagonal to the conventional precision=1 endpoint.
        if name=='Class-prior baseline':
            continue
        precision,recall,_=precision_recall_curve(group[TARGET],group.Score)
        ax.step(recall,precision,where='post',label=name,color=PALETTE[i])
    ax.axhline(pred[TARGET].mean(),color='grey',ls='--',label='Test positive share')
    ax.set(xlabel='Recall',ylabel='Precision')
    ax.legend(fontsize=7,frameon=False)
    plot(fig,'Test precision recall curves','diabetes_pr')
with right:
    st.subheader('Score reliability')
    observed,mean_score=calibration_curve(pred[TARGET],pred.Score,n_bins=8,strategy='quantile')
    fig,ax=canvas(6,4)
    ax.plot(mean_score,observed,marker='o',label='Observed test response rate')
    ax.plot([0,1],[0,1],'--',color='grey',label='Perfect calibration')
    ax.set(xlabel='Mean model score',ylabel='Observed positive fraction',xlim=(0,1),ylim=(0,1))
    ax.legend(fontsize=8,frameon=False)
    plot(fig,'Reliability diagram for selected model','diabetes_calibration')
    st.caption('Class weighting changes score calibration. Scores are not validated personal diabetes probabilities.')

with st.expander('Validation results and split audit'):
    table(result['validation_metrics'].round(4),'Validation model selection results')
    table(pd.DataFrame([{'Split':k,'Rows':len(v),'Reported diabetes':int(v[TARGET].sum())} for k,v in result['splits'].items()]),'Fixed train validation test counts')
    st.caption('Sidebar filters do not change these results. Test results are reported for comparison, not used to retune the model.')
csv_button(result['predictions'],'Download test predictions','diabetes_test_predictions')
