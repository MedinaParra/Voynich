#!/usr/bin/env python3
import json, hashlib, urllib.request
from pathlib import Path

SOURCES={
'f69v':'https://vigibygg-cmyk.github.io/voynich-research/data/folio_maps/f69v_mapping.json',
'f75r':'https://vigibygg-cmyk.github.io/voynich-research/data/folio_maps/f75r_mapping.json'}

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r: b=r.read()
    return b,json.loads(b)

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
    rows=[]; total_pairs=0; classes={}; infra=True
    for folio,url in SOURCES.items():
        try:
            b,d=fetch(url)
            pairs=explicit_pair_records(d)
            pair_classes=[]
            for _,x in pairs:
                c=x.get('object_class') or x.get('class') or x.get('object_type')
                if c: classes[c]=classes.get(c,0)+1; pair_classes.append(c)
            total_pairs += len(pairs)
            rows.append({'folio':folio,'url':url,'sha256':hashlib.sha256(b).hexdigest(),
                         'parseable_json':True,'heldout_from_rosettes':folio not in {'f85v','f86r','f85v_86r'},
                         'explicit_pair_records':len(pairs),'pair_classes':sorted(set(pair_classes))})
        except Exception as e:
            infra=False; rows.append({'folio':folio,'url':url,'parseable_json':False,'error':repr(e)})
    class_ge10=sum(1 for n in classes.values() if n>=10)
    gates={
      'source_access_parse':infra and all(r.get('parseable_json') for r in rows),
      'heldout_from_h105':all(r.get('heldout_from_rosettes',False) for r in rows if r.get('parseable_json')),
      'explicit_pair_level_structure':total_pairs>=30,
      'at_least_30_pairs':total_pairs>=30,
      'two_visual_classes_ge10':class_ge10>=2,
      'no_token_informed_repair_required':total_pairs>=30 and class_ge10>=2}
    status='BLOCKED' if not gates['source_access_parse'] else ('PASS' if all(gates.values()) else 'FAIL')
    out={'experiment':'H112','status':status,'lexical_replication':'NOT_RUN','sources':rows,
         'total_explicit_pairs':total_pairs,'class_counts':classes,'gates':gates,
         'note':'Structural admissibility only; token spelling/length/frequency/translation were not inspected.'}
    Path('research_gpt6/results').mkdir(parents=True,exist_ok=True)
    Path('research_gpt6/results/h112_independent_heldout_visual_lexical_admissibility.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
