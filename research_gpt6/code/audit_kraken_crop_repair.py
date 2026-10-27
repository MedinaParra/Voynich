#!/usr/bin/env python3
"""Audit exported masks and pixels without rerunning the ownership algorithm."""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import uniform_filter

from audit_kraken_stage2 import edit


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(root, repo, previous=None, ocr_results=None):
    checked=0;errors=[]
    def check(name, actual, expected=True):
        nonlocal checked
        checked+=1
        equal=math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-12) if isinstance(actual,(int,float)) and isinstance(expected,(int,float)) else actual==expected
        if not equal:errors.append({'check':name,'actual':actual,'expected':expected})
    records=json.loads((root/'dataset.json').read_text())
    summary=json.loads((root/'preparation.json').read_text())
    old=json.loads((repo/'results/kraken_stage2/ocr/dataset.json').read_text())
    old={r['id']:r for r in old}
    masks={p['folio']:p for p in json.loads((repo/'data/kraken_region_masks.json').read_text())['pages']}
    refs={p['folio']:p for p in json.loads((repo/'data/kraken_line_reference.json').read_text())['pages']}
    pages=[]
    check('record_count',len(records),122)
    for variant in ['original','repaired']:
        rr=[r for r in records if r['variant']==variant]
        check('coverage:'+variant,{r['id'] for r in rr},set(old))
        for row in rr:
            path=root/variant/Path(row['path']).name
            check('png_hash:'+variant+':'+row['id'],sha(path),row['image_sha256'])
            check('label:'+variant+':'+row['id'],row['text'],old[row['id']]['text'])
            check('gt_file:'+variant+':'+row['id'],path.with_suffix('.gt.txt').read_text(),row['text'])
            with Image.open(path) as src:arr=np.asarray(src.convert('RGB'))
            check('pixel_hash:'+variant+':'+row['id'],hashlib.sha256(arr.tobytes()).hexdigest(),row['pixel_sha256'])
            if variant=='original' and previous:
                old_path=previous/'ocr'/old[row['id']]['role']/path.name
                with Image.open(old_path) as src:prior=np.asarray(src.convert('RGB'))
                check('original_exact_pixels:'+row['id'],np.array_equal(arr,prior))
    for folio,page in refs.items():
        source=root/'images'/(folio+'.jpg')
        check('source_hash:'+folio,sha(source),page['image_sha256'])
        with Image.open(source) as src:im=src.convert('RGB')
        original=np.asarray(im);h,w=original.shape[:2]
        mask=Image.new('L',im.size,0);draw=ImageDraw.Draw(mask)
        for region in masks[folio]['regions']:
            for poly in region['polygons']:draw.polygon([(round(x*w),round(y*h)) for x,y in poly],fill=255)
        valid=np.asarray(mask)>0
        old_coverage=np.zeros((h,w),dtype=np.uint16)
        for row in page['lines']:
            b=row['bbox'];x0,y0=int(b[0]*w),int(b[1]*h);x1,y1=math.ceil(b[2]*w),math.ceil(b[3]*h)
            old_coverage[y0:y1,x0:x1]+=1
        domain=valid&(old_coverage>0)
        coverage=np.zeros((h,w),dtype=np.uint16)
        for row in [r for r in records if r['folio']==folio and r['variant']=='repaired']:
            path=root/'repaired'/Path(row['path']).name
            with Image.open(path) as src:crop=np.asarray(src.convert('RGB'))
            keep=np.load(path.with_name(path.stem+'_ownership.npz'))['mask']
            x0,y0,x1,y1=row['source_bbox']
            check('export_dimensions:'+row['id'],list(crop.shape[:2]),[y1-y0,x1-x0])
            check('mask_dimensions:'+row['id'],keep.shape,crop.shape[:2])
            check('preserved_source_pixels:'+row['id'],np.array_equal(crop[keep],original[y0:y1,x0:x1][keep]))
            check('unowned_pixels_white:'+row['id'],bool((crop[~keep]==255).all()))
            check('mask_within_old_domain:'+row['id'],bool(domain[y0:y1,x0:x1][keep].all()))
            coverage[y0:y1,x0:x1]+=keep
        gray=np.asarray(im.convert('L'),dtype=float)/255
        contrast=uniform_filter(gray,size=31,mode='reflect')-gray
        stats={}
        expected=next(p for p in summary['pages'] if p['folio']==folio)
        for delta in [.06,.10,.14]:
            candidate=(contrast>=delta)&domain;key=f'{delta:.2f}'
            stats[key]={'positions_before':int(candidate.sum()),'repeated_before':int((candidate&(old_coverage>1)).sum()),
                        'repeated_after':int((candidate&(coverage>1)).sum()),'lost_candidate_positions':int((candidate&(coverage==0)).sum())}
            for k,v in stats[key].items():check(f'measure:{folio}:{key}:{k}',v,expected['metrics'][key][k])
            check('exclusive:'+folio+':'+key,stats[key]['repeated_after'],0)
            check('conserved:'+folio+':'+key,stats[key]['lost_candidate_positions'],0)
        pages.append({'folio':folio,'metrics':stats})
    metrics=[]
    for result_path in ocr_results or []:
        r=json.loads(result_path.read_text());model=result_path.parent/'final_epoch.mlmodel'
        check('fixed_epoch:'+r['variant'],r['final_epoch_zero_based'],r['epochs']-1)
        check('model_hash:'+r['variant'],sha(model),r['model_sha256'])
        denominator=sum(len(row['reference']) for row in r['rows'])
        check('recognition_rows:'+r['variant'],len(r['rows']),27)
        scores={}
        for method in r['metrics']:
            total=0
            for row in r['rows']:
                value=edit(row['reference'],row['predictions'][method]);total+=value
                check('edit:'+r['variant']+':'+row['id']+':'+method,value,row['errors'][method])
            check('errors:'+r['variant']+':'+method,total,r['metrics'][method]['errors'])
            check('denominator:'+r['variant']+':'+method,denominator,r['metrics'][method]['reference_units'])
            check('gcr:'+r['variant']+':'+method,total/denominator,r['metrics'][method]['gcr'])
            scores[method]={'errors':total,'reference_units':denominator,'gcr':total/denominator}
        metrics.append({'variant':r['variant'],'metrics':scores})
    result={'status':'PASS_INTERNAL_EXPORTED_DATA_AUDIT' if not errors else 'FAIL_INTERNAL_EXPORTED_DATA_AUDIT',
            'checks':checked,'mismatches':errors,'pages':pages,'recognition_metrics_recomputed':metrics,
            'scope':'Audits actual exported PNGs and ownership masks; no semantic or expert glyph validation.',
            'independent_expert_review':'NOT_REVIEWED'}
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--previous-bundle',type=Path);p.add_argument('--ocr-result',type=Path,action='append',default=[])
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=audit(a.data,a.repo,a.previous_bundle,a.ocr_result);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':r['checks'],'mismatches':r['mismatches']}))
    raise SystemExit(bool(r['mismatches']))
