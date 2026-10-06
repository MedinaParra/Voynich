#!/usr/bin/env python3
"""Rolling-origin TimesFM robustness test; structural forecast, not decipherment."""
import argparse,hashlib,json,math,re
from collections import Counter
from pathlib import Path
import numpy as np
BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'; MODEL='google/timesfm-2.5-200m-pytorch'
def sha(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def entropy(s):
 c=Counter(s);n=len(s);return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0
def parse(raw):
 out=[]
 for line in raw.splitlines():
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m[1] or not re.search(r'P[0-9a-z]',m[1].split(',',1)[1]):continue
  text=m[2];clean=re.sub(r'<[^>]*>','',text)
  if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+',clean):continue
  w=[x for x in re.split(r'[.\s]+',clean.strip()) if x]
  if len(w)<4:continue
  s=''.join(w);n=len(w);f=lambda x:s.count(x)/len(s)
  out.append([n,sum(map(len,w))/n,len(set(w))/n,entropy(s),f('q'),f('o'),f('y'),f('d'),sum(x.startswith('q') for x in w)/n,sum(x.endswith('y') for x in w)/n])
 return np.asarray(out,dtype=np.float32)
def main():
 p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--context',type=int,default=128);p.add_argument('--horizon',type=int,default=16);p.add_argument('--folds',type=int,default=8);a=p.parse_args();b=a.corpus.read_bytes()
 if sha(b)!=BLOB:raise SystemExit('Corpus blob mismatch')
 X=parse(b.decode());import torch,timesfm;torch.set_float32_matmul_precision('high')
 m=timesfm.TimesFM_2p5_200M_torch.from_pretrained(MODEL);m.compile(timesfm.ForecastConfig(max_context=a.context,max_horizon=a.horizon,normalize_inputs=True,use_continuous_quantile_head=True,force_flip_invariance=True,infer_is_positive=False,fix_quantile_crossing=True))
 rr=[]
 for k in range(a.folds,0,-1):
  end=len(X)-a.horizon*(k-1);start=end-a.horizon
  ctx=X[start-a.context:start];y=X[start:end];point,_=m.forecast(horizon=a.horizon,inputs=[ctx[:,j] for j in range(ctx.shape[1])]);pred=np.asarray(point).T;naive=np.repeat(ctx[-1:,:],a.horizon,axis=0)
  pm=((pred-y)**2).mean(axis=0);nm=((naive-y)**2).mean(axis=0);r=1-float(pm.mean())/float(nm.mean());rr.append({'start':start,'end':end,'skill':r,'features_beating_naive':int(sum(pm<nm))})
 skills=np.array([x['skill'] for x in rr]);res={'classification':'TIMESFM_ROLLING_STRUCTURAL_ROBUSTNESS_NOT_DECIPHERMENT','source_blob':BLOB,'model':MODEL,'context':a.context,'horizon':a.horizon,'folds':len(rr),'fold_results':rr,'mean_relative_mse_reduction':float(skills.mean()),'median_relative_mse_reduction':float(np.median(skills)),'min_relative_mse_reduction':float(skills.min()),'max_relative_mse_reduction':float(skills.max()),'folds_beating_naive':int(sum(skills>0)),'mean_target_exceeds_63pct':bool(skills.mean()>0.63),'status':'PASS_EXECUTED'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
if __name__=='__main__':main()
