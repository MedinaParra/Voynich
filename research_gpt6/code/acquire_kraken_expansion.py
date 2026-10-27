#!/usr/bin/env python3
"""Freeze six preselected Voynichese data pages and Yale photographs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')


def acquire(a):
    plan=json.loads(a.plan.read_text());root=a.repo/'results/kraken_expansion/inputs';root.mkdir(parents=True,exist_ok=True)
    if sha(a.archive)!='402d99ca8191ae53a4f25912ee0af0a7e6b6d9a3714b2beaf86404a27d5b7ad5':raise ValueError('Changed archived XML source')
    receipts=json.loads(a.receipts.read_text());by={r['folio']:r for r in receipts['images']};pages=[];downloads=[]
    z=zipfile.ZipFile(a.archive)
    for folio in plan['additional_training_folios']+plan['reserved_folios']:
        record={'folio':folio,'role':'additional_train' if folio in plan['additional_training_folios'] else 'reserved'}
        for kind,suffix,url in [('json','json',f'https://www.voynichese.com/1/data/folio/script/{folio}.js'),('preview','jpg',f'https://www.voynichese.com/1/data/folio/image/glance/color/large/{folio}.jpg')]:
            dest=root/(folio+'_'+kind+'.'+suffix)
            request=urllib.request.Request(url,headers={'User-Agent':'Voynich-research-reproducible-pilot/1.0'})
            with urllib.request.urlopen(request,timeout=60) as r:
                b=r.read();content_type=r.headers.get('Content-Type');status=r.status
            dest.write_bytes(b);record[kind+'_path']=str(dest.relative_to(a.repo));record[kind+'_sha256']=sha(dest)
            downloads.append({'folio':folio,'kind':kind,'url':url,'bytes':len(b),'sha256':sha(dest),'content_type':content_type,'http_status':status,'retrieved_utc':datetime.now(timezone.utc).isoformat()})
        y=by[folio[1:]];oid=y['canvas_id'].split('/')[-1];source=a.scans/(oid+'.jpg')
        if sha(source)!=y['source_sha256']:raise ValueError('Changed Yale raw scan')
        target=root/(folio+'_yale.jpg');shutil.copy2(source,target)
        record.update(yale_path=str(target.relative_to(a.repo)),yale_sha256=sha(target),yale_url=y['source_url'],yale_original_receipt=y)
        xml=root/(folio+'.xml');xml.write_bytes(z.read('data/'+folio+'.xml'));x=ET.fromstring(xml.read_bytes())
        if b'Apache License, Version 2.0' not in xml.read_bytes():raise ValueError('Missing source license header')
        data=json.loads((a.repo/record['json_path']).read_text());tokens,boxes=data
        if len(boxes)!=len(x.findall('word')):raise ValueError('Different source segmentation')
        words=[]
        for index,(box,old) in enumerate(zip(boxes,x.findall('word'))):
            eva=tokens[box[0]][0]
            if eva!=(old.text or '') or index!=int(old.attrib['index']):raise ValueError('EVA sequence differs from archived XML: '+folio)
            words.append({'index':index,'eva':eva,'preview_bbox':box[1:],'xml_bbox':[int(old.attrib[k]) for k in ['x','y','width','height']]})
        with Image.open(a.repo/record['preview_path']) as im:record['preview_size']=list(im.size)
        with Image.open(target) as im:record['yale_size']=list(im.size)
        record.update(xml_path=str(xml.relative_to(a.repo)),xml_sha256=sha(xml),words=words,sequence_equal_to_licensed_xml=True)
        pages.append(record)
        print(json.dumps({'folio':folio,'source_words':len(words),'role':record['role'],'sequence_equal':True}),flush=True)
    save(root/'acquisition_receipts.json',downloads)
    save(a.repo/'data/kraken_expansion_inputs.json',{'protocol_commit':a.protocol_commit,'plan_sha256':sha(a.plan),'xml_archive_sha256':sha(a.archive),'xml_archive_url':'https://www.voynichese.com/1/data/folio/voynichese_data.zip','pages':pages,'expert_review':'NOT_REVIEWED'})
    print('EXPANSION_ACQUISITION_COMPLETE',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--archive',type=Path,required=True);p.add_argument('--receipts',type=Path,required=True);p.add_argument('--scans',type=Path,required=True);p.add_argument('--protocol-commit',required=True);acquire(p.parse_args())
