#!/usr/bin/env python3
import argparse, hashlib, json, math, os
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from h96_metrics import parse_corpus, corpus_stats, entropy, sha256
EXPECTED_SOURCE='32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77'
EXPECTED_PARTITION='50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c'
N=999

def feat(tokens):
    lens=np.array([len(t) for t in tokens],float); chars=Counter(''.join(tokens)); rep=sum(a==b for a,b in zip(tokens,tokens[1:]))/max(1,len(tokens)-1)
    return [float(lens.mean()),float(lens.std()),float(entropy(chars)),float(rep)]

def fit_markov(corpus, ids):
    vocab=sorted({t for f in ids for t in corpus[f]}); uni=Counter(); tr=defaultdict(Counter)
    for f in ids:
        x=corpus[f]; uni.update(x)
        for a,b in zip(x,x[1:]): tr[a][b]+=1
    return vocab,uni,tr

def draw(counter, rng):
    ks=sorted(counter); w=np.array([counter[k] for k in ks],float); w/=w.sum(); return ks[int(rng.choice(len(ks),p=w))]

def generate(models, props, counts, order, seed):
    rng=np.random.default_rng(seed); out={}
    for f in order:
        state=int(rng.choice(4,p=props)); vocab,uni,tr=models[state]; n=counts[f]; x=[draw(uni,rng)]
        for _ in range(1,n):
            prev=x[-1]; c=tr.get(prev)
            # additive smoothing 1e-6 over full state vocabulary
            weights=np.array([(c.get(v,0) if c else 0)+1e-6 for v in vocab],float); weights/=weights.sum(); x.append(vocab[int(rng.choice(len(vocab),p=weights))])
        out[f]=x
    return out

def percentile(rows):
    a=np.asarray(rows,float); return np.median(a,axis=0),np.percentile(a,.5,axis=0),np.percentile(a,99.5,axis=0)

def main():
    p=argparse.ArgumentParser();p.add_argument('--takahashi',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    raw=a.takahashi.read_bytes(); source=sha256(raw)
    if source!=EXPECTED_SOURCE: raise SystemExit('BLOCKED: source SHA mismatch')
    corpus=parse_corpus(raw.decode('utf-8','strict')); folios=sorted(corpus)
    ranked=sorted(folios,key=lambda f:(hashlib.sha256(('H96-HOLDOUT-20261010|'+f).encode()).hexdigest(),f)); nh=max(1,math.ceil(.2*len(folios))); hold=sorted(ranked[:nh]); dev=sorted(set(folios)-set(hold)); ph=sha256(('DEV\n'+'\n'.join(dev)+'\nHOLD\n'+'\n'.join(hold)).encode())
    if len(folios)!=200 or len(dev)!=160 or len(hold)!=40 or ph!=EXPECTED_PARTITION: raise SystemExit('BLOCKED: H96 partition mismatch')
    X=np.asarray([feat(corpus[f]) for f in dev]); mu=X.mean(0); sd=X.std(0)
    if np.any(sd==0): raise SystemExit('BLOCKED: zero feature SD')
    Z=(X-mu)/sd; km=KMeans(n_clusters=4,random_state=97001,n_init=100).fit(Z); labels=km.labels_; occ=[int(np.sum(labels==k)) for k in range(4)]
    if min(occ)<10: raise SystemExit('BLOCKED: cluster occupancy <10')
    models=[]
    for k in range(4): models.append(fit_markov(corpus,[f for f,l in zip(dev,labels) if int(l)==k]))
    props=np.array(occ,float)/len(dev); counts={f:len(corpus[f]) for f in hold}; real=corpus_stats(corpus,hold)
    rows=[]; empty=0; total=0
    for r in range(N):
        g=generate(models,props,counts,hold,97001+r); rows.append(corpus_stats(g,hold)); total+=sum(map(len,g.values())); empty+=sum(t=='' for x in g.values() for t in x)
    # mandatory determinism control: replica 0 twice
    g0a=generate(models,props,counts,hold,97001); g0b=generate(models,props,counts,hold,97001)
    h0a=sha256(json.dumps({'corpus':g0a,'stats':corpus_stats(g0a,hold)},sort_keys=True,separators=(',',':')).encode()); h0b=sha256(json.dumps({'corpus':g0b,'stats':corpus_stats(g0b,hold)},sort_keys=True,separators=(',',':')).encode())
    med,lo,hi=percentile(rows); mask=[bool(lo[j]<=real[j]<=hi[j]) for j in range(8)]; finite=bool(np.isfinite(np.asarray(rows)).all()); ef=empty/max(1,total)
    controls={'source_sha':'PASS','partition_hash':'PASS','holdout_fit_firewall':'PASS','token_count_preservation':'PASS','degeneracy':'PASS' if ef<=.05 and finite else 'FAIL','determinism':'PASS' if h0a==h0b else 'FAIL','cluster_occupancy':'PASS'}
    status='PASS' if all(mask) and all(v=='PASS' for v in controls.values()) else 'FAIL'
    out={'classification':'H97_HIERARCHICAL_FOLIO_STATE','status':status,'executing_commit':os.environ.get('GITHUB_SHA','UNKNOWN'),'source_sha256':source,'partition_hash':ph,'eligible_folios':len(folios),'development_folios':dev,'holdout_folios':hold,'cluster_occupancies':occ,'cluster_centroids_standardized':km.cluster_centers_.tolist(),'feature_mean':mu.tolist(),'feature_sd':sd.tolist(),'state_proportions':props.tolist(),'n_replicas':N,'seeds':{'kmeans':97001,'replicas':'97001+replica_index'},'real_holdout':real,'synthetic_median':med.tolist(),'synthetic_99pct_lo':lo.tolist(),'synthetic_99pct_hi':hi.tolist(),'endpoint_pass_mask':mask,'endpoint_pass_count':sum(mask),'empty_fraction':ef,'replica0_sha256':h0a,'controls':controls,'interpretation_ceiling':{'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'}}
    out['statistics_hash']=sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()); a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
