#!/usr/bin/env python3
"""TimesFM structural forecasting tournament for Voynich.

NOT decipherment. Uses a frozen final horizon, tunes only on an earlier
validation horizon, then evaluates exactly once on the untouched final horizon.
"""
import argparse, hashlib, json, math, re
from collections import Counter
from pathlib import Path
import numpy as np

SOURCE_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
FEATURES=['tokens','mean_len','uniq_ratio','entropy_char','q_frac','o_frac','y_frac','d_frac','first_q','last_y']
MODEL_ID='google/timesfm-2.5-200m-pytorch'

def git_blob_sha1(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def entropy(chars):
 c=Counter(chars);n=sum(c.values());return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0.
def parse_lines(raw):
 meta={};out=[]
 for line in raw.splitlines():
  pm=re.match(r'^<([^>.,]+)>\s*<!',line)
  if pm: meta=dict(re.findall(r'\$([A-Z])=([^\s>]+)',line));continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m[1] or not re.search(r'P[0-9a-z]',m[1].split(',',1)[1]):continue
  locus,text=m.groups();clean=re.sub(r'<[^>]*>','',text)
  if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+',clean):continue
  words=[w for w in re.split(r'[.\s]+',clean.strip()) if w]
  if len(words)<4:continue
  chars=''.join(words);n=len(words);frac=lambda ch:chars.count(ch)/len(chars) if chars else 0.
  out.append({'locus':locus,'quire':meta.get('Q'),'x':[n,sum(map(len,words))/n,len(set(words))/n,entropy(chars),frac('q'),frac('o'),frac('y'),frac('d'),sum(w.startswith('q') for w in words)/n,sum(w.endswith('y') for w in words)/n]})
 return out

def load_model(max_context,horizon):
 import torch,timesfm
 torch.set_float32_matmul_precision('high')
 model=timesfm.TimesFM_2p5_200M_torch.from_pretrained(MODEL_ID)
 model.compile(timesfm.ForecastConfig(max_context=max_context,max_horizon=horizon,normalize_inputs=True,use_continuous_quantile_head=True,force_flip_invariance=True,infer_is_positive=False,fix_quantile_crossing=True))
 return model

def forecast(model,context,horizon):
 point,_=model.forecast(horizon=horizon,inputs=[context[:,j].astype(np.float32) for j in range(context.shape[1])])
 return np.asarray(point,dtype=np.float32).T

def mse(a,b):return ((a-b)**2).mean(axis=0)
def skill(m,n):
 denominator=float(n.mean())
 return 1.-float(m.mean())/denominator if denominator>0 else None

def select_validation(val_preds,target,scales):
 """Select context and variant without receiving final-test labels."""
 losses={c:float((mse(p,target)/scales).mean()) for c,p in val_preds.items()}
 ranked=sorted(losses,key=lambda c:(losses[c],c));best=ranked[0];top=ranked[:2]
 variants={'best_context':val_preds[best],'top2_ensemble':np.mean([val_preds[c] for c in top],axis=0)}
 scores={name:float((mse(p,target)/scales).mean()) for name,p in variants.items()}
 primary=min(scores,key=lambda name:(scores[name],name))
 return best,top,primary,scores

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--horizon',type=int,default=16);ap.add_argument('--contexts',default='128,256,512,1024');a=ap.parse_args()
 b=a.corpus.read_bytes()
 if git_blob_sha1(b)!=SOURCE_BLOB:raise SystemExit('Corpus blob mismatch')
 X=np.asarray([r['x'] for r in parse_lines(b.decode())],dtype=np.float32);h=a.horizon
 if h<1:raise SystemExit('Horizon must be positive')
 if len(X)<2*h+128:raise SystemExit('Insufficient rows')
 contexts=[int(x) for x in a.contexts.split(',') if int(x)>0 and int(x)<=len(X)-2*h]
 if not contexts:raise SystemExit('No valid contexts')
 maxc=max(contexts);model=load_model(maxc,h)
 # Validation immediately precedes the frozen final test; final h rows are never used for selection.
 val_target=X[-2*h:-h];val_base=X[:-2*h]
 scales=np.maximum(np.var(val_base,axis=0),1e-8)
 candidates=[];val_preds={}
 for c in contexts:
  ctx=val_base[-c:];p=forecast(model,ctx,h);n=np.repeat(ctx[-1:,:],h,axis=0);mm=mse(p,val_target);nn=mse(n,val_target)
  candidates.append({'context':c,'val_mean_mse':float(mm.mean()),'val_naive_mean_mse':float(nn.mean()),'val_skill':skill(mm,nn)});val_preds[c]=p
 best,top,primary,val_variant_scores=select_validation(val_preds,val_target,scales)
 # Also test an ensemble selected without test labels: mean of top two validation contexts.
 test_target=X[-h:];test_base=X[:-h]
 test_preds={c:forecast(model,test_base[-c:],h) for c in set([best]+top)}
 variants={'best_context':test_preds[best],'top2_ensemble':np.mean([test_preds[c] for c in top],axis=0)}
 naive=np.repeat(test_base[-1:,:],h,axis=0);nm=mse(naive,test_target);evaluated={}
 for name,p in variants.items():
  mm=mse(p,test_target);evaluated[name]={'contexts':([best] if name=='best_context' else top),'mse_by_feature':dict(zip(FEATURES,map(float,mm))),'mean_mse':float(mm.mean()),'naive_mean_mse':float(nm.mean()),'relative_mse_reduction':skill(mm,nm),'features_beating_naive':sum(float(x)<float(y) for x,y in zip(mm,nm))}
 for name,p in variants.items():
  sm=mse(p,test_target)/scales
  evaluated[name]['standardized_mean_mse']=float(sm.mean())
  evaluated[name]['standardized_skill_vs_persistence']=skill(sm,nm/scales)
 mean_pred=np.repeat(test_base.mean(axis=0,keepdims=True),h,axis=0)
 mean_loss=mse(mean_pred,test_target)
 result={'classification':'TIMESFM_EXPLORATORY_STRUCTURAL_FORECAST_NOT_DECIPHERMENT','source_blob':SOURCE_BLOB,'rows':len(X),'features':FEATURES,'model':MODEL_ID,'status':'PASS_EXECUTED','horizon':h,'selection_rule':'context and primary variant chosen only by validation standardized MSE; final test used for reporting, not selection','validation_candidates':candidates,'validation_variant_standardized_mse':val_variant_scores,'primary_variant':primary,'training_variance_scales':list(map(float,scales)),'test_naive_mse_by_feature':dict(zip(FEATURES,map(float,nm))),'test_mean_baseline_standardized_mse':float((mean_loss/scales).mean()),'test_variants':evaluated,'primary_standardized_skill_vs_persistence':evaluated[primary]['standardized_skill_vs_persistence'],'limitations':['Previously inspected final horizon is not a fresh confirmatory holdout.','One final horizon cannot establish cross-folio or cross-quire robustness.','Feature forecasts do not decode symbols or establish semantics.']}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
