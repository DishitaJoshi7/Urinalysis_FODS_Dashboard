"""Experiment 6: normalization and interpretable one-dimensional discretization."""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from core import measurement_columns, normalization, discretize
from charts import canvas, sns, PALETTE, TEAL
from ui import context, plot, table, csv_button, explain

df,labels=context()
st.caption('FEATURE ANALYSIS · Normalization and discretization')
options=measurement_columns(df)
field=st.selectbox('Measurement',options,index=options.index('LBXHGB'))
normalized,power=normalization(df[field])
st.subheader('One measurement, four scales')
for container,col in zip(st.columns(4),normalized):
    with container:
        fig,ax=canvas(3.6,3)
        sns.histplot(normalized[col].dropna(),bins=25,ax=ax,color=TEAL)
        ax.set(title=col,xlabel=field if col=='Original' else 'Transformed value',ylabel='Count')
        plot(fig,col+' distribution','normalization_'+col)
table(normalized.head(12).round(4).reset_index(names='Source row'),'Original and normalized values')
csv_button(pd.concat([df.SEQN,normalized],axis=1),'Download normalized values','normalized_values')
st.caption(f'Min-max: (x−min)/(max−min). Z-score: (x−mean)/sample SD (ddof=1). Decimal: x/10^{power}. '
           'These are descriptive transforms fit to the selected cohort. For predictive work, fit on training data only.')

st.subheader('Turn continuous values into intervals')
method=st.segmented_control('Discretization method',['K-means','Equal width','Equal frequency'],default='K-means',key='discretization_method')
k=st.slider('Number of bins / clusters',2,8,3)
try:
    binned,edges=discretize(df[field],k,method)
except ValueError as error:
    st.info(str(error))
    st.stop()
left,right=st.columns([1.4,1])
with left:
    fig,ax=canvas(8,4)
    for i in sorted(binned.Bin.unique()):
        part=binned[binned.Bin==i]
        ax.scatter(part.index,part.Value,s=8,alpha=.5,label=f'Bin {i}',color=PALETTE[(i-1)%len(PALETTE)])
    if method=='K-means':
        for center in edges:
            ax.axhline(center,color='#87979a',ls='--',lw=1)
    ax.set(xlabel='Source row index (not time)',ylabel=labels[field])
    ax.legend(ncol=2,frameon=False)
    plot(fig,method+' discretization of '+field,'discretization')
with right:
    table(binned.groupby('Bin').Value.agg(['count','min','max','mean']).reset_index().round(3),'Discretization groups')
    st.caption('Bins are ordered from lower to higher values; they are statistical groups, not clinical categories.')
    table(pd.DataFrame({'Centroid' if method=='K-means' else 'Interval edge':edges}),'Centroids or cut points')
    if method=='Equal frequency' and binned.Bin.nunique()<k:
        st.info('Tied values reduced the number of distinct quantile bins.')
csv_button(df[['SEQN']].join(binned),'Download bin assignments','discretized_values')
with st.expander('K-means elbow plot'):
    # Compute only when requested, keeping ordinary page interactions quick.
    if st.button('Calculate elbow curve'):
        values=df[field].dropna().to_numpy().reshape(-1,1)
        ks=range(1,min(8,len(np.unique(values)))+1)
        inertia=[KMeans(n_clusters=i,n_init=10,random_state=42).fit(values).inertia_ for i in ks]
        fig,ax=canvas()
        ax.plot(list(ks),inertia,marker='o',color=TEAL)
        ax.set(xlabel='Number of clusters',ylabel='Within-cluster sum of squares')
        plot(fig,'Elbow curve for K-means','elbow_curve')
explain('Normalization changes scale but does not make a skewed distribution normal. '
        'K-means groups values by proximity to learned centroids. Equal-width bins partition the range; '
        'equal-frequency bins use quantiles and can collapse when many values are tied. Missing values '
        'remain missing in downloads. Extreme observations are retained and can strongly affect scaling and clusters.')
