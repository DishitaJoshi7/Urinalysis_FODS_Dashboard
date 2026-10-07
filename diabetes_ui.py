"""Shared data and model caches for the diabetes dashboard."""
import streamlit as st
from core import DATA_PATH,ROOT
from diabetes import load_diabetes,train_models


def source_version():
    """Invalidate caches if any local source changes."""
    return tuple(p.stat().st_mtime_ns for p in [DATA_PATH,*sorted((ROOT/'data'/'nhanes').glob('*.xpt'))])


@st.cache_data(max_entries=2,show_spinner='Joining NHANES laboratory and diabetes records…')
def get_data(version):
    return load_diabetes()


@st.cache_resource(max_entries=2,show_spinner='Evaluating models on fixed training, validation and test splits…')
def get_models(version):
    # Model evaluation deliberately uses the full fixed analytic cohort, never sidebar subsets.
    return train_models(get_data(version)['eligible'])
