#!/usr/bin/env python3
"""Diagnostic schema/geometry audit of the original Voynichese XML release.

Does not validate readings, image registration, or glyph ownership. Does not
execute downloaded code. The archive inspected on 2026-10-26 is hash-pinned.
"""
import argparse,collections,hashlib,json,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

EXPECTED='402d99ca8191ae53a4f25912ee0af0a7e6b6d9a3714b2beaf86404a27d5b7ad5'
def audit(path,out):
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest!=EXPECTED:raise ValueError('The source archive changed; do not silently substitute a new dataset.')
    pages=[];totals=collections.Counter();bad=[]
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist())>100_000_000:raise ValueError('Unexpected expanded archive size')
        for name in sorted(z.namelist()):
            if not name.endswith('.xml'):continue
            raw=z.read(name);root=ET.fromstring(raw);folio=root.attrib['name'];w=int(root.attrib['width']);h=int(root.attrib['height'])
            words=list(root.findall('word'));flags=collections.Counter();indices=[]
            for word in words:
                a=word.attrib;idx=int(a['index']);x,y,bw,bh=[int(a[k]) for k in ('x','y','width','height')];indices.append(idx);reason=[]
                if bw<=0:reason.append('nonpositive_width')
                if bh<=0:reason.append('nonpositive_height')
                if x<0 or y<0 or x+bw>w or y+bh>h:reason.append('outside_declared_frame')
                for flag in reason:flags[flag]+=1
                if reason:bad.append({'folio':folio,'index':idx,'bbox':[x,y,bw,bh],'reasons':reason})
            flags['duplicate_indices']=len(indices)-len(set(indices));flags['declared_count_difference']=abs(len(words)-int(root.attrib['wordCount']))
            page={'folio':folio,'frame':[w,h],'words':len(words),'flags':dict(flags),'apache_header_present':b'Apache License, Version 2.0' in raw}
            pages.append(page);totals['words']+=len(words)
            for k,v in flags.items():totals[k]+=v
    flagged=sum(any(v for v in p['flags'].values()) for p in pages)
    report={'date':'2026-10-26','type':'Exploratory source quality audit, prompted by inspecting a sample; not preregistered hypothesis testing',
      'source_url':'https://www.voynichese.com/1/data/folio/voynichese_data.zip','archive_sha256':digest,'archive_bytes':path.stat().st_size,
      'xml_folios':len(pages),'flagged_folios':flagged,'totals':dict(totals),'pages':pages,'flagged_words':bad,
      'license_evidence':'Apache 2.0 inline headers in original XML; project DataSets.md documents the same release terms.',
      'pages_with_apache_header':sum(p['apache_header_present'] for p in pages),
      'limitations':['A positive-area in-frame box is not proof of correct transcription or alignment.','These are older viewport-based image coordinates, not registered to the current Yale scans.','No automatic mapping to Boxer units has been established.'],
      'registration_to_current_yale':'NOT_RUN','recognition':'NOT_RUN','translation':'NOT_RUN'}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('xml_folios','flagged_folios','totals','pages_with_apache_header')}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();audit(a.archive,a.out)
