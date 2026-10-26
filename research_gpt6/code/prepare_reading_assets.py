#!/usr/bin/env python3
"""Prepare consultation-resolution JPEGs while retaining raw download hashes."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image

def run(root):
    summary=json.loads((root/'image_receipts.json').read_text());images=[]
    for old in summary['images']:
        oid=old['canvas_id'].rsplit('/',1)[-1];raw=root/'raw'/f'{oid}.jpg';asset=root/'assets'/f'{oid}.jpg'
        if hashlib.sha256(raw.read_bytes()).hexdigest()!=old['source_sha256']:raise ValueError('Changed raw scan')
        with Image.open(raw) as im:rgb=im.convert('RGB');native=list(rgb.size)
        if rgb.width/rgb.height<=1.2:rgb.thumbnail((1600,1600),Image.Resampling.LANCZOS)
        rgb.save(asset,format='JPEG',quality=60,optimize=True,subsampling=2)
        updated={**old,'source_image_size':native,'image_size':list(rgb.size),'reader_asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'reader_bytes':asset.stat().st_size,'reader_transform':'Consultation copy: ordinary/tall images bounded to 1600x1600; wide scans retain downloaded size; JPEG quality 60. No cropping or flipping.'}
        (root/'receipts'/f'{oid}.json').write_text(json.dumps(updated,sort_keys=True,indent=2)+'\n');images.append(updated)
    summary['images']=images;summary['reader_bytes']=sum(i['reader_bytes'] for i in images);summary['asset_preparation']='JPEG consultation copies; raw downloads retained and hash verified'
    (root/'image_receipts.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'available_images':len(images),'missing':summary['failures'],'reader_bytes':summary['reader_bytes']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scans',type=Path,required=True);a=p.parse_args();run(a.scans)
