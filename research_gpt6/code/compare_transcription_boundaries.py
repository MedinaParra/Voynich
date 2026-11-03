#!/usr/bin/env python3
"""Source disagreement inventory; no OCR, training, or automatic label repair."""
import argparse
from collections import Counter,defaultdict
import gzip,hashlib,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from kraken_eva_word_training import crop_word


def read(p):
    return json.loads(p.read_bytes() if p.exists() else gzip.decompress(p.with_suffix(p.suffix+'.gz').read_bytes()))
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def digest(b):return hashlib.sha256(b).hexdigest()


def payload(raw):
    """Lossless node list plus explicitly lossy literal diagnostic projection."""
    pattern=r'<[^>]*>|\[[^\]]*\]|\{[^}]*\}|@\d{3};|\?+|[.,]|[a-zA-Z]+|\s+|.'
    nodes=[];chars='';boundaries=[];flags=[]
    for m in re.finditer(pattern,raw):
        s=m.group();node={'raw':s,'start':m.start(),'end':m.end()}
        if s in ['.',',','<->','<~>']:
            node['kind']='boundary';boundaries.append({'offset':len(chars),'kind':s})
        elif s.startswith('<'):node['kind']='metadata'
        elif s.isspace():node['kind']='format_whitespace'
        elif re.fullmatch('[A-Za-z]+',s):node['kind']='literal';chars+=s.lower()
        elif s.startswith('{') and re.fullmatch('[A-Za-z]+',s[1:-1]):node['kind']='ligature';chars+=s[1:-1].lower()
        else:
            node['kind']='alternative' if s.startswith('[') else 'unreadable' if s.startswith('?') else 'extended_or_unsupported'
            flags.append(node['kind']);chars+=s
        nodes.append(node)
    assert ''.join(x['raw'] for x in nodes)==raw
    offsets=[0]+[b['offset'] for b in boundaries]+[len(chars)]
    tokens=[chars[a:b] for a,b in zip(offsets,offsets[1:])]
    return {'raw':raw,'nodes':nodes,'chars':chars,'boundaries':boundaries,'tokens':tokens,'flags':sorted(set(flags))}


def ivtff(path,folios):
    out={};pending=''
    for physical in path.read_text().splitlines():
        if physical.startswith('/'):
            if not pending:raise ValueError('Unexpected continuation')
            pending+=physical[1:]
        else:
            if pending:raise ValueError('Missing continuation')
            pending=physical
        if pending.endswith('/'):
            pending=pending[:-1];continue
        line=pending;pending=''
        m=re.match(r'<(f[^.>]+)\.(\d+),([^>]+)>\s*(.*)$',line)
        if not m or m[1] not in folios:continue
        f,num,kind,raw=m.groups();key=f+'.'+num
        if key in out:raise ValueError('Duplicate locus '+key)
        out[key]={'id':key,'folio':f,'number':int(num),'locus_type':kind,'projection':payload(raw)}
    if pending:raise ValueError('Incomplete continuation')
    return out


def distance_matrix(a,b):
    d=[[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(len(a)+1):d[i][0]=i
    for j in range(len(b)+1):d[0][j]=j
    for i in range(1,len(a)+1):
        for j in range(1,len(b)+1):d[i][j]=min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]!=b[j-1]))
    return d


def align(a,b):
    f=distance_matrix(a,b);r=distance_matrix(a[::-1],b[::-1]);n,m=len(a),len(b);cost=f[n][m]
    vt=[[j for j in range(m+1) if f[i][j]+r[n-i][m-j]==cost] for i in range(n+1)]
    zl=[[i for i in range(n+1) if j in vt[i]] for j in range(m+1)]
    return {'distance':cost,'vt_states':vt,'zl_states':zl}


def boundary_records(a,b,states):
    target={x['offset']:x['kind'] for x in b['boundaries']};out=[]
    for bound in a['boundaries']:
        positions=states[bound['offset']]
        out.append({**bound,'target_offsets':positions,'target_kinds':[target.get(j) for j in positions],
                    'status':'alignment_ambiguous' if len(positions)!=1 else 'absent_in_target' if positions[0] not in target else 'same_marker' if bound['kind']==target[positions[0]] else 'different_marker'})
    return out


def xml_path(repo,f):
    if f in ['f3r','f3v','f4r','f4v']:return repo/'results/voynichese_registration/inputs'/(f+'.xml')
    if f in ['f8r','f8v']:return repo/'results/kraken_shared_region/fresh_data/inputs'/(f+'.xml')
    return repo/'results/kraken_expansion/inputs'/(f+'.xml')


def compare(repo,out,plan_path):
    plan=read(plan_path);folios=plan['folios'];sources=out/'sources'
    for key,name in [('VT','VT0e-n.txt'),('ZL','ZL3b-n.txt')]:
        b=(sources/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==plan['sources'][key]['expected_git_blob']
    v=ivtff(sources/'VT0e-n.txt',folios);z=ivtff(sources/'ZL3b-n.txt',folios);loci=[]
    for key in sorted(set(v)|set(z),key=lambda k:(folios.index(k.split('.')[0]),int(k.split('.')[1]))):
        record={'id':key,'folio':key.split('.')[0]}
        if key not in v or key not in z:
            record.update(status='missing_source',vt=v.get(key),zl=z.get(key));loci.append(record);continue
        a,b=v[key],z[key];x,y=a['projection'],b['projection'];record.update(vt=x,zl=y,vt_locus_type=a['locus_type'],zl_locus_type=b['locus_type'])
        if a['locus_type'][1:2]!=b['locus_type'][1:2]:record['status']='type_mismatch'
        elif x['flags'] or y['flags']:record['status']='excluded_complex'
        else:
            record['status']='compared';al=align(x['chars'],y['chars']);record['alignment']=al
            record['vt_boundaries']=boundary_records(x,y,al['vt_states']);record['zl_boundaries']=boundary_records(y,x,al['zl_states'])
            record['letter_equal']=x['chars']==y['chars'];record['boundary_offsets_equal']=[t['offset'] for t in x['boundaries']]==[t['offset'] for t in y['boundaries']]
        loci.append(record)
    bridges=[];word_lookup={}
    for f in folios:
        xml=xml_path(repo,f);words=list(ET.parse(xml).getroot().findall('word'));vp=[w.text or '' for w in words]
        lines=sorted([r for r in v.values() if r['folio']==f],key=lambda r:r['number']);vt=[t for r in lines for t in r['projection']['tokens']]
        status='exact_token_sequence' if vp==vt else 'unmapped'
        bridge={'folio':f,'status':status,'xml_path':str(xml.relative_to(repo)),'xml_sha256':digest(xml.read_bytes()),'vp_tokens':vp,'vt_tokens':vt}
        bridges.append(bridge)
        if status=='unmapped':continue
        offset=0
        for line in lines:
            p=line['projection'];start=0
            for token,end in zip(p['tokens'],[b['offset'] for b in p['boundaries']]+[len(p['chars'])]):
                w=words[offset];index=int(w.attrib['index']);word_lookup[(f,index)]={'locus':line['id'],'start':start,'end':end,'token':token}
                offset+=1;start=end
    by_locus={r['id']:r for r in loci}
    rows=read(repo/'results/kraken_expansion/followup_prepared/dataset.json')+read(repo/'results/kraken_shared_region/fresh_data/dataset.json')
    assert len(rows)==989
    assert len({r['id'] for r in rows})==989
    by_folio=defaultdict(list)
    for r in rows:by_folio[r['folio']].append(r)
    geometries=[]
    for f,items in by_folio.items():
        with Image.open(repo/items[0]['source_image_path']) as im:photo=im.convert('RGB')
        coverage=np.zeros((photo.height,photo.width),dtype=np.uint16);local={}
        for r in items:
            crop,mask,bounds=crop_word(photo,r['polygon'],4)
            import io
            for image,key in [(crop,'image_sha256'),(mask,'mask_sha256')]:
                buf=io.BytesIO();image.save(buf,format='PNG');assert digest(buf.getvalue())==r[key],r['id']+' frozen pixels changed'
            assert bounds==r['bounds'];m=np.asarray(mask)>0;x0,y0,x1,y1=bounds;coverage[y0:y1,x0:x1]+=m
            local[r['id']]=(crop,mask)
        for r in items:
            crop,mask=local[r['id']];m=np.asarray(mask)>0;x0,y0,x1,y1=r['bounds'];shared=m&(coverage[y0:y1,x0:x1]>1)
            gray=np.asarray(crop.convert('L'));dark=m&(gray<=float(np.median(gray[m]))-40)
            g={'id':r['id'],'folio':f,'role':r['role'],'reference':r['reference'],'bounds':r['bounds'],'source_image_path':r['source_image_path'],'polygon':r['polygon'],'image_sha256':r['image_sha256'],'mask_sha256':r['mask_sha256'],'shared_mask_fraction':float(shared.sum()/m.sum()),'dark_pixels':int(dark.sum()),'shared_dark_pixels':int((dark&shared).sum()),'shared_dark_fraction':float((dark&shared).sum()/dark.sum()) if dark.sum() else 0.0}
            link=word_lookup.get((f,r['index']));g['source_link']=link;g['source_flags']=[]
            if link is None:g['source_flags']=['unmapped_folio']
            else:
                assert link['token']==r['reference']
                locus=by_locus[link['locus']]
                if locus['status']!='compared':g['source_flags']=['locus_not_literal']
                else:
                    al=locus['alignment'];left=al['vt_states'][link['start']];right=al['vt_states'][link['end']]
                    g['zl_endpoint_candidates']={'start':left,'end':right}
                    if len(left)!=1 or len(right)!=1:g['source_flags'].append('alignment_ambiguous')
                    else:
                        lo,hi=left[0],right[0];g['zl_span_chars']=locus['zl']['chars'][lo:hi]
                        if g['zl_span_chars']!=r['reference']:g['source_flags'].append('letter_disagreement')
                        boundaries=locus['zl']['boundaries'];offsets={b['offset'] for b in boundaries}|{0,len(locus['zl']['chars'])}
                        if lo not in offsets or hi not in offsets or any(lo<b['offset']<hi for b in boundaries):g['source_flags'].append('boundary_disagreement')
                        if any(b['kind']==',' and lo<=b['offset']<=hi for b in boundaries):g['source_flags'].append('uncertain_boundary')
            geometries.append(g)
    train=[g for g in geometries if g['role'] in ['original_train','additional_train']];assert len(train)==442
    chosen=[]
    for label,candidates in [('source_disagreement',sorted([g for g in train if g['source_flags']],key=lambda g:g['id'])),('high_shared_dark',sorted(train,key=lambda g:(-g['shared_dark_fraction'],g['id']))),('low_shared_dark',sorted(train,key=lambda g:(g['shared_dark_fraction'],g['id'])))]:
        selected=[g for g in candidates if g['id'] not in {x['id'] for x in chosen}][:8]
        chosen.extend([{**g,'selection_group':label,'assistant_visual_review':'PENDING','independent_expert_review':'NOT_REVIEWED','label_change':'NONE','geometry_change':'NONE'} for g in selected])
    result={'plan_sha256':digest(plan_path.read_bytes()),'loci':loci,'bridges':bridges}
    save(out/'comparison.json',result);save(out/'geometry_words.json',geometries);save(out/'review_queue.json',{'selection':'plan-fixed training-only, no OCR errors consulted','records':chosen,'expert_review':'NOT_REVIEWED','changes_applied':0})
    paired=[r for r in loci if r['status']=='compared'];stats={'status':'DESCRIPTIVE_COMPARISON_COMPLETE_UNREVIEWED_CANDIDATES','loci_total':len(loci),'locus_status_counts':dict(Counter(r['status'] for r in loci)),'literal_loci':len(paired),'same_letters_loci':sum(r['letter_equal'] for r in paired),'same_letters_different_boundary_offsets':sum(r['letter_equal'] and not r['boundary_offsets_equal'] for r in paired),'letter_differing_loci':sum(not r['letter_equal'] for r in paired),'literal_letter_edit_distance_sum':sum(r['alignment']['distance'] for r in paired),'VT_boundary_statuses':dict(Counter(b['status'] for r in paired for b in r['vt_boundaries'])),'ZL_boundary_statuses':dict(Counter(b['status'] for r in paired for b in r['zl_boundaries'])),'bridges':{r['folio']:r['status'] for r in bridges},'geometry_words':len(geometries),'word_source_flag_counts':dict(Counter(flag for g in geometries for flag in g['source_flags'])),'review_words':len(chosen),'review_roles':dict(Counter(g['role'] for g in chosen)),'new_training':'NOT_RUN','new_neural_inference':'NOT_RUN','translation':'NOT_RUN','expert_review':'NOT_REVIEWED'}
    save(out/'summary.json',stats);print(json.dumps(stats,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--plan',type=Path,required=True);a=p.parse_args();compare(a.repo,a.out,a.plan)
