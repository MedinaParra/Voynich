#!/usr/bin/env python3
"""PACS pilot: Predictive Dependency Spectrum + context ablations + synthetic controls.

This is a structural forecasting experiment, not decipherment.  TimesFM is used
as a fixed zero-shot contrast function.  All evaluation targets are untouched.
Ablations modify only the past context, so a positive loss delta means that the
destroyed property carried predictive information for the original future.
"""
import argparse, hashlib, json, math, re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
MODEL = "google/timesfm-2.5-200m-pytorch"
FEATURES = [
    "tokens","mean_len","uniq_ratio","entropy_char",
    "q_frac","o_frac","y_frac","d_frac","ch_frac","sh_frac","ok_frac","qok_frac",
    "first_q","last_y","suffix_dy"
]
STRUCTURE_COLS = [0,1,2,3]
MORPH_COLS = list(range(4, len(FEATURES)))

def blob_sha(b):
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def entropy(s):
    c = Counter(s); n = len(s)
    return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0.0

def parse(raw):
    out=[]; meta={}
    for line in raw.splitlines():
        mm=re.match(r"^<([^>.,]+)>\s*<!", line)
        if mm:
            meta=dict(re.findall(r"\$([A-Z])=([^\s>]+)",line)); continue
        m=re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m or "," not in m[1] or not re.search(r"P[0-9a-z]",m[1].split(",",1)[1]):
            continue
        locus,text=m.groups()
        clean=re.sub(r"<[^>]*>","",text)
        if "," in text or "<->" in text or not re.fullmatch(r"[a-z.\s]+",clean):
            continue
        w=[x for x in re.split(r"[.\s]+",clean.strip()) if x]
        if len(w)<4: continue
        s="".join(w); n=len(w); L=max(len(s),1)
        occ=lambda pat:s.count(pat)/L
        vals=[
            n, sum(map(len,w))/n, len(set(w))/n, entropy(s),
            occ("q"),occ("o"),occ("y"),occ("d"),occ("ch"),occ("sh"),occ("ok"),occ("qok"),
            sum(x.startswith("q") for x in w)/n,
            sum(x.endswith("y") for x in w)/n,
            sum(x.endswith("dy") for x in w)/n,
        ]
        out.append({
            "x":vals,
            "folio":re.sub(r"\.\d+$","",locus.split(",",1)[0]),
            "quire":meta.get("Q","?"),
            "currier":meta.get("L","?"),
            "hand":meta.get("H","?"),
            "section":meta.get("I","?"),
        })
    return out

def load_model(max_context,horizon):
    import torch, timesfm
    torch.set_float32_matmul_precision("high")
    m=timesfm.TimesFM_2p5_200M_torch.from_pretrained(MODEL)
    m.compile(timesfm.ForecastConfig(
        max_context=max_context,max_horizon=horizon,normalize_inputs=True,
        use_continuous_quantile_head=True,force_flip_invariance=True,
        infer_is_positive=False,fix_quantile_crossing=True
    ))
    return m

def forecast(model,ctx,h):
    point,_=model.forecast(
        horizon=h,
        inputs=[ctx[:,j].astype(np.float32) for j in range(ctx.shape[1])]
    )
    return np.asarray(point,dtype=np.float32).T

def loss(pred,y,scales):
    per=((pred-y)**2).mean(axis=0)
    return float((per/scales).mean()), per

def persistence(ctx,h):
    return np.repeat(ctx[-1:,:],h,axis=0)

def folds_for(X,h,folds):
    ans=[]
    for k in range(folds,0,-1):
        end=len(X)-h*(k-1); start=end-h
        ans.append((start,end))
    return ans

def score_condition(model,X,contexts,h,folds,scales):
    rows=[]
    for c in contexts:
        fold_rows=[]
        for start,end in folds_for(X,h,folds):
            ctx=X[start-c:start]; y=X[start:end]
            p=forecast(model,ctx,h); n=persistence(ctx,h)
            lp,_=loss(p,y,scales); ln,_=loss(n,y,scales)
            fold_rows.append({
                "start":start,"end":end,"standardized_mse":lp,
                "persistence_standardized_mse":ln,
                "skill_vs_persistence":(1-lp/ln) if ln>0 else None
            })
        sm=np.array([r["standardized_mse"] for r in fold_rows],float)
        sk=np.array([r["skill_vs_persistence"] for r in fold_rows if r["skill_vs_persistence"] is not None],float)
        rows.append({
            "context":c,
            "mean_standardized_mse":float(sm.mean()),
            "median_standardized_mse":float(np.median(sm)),
            "mean_skill_vs_persistence":float(sk.mean()) if len(sk) else None,
            "folds_beating_persistence":int(sum(x>0 for x in sk)),
            "folds":fold_rows
        })
    return rows

def folio_blocks(meta_idx):
    blocks=[]; cur=[]; prev=None
    for i,folio in enumerate(meta_idx):
        if prev is None or folio==prev:
            cur.append(i)
        else:
            blocks.append(cur); cur=[i]
        prev=folio
    if cur: blocks.append(cur)
    return blocks

def ablate(ctx,meta,rng,name):
    z=ctx.copy()
    if name=="reverse_context":
        return z[::-1].copy()
    if name=="channel_shuffle":
        for j in range(z.shape[1]): z[:,j]=z[rng.permutation(len(z)),j]
        return z
    if name=="shuffle_folio_blocks":
        blocks=folio_blocks([r["folio"] for r in meta])
        order=rng.permutation(len(blocks))
        ix=[i for b in order for i in blocks[b]]
        return z[ix]
    if name=="shuffle_lines_within_folio":
        groups=defaultdict(list)
        for i,r in enumerate(meta): groups[r["folio"]].append(i)
        for ids in groups.values():
            perm=rng.permutation(ids)
            z[ids]=z[perm]
        return z
    if name=="flatten_structure":
        z[:,STRUCTURE_COLS]=np.mean(z[:,STRUCTURE_COLS],axis=0,keepdims=True)
        return z
    if name=="flatten_morphology":
        z[:,MORPH_COLS]=np.mean(z[:,MORPH_COLS],axis=0,keepdims=True)
        return z
    raise ValueError(name)

def score_ablations(model,X,rows,context,h,folds,scales,seed,names=None):
    if names is None:
        names=[
            "shuffle_folio_blocks","shuffle_lines_within_folio","reverse_context",
            "channel_shuffle","flatten_structure","flatten_morphology"
        ]
    out={n:[] for n in names}; base=[]
    for fi,(start,end) in enumerate(folds_for(X,h,folds)):
        ctx=X[start-context:start]; y=X[start:end]; meta=rows[start-context:start]
        bp=forecast(model,ctx,h); bl,_=loss(bp,y,scales); base.append(bl)
        for name in names:
            rr=np.random.default_rng(seed + 1009*fi + 7919*(names.index(name)+1))
            z=ablate(ctx,meta,rr,name)
            p=forecast(model,z,h); l,_=loss(p,y,scales)
            out[name].append({"start":start,"end":end,"standardized_mse":l,"delta_vs_original":l-bl})
    summary={}
    for name,v in out.items():
        d=np.array([x["delta_vs_original"] for x in v],float)
        l=np.array([x["standardized_mse"] for x in v],float)
        summary[name]={
            "mean_standardized_mse":float(l.mean()),
            "mean_delta_vs_original":float(d.mean()),
            "median_delta_vs_original":float(np.median(d)),
            "folds_harmed":int(sum(d>0)),
            "folds_helped":int(sum(d<0)),
            "folds":v
        }
    return {
        "context":context,
        "original_mean_standardized_mse":float(np.mean(base)),
        "interpretation":"positive delta means the context destruction increased forecasting loss on the untouched real future",
        "ablations":summary
    }

def make_controls(X,fit_end,seed):
    rng=np.random.default_rng(seed); train=X[:fit_end].astype(float)
    n,d=X.shape; lo=train.min(axis=0); hi=train.max(axis=0)
    iid_rows=train[rng.integers(0,fit_end,size=n)].copy()
    chan=np.empty((n,d),float)
    for j in range(d): chan[:,j]=train[rng.integers(0,fit_end,size=n),j]
    ar=np.empty((n,d),float); ar[0]=train[0]
    for j in range(d):
        x=train[:-1,j]; y=train[1:,j]
        vx=float(np.var(x))
        phi=float(np.cov(x,y,bias=True)[0,1]/vx) if vx>1e-12 else 0.0
        phi=float(np.clip(phi,-0.98,0.98))
        mu=float(np.mean(train[:,j]))
        resid=y-(mu+phi*(x-mu))
        sig=float(np.std(resid))
        for t in range(1,n):
            ar[t,j]=mu+phi*(ar[t-1,j]-mu)+rng.normal(0,sig)
    ar=np.clip(ar,lo,hi)
    cp=np.empty((n,d),float); cp[0]=train[0]
    sig=np.maximum(np.std(train,axis=0)*0.10,1e-8)
    for t in range(1,n):
        left=max(0,t-8); src=int(rng.integers(left,t))
        cp[t]=cp[src]+rng.normal(0,sig,size=d)
    cp=np.clip(cp,lo,hi)
    return {
        "iid_row_resample":iid_rows.astype(np.float32),
        "independent_channel_resample":chan.astype(np.float32),
        "ar1_matched":ar.astype(np.float32),
        "local_copy_mutate":cp.astype(np.float32),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--contexts",default="32,64,128,256,512")
    ap.add_argument("--horizon",type=int,default=16)
    ap.add_argument("--folds",type=int,default=6)
    ap.add_argument("--ablation-context",type=int,default=128)
    ap.add_argument("--seed",type=int,default=20261007)
    ap.add_argument("--only-folio",action="store_true")
    a=ap.parse_args()
    b=a.corpus.read_bytes()
    if blob_sha(b)!=BLOB: raise SystemExit("Corpus blob mismatch")
    rows=parse(b.decode()); X=np.asarray([r["x"] for r in rows],dtype=np.float32)
    contexts=[int(x) for x in a.contexts.split(",") if int(x)>0]
    if min(start for start,_ in folds_for(X,a.horizon,a.folds)) <= max(max(contexts),a.ablation_context):
        raise SystemExit("Insufficient rows for requested contexts")
    fit_end=len(X)-a.horizon*a.folds
    scales=np.maximum(np.var(X[:fit_end],axis=0),1e-8)
    folio_counts=Counter(r["folio"] for r in rows)
    repeated_folios=sum(v>1 for v in folio_counts.values())
    if repeated_folios == 0:
        raise SystemExit("Folio parser invariant failed: every row has a unique folio")
    model=load_model(max(max(contexts),a.ablation_context),a.horizon)

    if a.only_folio:
        audit=score_ablations(
            model,X,rows,a.ablation_context,a.horizon,a.folds,scales,a.seed,
            names=["shuffle_folio_blocks","shuffle_lines_within_folio"]
        )
        result={
            "classification":"PACS_FOLIO_PATCH_AUDIT_NOT_DECIPHERMENT",
            "status":"PASS_EXECUTED",
            "source_blob":BLOB,"model":MODEL,"seed":a.seed,
            "rows":len(X),"unique_folios":len(folio_counts),
            "folios_with_multiple_rows":repeated_folios,
            "evaluation":{"horizon":a.horizon,"folds":a.folds,"context":a.ablation_context},
            "context_ablation_matrix":audit,
            "parser_fix":"line suffix stripped from locus before folio grouping"
        }
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,indent=2))
        return

    real_spectrum=score_condition(model,X,contexts,a.horizon,a.folds,scales)
    ablations=score_ablations(model,X,rows,a.ablation_context,a.horizon,a.folds,scales,a.seed)

    controls=make_controls(X,fit_end,a.seed)
    control_results={}
    for name,C in controls.items():
        cscale=np.maximum(np.var(C[:fit_end],axis=0),1e-8)
        control_results[name]=score_condition(model,C,contexts,a.horizon,a.folds,cscale)

    best_real=min(real_spectrum,key=lambda r:r["mean_standardized_mse"])
    fingerprint={
        "spectrum_contexts":contexts,
        "real_energy":[r["mean_standardized_mse"] for r in real_spectrum],
        "real_skill":[r["mean_skill_vs_persistence"] for r in real_spectrum],
        "ablation_delta":{k:v["mean_delta_vs_original"] for k,v in ablations["ablations"].items()},
        "best_context_by_energy":best_real["context"],
        "best_mean_standardized_mse":best_real["mean_standardized_mse"],
    }
    result={
        "classification":"PACS_PREDICTIVE_ARCHAEOLOGY_PILOT_NOT_DECIPHERMENT",
        "status":"PASS_EXECUTED",
        "source_blob":BLOB,"model":MODEL,"seed":a.seed,
        "rows":len(X),"features":FEATURES,
        "method_note":"TimesFM is used as a fixed multi-channel zero-shot contrast function; channels are forecast as separate series in one batched call, not as proof of linguistic semantics.",
        "evaluation":{
            "horizon":a.horizon,"folds":a.folds,"fit_end":fit_end,
            "target_policy":"all targets untouched; scales and synthetic-control parameters fitted before all evaluation targets"
        },
        "predictive_dependency_spectrum":{"real":real_spectrum,"controls":control_results},
        "context_ablation_matrix":ablations,
        "fingerprint":fingerprint,
        "limitations":[
            "Exploratory pilot on one EVA transcription and one TimesFM model.",
            "Synthetic controls are mechanism probes, not exhaustive models of natural language or historical cipher production.",
            "Ablations identify predictive dependence, not semantic causation.",
            "Multiple seeds and independent transcriptions are required before confirmatory claims."
        ]
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
