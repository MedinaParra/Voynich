#!/usr/bin/env python3
"""Frozen integer character LM, using only public Apicius training books."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np

def build(public,out):
    data=json.loads((public/'training_corpus.json').read_text());out.mkdir(parents=True,exist_ok=True)
    counts=[np.zeros(26**n,dtype=np.int64) for n in range(1,5)]
    books=[]
    for book in data['books']:
        text=''.join(c for c in book['text'] if 'a'<=c<='z');a=np.frombuffer(text.encode(),dtype=np.uint8).astype(np.int64)-97
        for n in range(1,5):
            idx=np.zeros(len(a)-n+1,dtype=np.int64)
            for j in range(n):idx=idx*26+a[j:j+len(idx)]
            counts[n-1]+=np.bincount(idx,minlength=26**n)
        books.append({'source_path':book['source_path'],'letters':len(text),'letters_sha256':hashlib.sha256(text.encode()).hexdigest()})
    p=(counts[0]+.5)/(counts[0].sum()+13)
    for n,alpha in [(2,10),(3,5),(4,2)]:
        c=counts[n-1].reshape((26,)*n);back=np.broadcast_to(p, c.shape);p=(c+alpha*back)/(c.sum(axis=-1,keepdims=True)+alpha)
    table=np.rint(1000*np.log(p)).astype('<i4').ravel();table.tofile(out/'lm_int32.bin')
    thresholds=np.array([min(2**32,int(math.exp(-i/256)*2**32)) for i in range(8193)],dtype='<u8');thresholds.tofile(out/'accept_u64.bin')
    temps=np.array([round(30000*(200/30000)**(i/99)) for i in range(100)],dtype='<i4');temps.tofile(out/'temperatures_i32.bin')
    rank=sorted(range(26),key=lambda i:(-int(counts[0][i]),i));(out/'plain_frequency_rank.txt').write_text(' '.join(map(str,rank))+'\n')
    metadata={'books':books,'total_letters':sum(b['letters'] for b in books),'alphabet':'abcdefghijklmnopqrstuvwxyz','score':'sum integer conditional4gram log-score; first3letters unscored','quantization':1000,'backoff_strengths':[10,5,2],'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.iterdir() if p.is_file() and p.name!='model.json'}}
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n');print({'training_letters':metadata['total_letters'],'frozen_table_entries':len(table)})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--public',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();build(a.public,a.out)
