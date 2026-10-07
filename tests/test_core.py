"""Check source fidelity, statistical edge cases, and holdout separation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import pytest
from scipy.io import arff
from io import StringIO
from core import read_workbook, manual_pearson, normalization, discretize, regression_experiment, arff_text, grouped_stats


@pytest.fixture(scope='module')
def data():
    return read_workbook()[0]


def test_excel_headers_and_join(data):
    merged=data['Merged_Dataset']
    assert merged.shape==(7936,29)
    assert merged.SEQN.is_unique and merged.SEQN.notna().all()
    assert merged.URDACT.notna().sum()==7632
    assert merged.LBXHGB.notna().sum()==7247
    rebuilt=data['Urine_Albumin_Creatinine'].merge(data['Complete_Blood_Count'],on='SEQN',validate='one_to_one')
    pd.testing.assert_frame_equal(merged.sort_values('SEQN').reset_index(drop=True),
                                  rebuilt.sort_values('SEQN').reset_index(drop=True),check_dtype=False)


def test_manual_pearson_edge_cases():
    assert manual_pearson([1,2,3],[3,2,1])==(-1.0,3)
    assert np.isnan(manual_pearson([1,1],[2,3])[0])
    assert np.isnan(manual_pearson([np.nan,1],[2,3])[0])
    x=pd.Series([1,3,4,np.nan,8]); y=pd.Series([5,7,2,9,10])
    assert manual_pearson(x,y)[0]==pytest.approx(x.corr(y))


def test_normalization_preserves_missing():
    scaled,power=normalization(pd.Series([0.,10.,20.,np.nan]))
    assert scaled['Min-max'].min()==0 and scaled['Min-max'].max()==1
    assert scaled['Z-score'].std(ddof=1)==pytest.approx(1)
    assert scaled.iloc[-1].isna().all()
    assert power==2 and scaled.Decimal.max()<1
    constant,_=normalization(pd.Series([4.,4.,np.nan]))
    assert constant['Min-max'].iloc[0]==0
    assert constant['Z-score'].iloc[0]==0


@pytest.mark.parametrize('method',['K-means','Equal width','Equal frequency'])
def test_discretization_covers_observed(method):
    s=pd.Series([0,1,2,3,4,5,np.nan,9])
    result,_=discretize(s,3,method)
    assert len(result)==s.notna().sum()
    assert result.Bin.ge(1).all()
    assert result.Value.max()==9


def test_grouped_frequency_includes_extremes():
    table,stats=grouped_stats(pd.Series([0,1,2,3,4,100]),3)
    assert table.Frequency.sum()==6
    assert table.Lower.iloc[0]==0 and table.Upper.iloc[-1]==100
    assert np.isfinite(list(stats.values())).all()


def test_regression_split_and_actual_missing(data):
    df=data['Merged_Dataset']
    result=regression_experiment(df,['LBXHGB'])
    assert set(result['train'].SEQN).isdisjoint(set(result['test'].SEQN))
    assert result['missing'].empty and result['unfilled']==689
    assert result['metrics'].iloc[0].RMSE<result['metrics'].iloc[1].RMSE
    # Hide a known value in a copy to exercise genuine-imputation eligibility.
    edited=df.copy()
    index=edited[['LBXHGB','LBXHCT']].dropna().index[0]
    original_value=df.loc[index,'LBXHCT']
    edited.loc[index,'LBXHCT']=np.nan
    fitted=regression_experiment(edited,['LBXHGB'])
    assert len(fitted['missing'])==1
    assert pd.isna(edited.loc[index,'LBXHCT'])
    assert df.loc[index,'LBXHCT']==original_value


def test_arff_roundtrip():
    df=pd.DataFrame({'LBXHGB':[1.,np.nan,3.],'LBXHCT':[2.,4.,6.]})
    rows,metadata=arff.loadarff(StringIO(arff_text(df)))
    assert metadata.names()==['LBXHGB','LBXHCT']
    assert len(rows)==3 and np.isnan(rows['LBXHGB'][1])
