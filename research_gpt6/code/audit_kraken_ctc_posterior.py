#!/usr/bin/env python3
"""Independent probability-space CTC replay; no network loading or inference."""
import argparse
from collections import Counter,defaultdict
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import numpy as np
from audit_kraken_stage2 import edit


def raw(p):return p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes())
def read(p):return json.loads(raw(p))
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def array_sha(p):return hashlib.sha256(np.asarray(p,dtype=np.float32).tobytes(order='C')).hexdigest()


def probability_beam(p,width):
    """Separate recurrence with multiplication, additions and per-frame scaling."""
    states={():[1.,0.]};scale=0.
    for row in np.asarray(p,dtype=float):
        next_states=defaultdict(lambda:[0.,0.])
        for prefix,(blank,nonblank) in states.items():
            total=blank+nonblank;next_states[prefix][0]+=total*row[0]
            for label in range(1,len(row)):
                v=float(row[label])
                if not v:continue
                if prefix and label==prefix[-1]:
                    next_states[prefix][1]+=nonblank*v
                    next_states[prefix+(label,)][1]+=blank*v
                else:next_states[prefix+(label,)][1]+=total*v
        selected=sorted(((k,v) for k,v in next_states.items() if sum(v)>0),key=lambda kv:(-sum(kv[1]),kv[0]))[:width]
        normalization=math.fsum(sum(v) for k,v in selected)
        if normalization<=0:raise ValueError('No positive probability prefix')
        scale+=math.log(normalization);states={k:[v[0]/normalization,v[1]/normalization] for k,v in selected}
    final=sorted(states.items(),key=lambda kv:(-sum(kv[1]),kv[0]));prefix,mass=final[0]
    return prefix,math.log(sum(mass))+scale


def audit(bundle,repo):
    plan_path=repo/'data/kraken_ctc_posterior_plan.json';plan=read(plan_path);result=read(bundle/'result.json');data=read(repo/plan['prepared_dataset_path']);evaluation=[r for r in data if r['role'] in ['historical_development','reserved']];vocabulary={r['reference'] for r in data if r['role'] in ['original_train','additional_train']};codec=read(bundle/'codec.json');id_text={v[0]:k for k,v in codec.items()};records=read(bundle/'capture_records.json');record_by={(r['pass'],r['id']):r for r in records};checks=0;errors=[]
    def check(label,a,b=True):
        nonlocal checks
        checks+=1
        equal=math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9) if isinstance(a,(int,float)) and isinstance(b,(int,float)) else a==b
        if not equal:errors.append({'check':label,'actual':a,'expected':b})
    def text(labels):return ''.join(id_text[i] for i in labels)
    check('plan_hash',result['plan_sha256'],sha(plan_path));check('model_hash',result['source_model_sha256'],sha(repo/plan['source_model_path']));check('model_fixed',result['source_model_sha256'],plan['source_model_sha256']);check('dataset_hash',result['prepared_dataset_sha256'],sha(repo/plan['prepared_dataset_path']));check('beam_width',result['beam_width'],32);check('no_lexicon',result['word_lexicon'],'NONE');check('no_lm',result['language_model'],'NONE');check('no_label_pruning',result['label_pruning'],'NONE');check('fixed_first_pass',result['primary_pass'],0);check('two_passes',result['passes'],2);check('record_count',len(records),564);check('unique_records',len(record_by),564);check('record_file_hash',result['capture_records_sha256'],sha(bundle/'capture_records.json'))
    check('output_labels',sorted(id_text),list(range(1,20)));check('all_codec_single_characters',all(len(c)==1 and 'a'<=c<='z' and len(v)==1 for c,v in codec.items()))
    caches=[];decoded=[];parity=[]
    for pass_index in range(2):
        filename='posterior_pass'+str(pass_index)+'.npz';check(filename+'/hash',result['posterior_file_sha256'][filename],sha(bundle/filename));npz=np.load(bundle/filename,allow_pickle=False);cache={k:npz[k] for k in npz.files};npz.close();caches.append(cache);check(filename+'/ids',sorted(cache),sorted(r['id'] for r in evaluation));outputs={}
        for index,r in enumerate(evaluation):
            name=str(pass_index)+'/'+r['id'];p=cache[r['id']];record=record_by[(pass_index,r['id'])];check(name+'/shape',record['shape'],list(p.shape));check(name+'/dtype',record['dtype'],str(p.dtype));check(name+'/float32',str(p.dtype),'float32');check(name+'/matrix_hash',record['matrix_sha256'],array_sha(p));check(name+'/image_hash',record['image_sha256'],r['image_sha256']);check(name+'/finite',bool(np.isfinite(p).all()));check(name+'/nonnegative',bool((p>=0).all()));check(name+'/classes',p.shape[1],20)
            row_error=float(np.max(np.abs(p.sum(axis=1,dtype=float)-1)));check(name+'/recorded_row_sum_error',record['maximum_row_sum_error'],row_error);check(name+'/normalized',row_error<=plan['probability_row_sum_tolerance'])
            path=[max(range(len(row)),key=lambda c:row[c]) for row in p];greedy=text(tuple(k for k,g in itertools.groupby(path) if k!=0));original=result['legacy_text_passes'][pass_index][index]
            if greedy!=original:parity.append({'pass':pass_index,'id':r['id'],'original':original,'custom_greedy':greedy})
            order=np.random.default_rng(plan['seed']+index).permutation(len(p));labels,logmass=probability_beam(p,32);shuffled,shuffled_mass=probability_beam(p[order],32);values={'greedy':greedy,'beam32':text(labels),'shuffled_beam32':text(shuffled)};outputs[r['id']]=values;actual=result['all_pass_results'][pass_index];check(name+'/decoded',actual['predictions'][r['id']],values);details=actual['details'][r['id']]
            for k,v in [('beam_labels',list(labels)),('beam_logmass',logmass),('shuffled_labels',list(shuffled)),('shuffled_logmass',shuffled_mass),('frame_permutation',order.tolist())]:check(name+'/'+k,details[k],v)
        decoded.append(outputs);check(filename+'/network_calls',result['forward_calls'][pass_index],282)
    check('interface_parity_differences',result['interface_parity_differences'],parity);check('interface_parity_count',result['interface_parity_checks'],564);interface=read(bundle/'interface_parity.json');check('interface/status',interface['status'],'PASS');check('interface/tensor_records',interface['source_tensors_before'],interface['source_tensors_after']);check('interface/tensor_count',len(interface['source_tensors_before']),14);check('interface/source_unchanged_flag',result['source_tensors_unchanged'])
    cached={r['id']:r for r in read(repo/plan['cached_baselines_path'])['rows']};check('cached_image_comparator_hash',result['cached_baselines_sha256'],sha(repo/plan['cached_baselines_path']));scored=result['rows'];check('evaluation_ids',[r['id'] for r in scored],[r['id'] for r in evaluation])
    for r,source in zip(scored,evaluation):
        name='score/'+r['id'];check(name+'/reference',r['reference'],source['reference']);check(name+'/role',r['role'],source['role']);check(name+'/folio',r['folio'],source['folio']);check(name+'/vocabulary',r['seen_in_training'],r['reference'] in vocabulary)
        for method,value in decoded[0][r['id']].items():check(name+'/'+method,r['predictions'][method],value)
        check(name+'/image_baseline',r['predictions']['nearest_image'],cached[r['id']]['predictions']['nearest_image']);check(name+'/nearest_id',r['nearest_train_id'],cached[r['id']]['nearest_train_id']);check(name+'/details',r['decoder_details'],result['all_pass_results'][0]['details'][r['id']])
        for method,pred in r['predictions'].items():check(name+'/distance/'+method,r['errors'][method],edit(r['reference'],pred))
    def metrics(rows):
        if not rows:return None
        n=sum(len(r['reference']) for r in rows)
        return {m:{'errors':sum(edit(r['reference'],r['predictions'][m]) for r in rows),'eva_characters':n,'cer':sum(edit(r['reference'],r['predictions'][m]) for r in rows)/n,'exact_words':sum(r['reference']==r['predictions'][m] for r in rows),'words':len(rows),'exact_word_fraction':sum(r['reference']==r['predictions'][m] for r in rows)/len(rows)} for m in rows[0]['predictions']}
    summary={}
    for role in ['historical_development','reserved']:
        selected=[r for r in scored if r['role']==role];summary[role]={'all':metrics(selected),'seen':metrics([r for r in selected if r['seen_in_training']]),'unseen':metrics([r for r in selected if not r['seen_in_training']]),'length_1_4':metrics([r for r in selected if len(r['reference'])<=4]),'length_5_6':metrics([r for r in selected if 5<=len(r['reference'])<=6]),'length_7_plus':metrics([r for r in selected if len(r['reference'])>=7])}
    check('all_metrics',result['metrics'],summary);matrix_repeat=[r['id'] for r in evaluation if array_sha(caches[0][r['id']])!=array_sha(caches[1][r['id']])];check('matrix_repeat',result['matrix_replay_differences'],matrix_repeat);repeat=[{'id':r['id'],'method':m,'pass0':decoded[0][r['id']][m],'pass1':decoded[1][r['id']][m]} for r in evaluation for m in ['greedy','beam32','shuffled_beam32'] if decoded[0][r['id']][m]!=decoded[1][r['id']][m]];check('text_repeat',result['text_replay_differences'],repeat)
    check('no_new_training',result['new_training'],'NOT_RUN');check('no_translation',result['translation'],'NOT_RUN');primary=[r for r in scored if r['role']=='reserved' and not r['seen_in_training']];check('primary/words',len(primary),76);check('primary/eva_characters',sum(len(r['reference']) for r in primary),446)
    changes={}
    for role in ['historical_development','reserved']:
        rs=[r for r in scored if r['role']==role];changes[role]={'text_changed':sum(r['predictions']['beam32']!=r['predictions']['greedy'] for r in rs),'lower_edit_error':sum(r['errors']['beam32']<r['errors']['greedy'] for r in rs),'higher_edit_error':sum(r['errors']['beam32']>r['errors']['greedy'] for r in rs),'equal_edit_error':sum(r['errors']['beam32']==r['errors']['greedy'] for r in rs)}
    return {'status':'PASS' if not errors else 'FAIL','checks':checks,'mismatches':errors,'result_sha256':sha(bundle/'result.json'),'run_id':result['run_id'],'execution_commit':result['execution_commit'],'primary_reserved_unseen':summary['reserved']['unseen'],'all_metrics':summary,'paired_changes':changes,'interface_parity_checks':564,'network_forward_calls':sum(result['forward_calls']),'matrix_repeat_differences':len(matrix_repeat),'text_repeat_differences':len(repeat),'scope':'Independent probability-space/scaled prefix recurrence versus log-space implementation on every archived matrix, all text paths/scores, frame permutations, codec, source tensor records, input/weight/array hashes and full-matrix edit arithmetic. No new inference, training or expert/semantic validation.','translation':'NOT_RUN'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=audit(a.bundle,a.repo);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','checks','mismatches','network_forward_calls','matrix_repeat_differences','text_repeat_differences']}));raise SystemExit(r['status']!='PASS')
