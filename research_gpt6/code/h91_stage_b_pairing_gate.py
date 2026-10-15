#!/usr/bin/env python3
"""H91 Stage B: blind label-box/object pairing stability gate.

Uses only geometry frozen by H91g. It never reads, retains, prints, hashes, or
selects on lexical token values. Pairing and jitter rules are exactly those
frozen in H91g.
"""
import argparse, json, math
from pathlib import Path
from h91b_stage_a_inventory import (
    API, EXCLUDED, EXPECTED_CANDIDATES, JITTER_OFFSETS, JITTER_VERSION,
    PAIRING_RULE, blind_label_boxes, frozen_objects, get_bytes,
)
from h76_visual_object_extraction_admissibility import run_page

MIN_OBJECTS=15
MIN_STABILITY=0.80
MIN_FOLIOS=2
MIN_TOTAL_STABLE_PAIRS=40


def greedy_pairs(objects, labels, dx=0.0, dy=0.0):
    edges=[]
    for o in objects:
        ox=float(o["centroid"][0])+dx; oy=float(o["centroid"][1])+dy
        for lab in labels:
            lx=float(lab["centroid"][0]); ly=float(lab["centroid"][1])
            d=math.hypot(ox-lx,oy-ly)
            edges.append((d,o["object_id"],int(lab["label_ordinal"])))
    edges.sort(key=lambda z:(z[0],z[1],z[2]))
    used_o=set(); used_l=set(); out={}
    for _,oid,lid in edges:
        if oid in used_o or lid in used_l: continue
        used_o.add(oid); used_l.add(lid); out[oid]=lid
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",type=Path,required=True); a=ap.parse_args()
    listing=json.loads(get_bytes(API))
    files=sorted((x for x in listing if x.get("type")=="file" and x["name"].endswith(".json")),key=lambda x:x["name"])
    evaluated=[]; stage_a_candidates=0; blocked=0
    for item in files:
        page=item["name"][:-5]
        if page in EXCLUDED: continue
        try:
            raw=get_bytes(item["download_url"]); p=Path("/tmp")/item["name"]; p.write_bytes(raw)
            r=run_page(page,p); objects=frozen_objects(r)
            if len(objects)<MIN_OBJECTS: continue
            stage_a_candidates+=1
            labels=blind_label_boxes(raw)
            base=greedy_pairs(objects,labels,0,0)
            jitter_maps=[greedy_pairs(objects,labels,float(dx),float(dy)) for dx,dy in JITTER_OFFSETS]
            stable=[]
            for oid,lid in sorted(base.items()):
                if all(m.get(oid)==lid for m in jitter_maps): stable.append([oid,lid])
            raw_pairs=len(base); stable_n=len(stable)
            frac=(stable_n/raw_pairs) if raw_pairs else 0.0
            admissible=(len(objects)>=MIN_OBJECTS and raw_pairs>=MIN_OBJECTS and frac>=MIN_STABILITY)
            evaluated.append({
                "page":page,"object_count":len(objects),"label_box_count":len(labels),
                "raw_pair_count":raw_pairs,"stable_pair_count":stable_n,
                "stability_fraction":frac,"admissible":admissible,
                "stable_pairs":[{"object_id":oid,"label_ordinal":lid} for oid,lid in stable],
                "coord_blob_sha":item.get("sha"),"image_sha256":r.get("image_sha256"),
            })
        except Exception as e:
            blocked+=1; evaluated.append({"page":page,"status":"BLOCKED","error":f"{type(e).__name__}: {e}"})
    admissible=[x for x in evaluated if x.get("admissible")]
    total_stable=sum(x["stable_pair_count"] for x in admissible)
    inventory_ok=(stage_a_candidates==EXPECTED_CANDIDATES)
    family_pass=(len(admissible)>=MIN_FOLIOS and total_stable>=MIN_TOTAL_STABLE_PAIRS)
    status="BLOCKED" if blocked else ("PASS" if inventory_ok and family_pass else "FAIL")
    out={
      "experiment":"H91 independent label-object replication gate Stage B",
      "classification":"BLIND_GEOMETRIC_PAIRING_NOT_SEMANTICS",
      "lexical_strings":"NOT_READ_OR_RETAINED",
      "pairing_rule_id":PAIRING_RULE,"jitter_version":JITTER_VERSION,"jitter_offsets_pixels":JITTER_OFFSETS,
      "thresholds":{"min_objects":MIN_OBJECTS,"min_stability_fraction":MIN_STABILITY,"min_admissible_folios":MIN_FOLIOS,"min_total_stable_pairs":MIN_TOTAL_STABLE_PAIRS},
      "stage_a_candidate_count_reproduced":stage_a_candidates,"expected_stage_a_candidate_count":EXPECTED_CANDIDATES,"inventory_ok":inventory_ok,
      "evaluated_candidate_count":len([x for x in evaluated if x.get("status")!="BLOCKED"]),"blocked_count":blocked,
      "admissible_folio_count":len(admissible),"admissible_folios":[x["page"] for x in admissible],
      "total_stable_pairs_across_admissible_folios":total_stable,"family_gate_pass":family_pass,
      "folios":evaluated,"status":status,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ("status","stage_a_candidate_count_reproduced","inventory_ok","blocked_count","admissible_folio_count","total_stable_pairs_across_admissible_folios","family_gate_pass")},indent=2,sort_keys=True))
if __name__=="__main__": main()
