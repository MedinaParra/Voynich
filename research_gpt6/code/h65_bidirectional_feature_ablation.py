#!/usr/bin/env python3
import argparse,hashlib,json,math,random,re
from collections import defaultdict
from pathlib import Path
ZL_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
TAK_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
SEED=20261007
FEATURES=['frac_o','frac_a','frac_y','starts_q','ends_y']
ABLATIONS={f'minus_{name}':[i for i in range(5) if i!=j] for j,name in enumerate(FEATURES)}

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def full_feats(t): return [t.count('o')/len(t),t.count('a')/len(t),t.count('y')/len(t),float(t.startswith('q')),float(t.endswith('y'))]
def clean_tokens(text):
 clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def locus_type(pos):
 m=re.search(r'([PLCR])(?:[A-Za-z0-9]*)',pos); return m.group(1) if m else None

def parse(raw):
 pages={}; pos=[]; running=defaultdict(list)
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2))); pages[p.group(1)]={'currier':m.get('L','?'),'hand':m.get('H','?')}; continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; loc=locus.split(',',1)[1]; meta=pages.get(fol,{})
  toks=clean_tokens(text); typ=locus_type(loc)
  if typ=='L' and len(toks)==1 and '?' not in text:
   pos.append({'folio':fol,'token':toks[0],**meta}); continue
  if typ=='P':
   for t in toks: running[(fol,meta.get('currier','?'),meta.get('hand','?'),len(t))].append(t)
 return pos,running

def pairs(pos,running):
 rng=random.Random(SEED); out=[]; excluded=0
 for r in sorted(pos,key=lambda x:(x['folio'],x['token'],x['currier'],x['hand'])):
  key=(r['folio'],r['currier'],r['hand'],len(r['token'])); cand=running.get(key,[])
  if not cand: excluded+=1; continue
  out.append({'folio':r['folio'],'positive':r['token'],'control':cand[rng.randrange(len(cand))]})
 return out,excluded

def vec(t,idx):
 f=full_feats(t); return [f[i] for i in idx]
def fit(train,idx):
 X=[]; y=[]
 for p in train:
  X.extend([vec(p['positive'],idx),vec(p['control'],idx)]); y.extend([1,0])
 d=len(idx); mu=[sum(x[j] for x in X)/len(X) for j in range(d)]; sd=[]
 for j in range(d):
  v=sum((x[j]-mu[j])**2 for x in X)/len(X); sd.append(math.sqrt(v) if v>0 else 1.0)
 Z=[[(x[j]-mu[j])/sd[j] for j in range(d)] for x in X]; means={}
 for c in (0,1):
  z=[Z[k] for k,v in enumerate(y) if v==c]; means[c]=[sum(x[j] for x in z)/len(z) for j in range(d)]
 return mu,sd,means

def pred_token(t,idx,model):
 mu,sd,means=model; x=vec(t,idx); z=[(x[j]-mu[j])/sd[j] for j in range(len(idx))]
 return min((0,1),key=lambda c:sum((z[j]-means[c][j])**2 for j in range(len(idx))))

def predictions(train,test,idx):
 models={}; counts={}; out=[]
 for fol in sorted(set(p['folio'] for p in test)):
  tr=[p for p in train if p['folio']!=fol]
  if not tr: raise RuntimeError('empty training set after folio exclusion')
  models[fol]=fit(tr,idx); counts[fol]=len(tr)
 for p in test:
  m=models[p['folio']]; out.append((pred_token(p['positive'],idx,m),pred_token(p['control'],idx,m)))
 return out,counts

def ba(pred,labels):
 truth=[]; yhat=[]
 for i,(a,b) in enumerate(pred):
  lab=labels[i]; yhat.extend([a,b]); truth.extend([lab,1-lab])
 rec=[]
 for c in (0,1):
  ix=[i for i,v in enumerate(truth) if v==c]; rec.append(sum(yhat[i]==c for i in ix)/len(ix))
 return sum(rec)/2

def direction(train,test):
 folios=len(set(p['folio'] for p in test))
 if len(train)<60 or len(test)<60 or folios<8:
  return {'status':'BLOCKED','test_pairs':len(test),'test_folios':folios,'permutations_completed':0,'reason':'sample threshold not met'}
 preds={}; counts={}
 for name,idx in ABLATIONS.items(): preds[name],counts[name]=predictions(train,test,idx)
 observed={name:ba(pr,[1]*len(test)) for name,pr in preds.items()}
 rng=random.Random(SEED); null={name:[] for name in ABLATIONS}
 for _ in range(999):
  labels=[rng.randrange(2) for _ in test]
  for name,pr in preds.items(): null[name].append(ba(pr,labels))
 cells={}
 for name in ABLATIONS:
  p=(1+sum(v>=observed[name] for v in null[name]))/1000
  status='PASS' if observed[name]>0.5 and p<=0.05 else 'FAIL'
  cells[name]={'retained_features':[FEATURES[i] for i in ABLATIONS[name]],'observed_balanced_accuracy':observed[name],'null_mean_balanced_accuracy':sum(null[name])/999,'monte_carlo_p':p,'permutations_completed':999,'min_training_pairs_per_test_folio':min(counts[name].values()),'max_training_pairs_per_test_folio':max(counts[name].values()),'status':status}
 return {'test_pairs':len(test),'test_folios':folios,'permutations_completed':999,'cells':cells,'status':'PASS' if all(c['status']=='PASS' for c in cells.values()) else 'FAIL'}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--zl',type=Path,required=True); ap.add_argument('--takahashi',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
 zb=a.zl.read_bytes(); tb=a.takahashi.read_bytes()
 if blob_sha(zb)!=ZL_BLOB: raise SystemExit('frozen ZL mismatch')
 if blob_sha(tb)!=TAK_BLOB: raise SystemExit('frozen Takahashi mismatch')
 zp,zr=parse(zb.decode()); tp,tr=parse(tb.decode()); zpair,zex=pairs(zp,zr); tpair,tex=pairs(tp,tr)
 z2t=direction(zpair,tpair); t2z=direction(tpair,zpair)
 status='BLOCKED' if 'BLOCKED' in (z2t['status'],t2z['status']) else ('PASS' if z2t['status']=='PASS' and t2z['status']=='PASS' else 'FAIL')
 out={'classification':'BIDIRECTIONAL_ZERO_SHOT_LEAVE_ONE_FEATURE_OUT_NOT_TRANSLATION','zl_blob':ZL_BLOB,'takahashi_blob':TAK_BLOB,'seed':SEED,'feature_set':FEATURES,'zl_positive_tokens':len(zp),'zl_matched_pairs':len(zpair),'zl_excluded_no_match':zex,'takahashi_positive_tokens':len(tp),'takahashi_matched_pairs':len(tpair),'takahashi_excluded_no_match':tex,'directions':{'zl_to_takahashi':z2t,'takahashi_to_zl':t2z},'status':status}
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
