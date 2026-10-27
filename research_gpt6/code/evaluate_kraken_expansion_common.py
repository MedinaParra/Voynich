#!/usr/bin/env python3
"""Two fixed passes over three frozen models in one process; no training."""
import argparse
from collections import Counter
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import time
import traceback
import torch
from kraken.lib.models import load_any
from kraken_eva_word_training import sha,save,recognize
from kraken_row_tools import levenshtein
from retrain_kraken_expansion import metrics


def run(a):
    expected={'initial':'c2b93256804d4697b56990e6bae0ae132942308ab9038b220a06352f8b013e8b','continuation_200':'08e3586bc39103eaea3a984e85ec050531f46ef1a79c2d97b0ff06344b8eeaab','expanded_200':'35092d9baf56083eb6c70a2e32c478d8910ef5e685d0cee33fc5a935ca1c71d8'}
    models={'initial':a.repo/'results/kraken_eva_words/runs/aligned_200/final_epoch.mlmodel',**{v:a.runs/v/'final_epoch.mlmodel' for v in ['continuation_200','expanded_200']}}
    for name,path in models.items():
        if sha(path)!=expected[name]:raise ValueError('Changed frozen model '+name)
    execution=json.loads((a.repo/'data/kraken_expansion_execution.json').read_text())
    for name,h in execution['prepared_hashes'].items():
        if sha(a.prepared/name)!=h:raise ValueError('Changed input metadata '+name)
    data=json.loads((a.prepared/'dataset.json').read_text());rows=[dict(r) for r in data if r['role'] in ['historical_development','reserved']]
    for r in rows:
        r['path']=str((a.prepared/'crops'/Path(r['path']).name).resolve())
        if sha(r['path'])!=r['image_sha256']:raise ValueError('Changed sample')
    if Counter(r['role'] for r in rows)!=Counter({'historical_development':147,'reserved':135}):raise ValueError('Changed evaluation split')
    torch.set_num_threads(2);torch.manual_seed(20261027);torch.use_deterministic_algorithms(True);passes=[];calls=[];timings=[]
    for pass_index in range(2):
        output={};forward_counts={};seconds={}
        for name,path in models.items():
            net=load_any(str(path),train=False,device='cpu');counter={'calls':0}
            def count(*args):counter['calls']+=1
            handle=net.nn.nn.register_forward_hook(count);started=time.perf_counter();output[name]=recognize(net,rows);seconds[name]=time.perf_counter()-started;handle.remove();forward_counts[name]=counter['calls'];del net
        passes.append(output);calls.append(forward_counts);timings.append(seconds)
    scored=[]
    old_vocabulary={r['reference'] for r in data if r['role']=='original_train'};new_vocabulary={r['reference'] for r in data if r['role'] in ['original_train','additional_train']}
    for i,r in enumerate(rows):
        predictions={name:p[i] for name,p in passes[0].items()};scored.append({'id':r['id'],'folio':r['folio'],'role':r['role'],'reference':r['reference'],'predictions':predictions,'errors':{name:levenshtein(r['reference'],p) for name,p in predictions.items()},'seen_in_original_training':r['reference'] in old_vocabulary,'seen_in_expanded_training':r['reference'] in new_vocabulary})
    replay_differences=[{'model':name,'id':r['id'],'pass0':passes[0][name][i],'pass1':passes[1][name][i]} for name in models for i,r in enumerate(rows) if passes[0][name][i]!=passes[1][name][i]]
    prior_differences={}
    for variant in ['continuation_200','expanded_200']:
        previous=json.loads((a.runs/variant/'result.json').read_text());by={r['id']:r for r in previous['rows']}
        prior_differences[variant]=[{'id':r['id'],'training_job':by[r['id']]['predictions']['kraken'],'common_pass0':r['predictions'][variant]} for r in scored if by[r['id']]['predictions']['kraken']!=r['predictions'][variant]]
        prior_differences[variant+'_initial']=[{'id':r['id'],'training_job':by[r['id']]['predictions']['frozen_initial'],'common_pass0':r['predictions']['initial']} for r in scored if by[r['id']]['predictions']['frozen_initial']!=r['predictions']['initial']]
    cpu=[line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')]
    result={'status':'EXECUTED_SAME_PROCESS_REPLAY_NOT_NEW_TRAINING','primary_pass':0,'passes':2,'model_sha256':expected,'prepared_dataset_sha256':sha(a.prepared/'dataset.json'),
            'metrics':{role:metrics([r for r in scored if r['role']==role]) for role in ['historical_development','reserved']},'by_folio':{f:metrics([r for r in scored if r['folio']==f]) for f in sorted({r['folio'] for r in scored})},
            'rows':scored,'all_pass_predictions':passes,'forward_calls':calls,'seconds':timings,'within_process_replay_differences':replay_differences,'differences_from_training_jobs':prior_differences,
            'run_id':os.getenv('GITHUB_RUN_ID'),'execution_commit':os.getenv('GITHUB_SHA'),'environment':{k:importlib.metadata.version(k) for k in ['torch','torchvision','kraken','pillow','numpy','scipy','lightning']},'hardware':{'machine':platform.machine(),'cpu_model':cpu[0] if cpu else None,'logical_cpus':os.cpu_count(),'threads':torch.get_num_threads()},
            'expert_review':'NOT_REVIEWED','translation':'NOT_RUN','new_training':'NOT_RUN','scope':'Post-hoc diagnostic after observing cross-server inference variation; same-process comparisons, no checkpoint selection or new external validation.'}
    save(a.out/'result.json',result);print('COMMON_EVALUATION_RESULT='+json.dumps({k:v for k,v in result.items() if k not in ['rows','all_pass_predictions','differences_from_training_jobs','by_folio','environment']},ensure_ascii=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--runs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    try:run(a)
    except Exception as e:save(a.out/'failure.json',{'error':str(e),'traceback':traceback.format_exc()});raise
