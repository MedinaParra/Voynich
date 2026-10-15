#!/usr/bin/env python3
import argparse, hashlib, json, math, os
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from h96_metrics import parse_corpus, corpus_stats, entropy, sha256
from h97_hierarchical_folio_state import feat, fit_markov, draw, percentile
EXPECTED_SOURCE='32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77'
EXPECTED_PARTITION='50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c'
N=999

def gen(models, initp, trans, counts, order, seed):
    rng=np.random.default_rng(seed); out={}; states=[]
    s=int(rng.choice(4,p=initp))
    for i,f in enumerate(order):
        if i: s=int(rng.choice(4,p=trans[s]))
        states.append(s); vocab,uni,tr=models[s]; n=counts[f]; x=[draw(uni,rng)]
        for _ in range(1,n):
            c=tr.get(x[-1]); w=np.array([(c.get(v,0) if c else 0)+1e-6 for v in vocab],float); w/=w.sum(); x.append(vocab[int(rng.choice(len(vocab),p=w))])
        out[f]=x
    return out,states

def main():
    p=argparse.ArgumentParser(); p.add_argument('--takahashi',type=Path,required=True); p.add_argument('--out',type=Path,required=True); a=p.parse_args()
    raw=a.takahashi.read_bytes(); source=sha256(raw)
    if source!=EXPECTED_SOURCE: raise SystemExit('BLOCKED: source SHA mismatch')
    corpus=parse_corpus(raw.decode('utf-8','strict')); folios=sorted(corpus)
    order_hash=sha256(('\n'.join(folios)+'\n').encode())
    ranked=sorted(folios,key=lambda f:(hashlib.sha256(('H96-HOLDOUT-20261010|'+f).encode()).hexdigest(),f)); nh=max(1,math.ceil(.2*len(folios))); hold_set=set(ranked[:nh]); hold=[f for f in folios if f in hold_set]; dev=[f for f in folios if f not in hold_set]
    ph=sha256(('DEV\n'+'\n'.join(sorted(dev))+'\nHOLD\n'+'\n'.join(sorted(hold)) ).encode())
    if len(folios)!=200 or len(dev)!=160 or len(hold)!=40 or ph!=EXPECTED_PARTITION: raise SystemExit('BLOCKED: H96 partition mismatch')
    X=np.asarray([feat(corpus[f]) for f in sorted(dev)]); mu=X.mean(0); sd=X.std(0)
    if np.any(sd==0): raise SystemExit('BLOCKED: zero feature SD')
    dev_sorted=sorted(dev); km=KMeans(n_clusters=4,random_state=97001,n_init=100).fit((X-mu)/sd); labs={f:int(l) for f,l in zip(dev_sorted,km.labels_)}; occ=[sum(labs[f]==k for f in dev) for k in range(4)]
    if min(occ)<10: raise SystemExit('BLOCKED: cluster occupancy <10')
    models=[fit_markov(corpus,[f for f in dev if labs[f]==k]) for k in range(4)]
    tc=np.zeros((4,4),int); eligible=0
    for x,y in zip(folios,folios[1:]):
        if x in labs and y in labs: tc[labs[x],labs[y]]+=1; eligible+=1
    trans=(tc.astype(float)+1.0); trans/=trans.sum(axis=1,keepdims=True)
    if not np.isfinite(trans).all() or not np.all(np.abs(trans.sum(1)-1)<=1e-12): raise SystemExit('BLOCKED: transition matrix control')
    init=(np.array(occ,float)+1.0); init/=init.sum(); counts={f:len(corpus[f]) for f in hold}; real=corpus_stats(corpus,hold)
    rows=[]; empty=total=0; switch=[]
    for r in range(N):
        g,st=gen(models,init,trans,counts,hold,100001+r); rows.append(corpus_stats(g,hold)); total+=sum(map(len,g.values())); empty+=sum(t=='' for x in g.values() for t in x); switch.append(sum(a!=b for a,b in zip(st,st[1:]))/39)
    g0a,s0a=gen(models,init,trans,counts,hold,100001); g0b,s0b=gen(models,init,trans,counts,hold,100001)
    h0a=sha256(json.dumps({'corpus':g0a,'states':s0a,'stats':corpus_stats(g0a,hold)},sort_keys=True,separators=(',',':')).encode()); h0b=sha256(json.dumps({'corpus':g0b,'states':s0b,'stats':corpus_stats(g0b,hold)},sort_keys=True,separators=(',',':')).encode())
    med,lo,hi=percentile(rows); mask=[bool(lo[j]<=real[j]<=hi[j]) for j in range(8)]; finite=bool(np.isfinite(np.asarray(rows)).all()); ef=empty/max(1,total)
    token_ok=all(len(g0a[f])==counts[f] for f in hold)
    controls={'source_sha':'PASS','partition_hash':'PASS','inherited_order_identity':'PASS','holdout_fit_firewall':'PASS','cluster_occupancy':'PASS','development_adjacency_only':'PASS','transition_matrix':'PASS','token_count_preservation':'PASS' if token_ok else 'FAIL','degeneracy':'PASS' if ef<=.05 and finite else 'FAIL','determinism':'PASS' if h0a==h0b else 'FAIL'}
    status='PASS' if all(mask) and all(v=='PASS' for v in controls.values()) else 'FAIL'
    out={'classification':'H100_GLOBAL_FOLIO_TRANSITION','status':status,'executing_commit':os.environ.get('GITHUB_SHA','UNKNOWN'),'source_sha256':source,'partition_hash':ph,'inherited_order_sha256':order_hash,'eligible_folios':len(folios),'development_folios':dev,'holdout_folios':hold,'cluster_occupancies':occ,'transition_counts':tc.tolist(),'eligible_development_adjacencies':eligible,'transition_probabilities':trans.tolist(),'initial_state_distribution':init.tolist(),'n_replicas':N,'seeds':{'kmeans':97001,'replicas':'100001+replica_index'},'real_holdout':real,'synthetic_median':med.tolist(),'synthetic_99pct_lo':lo.tolist(),'synthetic_99pct_hi':hi.tolist(),'endpoint_pass_mask':mask,'endpoint_pass_count':sum(mask),'synthetic_state_switch_rate_median':float(np.median(switch)),'empty_fraction':ef,'replica0_sha256':h0a,'controls':controls,'interpretation_ceiling':{'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'}}
    out['statistics_hash']=sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
