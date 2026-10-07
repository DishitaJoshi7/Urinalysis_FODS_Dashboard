"""Project context, analytical methods, and the limits of the available data."""
import streamlit as st
from core import ROOT

st.markdown('**Urine test strip reader using colorimetry as a point-of-care technology**')
st.caption('Use case KJS-HC-03 · NHANES 2017–2018 laboratory measurements')

# Present the completed analytical scope and the evidence supporting it.
st.subheader('Project objective')
st.markdown('Analyze urine chemistry and complete blood count measurements to characterize '
    'data quality, distributions, associations and regression performance. The dashboard '
    'provides a reproducible analytical foundation for the proposed urine-strip reader.')
st.subheader('Analytical scope')
st.markdown('The project integrates source-table reconciliation, missing-data assessment, '
    'descriptive statistics, Pearson correlation, hematocrit regression, normalization '
    'and clustering. Results can be exported as charts, data tables and matched model-evaluation datasets.')
st.subheader('Data limitations')
st.markdown('The supplied data contains laboratory measurements but no pad images, RGB calibration '
    'pairs or repeat-visit timestamps. Blood leukocyte measurements are not urinary leukocyte-pad '
    'measurements. Consequently, this analysis does not establish strip-reader calibration '
    'accuracy or clinical diagnostic performance. Summaries describe the unweighted sample.')
with st.expander('Data provenance and analytical methods', expanded=True):
    # Detailed scientific notes remain available alongside the results.
    text=(ROOT/'docs'/'METHODOLOGY.md').read_text(encoding='utf-8')
    st.markdown(text.split('## Supplied references and coverage')[0])
