#!/usr/bin/env python3
"""H111 preregistered token-blind H91 visual-box <-> IVTFF L* bridge gate."""
import argparse, hashlib, json, re, subprocess
from collections import Counter, defaultdict
from pathlib import Path
from h91b_stage_a_inventory import API, EXCLUDED, blind_label_boxes, get_bytes
from h67_richer_label_source_audit import OBJECT_UNITS, clean_known_tokens, normalized_unit, sha256, git_blob_sha1

MIN_FOLIOS=3
MIN_PAIRS=30
MIN_CLASSES=2


def git_head():
    try: return subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
    except Exception: return None


def folio_from_locus(s):
    # IVTFF locus begins with a folio/page id before the comma, e.g. f1r.
    x=s.split(',',1)[0].strip()
    return x[1:] if x.startswith('<') else x


def textual_records(text):
    by=defaultdict(list)
    ordinal=Counter()
    for line_no,line in enumerate(text.splitlines(),1):
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m.group(1): continue
        locus,payload=m.groups(); locator=locus.split(',',1)[1]
        unit=normalized_unit(locator)
        if unit not in OBJECT_UNITS: continue
        page=folio_from_locus(locus)
        ordinal[page]+=1
        # Token values are sealed payload: retained for audit output only and never
        # passed to sorting, equality, filtering, or pairing logic.
        by[page].append({'text_ordinal':ordinal[page], 'locator':locator,
                         'unit':unit, 'line_no':line_no, 'sealed_payload':payload})
    return by


def visual_order(labels):
    # H91 boxes expose centroid and label_ordinal. Pairing keys use geometry only.
    return sorted(labels,key=lambda x:(float(x['centroid'][1]),float(x['centroid'][0]),int(x['label_ordinal'])))


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    data=a.source.read_bytes(); text=data.decode('utf-8','strict')
    base={'experiment':'H111 visual-box Lstar bridge admissibility','classification':'TOKEN_BLIND_BRIDGE_NOT_SEMANTICS',
          'commit_sha':git_head(),'source_sha256':sha256(data),'source_git_blob_sha1':git_blob_sha1(data),
          'thresholds':{'min_folio_pages':MIN_FOLIOS,'min_pairs':MIN_PAIRS,'min_lstar_classes':MIN_CLASSES},
          'pairing_lexical_fields_imported':False,'visual_boxes_mutated':False}
    try:
        tby=textual_records(text)
        listing=json.loads(get_bytes(API))
        files=sorted((x for x in listing if x.get('type')=='file' and x['name'].endswith('.json')),key=lambda x:x['name'])
        vby={}; visual_source=[]
        for item in files:
            page=item['name'][:-5]
            if page in EXCLUDED: continue
            raw=get_bytes(item['download_url']); labs=blind_label_boxes(raw)
            vby[page]=visual_order(labs); visual_source.append({'page':page,'coord_blob_sha':item.get('sha'),'n_visual':len(labs)})
        common=sorted(set(vby)&set(tby))
        pages=[]; pairs=[]; classes=set()
        for page in common:
            vv=vby[page]; tt=tby[page]; equal=len(vv)==len(tt)
            retained=len(vv) if equal else 0
            pages.append({'page':page,'n_visual':len(vv),'n_Lstar':len(tt),'equal':equal,'retained_pairs':retained})
            if equal:
                for rank,(v,t) in enumerate(zip(vv,tt),1):
                    classes.add(t['unit'])
                    pairs.append({'page':page,'rank':rank,'label_ordinal':int(v['label_ordinal']),
                                  'centroid':[float(v['centroid'][0]),float(v['centroid'][1])],
                                  'text_ordinal':t['text_ordinal'],'locator':t['locator'],'unit':t['unit'],
                                  'source_line_no':t['line_no'],'sealed_token_value':t['sealed_payload']})
        f_exact=sum(1 for x in pages if x['equal']); n_exact=len(pairs)
        status='PASS' if f_exact>=MIN_FOLIOS and n_exact>=MIN_PAIRS and len(classes)>=MIN_CLASSES else 'FAIL'
        base.update({'common_folio_page_count':len(common),'per_folio_page':pages,'F_exact':f_exact,'N_exact':n_exact,
                     'represented_Lstar_classes':sorted(classes),'represented_Lstar_class_count':len(classes),
                     'manual_or_token_informed_repairs':0,'bridge':pairs,'visual_source_manifest':visual_source,'status':status})
    except Exception as e:
        base.update({'status':'BLOCKED','reason':f'{type(e).__name__}: {e}'})
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(base,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:base.get(k) for k in ('status','common_folio_page_count','F_exact','N_exact','represented_Lstar_classes','reason')},indent=2,sort_keys=True))

if __name__=='__main__': main()
