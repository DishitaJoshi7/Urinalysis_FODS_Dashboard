"""Refresh the three public CDC source files; run explicitly when reproducing downloads."""
from urllib.request import Request,urlopen
from datetime import datetime,timezone
import hashlib
import json
import pandas as pd
from core import ROOT


def main():
    destination=ROOT/'data'/'nhanes'
    destination.mkdir(parents=True,exist_ok=True)
    sources=[]
    for code in ['DIQ_J','DEMO_J','BMX_J']:
        url=f'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/{code}.xpt'
        payload=urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read()
        if not payload.startswith(b'HEADER RECORD'):
            raise ValueError(f'{code}: server returned an unexpected file format.')
        path=destination/(code+'.xpt')
        path.write_bytes(payload)
        frame=pd.read_sas(path,format='xport')
        sources.append({'file':path.name,'url':url,'documentation':url[:-4]+'.htm',
            'retrieved_utc':datetime.now(timezone.utc).isoformat(),'rows':len(frame),
            'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()})
        print(f'{code}: {len(frame):,} rows',flush=True)
    (destination/'sources.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
    print('Run prepare_diabetes.py to regenerate the cohort and model outputs.')


if __name__=='__main__':
    main()
