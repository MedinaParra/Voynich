#!/usr/bin/env python3
import argparse,hashlib,json,math,random,re
from collections import defaultdict
from pathlib import Path
TRAIN_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
TEST_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
SEED=20261007

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def feats(t): return [t.count('o')/len(t),t.count('a')/len(t),t.count('y')/len(t),float(t.startswith('q')),float(t.endswith('y'))]
def clean_tokens(text):
 clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def generic_locus_type(pos):
 m=re.search(r'([PLCR])(?:[A-Za-z0-9]*)',pos)
 return m.group(1) if m else None

def parse(raw):
 pages={}; positives=[]; running=defaultdict(list)
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
   pages[p.group(1)]={'currier':m.get('L','?'),'hand':m.get('H','?')}
   continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]; meta=pages.get(fol,{})
  toks=clean_tokens(text); typ=generic_locus_type(pos)
  if typ=='L' and len(toks)==1 and '?' not in text:
   positives.append({'folio':fol,'token':toks[0],**meta}); continue
  if typ=='P':
   for t in toks:
    running[(fol,meta.get('currier','?'),meta.get('hand','?'),len(t))].append(t)
 return positives,running

def build_pairs(pos,running):
 rng=random.Random(SEED); pairs=[]; excluded=0
 for r in sorted(pos,key=lambda x:(x['folio'],x['token'],x['currier'],x['hand'])):
  key=(r['folio'],r['currier'],r['hand'],len(r['token'])); cand=running.get(key,[])
  if not cand: excluded+=1; continue
  control=cand[rng.randrange(len(cand))]
  pairs.append({'folio':r['folio'],'positive':r['token'],'control':control,'key':key})
 return pairs,excluded

def fit_model(pairs):
 X=[]; y=[]
 for p in pairs:
  X.extend([feats(p['positive']),feats(p['control'])]); y.extend([1,0])
 d=len(X[0]); mu=[sum(x[j] for x in X)/len(X) for j in range(d)]; sd=[]
 for j in range(d):
  v=sum((x[j]-mu[j])**2 for x in X)/len(X); sd.append(math.sqrt(v) if v>0 else 1.0)
 Z=[[(x[j]-mu[j])/sd[j] for j in range(d)] for x in X]
 means={}
 for c in (0,1):
  z=[Z[i] for i,v in enumerate(y) if v==c]
  means[c]=[sum(x[k] for x in z)/len(z) for k in range(d)]
 return mu,sd,means

def d2(a,b): return sum((x-y)**2 for x,y in zip(a,b))
def predict(token,model):
 mu,sd,means=model; x=feats(token); z=[(x[j]-mu[j])/sd[j] for j in range(len(x))]
 return min((0,1),key=lambda c:d2(z,means[c]))

def frozen_predictions(train_pairs,test_pairs):
 pred=[]; models={}; train_counts={}
 for fol in sorted(set(p['folio'] for p in test_pairs)):
  tr=[p for p in train_pairs if p['folio']!=fol]
  if not tr: raise RuntimeError('no Takahashi training pairs after folio exclusion')
  models[fol]=fit_model(tr); train_counts[fol]=len(tr)
 for p in test_pairs:
  model=models[p['folio']]
  pred.append((predict(p['positive'],model),predict(p['control'],model)))
 return pred,models,train_counts

def balanced_accuracy(pred,labels):
 truth=[]; pp=[]
 for i,(pa,pb) in enumerate(pred):
  lab=labels[i]; pp.extend([pa,pb]); truth.extend([lab,1-lab])
 rec=[]
 for c in (0,1):
  ix=[i for i,v in enumerate(truth) if v==c]
  rec.append(sum(pp[i]==c for i in ix)/len(ix))
 return sum(rec)/2

def negative_control(test_pairs,running,models):
 rng1=random.Random(SEED+1); rng2=random.Random(SEED+2); pred=[]; labels=[]; n=0
 for p in test_pairs:
  cand=running.get(tuple(p['key']),[])
  if not cand: continue
  ia=rng1.randrange(len(cand)); ib=rng2.randrange(len(cand))
  if len(cand)>1 and ib==ia: ib=(ib+1)%len(cand)
  model=models[p['folio']]
  pred.append((predict(cand[ia],model),predict(cand[ib],model))); labels.append(1); n+=1
 return balanced_accuracy(pred,labels) if n else None,n

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--training',type=Path,required=True); ap.add_argument('--test',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
 tb=a.training.read_bytes(); xb=a.test.read_bytes(); tsha=blob_sha(tb); xsha=blob_sha(xb)
 if tsha!=TRAIN_BLOB: raise SystemExit(f'frozen training mismatch: {tsha}')
 if xsha!=TEST_BLOB: raise SystemExit(f'frozen test mismatch: {xsha}')
 tpos,trun=parse(tb.decode()); xpos,xrun=parse(xb.decode()); tpairs,tex=build_pairs(tpos,trun); xpairs,xex=build_pairs(xpos,xrun); nfol=len(set(p['folio'] for p in xpairs))
 out={'classification':'REVERSE_ZERO_SHOT_CROSS_TRANSCRIPTION_STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION','training_blob':TRAIN_BLOB,'test_blob':TEST_BLOB,'seed':SEED,'training_positive_tokens':len(tpos),'training_matched_pairs':len(tpairs),'training_excluded_no_match':tex,'test_positive_tokens':len(xpos),'test_matched_pairs':len(xpairs),'test_represented_folios':nfol,'test_excluded_no_match':xex,'permutations_requested':a.permutations}
 if len(xpairs)<60 or nfol<8 or len(tpairs)<60:
  out.update({'status':'BLOCKED','permutations_completed':0,'reason':'preregistered training/test sample threshold not met'}); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return
 pred,models,train_counts=frozen_predictions(tpairs,xpairs); obs=balanced_accuracy(pred,[1]*len(xpairs))
 rng=random.Random(SEED); null=[]
 for _ in range(a.permutations): null.append(balanced_accuracy(pred,[rng.randrange(2) for _ in xpairs]))
 p=(1+sum(x>=obs for x in null))/(1+len(null)); status='PASS' if obs>0.5 and p<=0.05 and len(null)==999 else 'FAIL'
 neg,nneg=negative_control(xpairs,xrun,models)
 out.update({'observed_balanced_accuracy':obs,'null_mean_balanced_accuracy':sum(null)/len(null),'monte_carlo_p':p,'permutations_completed':len(null),'negative_control_balanced_accuracy':neg,'negative_control_pairs':nneg,'min_training_pairs_per_test_folio':min(train_counts.values()),'max_training_pairs_per_test_folio':max(train_counts.values()),'status':status})
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
