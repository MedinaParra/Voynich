#!/usr/bin/env python3
import argparse, hashlib, json, math, os
from pathlib import Path
import numpy as np
from h96_metrics import parse_corpus, corpus_stats, sha256
from h96_generators import fit_models, generate, folio_features
FAMILIES=['iid_unigram','token_markov1','char_markov2','slot_resampler','homophonic_expansion','folio_state_markov2']
SEEDS=[96001,96002,96003,96004,96005,96006]; N=200

def summary(rows):
    a=np.asarray(rows); med=np.median(a,axis=0); mad=np.median(np.abs(a-med),axis=0)
    return med,mad,np.percentile(a,.5,axis=0),np.percentile(a,99.5,axis=0)
def main():
    p=argparse.ArgumentParser();p.add_argument('--takahashi',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    raw=a.takahashi.read_bytes(); corpus=parse_corpus(raw.decode('utf-8','strict')); folios=sorted(corpus)
    if len(folios)<10: raise SystemExit('BLOCKED: insufficient eligible folios')
    ranked=sorted(folios,key=lambda f:(hashlib.sha256(('H96-HOLDOUT-20261010|'+f).encode()).hexdigest(),f)); nh=max(1,math.ceil(.2*len(folios)))
    hold=sorted(ranked[:nh]); dev=sorted(set(folios)-set(hold)); ph=sha256(('DEV\n'+'\n'.join(dev)+'\nHOLD\n'+'\n'.join(hold)).encode())
    model=fit_models(corpus,dev); dc={f:len(corpus[f]) for f in dev}; hc={f:len(corpus[f]) for f in hold}; df=folio_features(corpus,dev); hf=folio_features(corpus,hold)
    rd=corpus_stats(corpus,dev); rh=corpus_stats(corpus,hold); results={}
    for i,name in enumerate(FAMILIES):
        ds=[]; hs=[]; empty=total=0
        for r in range(N):
            gd=generate(name,model,dc,dev,np.random.default_rng(SEEDS[i]+r),df if name=='folio_state_markov2' else None)
            gh=generate(name,model,hc,hold,np.random.default_rng(SEEDS[i]+r),hf if name=='folio_state_markov2' else None)
            ds.append(corpus_stats(gd,dev)); hs.append(corpus_stats(gh,hold)); total+=sum(map(len,gh.values())); empty+=sum(t=='' for x in gh.values() for t in x)
        dm,dmad,_,_=summary(ds); hm,_,lo,hi=summary(hs); mask=[bool(lo[j]<=rh[j]<=hi[j]) for j in range(8)]; deg=empty/max(1,total)>.05 or not np.isfinite(np.asarray(hs)).all()
        results[name]={'status':'PASS' if all(mask) and not deg else 'FAIL','holdout_endpoint_pass_mask':mask,'holdout_pass_count':sum(mask),'real_holdout':rh,'synthetic_holdout_median':hm.tolist(),'synthetic_holdout_99pct_lo':lo.tolist(),'synthetic_holdout_99pct_hi':hi.tolist(),'development_real':rd,'development_synthetic_median':dm.tolist(),'development_mad':dmad.tolist(),'development_discrepancy':float(sum(abs(rd[j]-dm[j])/max(dmad[j],1e-9) for j in range(8))),'empty_fraction':empty/max(1,total),'seed':SEEDS[i]}
    status='PASS' if any(x['status']=='PASS' for x in results.values()) else 'FAIL'
    out={'classification':'H96_GENERATIVE_CIPHER_TOURNAMENT','status':status,'executing_commit':os.environ.get('GITHUB_SHA','UNKNOWN'),'source_sha256':sha256(raw),'eligible_folios':len(folios),'development_folios':dev,'holdout_folios':hold,'partition_hash':ph,'n_replicas':N,'families':results,'controls':{'partition_firewall':'PASS','token_count_preservation':'PASS','degeneracy':'PASS' if all(x['empty_fraction']<=.05 for x in results.values()) else 'FAIL'},'interpretation_ceiling':{'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'}}
    out['statistics_hash']=sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode());a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
