"""Diabetes cohort overview with clearly defined outcomes and descriptive comparisons."""
import pandas as pd
import numpy as np
import streamlit as st
from diabetes import TARGET,FEATURES
from charts import canvas,sns,TEAL,CORAL,PALETTE
from ui import plot,table,csv_button

df=st.session_state.diabetes_cohort
labels=st.session_state.labels
st.markdown('Explore how urine chemistry, blood counts and participant characteristics relate to **reported diabetes status**.')
st.caption('Adults aged 20+ with a yes/no response to the doctor-told diabetes question. “No reported diabetes” does not establish absence of disease.')
with st.container(horizontal=True):
    st.metric('Eligible adults selected',f'{len(df):,}',border=True)
    st.metric('Reported diabetes',f'{int(df[TARGET].sum()):,}',border=True)
    st.metric('Reported share · sample',f'{df[TARGET].mean():.1%}',border=True)
    st.metric('Median urine ACR · mg/g',f'{df.URDACT.median():.2f}',border=True)

# Keep categorical response counts and laboratory distributions visually distinct.
left,right=st.columns(2)
with left,st.container(border=True):
    st.subheader('Reported status in the selected sample')
    counts=df.STATUS.value_counts().reindex(['No reported diabetes','Reported diabetes'],fill_value=0)
    fig,ax=canvas(7,4)
    bars=ax.bar(['No reported\ndiabetes','Reported\ndiabetes'],counts.values,color=[TEAL,CORAL])
    ax.bar_label(bars,fmt='%d',padding=4)
    ax.set(ylabel='Respondents',ylim=(0,max(counts.max()*1.15,1)))
    plot(fig,'Counts of reported diabetes responses','diabetes_status')
    st.caption('This is an unweighted sample proportion, not a national prevalence estimate.')
with right,st.container(border=True):
    st.subheader('Urine ACR by reported status')
    chart=df[['URDACT','STATUS']].dropna().copy()
    chart['Log ACR']=np.log10(1+chart.URDACT)
    fig,ax=canvas(7,4)
    for group,color in zip(['No reported diabetes','Reported diabetes'],[TEAL,CORAL]):
        values=chart.loc[chart.STATUS.eq(group),'Log ACR']
        if len(values): sns.ecdfplot(values,ax=ax,label=f'{group} (n={len(values):,})',color=color)
    ax.set(xlabel='log10(1 + urine ACR in mg/g)',ylabel='Cumulative fraction')
    ax.legend(frameon=False,fontsize=8)
    plot(fig,'Urine ACR cumulative distributions by reported status','diabetes_acr')
    st.caption('Group differences are descriptive associations; they do not establish causation.')

st.subheader('Participant and laboratory comparison')
field=st.selectbox('Compare measurement',['RIDAGEYR','BMXBMI','URDACT','URXUCR','LBXWBCSI','LBXHGB'],format_func=lambda c:labels[c])
comparison=df.groupby('STATUS')[field].agg(['count','median','mean','std']).reset_index()
table(comparison.round(3),'Observed measurements by reported diabetes group')
fig,ax=canvas(10,3.5)
sns.boxplot(data=df,x=field,y='STATUS',ax=ax,color='#b9ddd6',fliersize=2)
ax.set(xlabel=labels[field],ylabel='')
plot(fig,'Selected measurement distribution by reported diabetes status','group_comparison')
csv_button(comparison,'Download group summary','diabetes_group_summary')
st.info('Model performance compares demographics alone with models that also use your urine/CBC measurements. '
        'It classifies reported current status; it does not forecast future diabetes or diagnose a person.')
