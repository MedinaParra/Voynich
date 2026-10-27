#!/usr/bin/env python3
"""Full-matrix numerical audit of both passes; no neural inference."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from audit_kraken_stage2 import edit


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def audit(bundle,prepared,runs,repo):
    result=read(bundle/'result.json');data=read(prepared/'dataset.json');rows=[r for r in data if r['role'] in ['historical_development','reserved']];scored=result['rows'];checks=0;errors=[]
    def check(label,a,b=True):
        nonlocal checks
        checks+=1
        if a!=b:errors.append({'check':label,'actual':a,'expected':b})
    def metrics(rs):
        n=sum(len(r['reference']) for r in rs);multi=[r for r in rs if len(r['reference'])>1]
        return {m:{'errors':sum(edit(r['reference'],r['predictions'][m]) for r in rs),'reference_characters':n,'cer':sum(edit(r['reference'],r['predictions'][m]) for r in rs)/n,'exact_words':sum(r['reference']==r['predictions'][m] for r in rs),'words':len(rs),'exact_word_fraction':sum(r['reference']==r['predictions'][m] for r in rs)/len(rs),'multicharacter_exact_words':sum(r['reference']==r['predictions'][m] for r in multi),'multicharacter_words':len(multi)} for m in rs[0]['predictions']}
    models={'initial':repo/'results/kraken_eva_words/runs/aligned_200/final_epoch.mlmodel',**{name:runs/name/'final_epoch.mlmodel' for name in ['continuation_200','expanded_200']}}
    for name,p in models.items():check('model/'+name,result['model_sha256'][name],sha(p))
    check('input_metadata',result['prepared_dataset_sha256'],sha(prepared/'dataset.json'));check('primary_pass',result['primary_pass'],0);check('two_passes',result['passes'],2);check('evaluation_ids',[r['id'] for r in scored],[r['id'] for r in rows]);check('roles',Counter(r['role'] for r in scored),Counter({'historical_development':147,'reserved':135}))
    old={r['reference'] for r in data if r['role']=='original_train'};expanded={r['reference'] for r in data if r['role'] in ['original_train','additional_train']}
    for i,(r,source) in enumerate(zip(scored,rows)):
        label=r['id'];check(label+'/reference',r['reference'],source['reference']);check(label+'/folio',r['folio'],source['folio']);check(label+'/role',r['role'],source['role']);check(label+'/seen_old',r['seen_in_original_training'],r['reference'] in old);check(label+'/seen_expanded',r['seen_in_expanded_training'],r['reference'] in expanded)
        for name in models:check(label+'/'+name+'/pass0',r['predictions'][name],result['all_pass_predictions'][0][name][i]);check(label+'/'+name+'/edit',r['errors'][name],edit(r['reference'],r['predictions'][name]))
    for role in ['historical_development','reserved']:check(role+'/metrics',result['metrics'][role],metrics([r for r in scored if r['role']==role]))
    for f in ['f4r','f4v','f7r','f7v']:check(f+'/metrics',result['by_folio'][f],metrics([r for r in scored if r['folio']==f]))
    differences=[]
    for name in models:
        for index in [0,1]:check(name+'/pass'+str(index)+'/predictions',len(result['all_pass_predictions'][index][name]),282);check(name+'/pass'+str(index)+'/network_calls',result['forward_calls'][index][name],282)
        differences.extend({'model':name,'id':r['id'],'pass0':result['all_pass_predictions'][0][name][i],'pass1':result['all_pass_predictions'][1][name][i]} for i,r in enumerate(scored) if result['all_pass_predictions'][0][name][i]!=result['all_pass_predictions'][1][name][i])
    check('repeat_differences',result['within_process_replay_differences'],differences)
    for name in ['continuation_200','expanded_200']:
        previous={r['id']:r for r in read(runs/name/'result.json')['rows']}
        for key,method in [(name,'kraken'),(name+'_initial','frozen_initial')]:
            common_name=name if method=='kraken' else 'initial';expected=[{'id':r['id'],'training_job':previous[r['id']]['predictions'][method],'common_pass0':r['predictions'][common_name]} for r in scored if previous[r['id']]['predictions'][method]!=r['predictions'][common_name]];check('training_comparison/'+key,result['differences_from_training_jobs'][key],expected)
    check('no_new_training',result['new_training'],'NOT_RUN');check('no_translation',result['translation'],'NOT_RUN')
    exacts={role:[{'id':r['id'],'reference':r['reference'],'seen_in_expanded_training':r['seen_in_expanded_training']} for r in scored if r['role']==role and r['reference']==r['predictions']['expanded_200']] for role in ['historical_development','reserved']}
    return {'status':'PASS' if not errors else 'FAIL','checks':checks,'mismatches':errors,'common_run_id':result['run_id'],'result_sha256':sha(bundle/'result.json'),'same_process_replay_differences':len(differences),'forward_calls':sum(sum(p.values()) for p in result['forward_calls']),'metrics':result['metrics'],'expanded_exact_matches':exacts,'scope':'Independent edit-distance arithmetic, aggregation, model hashes, fixed first pass, both prediction inventories and logged network counters. No new inference, training, external paleographic or semantic validation.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--runs',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=audit(a.bundle,a.prepared,a.runs,a.repo);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','checks','mismatches','same_process_replay_differences','forward_calls']}));raise SystemExit(r['status']!='PASS')
