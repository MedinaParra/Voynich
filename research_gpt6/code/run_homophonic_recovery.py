#!/usr/bin/env python3
"""Public-input-only comparison. No reveal file or evaluator imports."""
import argparse, hashlib, json, os, platform, re, subprocess, time
from pathlib import Path
import numpy as np

def sha256(raw): return hashlib.sha256(raw).hexdigest()
def gitblob(raw): return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def score(text,lm):
    a=np.frombuffer(text.encode("ascii"),dtype=np.uint8).astype(np.int64)-97
    idx=np.zeros(len(a)-3,dtype=np.int64)
    for j in range(4): idx=idx*26+a[j:j+len(idx)]
    return int(lm[idx].astype(np.int64).sum())

def main(a):
    repo=a.repo.resolve(); bundle=a.bundle.resolve()
    frozen=json.loads((bundle/"source_freeze.json").read_text())
    for f in frozen["files"]:
        p=repo/f["path"]
        assert gitblob(p.read_bytes())==f["git_blob"],f["path"]
    config=repo/"data/homophonic_recovery_plan.json"
    config_blob=gitblob(config.read_bytes()); assert config_blob==frozen["config_git_blob"]
    plan=json.loads(config.read_text()); assert plan["search"]["baseline_fallback_or_warm_start"] is False
    cases=json.loads((bundle/"public/ciphertexts.json").read_text())["cases"]
    assert len(cases)==9 and len({c["id"] for c in cases})==9
    assert all(re.fullmatch("U0[1-9]",c["id"]) for c in cases)
    assert all(re.fullmatch("[a-z]{2000}",c["ciphertext"]) for c in cases)
    assert len({c["ciphertext"] for c in cases})==9
    model=repo/"results/known_cipher_recovery/model"
    lm=np.fromfile(model/"lm_int32.bin",dtype="<i4")
    assert sha256((model/"lm_int32.bin").read_bytes())==plan["training"]["lm_sha256"]
    a.out.mkdir(parents=True,exist_ok=True); inp=a.out/"search_inputs";inp.mkdir(exist_ok=True)
    out={"schema_version":1,"config_git_blob":config_blob,"model_source_commit":plan["base_commit"],
         "language_assumption":"known Latin","source_hashes":{f["path"]:sha256((repo/f["path"]).read_bytes()) for f in frozen["files"]},
         "selection":"maximum integer4gram score within each independent per-case search; no cross-case transfer or fallback",
         "Voynich_translation":"NOT_RUN","models":[]}
    runtime={"python":platform.python_version(),"numpy":np.__version__,"runs":[],"binaries":{}}
    started=time.perf_counter()
    for name,binary in [("bijective",a.bijective),("many_to_one",a.many_to_one)]:
        binary=binary.resolve();runtime["binaries"][name]=sha256(binary.read_bytes())
        records=[]
        for c in cases:
            text=c["ciphertext"]; digest=hashlib.sha256(text.encode()).digest()
            seed=int.from_bytes(digest[:8],"little")^plan["search"]["seed"]
            p=inp/(c["id"]+".txt");p.write_text(text+"\n")
            cmd=[str(binary),str(model/"lm_int32.bin"),str(model/"accept_u64.bin"),
                 str(model/"temperatures_i32.bin"),str(model/"plain_frequency_rank.txt"),str(p),
                 str(seed),str(plan["search"]["restarts"]),str(plan["search"]["steps_per_restart"]),
                 str(plan["search"]["polish_pass_cap"])]
            t=time.perf_counter();r=json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
            key=r["key"]; assert re.fullmatch("[a-z]{26}",key)
            if name=="bijective": assert len(set(key))==26
            decoded="".join(key[ord(x)-97] for x in text)
            assert decoded==r["letters_plaintext"] and score(decoded,lm)==r["score"]
            assert r["annealing_proposals"]==400000 and len(r["restart_scores"])==8
            records.append({"id":c["id"],"key":key,"plaintext":decoded,"letters_plaintext":decoded,
                            "seed":seed,**{k:v for k,v in r.items() if k not in ["key","letters_plaintext"]}})
            dt=time.perf_counter()-t;runtime["runs"].append({"model":name,"id":c["id"],"seconds":dt,
                "annealing_proposals":r["annealing_proposals"],"polish_pair_checks":r["polish_pair_checks"]})
            print(json.dumps({"model":name,"case":c["id"],"score":r["score"],"seconds":round(dt,3)}),flush=True)
        out["models"].append({"name":name,"cases":records})
    runtime["seconds"]=time.perf_counter()-started
    runtime["unique_searches"]=len(runtime["runs"])
    runtime["annealing_proposals"]=sum(r["annealing_proposals"] for r in runtime["runs"])
    runtime["polish_pair_checks"]=sum(r["polish_pair_checks"] for r in runtime["runs"])
    for label,value in [("predictions",out),("execution",runtime)]:
        raw=json.dumps(value,indent=2)+"\n";(a.out/(label+".json")).write_text(raw)
        for i in range(0,len(raw),2048):
            print("H88_"+label.upper()+"_PART:"+json.dumps(raw[i:i+2048]),flush=True)
    pred=(a.out/"predictions.json").read_bytes();execution=(a.out/"execution.json").read_bytes()
    print("H88_OUTPUT_META:"+json.dumps({"head_sha":os.environ.get("GITHUB_SHA"),
        "config_git_blob":config_blob,"public_manifest_git_blob":gitblob((bundle/"public/manifest.json").read_bytes()),
        "source_freeze_git_blob":gitblob((bundle/"source_freeze.json").read_bytes()),
        "predictions_git_blob":gitblob(pred),"predictions_sha256":sha256(pred),
        "execution_git_blob":gitblob(execution),"execution_sha256":sha256(execution),
        "unique_searches":runtime["unique_searches"],"annealing_proposals":runtime["annealing_proposals"]}),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True);p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--bijective",type=Path,required=True);p.add_argument("--many-to-one",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True);main(p.parse_args())
