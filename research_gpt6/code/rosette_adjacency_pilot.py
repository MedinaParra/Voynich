"""Single-foldout exploratory association; NOT independent semantic validation."""
import argparse,hashlib,itertools,json,re
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

NAMES=['NW','NORTH','NE','EAST','SE','SOUTH','SW','WEST','CENTER']
EDGES=[(i,(i+1)%8) for i in range(8)]+[(i,8) for i in [1,3,5,7]]

def run(raw, permutations=9999):
    data=json.loads(raw)
    pairs=list(itertools.combinations(range(9),2))
    mask=np.array([tuple(sorted(p)) in {tuple(sorted(e)) for e in EDGES} for p in pairs])
    results=[]
    for mode in ['all','labels_only','ring_only']:
        texts=[];counts=[]
        for name in NAMES:
            words=[]
            for region,entry in data['entities'][name]['sub_regions'].items():
                if mode=='labels_only' and 'label' not in region: continue
                if mode=='ring_only' and region!='ring': continue
                for locus in entry['loci']:
                    if not locus.get('reviewed'): continue
                    # Use literal author-transcribed words; ignore speculative morphology/glosses.
                    words.extend(w['word'] for w in locus['words'] if re.fullmatch('[a-z]+',w['word']))
            texts.append(' '.join(words));counts.append(len(words))
        vec=CountVectorizer(analyzer='char',ngram_range=(2,3))
        sim=cosine_similarity(vec.fit_transform(texts))
        def contrast(order):
            s=np.array([sim[order[a],order[b]] for a,b in pairs])
            return float(s[mask].mean()-s[~mask].mean())
        obs=contrast(np.arange(9));rng=np.random.default_rng(408)
        null=np.array([contrast(rng.permutation(9)) for _ in range(permutations)])
        results.append({'mode':mode,'accepted_word_counts':dict(zip(NAMES,counts)),
            'connected_minus_unconnected_cosine':obs,
            'permutations':permutations,'one_sided_p':float((1+(null>=obs).sum())/(permutations+1)),
            'null_mean':float(null.mean())})
    for r in results: r['bonferroni_three_modes_p']=min(1,r['one_sided_p']*3)
    return {'status':'PASS_EXECUTED','classification':'SINGLE_FOLDOUT_EXPLORATORY_NOT_TRANSLATION',
        'source_sha256':hashlib.sha256(raw.encode()).hexdigest(),
        'physical_foldouts':1,'nodes':9,'connected_pairs':int(mask.sum()),
        'unconnected_pairs':int((~mask).sum()),'results':results,
        'limitations':['External topology unverified against Yale image in this execution',
        'Blindness of external annotation not established','Edges confounded with grid proximity',
        'Whole node texts permuted; lengths and textual roles not matched',
        'Text selection and topology chosen after inspecting source; exploratory',
        'Three modes share one physical diagram and are not replications']}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);args=ap.parse_args()
    print(json.dumps(run(args.input.read_text()),indent=2))
