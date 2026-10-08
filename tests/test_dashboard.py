"""Use Streamlit's supported in-process test runner for page and widget coverage."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'app.py'


@pytest.mark.parametrize('page',['overview','explorer','classification','profile','statistics','correlation','regression','transforms','gallery','toolkit'])
def test_pages_render(page):
    at=AppTest.from_file(str(APP),default_timeout=90).run()
    if page!='overview':
        at.switch_page('app_pages/'+page+'.py').run()
    assert not at.exception, [e.message for e in at.exception]


def test_cohort_and_regression_change():
    at=AppTest.from_file(str(APP),default_timeout=90).run()
    at.selectbox(key='status_filter').set_value('Reported diabetes').run()
    assert not at.exception
    assert int(at.metric[0].value.replace(',',''))==836
    at.switch_page('app_pages/regression.py').run()
    at.session_state['regression_mode']='Multiple linear'
    at.run()
    assert not at.exception
    assert any('LBXRBCSI' in code.value for code in at.code)


def test_binning_alternatives_and_gallery():
    at=AppTest.from_file(str(APP),default_timeout=90).run()
    at.switch_page('app_pages/transforms.py').run()
    for method in ['Equal width','Equal frequency']:
        at.session_state['discretization_method']=method
        at.run()
        assert not at.exception
    at.switch_page('app_pages/gallery.py').run()
    at.selectbox[1].set_value('ECDF').run()
    assert not at.exception


def test_profile_and_fixed_classification_cohort():
    at=AppTest.from_file(str(APP),default_timeout=90).run()
    at.selectbox(key='status_filter').set_value('Reported diabetes').run()
    at.switch_page('app_pages/classification.py').run()
    assert not at.exception
    assert at.metric[0].value=='0.820'
    at.switch_page('app_pages/profile.py').run()
    at.button[0].click().run()
    assert not at.exception
    assert at.metric[0].label=='Model score for reported-diabetes class'
