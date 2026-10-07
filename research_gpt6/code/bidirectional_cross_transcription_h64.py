#!/usr/bin/env python3
import argparse,hashlib,json,math,random,re
from collections import defaultdict
from pathlib import Path
PRIMARY_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
INDEPENDENT_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
SEED=20261007

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def clean_tokens(text):
 clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
 return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def parse(raw):
 pages={}; positives=[]; running=defaultdict(list)
 for line in raw.splitlines():
  p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
  if p:
   m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
   pages[p.group(1)]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')}
   continue
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m or ',' not in m.group(1): continue
  locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]; meta=pages.get(fol,{})
  toks=clean_tokens(text); lm=re.search(r'(L[A-Za-z]?)',pos)
  if lm and len(toks)==1 and '?' not in text:
   positives.append({'folio':fol,'token':toks[0],**meta}); continue
  if not lm:
   for t in toks: running[(fol,meta.get('currier','?'),meta.get('hand','?'),len(t))].append(t)
 return positives,running,pages

def build_pairs(pos,running,pages):
 rng=random.Random(SEED); pairs=[]; excluded=0
 for r in sorted(pos,key=lambda x:(x['folio'],x['token'],x['currier'],x['hand'])):
  key=(r['folio'],r['currier'],r['hand'],len(r['token'])); cand=running.get(key,[])
  if not cand: excluded+=1; continue
  pairs.append({'folio':r['folio'],'quire':pages.get(r['folio'],{}).get('quire','?'),'positive':r['token'],'control':cand[rng.randrange(len(cand))]})
 return pairs,excluded

def feats(t):
 s=t[1:-1]
 if not s:return [0.0,0.0,0.0]
 return [s.count('o')/len(s),s.count('a')/len(s),s.count('y')/len(s)]
def d2(a,b): return sum((x-y)**2 for x,y in zip(a,b))
def fit_standardizer(X):
 d=len(X[0]); mu=[sum(x[j] for x in X)/len(X) for j in range(d)]; sd=[]
 for j in range(d):
  v=sum((x[j]-mu[j])**2 for x in X)/len(X); sd.append(math.sqrt(v) if v>0 else 1.0)
 return mu,sd
def transform(X,mu,sd): return [[(x[j]-mu[j])/sd[j] for j in range(len(mu))] for x in X]

def eligible_target_quires(source,target):
 tcounts=defaultdict(int)
 for p in target:
  if p['quire']!='?': tcounts[p['quire']]+=1
 out=[]
 for q,n in sorted(tcounts.items()):
  if n<10: continue
  train=[p for p in source if p['quire']!='?' and p['quire']!=q]
  qs=set(p['quire'] for p in train)
  if len(train)>=80 and len(qs)>=4: out.append(q)
 return out

def score_direction(source,target,source_pair_labels=None):
 if source_pair_labels is None: source_pair_labels=[1]*len(source)
 eq=eligible_target_quires(source,target); preds=[]; truth=[]; per={}; ntarget=0
 for q in eq:
  trix=[i for i,p in enumerate(source) if p['quire']!='?' and p['quire']!=q]
  te=[p for p in target if p['quire']==q]
  X=[]; y=[]
  for i in trix:
   p=source[i]; lab=source_pair_labels[i]
   X.extend([feats(p['positive']),feats(p['control'])]); y.extend([lab,1-lab])
  T=[]; yt=[]
  for p in te:
   T.extend([feats(p['positive']),feats(p['control'])]); yt.extend([1,0])
  mu,sd=fit_standardizer(X); Xz=transform(X,mu,sd); Tz=transform(T,mu,sd)
  means={}
  for c in (0,1):
   z=[Xz[j] for j,v in enumerate(y) if v==c]
   means[c]=[sum(x[k] for x in z)/len(z) for k in range(len(z[0]))]
  pp=[min((0,1),key=lambda c:d2(x,means[c])) for x in Tz]
  rec=[]
  for c in (0,1):
   ix=[j for j,v in enumerate(yt) if v==c]; rec.append(sum(pp[j]==c for j in ix)/len(ix))
  per[q]=sum(rec)/2; preds.extend(pp); truth.extend(yt); ntarget+=len(te)
 rec=[]
 for c in (0,1):
  ix=[j for j,v in enumerate(truth) if v==c]; rec.append(sum(preds[j]==c for j in ix)/len(ix))
 return {'ba':sum(rec)/2,'per_quire':per,'evaluable_quires':eq,'target_pairs':ntarget}

def run_direction(source,target,permutations):
 obs=score_direction(source,target)
 if len(obs['evaluable_quires'])<4 or obs['target_pairs']<80:
  return {**obs,'status':'BLOCKED','permutations_completed':0,'reason':'preregistered support threshold not met'}
 rng=random.Random(SEED); null=[]
 for _ in range(permutations):
  labs=[rng.randrange(2) for _ in source]; null.append(score_direction(source,target,labs)['ba'])
 p=(1+sum(x>=obs['ba'] for x in null))/(1+len(null)); above=sum(v>0.5 for v in obs['per_quire'].values())
 status='PASS_CROSS_TRANSCRIPTION_TRANSFER' if len(null)==999 and obs['ba']>0.55 and p<=0.01 and above>=3 else 'FAIL'
 return {**obs,'quires_above_chance':above,'null_mean_ba':sum(null)/len(null),'null_max_ba':max(null),'monte_carlo_p':p,'permutations_completed':len(null),'status':status}

def load(path,expected):
 b=path.read_bytes(); got=blob_sha(b)
 if got!=expected: raise SystemExit(f'frozen corpus mismatch: expected {expected}, got {got}')
 pos,running,pages=parse(b.decode()); pairs,excluded=build_pairs(pos,running,pages)
 return {'blob':got,'positive_tokens':len(pos),'matched_pairs':len(pairs),'excluded_no_match':excluded,'pairs':pairs}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--primary',type=Path,required=True); ap.add_argument('--independent',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
 P=load(a.primary,PRIMARY_BLOB); T=load(a.independent,INDEPENDENT_BLOB)
 pt=run_direction(P['pairs'],T['pairs'],a.permutations); tp=run_direction(T['pairs'],P['pairs'],a.permutations)
 status='PASS_BIDIRECTIONAL_CROSS_TRANSCRIPTION_TRANSFER' if pt['status']=='PASS_CROSS_TRANSCRIPTION_TRANSFER' and tp['status']=='PASS_CROSS_TRANSCRIPTION_TRANSFER' else ('BLOCKED' if 'BLOCKED' in (pt['status'],tp['status']) else 'FAIL')
 out={'classification':'H64_BIDIRECTIONAL_CROSS_TRANSCRIPTION_FUNCTIONAL_NOT_TRANSLATION','seed':SEED,'permutations_requested':a.permutations,'status':status,'primary_source':{k:v for k,v in P.items() if k!='pairs'},'independent_source':{k:v for k,v in T.items() if k!='pairs'},'primary_to_takahashi':pt,'takahashi_to_primary':tp}
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
