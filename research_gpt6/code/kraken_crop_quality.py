#!/usr/bin/env python3
"""Measure literal source-pixel duplication across provisional row crops.

Dark candidates are a contrast proxy, not a palaeographic ink classifier.
No OCR, language identification, parameter fitting or new training.
"""
import argparse,hashlib,json,math,unittest
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import uniform_filter

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rect(box,size):
    w,h=size
    return (max(0,math.floor(box[0]*w)),max(0,math.floor(box[1]*h)),min(w,math.ceil(box[2]*w)),min(h,math.ceil(box[3]*h)))
def paragraph_mask(size,regions):
    mask=Image.new('L',size,0);draw=ImageDraw.Draw(mask);w,h=size
    for region in regions:
        for polygon in region['polygons']:draw.polygon([(round(x*w),round(y*h)) for x,y in polygon],fill=255)
    return np.asarray(mask)>0
def measure(im,boxes,valid,deltas=(.06,.10,.14)):
    gray=np.asarray(im.convert('L'),dtype=np.float64)/255
    contrast=uniform_filter(gray,size=31,mode='reflect')-gray
    coverage=np.zeros(gray.shape,dtype=np.uint16)
    bounds=[rect(box,im.size) for box in boxes]
    for x0,y0,x1,y1 in bounds:coverage[y0:y1,x0:x1]+=1
    coverage[~valid]=0;stats={};main_duplicate=None
    for delta in deltas:
        candidate=(contrast>=delta)&(coverage>0);duplicate=candidate&(coverage>1)
        unique=int(candidate.sum());repeated=int(duplicate.sum());exposures=int(coverage[candidate].sum())
        rows=[]
        for i,(x0,y0,x1,y1) in enumerate(bounds):
            n=int(candidate[y0:y1,x0:x1].sum());d=int(duplicate[y0:y1,x0:x1].sum())
            rows.append({'index':i,'dark_positions':n,'repeated_dark_positions':d,'fraction':d/n if n else None})
        stats[f'{delta:.2f}']={'unique_dark_positions':unique,'repeated_dark_positions':repeated,
             'repeated_fraction':repeated/unique if unique else None,'total_dark_exposures':exposures,
             'redundant_exposures':exposures-unique,'redundant_exposure_fraction':(exposures-unique)/exposures if exposures else None,
             'rows_with_repeated_positions':sum(r['repeated_dark_positions']>0 for r in rows),'rows':rows}
        if math.isclose(delta,.10):main_duplicate=duplicate
    return stats,main_duplicate

class Controls(unittest.TestCase):
    def setUp(self):
        self.im=Image.new('L',(200,100),255);d=ImageDraw.Draw(self.im)
        d.rectangle((20,20,180,25),fill=0);d.rectangle((20,60,180,65),fill=0)
        self.valid=np.ones((100,200),dtype=bool);self.boxes=[[0,.15,1,.35],[0,.55,1,.75]]
    def test_blank(self):
        s,_=measure(Image.new('L',(200,100),255),self.boxes,self.valid)
        self.assertTrue(all(v['unique_dark_positions']==0 and v['repeated_fraction'] is None for v in s.values()))
    def test_separate_rows(self):
        s,_=measure(self.im,self.boxes,self.valid)
        self.assertTrue(all(v['unique_dark_positions']>0 and v['repeated_fraction']==0 for v in s.values()))
    def test_box_crossing_another_row(self):
        s,_=measure(self.im,self.boxes+[[0,.15,1,.75]],self.valid)
        self.assertTrue(all(v['repeated_fraction']>0 for v in s.values()))
    def test_duplicated_crop(self):
        s,_=measure(self.im,[self.boxes[0]]*2,self.valid)
        self.assertTrue(all(v['repeated_fraction']==1 for v in s.values()))
    def test_no_boxes(self):
        s,_=measure(self.im,[],self.valid)
        self.assertTrue(all(v['unique_dark_positions']==0 and v['repeated_fraction'] is None for v in s.values()))
    def test_mask_removes_outside(self):
        valid=self.valid.copy();valid[:50]=False
        s,_=measure(self.im,[self.boxes[0]]*2,valid)
        self.assertTrue(all(v['unique_dark_positions']==0 for v in s.values()))

def run(bundle,repo,out,prereg_commit):
    controls=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
    if not controls.wasSuccessful():raise RuntimeError('Synthetic controls failed')
    refs=json.loads((repo/'data/kraken_line_reference.json').read_text());masks=json.loads((repo/'data/kraken_region_masks.json').read_text())
    manifest=json.loads((bundle/'sha256_manifest.json').read_text())
    by={p['folio']:p for p in masks['pages']};pages=[];out.mkdir(parents=True,exist_ok=True)
    for page in refs['pages']:
        folio=page['folio'];path=bundle/'images'/f'{folio}.jpg'
        if sha(path)!=manifest[f'images/{folio}.jpg']:raise ValueError('Changed image '+folio)
        with Image.open(path) as src:im=src.convert('RGB')
        if sha(path)!=by[folio]['image_sha256']:raise ValueError('Image differs from frozen annotations')
        s,dup=measure(im,[r['bbox'] for r in page['lines']],paragraph_mask(im.size,by[folio]['regions']))
        for value in s.values():
            for row in value['rows']:row['id']=page['lines'][row.pop('index')]['id']
        pages.append({'folio':folio,'image_sha256':sha(path),'image_size':list(im.size),'rows':len(page['lines']),'thresholds':s})
        arr=np.asarray(im).copy();arr[dup]=[255,0,30];preview=Image.fromarray(arr);d=ImageDraw.Draw(preview)
        for row in page['lines']:d.rectangle(rect(row['bbox'],im.size),outline=(0,160,100),width=2)
        preview.thumbnail((900,1400));preview.save(out/f'{folio}_repeated_positions.jpg',quality=90)
    pooled={}
    for delta in ('.06','.10','.14'):
        key=f'{float(delta):.2f}';ss=[p['thresholds'][key] for p in pages]
        u=sum(x['unique_dark_positions'] for x in ss);r=sum(x['repeated_dark_positions'] for x in ss);e=sum(x['total_dark_exposures'] for x in ss)
        pooled[key]={'unique_dark_positions':u,'repeated_dark_positions':r,'repeated_fraction':r/u if u else None,
                     'total_dark_exposures':e,'redundant_exposures':e-u,'redundant_exposure_fraction':(e-u)/e if e else None,
                     'rows_with_repeated_positions':sum(x['rows_with_repeated_positions'] for x in ss)}
    result={'date':'2026-10-26','preregistration_commit':prereg_commit,'protocol_sha256':sha(repo/'51_crop_quality_protocol.md'),
      'code_sha256':sha(Path(__file__)),'source_run_id':38707533236,'controls_passed':controls.testsRun,'candidate_estimator':{'gray':'Pillow L / 255','local_mean_window':31,'boundary_mode':'reflect','main_delta':.10,'sensitivity_deltas':[.06,.14]},
      'status':'REVIEW_REQUIRED' if pooled['0.10']['repeated_dark_positions'] else 'NO_DUPLICATE_POSITIONS_DETECTED_NOT_VALIDATED',
      'pages':pages,'pooled':pooled,'limitations':['Dark candidates can include painting or noise.','Ascenders can legitimately overlap adjacent row rectangles.','This measures repeated source positions, not which line owns a glyph.','Previously explored leaves only; diagnostic, not new held-out evaluation.','No causal explanation of OCR failure is established.'],
      'recognition':'NOT_RUN','translation':'NOT_RUN','language_identification':'NOT_RUN'}
    (out/'crop_quality_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'controls_passed':controls.testsRun,'pooled':pooled}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path);p.add_argument('--repo',type=Path);p.add_argument('--out',type=Path);p.add_argument('--prereg-commit');p.add_argument('--controls-only',action='store_true');a=p.parse_args()
    if a.controls_only:
        test=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls));raise SystemExit(not test.wasSuccessful())
    if not all((a.bundle,a.repo,a.out,a.prereg_commit)):p.error('bundle, repo, out and prereg-commit are required')
    run(a.bundle,a.repo,a.out,a.prereg_commit)
