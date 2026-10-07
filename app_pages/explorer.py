"""Experiments 1 and 2: Pandas inspection, filtering, joins, cleaning, NumPy."""
import io
import numpy as np
import pandas as pd
import streamlit as st
from core import measurement_columns
from ui import context, table, csv_button

df, labels = context()
st.caption('EXPERIMENTS 01–02 · Data handling with Pandas and NumPy')
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

with st.expander('Pandas operations and the SEQN join'):
    sheets = st.session_state.sheets
    rebuilt = sheets['Urine_Albumin_Creatinine'].merge(sheets['Complete_Blood_Count'], on='SEQN',
                how='inner', validate='one_to_one')
    st.write(f'Urine table: {len(sheets["Urine_Albumin_Creatinine"]):,} rows. '
             f'CBC table: {len(sheets["Complete_Blood_Count"]):,} rows. '
             f'One-to-one inner join: {len(rebuilt):,} rows.')
    st.code('df.head()\ndf.tail()\ndf.shape\ndf.info()\ndf.describe()\n'
            'df.loc[df["URDACT"] > 30, ["SEQN", "URDACT"]]\n'
            'df.iloc[:10, :5]\ndf.isna().sum()\n'
            'urine.merge(cbc, on="SEQN", how="inner", validate="one_to_one")', language='python')
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())

with st.expander('Compare cleaning choices without changing the original data'):
    choice = st.selectbox('Teaching method', ['Keep missing', 'Drop missing', 'Mean fill', 'Median fill'])
    s = df[field].copy()
    changed = s.dropna() if choice == 'Drop missing' else s.fillna(s.mean()) if choice == 'Mean fill' else s.fillna(s.median()) if choice == 'Median fill' else s
    table(pd.DataFrame({'Method':['Original',choice], 'Rows':[len(s),len(changed)],
        'Missing':[s.isna().sum(),changed.isna().sum()], 'Mean':[s.mean(),changed.mean()],
        'Sample SD':[s.std(),changed.std()]}), 'Effect of teaching imputation choices')
    st.caption('Mean/median filling can reduce variance. These comparisons are descriptive; predictive preprocessing must be fit on training data only.')

with st.expander('NumPy: arrays, slicing, broadcasting, aggregation'):
    values = observed.to_numpy()
    table(pd.DataFrame({'First 8 values':values[:8], 'Centered (broadcast subtract mean)':values[:8]-values.mean()}), 'NumPy array example')
    st.code('values = df[field].dropna().to_numpy()\nvalues[:8]\nvalues - np.mean(values)\n'
            'np.mean(values), np.median(values), np.std(values, ddof=1)\nnp.unique(values)', language='python')
    st.write({'Mean': float(np.mean(values)), 'Median':float(np.median(values)),
              'Sample SD':float(np.std(values,ddof=1)), 'Unique values':int(len(np.unique(values)))})
