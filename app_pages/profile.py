"""A research-only score for an illustrative complete laboratory profile."""
import pandas as pd
import streamlit as st
from diabetes_ui import get_models,source_version
from diabetes import FEATURES,LAB_FEATURES
from ui import table

st.info('Research demonstration: this model classifies self-reported doctor-told diabetes. '
    'It cannot diagnose diabetes, rule it out, or predict future disease. Scores are not calibrated clinical probabilities.')
result=get_models(source_version())
name=result['winner']
info=result['models'][name]
train=result['splits']['train']
labels=st.session_state.labels
st.caption('Model: '+name+'. Initial inputs are training medians for an illustrative profile, not a real patient. '
    'Enter recorded measurements in the displayed units; the form does not save personal data.')

# Batch inputs in a form so the model scores only when the user submits a complete profile.
with st.form('profile_form'):
    a,b,c=st.columns(3)
    with a:
        age=st.number_input('Age (years; select 80 for 80+)',20,80,int(train.RIDAGEYR.median()))
    with b:
        sex=st.selectbox('Recorded sex',['Female','Male'])
    with c:
        bmi=st.number_input('BMI (kg/m²)',min_value=1.,max_value=150.,value=float(train.BMXBMI.median()),step=.1)
    values={'RIDAGEYR':age,'SEX_FEMALE':1 if sex=='Female' else 0,'BMXBMI':bmi}
    for start in range(0,len(LAB_FEATURES),2):
        for container,feature in zip(st.columns(2),LAB_FEATURES[start:start+2]):
            with container:
                values[feature]=st.number_input(labels[feature],min_value=0.,
                    value=float(train[feature].median()),format='%.2f',key='profile_'+feature)
    submitted=st.form_submit_button('Calculate research score',type='primary')
if submitted:
    entered=pd.DataFrame([values])[FEATURES]
    outside=[labels[f] for f in info['features'] if values[f]<train[f].min() or values[f]>train[f].max()]
    if outside:
        st.warning('Score not generated: inputs outside the model’s observed training range: '+', '.join(outside))
    else:
        score=float(info['pipeline'].predict_proba(entered[info['features']])[0,1])
        cutoff=result['thresholds'][name]
        st.metric('Model score for reported-diabetes class',f'{score:.3f}')
        st.write('Model classification: **'+('Reported diabetes' if score>=cutoff else 'No reported diabetes')+'**')
        st.caption(f'Frozen validation-selected threshold: {cutoff:.2f}. This classification is not a medical finding.')
        table(entered.rename(columns=labels),'Submitted illustrative profile')
