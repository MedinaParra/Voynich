#!/usr/bin/env python3
"""Exact boundary-stress certificate and conservative coupled permutation envelope."""
import argparse,gzip,hashlib,itertools,json,random
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


def raw(p):return p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes())
def read(p):return json.loads(raw(p))
def frac(x):return [x.numerator,x.denominator]
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def edit(a,b):
    row=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        nxt=[i]
        for j,y in enumerate(b,1):nxt.append(min(nxt[-1]+1,row[j]+1,row[j-1]+(x!=y)))
        row=nxt
    return row[-1]
def near(a,b):return int(min(len(a),len(b))>=3 and edit(a,b)<=1)


def score(tokens):
    t=tokens[1:-1];m=len(t)
    if m<2:return F(0)
    adjacent=sum(near(a,b) for a,b in zip(t,t[1:]));pairs=sum(near(a,b) for i,a in enumerate(t) for j,b in enumerate(t) if i!=j)
    return F(adjacent,m-1)-F(pairs,m*(m-1))


def make_locus(id,chars,mandatory,optional,vt_cuts):
    mandatory=sorted(mandatory);optional=sorted(optional);vt_cuts=sorted(vt_cuts);paths=[]
    for index,bits in enumerate(itertools.product([0,1],repeat=len(optional))):
        cuts=sorted(set(mandatory)|{p for p,bit in zip(optional,bits) if bit});bounds=[0]+cuts+[len(chars)];tokens=[chars[a:b] for a,b in zip(bounds,bounds[1:])]
        assert all(tokens)
        paths.append({'id':index,'cuts':cuts,'flips':len(set(cuts)^set(vt_cuts)),'tokens':tokens,'score':frac(score(tokens))})
    return {'id':id,'chars':chars,'mandatory':mandatory,'optional':optional,'vt_cuts':vt_cuts,'paths':paths}


def certificates(loci,budgets):
    # For each exact cost keep exact min/max additive scores and their witnesses.
    dp={0:(F(0),[],F(0),[])}
    for locus in loci:
        nd={}
        for cost,(lo,lw,hi,hw) in dp.items():
            for p in locus['paths']:
                c=cost+p['flips'];s=F(*p['score']);a,b=lo+s,hi+s
                if c not in nd:nd[c]=(a,lw+[p['id']],b,hw+[p['id']])
                else:
                    old=nd[c];nd[c]=(a,lw+[p['id']],old[2],old[3]) if a<old[0] else old
                    old=nd[c];nd[c]=(old[0],old[1],b,hw+[p['id']]) if b>old[2] else old
        dp=nd
    out=[]
    for budget in budgets:
        allowed=[(cost,v) for cost,v in dp.items() if cost<=budget]
        lc,lv=min(allowed,key=lambda x:(x[1][0],x[0]));hc,hv=max(allowed,key=lambda x:(x[1][2],-x[0]))
        out.append({'budget':budget,'min':frac(lv[0]),'max':frac(hv[2]),'min_witness':lv[1],'max_witness':hv[3],'min_actual_flips':lc,'max_actual_flips':hc})
    radius=min((c for c,v in dp.items() if v[0]<=0),default=None)
    return out,radius


def permutation(loci,B,seed):
    pre=[]
    for locus in loci:
        paths=[]
        for p in locus['paths']:
            t=p['tokens'][1:-1];m=len(t);starts=([0]+p['cuts'])[1:-1]
            assert len(starts)==m
            matrix=[[near(a,b) for b in t] for a in t];observed=sum(matrix[i][i+1] for i in range(m-1))
            paths.append((p['flips'],m,starts,matrix,observed))
        pre.append((locus['id'],paths))
    vt_diffs=[];envelopes=[]
    for replica in range(B):
        baseline=F(0);envelope=F(0)
        for name,paths in pre:
            starts={s for p in paths for s in p[2]};keys={s:hashlib.sha256(f'{seed}|{replica}|{name}|{s}'.encode()).digest() for s in starts};local=[]
            for flips,m,positions,mat,obs in paths:
                if m<2:d=F(0)
                else:
                    order=sorted(range(m),key=lambda j:keys[positions[j]])
                    hits=sum(mat[a][b] for a,b in zip(order,order[1:]));d=F(hits-obs,m-1)
                local.append(d)
                if flips==0:baseline+=d
            envelope+=max(local)
        assert envelope>=baseline
        vt_diffs.append(frac(baseline));envelopes.append(frac(envelope))
    vt_hits=sum(F(*x)>=0 for x in vt_diffs);upper_hits=sum(F(*x)>=0 for x in envelopes)
    return {'replicates':B,'seed':seed,'vt_tail_count':vt_hits,'envelope_tail_count':upper_hits,'p_vt_mc':(1+vt_hits)/(B+1),'p_upper_mc':(1+upper_hits)/(B+1),'vt_differences':vt_diffs,'envelope_differences':envelopes,'scope':'Conditional coupled finite-simulation tail envelope; not a universal p-value for an historical mechanism'}


def calibration(plan):
    opts=plan['calibration'];rng=random.Random(opts['generator_seed']);shuffle=random.Random(opts['shuffle_seed']);base=[];permuted=[]
    for i in range(opts['loci']):
        words=[]
        for j in range(opts['tokens_per_locus']):
            if words and rng.random()<opts['copy_previous_probability']:
                word=words[-1]
                if rng.random()<opts['mutate_given_copy_probability']:
                    k=rng.randrange(len(word));letters=[c for c in 'abcdefghijklmnopqrstuvwxyz' if c!=word[k]];word=word[:k]+rng.choice(letters)+word[k+1:]
            else:word=rng.choice(opts['vocabulary'])
            words.append(word)
        middle=words[1:-1];shuffle.shuffle(middle);other=[words[0]]+middle+[words[-1]]
        assert Counter(other)==Counter(words) and other[0]==words[0] and other[-1]==words[-1]
        base.append(words);permuted.append(other)
    results={}
    for name,corpus in [('copy',base),('shuffled_matched',permuted)]:
        for ambiguous in [False,True]:
            loci=[]
            for i,words in enumerate(corpus):
                cuts=[];pos=0
                for word in words[:-1]:pos+=len(word);cuts.append(pos)
                optional=[sum(map(len,words[:7]))+len(words[7])//2] if ambiguous and i%2==0 else []
                loci.append(make_locus('synthetic'+str(i),''.join(words),cuts,optional,cuts))
            tag=name+('_ambiguous' if ambiguous else '_clean');perms=permutation(loci,plan['randomization']['control_replicates'],plan['randomization']['seed']);cs,radius=certificates(loci,[0,sum(len(r['optional']) for r in loci)])
            results[tag]={'observed_VT_score':frac(sum((F(*next(p['score'] for p in l['paths'] if p['flips']==0)) for l in loci),F(0))),'certificates':cs,'fragility':radius,'permutation':perms,'loci':loci}
    gate=all(results[k]['permutation']['p_upper_mc']<=.05 for k in ['copy_clean','copy_ambiguous']) and all(results[k]['permutation']['p_vt_mc']>.05 for k in ['shuffled_matched_clean','shuffled_matched_ambiguous'])
    return {'gate_passed':gate,'examples':results,'scope':'Four long-locus examples, not matched to real locus-length distribution; no population power or false-positive estimate'}


def run(repo,out,plan_path):
    plan=read(plan_path);source=repo/plan['comparison_path'];assert hashlib.sha256(raw(source)).hexdigest()==plan['comparison_sha256'];comparison=read(source);cal=calibration(plan);save(out/'calibration.json',cal);loci=[]
    for r in comparison['loci']:
        if r['status']!='compared' or r['vt']['chars']!=r['zl']['chars']:continue
        a={b['offset']:b['kind'] for b in r['vt']['boundaries']};b={b['offset']:b['kind'] for b in r['zl']['boundaries']};common=set(a)&set(b);mandatory={p for p in common if a[p]!=',' and b[p]!=','};optional=(set(a)|set(b))-mandatory
        loci.append(make_locus(r['id'],r['vt']['chars'],mandatory,optional,a))
    assert len(loci)==98 and sum(len(l['optional']) for l in loci)==49 and sum(len(l['paths']) for l in loci)==170
    # Synthetic calibration completed before constructing real scored paths.
    budget=sum(len(l['optional']) for l in loci);cs,radius=certificates(loci,[0,1,2,4,8,budget]);vt_score=sum((F(*next(p['score'] for p in l['paths'] if p['flips']==0)) for l in loci),F(0));perms=permutation(loci,plan['randomization']['real_replicates'],plan['randomization']['seed'])
    table=str.maketrans('abcdefghijklmnopqrstuvwxyz','hijklmnopqrstuvwxyzabcdefg');invariances=[]
    for l in loci:
        for p in l['paths']:
            s=F(*p['score']);assert score([w.translate(table) for w in p['tokens']])==s;assert score(p['tokens'][::-1])==s
    result={'plan_sha256':hashlib.sha256(raw(plan_path)).hexdigest(),'comparison_sha256':plan['comparison_sha256'],'loci':loci,'vt_score':frac(vt_score),'certificates':cs,'fragility_min_flips_to_nonpositive':radius,'permutation':perms,'calibration_gate_passed':cal['gate_passed'],'global_boundary_worlds':2**budget,'local_paths':170,'optional_boundaries':budget,'baseline_token_counts':dict(sorted(Counter(len(next(p['tokens'] for p in l['paths'] if p['flips']==0)) for l in loci).items())),'invariances':{'all_local_paths_bijective_character_substitution':True,'all_local_paths_reversed_tokens':True,'consequence':'Statistic cannot identify a monoalphabetic key or reading direction'},'scope':'Already-used 98 literal letter-equal loci; boundary stress family only, no glyph-alternative or whole-family mechanism inference','training':'NOT_RUN','translation':'NOT_RUN'}
    save(out/'result.json',result)
    summary={k:result[k] for k in ['vt_score','fragility_min_flips_to_nonpositive','calibration_gate_passed','global_boundary_worlds','local_paths','optional_boundaries','baseline_token_counts','invariances','scope']};summary['score_vt_float']=float(vt_score);summary['p_vt_mc']=perms['p_vt_mc'];summary['p_upper_mc']=perms['p_upper_mc'];summary['stress']=[{'budget':r['budget'],'min_score':float(F(*r['min'])),'max_score':float(F(*r['max'])),'min_actual_flips':r['min_actual_flips']} for r in cs];summary['calibration']={k:{'p_vt':v['permutation']['p_vt_mc'],'p_upper':v['permutation']['p_upper_mc']} for k,v in cal['examples'].items()};save(out/'summary.json',summary);print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--plan',type=Path,required=True);a=p.parse_args();run(a.repo,a.out,a.plan)
