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

left,right=st.columns(2)
with left,st.container(border=True):
    st.subheader('RapidMiner / Altair AI Studio')
    st.markdown('1. Import `train.csv` and `test.csv` with numeric columns.\n'
        '2. Set `LBXHCT` to the **label** role in both datasets.\n'
        '3. Fit **Linear Regression** on the training data.\n'
        '4. Send its model and the test set to **Apply Model**.\n'
        '5. Connect predictions to **Performance (Regression)**.\n'
        '6. Compare RMSE with the Python baseline above.')
    st.caption('A ready-to-import process is in tools/rapidminer_regression.rmp. Adjust its two CSV paths after moving the project.')
with right,st.container(border=True):
    st.subheader('Weka Explorer')
    st.markdown('1. Open `train.arff` in **Preprocess**.\n'
        '2. Set the class to numeric `LBXHCT`.\n'
        '3. Choose **functions → LinearRegression** in **Classify**.\n'
        '4. Set attribute selection to **No attribute selection** and ridge to `0`.\n'
        '5. Choose **Supplied test set** and load `test.arff`.\n'
        '6. Click **Start** and compare MAE/RMSE.')
    st.caption('Weka reports correlation coefficient, not sklearn’s R². Do not compare those as identical metrics.')
st.info('The Python pipeline and export files are tested. RapidMiner and Weka desktop execution must be completed in those installed tools; no external-tool results are fabricated.')
with st.expander('Full tool instructions'):
    st.markdown((ROOT/'docs'/'RAPIDMINER_WEKA.md').read_text(encoding='utf-8'))
