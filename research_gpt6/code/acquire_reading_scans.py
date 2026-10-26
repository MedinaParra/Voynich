#!/usr/bin/env python3
"""Fetch public Yale IIIF scan copies for an explicitly experimental reader."""
import argparse,concurrent.futures,hashlib,io,json,time,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image

def acquire(row,root):
    oid=row['canvas_id'].rsplit('/',1)[-1]
    if not oid.isdigit():raise ValueError('Unexpected canvas id')
    record=root/'receipts'/f'{oid}.json';raw_path=root/'raw'/f'{oid}.jpg';asset=root/'assets'/f'{oid}.jpg'
    if record.exists() and raw_path.exists() and asset.exists():
        old=json.loads(record.read_text())
        if hashlib.sha256(raw_path.read_bytes()).hexdigest()==old['source_sha256'] and hashlib.sha256(asset.read_bytes()).hexdigest()==old['reader_asset_sha256']:return old
    url=row['image_service_url']+'/full/!1600,2000/0/default.jpg';raw=None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url,timeout=25) as response:
                data=response.read(30_000_001);content_type=response.headers.get('Content-Type');status=response.status
            if len(data)>30_000_000:raise ValueError('Unexpected scan size')
            with Image.open(io.BytesIO(data)) as im:im.load();rgb=im.convert('RGB')
            if rgb.width/rgb.height>1.2 and '!1600,' in url:
                url=row['image_service_url']+'/full/!5000,2000/0/default.jpg'
                continue
            raw=data;break
        except urllib.error.HTTPError as e:
            if e.code not in (429,500,502,503,504):raise
            if attempt==2:raise
            time.sleep(min(20,max(2,int(e.headers.get('Retry-After','3')))))
        except (OSError,TimeoutError):
            if attempt==2:raise
            time.sleep(2)
    if raw is None:raise RuntimeError('No complete scan response')
    raw_path.parent.mkdir(parents=True,exist_ok=True);asset.parent.mkdir(parents=True,exist_ok=True);record.parent.mkdir(parents=True,exist_ok=True)
    raw_path.write_bytes(raw);rgb.save(asset,format='JPEG',quality=80,optimize=True,subsampling=2)
    result={'folio':row['folio'],'canvas_id':row['canvas_id'],'source_position':row['source_position'],'source_url':url,
            'http_status':status,'content_type':content_type,'downloaded_utc':datetime.now(timezone.utc).isoformat(),
            'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),'image_size':list(rgb.size),
            'reader_asset':str(asset.resolve()),'reader_asset_sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
            'reader_bytes':asset.stat().st_size,'reader_transform':'JPEG quality 80, no cropping, flipping or added image content'}
    record.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');return result
def run(manifest,root):
    rows=json.loads(manifest.read_text())['images'];results=[];failures=[];tick=time.perf_counter();root.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        jobs={pool.submit(acquire,row,root):row for row in rows}
        for job in concurrent.futures.as_completed(jobs):
            row=jobs[job]
            try:results.append(job.result())
            except Exception as e:failures.append({'folio':row['folio'],'canvas_id':row['canvas_id'],'error':str(e)});print('SCAN_ERROR='+json.dumps(failures[-1]),flush=True)
            done=len(results)+len(failures)
            if done%15==0:print('SCAN_PROGRESS='+json.dumps({'complete':len(results),'failed':len(failures),'total':len(rows),'seconds':round(time.perf_counter()-tick,1)}),flush=True)
    results.sort(key=lambda r:r['source_position'])
    report={'source_manifest':str(manifest.resolve()),'count':len(results),'expected':len(rows),'failures':failures,'seconds':time.perf_counter()-tick,'source_bytes':sum(r['source_bytes'] for r in results),'reader_bytes':sum(r['reader_bytes'] for r in results),'images':results}
    (root/'image_receipts.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print('SCANS_COMPLETE='+json.dumps({k:v for k,v in report.items() if k!='images'}),flush=True)
    if failures or len(results)!=len(rows):raise RuntimeError('Incomplete scan acquisition; do not label a PDF complete')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.manifest,a.out)
