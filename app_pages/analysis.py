"""Group related analyses while executing only the selected view."""
from pathlib import Path
import runpy
import streamlit as st

# A fixed mapping preserves the original analyses without crowding the sidebar.
views = {'Charts': 'gallery.py', 'Summary statistics': 'statistics.py', 'Relationships': 'correlation.py'}
selected = st.radio('Choose an analysis', list(views), horizontal=True, key='analysis_view')
st.divider()
runpy.run_path(str(Path(__file__).with_name(views[selected])))
