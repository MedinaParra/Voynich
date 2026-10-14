#!/usr/bin/env python3
"""Conditional two-view pilot. Neither direction is translation.

Corpus pilot uses literal Lc/Lf metadata, not independently verified meanings.
Permutation diagnostics explicitly expose a frozen/weak null.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import platform
import re

import numpy as np

SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
SEED = 408
PATTERNS = ('a','c','d','e','h','i','k','l','n','o','q','r','s','t','y',
            'ch','sh','qo','ai','ee','dy')


def parse(raw):
    pages, rows = {}, []
    for line in raw.splitlines():
        p = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if p:
            pages[p[1]] = dict(re.findall(r'\$([A-Z])=([^\s>]+)', p[2]))
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m[1]:
            continue
        tag = m[1].split(',',1)[1]
        kind = next((k for k in ('Lc','Lf') if k in tag), None)
        token = re.sub(r'<[^>]*>', '', m[2]).strip()
        if kind is None or not re.fullmatch('[a-z]{2,}', token):
            continue
        folio = m[1].split('.')[0]
        meta = pages.get(folio,{})
        if meta.get('Q','?') == '?':
            continue
        rows.append(dict(id=m[1],folio=folio,quire=meta['Q'],
                         currier=meta.get('L','?'),hand=meta.get('H','?'),
                         token=token,label=kind))
    return rows


def arrays(rows):
    lengths = np.array([len(r['token']) for r in rows])
    # Exact length indicators 2..15, then 16+; no folio/quire ID features.
    nuisance = np.column_stack((lengths/10, (lengths/10)**2,
        np.eye(15)[np.clip(lengths-2,0,14)]))
    content = np.array([[r['token'].count(p)/len(r['token']) for p in PATTERNS]
                        for r in rows])
    return nuisance,content


def ridge(train_x, train_y, test_x):
    # Center/scale fitted exclusively on training rows. Fixed alpha, no tuning.
    mean, scale = train_x.mean(0), np.maximum(train_x.std(0), 1e-8)
    x = (train_x-mean)/scale
    t = (test_x-mean)/scale
    ymean = train_y.mean(0)
    w = np.linalg.solve(x.T@x + np.eye(x.shape[1]), x.T@(train_y-ymean))
    return t@w+ymean


def evaluate(rows, y=None, purge=True):
    classes = sorted({r['label'] for r in rows})
    if len(classes) != 2:
        raise ValueError('Pilot requires exactly two target categories')
    if y is None:
        y = np.array([classes.index(r['label']) for r in rows],dtype=float)
    nuisance,content = arrays(rows)
    quires = np.array([r['quire'] for r in rows])
    folds = []
    for q in sorted(set(quires)):
        te = np.flatnonzero(quires==q)
        tr = np.flatnonzero(quires!=q)
        old_n = len(tr)
        if purge:
            test_tokens = {rows[i]['token'] for i in te}
            tr = np.array([i for i in tr if rows[i]['token'] not in test_tokens])
        if len(tr)<4 or len(set(y[tr]))!=2 or len(set(y[te]))!=2:
            raise ValueError('Every fixed train/test fold must retain both classes after purging')
        base = np.clip(ridge(nuisance[tr],y[tr],nuisance[te]),0,1)
        joint = np.clip(ridge(np.column_stack((nuisance,content))[tr],y[tr],
                              np.column_stack((nuisance,content))[te]),0,1)
        def balanced_brier(p):
            return float(np.mean([np.mean((p[y[te]==c]-c)**2) for c in (0,1)]))
        def balanced_accuracy(p):
            return float(np.mean([np.mean((p[y[te]==c]>=.5)==c) for c in (0,1)]))
        # Inverse prediction targets standardized shape features, not literal text.
        mu = content[tr].mean(0)
        sigma = np.maximum(content[tr].std(0),.01)
        target = (content-mu)/sigma
        inv0 = ridge(nuisance[tr],target[tr],nuisance[te])
        invx = np.column_stack((nuisance,y))
        inv1 = ridge(invx[tr],target[tr],invx[te])
        e0,e1 = float(np.mean((inv0-target[te])**2)),float(np.mean((inv1-target[te])**2))
        folds.append(dict(quire=str(q),test_n=len(te),train_n=len(tr),
            purged_identical_tokens=old_n-len(tr),
            nuisance_balanced_accuracy=balanced_accuracy(base),
            joint_balanced_accuracy=balanced_accuracy(joint),
            nuisance_brier=balanced_brier(base),joint_brier=balanced_brier(joint),
            forward_gain=balanced_brier(base)-balanced_brier(joint),
            inverse_nuisance_mse=e0,inverse_joint_mse=e1,inverse_gain=e0-e1))
    if len(folds)<2:
        raise ValueError('Need two or more grouped folds')
    return dict(forward_gain=float(np.mean([f['forward_gain'] for f in folds])),
                inverse_gain=float(np.mean([f['inverse_gain'] for f in folds])),folds=folds)


def strata(rows):
    groups = defaultdict(list)
    for i,r in enumerate(rows):
        # Exact token length preserved, same physical folio/Currier/hand.
        key=(r['folio'],r['currier'],r['hand'],len(r['token']))
        groups[key].append(i)
    return [groups[k] for k in sorted(groups)]


def run(rows, permutations=999, purge=True):
    if permutations < 1:
        raise ValueError('Need at least one permutation')
    classes=sorted({r['label'] for r in rows})
    if len(classes)!=2:
        raise ValueError('Need two categories')
    y=np.array([classes.index(r['label']) for r in rows],dtype=float)
    observed=evaluate(rows,y,purge)
    groups=strata(rows)
    eligible=sum(len(ix) for ix in groups if len(set(y[ix]))==2)
    rng=np.random.default_rng(SEED)
    null=[]; changed=[]
    for _ in range(permutations):
        yp=y.copy()
        for ix in groups:
            yp[ix]=rng.permutation(y[ix])
        changed.append(float(np.mean(yp!=y)))
        score=evaluate(rows,yp,purge)
        null.append((score['forward_gain'],score['inverse_gain']))
    null=np.array(null)
    p=[float((1+np.sum(null[:,j]>=observed[k]))/(permutations+1))
       for j,k in enumerate(('forward_gain','inverse_gain'))]
    positive_folds=all(f['forward_gain']>0 and f['inverse_gain']>0 for f in observed['folds'])
    # Both directions must pass: intersection-union, not Fisher combination.
    numerical_pass=bool(max(p)<=.01 and positive_folds and eligible>0)
    return dict(status='PASS_EXECUTED',classification='TWO_VIEW_METADATA_PILOT_NOT_TRANSLATION',
        n=len(rows),folios=len({r['folio'] for r in rows}),
        quires=sorted({r['quire'] for r in rows}),classes=dict(Counter(r['label'] for r in rows)),
        observed=observed,permutation=dict(completed=permutations,
            scheme='row labels within physical folio x Currier x hand x exact token length',
            exchangeable_rows=eligible,mean_changed_fraction=float(np.mean(changed)),
            forward_p=p[0],inverse_p=p[1],intersection_union_p=max(p),
            null_mean_gains=null.mean(0).tolist()),numerical_pilot_pass=numerical_pass,
        semantic_gate='BLOCKED',translation='NOT_RUN',
        reasons=['Lc/Lf are transcription metadata; independent visual annotation absent',
            'Known corpus and only two quires; no fresh confirmatory holdout',
            'Inverse predicts shapes, not literal strings or meanings',
            'Within-folio row exchangeability is assumed, not proved; positional dependence remains',
            'Renaming all category meanings leaves these numerical scores unchanged'])


def rename_witness(rows):
    classes=sorted({r['label'] for r in rows})
    renamed=[dict(r,label=f'ARBITRARY_{classes.index(r["label"])}') for r in rows]
    a,b=evaluate(rows),evaluate(renamed)
    delta=max(abs(a[k]-b[k]) for k in ('forward_gain','inverse_gain'))
    return dict(status='PASS_EXECUTED',max_gain_difference=delta,
        conclusion='Two-view association alone does not identify category meanings')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--corpus',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--permutations',type=int,default=999)
    a=ap.parse_args();raw=a.corpus.read_bytes()
    git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if git_blob!=SOURCE_BLOB:
        raise SystemExit('frozen corpus mismatch')
    rows=parse(raw.decode());result=run(rows,a.permutations)
    result['identifiability_witness']=rename_witness(rows)
    result['source_blob']=git_blob;result['seed']=SEED
    result['environment']=dict(python=platform.python_version(),numpy=np.__version__)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
