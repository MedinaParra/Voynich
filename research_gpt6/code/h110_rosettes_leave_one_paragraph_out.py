#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,os
from collections import Counter
from pathlib import Path
import numpy as np
EXPECTED_SHA256='ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d'
EXPECTED_H105=1.5950207468879667
REQUIRED={'id','paragraph','token_index','token','x_px','y_px','angle_deg'}
N_PERM=9999
SEED=20261020
ALPHA=.005

def emit(out,status,reason=None,**kw):
 d={'experiment':'H110 Rosettes leave-one-paragraph-out geometry-to-length replication','status':status,'executing_commit_sha':os.environ.get('GITHUB_SHA','UNKNOWN'),'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'}
 if reason:d['reason']=reason
 d.update(kw); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); print(json.dumps(d,indent=2,sort_keys=True))

def prep(path):
 raw=path.read_bytes(); rows=[]
 with path.open(newline='',encoding='utf-8') as f:
  r=csv.DictReader(f); fields=set(r.fieldnames or [])
  if not REQUIRED<=fields:return raw,fields,[]
  for z in r:
   try:
    tok=z['token'].strip(); x=float(z['x_px']); y=float(z['y_px']); a=float(z['angle_deg']); p=int(z['paragraph']); ti=int(z['token_index'])
    if not tok or '?' in tok or not all(map(math.isfinite,[x,y,a])):continue
    rows.append((p,ti,z['id'],x,y,a,len(tok)))
   except Exception:continue
 return raw,fields,rows

def build_h105(rows):
 cnt=Counter(r[0] for r in rows); rows=[r for r in rows if cnt[r[0]]>=6]; rows.sort(key=lambda r:(r[0],r[1],r[2]))
 x=np.array([[r[3],r[4],math.sin(math.radians(r[5])),math.cos(math.radians(r[5]))] for r in rows],float); y=np.array([r[6] for r in rows],float); g=np.array([r[0] for r in rows],int)
 xh=x.copy()
 for j in (0,1):
  lo=xh[:,j].min(); hi=xh[:,j].max(); xh[:,j]=(xh[:,j]-lo)/(hi-lo) if hi>lo else 0
 neigh=[]
 for i in range(len(rows)):
  ix=np.where(g==g[i])[0]; ix=ix[ix!=i]; dist=((xh[ix]-xh[i])**2).sum(1); neigh.append(ix[np.argsort(dist,kind='stable')[:5]])
 replay=float(np.mean([abs(y[i]-np.mean(y[n])) for i,n in enumerate(neigh)]))
 return rows,x,y,g,replay

def lopo(x,y,g):
 pred_geo=np.empty(len(y)); pred_base=np.empty(len(y))
 for p in sorted(set(g.tolist())):
  te=np.where(g==p)[0]; tr=np.where(g!=p)[0]
  mu=x[tr].mean(0); sd=x[tr].std(0,ddof=0)
  if np.any(sd==0) or not np.isfinite(sd).all():raise ValueError('zero/nonfinite training feature SD')
  xt=(x[tr]-mu)/sd; xe=(x[te]-mu)/sd
  for pos,i in enumerate(te):
   dist=((xt-xe[pos])**2).sum(1); nn=tr[np.argsort(dist,kind='stable')[:5]]; pred_geo[i]=np.mean(y[nn])
  pred_base[te]=np.mean(y[tr])
 mg=float(np.mean(np.abs(y-pred_geo))); mb=float(np.mean(np.abs(y-pred_base)))
 return mg,mb,mb-mg

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--csv',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
 raw,fields,rawrows=prep(a.csv); sha=hashlib.sha256(raw).hexdigest(); controls={}
 controls['source_sha256_identity']='PASS' if sha==EXPECTED_SHA256 else 'FAIL'; controls['required_columns_present']='PASS' if REQUIRED<=fields else 'FAIL'
 if any(v!='PASS' for v in controls.values()):return emit(a.out,'BLOCKED','source/columns gate failed',controls=controls,source_sha256=sha)
 rows,x,y,g,replay=build_h105(rawrows); controls['cohort_482_tokens']='PASS' if len(rows)==482 else 'FAIL'; controls['cohort_23_paragraphs']='PASS' if len(set(g.tolist()))==23 else 'FAIL'; controls['h105_replay']='PASS' if abs(replay-EXPECTED_H105)<=1e-12 else 'FAIL'
 if any(v!='PASS' for v in controls.values()):return emit(a.out,'BLOCKED','cohort or H105 replay gate failed',controls=controls,source_sha256=sha,n_rows=len(rows),n_paragraphs=len(set(g.tolist())),h105_replay_mae=replay)
 try: mg,mb,dobs=lopo(x,y,g)
 except Exception as e:return emit(a.out,'BLOCKED',str(e),controls=controls,source_sha256=sha)
 rng=np.random.default_rng(SEED); vals=np.empty(N_PERM); groups=[np.where(g==p)[0] for p in sorted(set(g.tolist()))]
 try:
  for k in range(N_PERM):
   yp=y.copy()
   for ix in groups:yp[ix]=rng.permutation(yp[ix])
   vals[k]=lopo(x,yp,g)[2]
 except Exception as e:return emit(a.out,'BLOCKED','permutation pipeline failed: '+str(e),controls=controls,source_sha256=sha)
 pval=(1+int(np.sum(vals>=dobs-1e-15)))/10000
 controls['permutations_9999']='PASS'; controls['finite_outputs']='PASS' if np.isfinite([mg,mb,dobs,pval]).all() else 'FAIL'
 if controls['finite_outputs']!='PASS':return emit(a.out,'BLOCKED','nonfinite output',controls=controls,source_sha256=sha)
 status='PASS' if dobs>0 and pval<ALPHA else 'FAIL'
 emit(a.out,status,controls=controls,source_sha256=sha,n_rows=len(rows),n_paragraphs=len(set(g.tolist())),h105_replay_mae=replay,mae_geometry_lopo=mg,mae_global_lopo=mb,D=dobs,null_median_D=float(np.median(vals)),p=pval,n_permutations=N_PERM,seed=SEED,alpha=ALPHA,interpretation_ceiling='Paragraph-held-out geometry-to-token-length generalization in the frozen Rosettes dataset only.')
if __name__=='__main__':main()
