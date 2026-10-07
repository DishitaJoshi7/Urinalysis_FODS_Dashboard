"""Experiment 3: central tendency, variability, grouped frequency, boxplots."""
import pandas as pd
import streamlit as st
from core import summary_table, grouped_stats, measurement_columns
from charts import canvas, sns, TEAL
from ui import context, table, plot, csv_button, explain

df, labels = context()
st.caption('STATISTICAL SUMMARY · Central tendency and variability')
cols = st.multiselect('Measurements', measurement_columns(df), default=['URDACT','LBXWBCSI','LBXRBCSI','LBXHGB','LBXMCVSI','LBXPLTSI'])
if not cols:
    st.info('Select at least one measurement.')
    st.stop()
stats = summary_table(df,cols)
table(stats.round(3), 'Descriptive statistics by measurement')
csv_button(stats, 'Download statistics', 'descriptive_statistics')
st.caption('Variance and SD use n−1. Multiple modes are retained (up to five displayed). IQR outliers are statistical flags, not diagnoses.')

# Separate units prevent platelet counts from visually flattening smaller-valued variables.
st.subheader('Boxplots in original measurement units')
for offset in range(0,len(cols),3):
    for container,c in zip(st.columns(3),cols[offset:offset+3]):
        with container:
            fig,ax = canvas(4,3)
            sns.boxplot(x=df[c],ax=ax,color='#b9ddd6',fliersize=2)
            ax.set(xlabel=labels[c],title=c)
            plot(fig, 'Boxplot of '+labels[c], 'stats_'+c)

st.subheader('Grouped frequency and midpoint estimates')
c = st.selectbox('Grouped variable', cols)
bins = st.slider('Equal-width intervals',3,20,8)
freq, approximations = grouped_stats(df[c],bins)
left,right=st.columns([1.3,1])
with left:
    table(freq.round(3),'Grouped frequency distribution')
with right:
    table(pd.DataFrame({'Statistic':list(approximations),'Approximate value':list(approximations.values())}).round(3),'Grouped approximations')
fig,ax=canvas(9,3)
ax.bar(freq.Midpoint,freq.Frequency,width=(freq.Upper-freq.Lower)*.9,color=TEAL)
ax.set(xlabel=labels[c],ylabel='Frequency')
plot(fig,'Grouped frequency histogram','grouped_frequency')
explain('The top table uses individual observations. Grouped mean and variance replace observations with '
        'interval midpoints; grouped quartiles interpolate within the relevant interval. The grouped mode uses '
        'the first modal interval and its neighbors. These estimates depend on bin width. Intervals include their '
        'left edge; only the final interval includes its right edge. No observed values are discarded.')
