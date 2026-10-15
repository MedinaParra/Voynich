#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,os
from pathlib import Path
import numpy as np
EXPECTED_SHA='ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d'
REQUIRED={'id','paragraph','token_index','token','x_px','y_px','angle_deg'}
EXPECTED=(482,23); N=9999; H105_MAE=1.5950207468879667

def emit(out,status,**kw):
 d={'experiment':'H108 Rosettes paragraph-order confound test','status':status,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'};d.update(kw);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(d,indent=2,sort_keys=True))

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

def arrays(rows):
 pos=np.array([[r[3],r[4]] for r in rows],float)
 for j in (0,1):
  lo=pos[:,j].min();hi=pos[:,j].max();pos[:,j]=(pos[:,j]-lo)/(hi-lo) if hi>lo else 0
 ori=np.array([[math.sin(math.radians(r[5])),math.cos(math.radians(r[5]))] for r in rows],float)
 g=np.array([r[0] for r in rows],int); order=np.zeros(len(rows),float)
 for p in sorted(set(g.tolist())):
  ix=np.where(g==p)[0];v=np.array([rows[i][1] for i in ix],float);lo=v.min();hi=v.max();order[ix]=(v-lo)/(hi-lo) if hi>lo else 0
 sd=order.std();order=(order-order.mean())/sd if sd>0 else np.zeros_like(order)
 return pos,ori,order[:,None]

def neighbors(x,g):
 out=[]
 for i in range(len(g)):
  ix=np.where(g==g[i])[0];ix=ix[ix!=i];dist=((x[ix]-x[i])**2).sum(1);out.append(ix[np.argsort(dist,kind='stable')[:5]])
 return out

def mae(y,x,g):
 nn=neighbors(x,g);return float(np.mean([abs(y[i]-np.mean(y[n])) for i,n in enumerate(nn)]))

def permuted_order(order,g,rng):
 op=order.copy();
 for p in sorted(set(g.tolist())):
  ix=np.where(g==p)[0];off=int(rng.integers(1,len(ix)));op[ix]=order[np.roll(ix,off)]
 return op

def null_geom_over_order(y,g,combined,order,obs,seed):
 rng=np.random.default_rng(seed);vals=np.empty(N)
 for k in range(N):
  op=permuted_order(order,g,rng);vals[k]=mae(y,op,g)-mae(y,np.column_stack([combined,op]),g)
 return {'observed_D':obs,'null_median_D':float(np.median(vals)),'p':(1+int(np.sum(vals>=obs-1e-15)))/(N+1),'n_permutations':N}

def null_order_over_geom(y,g,combined,order,combined_mae,obs,seed):
 rng=np.random.default_rng(seed);vals=np.empty(N)
 for k in range(N):
  op=permuted_order(order,g,rng);vals[k]=combined_mae-mae(y,np.column_stack([combined,op]),g)
 return {'observed_D':obs,'null_median_D':float(np.median(vals)),'p':(1+int(np.sum(vals>=obs-1e-15)))/(N+1),'n_permutations':N}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--csv',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 raw,fields,rows=prep(a.csv);sha=hashlib.sha256(raw).hexdigest()
 if sha!=EXPECTED_SHA:return emit(a.out,'BLOCKED',reason='frozen source SHA mismatch',source_sha256=sha)
 if not REQUIRED<=fields:return emit(a.out,'BLOCKED',reason='required columns absent')
 rows=cohort(rows);g=np.array([r[0] for r in rows],int);y=np.array([r[6] for r in rows],float)
 if (len(rows),len(set(g.tolist())))!=EXPECTED:return emit(a.out,'BLOCKED',reason='frozen cohort mismatch',n_rows=len(rows),n_paragraphs=len(set(g.tolist())))
 pos,ori,order=arrays(rows);combined=np.column_stack([pos,ori]);cm=mae(y,combined,g)
 if abs(cm-H105_MAE)>1e-10:return emit(a.out,'BLOCKED',reason='H105 exact numerical replay gate failed',combined_mae=cm,expected_h105_mae=H105_MAE)
 om=mae(y,order,g);cpo=mae(y,np.column_stack([combined,order]),g);dg=om-cpo;do=cm-cpo
 rg=null_geom_over_order(y,g,combined,order,dg,20261017);ro=null_order_over_geom(y,g,combined,order,cm,do,20261018)
 gp=dg>0 and rg['p']<.005;op=do>0 and ro['p']<.005;status='PASS' if gp else 'FAIL'
 emit(a.out,status,executing_commit_sha=os.environ.get('GITHUB_SHA','UNKNOWN'),source_sha256=sha,n_rows=len(rows),n_paragraphs=len(set(g.tolist())),h105_replay='PASS',mae={'COMBINED':cm,'ORDER':om,'COMBINED_PLUS_ORDER':cpo},D_geom_over_order=rg,D_order_over_geom=ro,geometry_survives_order=gp,order_adds_beyond_geometry=op,seeds={'D_geom_over_order':20261017,'D_order_over_geom':20261018},interpretation_ceiling='Confound test of frozen Rosettes geometry-length association only; no semantic or linguistic claim.')
if __name__=='__main__':main()
