#!/usr/bin/env python3
"""Acquire the fixed leaf8 reserve and apply the existing geometric gates."""
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import time
import traceback
from types import SimpleNamespace
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image
from eva_unit_tools import read, sha, save


def download(url):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Voynich-reproducible-research/1.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read(), response.status, response.headers.get('Content-Type')
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2**(attempt+1))


def prepare(a):
    import hashlib
    from prepare_kraken_expansion import prepare as geometry_prepare
    plan = read(a.plan)
    root = a.repo/plan['fresh_root']
    inputs = root/'inputs'
    inputs.mkdir(parents=True, exist_ok=True)
    receipts, pages = [], []
    metadata = {'plan_sha256': sha(a.plan), 'run_id': __import__('os').getenv('GITHUB_RUN_ID'),
                'execution_commit': __import__('os').getenv('GITHUB_SHA'), 'selected_folios': plan['fresh_folios'],
                'expert_review': 'NOT_REVIEWED', 'translation': 'NOT_RUN'}
    try:
        archive, status, content_type = download(plan['xml_archive_url'])
        if hashlib.sha256(archive).hexdigest() != plan['xml_archive_sha256']:
            raise ValueError('Frozen XML archive changed')
        receipts.append({'kind': 'xml_archive', 'url': plan['xml_archive_url'], 'sha256': hashlib.sha256(archive).hexdigest(),
                         'bytes': len(archive), 'http_status': status, 'content_type': content_type})
        z = zipfile.ZipFile(io.BytesIO(archive))
        for page in plan['fresh_pages']:
            folio = page['folio']
            record = {'folio': folio, 'role': 'reserved'}
            for key, suffix in [('json', '.js'), ('preview', '.jpg'), ('yale', '.jpg')]:
                url = page[key+'_url']
                data, status, content_type = download(url)
                path = inputs/(folio+'_'+key+suffix)
                path.write_bytes(data)
                digest = sha(path)
                if key == 'yale' and digest != page['yale_sha256']:
                    raise ValueError('Changed Yale source photograph '+folio)
                record[key+'_path'] = str(path.relative_to(a.repo))
                record[key+'_sha256'] = digest
                receipts.append({'folio': folio, 'kind': key, 'url': url, 'path': str(path.relative_to(a.repo)),
                                 'sha256': digest, 'bytes': len(data), 'http_status': status, 'content_type': content_type,
                                 'retrieved_utc': datetime.now(timezone.utc).isoformat()})
            xml = inputs/(folio+'.xml')
            xml.write_bytes(z.read('data/'+folio+'.xml'))
            if b'Apache License, Version 2.0' not in xml.read_bytes():
                raise ValueError('Source license header missing')
            original = ET.fromstring(xml.read_bytes()).findall('word')
            tokens, boxes = json.loads((a.repo/record['json_path']).read_text())
            if len(original) != len(boxes):
                raise ValueError('Source word segmentation changed '+folio)
            words = []
            for index, (box, word) in enumerate(zip(boxes, original)):
                text = tokens[box[0]][0]
                if index != int(word.attrib['index']) or text != (word.text or ''):
                    raise ValueError('Source transcription sequence changed '+folio)
                words.append({'index': index, 'eva': text, 'preview_bbox': box[1:]})
            record.update(xml_path=str(xml.relative_to(a.repo)), xml_sha256=sha(xml), words=words,
                          sequence_equal_to_licensed_xml=True, canvas_id=page['canvas_id'])
            for key in ['preview', 'yale']:
                with Image.open(a.repo/record[key+'_path']) as im:
                    record[key+'_size'] = list(im.size)
            pages.append(record)
        empty = inputs/'empty_previous_dataset.json'
        save(empty, [])
        geometry = dict(plan['geometry'])
        runtime_plan = {'seed': plan['seed'], 'additional_training_folios': [], 'reserved_folios': plan['fresh_folios'],
                        'previous_dataset_path': str(empty.relative_to(a.repo)), **geometry}
        runtime_path = inputs/'geometry_plan.json'
        save(runtime_path, runtime_plan)
        input_path = inputs/'acquired_inputs.json'
        save(input_path, {'plan_sha256': sha(runtime_path), 'parent_plan_sha256': sha(a.plan), 'pages': pages})
        save(inputs/'acquisition_receipts.json', receipts)
        geometry_prepare(SimpleNamespace(plan=runtime_path, inputs=input_path, repo=a.repo, out=root))
        # Canonical relative crop paths make the frozen dataset portable.
        dataset = read(root/'dataset.json')
        old_hash = sha(root/'dataset.json')
        for r in dataset:
            r['path'] = 'crops/'+Path(r['path']).name
            r['mask_path'] = 'crops/'+Path(r['mask_path']).name
        save(root/'dataset.json', dataset)
        geometric = read(root/'geometry_result.json')
        geometric['dataset_sha256_before_path_normalization'] = old_hash
        geometric['dataset_sha256'] = sha(root/'dataset.json')
        geometric['path_normalization_only'] = True
        save(root/'geometry_result.json', geometric)
        metadata.update(status='PASS_FRESH_GEOMETRY_CANDIDATES', dataset_sha256=sha(root/'dataset.json'),
                        words=len(dataset), characters=sum(len(r['reference']) for r in dataset),
                        folio_words={f: sum(r['folio'] == f for r in dataset) for f in plan['fresh_folios']})
    except Exception as error:
        metadata.update(status='BLOCKED_FRESH_GEOMETRY_NO_SUBSTITUTION', error=str(error), traceback=traceback.format_exc())
    save(inputs/'acquisition_receipts.json', receipts)
    save(root/'fresh_result.json', metadata)
    print('FRESH_RESERVE_RESULT='+json.dumps(metadata), flush=True)
    # A completed acquisition attempt is separate from passing the scientific gate.
    # The evaluator reports its primary criterion BLOCKED if either page failed.
    return metadata


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--repo', type=Path, required=True)
    prepare(p.parse_args())
