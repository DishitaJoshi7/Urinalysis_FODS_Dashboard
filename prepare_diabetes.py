"""Rebuild diabetes cohort, frozen evaluation, and course-tool exports from local source files."""
import json
from diabetes import load_diabetes,train_models,export_results

if __name__=='__main__':
    print('Loading original workbook and matching CDC records…',flush=True)
    data=load_diabetes()
    print(data['flow'].to_string(index=False),flush=True)
    result=train_models(data['eligible'])
    manifest=export_results(data,result)
    print(json.dumps(manifest,indent=2),flush=True)
