"""Experiments 1 and 2: Pandas inspection, filtering, joins, cleaning, NumPy."""
import io
import numpy as np
import pandas as pd
import streamlit as st
from core import measurement_columns
from ui import context, table, csv_button

df, labels = context()
st.caption('DATA EXPLORATION · Measurement coverage and quality')
cols = st.multiselect('Columns to explore', list(df.columns),
                     default=['SEQN','URXUMA','URXUCR','URDACT','LBXHGB','LBXHCT'])
field = st.selectbox('Filter measurement', measurement_columns(df), index=2)
observed = df[field].dropna()
low, high = st.slider('Keep values in this range', float(observed.min()), float(observed.max()),
                      (float(observed.min()), float(observed.max())))
include_missing = st.checkbox('Include missing values for this measurement', value=True)
mask = df[field].between(low,high) | (df[field].isna() if include_missing else False)
view = df.loc[mask, cols]
st.caption(f'{len(view):,} records after explorer filters. Other pages use the sidebar cohort only.')
table(view, 'Filtered respondent measurements', height=350)
csv_button(view, 'Download filtered CSV', 'filtered_data')

# Profile keeps counts and units next to each variable rather than guessing types.
with st.expander('Data dictionary and missing-value audit', expanded=True):
    profile = pd.DataFrame({'Code': df.columns, 'Definition / unit': [labels[c] for c in df],
        'Type': [str(df[c].dtype) for c in df], 'Observed':df.notna().sum().values,
        'Missing':df.isna().sum().values, 'Missing %':df.isna().mean().mul(100).round(2).values})
    table(profile, 'Variable definitions, types, and missing counts')
    st.caption('URDUMALC and URDUCRLC are detection-limit flags, not analyte concentrations. '
               'URXUMS and URXCRS repeat measurements in alternative units.')

with st.expander('Source table reconciliation'):
    sheets = st.session_state.sheets
    rebuilt = sheets['Urine_Albumin_Creatinine'].merge(sheets['Complete_Blood_Count'], on='SEQN',
                how='inner', validate='one_to_one')
    st.write(f'Urine table: {len(sheets["Urine_Albumin_Creatinine"]):,} rows. '
             f'CBC table: {len(sheets["Complete_Blood_Count"]):,} rows. '
             f'One-to-one inner join: {len(rebuilt):,} rows.')
with st.expander('Compare cleaning choices without changing the original data'):
    choice = st.selectbox('Missing-value treatment', ['Keep missing', 'Drop missing', 'Mean fill', 'Median fill'])
    s = df[field].copy()
    changed = s.dropna() if choice == 'Drop missing' else s.fillna(s.mean()) if choice == 'Mean fill' else s.fillna(s.median()) if choice == 'Median fill' else s
    table(pd.DataFrame({'Method':['Original',choice], 'Rows':[len(s),len(changed)],
        'Missing':[s.isna().sum(),changed.isna().sum()], 'Mean':[s.mean(),changed.mean()],
        'Sample SD':[s.std(),changed.std()]}), 'Effect of missing-value treatment')
    st.caption('Mean/median filling can reduce variance. These comparisons are descriptive; predictive preprocessing must be fit on training data only.')

