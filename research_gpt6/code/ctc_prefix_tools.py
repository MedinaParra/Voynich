"""Own log-space implementation of standard CTC prefix beam decoding."""
import math
import numpy as np

NEG=-math.inf


def validate(probabilities):
    p=np.asarray(probabilities,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]<1 or not np.isfinite(p).all() or (p<0).any():raise ValueError('Invalid probability matrix')
    if len(p) and not np.allclose(p.sum(axis=1),1,rtol=0,atol=1e-5):raise ValueError('Probabilities do not sum to one')
    return p


def logadd(a,b):
    if a==NEG:return b
    if b==NEG:return a
    return max(a,b)+math.log1p(math.exp(-abs(a-b)))


def collapse(path,blank=0):
    out=[];previous=None
    for c in path:
        c=int(c)
        if c!=blank and c!=previous:out.append(c)
        previous=c
    return tuple(out)


def greedy(probabilities,blank=0):
    p=validate(probabilities)
    return collapse(np.argmax(p,axis=1),blank)


def prefix_beam(probabilities,width=32,blank=0):
    p=validate(probabilities)
    if width<1 or not 0<=blank<p.shape[1]:raise ValueError('Invalid beam or blank')
    beam={():[0.,NEG]}
    for row in p:
        logs=[math.log(v) if v else NEG for v in row];nxt={}
        def add(prefix,kind,value):
            if value==NEG:return
            entry=nxt.setdefault(prefix,[NEG,NEG]);entry[kind]=logadd(entry[kind],value)
        for prefix,(pb,pnb) in beam.items():
            total=logadd(pb,pnb);add(prefix,0,total+logs[blank])
            for c,lp in enumerate(logs):
                if c==blank or lp==NEG:continue
                if prefix and prefix[-1]==c:
                    add(prefix,1,pnb+lp)
                    add(prefix+(c,),1,pb+lp)
                else:add(prefix+(c,),1,total+lp)
        ordered=sorted(nxt.items(),key=lambda kv:(-logadd(*kv[1]),kv[0]))[:width];beam=dict(ordered)
    return sorted([(prefix,logadd(*mass)) for prefix,mass in beam.items()],key=lambda x:(-x[1],x[0]))
