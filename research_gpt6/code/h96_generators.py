from collections import Counter, defaultdict
import numpy as np
from sklearn.cluster import KMeans
from h96_metrics import entropy

def draw(counter,rng):
    keys=list(counter); w=np.array([counter[k] for k in keys],float); w/=w.sum()
    return keys[int(rng.choice(len(keys),p=w))]

def char2(tokens,aliases=False):
    out=defaultdict(Counter)
    for token in tokens:
        body=[c+str(i%2) for i,c in enumerate(token)] if aliases else list(token)
        seq=['^','^']+body+['$']
        for i in range(2,len(seq)): out[(seq[i-2],seq[i-1])][seq[i]]+=1
    return out

def gen_char(model,rng,collapse=False):
    a=b='^'; out=[]
    for _ in range(30):
        choices=model.get((a,b))
        if not choices: break
        z=draw(choices,rng)
        if z=='$': break
        out.append(z[:-1] if collapse else z); a,b=b,z
    return ''.join(out) or 'aa'

def folio_features(corpus,order):
    ans={}
    for f in order:
        x=corpus[f]
        ans[f]=np.array([np.mean([len(t) for t in x]),len(set(x))/len(x),entropy(Counter(''.join(x)))])
    return ans

def fit_models(corpus,dev):
    toks=[t for f in dev for t in corpus[f]]; unig=Counter(toks); tm=defaultdict(Counter)
    for f in dev:
        x=corpus[f]
        for a,b in zip(['^']+x,x): tm[a][b]+=1
    slots=[[],[],[]]
    for t in toks:
        a=len(t)//3; b=2*len(t)//3
        slots[0].append(t[:a]); slots[1].append(t[a:b]); slots[2].append(t[b:])
    feats=folio_features(corpus,dev); matrix=np.asarray([feats[f] for f in dev])
    km=KMeans(n_clusters=2,random_state=96001,n_init=100).fit(matrix)
    states=[]
    for s in range(2): states.append(char2([t for f,label in zip(dev,km.labels_) if label==s for t in corpus[f]]))
    return {'unig':unig,'tm':tm,'char2':char2(toks),'slots':slots,'aliases':char2(toks,True),'centroids':km.cluster_centers_,'states':states}

def generate(name,model,counts,order,rng,features=None):
    result={}; unig=model['unig']; uk=list(unig); uw=np.array([unig[k] for k in uk],float); uw/=uw.sum()
    for f in order:
        n=counts[f]
        if name=='iid_unigram': arr=[uk[int(rng.choice(len(uk),p=uw))] for _ in range(n)]
        elif name=='token_markov1':
            arr=[]; prev='^'
            for _ in range(n):
                z=draw(model['tm'].get(prev,unig),rng); arr.append(z); prev=z
        elif name=='char_markov2': arr=[gen_char(model['char2'],rng) for _ in range(n)]
        elif name=='slot_resampler': arr=[''.join(pool[int(rng.integers(len(pool)))] for pool in model['slots']) or 'aa' for _ in range(n)]
        elif name=='homophonic_expansion': arr=[gen_char(model['aliases'],rng,True) for _ in range(n)]
        elif name=='folio_state_markov2':
            state=int(np.argmin(np.sum((model['centroids']-features[f])**2,axis=1)))
            arr=[gen_char(model['states'][state],rng) for _ in range(n)]
        else: raise ValueError(name)
        result[f]=arr
    return result
