#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import defaultdict
from pathlib import Path

SEED_A=20261007
SEED_B=20261008
BLOBS={'A':'2a4533ab9bdfa85db9bad602d590978953055df1','B':'7f491b574b65e5fba6b553e57372c3fa50e10fec'}
STRATA=(6,7)
MIN_EVENTS={6:30,7:15}
MIN_FOLIOS={6:8,7:8}


def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def gtype(pos):
    m=re.search(r'([PLCR])(?:[A-Za-z0-9]*)',pos); return m.group(1) if m else None

def parse(raw):
    pages={}; labels={}; running=defaultdict(list)
    for line in raw.splitlines():
        p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
        if p:
            meta=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p.group(2)))
            pages[p.group(1)]=(meta.get('L','?'),meta.get('H','?')); continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1): continue
        locus,text=m.groups(); fol=locus.split('.')[0]; pos=locus.split(',',1)[1]
        cur,hand=pages.get(fol,('?','?')); toks=clean_tokens(text)
        if re.search(r'(L[A-Za-z]?)',pos) and len(toks)==1 and '?' not in text:
            labels[locus]={'folio':fol,'token':toks[0],'currier':cur,'hand':hand}; continue
        if gtype(pos)=='P':
            for t in toks:
                if len(t)>=5: running[(fol,cur,hand,len(t),t[:2])].append(t)
    return labels,running

def build_common(la,ra,lb,rb):
    events=[]
    for locus in sorted(set(la)&set(lb)):
        a,b=la[locus],lb[locus]
        if a['token']!=b['token'] or a['currier']!=b['currier'] or a['hand']!=b['hand']: continue
        t=a['token']
        if len(t)<5: continue
        key=(a['folio'],a['currier'],a['hand'],len(t),t[:2])
        pa,pb=ra.get(key,[]),rb.get(key,[])
        if not pa or not pb: continue
        events.append({'folio':a['folio'],'label':t,'pool_a':pa,'pool_b':pb})
    return events

def residual(label,pool):
    lab=1.0 if label[4]=='a' else 0.0
    base=sum(1.0 if t[4]=='a' else 0.0 for t in pool)/len(pool)
    return lab-base

def prepare(events,pool_key,length):
    rows=[(e['folio'],residual(e['label'],e[pool_key])) for e in events if len(e['label'])==length]
    by=defaultdict(list)
    for f,r in rows: by[f].append(r)
    fm={f:sum(v)/len(v) for f,v in by.items()}
    return {'events':len(rows),'folios':len(fm),'folio_means':fm,'event_weighted_mean':sum(r for _,r in rows)/len(rows),'equal_folio_mean':sum(fm.values())/len(fm)}

def evaluate(events,pool_key,nperm,seed):
    prep={L:prepare(events,pool_key,L) for L in STRATA}
    allfol=sorted(set().union(*(set(prep[L]['folio_means']) for L in STRATA)))
    obs=sum(prep[L]['equal_folio_mean'] for L in STRATA)/len(STRATA)
    rng=random.Random(seed); null=[]
    for _ in range(nperm):
        signs={f:(1 if rng.randrange(2) else -1) for f in allfol}
        means=[]
        for L in STRATA:
            fm=prep[L]['folio_means']; means.append(sum(fm[f]*signs[f] for f in fm)/len(fm))
        null.append(sum(means)/len(means))
    p=(1+sum(x>=obs for x in null))/(1+len(null))
    return {'strata':{str(L):{'events':prep[L]['events'],'folios':prep[L]['folios'],'equal_folio_mean_residual_a':prep[L]['equal_folio_mean'],'event_weighted_mean_residual_a':prep[L]['event_weighted_mean']} for L in STRATA},'combined_equal_stratum_mean':obs,'null_mean':sum(null)/len(null),'p_one_sided':p,'permutations_completed':len(null)}

def write(path,out):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source-a',type=Path,required=True); ap.add_argument('--source-b',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
    ba,bb=a.source_a.read_bytes(),a.source_b.read_bytes(); out={'classification':'H73_LENGTH_STRATIFIED_LEFT_ANCHOR_NOT_TRANSLATION','source_a_blob':blob_sha(ba),'source_b_blob':blob_sha(bb),'seed_a':SEED_A,'seed_b':SEED_B,'strata':list(STRATA),'permutations_requested_each_source':a.permutations}
    if out['source_a_blob']!=BLOBS['A'] or out['source_b_blob']!=BLOBS['B']:
        out.update(status='BLOCKED',reason='frozen source blob mismatch'); write(a.out,out); return
    la,ra=parse(ba.decode()); lb,rb=parse(bb.decode()); events=build_common(la,ra,lb,rb)
    audit={}
    for L in STRATA:
        es=[e for e in events if len(e['label'])==L]; audit[str(L)]={'events':len(es),'folios':len(set(e['folio'] for e in es)),'minimum_events':MIN_EVENTS[L],'minimum_folios':MIN_FOLIOS[L]}
    out['sample_audit']=audit
    if any(audit[str(L)]['events']<MIN_EVENTS[L] or audit[str(L)]['folios']<MIN_FOLIOS[L] for L in STRATA):
        out.update(status='BLOCKED',reason='preregistered exact-length sample threshold not met'); write(a.out,out); return
    A=evaluate(events,'pool_a',a.permutations,SEED_A); B=evaluate(events,'pool_b',a.permutations,SEED_B); out['source_a']=A; out['source_b']=B
    passed=A['permutations_completed']==999 and B['permutations_completed']==999 and A['combined_equal_stratum_mean']>0 and B['combined_equal_stratum_mean']>0 and A['p_one_sided']<=.05 and B['p_one_sided']<=.05 and all(A['strata'][str(L)]['equal_folio_mean_residual_a']>0 and B['strata'][str(L)]['equal_folio_mean_residual_a']>0 for L in STRATA)
    out['status']='PASS' if passed else 'FAIL'; out.update(language_identification='NOT_RUN',semantic_identification='NOT_RUN',translation='NOT_RUN',decipherment='NOT_RUN'); write(a.out,out)
if __name__=='__main__': main()
