#!/usr/bin/env python3
import argparse,hashlib,json,random,re
from collections import defaultdict
from pathlib import Path

PRIMARY_BLOB='2a4533ab9bdfa85db9bad602d590978953055df1'
INDEPENDENT_BLOB='7f491b574b65e5fba6b553e57372c3fa50e10fec'
PRIMARY_SEED=20261007
INDEPENDENT_SEED=20261008


def blob_sha(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)


def parse(raw):
    pages={}; positives=[]; running=defaultdict(list); candidate_labels=0
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
        toks=clean_tokens(text); is_label=bool(re.search(r'(L[A-Za-z]?)',pos)); uncertain='?' in text
        meta=pages.get(folio,{'quire':'?','currier':'?','hand':'?'})
        if is_label and len(toks)==1 and not uncertain:
            candidate_labels+=1
            positives.append({'locus':locus,'folio':folio,'token':toks[0],**meta})
        elif not is_label:
            for t in toks:
                running[(folio,meta['currier'],meta['hand'],len(t))].append(t)
    return pages,positives,running,candidate_labels


def build_pairs(raw,seed):
    pages,positives,running,candidate_labels=parse(raw)
    rng=random.Random(seed); pairs=[]; excluded=0
    for r in sorted(positives,key=lambda x:(x['locus'],x['token'])):
        key=(r['folio'],r['currier'],r['hand'],len(r['token']))
        cand=sorted(running.get(key,[]))
        if not cand:
            excluded+=1; continue
        pairs.append({'locus':r['locus'],'folio':r['folio'],'quire':r['quire'],'label':r['token'],'control':cand[rng.randrange(len(cand))]})
    return pages,pairs,candidate_labels,excluded


def starts_q(t): return 1 if t.startswith('q') else 0

def delta(pairs):
    if not pairs:return 0.0
    return sum(starts_q(p['label'])-starts_q(p['control']) for p in pairs)/len(pairs)


def sign(x): return 1 if x>0 else (-1 if x<0 else 0)


def run_one(path,expected_blob,pair_seed,permutations):
    b=path.read_bytes(); got=blob_sha(b)
    if got!=expected_blob: raise SystemExit(f'frozen corpus mismatch: expected {expected_blob}, got {got}')
    pages,pairs,candidate_labels,excluded=build_pairs(b.decode(),pair_seed)
    counts=defaultdict(int)
    for p in pairs: counts[p['quire']]+=1
    eq=sorted(q for q,n in counts.items() if q!='?' and n>=10)
    ep=[p for p in pairs if p['quire'] in eq]
    out={'source_blob':got,'parsed_folios':len(pages),'candidate_labels':candidate_labels,'matched_pairs_all':len(pairs),
         'excluded_no_match':excluded,'quire_pair_counts':dict(sorted(counts.items())),'evaluable_quires':eq,
         'evaluable_pairs':len(ep),'pair_selection_seed':pair_seed,'permutations_requested':permutations}
    if len(eq)<4 or len(ep)<80:
        out.update(status='BLOCKED',reason='frozen support gate not met',permutations_completed=0); return out
    obs=delta(ep); label_prev=sum(starts_q(p['label']) for p in ep)/len(ep); control_prev=sum(starts_q(p['control']) for p in ep)/len(ep)
    byq={q:delta([p for p in ep if p['quire']==q]) for q in eq}; s=sign(obs); same=sum(sign(v)==s for v in byq.values()) if s else 0
    rng=random.Random(pair_seed); null=[]
    for _ in range(permutations):
        d=0
        for p in ep:
            z=starts_q(p['label'])-starts_q(p['control'])
            d += z if rng.randrange(2)==0 else -z
        null.append(d/len(ep))
    pval=(1+sum(abs(x)>=abs(obs) for x in null))/(1+len(null))
    positive=(len(null)==999 and abs(obs)>=0.05 and pval<=0.01 and same>=3)
    out.update(status='POSITIVE' if positive else 'NEGATIVE',label_q_prevalence=label_prev,control_q_prevalence=control_prev,
               observed_delta_q=obs,per_quire_delta_q=byq,quires_same_direction=same,null_mean_delta_q=sum(null)/len(null),
               null_max_abs_delta_q=max(abs(x) for x in null),monte_carlo_p_two_sided=pval,permutations_completed=len(null))
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--primary',type=Path,required=True); ap.add_argument('--independent',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
    p=run_one(a.primary,PRIMARY_BLOB,PRIMARY_SEED,a.permutations); i=run_one(a.independent,INDEPENDENT_BLOB,INDEPENDENT_SEED,a.permutations)
    if 'BLOCKED' in (p.get('status'),i.get('status')): status='BLOCKED'
    else:
        same_sign=sign(p.get('observed_delta_q',0))==sign(i.get('observed_delta_q',0)) and sign(p.get('observed_delta_q',0))!=0
        status='PASS_REPLICATED_Q_REGISTER' if p.get('status')=='POSITIVE' and i.get('status')=='POSITIVE' and same_sign else 'FAIL'
    out={'classification':'H68_DUAL_TRANSCRIPTION_Q_INITIAL_PAIRED_PREVALENCE_NOT_SEMANTIC','status':status,
         'primary':p,'independent':i,'same_effect_direction':(sign(p.get('observed_delta_q',0))==sign(i.get('observed_delta_q',0)) and sign(p.get('observed_delta_q',0))!=0)}
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
