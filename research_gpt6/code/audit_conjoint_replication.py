#!/usr/bin/env python3
"""Replay complete archived replication evidence without TimesFM weights."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

import q13_matching_control as base


def audit_matchings(data, pairs, higher):
    pairs=base.canonical(pairs)
    nodes=sorted(itertools.chain.from_iterable(pairs))
    left={a for a,_ in pairs}
    observed={name:sum(edges[base.edge_key(p)] for p in pairs)/len(pairs)
              for name,edges in data['edge_scores'].items()}
    values={name:{'all':[],'cross_half':[]} for name in data['edge_scores']}
    seen=set();score_checks=0
    for record in data['all_matching_scores']:
        matching=base.canonical(record['pairs'])
        if matching in seen or sorted(itertools.chain.from_iterable(matching))!=nodes:
            raise ValueError('Duplicate/incomplete physical matching')
        seen.add(matching)
        cross=all((a in left)!=(b in left) for a,b in matching)
        if cross!=record['cross_half']:raise ValueError('Incorrect cross-half flag')
        for name,edges in data['edge_scores'].items():
            value=sum(edges[base.edge_key(p)] for p in matching)/len(pairs)
            if abs(value-record['scores'][name])>1e-12:raise ValueError('Incorrect matching score')
            values[name]['all'].append(value)
            if cross:values[name]['cross_half'].append(value)
            score_checks+=1
    expected=math.prod(range(1,len(nodes),2))
    if len(seen)!=expected:raise ValueError('Incomplete exhaustive reference')
    summaries=0
    for name,by_null in values.items():
        value=observed[name]
        for null,vals in by_null.items():
            s=data['summary'][name][null]
            if len(vals)!=(expected if null=='all' else math.factorial(len(pairs))):
                raise ValueError('Incorrect reference size')
            tail=sum(x>=value-1e-12 for x in vals) if higher else sum(x<=value+1e-12 for x in vals)
            better=sum(x>value+1e-12 for x in vals) if higher else sum(x<value-1e-12 for x in vals)
            if tail!=s['inclusive_tail_count'] or tail/len(vals)!=s['exact_tail_p'] or better+1!=s['rank_best_is_1']:
                raise ValueError('Incorrect tail or rank')
            mean=math.fsum(vals)/len(vals)
            expected_fields={'observed':value,'null_min':min(vals),'null_max':max(vals),'null_mean':mean,'observed_minus_null_mean':value-mean}
            if any(abs(v-s[k])>1e-12 for k,v in expected_fields.items()):raise ValueError('Incorrect null summary')
            summaries+=1
    return {'matching_records':len(seen),'matching_scores':score_checks,'matching_summaries':summaries}


def audit_pool(groups, panel):
    counts=[]
    for metric,pool in panel['pooled'].items():
        normalized={'all':[],'cross_half':[]};obs=[]
        for name,data in groups.items():
            vals=np.asarray([r['scores'][metric] for r in data['all_matching_scores']],dtype=np.float64)
            norm=pool['normalization'][name]
            mean=math.fsum(vals.tolist())/len(vals)
            sd=float(np.sqrt(np.mean((vals-mean)**2)))
            if abs(mean-norm['full_null_mean'])>1e-12 or abs(sd-norm['full_null_population_sd'])>1e-12:
                raise ValueError('Incorrect pooling normalization')
            value=data['summary'][metric]['all']['observed']
            obs.append((value-mean)/sd if sd>1e-12 else 0.)
            for null in normalized:
                subset=np.asarray([r['scores'][metric] for r in data['all_matching_scores'] if null=='all' or r['cross_half']],dtype=np.float64)
                normalized[null].append((subset-mean)/sd if sd>1e-12 else np.zeros_like(subset))
        observed=math.fsum(obs)/len(obs)
        for null,arrays in normalized.items():
            meshes=np.meshgrid(*arrays,indexing='ij')
            joint=np.stack(meshes,axis=-1).mean(axis=-1).ravel()
            s=pool['summary'][null]
            tail=int(np.count_nonzero(joint>=observed-1e-12));better=int(np.count_nonzero(joint>observed+1e-12))
            if joint.size!=s['n_exact'] or tail!=s['inclusive_tail_count'] or tail/joint.size!=s['exact_tail_p'] or better+1!=s['rank_best_is_1']:
                raise ValueError('Incorrect pooled reference or tail')
            expected={'observed':observed,'null_min':float(joint.min()),'null_max':float(joint.max()),
                      'null_mean':float(joint.mean()),'observed_minus_null_mean':observed-float(joint.mean())}
            if any(abs(v-s[k])>1e-12 for k,v in expected.items()):raise ValueError('Incorrect pooled summary')
            counts.append(int(joint.size))
    return counts


def audit_timesfm(data):
    if data['status']=='BLOCKED_INSUFFICIENT_CLEAN_ROWS':
        if not data['pages_below_fixed_horizon'] or data['partial_group_scored']:
            raise ValueError('Invalid blocked diagnostic')
        return {'status':'VERIFIED_BLOCKED','feature_losses':0,'edge_values':0}
    if data['status']!='PASS_EXECUTED_DESCRIPTIVE':raise ValueError('TimesFM evidence missing')
    scales=np.asarray(data['scales_outside_quire'],dtype=np.float32)
    losses=0;max_delta=0.
    for src,pred in data['frozen_predictions'].items():
        context=np.asarray(data['source_contexts'][src],dtype=np.float32)
        forecasts={'model':np.asarray(pred,dtype=np.float32),
                   'persistence':np.repeat(context[-1:],4,axis=0),
                   'source_mean':np.repeat(context.mean(axis=0,keepdims=True),4,axis=0)}
        for tgt,target in data['target_rows'].items():
            if src==tgt:continue
            target=np.asarray(target,dtype=np.float32)
            for name,forecast in forecasts.items():
                replay=(((forecast-target)**2).mean(axis=0)/scales).astype(float)
                saved=np.asarray(data['directed_page_standardized_mse_by_feature'][name][src+'->'+tgt])
                delta=float(np.max(np.abs(replay-saved)))
                if delta>1e-7:raise ValueError('Forecast loss differs from saved inputs')
                max_delta=max(max_delta,delta);losses+=len(saved)
    leaves=sorted(itertools.chain.from_iterable(data['group']['pairs']));checks=0
    for a,b in itertools.combinations(leaves,2):
        calculated={}
        for name,page_errors in data['directed_page_standardized_mse_by_feature'].items():
            rows=[]
            for x,y in ((a,b),(b,a)):
                rows.extend(page_errors[f'f{x}{sx}->f{y}{sy}'] for sx in ('r','v') for sy in ('r','v'))
            calculated[name]=float(np.asarray(rows).mean())
            if name=='model':calculated['model_without_token_count']=float(np.asarray(rows)[:,1:].mean())
        calculated['model_minus_persistence']=calculated['model']-calculated['persistence']
        for name,value in calculated.items():
            if abs(value-data['edge_scores'][name][base.edge_key((a,b))])>1e-12:
                raise ValueError('Incorrect eight-direction edge aggregation')
            checks+=1
    return {'status':'PASS_FROZEN_LOSS_REPLAY','feature_losses':losses,'max_loss_abs_difference':max_delta,'edge_values':checks}


def audit(result):
    group_counts={};pooled=[];time_counts={}
    for mode,groups in result['lexical'].items():
        for name,data in groups.items():
            group_counts[f'{mode}/{name}']=audit_matchings(data,data['group']['pairs'],True)
        pooled.extend(audit_pool(groups,result['panel'][mode]))
    for name,data in result['timesfm'].items():
        time_counts[name]=audit_timesfm(data)
        if data['status']=='PASS_EXECUTED_DESCRIPTIVE':
            group_counts[f'timesfm/{name}']=audit_matchings(data,data['group']['pairs'],False)
    return {'status':'PASS_FULL_FROZEN_EVIDENCE_REPLAY','group_matching_counts':group_counts,
            'pooled_reference_sizes_replayed':pooled,'timesfm':time_counts,'new_model_inference':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--result',type=Path,required=True)
    args=parser.parse_args();data=args.result.read_bytes()
    verified=audit(json.loads(data));verified['input_sha256']=hashlib.sha256(data).hexdigest()
    print(json.dumps(verified,sort_keys=True))


if __name__=='__main__':main()
