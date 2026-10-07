"""Run with: python -m streamlit run app.py (see README for VS Code setup)."""
import streamlit as st
from core import DATA_PATH
from diabetes_ui import get_data, source_version

# Native navigation runs only the active page, avoiding computation in hidden tabs.
st.set_page_config(page_title='Diabetes Analyzer | NHANES', page_icon=':material/monitor_heart:', layout='wide')
page = st.navigation({
    'Dashboard': [
        st.Page('app_pages/overview.py', title='Overview', icon=':material/dashboard:'),
        st.Page('app_pages/explorer.py', title='Data explorer', icon=':material/table_chart:')],
    'Diabetes models': [
        st.Page('app_pages/classification.py', title='Model performance', icon=':material/model_training:'),
        st.Page('app_pages/profile.py', title='Research profile score', icon=':material/analytics:')],
    'Analysis': [
        st.Page('app_pages/statistics.py', title='Descriptive statistics', icon=':material/functions:'),
        st.Page('app_pages/correlation.py', title='Correlation', icon=':material/scatter_plot:'),
        st.Page('app_pages/regression.py', title='CBC regression', icon=':material/functions:'),
        st.Page('app_pages/transforms.py', title='Normalization & clustering', icon=':material/tune:'),
        st.Page('app_pages/gallery.py', title='Visualizations', icon=':material/bar_chart:')],
    'Project': [
        st.Page('app_pages/toolkit.py', title='Data & model exports', icon=':material/build:'),
        st.Page('app_pages/methodology.py', title='Project methodology', icon=':material/menu_book:')]
})

# Cache the original tables; interactive selection never modifies source records.
try:
    data = get_data(source_version())
except (FileNotFoundError, ValueError) as error:
    st.error(f'Cannot load the required dataset: {error}. See README for the included source files.')
    st.stop()
full = data['eligible']
sheets, labels = data['sheets'], data['labels']
with st.sidebar:
    st.divider()
    st.markdown('**DIABETES ANALYZER**')
    st.caption('Fundamentals of Data Science · NHANES 2017–2018')
    status = st.selectbox('Reported status', ['All eligible adults','Reported diabetes','No reported diabetes'],key='status_filter')
    age = st.slider('Age range (80 = 80+)',20,80,(20,80),key='age_filter')
    df = full.loc[full.RIDAGEYR.between(*age)].copy()
    if status != 'All eligible adults':
        df = df.loc[df.STATUS.eq(status)]
    st.caption(f'{len(df):,} of {len(full):,} eligible adults selected')
    st.caption('Filters affect descriptive views. Model evaluation uses the fixed full cohort.')
    st.caption('Unweighted sample. Outcome: self-reported doctor-told diabetes.')

# Store the selected cohort once so each page uses the same denominator.
# Existing laboratory analyses receive only original workbook columns; no labels enter their calculations.
st.session_state.update(cohort=df[sheets['Merged_Dataset'].columns], diabetes_cohort=df,
                       labels=labels, sheets=sheets, diabetes_data=data)
st.caption('DIABETES ANALYZER / NHANES 2017–2018')
st.title(page.title.split(' · ')[-1])
if df.empty:
    st.info('No respondents match these filters. Expand the age range or select all eligible adults.')
    st.stop()
page.run()
