#!/usr/bin/env python3
import argparse, hashlib, json, math, os
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from h96_metrics import parse_corpus, sha256
from h96_generators import fit_models, generate

N=200
SEED=96002
EXPECTED_SOURCE='32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77'
EXPECTED_PARTITION='50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c'
ALPHA=.5
UNK='<UNK>'

def partition(folios):
    ranked=sorted(folios,key=lambda f:(hashlib.sha256(('H96-HOLDOUT-20261010|'+f).encode()).hexdigest(),f))
    nh=max(1,math.ceil(.2*len(folios))); hold=sorted(ranked[:nh]); dev=sorted(set(folios)-set(hold))
    ph=sha256(('DEV\n'+'\n'.join(dev)+'\nHOLD\n'+'\n'.join(hold)).encode())
    return dev,hold,ph

def fit_predictors(corpus,dev):
    vocab=sorted(set(t for f in dev for t in corpus[f])); vset=set(vocab); V=len(vocab)+1
    unig=Counter(); m1=defaultdict(Counter); m2=defaultdict(Counter)
    for f in dev:
        x=[t if t in vset else UNK for t in corpus[f]]
        unig.update(x)
        for i in range(1,len(x)): m1[x[i-1]][x[i]]+=1
        for i in range(2,len(x)): m2[(x[i-2],x[i-1])][x[i]]+=1
    return {'vocab':vocab,'vset':vset,'V':V,'unig':unig,'m1':m1,'m2':m2}

def prob(counter,token,V):
    return (counter.get(token,0)+ALPHA)/(sum(counter.values())+ALPHA*V)

def evaluate(corpus,hold,model):
    rows=[]; total=[0.,0.,0.]; n=0; unk=0
    for f in hold:
        x=[t if t in model['vset'] else UNK for t in corpus[f]]
        s=[0.,0.,0.]; nf=0; uf=0
        for i in range(2,len(x)):
            y=x[i]; uf+=int(y==UNK); nf+=1; n+=1; unk+=int(y==UNK)
            p0=prob(model['unig'],y,model['V'])
            c1=model['m1'].get(x[i-1]); p1=prob(c1,y,model['V']) if c1 else p0
            c2=model['m2'].get((x[i-2],x[i-1])); p2=prob(c2,y,model['V']) if c2 else p1
            vals=[-math.log(p0),-math.log(p1),-math.log(p2)]
            for j,z in enumerate(vals): s[j]+=z; total[j]+=z
        if nf: rows.append({'folio':f,'n':nf,'nll_unigram':s[0]/nf,'nll_token_m1':s[1]/nf,'nll_token_m2':s[2]/nf,'d10':(s[0]-s[1])/nf,'d21':(s[1]-s[2])/nf,'unk_rate':uf/nf})
    if not n: raise RuntimeError('no eligible prediction positions')
    nll=[z/n for z in total]
    return {'n':n,'nll_unigram':nll[0],'nll_token_m1':nll[1],'nll_token_m2':nll[2],'d10':nll[0]-nll[1],'d21':nll[1]-nll[2],'unk_rate':unk/n,'folios':rows}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--takahashi',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    raw=a.takahashi.read_bytes(); source=sha256(raw)
    if source!=EXPECTED_SOURCE: raise SystemExit('BLOCKED: frozen source hash mismatch '+source)
    corpus=parse_corpus(raw.decode('utf-8','strict')); folios=sorted(corpus); dev,hold,ph=partition(folios)
    if ph!=EXPECTED_PARTITION: raise SystemExit('BLOCKED: frozen partition hash mismatch '+ph)
    observed=evaluate(corpus,hold,fit_predictors(corpus,dev))
    h96model=fit_models(corpus,dev); dc={f:len(corpus[f]) for f in dev}; hc={f:len(corpus[f]) for f in hold}
    null=[]
    for r in range(N):
        gd=generate('token_markov1',h96model,dc,dev,np.random.default_rng(SEED+r))
        gh=generate('token_markov1',h96model,hc,hold,np.random.default_rng(SEED+r))
        ev=evaluate(gh,hold,fit_predictors(gd,dev)); null.append([ev['d10'],ev['d21']])
    arr=np.asarray(null); q99=np.percentile(arr,99,axis=0); med=np.median(arr,axis=0)
    pass10=bool(observed['d10']>0 and observed['d10']>q99[0]); pass21=bool(observed['d21']>0 and observed['d21']>q99[1]); status='PASS' if pass10 and pass21 else 'FAIL'
    out={'classification':'H114_HELDOUT_PREDICTIVE_STRUCTURE','status':status,'executing_commit':os.environ.get('GITHUB_SHA','UNKNOWN'),'source_sha256':source,'eligible_folios':len(folios),'development_folios':dev,'holdout_folios':hold,'partition_hash':ph,'primary_null':'H96_token_markov1','null_seed':SEED,'n_replicas':N,'alpha':ALPHA,'observed':observed,'null_d10_median':float(med[0]),'null_d21_median':float(med[1]),'null_d10_p99':float(q99[0]),'null_d21_p99':float(q99[1]),'d10_pass':pass10,'d21_pass':pass21,'controls':{'source_hash':'PASS','partition_hash':'PASS','train_test_nonempty':'PASS','null_replicas':'PASS' if len(null)==N else 'FAIL'},'diagnostics':{'vocabulary_size':len(fit_predictors(corpus,dev)['vocab'])+1,'eligible_prediction_count':observed['n'],'unk_rate':observed['unk_rate'],'folio_d10_positive_fraction':sum(x['d10']>0 for x in observed['folios'])/len(observed['folios']),'folio_d21_positive_fraction':sum(x['d21']>0 for x in observed['folios'])/len(observed['folios'])},'interpretation_ceiling':{'semantics':'NOT_RUN','language':'NOT_RUN','translation':'NOT_RUN','decipherment':'NOT_RUN'}}
    out['statistics_hash']=sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
