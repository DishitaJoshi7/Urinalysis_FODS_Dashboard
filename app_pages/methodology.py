"""Formal project scope, reproducible methods, and documented evidence limits."""
import streamlit as st
from core import ROOT
st.markdown((ROOT/'docs/METHODOLOGY.md').read_text(encoding='utf-8'))
