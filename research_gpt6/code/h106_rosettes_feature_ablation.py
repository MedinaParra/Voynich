#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,os
from pathlib import Path
import numpy as np
EXPECTED_SHA='ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d'
REQUIRED={'id','paragraph','token_index','token','x_px','y_px','angle_deg'}
N=9999
EXPECTED=(482,23)
H105={'observed_mae':1.5950207468879667,'null_median_mae':1.675933609958506,'p':0.0049}

def emit(out,status,**kw):
 d={'experiment':'H106 Rosettes spatial lexical-anchor feature ablation','status':status,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'};d.update(kw);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(d,indent=2,sort_keys=True))

def prep(path):
 raw=path.read_bytes(); rows=[]
 with path.open(newline='',encoding='utf-8') as f:
  r=csv.DictReader(f); fields=set(r.fieldnames or [])
  if not REQUIRED<=fields:return raw,fields,[]
  for z in r:
   try:
    tok=z['token'].strip();x=float(z['x_px']);y=float(z['y_px']);a=float(z['angle_deg']);p=int(z['paragraph']);ti=int(z['token_index'])
    if not tok or '?' in tok or not all(map(math.isfinite,[x,y,a])):continue
    rows.append((p,ti,z['id'],x,y,a,len(tok)))
   except Exception:continue
 return raw,fields,rows

def cohort(rows):
 from collections import Counter
 cnt=Counter(r[0] for r in rows);rows=[r for r in rows if cnt[r[0]]>=6];rows.sort(key=lambda r:(r[0],r[1],r[2]));return rows

def features(rows,mode):
 a=[]
 for r in rows:
  pos=[r[3],r[4]];ori=[math.sin(math.radians(r[5])),math.cos(math.radians(r[5]))]
  a.append(pos if mode=='POSITION' else ori if mode=='ORIENTATION' else pos+ori)
 x=np.array(a,float)
 if mode in ('POSITION','COMBINED'):
  for j in (0,1):
   lo=x[:,j].min();hi=x[:,j].max();x[:,j]=(x[:,j]-lo)/(hi-lo) if hi>lo else 0
 return x

def neighbors(x,g):
 out=[]
 for i in range(len(g)):
  ix=np.where(g==g[i])[0];ix=ix[ix!=i];dist=((x[ix]-x[i])**2).sum(1);out.append(ix[np.argsort(dist,kind='stable')[:5]])
 return out

def mae(y,nn):return float(np.mean([abs(y[i]-np.mean(y[n])) for i,n in enumerate(nn)]))
def test(y,g,nn,seed):
 obs=mae(y,nn);rng=np.random.default_rng(seed);vals=np.empty(N);groups=[np.where(g==v)[0] for v in sorted(set(g.tolist()))]
 for k in range(N):
  yp=y.copy()
  for ix in groups:yp[ix]=rng.permutation(yp[ix])
  vals[k]=mae(yp,nn)
 return {'observed_mae':obs,'null_median_mae':float(np.median(vals)),'p':(1+int(np.sum(vals<=obs+1e-15)))/(N+1),'n_permutations':N}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--csv',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 raw,fields,rows=prep(a.csv);sha=hashlib.sha256(raw).hexdigest()
 if sha!=EXPECTED_SHA:return emit(a.out,'BLOCKED',reason='frozen source SHA mismatch',source_sha256=sha)
 if not REQUIRED<=fields:return emit(a.out,'BLOCKED',reason='required columns absent')
 rows=cohort(rows);g=np.array([r[0] for r in rows],int);y=np.array([r[6] for r in rows],float)
 if (len(rows),len(set(g.tolist())))!=EXPECTED:return emit(a.out,'BLOCKED',reason='frozen cohort mismatch',n_rows=len(rows),n_paragraphs=len(set(g.tolist())))
 seeds={'POSITION':20261013,'ORIENTATION':20261014,'COMBINED':20261012};res={}
 for mode in ('POSITION','ORIENTATION','COMBINED'):
  x=features(rows,mode);res[mode]=test(y,g,neighbors(x,g),seeds[mode])
 replay=res['COMBINED']; replay_ok=all(abs(replay[k]-H105[k])<=1e-12 for k in H105)
 if not replay_ok:return emit(a.out,'BLOCKED',reason='H105 exact replay gate failed',source_sha256=sha,n_rows=len(rows),n_paragraphs=len(set(g.tolist())),results=res,expected_h105=H105)
 passed={m:(res[m]['observed_mae']<res[m]['null_median_mae'] and res[m]['p']<=.005) for m in ('POSITION','ORIENTATION')}
 status='PASS' if any(passed.values()) else 'FAIL'
 emit(a.out,status,executing_commit_sha=os.environ.get('GITHUB_SHA','UNKNOWN'),source_sha256=sha,n_rows=len(rows),n_paragraphs=len(set(g.tolist())),results=res,ablation_pass=passed,h105_replay='PASS',seeds=seeds,interpretation_ceiling='Feature attribution of the H105 geometry-to-token-length association only; no semantic or linguistic claim.')
if __name__=='__main__':main()
