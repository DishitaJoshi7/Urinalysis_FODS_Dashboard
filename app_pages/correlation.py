"""Experiment 4: manual Pearson coefficient and three relationship examples."""
import numpy as np
import streamlit as st
from core import manual_pearson, measurement_columns
from charts import scatter, canvas, sns
from ui import context, plot, table, explain

df,labels=context()
st.caption('RELATIONSHIP ANALYSIS · Pearson correlation')
cols=measurement_columns(df)
a,b=st.columns(2)
with a:
    x=st.selectbox('X measurement',cols,index=cols.index('LBXHGB'))
with b:
    y=st.selectbox('Y measurement',[c for c in cols if c!=x],index=([c for c in cols if c!=x]).index('LBXHCT') if x!='LBXHCT' else 0)
r,n=manual_pearson(df[x],df[y])
with st.container(horizontal=True):
    st.metric('Manual Pearson r',f'{r:.4f}',border=True)
    st.metric('Paired observations',f'{n:,}',border=True)
    st.metric('Pairs excluded',f'{len(df)-n:,}',border=True)
plot(scatter(df,x,y,labels),'Relationship between selected measurements','selected_correlation')
st.latex(r'r=\frac{\sum_i(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum_i(x_i-\bar{x})^2\sum_i(y_i-\bar{y})^2}}')

with st.expander('Selected measurement relationships',expanded=True):
    for x,y,heading in [('LBXHGB','LBXHCT','Hemoglobin and hematocrit'),
                         ('LBXLYPCT','LBXNEPCT','Lymphocyte and neutrophil percentages'),
                         ('LBDEONO','LBXMCHSI','Eosinophil number and mean cell hemoglobin')]:
        st.markdown('**'+heading+'**')
        plot(scatter(df,x,y,labels),heading,'example_'+x)
    st.caption('The third pair has a weak linear association; its measured coefficient is reported. '
               'Differential percentages share a total, which contributes to their inverse relationship.')

st.subheader('Seaborn correlation heatmap')
selected=st.multiselect('Heatmap measurements',cols,default=['URDACT','LBXWBCSI','LBXHGB','LBXHCT','LBXRBCSI','LBXMCVSI'])
if len(selected)>=2:
    corr=df[selected].corr(min_periods=3)
    fig,ax=canvas(8,5)
    sns.heatmap(corr,annot=True,fmt='.2f',cmap='vlag',vmin=-1,vmax=1,center=0,square=True,ax=ax)
    plot(fig,'Pairwise Pearson correlation heatmap','correlation_heatmap')
    with st.expander('Number of observed pairs per heatmap cell'):
        observed=df[selected].notna().astype(int)
        table((observed.T@observed).reset_index(),'Pair counts for the correlation matrix')
explain('Pearson r measures linear association. Missing measurements are removed separately for each pair, '
        'so heatmap cells can have different sample sizes. A zero coefficient does not rule out a nonlinear relationship. '
        'Constant variables have undefined correlation. IDs, detection flags, and duplicate units are excluded.')
