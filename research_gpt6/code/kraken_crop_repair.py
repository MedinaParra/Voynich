#!/usr/bin/env python3
"""Provisional row ownership: preserve weak-contrast components without duplication.

Inputs include old operator row boxes. This is NOT autonomous segmentation.
Foreground conservation is relative to a contrast proxy, not expert ink truth.
"""
import math
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, label, uniform_filter

from kraken_crop_quality import paragraph_mask, rect


def find_anchors(dark, rows, size, minimum_pitch_fraction=.5, center_penalty=.25):
    """Jointly choose distinct ink-density anchors, constrained by old row boxes."""
    w, h = size
    anchors = np.zeros(len(rows), dtype=float)
    for paragraph in sorted({r['paragraph'] for r in rows}):
        indices = [i for i, r in enumerate(rows) if r['paragraph'] == paragraph]
        boxes = [rect(rows[i]['bbox'], size) for i in indices]
        centers = np.array([(b[1] + b[3]) / 2 for b in boxes])
        if len(centers) > 1 and np.any(np.diff(centers) <= 0):
            raise ValueError('Indistinguishable or unordered row guides')
        pitch = float(np.median(np.diff(centers))) if len(centers) > 1 else max(1, boxes[0][3] - boxes[0][1])
        gap = max(1, int(pitch * minimum_pitch_fraction))
        scores = []
        yy = np.arange(h)
        for b, center in zip(boxes, centers):
            profile = dark[:, b[0]:b[2]].sum(axis=1).astype(float)
            score = np.log1p(profile) - center_penalty * ((yy - center) / max(1, pitch)) ** 2
            score[(yy < b[1]) | (yy >= b[3])] = -np.inf
            scores.append(score)
        previous = scores[0].copy()
        back = []
        for score in scores[1:]:
            best = np.maximum.accumulate(previous)
            arg = np.zeros(h, dtype=np.int32)
            current_arg = 0
            for y in range(h):
                if previous[y] > previous[current_arg]:
                    current_arg = y
                arg[y] = current_arg
            shifted = np.full(h, -np.inf)
            shifted[gap:] = best[:-gap]
            bp = np.full(h, -1, dtype=np.int32)
            bp[gap:] = arg[:-gap]
            previous = score + shifted
            back.append(bp)
        if not np.isfinite(previous).any():
            raise ValueError('No feasible ordered row anchors')
        chosen = [int(np.argmax(previous))]
        for bp in reversed(back):
            chosen.append(int(bp[chosen[-1]]))
        for idx, y in zip(indices, reversed(chosen)):
            anchors[idx] = y
    return anchors


def repair(im, rows, regions, opts):
    rgb = np.asarray(im.convert('RGB'))
    gray = np.asarray(im.convert('L'), dtype=float) / 255
    contrast = uniform_filter(gray, size=31, mode='reflect') - gray
    valid = paragraph_mask(im.size, regions)
    h, w = gray.shape
    bounds = [rect(r['bbox'], im.size) for r in rows]
    coverage = np.zeros((h, w), dtype=np.uint16)
    for x0, y0, x1, y1 in bounds:
        coverage[y0:y1, x0:x1] += 1
    domain = valid & (coverage > 0)
    dark = (contrast >= opts['ownership_delta']) & domain
    anchors = find_anchors(dark, rows, im.size, opts['minimum_pitch_fraction'], opts['center_penalty'])
    owner = np.full((h, w), -1, dtype=np.int16)
    best = np.full((h, w), np.inf, dtype=np.float32)
    for i, (x0, y0, x1, y1) in enumerate(bounds):
        distance = np.abs(np.arange(y0, y1)[:, None] - anchors[i])
        change = domain[y0:y1, x0:x1] & (distance < best[y0:y1, x0:x1])
        owner[y0:y1, x0:x1][change] = i
        best[y0:y1, x0:x1][change] = np.broadcast_to(distance, change.shape)[change]
    components, n_components = label(dark, structure=np.ones((3, 3), dtype=np.uint8))
    votes = np.bincount(components[dark].astype(np.int64) * len(rows) + owner[dark], minlength=(n_components + 1) * len(rows)).reshape(-1, len(rows))
    winner = votes.argmax(axis=1)
    totals = votes.sum(axis=1)
    dominant = np.divide(votes.max(axis=1), totals, out=np.ones_like(totals, dtype=float), where=totals > 0)
    ambiguous = (dominant < opts['component_dominance_review_threshold']) & (totals >= opts['minimum_component_review_area'])
    ambiguous[0] = False
    owner[dark] = winner[components[dark]]
    # Give nearby anti-aliased pixels to the same owner while retaining exclusivity.
    if dark.any():
        distance, nearest = distance_transform_edt(~dark, return_indices=True)
        halo = (distance <= opts['halo_pixels']) & domain
        nearest_owner = owner[nearest[0], nearest[1]]
        owner[halo] = nearest_owner[halo]
    repaired = []
    rendered_coverage = np.zeros((h, w), dtype=np.uint16)
    for i, row in enumerate(rows):
        ink = dark & (owner == i)
        if not ink.any():
            raise ValueError('No foreground remains for row ' + row['id'])
        yy, xx = np.where(ink)
        pad = opts['crop_padding_pixels']
        x0, y0 = max(0, int(xx.min()) - pad), max(0, int(yy.min()) - pad)
        x1, y1 = min(w, int(xx.max()) + pad + 1), min(h, int(yy.max()) + pad + 1)
        keep = (owner[y0:y1, x0:x1] == i) & domain[y0:y1, x0:x1]
        crop = rgb[y0:y1, x0:x1].copy()
        crop[~keep] = 255
        rendered_coverage[y0:y1, x0:x1] += keep
        component_ids = np.unique(components[ink])
        flags = [int(k) for k in component_ids if ambiguous[k]]
        repaired.append({'id': row['id'], 'image': Image.fromarray(crop), 'mask': keep,
                         'bounds': [x0, y0, x1, y1], 'anchor_y': float(anchors[i]),
                         'dark_positions': int(ink.sum()), 'ambiguous_component_ids': flags})
    metrics = {}
    for delta in [.06, .10, .14]:
        candidate = (contrast >= delta) & domain
        n = int(candidate.sum())
        repeated_before = int((candidate & (coverage > 1)).sum())
        repeated_after = int((candidate & (rendered_coverage > 1)).sum())
        lost = int((candidate & (rendered_coverage == 0)).sum())
        metrics[f'{delta:.2f}'] = {'positions_before': n, 'repeated_before': repeated_before,
            'repeated_after': repeated_after, 'lost_candidate_positions': lost,
            'repeated_fraction_before': repeated_before / n if n else None,
            'repeated_fraction_after': repeated_after / n if n else None,
            'retained_fraction': (n - lost) / n if n else None}
        if repeated_after or lost:
            raise ValueError('Ownership export violates foreground conservation')
    diagnostics = {'metrics': metrics, 'components': n_components,
                   'ambiguous_components': int(ambiguous.sum()),
                   'rows_with_ambiguous_components': sum(bool(r['ambiguous_component_ids']) for r in repaired),
                   'component_dominance_threshold': opts['component_dominance_review_threshold'],
                   'status': 'REVIEW_REQUIRED_NOT_EXPERT_VALIDATED',
                   'limits': ['Zero duplicate positions is enforced by construction, not a recognition score.',
                              'Conservation concerns contrast candidates inside the old crop union only.',
                              'A component can connect multiple lines; ownership can be wrong despite conservation.',
                              'Old row/text associations remain provisional assistant annotations.']}
    return repaired, diagnostics


def contact_sheet(original, repaired, texts, path):
    from PIL import ImageFont
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    width, cellheight = 1600, 150
    sheet = Image.new('RGB', (width, cellheight * len(repaired)), '#f5f7f8')
    d = ImageDraw.Draw(sheet)
    for i, row in enumerate(repaired):
        d.text((10, i * cellheight + 3), row['id'] + ' | original / ownership repair | ' + texts[row['id']], fill='black', font=font)
        for j, im in enumerate([original[row['id']], row['image']]):
            thumb = im.copy(); thumb.thumbnail((780, 113))
            sheet.paste(thumb, (10 + j * 800, i * cellheight + 30))
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path, quality=88)
