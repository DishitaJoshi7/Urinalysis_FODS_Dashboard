"""A quick introduction to the cohort and its measurement coverage."""
import streamlit as st
from core import measurement_columns
from charts import distribution, missingness
from ui import context, plot, table

df, labels = context()
st.markdown('Explore urine chemistry and blood-count measurements, then follow the full data science workflow.')
with st.container(horizontal=True):
    st.metric('Respondents', f'{len(df):,}', border=True)
    st.metric('Urine ACR observed', f'{df.URDACT.notna().sum():,}', border=True)
    st.metric('Hemoglobin observed', f'{df.LBXHGB.notna().sum():,}', border=True)
    st.metric('Median ACR · mg/g', f'{df.URDACT.median():.2f}', border=True)

# Two prominent charts establish distribution shape and data quality first.
left, right = st.columns([1.15, 1])
with left, st.container(border=True):
    st.subheader('Urine albumin / creatinine')
    st.caption('Observed values on a log scale to make the long right tail visible.')
    plot(distribution(df.URDACT, 'ACR (mg/g)', log=True), 'Distribution of urine ACR', 'overview_acr')
with right, st.container(border=True):
    st.subheader('Where measurements are missing')
    st.caption('The twelve variables with the largest missing fractions.')
    plot(missingness(df), 'Missing measurements by variable', 'overview_missing')

with st.container(border=True):
    st.subheader('From laboratory data to a strip-reader use case')
    st.markdown('**This project covers the data science layer:** inspect → clean → visualize → correlate → estimate → evaluate. '
        'The supplied workbook contains urine chemistry and CBC results. RGB pad readings, strip images, '
        'calibration pairs, and repeat-visit timestamps are unavailable.')
    st.caption('Blood leukocyte counts are not urinary leukocyte-pad results. Urine albumin is not a direct calibration of a total-protein strip pad. '
               'This coursework app does not provide diagnoses or validated strip-reader predictions.')

st.subheader('Measurement snapshot')
cols = ['URXUMA','URXUCR','URDACT','LBXWBCSI','LBXHGB','LBXHCT']
table(df[['SEQN']+cols].head(12), 'First twelve selected respondents')
st.caption('Variable definitions and units are available in Data explorer. Source: supplied NHANES workbook, Merged_Dataset.')
