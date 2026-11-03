#!/usr/bin/env python3
"""Prepare original-pixel, source-label-blinded review sheets; no training data edits."""
import argparse,hashlib,json,random
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont


def build(repo,out,blind):
    queue=repo/'results/transcription_boundaries/review_queue.json';records=json.loads(queue.read_text())['records'];assert len(records)==24
    order=list(range(24));random.Random(20261103).shuffle(order)
    receipts=json.loads((out/'sources/acquisition_receipts.json').read_text());sources={r['folio']:r for r in receipts};assert all(r['status']=='ACQUIRED_NATIVE' for r in receipts)
    blind.mkdir(parents=True,exist_ok=True);(out/'blind_sheets').mkdir(exist_ok=True)
    font=ImageFont.truetype(str(out/'sources/DejaVuSans.ttf'),16)
    cards=[];mapping=[]
    def resized(im,size):
        scale=min(size[0]/im.width,size[1]/im.height)
        return im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.NEAREST)
    for i,idx in enumerate(order):
        r=records[idx];alias=f'B{i+1:02d}';source=out/'sources'/(r['folio']+'_native.jpg');b=source.read_bytes();assert hashlib.sha256(b).hexdigest()==sources[r['folio']]['sha256']
        with Image.open(source) as im:photo=im.convert('RGB')
        with Image.open(repo/r['source_image_path']) as im:oldsize=im.size
        sx,sy=photo.width/oldsize[0],photo.height/oldsize[1]
        bounds=[round(v*(sx if k%2==0 else sy)) for k,v in enumerate(r['bounds'])];x0,y0,x1,y1=bounds
        region=[max(0,x0-120),max(0,y0-120),min(photo.width,x1+120),min(photo.height,y1+120)]
        crop=photo.crop(bounds);context=photo.crop(region);d=ImageDraw.Draw(context)
        d.rectangle([x0-region[0],y0-region[1],x1-region[0]-1,y1-region[1]-1],outline='red',width=2)
        card=Image.new('RGB',(800,510),'#fafafa');cd=ImageDraw.Draw(card)
        cd.text((12,8),alias+' | original rectangle, no mask',font=font,fill='black');card.paste(resized(crop,(776,165)),(12,35))
        cd.text((12,207),'Original photo context | red = target rectangle',font=font,fill='black');card.paste(resized(context,(776,248)),(12,234))
        cd.text((12,489),'No transcript or OCR labels shown; enlarged nearest-neighbor',font=font,fill='black')
        cards.append(card);mapping.append({'alias':alias,'id':r['id'],'folio':r['folio'],'queue_index':idx,'native_bounds':bounds,'native_context_bounds':region,'frozen_bounds':r['bounds'],'frozen_size':list(oldsize),'native_size':list(photo.size),'scale_xy':[sx,sy],'source_sha256':hashlib.sha256(b).hexdigest()})
    sheets=[]
    for i in range(6):
        sheet=Image.new('RGB',(1600,1020),'white')
        for j,c in enumerate(cards[i*4:i*4+4]):sheet.paste(c,((j%2)*800,(j//2)*510))
        import io
        buf=io.BytesIO();sheet.save(buf,format='JPEG',quality=92);data=buf.getvalue();name=f'sheet_{i+1}.jpg'
        (blind/name).write_bytes(data);(out/'blind_sheets'/name).write_bytes(data)
        sheets.append({'file':name,'sha256':hashlib.sha256(data).hexdigest(),'aliases':[m['alias'] for m in mapping[i*4:i*4+4]]})
    record={'seed':20261103,'queue_sha256':hashlib.sha256(queue.read_bytes()).hexdigest(),'coordinate_transfer':'same Yale canvas; proportional raster coordinates rounded; descriptive not new SIFT calibration','mapping':mapping,'sheets':sheets}
    (out/'presentation_mapping.json').write_text(json.dumps(record,indent=2)+'\n')
    instructions={'cases':[r['alias'] for r in mapping],'sheets':sheets,'task':'Describe visible morphology, body isolation and lateral spacing only. No transcription candidates, folio, OCR outputs or previous observations supplied. Do not infer language/meaning or stroke order. Human expert review remains absent.'}
    (blind/'packet.json').write_text(json.dumps(instructions,indent=2)+'\n')
    print({'cases':24,'blind_sheets':6,'native_sources':4})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--blind',type=Path,required=True);a=p.parse_args();build(a.repo,a.out,a.blind)
