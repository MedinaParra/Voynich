#!/usr/bin/env python3
"""H91g complete blind Stage-A manifest.

Implements the prospectively frozen H91g manifest schema. Lexical token values are
never retained, printed, hashed as values, or used for selection. Coordinate rows
are reduced immediately to ordinal + numeric geometry.
"""
import argparse, hashlib, json, os, urllib.request
from pathlib import Path
from h76_visual_object_extraction_admissibility import run_page

YALE_SHA="c4d36f4595292c92da8c7428e30cb23b700a019b"
API=f"https://api.github.com/repos/YaleDHLab/voynich/contents/utils/voynichese/coords?ref={YALE_SHA}"
EXCLUDED={"f68r1","f68r2"}
PAIRING_RULE="nearest-label-centroid-euclidean-global-greedy-v1"
JITTER_VERSION="NONE_DETERMINISTIC_GRID_V1"
JITTER_OFFSETS=[[-5,-5],[-5,0],[-5,5],[0,-5],[0,0],[0,5],[5,-5],[5,0],[5,5]]
EXPECTED_CONTROLS={"f68r1":57,"f68r2":89}
EXPECTED_CANDIDATES=168

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Voynich-H91g/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r: return r.read()

def blind_label_boxes(raw):
    data=json.loads(raw)
    if not isinstance(data,list) or len(data)!=2 or not isinstance(data[1],list):
        raise ValueError("unexpected Yale coordinate JSON structure")
    out=[]
    for ordinal,row in enumerate(data[1]):
        if not isinstance(row,list) or len(row)<5: continue
        # Deliberately never bind/read row[0] (lexical value).
        x,y,w,h=(int(row[i]) for i in range(1,5))
        out.append({"label_ordinal":ordinal,"bbox":[x,y,w,h],"centroid":[x+w/2.0,y+h/2.0]})
    return out

def frozen_objects(result):
    out=[]
    for c in result.get("components",[]):
        if not c.get("low_text_overlap"): continue
        out.append({
            "object_id":f"component-{int(c['component_id']):06d}",
            "bbox":c["bbox"],"centroid":c["centroid"],"area":int(c["area"]),
            "text_overlap_fraction":float(c["text_bbox_overlap_fraction"]),
        })
    return sorted(out,key=lambda x:x["object_id"])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args()
    runner_sha256=sha256_bytes(Path(__file__).read_bytes())
    executing_commit=os.environ.get("GITHUB_SHA","UNKNOWN")
    listing=json.loads(get_bytes(API))
    files=sorted((x for x in listing if x.get("type")=="file" and x["name"].endswith(".json")),key=lambda x:x["name"])
    records=[]; controls={}; blocked=0
    for item in files:
        page=item["name"][:-5]
        raw=get_bytes(item["download_url"]); p=Path("/tmp")/item["name"]; p.write_bytes(raw)
        try:
            r=run_page(page,p)
            n=int(r.get("low_text_overlap_component_count",0))
            if page in EXCLUDED:
                controls[page]={"observed_low_text_overlap_component_count":n,"expected":EXPECTED_CONTROLS[page],"pass":n==EXPECTED_CONTROLS[page]}
                records.append({"page":page,"status":"EXCLUDED_MECHANICAL","reason":"frozen H91b exclusion","coord_blob_sha":item["sha"],"coord_sha256":sha256_bytes(raw),"image_sha256":r.get("image_sha256"),"control_low_text_overlap_component_count":n})
                continue
            labels=blind_label_boxes(raw)
            objects=frozen_objects(r)
            records.append({"page":page,"coord_blob_sha":item["sha"],"coord_sha256":sha256_bytes(raw),"image_sha256":r.get("image_sha256"),"visual_status":r.get("status"),"candidate_object_count":n,"stage_a_candidate":n>=15,"objects":objects,"label_boxes":labels})
        except Exception as e:
            blocked+=1
            records.append({"page":page,"coord_blob_sha":item.get("sha"),"status":"BLOCKED","error":f"{type(e).__name__}: {e}"})
    candidates=[x["page"] for x in records if x.get("stage_a_candidate")]
    controls_pass=all(controls.get(p,{}).get("pass") is True for p in sorted(EXPECTED_CONTROLS))
    schema_complete=blocked==0 and all((r.get("status")=="EXCLUDED_MECHANICAL") or all(k in r for k in ("coord_blob_sha","coord_sha256","image_sha256","objects","label_boxes","stage_a_candidate")) for r in records)
    candidate_count_pass=len(candidates)==EXPECTED_CANDIDATES
    status="PASS" if controls_pass and schema_complete and candidate_count_pass else ("BLOCKED" if blocked else "FAIL")
    out={
      "experiment":"H91g complete blind Stage-A manifest","classification":"BLIND_VISUAL_MANIFEST_NOT_SEMANTICS",
      "lexical_strings":"NOT_INSPECTED_OR_RETAINED","yale_source_commit":YALE_SHA,
      "executing_repository_commit_sha":executing_commit,"stage_a_runner_sha256":runner_sha256,
      "inventory_rule":"all Yale coords JSON in canonical filename order; f68r1/f68r2 controls excluded from independent inventory; candidate iff frozen H76/H91c low-overlap component count >=15",
      "pairing_rule":{"id":PAIRING_RULE,"definition":"nearest eligible label-box centroid to object centroid in Euclidean image coordinates; deterministic tie break by lowest label ordinal; one-to-one assignment by globally sorted (distance, object_id, label_ordinal) greedy acceptance"},
      "jitter_schedule":{"version":JITTER_VERSION,"offsets_pixels":JITTER_OFFSETS},
      "positive_controls":controls,"controls_pass":controls_pass,"schema_complete":schema_complete,"blocked_record_count":blocked,
      "expected_candidate_count":EXPECTED_CANDIDATES,"candidate_count_pass":candidate_count_pass,
      "records":records,"candidate_folios":candidates,"candidate_count":len(candidates),"status":status}
    canonical=json.dumps(out,sort_keys=True,separators=(",",":")); out["manifest_sha256"]=sha256_bytes(canonical.encode())
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"candidate_count":len(candidates),"controls":controls,"schema_complete":schema_complete,"blocked_record_count":blocked,"manifest_sha256":out["manifest_sha256"]},indent=2,sort_keys=True))
if __name__=="__main__": main()
