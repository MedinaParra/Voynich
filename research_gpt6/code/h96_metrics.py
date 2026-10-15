import hashlib, math, re
from collections import Counter, defaultdict
import numpy as np

def sha256(b): return hashlib.sha256(b).hexdigest()

def clean_tokens(text):
    clean=re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\]|@[0-9]+;', ' ', text).replace('?', ' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])', clean.lower())

def parse_corpus(raw):
    d=defaultdict(list)
    for line in raw.splitlines():
        m=re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m: continue
        fm=re.match(r'^(f\d+[rv]?)', m.group(1))
        if fm: d[fm.group(1)].extend(clean_tokens(m.group(2)))
    return {k:v for k,v in d.items() if len(v)>=20}

def entropy(cnt):
    n=sum(cnt.values())
    return 0.0 if not n else -sum((v/n)*math.log2(v/n) for v in cnt.values() if v)

def js(a,b):
    keys=set(a)|set(b); sa=sum(a.values()); sb=sum(b.values())
    if not sa or not sb: return 0.0
    pa={k:a.get(k,0)/sa for k in keys}; pb={k:b.get(k,0)/sb for k in keys}; pm={k:(pa[k]+pb[k])/2 for k in keys}
    def kl(p): return sum(v*math.log2(v/pm[k]) for k,v in p.items() if v and pm[k])
    return .5*(kl(pa)+kl(pb))

def corpus_stats(corpus, order):
    toks=[t for f in order for t in corpus[f]]; lens=[len(t) for t in toks]; chars=''.join(toks)
    prev=Counter(); pairs=Counter()
    for t in toks:
        s='^'+t+'$'
        for a,b in zip(s,s[1:]): prev[a]+=1; pairs[(a,b)]+=1
    total=sum(pairs.values()); cond=-sum((n/total)*math.log2(n/prev[a]) for (a,b),n in pairs.items())
    repeated=sum(a==b for a,b in zip(toks,toks[1:]))/max(1,len(toks)-1)
    halves=[]
    for f in order:
        x=corpus[f]; h=len(x)//2
        halves.append(js(Counter(''.join(x[:h])),Counter(''.join(x[h:]))))
    adjacent=[js(Counter(''.join(corpus[a])),Counter(''.join(corpus[b]))) for a,b in zip(order,order[1:])]
    return [float(np.mean(lens)),float(np.std(lens)),len(set(toks))/len(toks),entropy(Counter(chars)),cond,repeated,float(np.median(halves)),float(np.median(adjacent))]
