#!/usr/bin/env python3
import argparse,hashlib,json,random,re
from collections import defaultdict
from pathlib import Path

PRIMARY_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
INDEPENDENT_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
PRIMARY_SEED=20261009
INDEPENDENT_SEED=20261010


def blob_sha(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text)
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)


def starts_q(t):
    return 1 if t.startswith('q') else 0


def parse(raw):
    pages={}; labels=defaultdict(list); running=defaultdict(list); candidate_labels=0
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
        meta=pages.get(folio,{'quire':'?','currier':'?','hand':'?'})
        is_label=bool(re.search(r'(L[A-Za-z]?)',pos)); uncertain='?' in text
        toks=clean_tokens(text)
        if is_label and len(toks)==1 and not uncertain:
            candidate_labels+=1
            t=toks[0]; key=(folio,meta['currier'],meta['hand'],len(t)); labels[key].append(t)
        elif not is_label and not uncertain:
            for t in toks:
                key=(folio,meta['currier'],meta['hand'],len(t)); running[key].append(t)
    return pages,labels,running,candidate_labels


def make_specs(pages,labels,running):
    specs=[]; quire_counts=defaultdict(int); excluded_labels=0
    for key,labs in labels.items():
        runs=running.get(key,[])
        if not runs:
            excluded_labels+=len(labs); continue
        folio=key[0]; q=pages.get(folio,{}).get('quire','?')
        quire_counts[q]+=len(labs)
        ql=sum(starts_q(t) for t in labs); qr=sum(starts_q(t) for t in runs)
        nL=len(labs); nR=len(runs); nT=nL+nR; qT=ql+qr
        specs.append({'key':key,'quire':q,'nL':nL,'nR':nR,'nT':nT,'qL':ql,'qR':qr,'qT':qT})
    return specs,quire_counts,excluded_labels


def cond_d(specs):
    n=sum(s['nL'] for s in specs)
    if not n:return 0.0
    return sum(s['qL'] - s['nL']*s['qT']/s['nT'] for s in specs)/n


def perm_d(specs,rng):
    n=sum(s['nL'] for s in specs); resid=0.0
    for s in specs:
        picks=rng.sample(range(s['nT']),s['nL'])
        pseudo_q=sum(1 for x in picks if x < s['qT'])
        resid += pseudo_q - s['nL']*s['qT']/s['nT']
    return resid/n


def run_one(path,expected_blob,seed,permutations):
    b=path.read_bytes(); got=blob_sha(b)
    if got!=expected_blob: raise SystemExit(f'frozen corpus mismatch: expected {expected_blob}, got {got}')
    pages,labels,running,candidate_labels=parse(b.decode()); specs,counts,excluded=make_specs(pages,labels,running)
    eq=sorted(q for q,n in counts.items() if q!='?' and n>=10)
    es=[s for s in specs if s['quire'] in eq]
    nlabels=sum(s['nL'] for s in es); nrun=sum(s['nR'] for s in es)
    out={'source_blob':got,'parsed_folios':len(pages),'candidate_labels':candidate_labels,'excluded_labels_no_running_stratum':excluded,
         'quire_label_counts':dict(sorted(counts.items())),'evaluable_quires':eq,'included_exact_strata':len(es),
         'included_label_instances':nlabels,'included_running_instances':nrun,'seed':seed,'permutations_requested':permutations}
    if len(eq)<4 or nlabels<80 or len(es)<20:
        out.update(status='BLOCKED',reason='frozen support gate not met',permutations_completed=0); return out
    obs=cond_d(es); perq={q:cond_d([s for s in es if s['quire']==q]) for q in eq}; neg=sum(v<0 for v in perq.values())
    qlabels=sum(s['qL'] for s in es); qruns=sum(s['qR'] for s in es)
    rng=random.Random(seed); null=[perm_d(es,rng) for _ in range(permutations)]
    pval=(1+sum(abs(x)>=abs(obs) for x in null))/(1+len(null))
    positive=(len(null)==999 and obs<=-0.05 and pval<=0.01 and neg>=3)
    out.update(status='POSITIVE' if positive else 'NEGATIVE',observed_conditional_D=obs,
               raw_label_q_prevalence=qlabels/nlabels,raw_running_q_prevalence=qruns/nrun,
               per_quire_conditional_D=perq,quires_negative=neg,null_mean_D=sum(null)/len(null),
               null_max_abs_D=max(abs(x) for x in null),monte_carlo_p_two_sided=pval,permutations_completed=len(null))
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--primary',type=Path,required=True); ap.add_argument('--independent',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
    p=run_one(a.primary,PRIMARY_BLOB,PRIMARY_SEED,a.permutations); i=run_one(a.independent,INDEPENDENT_BLOB,INDEPENDENT_SEED,a.permutations)
    if 'BLOCKED' in (p.get('status'),i.get('status')): status='BLOCKED'
    else: status='PASS_EXACT_STRATUM_Q_DEPLETION' if p.get('status')=='POSITIVE' and i.get('status')=='POSITIVE' else 'FAIL'
    out={'classification':'H69_EXACT_STRATUM_Q_INITIAL_CONDITIONAL_NOT_SEMANTIC','status':status,'primary':p,'independent':i}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
