"""Deterministic two-view data intervention; never certifies a reading."""
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

from eva_unit_tools import read, sha, save, restore_and_load
from kraken_alignment_diagnostic import overlap_mask


def perturb(rgb, target_mask, shared_mask, identity, variant, seed, delta=40):
    rgb = np.asarray(rgb, dtype=np.uint8)
    target = np.asarray(target_mask, dtype=bool)
    shared = np.asarray(shared_mask, dtype=bool)
    if rgb.ndim != 3 or rgb.shape[2] != 3 or target.shape != rgb.shape[:2] or shared.shape != target.shape:
        raise ValueError('Inconsistent image/mask shapes')
    if not target.any() or (shared & ~target).any():
        raise ValueError('Empty target or shared pixels outside target')
    if variant not in ['repeat', 'random_ink', 'shared_ink']:
        raise ValueError('Unknown variant')
    gray = np.asarray(Image.fromarray(rgb).convert('L'))
    threshold = float(np.median(gray[target]))-delta
    dark = target & (gray <= threshold)
    eligible = dark & shared
    selected = np.zeros(target.shape, dtype=bool)
    n = int(eligible.sum())
    key = int.from_bytes(hashlib.sha256((str(seed)+'/'+identity).encode()).digest()[:8], 'big')
    if variant == 'shared_ink':
        selected = eligible.copy()
    elif variant == 'random_ink' and n:
        positions = np.flatnonzero(dark)
        choices = np.random.default_rng(key).choice(positions, size=n, replace=False)
        selected.flat[choices] = True
    paper = np.rint(np.median(rgb[target], axis=0)).astype(np.uint8)
    out = rgb.copy()
    out[selected] = ((rgb[selected].astype(np.uint16)+paper.astype(np.uint16)+1)//2).astype(np.uint8)
    if not np.array_equal(out[~selected], rgb[~selected]):
        raise ValueError('Perturbation changed unselected pixels')
    return out, selected, {'dark_threshold': threshold, 'dark_pixels': int(dark.sum()), 'shared_dark_pixels': n,
                            'selected_pixels': int(selected.sum()), 'selected_shared_pixels': int((selected & shared).sum()),
                            'changed_pixels': int(np.any(out != rgb, axis=2).sum()), 'paper_rgb': paper.tolist(),
                            'sample_seed': key, 'selected_array_sha256': hashlib.sha256(selected.tobytes()).hexdigest()}


def training_only(rows):
    selected = [r for r in rows if r['role'] in ['original_train', 'additional_train']]
    if {r['folio'][:-1] for r in selected} & {r['folio'][:-1] for r in rows if r['role'] in ['historical_development', 'reserved', 'fresh_reserved']}:
        raise ValueError('Physical-leaf leakage')
    return selected


def prepare_views(repo, plan, out, variant):
    all_rows, training, evaluation = restore_and_load(repo, plan)
    if [r['id'] for r in training_only(all_rows)] != [r['id'] for r in training]:
        raise ValueError('Changed training selection')
    path = repo/plan['geometry_reference_path']
    import gzip
    raw = path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix('.json.gz').read_bytes())
    if hashlib.sha256(raw).hexdigest() != plan['geometry_reference_sha256']:
        raise ValueError('Changed frozen overlap reference')
    expected = {r['id']: r for r in json.loads(raw)}
    masks = {}
    for r in training:
        with Image.open(r['mask_path']) as im:
            masks[r['id']] = (r['bounds'], np.asarray(im.convert('L')) > 0)
    images = (out/'training_images').resolve()
    images.mkdir(parents=True, exist_ok=True)
    selection = out/'selection_masks'
    selection.mkdir(parents=True, exist_ok=True)
    views, records = [], []
    for r in training:
        shared, neighbors = overlap_mask(masks[r['id']], [(s['id'], masks[s['id']]) for s in training if s['folio'] == r['folio'] and s['id'] != r['id']])
        if hashlib.sha256(shared.tobytes()).hexdigest() != expected[r['id']]['shared_mask_array_sha256']:
            raise ValueError('Overlap reconstruction mismatch '+r['id'])
        with Image.open(r['path']) as im:
            rgb = np.asarray(im.convert('RGB'))
        transformed, chosen, stats = perturb(rgb, masks[r['id']][1], shared, r['id'], variant, plan['seed'], plan['dark_median_delta'])
        if stats['shared_dark_pixels'] != expected[r['id']]['ink_proxies']['40']['shared_dark_pixels']:
            raise ValueError('Dark-pixel reference mismatch '+r['id'])
        mask_path = selection/(r['id']+'.png')
        Image.fromarray(chosen.astype(np.uint8)*255).save(mask_path)
        records.append({'id': r['id'], 'folio': r['folio'], 'reference': r['reference'], 'role': r['role'],
                        'image_sha256': r['image_sha256'], 'source_mask_sha256': r['mask_sha256'],
                        'selection_mask_path': str(mask_path.resolve()), 'selection_mask_sha256': sha(mask_path),
                        'overlap_array_sha256': expected[r['id']]['shared_mask_array_sha256'], 'neighbors': neighbors, **stats})
        for index in [0, 1]:
            identity = r['id']+'_v'+str(index)
            dest = images/(identity+'.png')
            if index == 0 or variant == 'repeat':
                shutil.copy2(r['path'], dest)
            else:
                Image.fromarray(transformed).save(dest)
            gt = dest.with_suffix('.gt.txt')
            gt.write_text(r['reference'])
            views.append({'id': identity, 'source_id': r['id'], 'view': index, 'folio': r['folio'], 'reference': r['reference'],
                          'path': str(dest), 'image_sha256': sha(dest), 'label_sha256': sha(gt)})
    if len(training) != plan['training_words'] or len(views) != plan['training_views']:
        raise ValueError('Changed view/training counts')
    save(out/'training_views.json', views)
    save(out/'perturbation_records.json', records)
    save(out/'preparation.json', {'variant': variant, 'training_words': len(training), 'training_views': len(views),
                                 'evaluation_used_for_intervention': False, 'label_changes': 0, 'geometry_changes': 0,
                                 'selected_pixels': sum(r['selected_pixels'] for r in records),
                                 'changed_pixels': sum(r['changed_pixels'] for r in records),
                                 'plan_source_model_sha256': plan['source_model_sha256'], 'expert_review': 'NOT_REVIEWED'})
    return views, records
