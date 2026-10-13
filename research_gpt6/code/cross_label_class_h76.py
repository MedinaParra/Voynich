#!/usr/bin/env python3
import argparse, hashlib, json, random, re
from collections import Counter, defaultdict
from pathlib import Path

SEED_A=20261007
SEED_B=20261008
BLOBS={'A':'2a4533ab9bdfa85db9bad602d590978953055df1','B':'7f491b574b65e5fba6b553e57372c3fa50e10fec'}
MIN_CLASS_EVENTS=15
MIN_CLASS_FOLIOS=6
MIN_TOTAL_EVENTS=40
MIN_TOTAL_FOLIOS=12
CLASSES={'ZODIAC':{'Lz'},'PHARMA':{'Lc','Lf'}}


def blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;',' ',text).replace('?',' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])',clean)
def gtype(pos):
    m=re.search(r'([PLCR])(?:[A-Za-z0-9]*)',pos); return m.group(1) if m else None
def ltype(pos):
    m=re.search(r'(L[A-Za-z0-9]?)',pos); return m.group(1) if m else None

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
        cur,hand=pages.get(fol,('?','?')); toks=clean_tokens(text); lt=ltype(pos)
        if lt and len(toks)==1 and '?' not in text:
            labels[locus]={'folio':fol,'token':toks[0],'currier':cur,'hand':hand,'ltype':lt}; continue
        if gtype(pos)=='P':
            for t in toks:
                if len(t)>=6: running[(fol,cur,hand,len(t),t[:2])].append(t)
    return labels,running

def class_of(lt):
    for name,types in CLASSES.items():
        if lt in types: return name
    return None

def build_common(la,ra,lb,rb):
    events=[]
    for locus in sorted(set(la)&set(lb)):
        a,b=la[locus],lb[locus]
        if a['ltype']!=b['ltype']: continue
        cls=class_of(a['ltype'])
        if not cls: continue
        if a['token']!=b['token'] or a['currier']!=b['currier'] or a['hand']!=b['hand']: continue
        t=a['token']
        if len(t)<6: continue
        key=(a['folio'],a['currier'],a['hand'],len(t),t[:2])
        pa,pb=ra.get(key,[]),rb.get(key,[])
        if not pa or not pb: continue
        events.append({'folio':a['folio'],'label':t,'ltype':a['ltype'],'class':cls,'prefix':t[:2],'pool_a':pa,'pool_b':pb})
    return events

def residual(label,pool):
    lab=1.0 if label[4]=='a' else 0.0
    base=sum(1.0 if t[4]=='a' else 0.0 for t in pool)/len(pool)
    return lab-base

def class_summary(rows):
    by=defaultdict(list)
    for e,r in rows: by[e['folio']].append(r)
    fm={f:sum(v)/len(v) for f,v in by.items()}
    eq=sum(fm.values())/len(fm)
    ew=sum(r for _,r in rows)/len(rows)
    pref=Counter(e['prefix'] for e,_ in rows)
    subtype=defaultdict(list)
    for e,r in rows: subtype[e['ltype']].append(r)
    subdesc={lt:{'events':len(v),'mean_residual_a':sum(v)/len(v)} for lt,v in sorted(subtype.items()) if len(v)>=5}
    return {'events':len(rows),'folios':len(fm),'equal_folio_mean_residual_a':eq,'event_weighted_mean_residual_a':ew,'folio_means':fm,'prefix_counts':dict(sorted(pref.items())),'subtype_descriptive':subdesc}

def evaluate(events,pool_key,nperm,seed):
    rows_by_class={c:[] for c in CLASSES}
    for e in events: rows_by_class[e['class']].append((e,residual(e['label'],e[pool_key])))
    summaries={c:class_summary(rows_by_class[c]) for c in CLASSES}
    obs=sum(summaries[c]['equal_folio_mean_residual_a'] for c in CLASSES)/len(CLASSES)
    allfol=sorted(set().union(*(set(summaries[c]['folio_means']) for c in CLASSES)))
    rng=random.Random(seed); null=[]
    for _ in range(nperm):
        signs={f:(1 if rng.randrange(2) else -1) for f in allfol}; means=[]
        for c in CLASSES:
            fm=summaries[c]['folio_means']; means.append(sum(fm[f]*signs[f] for f in fm)/len(fm))
        null.append(sum(means)/len(means))
    p=(1+sum(x>=obs for x in null))/(1+len(null))
    clean={}
    for c,s in summaries.items():
        clean[c]={k:v for k,v in s.items() if k!='folio_means'}
    return {'classes':clean,'equal_class_weighted_mean_residual_a':obs,'null_mean':sum(null)/len(null),'p_one_sided':p,'permutations_completed':len(null)}

def write(path,out):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source-a',type=Path,required=True); ap.add_argument('--source-b',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
    ba,bb=a.source_a.read_bytes(),a.source_b.read_bytes(); out={'classification':'H76_CROSS_LABEL_CLASS_NOT_TRANSLATION','source_a_blob':blob_sha(ba),'source_b_blob':blob_sha(bb),'seed_a':SEED_A,'seed_b':SEED_B,'frozen_classes':{'ZODIAC':['Lz'],'PHARMA':['Lc','Lf']},'minimum_class_events':MIN_CLASS_EVENTS,'minimum_class_folios':MIN_CLASS_FOLIOS,'minimum_total_events':MIN_TOTAL_EVENTS,'minimum_total_folios':MIN_TOTAL_FOLIOS,'permutations_requested_each_source':a.permutations}
    if out['source_a_blob']!=BLOBS['A'] or out['source_b_blob']!=BLOBS['B']:
        out.update(status='BLOCKED',reason='frozen source blob mismatch'); write(a.out,out); return
    la,ra=parse(ba.decode()); lb,rb=parse(bb.decode()); events=build_common(la,ra,lb,rb)
    audit={}
    for c in CLASSES:
        ev=[e for e in events if e['class']==c]; audit[c]={'events':len(ev),'folios':len(set(e['folio'] for e in ev)),'subtype_counts':dict(sorted(Counter(e['ltype'] for e in ev).items()))}
    out['sample_audit']=audit; out['total_events']=len(events); out['total_unique_folios']=len(set(e['folio'] for e in events))
    blocked=out['total_events']<MIN_TOTAL_EVENTS or out['total_unique_folios']<MIN_TOTAL_FOLIOS or any(audit[c]['events']<MIN_CLASS_EVENTS or audit[c]['folios']<MIN_CLASS_FOLIOS for c in CLASSES)
    if blocked:
        out.update(status='BLOCKED',reason='preregistered cross-class sample threshold not met'); write(a.out,out); return
    A=evaluate(events,'pool_a',a.permutations,SEED_A); B=evaluate(events,'pool_b',a.permutations,SEED_B); out['source_a']=A; out['source_b']=B
    passed=A['permutations_completed']==999 and B['permutations_completed']==999 and A['equal_class_weighted_mean_residual_a']>0 and B['equal_class_weighted_mean_residual_a']>0 and A['p_one_sided']<=.05 and B['p_one_sided']<=.05 and all(A['classes'][c]['equal_folio_mean_residual_a']>0 and B['classes'][c]['equal_folio_mean_residual_a']>0 for c in CLASSES)
    out['status']='PASS' if passed else 'FAIL'; out.update(language_identification='NOT_RUN',semantic_identification='NOT_RUN',translation='NOT_RUN',decipherment='NOT_RUN'); write(a.out,out)
if __name__=='__main__': main()
