"""Experiment 7 collects the six required plots and additional Seaborn views."""
import matplotlib.pyplot as plt
import streamlit as st
from core import measurement_columns
from charts import six_plots, canvas, sns, TEAL
from ui import context, plot

df,labels=context()
st.caption('MEASUREMENT VISUALIZATIONS · Distributions, composition and relationships')
choices=measurement_columns(df)
field=st.selectbox('Distribution measurement',choices,index=choices.index('LBXHGB'))
bins=st.slider('Histogram bins',5,60,25)
figures=six_plots(df,labels,field,bins)
for start in range(0,6,2):
    for container,(title,fig,interpretation) in zip(st.columns(2),figures[start:start+2]):
        with container,st.container(border=True):
            st.subheader(title)
            st.caption(interpretation)
            plot(fig,title+' for NHANES cohort','gallery_'+title.replace(' ','_'))

st.subheader('Additional Seaborn exploration')
kind=st.selectbox('Additional visualization',['Violin plot','ECDF','Pair plot'])
if kind=='Violin plot':
    fig,ax=canvas(9,3)
    sns.violinplot(x=df[field].dropna(),inner='quart',cut=0,ax=ax,color='#b9ddd6')
    ax.set(xlabel=labels[field])
    plot(fig,'Violin distribution of '+field,'seaborn_violin')
    st.caption('Width represents smoothed density; interior marks show quartiles.')
elif kind=='ECDF':
    fig,ax=canvas(9,3)
    sns.ecdfplot(df[field].dropna(),ax=ax,color=TEAL)
    ax.set(xlabel=labels[field],ylabel='Fraction at or below value')
    plot(fig,'Empirical cumulative distribution of '+field,'seaborn_ecdf')
else:
    # Limit an explicitly labeled sample to keep a scatter matrix responsive.
    pair_cols=['LBXHGB','LBXHCT','LBXRBCSI','LBXMCVSI']
    complete=df[pair_cols].dropna()
    sampled=complete.sample(min(600,len(complete)),random_state=42)
    st.caption(f'Pair plot: fixed sample of {len(sampled):,} complete CBC rows (seed 42). Other charts use all available selected rows.')
    grid=sns.pairplot(sampled,diag_kind='hist',plot_kws={'s':10,'alpha':.3},height=2.2)
    plot(grid.fig,'Sampled CBC scatter matrix','seaborn_pairplot')
