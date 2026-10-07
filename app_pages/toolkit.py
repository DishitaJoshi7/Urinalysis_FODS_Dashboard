"""Expose classification exports with nominal labels and the actual Python benchmark."""
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
import pandas as pd
import streamlit as st
from core import ROOT
from ui import table

st.markdown('Download the fixed adult diabetes cohort splits for Python, RapidMiner and Weka.')
st.caption('These files use the full fixed cohort. Sidebar descriptive filters do not change the training/test records.')
folder=ROOT/'exports'/'diabetes'
if not (folder/'benchmark.json').exists():
    st.error('Run python prepare_diabetes.py to generate the classification exports.')
    st.stop()
buffer=BytesIO()
with ZipFile(buffer,'w',ZIP_DEFLATED) as archive:
    for path in sorted(folder.iterdir()):
        if path.is_file(): archive.write(path,path.name)
st.download_button('Download diabetes analysis bundle',buffer.getvalue(),
    'diabetes_analysis_exports.zip','application/zip',icon=':material/download:')
table(pd.read_csv(folder/'test_metrics.csv').round(4),'Recorded Python test metrics')
st.subheader('Export specification')
st.markdown('Ten numerical predictors and a **yes/no nominal outcome**. CSV and ARFF share '
    'the same training, validation and test rows. Missing predictors in tool-ready files use '
    'training medians only. Raw variants retain missing values; IDs are in separate audit files.')
st.caption('Python pipelines additionally use missing indicators and class weighting. External-tool '
    'settings and scores may differ. The old root-level exports belong to the supplementary CBC regression.')
st.info('RapidMiner and Weka files are prepared. Neither tool has been executed for the diabetes task; '
    'the table reports Python results only.')
st.download_button('Download tool integration instructions',
    (ROOT/'docs'/'RAPIDMINER_WEKA.md').read_text(encoding='utf-8'),
    'RAPIDMINER_WEKA.md','text/markdown')
