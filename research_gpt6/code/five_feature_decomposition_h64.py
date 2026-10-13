#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import defaultdict
from pathlib import Path

A_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
B_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
SEED=20261007
NAMES=['frac_o','frac_a','frac_y','starts_q','ends_y']
EXPECTED={'A':(780,495,34,285),'B':(669,388,32,281)}

def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def feats(t): return [t.count('o')/len(t),t.count('a')/len(t),t.count('y')/len(t),float(t.startswith('q')),float(t.endswith('y'))]
def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def generic(pos):
    m=re.search(r'([PLCR])(?:[A-Za-z0-9]*)',pos); return m.group(1) if m else None

def parse(raw):
    pages={}; pos=[]; run=defaultdict(list)
    for line in raw.splitlines():
        p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
        if p:
            m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2))); pages[p.group(1)]={'currier':m.get('L','?'),'hand':m.get('H','?')}; continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1): continue
        locus,text=m.groups(); fol=locus.split('.')[0]; po=locus.split(',',1)[1]; meta=pages.get(fol,{})
        toks=clean_tokens(text); lm=re.search(r'(L[A-Za-z]?)',po)
        if lm and len(toks)==1 and '?' not in text:
            pos.append({'folio':fol,'token':toks[0],**meta}); continue
        if generic(po)=='P':
            for t in toks: run[(fol,meta.get('currier','?'),meta.get('hand','?'),len(t))].append(t)
    return pos,run

def pairs_for(raw):
    pos,run=parse(raw); rng=random.Random(SEED); pairs=[]; excluded=0
    for r in sorted(pos,key=lambda x:(x['folio'],x['token'],x['currier'],x['hand'])):
        key=(r['folio'],r['currier'],r['hand'],len(r['token'])); cand=run.get(key,[])
        if not cand: excluded+=1; continue
        pairs.append((r['folio'],r['token'],cand[rng.randrange(len(cand))]))
    return pos,pairs,excluded

def stats(diffs):
    n=len(diffs); out=[]
    for j in range(5):
        x=[d[j] for d in diffs]; mu=sum(x)/n
        if n<2: out.append((mu,0.0)); continue
        var=sum((v-mu)**2 for v in x)/(n-1); se=math.sqrt(var/n)
        t=0.0 if se==0 and mu==0 else (float('inf') if se==0 else abs(mu)/se)
        out.append((mu,t))
    return out

def analyze(pairs,seed,perms):
    diffs=[[a-b for a,b in zip(feats(lp),feats(pp))] for _,lp,pp in pairs]
    obs=stats(diffs); rng=random.Random(seed); maxnull=[]
    for _ in range(perms):
        pd=[]
        for d in diffs:
            s=1 if rng.randrange(2) else -1; pd.append([s*x for x in d])
        st=stats(pd); maxnull.append(max(t for _,t in st))
    feats_out=[]
    for name,(mu,t) in zip(NAMES,obs):
        p=(1+sum(x>=t for x in maxnull))/(1+len(maxnull))
        feats_out.append({'feature':name,'mean_difference_L_minus_P':mu,'studentized_abs_T':t,'p_fwer':p,'direction':'L>P' if mu>0 else ('L<P' if mu<0 else 'ZERO')})
    return feats_out,maxnull

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source-a',type=Path,required=True); ap.add_argument('--source-b',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
    ba=a.source_a.read_bytes(); bb=a.source_b.read_bytes(); out={'classification':'H64_REPLICATED_FIVE_FEATURE_DECOMPOSITION_NOT_TRANSLATION','permutations_requested_each_source':a.permutations,'source_a_blob':blob_sha(ba),'source_b_blob':blob_sha(bb)}
    if blob_sha(ba)!=A_BLOB or blob_sha(bb)!=B_BLOB:
        out.update({'status':'BLOCKED','reason':'frozen source blob mismatch'}); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return
    pa,A,exa=pairs_for(ba.decode()); pb,B,exb=pairs_for(bb.decode()); checks={'A':(len(pa),len(A),len(set(x[0] for x in A)),exa),'B':(len(pb),len(B),len(set(x[0] for x in B)),exb)}; out['reconstruction']=checks
    if checks!=EXPECTED or any(checks[k][1]<60 or checks[k][2]<8 for k in checks):
        out.update({'status':'BLOCKED','reason':'preregistered sample reconstruction mismatch/threshold'}); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2)); return
    fa,na=analyze(A,SEED,a.permutations); fb,nb=analyze(B,SEED+1,a.permutations)
    reps=[]
    for xa,xb in zip(fa,fb):
        same=(xa['direction']==xb['direction'] and xa['direction']!='ZERO'); ok=same and xa['p_fwer']<=0.05 and xb['p_fwer']<=0.05 and len(na)==999 and len(nb)==999
        if ok: reps.append(xa['feature'])
    out.update({'source_a_features':fa,'source_b_features':fb,'source_a_permutations_completed':len(na),'source_b_permutations_completed':len(nb),'replicated_components':reps,'status':'PASS' if reps else 'FAIL','language_identification':'NOT_RUN','semantic_identification':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'})
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
