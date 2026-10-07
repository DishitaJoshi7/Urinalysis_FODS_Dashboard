"""Inspect the original laboratory fields, added CDC variables, and cohort construction."""
import pandas as pd
import streamlit as st
from diabetes import FEATURES,TARGET
from charts import missingness
from ui import table,plot,csv_button

df=st.session_state.diabetes_cohort
labels=st.session_state.labels
st.caption('DATA EXPLORATION · Original urine/CBC measurements joined to matching 2017–2018 CDC records')
default=['SEQN','STATUS','RIDAGEYR','BMXBMI','URDACT','LBXHGB']
cols=st.multiselect('Displayed columns',df.columns.tolist(),default=default)
if cols:
    table(df[cols],'Selected adult respondent records',height=350)
    csv_button(df[cols],'Download selected records','diabetes_selected_records')
plot(missingness(df[FEATURES]),'Missing predictor measurements in selected cohort','diabetes_missingness')

with st.expander('Data dictionary and missing-value audit',expanded=True):
    profile=pd.DataFrame({'Code':df.columns,'Definition / unit':[labels.get(c,c) for c in df],
        'Observed':df.notna().sum().values,'Missing':df.isna().sum().values,
        'Missing %':df.isna().mean().mul(100).round(2).values})
    table(profile,'Joined variable definitions and missing counts')
with st.expander('Source matching and inclusion criteria',expanded=True):
    data=st.session_state.diabetes_data
    table(data['join_audit'],'CDC source matching by respondent ID')
    table(data['flow'],'Cohort inclusion and exclusion counts')
    st.caption('These counts describe the full source cohort before sidebar filters. '
        'Borderline, refused, unknown and missing answers are excluded from binary classification.')
with st.expander('Compare missing-value treatments'):
    field=st.selectbox('Measurement for treatment comparison',FEATURES,format_func=lambda c:labels[c])
    method=st.selectbox('Treatment',['Keep missing','Drop missing','Mean fill','Median fill'])
    s=df[field]
    changed=s.dropna() if method=='Drop missing' else s.fillna(s.mean()) if method=='Mean fill' else s.fillna(s.median()) if method=='Median fill' else s
    table(pd.DataFrame({'Method':['Original',method],'Rows':[len(s),len(changed)],
        'Missing':[s.isna().sum(),changed.isna().sum()],'Mean':[s.mean(),changed.mean()],
        'Sample SD':[s.std(),changed.std()]}),'Descriptive effect of missing-value treatment')
    st.caption('This comparison does not modify source data or model inputs. The model learns imputation values from training rows only.')
