#!/usr/bin/env python3
import argparse,csv,hashlib,json,math,os
from pathlib import Path
import numpy as np
EXPECTED_SHA='ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d'
REQUIRED={'id','paragraph','token_index','token','x_px','y_px','angle_deg'}
EXPECTED=(482,23); N=9999
H105_MAE=1.5950207468879667

def emit(out,status,**kw):
 d={'experiment':'H107 Rosettes joint-geometry incremental-value test','status':status,'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'};d.update(kw);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps(d,indent=2,sort_keys=True))

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
 return pos,ori

def neighbors(x,g):
 out=[]
 for i in range(len(g)):
  ix=np.where(g==g[i])[0];ix=ix[ix!=i];dist=((x[ix]-x[i])**2).sum(1);out.append(ix[np.argsort(dist,kind='stable')[:5]])
 return out

def errors(y,nn):return np.array([abs(y[i]-np.mean(y[n])) for i,n in enumerate(nn)],float)

def null_test(y,g,pos,ori,reduced_err,observed_d,seed):
 rng=np.random.default_rng(seed);groups=[np.where(g==v)[0] for v in sorted(set(g.tolist()))];vals=np.empty(N)
 for k in range(N):
  op=ori.copy()
  for ix in groups:
   off=int(rng.integers(1,len(ix)));op[ix]=ori[np.roll(ix,off)]
  ce=errors(y,neighbors(np.column_stack([pos,op]),g));vals[k]=float(np.mean(reduced_err-ce))
 return {'observed_D':observed_d,'null_median_D':float(np.median(vals)),'p':(1+int(np.sum(vals>=observed_d-1e-15)))/(N+1),'n_permutations':N}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--csv',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 raw,fields,rows=prep(a.csv);sha=hashlib.sha256(raw).hexdigest()
 if sha!=EXPECTED_SHA:return emit(a.out,'BLOCKED',reason='frozen source SHA mismatch',source_sha256=sha)
 if not REQUIRED<=fields:return emit(a.out,'BLOCKED',reason='required columns absent')
 rows=cohort(rows);g=np.array([r[0] for r in rows],int);y=np.array([r[6] for r in rows],float)
 if (len(rows),len(set(g.tolist())))!=EXPECTED:return emit(a.out,'BLOCKED',reason='frozen cohort mismatch',n_rows=len(rows),n_paragraphs=len(set(g.tolist())))
 pos,ori=arrays(rows);pe=errors(y,neighbors(pos,g));oe=errors(y,neighbors(ori,g));ce=errors(y,neighbors(np.column_stack([pos,ori]),g));combined_mae=float(np.mean(ce))
 if abs(combined_mae-H105_MAE)>1e-12:return emit(a.out,'BLOCKED',reason='H105 exact numerical replay gate failed',combined_mae=combined_mae,expected_h105_mae=H105_MAE)
 dp=float(np.mean(pe-ce));do=float(np.mean(oe-ce))
 rp=null_test(y,g,pos,ori,pe,dp,20261015);ro=null_test(y,g,pos,ori,oe,do,20261016)
 pp=dp>0 and rp['p']<=.005;po=do>0 and ro['p']<=.005;status='PASS' if pp and po else 'FAIL'
 emit(a.out,status,executing_commit_sha=os.environ.get('GITHUB_SHA','UNKNOWN'),source_sha256=sha,n_rows=len(rows),n_paragraphs=len(set(g.tolist())),h105_replay='PASS',mae={'POSITION':float(np.mean(pe)),'ORIENTATION':float(np.mean(oe)),'COMBINED':combined_mae},D_position=rp,D_orientation=ro,incremental_pass={'vs_POSITION':pp,'vs_ORIENTATION':po},seeds={'D_position':20261015,'D_orientation':20261016},interpretation_ceiling='Incremental predictive value of joint spatial representation in the frozen Rosettes dataset only; no semantic or linguistic claim.')
if __name__=='__main__':main()
