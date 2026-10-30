#!/usr/bin/env python3
"""Prepare an unreviewed training-only queue; never changes source labels."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from kraken_alignment_diagnostic import read, save, digest, overlap_mask


def review_queue(dataset, geometry):
    by_id = {r['id']: r for r in geometry}
    queue = []
    for row in dataset:
        if row['role'] not in ['original_train', 'additional_train']:
            continue
        g = by_id[row['id']]
        if g['reference'] != row['reference'] or g['role'] != row['role']:
            raise ValueError('Queue metadata mismatch')
        queue.append({'id': row['id'], 'folio': row['folio'], 'role': row['role'],
                      'candidate_reference': row['reference'], 'source_image_path': row['source_image_path'],
                      'source_image_sha256': row['source_image_sha256'], 'bounds': row['bounds'], 'polygon': row['polygon'],
                      'image_sha256': row['image_sha256'], 'mask_sha256': row['mask_sha256'],
                      'shared_mask_fraction': g['shared_mask_fraction'],
                      'shared_dark_fraction_delta40': g['ink_proxies']['40']['shared_fraction'],
                      'neighbor_ids': [n['id'] for n in g['neighbors']], 'review_status': 'UNREVIEWED',
                      'approved_reference': None, 'approved_polygon': None})
    queue.sort(key=lambda r: (-(r['shared_dark_fraction_delta40'] if r['shared_dark_fraction_delta40'] is not None else 0), -r['shared_mask_fraction'], r['id']))
    for rank, row in enumerate(queue, 1):
        row['review_priority'] = rank
    return queue


def render(repo, bundle, out, count=12):
    dataset = read(repo/'results/kraken_expansion/followup_prepared/dataset.json')
    geometric = read(bundle/'geometry_rows.json')
    queue = review_queue(dataset, geometric)
    by_id = {r['id']: r for r in dataset}
    g_by_id = {r['id']: r for r in geometric}
    prepared = repo/'results/kraken_expansion/followup_prepared/crops'
    packet = {'status': 'PREPARED_UNREVIEWED_TRAINING_QUEUE',
              'selection': 'After exploratory diagnostic: descending shared-dark-pixel fraction at fixed median-minus-40 threshold, then shared-mask fraction and ID. Only training records; no OCR predictions used.',
              'reviewed_words': 0, 'label_changes': 0, 'geometry_changes': 0, 'words': len(queue),
              'preview_words': min(count, len(queue)), 'records': queue}
    save(out/'review_queue.json', packet)
    columns, cell_width, cell_height = 4, 310, 300
    shown = queue[:count]
    sheet = Image.new('RGB', (columns*cell_width, 70+((len(shown)+columns-1)//columns)*cell_height), '#f4f4f4')
    draw = ImageDraw.Draw(sheet)
    draw.text((12, 10), 'UNREVIEWED training candidates | original above; shared-mask overlay below', fill='black')
    draw.text((12, 32), 'Red marks annotation overlap, not ownership of ink. No corrected labels or new OCR.', fill='black')
    masks = {}
    def mask(identity):
        if identity not in masks:
            row = by_id[identity]
            with Image.open(prepared/Path(row['mask_path']).name) as im:
                masks[identity] = (row['bounds'], np.array(im.convert('L')) > 0)
        return masks[identity]
    for index, item in enumerate(shown):
        row = by_id[item['id']]
        path = prepared/Path(row['path']).name
        if digest(path.read_bytes()) != row['image_sha256']:
            raise ValueError('Changed preview input')
        with Image.open(path) as im:
            original = im.convert('RGB')
        shared, _ = overlap_mask(mask(item['id']), [(n['id'], mask(n['id'])) for n in g_by_id[item['id']]['neighbors']])
        pixels = np.asarray(original).copy()
        pixels[shared] = np.rint(.55*pixels[shared] + .45*np.array([255, 25, 25])).astype(np.uint8)
        overlay = Image.fromarray(pixels)
        x, y = (index % columns)*cell_width+8, 70+(index//columns)*cell_height
        draw.text((x, y), item['id']+' | '+item['candidate_reference'], fill='black')
        draw.text((x, y+17), 'mask %.1f%% | dark proxy %.1f%%' % (100*item['shared_mask_fraction'], 100*(item['shared_dark_fraction_delta40'] or 0)), fill='black')
        scale = min(290/original.width, 105/original.height)
        size = (max(1, round(original.width*scale)), max(1, round(original.height*scale)))
        sheet.paste(original.resize(size, Image.Resampling.NEAREST), (x, y+39))
        sheet.paste(overlay.resize(size, Image.Resampling.NEAREST), (x, y+158))
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(out/'training_review_preview.png')
    return packet


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    packet = render(a.repo, a.bundle, a.out)
    print({k: packet[k] for k in ['status', 'words', 'preview_words', 'reviewed_words', 'label_changes']})
