#!/usr/bin/env python3
"""Numerical audit of the archived Kraken pilot; no new model inference.

Uses augmenting-path maximum matching and a full edit matrix, independently
of the experiment's Hungarian assignment and rolling-row edit distance.
Does not validate the assistant's provisional palaeographic annotations.
"""
import argparse,collections,hashlib,json,math
from pathlib import Path
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def iou(a,b):
    overlap=math.prod(max(0,min(a[k+2],b[k+2])-max(a[k],b[k])) for k in (0,1))
    area=lambda x:math.prod(max(0,x[k+2]-x[k]) for k in (0,1))
    return overlap/(area(a)+area(b)-overlap) if area(a)+area(b)>overlap else 0
def cardinality(pred,truth,t):
    edges=[[j for j,b in enumerate(truth) if iou(a,b)>=t] for a in pred];owners={}
    def visit(i,seen):
        for j in edges[i]:
            if j in seen:continue
            seen.add(j)
            if j not in owners or visit(owners[j],seen):owners[j]=i;return True
        return False
    return sum(visit(i,set()) for i in range(len(pred)))
def edit(a,b):
    d=[[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(len(a)+1):d[i][0]=i
    for j in range(len(b)+1):d[0][j]=j
    for i in range(1,len(a)+1):
        for j in range(1,len(b)+1):d[i][j]=min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]!=b[j-1]))
    return d[-1][-1]
def feature(path):
    with Image.open(path) as im:
        data=[v/255 for v in im.convert('L').resize((64,16),Image.Resampling.LANCZOS).tobytes()];aspect=math.log(im.width/im.height)
    mean=math.fsum(data)/len(data);std=max(.05,math.sqrt(math.fsum((v-mean)**2 for v in data)/len(data)))
    return [(v-mean)/std for v in data],aspect
def run(bundle,repo):
    result=read(bundle/'stage2_result.json');plan=read(repo/'data/kraken_stage2_plan.json');refs=read(repo/'data/kraken_line_reference.json')
    checked=0;errors=[]
    def check(label,a,b=True):
        nonlocal checked
        checked+=1
        equal=math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12) if isinstance(a,(int,float)) and isinstance(b,(int,float)) else a==b
        if not equal:errors.append({'check':label,'actual':a,'expected':b})
    for name,h in read(bundle/'sha256_manifest.json').items():check('manifest:'+name,sha(bundle/name),h)
    check('archived_result',sha(bundle/'stage2_result.json'),'2885560464c395fab2a3a584d932e588dcedce70b56e280d82cb08caf3eeb396')
    for key,name in [('plan_sha256','kraken_stage2_plan.json'),('masks_sha256','kraken_region_masks.json'),('reference_sha256','kraken_line_reference.json')]:check(key,result[key],sha(repo/'data'/name))
    check('source_code_sha256',result['code_sha256'],sha(repo/'code/kraken_stage2.py'))
    ref_by={p['folio']:p['lines'] for p in refs['pages']};cases=result['layout']['cases'];check('case_count',len(cases),24)
    for c in cases:
        name=f"{c['folio']}/{c['width']}/{c['variant']}";p=[x['bbox_normalized'] for x in c['lines']];t=[x['bbox'] for x in ref_by[c['folio']]]
        m=c['matching'];tp=cardinality(p,t,m['threshold'])
        for k,v in {'tp':tp,'fp':len(p)-tp,'fn':len(t)-tp,'pred_count':len(p),'truth_count':len(t),'precision':tp/len(p),'recall':tp/len(t),'f1':2*tp/(len(p)+len(t))}.items():check(name+':'+k,m[k],v)
        check(name+':line_count',c['line_count'],len(p));check(name+':count_error',c['absolute_count_error'],abs(len(p)-len(t)))
        check(name+':pair_count',len(m['pairs']),tp)
        check(name+':pred_unique',len({x['pred'] for x in m['pairs']}),tp);check(name+':truth_unique',len({x['truth'] for x in m['pairs']}),tp)
        for pair in m['pairs']:
            overlap=iou(p[pair['pred']],t[pair['truth']]);check(name+':pair_iou',pair['iou'],overlap);check(name+':pair_threshold',overlap>=m['threshold'])
        for x in c['lines']:check(name+':box_units',all(math.isclose(v,z/s,abs_tol=1e-12) for v,z,s in zip(x['bbox_normalized'],x['bbox_pixels'],c['image_size']*2)))
    primary={}
    for width in plan['layout']['widths']:
        for variant in plan['layout']['variants']:
            selected=[c for c in cases if c['width']==width and c['variant']==variant and c['folio'] in plan['layout']['primary_folios']]
            n=sum(c['line_count'] for c in selected);g=sum(c['reference_count'] for c in selected);tp=sum(c['matching']['tp'] for c in selected)
            key=f'{variant}_{width}';values={'tp':tp,'predicted':n,'reference':g,'f1':2*tp/(n+g),'relative_count_error':sum(abs(c['line_count']-c['reference_count']) for c in selected)/g,'complete':len(selected)==2};primary[key]=values
            for k,v in values.items():check('primary:'+key+':'+k,result['layout']['primary_summaries'][key][k],v)
    gate=plan['layout']['gate'];passes=[]
    for width in plan['layout']['widths']:
        a=primary[f'paragraph_filter_and_assembly_{width}'];b=primary[f'full_page_raw_{width}']
        passes.append(a['complete'] and a['f1']>=gate['micro_f1_min'] and a['f1']>b['f1'] and a['relative_count_error']<=gate['maximum_relative_count_error'])
    check('layout_gate',result['layout']['status'],'PASS_OPERATOR_ASSISTED_LAYOUT_PILOT' if all(passes) else 'FAIL_OPERATOR_ASSISTED_LAYOUT_PILOT')
    mapping=read(bundle/'sources/unicode_dict.json');ds=read(bundle/'ocr/dataset.json');by={x['id']:x for x in ds};paths={}
    check('unique_rows',len(by),61)
    for page in refs['pages']:
        for row in page['lines']:
            key=row['id'];r=by[key];target=' '.join(''.join(mapping[c] for c in word.split(',')) for word in row['boxer_tokens']);p=bundle/'ocr'/r['role']/Path(r['path']).name;paths[key]=p
            check('label:'+key,r['text'],target);check('textfile:'+key,p.with_suffix('.gt.txt').read_text(),target);check('image:'+key,sha(p),r['image_sha256'])
            check('folio_role:'+key,r['folio'] in plan['ocr'][r['role']+'_folios'])
    groups={role:[x for x in ds if x['role']==role] for role in ('train','test')}
    for role,rs in groups.items():check(role+'_rows',len(rs),plan['ocr'][role+'_rows'])
    check('no_physical_leaf_overlap',not ({x['folio'].rstrip('rv') for x in groups['train']}&{x['folio'].rstrip('rv') for x in groups['test']}))
    config=read(bundle/'ocr/training_config.json');check('monitor_training_only',config['train']['training_data'],config['train']['evaluation_data'])
    for key in ('epochs','freq','spec','batch_size','lrate'):check('fixed_'+key,config['train'][key],plan['ocr'][key])
    check('40_epochs_reached','max_epochs=40` reached' in (bundle/'ocr/training.log').read_text())
    o=result['ocr'];rows=o['rows'];check('test_outputs',len(rows),27)
    train=groups['train'];tf=[feature(paths[x['id']]) for x in train];counts=collections.Counter(c for x in train for c in x['text'] if c!=' ');mode=counts.most_common(1)[0][0]
    lengths=sorted(len(x['text']) for x in train);median=int((lengths[16]+lengths[17])/2);totals=collections.Counter();ns=collections.Counter();n=0;nonspace=0
    for row in rows:
        key=row['id'];target=by[key]['text'];check('test_label:'+key,row['reference'],target);check('PUA_unit_length:'+key,row['reference_units_count'],len(target));n+=len(target);nonspace+=len(target.replace(' ',''))
        f,a=feature(paths[key]);scores=[math.fsum((u-v)**2 for u,v in zip(f,g))/len(f)+.05*(a-b)**2 for g,b in tf];nearest=train[min(range(len(train)),key=lambda i:scores[i])]
        check('nearest_id:'+key,row['nearest_train_id'],nearest['id']);check('nearest_text:'+key,row['predictions']['nearest_training_line_by_fixed_image_features'],nearest['text'])
        check('mode:'+key,row['predictions']['repeat_training_mode_to_training_median_length'],mode*median);check('empty:'+key,row['predictions']['empty_output'],'')
        for name,text in row['predictions'].items():
            d=edit(target,text);e=edit(target.replace(' ',''),text.replace(' ',''));totals[name]+=d;ns[name]+=e
            check('distance:'+key+':'+name,row['errors'][name],d);check('nonspace_distance:'+key+':'+name,row['nonspace_errors'][name],e)
    for name,d in totals.items():
        for key,value in {'errors':d,'reference_units':n,'gcr':d/n,'nonspace_gcr':ns[name]/nonspace}.items():check('score:'+name+':'+key,o['metrics'][name][key],value)
    passed=totals['kraken']/n<=plan['ocr']['gate']['gcr_max'] and totals['kraken']<min(v for k,v in totals.items() if k not in ('kraken','empty_output'))
    check('ocr_gate',o['status'],'PASS_CONDITIONAL_OCR_PILOT' if passed else 'FAIL_CONDITIONAL_OCR_PILOT')
    for key,path in [('model_sha256','ocr/final_epoch.mlmodel'),('training_log_sha256','ocr/training.log')]:check(key,o[key],sha(bundle/path))
    check('checkpoint_sha256',o['checkpoint_sha256'],sha(next((bundle/'ocr/checkpoints').glob('checkpoint_39-*.ckpt'))))
    check('translation',result['translation'],'NOT_RUN');check('language',result['language_identification'],'NOT_RUN')
    return {'audit_date':'2026-10-26','scope':'Independent numerical reimplementation; not new inference or expert annotation review','checks':checked,'mismatches':errors,'status':'PASS' if not errors else 'FAIL','run_id':result['run_id'],'result_sha256':sha(bundle/'stage2_result.json'),'primary':primary,'ocr_metrics':o['metrics']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.bundle,a.repo);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(json.dumps({k:r[k] for k in ('status','checks','mismatches')}));raise SystemExit(r['status']!='PASS')
