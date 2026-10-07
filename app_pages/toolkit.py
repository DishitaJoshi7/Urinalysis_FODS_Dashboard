"""Export the same records for reproducible comparisons across course tools."""
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import streamlit as st
from core import regression_experiment, arff_text, ROOT
from ui import context, table

df,labels=context()
st.markdown('Use the same training and test records in Python, RapidMiner, and Weka.')
st.caption('Exports follow the selected sidebar cohort. The packaged exports/ folder contains the default full cohort.')
features=['LBXHGB']
result=regression_experiment(df,features)
target='LBXHCT'

# SEQN is deliberately omitted from model matrices; it is saved in a separate audit file.
buffer=BytesIO()
with ZipFile(buffer,'w',ZIP_DEFLATED) as archive:
    for split in ['train','test']:
        matrix=result[split][features+[target]]
        archive.writestr(f'{split}.csv',matrix.to_csv(index=False))
        archive.writestr(f'{split}.arff',arff_text(matrix))
        archive.writestr(f'{split}_ids.csv',result[split][['SEQN']].to_csv(index=False))
    archive.writestr('python_metrics.csv',result['metrics'].to_csv(index=False))
    archive.writestr('README.txt','Simple linear regression: LBXHGB -> LBXHCT.\n'
        '80% train / 20% test, random_state=42. Target is last.\n'
        'Do not add IDs to the model. Import train and test separately.\n'
        'Python R2 is not the same as Weka correlation coefficient.\n')
st.download_button('Download CSV + ARFF comparison bundle',buffer.getvalue(),
                   'course_tool_exports.zip','application/zip',icon=':material/download:')
table(result['metrics'].round(4),'Python reference metrics for tool comparison')

st.subheader('Export specification')
st.markdown('**Predictor:** hemoglobin (LBXHGB). **Target:** hematocrit (LBXHCT). '
    '**Split:** 80% training / 20% test, random seed 42. '
    'CSV and ARFF files contain identical records; respondent IDs are provided separately for auditing.')
st.caption('These exports support RapidMiner and Weka. External-tool results have not been measured. '
           'The table above reports the verified Python benchmark.')
st.download_button('Download integration documentation',
    (ROOT/'docs'/'RAPIDMINER_WEKA.md').read_text(encoding='utf-8'),
    'RAPIDMINER_WEKA.md','text/markdown')
