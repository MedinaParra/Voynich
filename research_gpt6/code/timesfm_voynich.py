#!/usr/bin/env python3
"""TimesFM 3.0 harness for Voynich structural experiments.

This is NOT a decipherment tool. It converts clean IVTFF paragraph lines into a
multivariate numerical sequence and asks whether TimesFM can forecast held-out
structural features. Physical-order experiments must provide an independently
verified ordering; this script deliberately contains no Layfield/Davis order.
"""
import argparse, hashlib, json, math, re
from collections import Counter
from pathlib import Path
import numpy as np

SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
FEATURES = ['tokens','mean_len','uniq_ratio','entropy_char','q_frac','o_frac','y_frac','d_frac','first_q','last_y']

def git_blob_sha1(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def entropy(chars):
    c=Counter(chars); n=sum(c.values())
    return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0.0

def parse_lines(raw):
    meta={}; out=[]
    for line in raw.splitlines():
        pm=re.match(r'^<([^>.,]+)>\s*<!',line)
        if pm:
            meta=dict(re.findall(r'\$([A-Z])=([^\s>]+)',line)); continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m[1] or not re.search(r'P[0-9a-z]',m[1].split(',',1)[1]): continue
        locus,text=m.groups(); clean=re.sub(r'<[^>]*>','',text)
        if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+',clean): continue
        words=[w for w in re.split(r'[.\s]+',clean.strip()) if w]
        if len(words)<4: continue
        chars=''.join(words); n=len(words)
        def frac(ch): return chars.count(ch)/len(chars) if chars else 0.0
        vec=[n,sum(map(len,words))/n,len(set(words))/n,entropy(chars),frac('q'),frac('o'),frac('y'),frac('d'),sum(w.startswith('q') for w in words)/n,sum(w.endswith('y') for w in words)/n]
        folio=locus.split('.')[0]
        out.append({'locus':locus,'folio':folio,'quire':meta.get('Q'),'x':vec})
    return out

def load_timesfm(device):
    try:
        from timesfm3 import TimesFM3Evaluator, ModelConfig
    except ImportError as e:
        raise SystemExit('TimesFM 3 unavailable. Install official package: pip install "timesfm[torch]"') from e
    cfg=ModelConfig(checkpoint_path='google/timesfm-3.0-pytorch',per_core_batch_size=1,device=device)
    return TimesFM3Evaluator(cfg)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--corpus',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--device',default='cpu')
    ap.add_argument('--horizon',type=int,default=16)
    ap.add_argument('--dry-run',action='store_true')
    a=ap.parse_args(); b=a.corpus.read_bytes()
    if git_blob_sha1(b)!=SOURCE_BLOB: raise SystemExit('Corpus blob mismatch; refusing non-frozen input')
    rows=parse_lines(b.decode()); X=np.asarray([r['x'] for r in rows],dtype=np.float32)
    result={'classification':'EXPERIMENTAL_TIMESFM_STRUCTURAL_FORECAST_NOT_DECIPHERMENT','source_blob':SOURCE_BLOB,'features':FEATURES,'rows':len(rows),'shape':list(X.shape),'device':a.device,'checkpoint':'google/timesfm-3.0-pytorch','status':'DRY_RUN' if a.dry_run else 'NOT_RUN'}
    if not a.dry_run:
        model=load_timesfm(a.device)
        # TimesFM 3 native multivariate interface is intentionally isolated here;
        # fail closed if the installed API differs from the pinned official release.
        if not hasattr(model,'forecast'):
            raise SystemExit('Installed TimesFM API has no forecast method; refusing to guess API')
        context=X[:-a.horizon]
        target=X[-a.horizon:]
        pred=model.forecast(context, horizon_len=len(target))
        pred=np.asarray(pred)
        if pred.shape!=target.shape:
            raise SystemExit(f'Unexpected forecast shape {pred.shape}, expected {target.shape}')
        mse=((pred-target)**2).mean(axis=0)
        result.update(status='PASS_EXECUTED',horizon=len(target),mse_by_feature=dict(zip(FEATURES,map(float,mse))),mean_mse=float(mse.mean()))
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
