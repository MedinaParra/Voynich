#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re, subprocess
from collections import Counter, defaultdict

EXPECTED='2a4533ab9bdfa85db9bad602d590978953055df1'
PAIRS=[('ch','sh'),('ok','qok')]
SEED=20261007

def blob(path):
    return subprocess.check_output(['git','hash-object',path],text=True).strip()

def js(a,b):
    keys=set(a)|set(b)
    sa=sum(a.values()); sb=sum(b.values())
    if not keys or not sa or not sb: return 0.0
    pa={k:a.get(k,0)/sa for k in keys}; pb={k:b.get(k,0)/sb for k in keys}
    m={k:(pa[k]+pb[k])/2 for k in keys}
    def kl(p): return sum(v*math.log(v/m[k],2) for k,v in p.items() if v>0 and m[k]>0)
    return (kl(pa)+kl(pb))/2

def parse(path):
    meta={'Q':'?','L':'?','H':'?','I':'?'}; obs=[]; stats=Counter()
    with open(path,encoding='utf-8',errors='ignore') as f:
        for raw in f:
            stats['lines_total']+=1
            for k,v in re.findall(r'\$([QLHI])=([^\s>]+)',raw): meta[k]=v
            m=re.match(r'^<([^>]+)>\s*(.*)$',raw.rstrip('\n'))
            if not m: continue
            locus,text=m.groups(); clean=re.sub(r'<[^>]*>','',text)
            if ',' in text or '<->' in text or not re.fullmatch(r'[a-z.\s]+',clean):
                stats['lines_skipped_syntax']+=1; continue
            toks=[t for t in re.split(r'[.\s]+',clean) if t]
            if toks: stats['lines_used']+=1
            folio=locus.split('.')[0].split(',')[0]
            n=len(toks)
            for i,t in enumerate(toks):
                stats['tokens_total']+=1
                if i==0 or i==n-1:
                    stats['tokens_boundary_excluded']+=1; continue
                posbin='early' if i/max(1,n-1)<.34 else ('late' if i/max(1,n-1)>.66 else 'middle')
                for p1,p2 in PAIRS:
                    p=None
                    if t.startswith(p1) and len(t)>len(p1)+1: p=p1
                    elif t.startswith(p2) and len(t)>len(p2)+1: p=p2
                    if p:
                        obs.append({'pair':p1+'/'+p2,'prefix':p,'stem':t[len(p):], 'left':toks[i-1], 'right':toks[i+1], 'folio':folio,'Q':meta['Q'],'L':meta['L'],'H':meta['H'],'I':meta['I'],'pos':posbin})
                        break
    return obs,stats

def eligible(rows,min_form=3):
    c=Counter((r['stem'],r['prefix']) for r in rows)
    bypair=defaultdict(list)
    for r in rows: bypair[r['pair']].append(r)
    out={}
    for pair,rs in bypair.items():
        a,b=pair.split('/')
        stems=sorted({r['stem'] for r in rs if c[(r['stem'],a)]>=min_form and c[(r['stem'],b)]>=min_form})
        out[pair]=stems
    return out

def statistic(rows,stems,pair):
    a,b=pair.split('/'); vals=[]
    for s in stems:
        aa=[r for r in rows if r['stem']==s and r['prefix']==a]; bb=[r for r in rows if r['stem']==s and r['prefix']==b]
        if not aa or not bb: continue
        ca=Counter(); cb=Counter()
        for r in aa: ca.update(('L:'+r['left'],'R:'+r['right']))
        for r in bb: cb.update(('L:'+r['left'],'R:'+r['right']))
        vals.append((s,js(ca,cb),len(aa)+len(bb)))
    den=sum(w for _,_,w in vals)
    return (sum(v*w for _,v,w in vals)/den if den else None), vals

def pools(rows):
    # Strict-to-relaxed pools, always preserving stem and position bin.
    levels=[('strict',('stem','L','H','I','pos')),('no_section',('stem','L','H','pos')),('currier_pos',('stem','L','pos')),('stem_pos',('stem','pos'))]
    assignment={}; counts=Counter()
    for idx,r in enumerate(rows):
        for name,keys in levels:
            ids=[j for j,x in enumerate(rows) if all(x[k]==r[k] for k in keys)]
            if len({rows[j]['prefix'] for j in ids})>=2:
                assignment[idx]=(name,tuple(ids)); counts[name]+=1; break
        else: assignment[idx]=('fixed',(idx,)); counts['fixed']+=1
    return assignment,counts

def permuted(rows,assignment,rng):
    out=[dict(r) for r in rows]; done=set()
    for i,(lvl,ids) in assignment.items():
        if lvl=='fixed' or ids in done: continue
        done.add(ids); labels=[rows[j]['prefix'] for j in ids]; rng.shuffle(labels)
        for j,l in zip(ids,labels): out[j]['prefix']=l
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',required=True); ap.add_argument('--out',required=True); ap.add_argument('--permutations',type=int,default=999); a=ap.parse_args()
    if blob(a.corpus)!=EXPECTED: raise SystemExit('frozen corpus blob mismatch')
    rows,stats=parse(a.corpus)
    folios=sorted({r['folio'] for r in rows}); test=set(folios[4::5]); dev=[r for r in rows if r['folio'] not in test]; hold=[r for r in rows if r['folio'] in test]
    elig=eligible(dev); rng=random.Random(SEED); results={}
    for pair in [x+'/'+y for x,y in PAIRS]:
        stems=elig.get(pair,[]); observed,stemvals=statistic(dev,stems,pair)
        assn,relax=pools([r for r in dev if r['pair']==pair and r['stem'] in stems]) if stems else ({},Counter())
        base=[r for r in dev if r['pair']==pair and r['stem'] in stems]
        null=[]
        if observed is not None:
            for _ in range(a.permutations):
                pr=permuted(base,assn,rng); v,_=statistic(pr,stems,pair); null.append(v if v is not None else 0.0)
        p=(1+sum(v>=observed for v in null))/(1+len(null)) if null and observed is not None else None
        hold_stems=[s for s in stems if len({r['prefix'] for r in hold if r['pair']==pair and r['stem']==s})==2]
        hv,hvals=statistic([r for r in hold if r['pair']==pair],hold_stems,pair)
        results[pair]={'eligible_dev_stems':len(stems),'observed_dev_js':observed,'mc_p':p,'null_mean':sum(null)/len(null) if null else None,'pool_relaxation_occurrences':dict(relax),'holdout_folios':len(test),'eligible_holdout_stems':len(hvals),'holdout_js':hv,'dev_stem_effects':stemvals[:50],'holdout_stem_effects':hvals[:50]}
    primary=results['ch/sh']; pass_primary=bool(primary['eligible_dev_stems']>=5 and primary['mc_p'] is not None and primary['mc_p']<=.01 and primary['holdout_js'] is not None and primary['holdout_js']>0)
    payload={'classification':'PREREGISTERED_ADVERSARIAL_COMPOSITIONAL_NULL_NOT_TRANSLATION','source_blob':EXPECTED,'seed':SEED,'permutations':a.permutations,'parser_stats':dict(stats),'folios_with_pair_observations':len(folios),'holdout_rule':'sorted folios, every fifth folio starting at index 4','results':results,'primary_status':'PASS_EXECUTED' if pass_primary else 'FAIL_EXECUTED','interpretation_ceiling':'Distributional compositional structure only; no semantic or translation claim.'}
    with open(a.out,'w',encoding='utf-8') as f: json.dump(payload,f,indent=2,ensure_ascii=False)
    print(json.dumps(payload,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
