"""Explain course coverage, provenance, and the boundary of available evidence."""
import pandas as pd
import streamlit as st
from core import ROOT
from ui import table

st.markdown('**Urine test strip reader using colorimetry as a point-of-care technology**')
st.caption('Use case ID inside the supplied document: KJS-HC-03. The filename is KJS-HLC-01 Use Case - Dr. Ninad.pdf.')
st.markdown('The proposed device waits for a strip reaction, captures the ten pads under controlled illumination, '
    'extracts RGB features, and learns a mapping to laboratory concentrations. This FODS project develops '
    'the exploratory and statistical workflow using the supplied NHANES laboratory dataset.')
table(pd.DataFrame([
    ['01','Pandas / NumPy foundations','Data explorer: arrays, slicing, aggregation, inspection'],
    ['02','Data handling','Data explorer: filtering, missing values, SEQN merge, CSV export'],
    ['03','Central tendency / variability','Statistics: mean, median, modes, sample variance/SD, IQR, grouped frequency, boxplots'],
    ['04','Correlation coefficient','Manual Pearson r; positive, negative and weak examples; trend lines and heatmap'],
    ['05','Regression imputation','Simple and multiple regression; training/holdout split; eligible missing-value estimates'],
    ['06','Normalization / discretization','Min-max, sample z-score, decimal scaling; K-means scatter; width/quantile bins'],
    ['07','Matplotlib plots','Line, bar, scatter, pie, box and histogram; annotations and PNG export']],
    columns=['Experiment','Topic','Implementation']),'Mapping from the seven supplied experiments to dashboard features')

st.subheader('What the available data supports')
st.markdown('- Cross-sectional summaries of urine albumin, creatinine, ACR and CBC measurements.\n'
    '- Data quality checks, correlations, regression demonstrations and normalization.\n'
    '- Reproducible training/test datasets for RapidMiner and Weka.')
st.subheader('What would be needed for the actual strip reader')
st.markdown('- Paired RGB features and reference laboratory concentrations for each analyte.\n'
    '- Strip brand/batch, illumination calibration, reaction time and image metadata.\n'
    '- Participant identifiers for grouped validation, plus timestamps for real repeat-visit trends.\n'
    '- Independent validation data and clinical review before interpreting device predictions.')
st.caption('No RGB-to-concentration model can be learned from this workbook. The app has no live camera, hardware timer, '
           'hospital connection, authentication, or clinical deployment certification.')
with st.expander('Methodology and source notes',expanded=True):
    st.markdown((ROOT/'docs'/'METHODOLOGY.md').read_text(encoding='utf-8'))
with st.expander('Suggested presentation / viva walkthrough'):
    st.markdown((ROOT/'docs'/'PRESENTATION_GUIDE.md').read_text(encoding='utf-8'))
