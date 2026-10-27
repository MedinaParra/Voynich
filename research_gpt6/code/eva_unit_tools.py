"""Reversible operational EVA grouping; these codes have no linguistic value."""
import gzip
import hashlib
import json
from pathlib import Path

GROUPS=('cfh','ckh','cph','cth','ch','sh')
PRIVATE={text:chr(0xE100+i) for i,text in enumerate(GROUPS)}
EXPAND={v:k for k,v in PRIVATE.items()}


def read(path):
    path=Path(path)
    return json.loads(path.read_text() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes()))


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n')


def encode(text,variant):
    if any(c<'a' or c>'z' for c in text):raise ValueError('Expected literal lowercase EVA')
    if variant=='reset_letters':return text
    if variant!='reset_groups':raise ValueError('Unknown condition')
    out=[];i=0
    while i<len(text):
        unit=next((g for g in GROUPS if text.startswith(g,i)),None)
        out.append(PRIVATE[unit] if unit else text[i]);i+=len(unit) if unit else 1
    return ''.join(out)


def expand(text,variant):
    if variant not in ['reset_letters','reset_groups']:raise ValueError('Unknown condition')
    out=[]
    for c in text:
        if 'a'<=c<='z':out.append(c)
        elif variant=='reset_groups' and c in EXPAND:out.append(EXPAND[c])
        else:raise ValueError('Prediction outside declared output units')
    return ''.join(out)


def restore_and_load(repo,plan):
    from audit_kraken_expansion import restore_inputs
    from retrain_kraken_expansion import select_rows
    repo=Path(repo);primary=repo/'results/kraken_expansion/primary_geometry';prepared=repo/'results/kraken_expansion/followup_prepared'
    restore_inputs(primary,prepared,repo)
    if sha(repo/plan['prepared_dataset_path'])!=plan['prepared_dataset_sha256']:raise ValueError('Changed fixed dataset')
    rows=read(repo/plan['prepared_dataset_path'])
    for r in rows:
        r['path']=str((prepared/'crops'/Path(r['path']).name).resolve());r['mask_path']=str((prepared/'crops'/Path(r['mask_path']).name).resolve())
        if sha(r['path'])!=r['image_sha256'] or sha(r['mask_path'])!=r['mask_sha256']:raise ValueError('Changed fixed crop')
    train,evaluation=select_rows(rows,'expanded_200')
    if len(train)!=442 or len(evaluation)!=282:raise ValueError('Changed partition')
    return rows,train,evaluation


def metrics(rows):
    if not rows:return None
    total=sum(len(r['reference']) for r in rows)
    return {method:{'errors':sum(r['errors'][method] for r in rows),'eva_characters':total,'cer':sum(r['errors'][method] for r in rows)/total,
                    'exact_words':sum(r['reference']==r['predictions'][method] for r in rows),'words':len(rows),
                    'exact_word_fraction':sum(r['reference']==r['predictions'][method] for r in rows)/len(rows)}
            for method in rows[0]['predictions']}


def slices(rows):
    out={}
    for role in ['historical_development','reserved']:
        selected=[r for r in rows if r['role']==role]
        out[role]={'all':metrics(selected),'seen':metrics([r for r in selected if r['seen_in_training']]),'unseen':metrics([r for r in selected if not r['seen_in_training']]),
                   'length_1_4':metrics([r for r in selected if len(r['reference'])<=4]),'length_5_6':metrics([r for r in selected if 5<=len(r['reference'])<=6]),'length_7_plus':metrics([r for r in selected if len(r['reference'])>=7])}
    return out
