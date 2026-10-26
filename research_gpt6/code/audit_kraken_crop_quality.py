#!/usr/bin/env python3
"""Check duplication against actual PNGs, using coordinate counters.

The main measurement rasterizes boxes; this audit instead reads each training
PNG and counts only unchanged source pixels visible in that actual crop.
"""
import argparse,collections,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter

def run(bundle,result_path,out):
    r=json.loads(result_path.read_text());ds=json.loads((bundle/'ocr/dataset.json').read_text());n=0;errors=[]
    def check(name,a,b):
        nonlocal n
        n+=1
        if a!=b:errors.append({'check':name,'actual':a,'expected':b})
    for page in r['pages']:
        folio=page['folio']
        with Image.open(bundle/'images'/f'{folio}.jpg') as im:
            rgb=np.asarray(im.convert('RGB'));gray=np.asarray(im.convert('L'),dtype=float)/255;w,h=im.size
        contrast=uniform_filter(gray,size=31,mode='reflect')-gray;rows=[x for x in ds if x['folio']==folio]
        visible={}
        for row in rows:
            path=bundle/'ocr'/row['role']/Path(row['path']).name
            check('crop_sha:'+row['id'],hashlib.sha256(path.read_bytes()).hexdigest(),row['image_sha256'])
            with Image.open(path) as crop:arr=np.asarray(crop.convert('RGB'));cw,ch=crop.size
            x0=math.floor(row['source_bbox'][0]*w);y0=math.floor(row['source_bbox'][1]*h)
            source=rgb[y0:y0+ch,x0:x0+cw]
            if source.shape!=arr.shape:raise ValueError('Invalid actual crop extent')
            visible[row['id']]=(x0,y0,cw,ch,np.all(source==arr,axis=2))
        for key,expected in page['thresholds'].items():
            counter=collections.Counter();row_positions={}
            for row in rows:
                x0,y0,cw,ch,same=visible[row['id']]
                yy,xx=np.nonzero((contrast[y0:y0+ch,x0:x0+cw]>=float(key))&same)
                positions=((yy+y0)*w+xx+x0).tolist();counter.update(positions);row_positions[row['id']]=positions
            unique=len(counter);repeated=sum(v>1 for v in counter.values());exposures=sum(counter.values())
            for name,value in [('unique_dark_positions',unique),('repeated_dark_positions',repeated),('total_dark_exposures',exposures),('redundant_exposures',exposures-unique)]:check(f'{folio}/{key}/{name}',value,expected[name])
            expected_rows={x['id']:x for x in expected['rows']}
            for name,positions in row_positions.items():
                check(f'{folio}/{key}/{name}/dark',len(positions),expected_rows[name]['dark_positions'])
                check(f'{folio}/{key}/{name}/repeated',sum(counter[p]>1 for p in positions),expected_rows[name]['repeated_dark_positions'])
    report={'date':'2026-10-26','method':'Read preserved training/test PNGs and count repeated source coordinates, independently of box rasterization','checks':n,'mismatches':errors,'status':'PASS' if not errors else 'FAIL','result_sha256':hashlib.sha256(result_path.read_bytes()).hexdigest(),'limitation':'Checks numerical correspondence with actual exported crops, not expert ownership of ink or correctness of labels.'}
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report));return not errors
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--result',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();raise SystemExit(not run(a.bundle,a.result,a.out))
