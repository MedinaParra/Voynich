#!/usr/bin/env python3
"""Test whether prefix substitutions have stable contextual effects across shared stems.
Exploratory morphology only; no semantic glosses or translation claims.
"""
import argparse, hashlib, json, math, re
from collections import Counter, defaultdict
from pathlib import Path
BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
PREFIXES=('qok','pol','sol','ych','ysh','dsh','ch','sh','qo','ok','ot')
def gitblob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def js(a,b):
 keys=set(a)|set(b); sa=sum(a.values()); sb=sum(b.values())
 if not sa or not sb:return 0.0
 p={k:a[k]/sa for k in keys};q={k:b[k]/sb for k in keys};m={k:(p[k]+q[k])/2 for k in keys}
 def kl(x):return sum(v*math.log2(v/m[k]) for k,v in x.items() if v and m[k])
 return (kl(p)+kl(q))/2

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--min-pair',type=int,default=4);a=ap.parse_args();b=a.corpus.read_bytes()
 if gitblob(b)!=BLOB:raise SystemExit('Corpus blob mismatch')
 seqs=[]
 for line in b.decode().splitlines():
  m=re.match(r'^<([^>]+)>\s*(.*)$',line)
  if not m:continue
  clean=re.sub(r'<[^>]*>','',m.group(2))
  if ',' in m.group(2) or '<->' in m.group(2) or not re.fullmatch(r'[a-z.\s]+',clean):continue
  w=[x for x in re.split(r'[.\s]+',clean.strip()) if x]
  if w:seqs.append(w)
 contexts=defaultdict(Counter);counts=Counter();forms=defaultdict(Counter)
 for w in seqs:
  for i,x in enumerate(w):
   pref=next((p for p in PREFIXES if x.startswith(p) and len(x)>len(p)+1),None)
   if not pref:continue
   stem=x[len(pref):];key=(pref,stem);counts[key]+=1;forms[stem][pref]+=1
   if i:contexts[key]['L:'+w[i-1]]+=1
   if i+1<len(w):contexts[key]['R:'+w[i+1]]+=1
 shared=[]
 for stem,pc in forms.items():
  eligible=[p for p,n in pc.items() if n>=a.min_pair]
  if len(eligible)<2:continue
  for i,p1 in enumerate(eligible):
   for p2 in eligible[i+1:]:
    shared.append({'stem':stem,'prefix_a':p1,'prefix_b':p2,'n_a':counts[(p1,stem)],'n_b':counts[(p2,stem)],'context_js':js(contexts[(p1,stem)],contexts[(p2,stem)])})
 shared.sort(key=lambda z:(z['context_js'],min(z['n_a'],z['n_b'])),reverse=True)
 pairagg=defaultdict(list)
 for r in shared:pairagg[tuple(sorted((r['prefix_a'],r['prefix_b'])))].append(r['context_js'])
 summary=[]
 for pair,vals in pairagg.items():
  if len(vals)>=2:summary.append({'prefix_pair':list(pair),'shared_stems':len(vals),'mean_context_js':sum(vals)/len(vals),'min_context_js':min(vals),'max_context_js':max(vals)})
 summary.sort(key=lambda z:(z['shared_stems'],z['mean_context_js']),reverse=True)
 res={'classification':'EXPLORATORY_COMPOSITIONAL_MORPHOLOGY_NOT_TRANSLATION','source_blob':BLOB,'min_pair_count':a.min_pair,'shared_stem_comparisons':len(shared),'prefix_pair_summary':summary,'top_shared_stem_contrasts':shared[:80],'interpretation_rule':'Repeated prefix effects across >=2 independently recurring stems are candidates for compositional function; contextual differences alone do not identify meaning.','status':'PASS_EXECUTED'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'shared_stem_comparisons':len(shared),'top_prefix_pairs':summary[:12]},indent=2))
if __name__=='__main__':main()
