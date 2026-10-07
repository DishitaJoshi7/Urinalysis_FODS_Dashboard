"""Small display helpers keep every page readable and consistent."""
from io import BytesIO
import matplotlib.pyplot as plt
import streamlit as st
from core import read_workbook, DATA_PATH


@st.cache_data(max_entries=2, show_spinner='Reading NHANES workbook…')
def load_data(modified_time):
    # Modification time invalidates the cache if the included workbook changes.
    return read_workbook(DATA_PATH)


def context():
    return st.session_state['cohort'], st.session_state['labels']


def table(df, name, **kwargs):
    st.dataframe(df, hide_index=True, alt=name, **kwargs)


def plot(fig, name, key):
    # Save before closing; each chart has a presentation-ready PNG download.
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=180, bbox_inches='tight')
    st.pyplot(fig, alt=name)
    st.download_button('Save chart', buffer.getvalue(), file_name=key+'.png',
                       mime='image/png', key='download_'+key, icon=':material/download:')
    plt.close(fig)


def csv_button(df, name, key):
    st.download_button(name, df.to_csv(index=False).encode('utf-8'), file_name=key+'.csv',
                       mime='text/csv', key=key, icon=':material/download:')


def explain(text):
    with st.expander('Analysis notes'):
        st.markdown(text)
