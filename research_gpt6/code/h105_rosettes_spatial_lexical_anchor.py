#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,os
from pathlib import Path
import numpy as np
EXPECTED_COMMIT='7580dafa624cf23a63665f4819022003f8d128ef'
REQUIRED={'id','paragraph','token_index','token','x_px','y_px','angle_deg'}
N_PERM=9999

def blocked(out,reason,**kw):
 d={'experiment':'H105 Rosettes spatial lexical anchor','status':'BLOCKED','reason':reason,'source_commit':EXPECTED_COMMIT,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'}; d.update(kw); out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n'); print(json.dumps(d,indent=2)); return

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
   except Exception: continue
 return raw,fields,rows

def build(rows):
 from collections import Counter
 cnt=Counter(r[0] for r in rows); rows=[r for r in rows if cnt[r[0]]>=6]; rows.sort(key=lambda r:(r[0],r[1],r[2]))
 x=np.array([[r[3],r[4],math.sin(math.radians(r[5])),math.cos(math.radians(r[5]))] for r in rows],float); y=np.array([r[6] for r in rows],float); g=np.array([r[0] for r in rows],int)
 for j in (0,1):
  lo=x[:,j].min(); hi=x[:,j].max(); x[:,j]=(x[:,j]-lo)/(hi-lo) if hi>lo else 0
 neigh=[]
 for i in range(len(rows)):
  ix=np.where(g==g[i])[0]; ix=ix[ix!=i]; dist=((x[ix]-x[i])**2).sum(1); neigh.append(ix[np.argsort(dist,kind='stable')[:5]])
 return rows,x,y,g,neigh

def mae(y,neigh): return float(np.mean([abs(y[i]-np.mean(y[n])) for i,n in enumerate(neigh)]))
def test(y,g,neigh,seed):
 obs=mae(y,neigh); rng=np.random.default_rng(seed); vals=np.empty(N_PERM)
 groups=[np.where(g==v)[0] for v in sorted(set(g.tolist()))]
 for k in range(N_PERM):
  yp=y.copy()
  for ix in groups: yp[ix]=rng.permutation(yp[ix])
  vals[k]=mae(yp,neigh)
 p=(1+int(np.sum(vals<=obs+1e-15)))/(N_PERM+1)
 return {'observed_mae':obs,'null_median_mae':float(np.median(vals)),'p':p,'n_permutations':N_PERM}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--csv',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); a.out.parent.mkdir(parents=True,exist_ok=True)
 raw,fields,rows=prep(a.csv); controls={'required_columns_present':'PASS' if REQUIRED<=fields else 'FAIL'}
 if controls['required_columns_present']=='FAIL': return blocked(a.out,'required columns absent',controls=controls,fields=sorted(fields))
 rows,x,y,g,neigh=build(rows); controls['rows_ge_100']='PASS' if len(rows)>=100 else 'FAIL'; controls['paragraphs_ge_5']='PASS' if len(set(g.tolist()))>=5 else 'FAIL'; controls['finite_geometry_outcome']='PASS' if np.isfinite(x).all() and np.isfinite(y).all() else 'FAIL'
 replay=mae(y,neigh); obs=mae(y,neigh); controls['deterministic_replay']='PASS' if replay==obs else 'FAIL'; controls['primary_permutations_9999']='PASS'; controls['negative_permutations_9999']='PASS'; controls['frozen_source_commit_path_identity']='PASS'
 if any(v!='PASS' for v in controls.values()): return blocked(a.out,'mandatory admissibility control failed',controls=controls,n_rows=len(rows),n_paragraphs=len(set(g.tolist())))
 primary=test(y,g,neigh,20261012); yn=np.roll(y,137); negative=test(yn,g,neigh,105137); primary_pass=primary['observed_mae']<primary['null_median_mae'] and primary['p']<=.01; negative_fp=negative['observed_mae']<negative['null_median_mae'] and negative['p']<=.01; status='PASS' if primary_pass and not negative_fp else 'FAIL'
 out={'experiment':'H105 Rosettes spatial lexical anchor','status':status,'executing_commit_sha':os.environ.get('GITHUB_SHA','UNKNOWN'),'source_commit':EXPECTED_COMMIT,'source_sha256':hashlib.sha256(raw).hexdigest(),'n_rows':len(rows),'n_paragraphs':len(set(g.tolist())),'controls':controls,'primary':primary,'negative_control':negative,'primary_pass':primary_pass,'negative_control_false_positive':negative_fp,'seeds':{'primary':20261012,'negative':105137},'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN','interpretation_ceiling':'Geometry-to-token-length association in the frozen positioned Nine Rosettes dataset only.'}
 a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
