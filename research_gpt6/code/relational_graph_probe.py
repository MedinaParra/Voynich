"""Frozen pilot: does text improve prediction of independently annotated edges?

Input JSON: list of folios, each with folio, quire, nodes [{id,text,x,y}],
edges [[id,id]], annotation_blind=true, edges_complete=true.
Coordinates must be normalized to the image; edges are undirected.
One folio is one physical diagram, not a text paragraph.
"""
import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import HashingVectorizer


def validate(graphs):
    if len({g['quire'] for g in graphs}) < 3:
        raise ValueError('Need at least three independent quires; one foldout cannot validate transfer')
    if len({g['folio'] for g in graphs}) != len(graphs):
        raise ValueError('Duplicate physical folios')
    for g in graphs:
        if g.get('annotation_blind') is not True or g.get('edges_complete') is not True:
            raise ValueError('Need complete visual edges annotated without seeing text')
        ids = [n['id'] for n in g['nodes']]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate node IDs')
        for n in g['nodes']:
            if not (0 <= n['x'] <= 1 and 0 <= n['y'] <= 1):
                raise ValueError('Coordinates must be image-normalized')
        if any(a not in ids or b not in ids or a == b for a,b in g['edges']):
            raise ValueError('Invalid edge endpoints')


def matrix(graphs, rng=None):
    h = HashingVectorizer(analyzer='char', ngram_range=(1,3), n_features=64,
                          alternate_sign=False, norm='l2')
    geo, joint, ys, qs = [], [], [], []
    for g in graphs:
        nodes = g['nodes']
        texts = [n['text'] for n in nodes]
        # Entire labels move within physical folio; coordinates and edge truth stay fixed.
        if rng is not None:
            rng.shuffle(texts)
        z = h.transform(texts).toarray()
        edges = {frozenset(e) for e in g['edges']}
        for i,j in itertools.combinations(range(len(nodes)),2):
            a,b = nodes[i],nodes[j]
            dx,dy = abs(a['x']-b['x']),abs(a['y']-b['y'])
            lengths = sorted([len(texts[i]),len(texts[j])])
            base = [dx,dy,(dx*dx+dy*dy)**.5,*[v/30 for v in lengths]]
            geo.append(base)
            joint.append(base + list(abs(z[i]-z[j])) + list(z[i]*z[j]))
            ys.append(int(frozenset([a['id'],b['id']]) in edges))
            qs.append(g['quire'])
    return np.array(geo),np.array(joint),np.array(ys),np.array(qs)


def score(graphs, rng=None):
    geo,joint,y,q = matrix(graphs,rng)
    folds=[]
    for held in sorted(set(q)):
        train,test = q != held,q == held
        if len(set(y[train])) != 2 or len(set(y[test])) != 2:
            raise ValueError('Every train/test fold needs both edge classes')
        errors=[]
        for x in [geo,joint]:
            model=LogisticRegression(C=1.0,max_iter=1000,random_state=408)
            model.fit(x[train],y[train])
            p=model.predict_proba(x[test])[:,1]
            errors.append(float(np.mean((p-y[test])**2)))
        folds.append({'quire':held,'pairs':int(sum(test)),
                      'geometry_brier':errors[0],'joint_brier':errors[1],
                      'gain':errors[0]-errors[1]})
    return float(np.mean([f['gain'] for f in folds])),folds


def run(graphs,permutations):
    validate(graphs)
    observed,folds=score(graphs)
    rng=random.Random(408)
    null=[score(graphs,rng)[0] for _ in range(permutations)]
    return {'status':'PASS_EXECUTED','classification':'RELATIONAL_PILOT_NOT_TRANSLATION',
            'mean_quire_brier_gain':observed,'folds':folds,
            'permutations':permutations,
            'monte_carlo_p':(1+sum(v>=observed for v in null))/(1+len(null)),
            'positive_all_folds':all(f['gain']>0 for f in folds),
            'warning':'Exploratory; a graph association does not identify meanings or language'}


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('input',type=Path)
    ap.add_argument('--permutations',type=int,default=199)
    args=ap.parse_args()
    if args.permutations < 1:
        ap.error('permutations must be positive')
    raw=args.input.read_bytes()
    graphs=json.loads(raw)
    try:
        result=run(graphs,args.permutations)
    except ValueError as e:
        result={'status':'BLOCKED','reason':str(e)}
    result['input_sha256']=hashlib.sha256(raw).hexdigest()
    print(json.dumps(result,indent=2))
