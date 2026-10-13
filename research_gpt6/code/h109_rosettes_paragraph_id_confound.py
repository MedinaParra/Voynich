#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,os
from pathlib import Path
import numpy as np
EXPECTED_SHA='ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d'
REQUIRED={'id','paragraph','token_index','token','x_px','y_px','angle_deg'}
EXPECTED=(482,23); N=9999; H105_MAE=1.5950207468879667

def emit(out,status,**kw):
 d={'experiment':'H109 Rosettes paragraph-identity confound test','status':status,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'};d.update(kw);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(d,indent=2,sort_keys=True))

def prep(path):
 raw=path.read_bytes();rows=[]
 with path.open(newline='',encoding='utf-8') as f:
  r=csv.DictReader(f);fields=set(r.fieldnames or [])
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

def geometry(rows):
 pos=np.array([[r[3],r[4]] for r in rows],float)
 for j in (0,1):
  lo=pos[:,j].min();hi=pos[:,j].max();pos[:,j]=(pos[:,j]-lo)/(hi-lo) if hi>lo else 0
 ori=np.array([[math.sin(math.radians(r[5])),math.cos(math.radians(r[5]))] for r in rows],float)
 return np.column_stack([pos,ori])

def geom_mae(y,x,g):
 errs=[]
 for i in range(len(g)):
  ix=np.where(g==g[i])[0];ix=ix[ix!=i];dist=((x[ix]-x[i])**2).sum(1);nn=ix[np.argsort(dist,kind='stable')[:5]];errs.append(abs(y[i]-np.mean(y[nn])))
 return float(np.mean(errs))

def paragraph_mae(y,g):
 errs=[]
 for i in range(len(g)):
  ix=np.where(g==g[i])[0];ix=ix[ix!=i]
  if len(ix)<1: raise ValueError('paragraph has fewer than 2 eligible tokens')
  errs.append(abs(y[i]-np.mean(y[ix])))
 return float(np.mean(errs))

def rotate_geometry(x,g,rng):
 xp=x.copy()
 for p in sorted(set(g.tolist())):
  ix=np.where(g==p)[0]
  if len(ix)>1:
   off=int(rng.integers(1,len(ix)));xp[ix]=x[np.roll(ix,off)]
 return xp

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--csv',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 raw,fields,rows=prep(a.csv);sha=hashlib.sha256(raw).hexdigest()
 if sha!=EXPECTED_SHA:return emit(a.out,'BLOCKED',reason='frozen source SHA mismatch',source_sha256=sha)
 if not REQUIRED<=fields:return emit(a.out,'BLOCKED',reason='required columns absent')
 rows=cohort(rows);g=np.array([r[0] for r in rows],int);y=np.array([r[6] for r in rows],float)
 if (len(rows),len(set(g.tolist())))!=EXPECTED:return emit(a.out,'BLOCKED',reason='frozen cohort mismatch',n_rows=len(rows),n_paragraphs=len(set(g.tolist())))
 if any(np.sum(g==p)<2 for p in set(g.tolist())):return emit(a.out,'BLOCKED',reason='paragraph has fewer than 2 eligible tokens')
 x=geometry(rows);cm=geom_mae(y,x,g)
 if abs(cm-H105_MAE)>1e-10:return emit(a.out,'BLOCKED',reason='H105 exact numerical replay gate failed',combined_mae=cm,expected_h105_mae=H105_MAE)
 pm=paragraph_mae(y,g)
 # Under within-paragraph 5-NN, training-only paragraph residualization plus adding the same training mean back is algebraically identical to geometry KNN; compute explicitly as frozen model value.
 cpm=cm;obs=pm-cpm
 rng=np.random.default_rng(20261019);vals=np.empty(N)
 for k in range(N): vals[k]=pm-geom_mae(y,rotate_geometry(x,g,rng),g)
 pval=(1+int(np.sum(vals>=obs-1e-15)))/(N+1)
 status='PASS' if obs>0 and pval<.005 else 'FAIL'
 emit(a.out,status,executing_commit_sha=os.environ.get('GITHUB_SHA','UNKNOWN'),source_sha256=sha,n_rows=len(rows),n_paragraphs=len(set(g.tolist())),h105_replay='PASS',mae={'COMBINED':cm,'PARAGRAPH':pm,'COMBINED_PLUS_PARAGRAPH':cpm},D={'observed':obs,'null_median':float(np.median(vals)),'p':pval,'n_permutations':N},seed=20261019,alpha=.005,interpretation_ceiling='Confound test of frozen Rosettes geometry-length association only; no semantic or linguistic claim.')
if __name__=='__main__':main()
