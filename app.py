"""Run with: python -m streamlit run app.py (see README for VS Code setup)."""
import streamlit as st
from core import DATA_PATH
from diabetes_ui import get_data, source_version

# Native navigation runs only the active page, avoiding computation in hidden tabs.
st.set_page_config(page_title='Diabetes Analyzer | NHANES', page_icon=':material/monitor_heart:', layout='wide')
# Keep the main menu short; detailed lab tools remain inside the analysis pages.
page = st.navigation({
    'Explore': [
        st.Page('app_pages/overview.py', title='Dashboard', icon=':material/dashboard:'),
        st.Page('app_pages/explorer.py', title='View data', icon=':material/table_chart:'),
        st.Page('app_pages/analysis.py', title='Charts & statistics', icon=':material/bar_chart:')],
    'Diabetes analysis': [
        st.Page('app_pages/classification.py', title='Model results', icon=':material/model_training:'),
        st.Page('app_pages/profile.py', title='Try a sample profile', icon=':material/analytics:')],
    'More tools': [
        st.Page('app_pages/advanced.py', title='Advanced analysis', icon=':material/tune:'),
        st.Page('app_pages/toolkit.py', title='Downloads', icon=':material/download:')]
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
    st.markdown('**Filter data**')
    status = st.selectbox('Diabetes status', ['All eligible adults','Reported diabetes','No reported diabetes'],key='status_filter')
    age = st.slider('Age range',20,80,(20,80),key='age_filter', help='80 includes everyone aged 80 or older.')
    df = full.loc[full.RIDAGEYR.between(*age)].copy()
    if status != 'All eligible adults':
        df = df.loc[df.STATUS.eq(status)]
    st.caption(f'{len(df):,} of {len(full):,} eligible adults selected')
    with st.expander('About these filters'):
        st.caption('Filters change the data summaries and charts. Model results and profile scoring use the fixed full study group.')
        st.caption('Diabetes status is self-reported. Counts describe this sample, not population prevalence.')

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
