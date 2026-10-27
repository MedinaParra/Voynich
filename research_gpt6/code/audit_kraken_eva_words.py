#!/usr/bin/env python3
"""Audit preserved EVA retraining outputs; no training or fresh inference.

Uses a full edit matrix and scalar image features independent of the training
driver. Does not authenticate candidate readings or assess a translation.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from audit_kraken_stage2 import edit, feature


def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def restore_crops(root, repo):
    """Reconstruct ephemeral crop files from preserved photos and metadata."""
    plan=read(repo/'data/kraken_eva_words_plan.json');padding=plan['padding_pixels'];images={}
    for variant in ['aligned_200','permuted_200']:
        bundle=root/variant
        for r in read(bundle/'dataset.json'):
            source=repo/r['source_image_path']
            if source not in images:
                if sha(source)!=r['source_image_sha256']:raise ValueError('Changed source photograph')
                images[source]=Image.open(source).convert('RGB')
            x0,y0,x1,y1=r['bounds'];size=(x1-x0,y1-y0)
            mask=Image.new('L',size,0)
            ImageDraw.Draw(mask).polygon([(round(x-x0),round(y-y0)) for x,y in r['polygon']],fill=255)
            if padding:mask=mask.filter(ImageFilter.MaxFilter(2*padding+1))
            crop=Image.composite(images[source].crop(r['bounds']),Image.new('RGB',size,'white'),mask)
            path=bundle/'crops'/Path(r['path']).name;path.parent.mkdir(parents=True,exist_ok=True)
            mp=bundle/'crops'/Path(r['mask_path']).name
            if not path.exists():crop.save(path)
            if not mp.exists():mask.save(mp)
            gt=path.with_suffix('.gt.txt')
            if not gt.exists():gt.write_text(r['training_text'])
            if sha(path)!=r['image_sha256'] or sha(mp)!=r['mask_sha256']:raise ValueError('Restored PNG differs from archived bytes; use Pillow 12.3.0')


def run(root, repo):
    plan_path = repo/'data/kraken_eva_words_plan.json'
    plan = read(plan_path)
    source = {f"{w['folio']}_w{w['index']:04d}": w
              for w in read(repo/plan['words_path'])
              if w['yale_polygon'] is not None and not w['flags']}
    pages = {p['folio']: p for p in read(repo/plan['inputs_path'])['pages']}
    images = {f: Image.open(repo/p['yale_path']).convert('RGB') for f,p in pages.items()}
    errors = []; checks = 0

    def check(label, actual, expected=True):
        nonlocal checks
        checks += 1
        equal = (math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-12)
                 if isinstance(actual, (int,float)) and isinstance(expected, (int,float))
                 else actual == expected)
        if not equal: errors.append({'check':label,'actual':json.loads(json.dumps(actual,default=repr)),'expected':json.loads(json.dumps(expected,default=repr))})

    def metrics(rows):
        count = sum(len(r['reference']) for r in rows)
        return {m:{'errors':sum(edit(r['reference'],r['predictions'][m]) for r in rows),
                   'reference_characters':count,
                   'cer':sum(edit(r['reference'],r['predictions'][m]) for r in rows)/count,
                   'exact_words':sum(r['reference']==r['predictions'][m] for r in rows),
                   'words':len(rows),
                   'exact_word_fraction':sum(r['reference']==r['predictions'][m] for r in rows)/len(rows)}
                for m in rows[0]['predictions']}

    datasets = {}; results = {}; summaries = {}
    for variant in ['aligned_200','permuted_200']:
        bundle = root/variant
        ds = read(bundle/'dataset.json'); by = {r['id']:r for r in ds}
        result = read(bundle/'result.json'); prep = read(bundle/'preparation.json')
        datasets[variant] = ds; results[variant] = result
        check(variant+':all_ids', set(by), set(source))
        check(variant+':no_duplicate_ids',len(ds),len(by))
        check(variant+':variant',result['variant'],variant)
        check(variant+':plan',result['plan_sha256'],sha(plan_path))
        check(variant+':epochs',result['epochs'],200)
        check(variant+':last_epoch',result['final_epoch_zero_based'],199)
        train = [r for r in ds if r['role']=='train']; dev = [r for r in ds if r['role']=='development']
        check(variant+':training_count',len(train),197);check(variant+':development_count',len(dev),147)
        check(variant+':training_characters',sum(len(r['reference']) for r in train),944)
        check(variant+':development_characters',sum(len(r['reference']) for r in dev),744)
        check(variant+':train_leaves',{r['folio'][:-1] for r in train},{'f3'})
        check(variant+':development_leaves',{r['folio'][:-1] for r in dev},{'f4'})
        for r in ds:
            label = variant+':'+r['id']; original = source[r['id']]
            check(label+':EVA',r['reference'],original['eva'])
            check(label+':polygon',r['polygon'],original['yale_polygon'])
            check(label+':source_sha',r['source_image_sha256'],sha(repo/r['source_image_path']))
            crop = bundle/'crops'/Path(r['path']).name
            mask_path = bundle/'crops'/Path(r['mask_path']).name
            check(label+':crop_hash',sha(crop),r['image_sha256']);check(label+':mask_hash',sha(mask_path),r['mask_sha256'])
            with Image.open(crop) as im: actual = np.array(im.convert('RGB'))
            with Image.open(mask_path) as im: mask = np.array(im.convert('L'))
            bounds = r['bounds']; x0,y0,x1,y1 = bounds; polygon = r['polygon']; padding = plan['padding_pixels']
            page = images[r['folio']]
            expected_bounds = [max(0,math.floor(min(p[0] for p in polygon))-padding),
                               max(0,math.floor(min(p[1] for p in polygon))-padding),
                               min(page.width,math.ceil(max(p[0] for p in polygon))+padding),
                               min(page.height,math.ceil(max(p[1] for p in polygon))+padding)]
            check(label+':bounds',bounds,expected_bounds)
            raw = np.array(page.crop(bounds)); check(label+':size',list(raw.shape[:2][::-1]),r['crop_size'])
            expected_mask = Image.new('L',(x1-x0,y1-y0),0)
            ImageDraw.Draw(expected_mask).polygon([(round(x-x0),round(y-y0)) for x,y in polygon],fill=255)
            if padding: expected_mask = expected_mask.filter(ImageFilter.MaxFilter(2*padding+1))
            check(label+':mask_geometry',bool(np.array_equal(mask,np.array(expected_mask))))
            check(label+':original_pixels_inside',bool(np.array_equal(actual[mask==255],raw[mask==255])))
            check(label+':white_outside',bool(np.all(actual[mask==0]==255)))
            check(label+':label_file',crop.with_suffix('.gt.txt').read_text(),r['training_text'])
            assigned = by[r['training_label_source_id']]
            check(label+':assigned_text',r['training_text'],assigned['reference'])
            check(label+':same_role',r['role'],assigned['role'])
            check(label+':same_folio',r['folio'],assigned['folio'])
            check(label+':same_length',len(r['reference']),len(assigned['reference']))
            if variant=='aligned_200' or r['role']=='development':check(label+':unchanged_label',r['training_text'],r['reference'])
        check(variant+':preserved_train_inventory',Counter(r['training_text'] for r in train),Counter(r['reference'] for r in train))
        check(variant+':changed_training_labels',sum(r['training_text']!=r['reference'] for r in train),186 if variant=='permuted_200' else 0)
        check(variant+':reported_label_changes',prep['changed_training_labels'],186 if variant=='permuted_200' else 0)
        check(variant+':development_unchanged',prep['changed_development_labels'],0)
        config = read(bundle/'training/training_config.json'); command = read(bundle/'training/command.json')
        check(variant+':monitor_train_only',config['train']['training_data'],config['train']['evaluation_data'])
        check(variant+':monitor_only_train_files',[Path(p).name for p in (bundle/'training/train.lst').read_text().splitlines()],[Path(r['path']).name for r in train])
        for key,value in [('epochs',200),('min_epochs',200),('freq',200),('batch_size',16),('lrate',.001),('augment',False),('schedule','constant'),('freeze_backbone',0)]:check(variant+':config_'+key,config['train'][key],value)
        check(variant+':load_argument','--load' in command)
        check(variant+':resize_argument',command[-2:],['--resize','new'])
        check(variant+':source_model',result['warmstart_source_sha256'],plan['warmstart_sha256'])
        proof = read(bundle/'warmstart_equivalence.json')
        check(variant+':all_source_tensors_preserved',proof['source_tensors'],proof['converted_tensors'])
        check(variant+':tensor_proof_not_empty',len(proof['source_tensors'])>0)
        check(variant+':tensor_equivalence_report',proof['tensor_states_equal'])
        check(variant+':codec_equivalence_report',proof['codec_equal'])
        check(variant+':converted_hash',proof['converted_sha256'],sha(bundle/'warmstart.safetensors'))
        check(variant+':source_proof_hash',proof['source_sha256'],plan['warmstart_sha256'])
        check(variant+':model_hash',result['model_sha256'],sha(bundle/'final_epoch.mlmodel'))
        check(variant+':model_bytes_different_from_source',result['model_sha256']!=plan['warmstart_sha256'])
        check(variant+':log_hash',result['training_log_sha256'],sha(bundle/'training/training.log'))
        check(variant+':200_epochs_reached','max_epochs=200` reached' in (bundle/'training/training.log').read_text())
        checkpoints=list((bundle/'training/checkpoints').glob('checkpoint_199-*.ckpt'))
        check(variant+':one_final_checkpoint',len(checkpoints),1)
        if len(checkpoints)==1:check(variant+':checkpoint_hash',result['checkpoint_sha256'],sha(checkpoints[0]))
        codec = read(bundle/'trained_codec.json'); alphabet = set(''.join(r['reference'] for r in train))
        check(variant+':EVA_codec',set(''.join(codec)),alphabet)
        check(variant+':no_PUA',not any(ord(c)>=0xF0000 for c in ''.join(codec)))
        train_features=[feature(bundle/'crops'/Path(r['path']).name) for r in train]
        word = Counter(r['reference'] for r in train).most_common(1)[0][0]
        char = Counter(''.join(r['reference'] for r in train)).most_common(1)[0][0]
        nchar = int(statistics.median(len(r['reference']) for r in train)); vocabulary={r['reference'] for r in train}
        scored = result['rows']; check(variant+':development_output_ids',[r['id'] for r in scored],[r['id'] for r in dev])
        for r in scored:
            label=variant+':score:'+r['id']; target=by[r['id']]['reference'];check(label+':reference',r['reference'],target)
            f,a=feature(bundle/'crops'/Path(by[r['id']]['path']).name)
            distances=[math.fsum((x-y)**2 for x,y in zip(f,g))/len(f)+.05*(a-b)**2 for g,b in train_features]
            nearest=train[min(range(len(train)),key=lambda i:distances[i])]
            check(label+':nearest_id',r['nearest_train_id'],nearest['id'])
            for m,value in [('nearest_image',nearest['reference']),('mode_word',word),('repeat_character',char*nchar),('empty','')]:check(label+':'+m,r['predictions'][m],value)
            check(label+':vocabulary_seen',r['reference_seen_in_true_training_words'],target in vocabulary)
            check(label+':predicted_alphabet',set(r['predictions']['kraken'])<=alphabet)
            for m,pred in r['predictions'].items():check(label+':edit:'+m,r['errors'][m],edit(target,pred))
        for m,fields in metrics(scored).items():
            for key,value in fields.items():check(variant+':metric:'+m+':'+key,result['metrics'][m][key],value)
        for folio in sorted({r['folio'] for r in scored}):check(variant+':folio:'+folio,result['by_folio'][folio],metrics([r for r in scored if r['folio']==folio]))
        for key,seen in [('seen',True),('unseen',False)]:
            selected=[r for r in scored if r['reference_seen_in_true_training_words']==seen]
            check(variant+':lexical:'+key,result['lexical_strata'][key],metrics(selected) if selected else None)
        outputs=result['training_predictions'];check(variant+':training_output_ids',[r['id'] for r in outputs],[r['id'] for r in train])
        assigned_errors=0;true_errors=0
        for r in outputs:
            target=by[r['id']];label=variant+':train_output:'+r['id']
            check(label+':true_text',r['reference'],target['reference']);check(label+':assigned_text',r['assigned_training_text'],target['training_text'])
            actual=edit(target['reference'],r['prediction']);assigned=edit(target['training_text'],r['prediction'])
            check(label+':true_errors',r['true_errors'],actual);check(label+':assigned_errors',r['assigned_errors'],assigned)
            true_errors+=actual;assigned_errors+=assigned
        check(variant+':training_true_cer',result['training_fit_cer_true'],true_errors/944)
        check(variant+':training_assigned_cer',result['training_fit_cer_assigned'],assigned_errors/944)
        check(variant+':translation',result['translation'],'NOT_RUN')
        check(variant+':expert_review',result['expert_review'],'NOT_REVIEWED')
        summaries[variant]={'development_metrics':result['metrics'],'training_fit_cer_assigned':assigned_errors/944,'training_fit_cer_true':true_errors/944,'result_sha256':sha(bundle/'result.json')}
    a=datasets['aligned_200'];b=datasets['permuted_200']
    check('paired_datasets',[(r['id'],r['reference'],r['image_sha256'],r['mask_sha256'],r['bounds']) for r in a],[(r['id'],r['reference'],r['image_sha256'],r['mask_sha256'],r['bounds']) for r in b])
    check('paired_execution_commit',results['aligned_200']['execution_commit'],results['permuted_200']['execution_commit'])
    check('paired_run_id',results['aligned_200']['run_id'],results['permuted_200']['run_id'])
    for m in ['nearest_image','mode_word','repeat_character','empty']:check('paired_baseline:'+m,results['aligned_200']['metrics'][m],results['permuted_200']['metrics'][m])
    return {'status':'PASS' if not errors else 'FAIL','checks':checks,'mismatches':errors,'run_id':results['aligned_200']['run_id'],'execution_commit':results['aligned_200']['execution_commit'],'summary':summaries,'scope':'Independent arithmetic, input pixels, label and training evidence audit; no fresh inference, expert review or translation.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundles',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--restore-crops',action='store_true');a=p.parse_args()
    if a.restore_crops:restore_crops(a.bundles,a.repo)
    r=run(a.bundles,a.repo);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:r[k] for k in ['status','checks','mismatches']}));raise SystemExit(r['status']!='PASS')
