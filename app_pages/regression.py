"""Experiment 5: simple/multiple regression with an honest holdout evaluation."""
import numpy as np
import pandas as pd
import streamlit as st
from core import regression_experiment
from charts import canvas, TEAL, CORAL, sns
from ui import context, plot, table, csv_button, explain

df,labels=context()
st.caption('EXPERIMENT 05 · Predict missing hematocrit using regression')
st.markdown('Estimate **hematocrit (%)** from related CBC measurements. Compare against a training-mean baseline on unseen rows.')
mode=st.segmented_control('Regression model',['Simple linear','Multiple linear'],default='Simple linear',key='regression_mode')
features=['LBXHGB'] if mode=='Simple linear' else ['LBXHGB','LBXRBCSI','LBXMCVSI']
fraction=st.slider('Holdout fraction',.1,.4,.2,.05)

# Cache by cohort and model settings; the fixed seed makes comparisons repeatable.
@st.cache_data(max_entries=12,show_spinner='Fitting and evaluating regression…')
def fit(frame, predictors, size):
    return regression_experiment(frame,predictors,test_size=size)

try:
    result=fit(df,features,fraction)
except ValueError as error:
    st.warning(str(error))
    st.stop()
metrics=result['metrics']
with st.container(horizontal=True):
    st.metric('Training rows',f'{len(result["train"]):,}',border=True)
    st.metric('Held-out rows',f'{len(result["test"]):,}',border=True)
    st.metric('Holdout RMSE',f'{metrics.iloc[0].RMSE:.3f}',border=True)
    st.metric('Holdout R²',f'{metrics.iloc[0].R2:.3f}',border=True)
table(metrics.round(4),'Regression versus baseline on the identical holdout')
st.caption('MAE/RMSE are in hematocrit percentage points; MSE is in squared percentage points. '
           f'{result["excluded"]:,} rows lack at least one required measurement and are excluded from evaluation.')

# Show fitted coefficients so the mathematical model is visible to the student.
model=result['model']
equation=f'Hematocrit = {model.intercept_:.4f} '+''.join(f'{c:+.4f} × {f} ' for f,c in zip(features,model.coef_))
st.code(equation,language=None)
if len(features)==1:
    train=result['train']
    xx=train.LBXHGB.to_numpy()
    yy=train.LBXHCT.to_numpy()
    slope=np.sum((xx-xx.mean())*(yy-yy.mean()))/np.sum((xx-xx.mean())**2)
    intercept=yy.mean()-slope*xx.mean()
    st.caption(f'Manual least-squares check on the training rows: slope {slope:.4f}, intercept {intercept:.4f}.')

pred=result['predictions']
left,right=st.columns(2)
with left,st.container(border=True):
    st.subheader('Observed vs predicted')
    fig,ax=canvas()
    ax.scatter(pred.Observed,pred.Predicted,s=12,alpha=.3,color=TEAL)
    ends=[min(pred.Observed.min(),pred.Predicted.min()),max(pred.Observed.max(),pred.Predicted.max())]
    ax.plot(ends,ends,color=CORAL,ls='--',label='Perfect agreement')
    ax.set(xlabel='Observed hematocrit (%)',ylabel='Predicted hematocrit (%)')
    ax.legend(frameon=False)
    plot(fig,'Holdout predictions compared with measured hematocrit','regression_predictions')
with right,st.container(border=True):
    st.subheader('Residual diagnostics')
    fig,ax=canvas()
    ax.scatter(pred.Predicted,pred.Residual,s=12,alpha=.3,color=TEAL)
    ax.axhline(0,color=CORAL,ls='--')
    ax.set(xlabel='Predicted hematocrit (%)',ylabel='Observed − predicted (percentage points)')
    plot(fig,'Residuals on held-out observations','regression_residuals')

st.subheader('Actual missing-value eligibility')
with st.container(horizontal=True):
    st.metric('Missing hematocrit',int(df.LBXHCT.isna().sum()),border=True)
    st.metric('Can be estimated',len(result['missing']),border=True)
    st.metric('Still missing predictors',result['unfilled'],border=True)
if result['missing'].empty:
    st.info('No genuinely missing hematocrit values have complete predictors in this cohort. '
            'The holdout above demonstrates regression imputation by hiding known values. No artificial measurements are added.')
else:
    table(result['missing'],'Regression estimates for eligible missing targets')
    csv_button(result['missing'],'Download labeled estimates','hematocrit_estimates')
csv_button(pred,'Download holdout predictions','holdout_predictions')
csv_button(metrics,'Download model metrics','regression_metrics')
explain('The 80/20 default split is made before fitting. The regression and mean baseline see training rows only. '
        'After holdout scoring, a separate model is fit on all complete cases to estimate eligible missing values. '
        'These estimates are labeled and never overwrite the workbook. CBC relationships may be strong partly '
        'because laboratory indices are physiologically or mathematically related. This does not validate a colorimetric sensor. '
        'The missing-data mechanism is not established, and complete-case evaluation may not generalize to missing panels.')
