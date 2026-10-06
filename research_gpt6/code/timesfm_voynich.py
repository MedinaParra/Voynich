#!/usr/bin/env python3
"""TimesFM structural baseline for Voynich experiments.

This is NOT a decipherment tool. It converts clean IVTFF paragraph lines into
numerical feature sequences and tests zero-shot forecasting of held-out
structural features using the documented TimesFM 2.5 PyTorch API shipped by
the current `timesfm[torch]` package.
"""
import argparse, hashlib, json, math, re
from collections import Counter
from pathlib import Path
import numpy as np

SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
FEATURES = ['tokens','mean_len','uniq_ratio','entropy_char','q_frac','o_frac','y_frac','d_frac','first_q','last_y']
MODEL_ID = 'google/timesfm-2.5-200m-pytorch'

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

def load_timesfm(max_context, horizon):
    import torch, timesfm
    torch.set_float32_matmul_precision('high')
    if not hasattr(timesfm, 'TimesFM_2p5_200M_torch'):
        raise SystemExit('Installed timesfm package does not export TimesFM_2p5_200M_torch')
    model=timesfm.TimesFM_2p5_200M_torch.from_pretrained(MODEL_ID)
    model.compile(timesfm.ForecastConfig(
        max_context=max_context,
        max_horizon=horizon,
        normalize_inputs=True,
        use_continuous_quantile_head=True,
        force_flip_invariance=True,
        infer_is_positive=False,
        fix_quantile_crossing=True,
    ))
    return model

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--corpus',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--horizon',type=int,default=16)
    ap.add_argument('--max-context',type=int,default=512)
    ap.add_argument('--dry-run',action='store_true')
    a=ap.parse_args(); b=a.corpus.read_bytes()
    if git_blob_sha1(b)!=SOURCE_BLOB: raise SystemExit('Corpus blob mismatch; refusing non-frozen input')
    rows=parse_lines(b.decode()); X=np.asarray([r['x'] for r in rows],dtype=np.float32)
    if len(X) <= a.horizon: raise SystemExit('Not enough rows for requested horizon')
    context=X[:-a.horizon][-a.max_context:]
    target=X[-a.horizon:]
    result={'classification':'EXPERIMENTAL_TIMESFM_STRUCTURAL_FORECAST_NOT_DECIPHERMENT','source_blob':SOURCE_BLOB,'features':FEATURES,'rows':len(rows),'shape':list(X.shape),'model':MODEL_ID,'status':'DRY_RUN' if a.dry_run else 'NOT_RUN'}
    if not a.dry_run:
        model=load_timesfm(len(context), len(target))
        # TimesFM is univariate. Forecast each frozen structural feature separately;
        # this avoids pretending that independent feature columns are a native
        # multivariate semantic model.
        inputs=[context[:,j].astype(np.float32) for j in range(context.shape[1])]
        point,_quantiles=model.forecast(horizon=len(target), inputs=inputs)
        point=np.asarray(point,dtype=np.float32)
        if point.shape != (len(FEATURES), len(target)):
            raise SystemExit(f'Unexpected forecast shape {point.shape}')
        pred=point.T
        mse=((pred-target)**2).mean(axis=0)
        # Naive last-value baseline is reported so a foundation model cannot earn
        # credit merely for forecasting an easy smooth statistic.
        naive=np.repeat(context[-1:,:],len(target),axis=0)
        naive_mse=((naive-target)**2).mean(axis=0)
        result.update(
            status='PASS_EXECUTED', horizon=len(target), context=len(context),
            mse_by_feature=dict(zip(FEATURES,map(float,mse))),
            naive_mse_by_feature=dict(zip(FEATURES,map(float,naive_mse))),
            mean_mse=float(mse.mean()), naive_mean_mse=float(naive_mse.mean()),
            beats_naive_mean=bool(mse.mean() < naive_mse.mean()))
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
