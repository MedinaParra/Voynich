#!/usr/bin/env python3
"""Capture the original decoder's probabilities; compare fixed CTC searches."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time
import traceback
import numpy as np
from eva_unit_tools import read,sha,save,restore_and_load,slices
from ctc_prefix_tools import validate,greedy,prefix_beam
from kraken_eva_word_training import recognize,tensor_manifest
from kraken_row_tools import levenshtein


def matrix_sha(p):return hashlib.sha256(np.asarray(p,dtype=np.float32).tobytes(order='C')).hexdigest()


def run(a):
    import torch
    from kraken.lib.models import load_any
    plan=read(a.plan);path=a.repo/plan['source_model_path']
    if sha(path)!=plan['source_model_sha256']:raise ValueError('Changed frozen model')
    data,train,rows=restore_and_load(a.repo,plan);vocabulary={r['reference'] for r in train};torch.set_num_threads(2);torch.manual_seed(plan['seed']);torch.use_deterministic_algorithms(True)
    net=load_any(str(path),train=False,device='cpu');before=tensor_manifest(net.nn);codec=net.codec.c2l
    if any(len(c)!=1 or not 'a'<=c<='z' or len(labels)!=1 for c,labels in codec.items()):raise ValueError('Expected single-character EVA codec')
    id_text={labels[0]:c for c,labels in codec.items()};save(a.out/'codec.json',codec)
    def text(labels):return ''.join(id_text[int(i)] for i in labels)
    original_decoder=net.decoder;captured=[]
    def capture(outputs,seq_lens=None):
        values=np.asarray(outputs)
        if values.ndim==2:values=values[None,:,:]
        if values.ndim!=3 or values.shape[0]!=1:raise ValueError('Unexpected original decoder batch')
        length=values.shape[-1] if seq_lens is None else int(np.atleast_1d(seq_lens)[0]);p=values[0,:,:length].T.copy()
        validate(p)
        if p.shape[1]!=max(id_text)+1:raise ValueError('Posterior class count changed')
        captured.append(p);return original_decoder(outputs,seq_lens)
    net.decoder=capture;counter={'n':0}
    def count(*args):counter['n']+=1
    handle=net.nn.nn.register_forward_hook(count);caches=[];legacy_passes=[];counts=[];capture_records=[];parity=[];started=time.perf_counter()
    for pass_index in range(plan['passes']):
        cache={};legacy=[];call_start=counter['n']
        for r in rows:
            captured.clear();prediction=recognize(net,[r])[0]
            if len(captured)!=1:raise ValueError('Expected one captured decoder matrix')
            p=captured[0];cache[r['id']]=p;custom=text(greedy(p));legacy.append(prediction)
            capture_records.append({'pass':pass_index,'id':r['id'],'image_sha256':r['image_sha256'],'shape':list(p.shape),'dtype':str(p.dtype),'matrix_sha256':matrix_sha(p),'maximum_row_sum_error':float(np.max(np.abs(p.sum(axis=1,dtype=np.float64)-1)))})
            if custom!=prediction:parity.append({'pass':pass_index,'id':r['id'],'original':prediction,'custom_greedy':custom})
        name='posterior_pass'+str(pass_index)+'.npz';np.savez_compressed(a.out/name,**cache);caches.append(cache);legacy_passes.append(legacy);counts.append(counter['n']-call_start)
    handle.remove();after=tensor_manifest(net.nn);net.decoder=original_decoder
    save(a.out/'capture_records.json',capture_records);save(a.out/'interface_parity.json',{'status':'PASS' if not parity else 'FAIL_NO_BEAM_COMPARISON','checks':len(rows)*plan['passes'],'differences':parity,'source_tensors_before':before,'source_tensors_after':after})
    if parity or before!=after:raise ValueError('Original/custom greedy parity or immutable-weight check failed; beam not scored')
    cached={r['id']:r for r in read(a.repo/plan['cached_baselines_path'])['rows']};passes=[];scored=[]
    for pass_index,cache in enumerate(caches):
        outputs={};details={}
        for i,r in enumerate(rows):
            p=cache[r['id']];order=np.random.default_rng(plan['seed']+i).permutation(len(p));label_sequence,logmass=prefix_beam(p,plan['beam_width'])[0];shuffled,shuffled_mass=prefix_beam(p[order],plan['beam_width'])[0]
            outputs[r['id']]={'greedy':text(greedy(p)),'beam32':text(label_sequence),'shuffled_beam32':text(shuffled)}
            details[r['id']]={'beam_labels':list(label_sequence),'beam_logmass':logmass,'shuffled_labels':list(shuffled),'shuffled_logmass':shuffled_mass,'frame_permutation':order.tolist()}
            if pass_index==0:
                predictions={**outputs[r['id']],'nearest_image':cached[r['id']]['predictions']['nearest_image']}
                if cached[r['id']]['reference']!=r['reference']:raise ValueError('Cached comparator reference changed')
                scored.append({'id':r['id'],'folio':r['folio'],'role':r['role'],'reference':r['reference'],'seen_in_training':r['reference'] in vocabulary,'predictions':predictions,'errors':{k:levenshtein(r['reference'],v) for k,v in predictions.items()},'decoder_details':details[r['id']],'nearest_train_id':cached[r['id']]['nearest_train_id']})
        passes.append({'predictions':outputs,'details':details})
    repeat=[{'id':r['id'],'method':m,'pass0':passes[0]['predictions'][r['id']][m],'pass1':passes[1]['predictions'][r['id']][m]} for r in rows for m in ['greedy','beam32','shuffled_beam32'] if passes[0]['predictions'][r['id']][m]!=passes[1]['predictions'][r['id']][m]]
    matrix_repeat=[r['id'] for r in rows if matrix_sha(caches[0][r['id']])!=matrix_sha(caches[1][r['id']])]
    primary=[r for r in scored if r['role']=='reserved' and not r['seen_in_training']]
    if len(primary)!=76 or sum(len(r['reference']) for r in primary)!=446:raise ValueError('Primary stratum changed')
    result={'status':'EXECUTED_FROZEN_CTC_POSTERIOR_COMPARISON','plan_sha256':sha(a.plan),'source_model_sha256':sha(path),'prepared_dataset_sha256':plan['prepared_dataset_sha256'],'cached_baselines_sha256':sha(a.repo/plan['cached_baselines_path']),'beam_width':plan['beam_width'],'label_pruning':'NONE','word_lexicon':'NONE','language_model':'NONE','primary_pass':0,'passes':2,'metrics':slices(scored),'rows':scored,'all_pass_results':passes,'legacy_text_passes':legacy_passes,'forward_calls':counts,'matrix_replay_differences':matrix_repeat,'text_replay_differences':repeat,'interface_parity_checks':len(rows)*2,'interface_parity_differences':parity,'source_tensors_unchanged':before==after,
            'posterior_file_sha256':{name:sha(a.out/name) for name in ['posterior_pass0.npz','posterior_pass1.npz']},'capture_records_sha256':sha(a.out/'capture_records.json'),'seconds_capture_and_decoding':time.perf_counter()-started,'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),'environment':{p:importlib.metadata.version(p) for p in ['torch','torchvision','kraken','numpy','pillow','scipy','lightning']},'scope':plan['scope'],'new_training':'NOT_RUN','expert_review':'NOT_REVIEWED','translation':'NOT_RUN'}
    save(a.out/'result.json',result);print('POSTERIOR_RESULT='+json.dumps({k:v for k,v in result.items() if k not in ['rows','all_pass_results','legacy_text_passes','environment']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    try:run(a)
    except Exception as e:save(a.out/'failure.json',{'error':str(e),'traceback':traceback.format_exc(),'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA')});raise
