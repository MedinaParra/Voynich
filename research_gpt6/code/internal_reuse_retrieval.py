#!/usr/bin/env python3
"""Exploratory internal-image correspondence retrieval; never translates.

Hypotheses/visual pairs fixed in an explicit manifest before computing scores.
Literal and morphology retrieval are reported separately, with tie-aware ranks.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def sha_blob(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def clean_tokens(raw):
    raw=re.sub(r'<![^>]*>|<%>|<\$>','',raw)
    raw=raw.replace('<->','.')
    return [w for w in raw.split('.') if re.fullmatch('[a-z]{2,}',w)]


def parse(raw):
    pages={};labels=[];folio=None
    for line in raw.splitlines():
        p=re.match(r'^<([^>.,]+)>\s*<!([^>]*)>',line)
        if p:
            folio=p[1];meta=dict(re.findall(r'\$([A-Z])=([^\s>]+)',p[2]))
            pages[folio]=dict(folio=folio,quire=meta.get('Q','?'),currier=meta.get('L','?'),
                hand=meta.get('H','?'),section=meta.get('I','?'),tokens=[])
            continue
        m=re.match(r'^<([^>]+)>\s*(.*)$',line)
        if not m or ',' not in m[1]:continue
        locus,text=m.groups();fol=locus.split('.')[0];tag=locus.split(',',1)[1]
        if fol not in pages:continue
        toks=clean_tokens(text.strip())
        if tag[1:2]=='P':pages[fol]['tokens']+=toks
        if 'Lf' in tag:
            # Single literal unambiguous label, not fragments rescued from a bad token.
            literal=re.sub(r'<![^>]*>','',text).strip()
            number=re.search(r'<!([0-9]+[ab]?)>',text)
            if re.fullmatch('[a-z]{2,}',literal):
                labels.append(dict(locus=locus,token=literal,folio=fol,
                    fragment=number[1] if number else None,
                    currier=pages[fol]['currier'],hand=pages[fol]['hand']))
    return pages,labels


def tie_rank(scores,index):
    value=float(scores[index]);tol=1e-12
    better=int(np.sum(scores>value+tol))
    tied=int(np.sum(np.abs(scores-value)<=tol))
    return dict(rank_min=better+1,rank_max=better+tied,
        rank_mid=better+(tied+1)/2,score=value,
        fraction_strictly_better=better/len(scores))


def vector_scores(docs,queries):
    # No train/test claim: transductive TF-IDF fit on all candidate texts.
    v=TfidfVectorizer(analyzer='char_wb',ngram_range=(2,4),lowercase=False)
    x=v.fit_transform(docs)
    return cosine_similarity(v.transform(queries),x)


def run(corpus,manifest):
    if sha_blob(corpus)!=manifest['source_blob']:raise ValueError('Frozen source mismatch')
    pages,labels=parse(corpus.decode())
    matched=[];blocked=[]
    for a in manifest['anchors']:
        candidates=[l for l in labels if l['folio']==a['pharma'] and l['fragment']==a['fragment']]
        if len(candidates)!=1 or a['herbal'] not in pages:
            blocked.append(dict(anchor=a,reason='No unique literal Lf label and herbal folio'))
            continue
        label=candidates[0];page=pages[a['herbal']]
        docs=sorted([p for p in pages.values() if p['section']=='H' and len(p['tokens'])>=20
            and (p['currier'],p['hand'])==(page['currier'],page['hand'])],key=lambda p:p['folio'])
        pool=sorted([l for l in labels if (l['currier'],l['hand'])==
            (label['currier'],label['hand'])],key=lambda l:l['locus'])
        if not any(p['folio']==a['herbal'] for p in docs):
            blocked.append(dict(anchor=a,reason='Herbal folio absent from candidate pool'))
            continue
        scores=vector_scores([' '.join(p['tokens']) for p in docs],[label['token']])[0]
        i=next(i for i,p in enumerate(docs) if p['folio']==a['herbal'])
        reverse=vector_scores([l['token'] for l in pool],[' '.join(page['tokens'])])[0]
        j=next(i for i,l in enumerate(pool) if l['locus']==label['locus'])
        counts=Counter(page['tokens'])
        matches=[p['folio'] for p in docs if label['token'] in p['tokens']]
        matched.append(dict(anchor=a,label=label,
            exact_count_on_corresponding_herbal=counts[label['token']],
            herbal_candidates=len(docs),label_candidates=len(pool),
            exact_occurrence_on_other_herbals=matches,
            label_to_herbal=tie_rank(scores,i),herbal_to_label=tie_rank(reverse,j),
            top_herbal_candidates=[docs[k]['folio'] for k in np.argsort(-scores,kind='stable')[:5]],
            top_label_candidates=[pool[k]['locus'] for k in np.argsort(-reverse,kind='stable')[:5]]))
    unlabelled=[]
    for a in manifest['unlabelled_comparisons']:
        unlabelled.append(dict(anchor=a,has_literal_lf_label=any(l['folio']==a['pharma'] and
            l['fragment']==a['fragment'] for l in labels)))
    return dict(status='PASS_EXECUTED',classification='TENTATIVE_VISUAL_PAIR_RETRIEVAL_NOT_TRANSLATION',
        source_blob=sha_blob(corpus),pairs_scored=len(matched),pairs_blocked=blocked,
        exact_recurrence_pairs=sum(m['exact_count_on_corresponding_herbal']>0 for m in matched),
        comparisons=matched,unlabelled_comparisons=unlabelled,
        source_physical_leaves=sorted({re.match(r'f[0-9]+',m['anchor']['pharma'])[0] for m in matched}),
        visual_review_scope=manifest.get('visual_review_scope','No primary-image review recorded'),
        limitations=['Visual correspondences tentative; image review does not identify species or semantic roles',
            'Candidate texts reused from known corpus; transductive retrieval, no fresh holdout',
            'Repeated labels and score ties are retained; mid-ranks reported',
            'Two physical source leaves do not become independent samples by splitting panels',
            'No inferential p-value: query/pair dependence and selection are not calibrated',
            'Rare labels may be names, properties or procedures; exact absence does not refute all naming'],
        semantic_anchor='NOT_VALIDATED',translation='NOT_RUN',
        environment=dict(python=platform.python_version(),numpy=np.__version__))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--corpus',type=Path,required=True)
    ap.add_argument('--anchors',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();mraw=a.anchors.read_bytes();manifest=json.loads(mraw)
    result=run(a.corpus.read_bytes(),manifest)
    result['anchors_sha256']=hashlib.sha256(mraw).hexdigest()
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='comparisons'},indent=2))
    for r in result['comparisons']:
        print(r['anchor']['herbal'],r['label']['token'],r['exact_count_on_corresponding_herbal'],
            r['label_to_herbal']['rank_mid'],r['herbal_candidates'],
            r['herbal_to_label']['rank_mid'],r['label_candidates'])


if __name__=='__main__':main()
