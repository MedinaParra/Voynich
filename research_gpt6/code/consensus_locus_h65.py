#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import defaultdict
from pathlib import Path

PRIMARY_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
INDEPENDENT_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
SEED=20261007


def blob_sha(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)


def parse(raw):
    pages={}; loci={}; candidate_labels=0
    for line in raw.splitlines():
        p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
        if p:
            m=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
            pages[p.group(1)]={'quire':m.get('Q','?'),'currier':m.get('L','?'),'hand':m.get('H','?')}
            continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1):
            continue
        locus,text=m.groups(); folio=locus.split('.')[0]; pos=locus.split(',',1)[1]
        toks=clean_tokens(text); is_label=bool(re.search(r'(L[A-Za-z]?)',pos))
        uncertain='?' in text
        if is_label and len(toks)==1 and not uncertain:
            candidate_labels+=1
        loci[locus]={'folio':folio,'pos':pos,'tokens':toks,'is_label':is_label,'uncertain':uncertain,'text':text}
    return pages,loci,candidate_labels


def build_consensus(primary, independent):
    pp,pl,pc=parse(primary); ip,il,ic=parse(independent)
    positives=[]; running=defaultdict(list); consensus_loci=0; metadata_disagreements=0
    common=set(pl).intersection(il)
    for locus in sorted(common):
        a,b=pl[locus],il[locus]
        if a['uncertain'] or b['uncertain'] or a['tokens']!=b['tokens']:
            continue
        folio=a['folio']
        if folio!=b['folio']:
            continue
        ma=pp.get(folio,{}); mb=ip.get(folio,{})
        meta=(ma.get('quire','?'),ma.get('currier','?'),ma.get('hand','?'))
        if meta!=(mb.get('quire','?'),mb.get('currier','?'),mb.get('hand','?')):
            metadata_disagreements+=1; continue
        consensus_loci+=1
        quire,currier,hand=meta
        if a['is_label']!=b['is_label']:
            continue
        if a['is_label'] and len(a['tokens'])==1:
            positives.append({'locus':locus,'folio':folio,'token':a['tokens'][0],'quire':quire,'currier':currier,'hand':hand})
        elif not a['is_label']:
            for t in a['tokens']:
                running[(folio,currier,hand,len(t))].append(t)
    rng=random.Random(SEED); pairs=[]; excluded=0
    for r in sorted(positives,key=lambda x:(x['locus'],x['token'])):
        key=(r['folio'],r['currier'],r['hand'],len(r['token']))
        cand=sorted(running.get(key,[]))
        if not cand:
            excluded+=1; continue
        pairs.append({'folio':r['folio'],'quire':r['quire'],'positive':r['token'],'control':cand[rng.randrange(len(cand))]})
    return {
        'pages_primary':len(pp),'pages_independent':len(ip),'loci_primary':len(pl),'loci_independent':len(il),
        'candidate_labels_primary':pc,'candidate_labels_independent':ic,'common_loci':len(common),
        'exact_consensus_loci':consensus_loci,'metadata_disagreements':metadata_disagreements,
        'consensus_positive_loci':len(positives),'matched_pairs':pairs,'excluded_no_match':excluded
    }


def feats(t):
    s=t[1:-1]
    if not s:
        return [0.0,0.0,0.0]
    return [s.count('o')/len(s),s.count('a')/len(s),s.count('y')/len(s)]


def d2(a,b):
    return sum((x-y)**2 for x,y in zip(a,b))


def standardize(train,test):
    d=len(train[0]); mu=[]; sd=[]
    for j in range(d):
        m=sum(x[j] for x in train)/len(train); mu.append(m)
        v=sum((x[j]-m)**2 for x in train)/len(train); sd.append(math.sqrt(v) if v>0 else 1.0)
    z=lambda X:[[(x[j]-mu[j])/sd[j] for j in range(d)] for x in X]
    return z(train),z(test)


def score(pairs,quires,labels=None):
    if labels is None:
        labels=[1]*len(pairs)
    preds=[]; truth=[]; per={}
    for q in quires:
        tr=[i for i,p in enumerate(pairs) if p['quire'] in quires and p['quire']!=q]
        te=[i for i,p in enumerate(pairs) if p['quire']==q]
        if not tr or not te:
            continue
        X=[]; y=[]; T=[]; yt=[]
        for i in tr:
            p=pairs[i]; lab=labels[i]
            X.extend([feats(p['positive']),feats(p['control'])]); y.extend([lab,1-lab])
        for i in te:
            p=pairs[i]; lab=labels[i]
            T.extend([feats(p['positive']),feats(p['control'])]); yt.extend([lab,1-lab])
        X,T=standardize(X,T); means={}
        for c in (0,1):
            z=[X[j] for j,v in enumerate(y) if v==c]
            means[c]=[sum(x[k] for x in z)/len(z) for k in range(len(z[0]))]
        pp=[min((0,1),key=lambda c:d2(x,means[c])) for x in T]
        recalls=[]
        for c in (0,1):
            ix=[j for j,v in enumerate(yt) if v==c]
            recalls.append(sum(pp[j]==c for j in ix)/len(ix))
        per[q]=sum(recalls)/2; preds.extend(pp); truth.extend(yt)
    recalls=[]
    for c in (0,1):
        ix=[j for j,v in enumerate(truth) if v==c]
        recalls.append(sum(preds[j]==c for j in ix)/len(ix))
    return sum(recalls)/2,per


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--primary',type=Path,required=True); ap.add_argument('--independent',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999)
    a=ap.parse_args(); pb=a.primary.read_bytes(); ib=a.independent.read_bytes()
    pg=blob_sha(pb); ig=blob_sha(ib)
    if pg!=PRIMARY_BLOB: raise SystemExit(f'primary blob mismatch: {pg}')
    if ig!=INDEPENDENT_BLOB: raise SystemExit(f'independent blob mismatch: {ig}')
    c=build_consensus(pb.decode(),ib.decode()); pairs=c.pop('matched_pairs')
    counts=defaultdict(int)
    for p in pairs: counts[p['quire']]+=1
    eq=sorted(q for q,n in counts.items() if q!='?' and n>=10)
    ep=[p for p in pairs if p['quire'] in eq]
    out={'classification':'H65_EXACT_CONSENSUS_FUNCTIONAL_NOT_SEMANTIC','seed':SEED,'primary_blob':pg,'independent_blob':ig,**c,
         'quire_pair_counts':dict(sorted(counts.items())),'evaluable_quires':eq,'evaluable_pairs':len(ep),'permutations_requested':a.permutations}
    denom=max(c['candidate_labels_primary'],1)
    out['consensus_label_survival_fraction_vs_primary']=c['consensus_positive_loci']/denom
    if len(eq)<4 or len(ep)<80:
        out.update(status='BLOCKED',permutations_completed=0,reason='exact-consensus support below frozen threshold')
    else:
        obs,perq=score(ep,eq); rng=random.Random(SEED); null=[]
        for _ in range(a.permutations):
            labs=[rng.randrange(2) for _ in ep]
            null.append(score(ep,eq,labs)[0])
        pval=(1+sum(x>=obs for x in null))/(1+len(null)); above=sum(v>0.5 for v in perq.values())
        status='PASS_CONSENSUS_FUNCTIONAL_REPLICATION' if len(null)==999 and obs>0.55 and pval<=0.01 and above>=3 else 'FAIL'
        out.update(status=status,observed_balanced_accuracy=obs,per_quire_balanced_accuracy=perq,quires_above_chance=above,
                   null_mean_ba=sum(null)/len(null),null_max_ba=max(null),monte_carlo_p=pval,permutations_completed=len(null))
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
