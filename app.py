"""Run with: python -m streamlit run app.py (see README for VS Code setup)."""
import streamlit as st
from core import DATA_PATH
from ui import load_data

# Native navigation runs only the active page, avoiding computation in hidden tabs.
st.set_page_config(page_title='Urinalysis Lab | FODS', page_icon=':material/science:', layout='wide')
page = st.navigation({
    'Dashboard': [
        st.Page('app_pages/overview.py', title='Overview', icon=':material/dashboard:'),
        st.Page('app_pages/explorer.py', title='Data explorer', icon=':material/table_chart:')],
    'Experiments': [
        st.Page('app_pages/statistics.py', title='03 · Descriptive statistics', icon=':material/functions:'),
        st.Page('app_pages/correlation.py', title='04 · Correlation', icon=':material/scatter_plot:'),
        st.Page('app_pages/regression.py', title='05 · Regression & imputation', icon=':material/model_training:'),
        st.Page('app_pages/transforms.py', title='06 · Scale & discretize', icon=':material/tune:'),
        st.Page('app_pages/gallery.py', title='07 · Visualization gallery', icon=':material/bar_chart:')],
    'Project': [
        st.Page('app_pages/toolkit.py', title='RapidMiner & Weka', icon=':material/build:'),
        st.Page('app_pages/methodology.py', title='Use case & lab guide', icon=':material/menu_book:')]
})

# Cache the original tables; interactive selection never modifies source records.
try:
    sheets, labels = load_data(DATA_PATH.stat().st_mtime)
except (FileNotFoundError, ValueError) as error:
    st.error(f'Cannot load the supplied workbook: {error}')
    st.stop()
full = sheets['Merged_Dataset']
with st.sidebar:
    st.divider()
    st.markdown('**URINALYSIS LAB**')
    st.caption('Fundamentals of Data Science · NHANES 2017–2018')
    cohort = st.selectbox('Analysis cohort', ['All matched respondents', 'Observed urine panel',
        'Complete blood panel', 'Complete urine + blood panels'], key='cohort_choice')
    if cohort == 'Observed urine panel':
        df = full.dropna(subset=['URXUMA','URXUCR','URDACT'])
    elif cohort == 'Complete blood panel':
        df = full.dropna(subset=[c for c in full if c.startswith(('LBX','LBD'))])
    elif cohort == 'Complete urine + blood panels':
        df = full.dropna()
    else:
        df = full
    st.caption(f'{len(df):,} of {len(full):,} respondents selected')
    st.caption('All summaries are unweighted. Missing values remain missing.')

# Store the selected cohort once so each page uses the same denominator.
st.session_state.update(cohort=df, labels=labels, sheets=sheets)
st.caption('FODS PROJECT / NHANES 2017–2018')
st.title(page.title.split(' · ')[-1])
page.run()
