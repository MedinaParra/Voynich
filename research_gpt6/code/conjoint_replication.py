#!/usr/bin/env python3
"""Metadata-selected conjoint-leaf replication; no order optimization."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import q13_matching_control as base
import timesfm_singulion_q13 as qtf
import timesfm_voynich as tfm


def cross_matchings(pairs, nodes=None):
    left = tuple(sorted(a for a, _ in pairs))
    right = tuple(sorted(b for _, b in pairs))
    if nodes is not None:
        left = tuple(x for x in left if x in nodes)
        right = tuple(x for x in right if x in nodes)
    if len(left) != len(right) or set(left) & set(right):
        raise ValueError('Invalid physical-side partition')
    for perm in itertools.permutations(right):
        yield base.canonical(zip(left, perm))


def assess(edges, pairs, nodes=None, higher=True):
    observed = base.canonical(pairs)
    nodes = tuple(sorted(nodes if nodes is not None else itertools.chain.from_iterable(pairs)))
    cross = set(cross_matchings(pairs, nodes))
    records = [
        {'pairs': [list(p) for p in matching], 'cross_half': matching in cross,
         'scores': {name: base.matching_score(matching, e) for name, e in edges.items()}}
        for matching in base.perfect_matchings(nodes)
    ]
    if observed not in {base.canonical(r['pairs']) for r in records} or observed not in cross:
        raise ValueError('Observed matching missing from reference')
    summary = {}
    for name, e in edges.items():
        value = base.matching_score(observed, e)
        summary[name] = {
            'all': base.exact_summary(value, [r['scores'][name] for r in records], higher),
            'cross_half': base.exact_summary(value, [r['scores'][name] for r in records if r['cross_half']], higher),
        }
    return summary, records


def quire_leaves(metadata, quire):
    return sorted({base.leaf_number(p) for p, m in metadata.items() if m.get('Q') == quire})


def group_id(group):
    return f"Q{ord(group['quire'])-ord('A')+1}_H{group['hand']}_C{group['currier']}"


def validate_group(group, metadata, pages):
    pairs = base.canonical(group['pairs'])
    if len(pairs) < 4 or len(set(itertools.chain.from_iterable(pairs))) != len(pairs) * 2:
        raise ValueError('Insufficient or overlapping physical pairs')
    if max(a for a, _ in pairs) >= min(b for _, b in pairs):
        raise ValueError('Physical sides do not form earlier/later halves')
    for a, b in pairs:
        ids = [f'f{n}{s}' for n in (a, b) for s in ('r', 'v')]
        if any(not pages.get(p) for p in ids):
            raise ValueError('Empty paragraph side')
        required = {'Q': group['quire'], 'H': group['hand'], 'L': group['currier']}
        if any(metadata.get(p, {}).get(k) != v for p in ids for k, v in required.items()):
            raise ValueError('Group hand/Currier/quire mismatch')
        bifolios = {metadata[p].get('B') for p in ids}
        if len(bifolios) != 1 or None in bifolios:
            raise ValueError('Physical bifolio mapping mismatch')


def make_idf(pages, excluded_leaves):
    train = defaultdict(list)
    excluded = set(excluded_leaves)
    for page, words in pages.items():
        leaf = base.leaf_number(page)
        if leaf not in excluded:
            train[leaf].extend(words)
    df = Counter()
    for leaf in sorted(train):
        df.update(set(train[leaf]))
    idf = {w: math.log((1 + len(train)) / (1 + df[w])) + 1 for w in sorted(df)}
    return idf, len(train)


def nuisance_residual(raw_edges, style_edges, words, leaves):
    pairs = list(itertools.combinations(leaves, 2))
    design = np.asarray([
        [1., style_edges[base.edge_key((a,b))], abs(math.log(len(words[a])/len(words[b]))), (a-b)**2/100.]
        for a,b in pairs], dtype=np.float64)
    target = np.asarray([raw_edges[base.edge_key(p)] for p in pairs], dtype=np.float64)
    beta, _, rank, singular = np.linalg.lstsq(design, target, rcond=None)
    residual = target-design@beta
    return {base.edge_key(p): float(v) for p,v in zip(pairs,residual)}, {
        'columns': ['intercept','char3_cosine','absolute_log_token_count_ratio','squared_folio_gap_over_100'],
        'coefficients': beta.tolist(), 'matrix_rank': int(rank), 'singular_values': singular.tolist(),
        'physical_pair_labels_used_in_fit': False,
    }


def lexical_group(raw, group, mode):
    pages, metadata, parser_audit = base.parse_pages(raw, mode)
    validate_group(group, metadata, pages)
    pairs = base.canonical(group['pairs'])
    leaves = tuple(sorted(itertools.chain.from_iterable(pairs)))
    excluded = quire_leaves(metadata, group['quire'])
    idf, n_train = make_idf(pages, excluded)
    words = {n: pages[f'f{n}r']+pages[f'f{n}v'] for n in leaves}
    vectors = {n: base.tfidf(words[n],idf) for n in leaves}
    chars = {n: base.char3(words[n]) for n in leaves}
    edges = {name: {} for name in ('tfidf','char3','char_js','tfidf_recto','tfidf_verso')}
    for a,b in itertools.combinations(leaves,2):
        key=base.edge_key((a,b))
        edges['tfidf'][key]=base.cosine(vectors[a],vectors[b])
        edges['char3'][key]=base.cosine(chars[a],chars[b])
        edges['char_js'][key]=base.char_js(words[a],words[b])
        for side,name in (('r','recto'),('v','verso')):
            edges[f'tfidf_{name}'][key]=base.cosine(base.tfidf(pages[f'f{a}{side}'],idf),base.tfidf(pages[f'f{b}{side}'],idf))
    edges['tfidf_residual'],nuisance=nuisance_residual(edges['tfidf'],edges['char3'],words,leaves)
    summary,records=assess(edges,pairs)
    leave_out=[]
    for omitted in pairs:
        keep_pairs=tuple(p for p in pairs if p!=omitted)
        keep_nodes=tuple(n for n in leaves if n not in omitted)
        sub,_=assess({'tfidf':edges['tfidf']},keep_pairs,keep_nodes)
        leave_out.append({'omitted_pair':list(omitted),'summary':sub['tfidf']})
    gates=base.gate_from_summaries(summary,leave_out)
    ids=[f'f{n}{s}' for n in leaves for s in ('r','v')]
    return {
        'group':group,'comma_mode':mode,'status':'PASS_GROUP_STRICT' if all(gates.values()) else 'FAIL_GROUP_STRICT',
        'gates':gates,'summary':summary,'edge_scores':edges,'all_matching_scores':records,
        'leave_pair_out':leave_out,'nuisance_fit':nuisance,'parser_audit':parser_audit,
        'entire_quire_leaves_excluded_from_train':excluded,'idf_training_leaves':n_train,'vocabulary_size':len(idf),
        'idf_token_coverage_by_leaf':{str(n):sum(w in idf for w in words[n])/len(words[n]) for n in leaves},
        'tokens_by_page':{p:len(pages[p]) for p in ids},'metadata_by_page':{p:metadata[p] for p in ids},
    }


def pooled_exact(groups, metric):
    normalized={'all':[],'cross_half':[]}
    observed=[]
    scales={}
    for name,data in groups.items():
        all_values=np.asarray([r['scores'][metric] for r in data['all_matching_scores']],dtype=np.float64)
        mean=math.fsum(all_values.tolist())/len(all_values)
        sd=float(np.sqrt(np.mean((all_values-mean)**2)))
        obs=data['summary'][metric]['all']['observed']
        scales[name]={'full_null_mean':mean,'full_null_population_sd':sd,'flat_null':sd<=1e-12}
        observed.append((obs-mean)/sd if sd>1e-12 else 0.)
        for null in normalized:
            vals=np.asarray([r['scores'][metric] for r in data['all_matching_scores'] if null=='all' or r['cross_half']],dtype=np.float64)
            normalized[null].append((vals-mean)/sd if sd>1e-12 else np.zeros_like(vals))
    value=math.fsum(observed)/len(observed)
    result={'normalization':scales,'standardized_observed_by_group':dict(zip(groups,observed)),'summary':{}}
    for null, arrays in normalized.items():
        joint=np.asarray([0.],dtype=np.float64)
        for vals in arrays:
            joint=(joint[:,None]+vals[None,:]).reshape(-1)
        joint=joint/len(arrays)
        better=int(np.sum(joint>value+1e-12));tail=int(np.sum(joint>=value-1e-12))
        result['summary'][null]={
            'observed':value,'rank_best_is_1':better+1,'n_exact':int(joint.size),
            'inclusive_tail_count':tail,'exact_tail_p':tail/joint.size,
            'null_min':float(joint.min()),'null_mean':float(joint.mean()),'null_max':float(joint.max()),
            'observed_minus_null_mean':value-float(joint.mean()),'higher_is_better':True,'tie_tolerance':1e-12,
        }
    return result


def panel_analysis(groups):
    pooled={metric:pooled_exact(groups,metric) for metric in ('tfidf','tfidf_residual')}
    gates={}
    for metric in pooled:
        for null in ('all','cross_half'):
            gates[f'pooled_{metric}_{null}_p_le_05']=pooled[metric]['summary'][null]['exact_tail_p']<=.05
    for name,data in groups.items():
        for metric in pooled:
            gates[f'{name}_{metric}_positive']=data['summary'][metric]['all']['observed_minus_null_mean']>1e-12
        for key,value in data['gates'].items():
            if key.endswith('_positive'):
                gates[f'{name}_{key}']=value
    return {'pooled':pooled,'gates':gates,'all_gates_pass':all(gates.values())}


def page_errors_to_edges(page_errors, leaves, indices):
    result={}
    for a,b in itertools.combinations(leaves,2):
        vals=[]
        for x,y in ((a,b),(b,a)):
            for sx in ('r','v'):
                for sy in ('r','v'):
                    errors=page_errors[f'f{x}{sx}->f{y}{sy}']
                    vals.append(math.fsum(errors[i] for i in indices)/len(indices))
        result[base.edge_key((a,b))]=math.fsum(vals)/len(vals)
    return result


def outside_quire_feature_rows(rows, excluded_leaves):
    excluded=set(excluded_leaves)
    # Rosette paragraph loci have no ordinary numbered page ID. They are
    # outside these frozen ordinary-page target quires and remain in train.
    return [row['x'] for row in rows if row['page'] is None or base.leaf_number(row['page']) not in excluded]


def timesfm_group(raw, group):
    pairs=base.canonical(group['pairs'])
    leaves=tuple(sorted(itertools.chain.from_iterable(pairs)))
    ids=[f'f{n}{s}' for n in leaves for s in ('r','v')]
    rows=qtf.feature_rows(raw)
    grouped=defaultdict(list)
    for row in rows:grouped[row['page']].append(row['x'])
    missing={p:len(grouped[p]) for p in ids if len(grouped[p])<4}
    if missing:
        return {'status':'BLOCKED_INSUFFICIENT_CLEAN_ROWS','pages_below_fixed_horizon':missing,
                'fixed_horizon':4,'partial_group_scored':False}
    import torch
    random.seed(20261007);np.random.seed(20261007);torch.manual_seed(20261007)
    _,metadata,_=base.parse_pages(raw,'split')
    excluded=quire_leaves(metadata,group['quire'])
    train=outside_quire_feature_rows(rows,excluded)
    scales=np.maximum(np.var(np.asarray(train,dtype=np.float32),axis=0),1e-8)
    contexts={p:np.asarray(grouped[p],dtype=np.float32)[-64:] for p in ids}
    targets={p:np.asarray(grouped[p][:4],dtype=np.float32) for p in ids}
    model=tfm.load_model(64,4)
    predictions={p:tfm.forecast(model,contexts[p],4) for p in ids}
    page_errors={name:{} for name in ('model','persistence','source_mean')}
    for src in ids:
        forecasts={'model':predictions[src],
                   'persistence':np.repeat(contexts[src][-1:],4,axis=0),
                   'source_mean':np.repeat(contexts[src].mean(axis=0,keepdims=True),4,axis=0)}
        for tgt in ids:
            if src==tgt:continue
            for name,forecast in forecasts.items():
                page_errors[name][f'{src}->{tgt}']=(((forecast-targets[tgt])**2).mean(axis=0)/scales).astype(float).tolist()
    edges={name:page_errors_to_edges(v,leaves,range(10)) for name,v in page_errors.items()}
    edges['model_without_token_count']=page_errors_to_edges(page_errors['model'],leaves,range(1,10))
    edges['model_minus_persistence']={k:edges['model'][k]-edges['persistence'][k] for k in edges['model']}
    summary,records=assess(edges,pairs,higher=False)
    return {
        'status':'PASS_EXECUTED_DESCRIPTIVE','group':group,'model':tfm.MODEL_ID,'features':tfm.FEATURES,
        'seed':20261007,'context_cap':64,'horizon':4,'entire_quire_leaves_excluded_from_train':excluded,
        'scales_outside_quire':scales.astype(float).tolist(),'outside_quire_rows':len(train),
        'clean_rows_per_page':{p:len(grouped[p]) for p in ids},
        'source_contexts':{p:x.astype(float).tolist() for p,x in contexts.items()},
        'frozen_predictions':{p:x.astype(float).tolist() for p,x in predictions.items()},
        'target_rows':{p:x.astype(float).tolist() for p,x in targets.items()},
        'directed_page_standardized_mse_by_feature':page_errors,
        'edge_scores':edges,'summary':summary,'all_matching_scores':records,'lexical_decision_affected':False,
    }


def summary_record(result):
    return {k:result[k] for k in ('classification','status','semantic_status','source_sha256','plan_sha256','runtime')} | {
        'per_group':{mode:{name:{'status':g['status'],'gates':g['gates'],'summary':g['summary']} for name,g in groups.items()}
                     for mode,groups in result['lexical'].items()},
        'panel':result['panel'],
        'timesfm':{name:{'status':g['status'],'summary':g.get('summary'),'pages_below_fixed_horizon':g.get('pages_below_fixed_horizon')}
                   for name,g in result['timesfm'].items()},
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--corpus',type=Path,required=True)
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--metadata-audit',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--timesfm',action='store_true')
    args=ap.parse_args()
    corpus=args.corpus.read_bytes();digest=hashlib.sha256(corpus).hexdigest()
    if digest!=base.SOURCE_SHA256:raise SystemExit('BLOCKED: corpus hash mismatch')
    plan_bytes=args.plan.read_bytes();plan=json.loads(plan_bytes)
    metadata_bytes=args.metadata_audit.read_bytes();selection=json.loads(metadata_bytes)
    groups=plan['selection']['targets']
    if groups!=selection['selected']:raise SystemExit('BLOCKED: selection differs from protocol')
    if any(g['quire']=='M' for g in groups) or len(groups)!=3:
        raise SystemExit('BLOCKED: frozen replication target set mismatch')
    raw=corpus.decode()
    lexical={mode:{group_id(g):lexical_group(raw,g,mode) for g in groups} for mode in ('split','join')}
    panel={mode:panel_analysis(data) for mode,data in lexical.items()}
    result={
        'classification':'CONJOINT_LEAF_REPLICATION_NOT_DECIPHERMENT',
        'status':'PASS_REPLICATION_PANEL' if all(p['all_gates_pass'] for p in panel.values()) else 'FAIL_REPLICATION_PANEL',
        'semantic_status':'NOT_RUN','source_blob':base.digest_file(args.corpus)['git_blob'],'source_sha256':digest,
        'plan_sha256':hashlib.sha256(plan_bytes).hexdigest(),'metadata_audit_sha256':hashlib.sha256(metadata_bytes).hexdigest(),
        'targets':groups,'lexical':lexical,'panel':panel,
        'timesfm':{group_id(g):timesfm_group(raw,g) if args.timesfm else {'status':'NOT_RUN'} for g in groups},
        'runtime':{'python':platform.python_version(),'numpy':np.__version__},
        'code_hashes':[base.digest_file(Path(__file__)),base.digest_file(Path(base.__file__)),
                       base.digest_file(Path(qtf.__file__)),base.digest_file(Path(tfm.__file__))],
        'limitations':[
            'Follow-up on a previously explored corpus; no independent transcription or untouched manuscript holdout.',
            'Selected Q20 subset covers four of six extant bifolia, not the whole quire.',
            'Exchangeable random-matching references do not describe randomized historical binding.',
            'Pooled exact reference assumes independent assignments between groups.',
            'Character trigram adjustment can remove lexical content as well as style.',
            'Small group sizes and overlapping face/leave-pair-out views limit interpretation.',
            'TimesFM diagnostics cannot rescue lexical failure or establish semantics.',
        ],
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary_record(result),indent=2,allow_nan=False))
    print('RESULT_SHA256='+hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__=='__main__':main()
