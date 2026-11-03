#!/usr/bin/env python3
"""Verify provenance and record consistency, not correctness of paleography."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image

def verify(repo,bundle):
    checks=[]
    def check(name,value):
        checks.append(name)
        if not value:raise ValueError(name)
    read=lambda p:json.loads(p.read_text())
    m=read(bundle/'presentation_mapping.json');queue=repo/'results/transcription_boundaries/review_queue.json'
    check('prior_queue_unchanged',hashlib.sha256(queue.read_bytes()).hexdigest()==m['queue_sha256'])
    ids={r['id'] for r in read(queue)['records']};aliases={r['alias'] for r in m['mapping']}
    check('exact_original24_ids',len(ids)==24 and {r['id'] for r in m['mapping']}==ids and len(aliases)==24)
    for r in read(bundle/'sources/acquisition_receipts.json'):
        p=bundle/'sources'/(r['folio']+'_native.jpg');info=read(bundle/'sources'/(r['folio']+'_info.json'))
        check(r['folio']+'/original_native_hash',hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'])
        with Image.open(p) as im:check(r['folio']+'/declared_native_dimensions',list(im.size)==[r['width'],r['height']]==[info['width'],info['height']])
    for r in m['mapping']:
        x0,y0,x1,y1=r['native_bounds'];w,h=r['native_size']
        check(r['alias']+'/bounds',0<=x0<x1<=w and 0<=y0<y1<=h)
        check(r['alias']+'/coordinate_transfer',[round(v*r['scale_xy'][i%2]) for i,v in enumerate(r['frozen_bounds'])]==r['native_bounds'])
    for s in m['sheets']:check(s['file']+'/presentation_hash',hashlib.sha256((bundle/'blind_sheets'/s['file']).read_bytes()).hexdigest()==s['sha256'])
    for name in ['review_a.json','review_b.json']:
        a=read(bundle/'reviews'/name)['records'];check(name+'/exact24_aliases',len(a)==24 and {r['alias'] for r in a}==aliases)
        for r in a:
            check(name+'/'+r['alias']+'/schema',r['body_isolation'] in ['clean','mixed_rows','uncertain'] and r['geometry_action'] in ['retain_candidate','review_crop','unresolved'])
    result=read(bundle/'assessment.json');summary=result['summary'];rows=result['records']
    check('assessment_exact24',len(rows)==24 and {r['id'] for r in rows}==ids)
    check('no_approved_gold',all(r['label_approval']=='NOT_APPROVED' and r['geometry_approval']=='NOT_APPROVED' and r['expert_review']=='NOT_REVIEWED' for r in rows))
    check('labels_and_geometry_unchanged',summary['labels_changed']==summary['geometry_changed']==0)
    check('agreement_not_accuracy',summary['agreement_is_not_accuracy'] is True)
    check('editorial_preferences_count',sum('proposed_EVA' in r for r in rows)==summary['provisional_EVA_preferences']==3)
    check('geometry_triage_totals',sum(summary['geometry_triage'].values())==24)
    return {'status':'PASS','checks':len(checks),'check_names':checks,'scope':'File hashes, native resolution, coordinate transfer and consistency of AI/editorial records. Does not validate blinding enforcement, glyph readings, ink ownership, crop repair, human expertise, or transcription accuracy.','expert_review':'NOT_REVIEWED','labels_changed':0,'training':'NOT_RUN','translation':'NOT_RUN'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=verify(a.repo,a.bundle);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print({'status':r['status'],'integrity_checks':r['checks']})
