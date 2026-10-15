#!/usr/bin/env python3
# H112 frozen structural audit. Infrastructure fix: distinguish HTTP access failure
# (BLOCKED) from successfully fetched but non-JSON candidate data (FAIL), exactly
# as specified by the preregistered decision rule. Scientific gates unchanged.
import json, hashlib, urllib.request
from pathlib import Path

SOURCES={
'f69v':'https://vigibygg-cmyk.github.io/voynich-research/data/folio_maps/f69v_mapping.json',
'f75r':'https://vigibygg-cmyk.github.io/voynich-research/data/folio_maps/f75r_mapping.json'}

def fetch_bytes(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()

def explicit_pair_records(d):
    # Strict structural audit only: no token strings/lengths are inspected.
    candidates=[]
    for key in ('pairs','object_label_pairs','label_objects','annotations','labels'):
        v=d.get(key)
        if isinstance(v,list):
            for x in v:
                if not isinstance(x,dict): continue
                has_obj=any(k in x for k in ('object_id','object_bbox','object_coordinates','object'))
                has_lab=any(k in x for k in ('label_id','label_bbox','label_coordinates','label'))
                if has_obj and has_lab: candidates.append((key,x))
    return candidates

def main():
    rows=[]; total_pairs=0; classes={}; access_ok=True
    for folio,url in SOURCES.items():
        try:
            b=fetch_bytes(url)
        except Exception as e:
            access_ok=False
            rows.append({'folio':folio,'url':url,'fetch_ok':False,'parseable_json':False,'error':repr(e)})
            continue
        sha=hashlib.sha256(b).hexdigest()
        try:
            d=json.loads(b)
        except Exception as e:
            # Source was fetched successfully; malformed/non-JSON data fail gate 1.
            # This is a scientific admissibility FAIL, not an infrastructure BLOCKED.
            rows.append({'folio':folio,'url':url,'fetch_ok':True,'sha256':sha,
                         'parseable_json':False,'heldout_from_rosettes':folio not in {'f85v','f86r','f85v_86r'},
                         'error':repr(e)})
            continue
        pairs=explicit_pair_records(d)
        pair_classes=[]
        for _,x in pairs:
            c=x.get('object_class') or x.get('class') or x.get('object_type')
            if c: classes[c]=classes.get(c,0)+1; pair_classes.append(c)
        total_pairs += len(pairs)
        rows.append({'folio':folio,'url':url,'fetch_ok':True,'sha256':sha,
                     'parseable_json':True,'heldout_from_rosettes':folio not in {'f85v','f86r','f85v_86r'},
                     'explicit_pair_records':len(pairs),'pair_classes':sorted(set(pair_classes))})
    all_parse=access_ok and all(r.get('parseable_json',False) for r in rows)
    class_ge10=sum(1 for n in classes.values() if n>=10)
    gates={
      'source_access_parse':all_parse,
      'heldout_from_h105':all(r.get('heldout_from_rosettes',False) for r in rows if r.get('fetch_ok')),
      'explicit_pair_level_structure':total_pairs>=30,
      'at_least_30_pairs':total_pairs>=30,
      'two_visual_classes_ge10':class_ge10>=2,
      'no_token_informed_repair_required':total_pairs>=30 and class_ge10>=2}
    # Frozen rule: only inability to fetch/evaluate is BLOCKED. Successfully fetched
    # candidate sources that fail JSON/structural gates are FAIL.
    status='BLOCKED' if not access_ok else ('PASS' if all(gates.values()) else 'FAIL')
    out={'experiment':'H112','status':status,'lexical_replication':'NOT_RUN','sources':rows,
         'total_explicit_pairs':total_pairs,'class_counts':classes,'gates':gates,
         'note':'Structural admissibility only; token spelling/length/frequency/translation were not inspected.'}
    Path('research_gpt6/results').mkdir(parents=True,exist_ok=True)
    Path('research_gpt6/results/h112_independent_heldout_visual_lexical_admissibility.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
