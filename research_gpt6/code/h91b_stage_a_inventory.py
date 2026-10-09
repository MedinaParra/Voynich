#!/usr/bin/env python3
"""H91b/H91e Stage A: enumerate frozen Yale coordinate folios and run H91c visual extraction.
Lexical token values are never retained, printed, hashed separately, or used for selection.
H91e permits exactly one functional repair to H91b: read the validated H76/H91c
`low_text_overlap_component_count` result key rather than the nonexistent
`low_text_overlap_components` key.
"""
import argparse, hashlib, json, urllib.request
from pathlib import Path
from h76_visual_object_extraction_admissibility import run_page

YALE_SHA="c4d36f4595292c92da8c7428e30cb23b700a019b"
API=f"https://api.github.com/repos/YaleDHLab/voynich/contents/utils/voynichese/coords?ref={YALE_SHA}"
EXCLUDED={"f68r1","f68r2"}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Voynich-H91e/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r: return r.read()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args()
    listing=json.loads(get_json(API))
    files=sorted((x for x in listing if x.get("type")=="file" and x["name"].endswith(".json")),key=lambda x:x["name"])
    records=[]
    for item in files:
        page=item["name"][:-5]
        if page in EXCLUDED:
            records.append({"page":page,"status":"EXCLUDED_MECHANICAL","reason":"frozen H91b exclusion"}); continue
        raw=get_json(item["download_url"]); p=Path("/tmp")/item["name"]; p.write_bytes(raw)
        try:
            r=run_page(page,p)
            n=int(r.get("low_text_overlap_component_count",0))
            # Coordinate identifiers are ordinals only; token text is not exposed.
            records.append({"page":page,"coord_blob_sha":item["sha"],"coord_sha256":hashlib.sha256(raw).hexdigest(),"candidate_object_count":n,"stage_a_candidate":n>=15,"visual_status":r.get("status"),"image_sha256":r.get("image_sha256"),"label_coordinate_identifiers":"REDACTED_ORDINALS_ONLY"})
        except Exception as e:
            records.append({"page":page,"coord_blob_sha":item["sha"],"status":"BLOCKED","error":f"{type(e).__name__}: {e}"})
    candidates=[x["page"] for x in records if x.get("stage_a_candidate")]
    out={"experiment":"H91e repaired Stage A","lexical_strings":"NOT_INSPECTED_OR_RETAINED","yale_source_commit":YALE_SHA,"inventory_rule":"all Yale coords JSON in canonical filename order; exclude f68r1/f68r2; candidate iff frozen H76/H91c low-overlap component count >=15","records":records,"candidate_folios":candidates,"candidate_count":len(candidates),"status":"PASS" if candidates else "FAIL"}
    canonical=json.dumps(out,sort_keys=True,separators=(",",":")); out["manifest_sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"candidate_count":len(candidates),"manifest_sha256":out["manifest_sha256"]},indent=2))
if __name__=="__main__": main()
