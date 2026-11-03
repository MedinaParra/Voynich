#!/usr/bin/env python3
"""Blind-input runner; accepts public packet and frozen model, never truth files."""
import argparse,hashlib,json,subprocess,time,platform
from pathlib import Path
import numpy as np


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(repo,bundle,binary,out):
    manifest=bundle/'solver_manifest.json';m=json.loads(manifest.read_text())
    for f in m['files']:assert sha(repo/f['path'])==f['sha256'],f['path']
    plan=json.loads((repo/'data/known_cipher_recovery_plan.json').read_text());cases=json.loads((bundle/'public/ciphertexts.json').read_text())['cases'];model=bundle/'model';lm=np.fromfile(model/'lm_int32.bin',dtype='<i4');out.parent.mkdir(parents=True,exist_ok=True)
    cache={};predictions=[];runs=[];started=time.perf_counter()
    for case in cases:
        cipher=case['ciphertext'];letters=''.join(c for c in cipher if 'a'<=c<='z');assert len(letters)==2000
        digest=hashlib.sha256(letters.encode()).hexdigest()
        if digest not in cache:
            work=out.parent/'search_inputs';work.mkdir(exist_ok=True);path=work/(digest+'.txt');path.write_text(letters+'\n');seed=int.from_bytes(bytes.fromhex(digest)[:8],'little')^plan['search']['seed']
            command=[str(binary.resolve()),str((model/'lm_int32.bin').resolve()),str((model/'accept_u64.bin').resolve()),str((model/'temperatures_i32.bin').resolve()),str((model/'plain_frequency_rank.txt').resolve()),str(path.resolve()),str(seed),str(plan['search']['restarts']),str(plan['search']['steps_per_restart']),'100']
            start=time.perf_counter();proc=subprocess.run(command,capture_output=True,text=True,check=True);result=json.loads(proc.stdout);key=result['key'];assert len(key)==26 and sorted(key)==list('abcdefghijklmnopqrstuvwxyz')
            plain=''.join(key[ord(c)-97] for c in letters);assert result['letters_plaintext']==plain
            indices=np.frombuffer(plain.encode(),dtype=np.uint8).astype(np.int64)-97;idx=np.zeros(len(indices)-3,dtype=np.int64)
            for j in range(4):idx=idx*26+indices[j:j+len(idx)]
            exact_score=int(lm[idx].astype(np.int64).sum());assert exact_score==result['score']
            record={'stream_sha256':digest,'seed':seed,'first_case':case['id'],**result};cache[digest]=record;runs.append(record)
            print(json.dumps({'case':case['id'],'unique_search':len(runs),'score':result['score'],'seconds':round(time.perf_counter()-start,3)}),flush=True)
        result=cache[digest];key=result['key'];plaintext=''.join(key[ord(c)-97] if 'a'<=c<='z' else c for c in cipher)
        predictions.append({'id':case['id'],'key':key,'plaintext':plaintext,'letters_plaintext':result['letters_plaintext'],'score':result['score'],'stream_sha256':digest,'run_first_case':result['first_case']})
    output={'solver_sha256':sha(manifest),'public_manifest_sha256':sha(bundle/'public/manifest.json'),'cases':predictions,'unique_runs':runs,'selection':'maximum frozen integer4gram LM score; no truth access; no posthoc rejection threshold','language_assumption':'Latin supplied as known, not inferred','Voynich_translation':'NOT_RUN'}
    out.write_text(json.dumps(output,indent=2)+'\n')
    runtime={'python':platform.python_version(),'numpy':np.__version__,'binary_sha256':sha(binary),'seconds':time.perf_counter()-started,'unique_searches':len(runs),'annealing_proposals':sum(r['annealing_proposals'] for r in runs),'polish_pair_checks':sum(r['polish_pair_checks'] for r in runs),'scope':'Runtime metadata not part of deterministic predictions'}
    (out.parent/'execution.json').write_text(json.dumps(runtime,indent=2)+'\n');print(json.dumps({'predictions_sha256':sha(out),**runtime}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--binary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.repo,a.bundle,a.binary,a.out)
