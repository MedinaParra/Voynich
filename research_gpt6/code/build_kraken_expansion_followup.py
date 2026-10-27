#!/usr/bin/env python3
"""Explicit exploratory subset after primary geometry failure; no new fits."""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
from PIL import Image
from kraken_eva_word_training import sha,save,crop_word,sample_name


def build(plan_path,repo,primary,out):
    plan=json.loads(plan_path.read_text());original=json.loads((primary/'geometry_result.json').read_text());inputs=json.loads((repo/'data/kraken_expansion_inputs.json').read_text());out.mkdir(parents=True,exist_ok=True)
    expected=plan['additional_training_folios']+plan['reserved_folios'];by_page={p['folio']:p for p in inputs['pages']};summaries={p['folio']:p for p in original['pages']}
    if original['status']!='FAIL_PRESELECTED_PAGE_GEOMETRY_NO_EXPANSION_TRAINING' or summaries['f5r']['accepted']:raise ValueError('Primary failure not preserved as specified')
    if expected!=['f5v','f6r','f6v','f7r','f7v']:raise ValueError('Exploratory folio selection changed')
    cases=json.loads((primary/'geometry_cases.json').read_text())
    for f in expected:
        cs=[c for c in cases if c['folio']==f]
        if not summaries[f]['accepted'] or not summaries[f]['positive_grid'] or len(cs)!=5 or not all(c['conditions']['spatial_median']['accepted'] for c in cs):raise ValueError('A selected page did not pass original gates')
    for name in ['geometry_cases.json','geometry_correspondences.json','geometry_models.json','geometry_grids.json','new_word_polygons.json']:
        shutil.copy2(primary/name,out/name)
    shutil.copy2(primary/'geometry_result.json',out/'primary_geometry_result.json')
    images={};rows=[]
    def emit(r):
        source=repo/r['source_image_path']
        if source not in images:
            if sha(source)!=r['source_image_sha256']:raise ValueError('Source photo changed')
            with Image.open(source) as im:images[source]=im.convert('RGB')
        crop,mask,bounds=crop_word(images[source],r['polygon'],plan['padding_pixels']);path=out/'crops'/(r['id']+'.png');path.parent.mkdir(exist_ok=True);mp=path.with_name(r['id']+'_mask.png');crop.save(path);mask.save(mp)
        if 'image_sha256' in r and (r['image_sha256']!=sha(path) or r['mask_sha256']!=sha(mp) or r['bounds']!=bounds):raise ValueError('Original crop changed '+r['id'])
        r.update(path=str(path.relative_to(out)),mask_path=str(mp.relative_to(out)),bounds=bounds,crop_size=list(crop.size),image_sha256=sha(path),mask_sha256=sha(mp),training_text=r['reference'])
        path.with_suffix('.gt.txt').write_text(r['reference']);rows.append(r)
    for old in json.loads((repo/plan['previous_dataset_path']).read_text()):
        r=dict(old);r['role']='original_train' if r['role']=='train' else 'historical_development';emit(r)
    for w in json.loads((primary/'new_word_polygons.json').read_text()):
        if w['folio'] not in expected or w['flags'] or w['yale_polygon'] is None:continue
        p=by_page[w['folio']];emit({'id':sample_name(w['folio'],w['index']),'folio':w['folio'],'index':w['index'],'reference':w['eva'],'role':p['role'],'polygon':w['yale_polygon'],'source_image_path':p['yale_path'],'source_image_sha256':p['yale_sha256'],'reference_status':'CANDIDATE_EVA_NO_NEW_EXPERT_REVIEW'})
    counts=Counter(r['role'] for r in rows)
    if counts!=Counter({'original_train':197,'historical_development':147,'additional_train':245,'reserved':135}):raise ValueError('Follow-up candidate counts changed')
    save(out/'dataset.json',rows)
    result={'status':'FOLLOWUP_PREPARED_EXPLORATORY_AFTER_PRIMARY_FAILURE','primary_geometry_status':original['status'],'primary_geometry_result_sha256':sha(primary/'geometry_result.json'),'primary_run_id':original['run_id'],'plan_sha256':sha(plan_path),'pages':[summaries[f] for f in expected],'excluded_folio':'f5r','new_geometric_fits':0,'candidate_rows_by_role':dict(counts),'characters_by_role':{role:sum(len(r['reference']) for r in rows if r['role']==role) for role in counts},'dataset_sha256':sha(out/'dataset.json'),'expert_review':'NOT_REVIEWED','translation':'NOT_RUN'}
    save(out/'geometry_result.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--primary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.plan,a.repo,a.primary,a.out)))
