#!/usr/bin/env python3
"""Independent reversible-label, tensor-record and full edit-matrix audit.

No new neural inference, glyph annotation or linguistic interpretation.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
from audit_kraken_stage2 import edit


def raw(p):return p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes())
def read(p):return json.loads(raw(p))
def sha(p):return hashlib.sha256(raw(p)).hexdigest()


def audit(root,repo):
    plan_path=repo/'data/kraken_eva_units_plan.json';plan=read(plan_path);source=read(repo/plan['prepared_dataset_path']);by={r['id']:r for r in source};train=[r for r in source if r['role'] in ['original_train','additional_train']];evaluation=[r for r in source if r['role'] in ['historical_development','reserved']];vocabulary={r['reference'] for r in train}
    code={g:chr(n) for g,n in zip(plan['group_order'],plan['group_private_codepoints'])};inverse={ord(v):g for g,v in code.items()};pattern=re.compile('|'.join(re.escape(g) for g in plan['group_order']));checks=0;errors=[]
    def enc(text,variant):return pattern.sub(lambda m:code[m.group()],text) if variant=='reset_groups' else text
    def dec(text,variant):return text.translate(inverse) if variant=='reset_groups' else text
    def check(label,a,b=True):
        nonlocal checks
        checks+=1
        equal=math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12) if isinstance(a,(int,float)) and isinstance(b,(int,float)) else a==b
        if not equal:errors.append({'check':label,'actual':a,'expected':b})
    check('source_dataset_hash',sha(repo/plan['prepared_dataset_path']),plan['prepared_dataset_sha256']);check('source_model_hash',sha(repo/plan['source_model_path']),plan['source_model_sha256']);check('training_count',len(train),442);check('evaluation_count',len(evaluation),282);check('f5r_absent',not any(r['folio']=='f5r' for r in source));check('leaves_disjoint',not ({r['folio'][:-1] for r in train}&{r['folio'][:-1] for r in evaluation}))
    proofs={};run_results={};failure_weight_replays={}
    for variant in plan['variants']:
        bundle=root/'runs'/variant;result=read(bundle/'result.json');run_results[variant]=result;labels=read(bundle/'training_labels.json');proof=read(bundle/'head_reset_proof.json');proofs[variant]=proof;label=variant
        check(label+'/variant',result['variant'],variant);check(label+'/plan',result['plan_sha256'],sha(plan_path));check(label+'/source',result['source_model_sha256'],plan['source_model_sha256']);check(label+'/dataset',result['prepared_dataset_sha256'],plan['prepared_dataset_sha256']);check(label+'/source_dataset_copy',sha(bundle/'source_dataset.json'),plan['prepared_dataset_sha256']);check(label+'/training_ids',[r['id'] for r in labels],[r['id'] for r in train]);check(label+'/training_words',result['training_words'],442)
        for r,original in zip(labels,train):
            name=label+'/'+r['id'];expected=enc(original['reference'],variant);check(name+'/reference',r['reference'],original['reference']);check(name+'/encoded',r['encoded_text'],expected);check(name+'/roundtrip',dec(r['encoded_text'],variant),original['reference']);check(name+'/image_hash',r['image_sha256'],original['image_sha256']);check(name+'/label_hash',r['label_sha256'],hashlib.sha256(expected.encode()).hexdigest());check(name+'/folio',r['folio'],original['folio'])
        alphabet=sorted(set(''.join(enc(r['reference'],variant) for r in train)));codec={c:[i+1] for i,c in enumerate(alphabet)};units=sum(len(enc(r['reference'],variant)) for r in train)
        check(label+'/encoded_units',result['training_encoded_units'],units);check(label+'/units_fixed',units,1765 if variant=='reset_groups' else 2087);check(label+'/eva_characters',result['training_eva_characters'],2087);check(label+'/alphabet',result['unit_alphabet_size'],len(alphabet));check(label+'/output_size',result['ctc_output_size'],len(alphabet)+1);check(label+'/trained_codec',read(bundle/'trained_codec.json'),codec);check(label+'/reset_codec',proof['codec'],codec)
        check(label+'/proof_source',proof['source_sha256'],plan['source_model_sha256']);check(label+'/body_count',len(proof['backbone_keys']),12);check(label+'/head_count',len(proof['head_keys']),2);check(label+'/complete_partition',sorted(proof['head_keys']+proof['backbone_keys']),sorted(proof['source_tensors']))
        for key in proof['backbone_keys']:check(label+'/body/'+key,proof['source_tensors'][key],proof['reset_tensors'][key])
        check(label+'/head_actually_changed',any(proof['source_tensors'][k]!=proof['reset_tensors'][k] for k in proof['head_keys']));check(label+'/body_flag',proof['backbone_unchanged']);check(label+'/head_flag',proof['head_changed']);check(label+'/roundtrip_tensors',proof['reset_tensors'],proof['serialized_tensors']);check(label+'/roundtrip_tensors_flag',proof['serialization_tensors_equal']);check(label+'/roundtrip_codec_flag',proof['serialization_codec_equal']);check(label+'/reset_file_hash',proof['initial_reset_sha256'],sha(bundle/'initial_reset.safetensors'));check(label+'/head_seed',proof['reset_seed'],20261027)
        for key in proof['head_keys']:check(label+'/head_size/'+key,proof['reset_tensors'][key]['shape'][0],len(alphabet)+1)
        config=read(bundle/'training/training_config.json');command=read(bundle/'training/command.json');check(label+'/only_training_monitor',config['train']['training_data'],config['train']['evaluation_data']);check(label+'/training_manifest',[Path(p).stem for p in (bundle/'training/train.lst').read_text().splitlines()],[r['id'] for r in train]);check(label+'/resize_fail',command[-2:],['--resize','fail']);check(label+'/load_reset_file',Path(command[command.index('--load')+1]).name,'initial_reset.safetensors')
        for k,v in [('epochs',200),('min_epochs',200),('freq',200),('batch_size',16),('lrate',.001),('schedule','constant'),('augment',False),('freeze_backbone',0)]:check(label+'/config/'+k,config['train'][k],v)
        for k,v in [('epochs',200),('final_epoch_zero_based',199),('checkpoint_epoch',199),('optimizer_steps',5600)]:check(label+'/'+k,result[k],v)
        check(label+'/epochs_reached','max_epochs=200` reached' in (bundle/'training/training.log').read_text());check(label+'/training_log_hash',result['training_log_sha256'],sha(bundle/'training/training.log'));check(label+'/model_hash',result['model_sha256'],sha(bundle/'final_epoch.mlmodel'));check(label+'/reset_proof_hash',result['head_reset_proof_sha256'],sha(bundle/'head_reset_proof.json'));checkpoints=list((bundle/'training/checkpoints').glob('checkpoint_199-*.ckpt'));check(label+'/one_checkpoint',len(checkpoints),1)
        if len(checkpoints)==1:check(label+'/checkpoint_hash',result['checkpoint_sha256'],sha(checkpoints[0]))
        outputs=result['training_predictions'];check(label+'/training_prediction_ids',[r['id'] for r in outputs],[r['id'] for r in train]);eva_total=0;unit_total=0;exact=0
        for r in outputs:
            name=label+'/train/'+r['id'];reference=by[r['id']]['reference'];text=dec(r['raw_prediction'],variant);check(name+'/reference',r['reference'],reference);check(name+'/encoded_reference',r['encoded_reference'],enc(reference,variant));check(name+'/expanded_prediction',r['eva_prediction'],text);distance=edit(reference,text);unit=edit(enc(reference,variant),r['raw_prediction']);check(name+'/eva_errors',r['eva_errors'],distance);check(name+'/unit_errors',r['unit_errors'],unit);eva_total+=distance;unit_total+=unit;exact+=reference==text
        check(label+'/training_eva_total',result['training_eva_errors'],eva_total);check(label+'/training_unit_total',result['training_unit_errors'],unit_total);check(label+'/training_exact',result['training_exact_words'],exact)
        failed=root/'initial_failed_attempt'/variant/'head_reset_proof.json'
        if failed.exists():failure_weight_replays[variant]={'reset_tensor_states_equal':read(failed)['reset_tensors']==proof['reset_tensors'],'source_tensor_states_equal':read(failed)['source_tensors']==proof['source_tensors']}
    check('paired_source_tensors',proofs['reset_letters']['source_tensors'],proofs['reset_groups']['source_tensors']);check('paired_execution_commit',run_results['reset_letters']['execution_commit'],run_results['reset_groups']['execution_commit'])
    def metrics(rs):
        if not rs:return None
        n=sum(len(r['reference']) for r in rs)
        return {m:{'errors':sum(edit(r['reference'],r['predictions'][m]) for r in rs),'eva_characters':n,'cer':sum(edit(r['reference'],r['predictions'][m]) for r in rs)/n,'exact_words':sum(r['reference']==r['predictions'][m] for r in rs),'words':len(rs),'exact_word_fraction':sum(r['reference']==r['predictions'][m] for r in rs)/len(rs)} for m in rs[0]['predictions']}
    def summary(rs):
        out={}
        for role in ['historical_development','reserved']:
            selected=[r for r in rs if r['role']==role];out[role]={'all':metrics(selected),'seen':metrics([r for r in selected if r['seen_in_training']]),'unseen':metrics([r for r in selected if not r['seen_in_training']]),'length_1_4':metrics([r for r in selected if len(r['reference'])<=4]),'length_5_6':metrics([r for r in selected if 5<=len(r['reference'])<=6]),'length_7_plus':metrics([r for r in selected if len(r['reference'])>=7])}
        return out
    common=root/'common_evaluation';result=read(common/'result.json');scored=result['rows'];check('common/plan',result['plan_sha256'],sha(plan_path));check('common/first_pass',result['primary_pass'],0);check('common/two_passes',result['passes'],2);check('common/dataset',result['prepared_dataset_sha256'],plan['prepared_dataset_sha256']);check('common/model_source',result['model_sha256']['source'],plan['source_model_sha256']);check('common/evaluation_ids',[r['id'] for r in scored],[r['id'] for r in evaluation]);baseline={r['id']:r for r in read(repo/plan['cached_baselines_path'])['rows']};check('common/cached_comparator_hash',result['cached_baselines_sha256'],sha(repo/plan['cached_baselines_path']))
    for variant in plan['variants']:check('common/model/'+variant,result['model_sha256'][variant],sha(root/'runs'/variant/'final_epoch.mlmodel'))
    for i,(r,original) in enumerate(zip(scored,evaluation)):
        label='evaluation/'+r['id'];check(label+'/reference',r['reference'],original['reference']);check(label+'/folio',r['folio'],original['folio']);check(label+'/role',r['role'],original['role']);check(label+'/vocabulary_seen',r['seen_in_training'],r['reference'] in vocabulary);check(label+'/nearest_id',r['nearest_train_id'],baseline[r['id']]['nearest_train_id']);check(label+'/nearest_text',r['predictions']['nearest_image'],baseline[r['id']]['predictions']['nearest_image'])
        for name in ['source']+plan['variants']:
            p=result['all_pass_raw_predictions'][0][name][i];check(label+'/'+name+'/raw',r['raw_predictions'][name],p);text=dec(p,'reset_letters' if name=='source' else name);check(label+'/'+name+'/eva',r['predictions'][name],text);check(label+'/'+name+'/valid_lowercase',all('a'<=c<='z' for c in text))
        for method,pred in r['predictions'].items():check(label+'/'+method+'/edit',r['errors'][method],edit(r['reference'],pred))
    actual_summary=summary(scored);check('common/all_slices',result['metrics'],actual_summary)
    for folio in ['f4r','f4v','f7r','f7v']:check('common/folio/'+folio,result['by_folio'][folio],summary([r for r in scored if r['folio']==folio]))
    replay=[]
    for name in ['source']+plan['variants']:
        for pass_index in [0,1]:check('common/'+name+'/pass'+str(pass_index)+'/rows',len(result['all_pass_raw_predictions'][pass_index][name]),282);check('common/'+name+'/pass'+str(pass_index)+'/forward_calls',result['forward_calls'][pass_index][name],282)
        replay.extend({'model':name,'id':r['id'],'pass0':result['all_pass_raw_predictions'][0][name][i],'pass1':result['all_pass_raw_predictions'][1][name][i]} for i,r in enumerate(evaluation) if result['all_pass_raw_predictions'][0][name][i]!=result['all_pass_raw_predictions'][1][name][i])
    check('common/replay_differences',result['within_process_replay_differences'],replay);previous={r['id']:r['predictions']['expanded_200'] for r in read(repo/'results/kraken_expansion/common_evaluation/result.json')['rows']};differences=[{'id':r['id'],'previous_common':previous[r['id']],'current_source':r['predictions']['source']} for r in scored if previous[r['id']]!=r['predictions']['source']];check('common/source_previous_differences',result['source_differences_from_previous_common'],differences)
    check('common/no_evaluation_training',result['new_training_in_evaluation'],'NOT_RUN');check('common/no_translation',result['translation'],'NOT_RUN');primary=[r for r in scored if r['role']=='reserved' and not r['seen_in_training']];check('primary/words',len(primary),76);check('primary/eva_characters',sum(len(r['reference']) for r in primary),446)
    exact_unseen={name:[{'id':r['id'],'reference':r['reference']} for r in primary if r['reference']==r['predictions'][name]] for name in ['source']+plan['variants']}
    return {'status':'PASS' if not errors else 'FAIL','checks':checks,'mismatches':errors,'plan_sha256':sha(plan_path),'common_result_sha256':sha(common/'result.json'),'run_id':result['run_id'],'execution_commit':result['execution_commit'],'primary_reserved_unseen':actual_summary['reserved']['unseen'],'all_metrics':actual_summary,'same_process_replay_differences':len(replay),'logged_forward_calls':sum(sum(c.values()) for c in result['forward_calls']),'failed_and_corrected_reset_states':failure_weight_replays,'unseen_exact_matches':exact_unseen,'scope':'Independent regex grouping, expansion, encoded-label hashes, exported tensor records, input/weight/log/checkpoint hashes, full-matrix edit distances, all slices and repeat inventories. No new inference, expert glyph review or semantic validation.','translation':'NOT_RUN'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=audit(a.bundle,a.repo);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','checks','mismatches','same_process_replay_differences','logged_forward_calls']}));raise SystemExit(r['status']!='PASS')
