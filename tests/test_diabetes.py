"""Check cohort provenance, label coding, leakage controls and nominal tool exports."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import pytest
from scipy.io import arff
from diabetes import load_diabetes,train_models,derive_target,FEATURES,TARGET,ROOT


@pytest.fixture(scope='module')
def data():
    return load_diabetes()


@pytest.fixture(scope='module')
def trained(data):
    return train_models(data['eligible'])


def test_unknown_labels_are_not_negative():
    labels=derive_target(pd.Series([1,2,3,7,9,np.nan]))
    assert labels.iloc[:2].tolist()==[1,0]
    assert labels.iloc[2:].isna().all()


def test_original_data_and_adult_cohort(data):
    original=data['sheets']['Merged_Dataset']
    pd.testing.assert_frame_equal(data['joined'][original.columns],original)
    df=data['eligible']
    assert len(df)==5098 and df[TARGET].sum()==836
    assert df.SEQN.is_unique and df.RIDAGEYR.ge(20).all()
    assert df.DIQ010.isin([1,2]).all()
    assert not df.DIQ010.eq(3).any()


def test_disjoint_splits_and_train_only_medians(trained):
    splits=trained['splits']
    train,val,test=[set(splits[k].SEQN) for k in ['train','validation','test']]
    assert not (train&val or train&test or val&test)
    assert len(train|val|test)==5098
    assert [len(splits[k]) for k in ['train','validation','test']]==[3058,1020,1020]
    assert all(s[TARGET].nunique()==2 for s in splits.values())
    for info in trained['models'].values():
        expected=splits['train'][info['features']].median().to_numpy()
        actual=info['pipeline'].named_steps['imputer'].statistics_
        np.testing.assert_allclose(actual,expected)
    forbidden={TARGET,'SEQN','DIQ010','DIQ050','DIQ070','URXUMS','URXCRS'}
    assert forbidden.isdisjoint(FEATURES)


def test_selection_and_recorded_metrics(trained):
    validation=trained['validation_metrics']
    best=validation.loc[validation.Model!='Class-prior baseline'].sort_values('Average precision',ascending=False).iloc[0].Model
    assert trained['winner']==best
    assert trained['winner']=='Labs + demographics forest'
    row=trained['test_metrics'].set_index('Model').loc[best]
    assert int(row.TN+row.FP+row.FN+row.TP)==1020
    assert row['ROC AUC']==pytest.approx(.8200574232543121)
    assert trained['thresholds'][best]==pytest.approx(.46)


def test_weka_nominal_class_and_export_membership(trained):
    folder=ROOT/'exports'/'diabetes'
    for name in ['train','validation','test']:
        values,metadata=arff.loadarff(folder/f'{name}.arff')
        assert metadata.names()[-1]==TARGET
        assert metadata[TARGET]==('nominal',('no','yes'))
        assert len(values)==len(trained['splits'][name])
        ids=pd.read_csv(folder/f'{name}_ids.csv').SEQN
        assert ids.tolist()==trained['splits'][name].SEQN.tolist()
        assert not pd.read_csv(folder/f'{name}.csv').isna().any().any()
