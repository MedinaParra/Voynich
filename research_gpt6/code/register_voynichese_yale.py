#!/usr/bin/env python3
"""Two-stage geometric registration; mapped EVA words remain provisional."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n')
def project(points, matrix):
    p = np.c_[np.asarray(points, dtype=float), np.ones(len(points))] @ np.asarray(matrix, dtype=float).T
    if np.any(np.abs(p[:, 2]) < 1e-12): raise ValueError('Projection at infinity')
    return p[:, :2] / p[:, 2:]
def stats(values):
    if not len(values): return None
    a = np.asarray(values, dtype=float)
    return {'count': len(a), 'median': float(np.median(a)), 'p90': float(np.percentile(a, 90)),
            'maximum': float(a.max()), 'within_5_fraction': float((a <= 5).mean()),
            'within_6_fraction': float((a <= 6).mean())}
def word_holdout(folio, index):
    return int.from_bytes(hashlib.sha256((folio + ':' + str(index)).encode()).digest()[:8], 'big') % 5 == 0
def image_holdout(points, size):
    points = np.asarray(points); w, h = size
    cols = np.clip((points[:, 0] / w * 8).astype(int), 0, 7)
    rows = np.clip((points[:, 1] / h * 8).astype(int), 0, 7)
    return (cols + 2 * rows) % 5 == 0


def calibrate(page, plan):
    valid = [w for w in page['words'] if w['xml_bbox'][2] > 0 and w['xml_bbox'][3] > 0]
    old = np.array([[w['xml_bbox'][0] + w['xml_bbox'][2]/2, w['xml_bbox'][1] + w['xml_bbox'][3]/2] for w in valid])
    current = np.array([[w['preview_bbox'][0] + w['preview_bbox'][2]/2, w['preview_bbox'][1] + w['preview_bbox'][3]/2] for w in valid])
    held = np.array([word_holdout(page['folio'], w['index']) for w in valid], dtype=bool)
    cv2.setRNGSeed(plan['seed'])
    affine, inliers = cv2.estimateAffine2D(old[~held], current[~held], method=cv2.RANSAC,
                                          ransacReprojThreshold=3, maxIters=10000, confidence=.999, refineIters=10)
    if affine is None: return {'accepted': False, 'failure': 'No affine calibration', 'points': []}
    matrix = np.vstack([affine, [0, 0, 1]])
    errors = np.linalg.norm(project(old, matrix) - current, axis=1)
    held_stats = stats(errors[held]); train_inliers = int(inliers.sum())
    accepted = bool(train_inliers >= 20 and held.sum() >= 8 and held_stats['median'] <= 3
                    and held_stats['p90'] <= 6 and held_stats['within_6_fraction'] >= .8)
    points = [{'index': w['index'], 'xml_center': a.tolist(), 'preview_center': b.tolist(),
               'role': 'heldout' if hold else 'fit', 'error_preview_pixels': float(error)}
              for w, a, b, hold, error in zip(valid, old, current, held, errors)]
    naive = old / np.array(page['xml_frame']) * np.array(page['preview_size'])
    return {'accepted': accepted, 'matrix': matrix.tolist(), 'fit_rows': int((~held).sum()),
            'fit_inliers': train_inliers, 'heldout': held_stats, 'points': points,
            'naive_frame_scaling_heldout': stats(np.linalg.norm(naive[held] - current[held], axis=1)),
            'scope': 'Centers from two serializations of the same EVA tradition; not expert-independent annotations.'}


def match_images(source, target, source_size, plan):
    key_s, desc_s = source; key_t, desc_t = target
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    def filtered(a, b):
        if a is None or b is None or len(b) < 2: return {}
        found = {}
        for pair in matcher.knnMatch(a, b, k=2):
            if len(pair) == 2 and pair[0].distance < plan['ratio'] * pair[1].distance:
                found[pair[0].queryIdx] = pair[0].trainIdx
        return found
    forward = filtered(desc_s, desc_t); backward = filtered(desc_t, desc_s)
    matches = [(i, j) for i, j in sorted(forward.items()) if backward.get(j) == i]
    if len(matches) < 12:
        return {'accepted': False, 'failure': 'Fewer than 12 reciprocal ratio matches', 'matches': len(matches), 'points': []}
    a = np.array([key_s[i].pt for i, j in matches]); b = np.array([key_t[j].pt for i, j in matches])
    held = image_holdout(a, source_size)
    if (~held).sum() < 4:
        return {'accepted': False, 'failure': 'Fewer than four fit points', 'matches': len(matches), 'points': []}
    cv2.setRNGSeed(plan['seed'])
    matrix, inliers = cv2.findHomography(a[~held], b[~held], cv2.RANSAC, 3,
                                        maxIters=10000, confidence=.999)
    if matrix is None:
        return {'accepted': False, 'failure': 'No homography', 'matches': len(matches), 'points': []}
    errors = np.linalg.norm(project(a, matrix) - b, axis=1); held_stats = stats(errors[held])
    fitted_inliers = a[~held][inliers.ravel().astype(bool)]
    span = np.ptp(fitted_inliers, axis=0) / np.array(source_size) if len(fitted_inliers) else np.zeros(2)
    accepted = bool(len(fitted_inliers) >= 50 and held.sum() >= 10 and held_stats['median'] <= 2
                    and held_stats['p90'] <= 5 and held_stats['within_5_fraction'] >= .8 and np.all(span >= .5))
    return {'accepted': accepted, 'matrix': matrix.tolist(), 'matches': len(matches),
            'fit_matches': int((~held).sum()), 'fit_inliers': len(fitted_inliers),
            'fit_inlier_span_fraction': span.tolist(), 'heldout': held_stats,
            'points': [{'source': x.tolist(), 'target': y.tolist(), 'role': 'heldout' if hold else 'fit',
                        'error_yale_pixels': float(e)} for x, y, hold, e in zip(a, b, held, errors)]}


def mapped_words(page, matrix, size):
    words = []
    for w in page['words']:
        x, y, width, height = w['xml_bbox']; flags = []
        if width <= 0: flags.append('source_nonpositive_width')
        if height <= 0: flags.append('source_nonpositive_height')
        polygon = None
        if matrix is None: flags.append('registration_not_accepted')
        elif not flags:
            polygon = project([[x, y], [x+width, y], [x+width, y+height], [x, y+height]], matrix).tolist()
            if any(a < 0 or b < 0 or a > size[0] or b > size[1] for a, b in polygon): flags.append('outside_yale_frame')
        words.append({'folio': page['folio'], 'index': w['index'], 'eva': w['eva'],
                      'source_xml_bbox': w['xml_bbox'], 'yale_polygon': polygon, 'flags': flags,
                      'reading_status': 'SOURCE_TRANSCRIPTION_NOT_INDEPENDENTLY_REVIEWED'})
    return words


def overlay(target, words, out, detail=False):
    im = target.copy(); draw = ImageDraw.Draw(im)
    for w in words:
        if w['yale_polygon'] is None: continue
        p = [tuple(v) for v in w['yale_polygon']]
        draw.line(p + [p[0]], fill='red' if w['flags'] else '#009970', width=2)
        draw.text(p[0], str(w['index']), fill='#003fbb')
    if detail:
        polygons = [w['yale_polygon'] for w in words[:12] if w['yale_polygon']]
        if polygons:
            pts = np.array(polygons).reshape(-1, 2)
            im = im.crop((max(0, int(pts[:, 0].min())-15), max(0, int(pts[:, 1].min())-20),
                          min(im.width, int(pts[:, 0].max())+15), min(im.height, int(pts[:, 1].max())+35)))
    else: im.thumbnail((1100, 1600))
    out.parent.mkdir(parents=True, exist_ok=True); im.save(out, quality=92)


def run(args):
    started = time.perf_counter(); plan = json.loads(args.plan.read_text()); args.out.mkdir(parents=True, exist_ok=True)
    if importlib.metadata.version('opencv-python-headless') != '4.12.0.88': raise ValueError('Changed OpenCV version')
    if importlib.metadata.version('numpy') != '2.2.6': raise ValueError('Changed NumPy version')
    inputs_path = args.repo / plan['inputs_path']
    if sha(inputs_path) != plan['inputs_sha256']: raise ValueError('Frozen input metadata changed')
    data = json.loads(inputs_path.read_text()); cv2.setNumThreads(2)
    features_s = {}; features_t = {}; images_t = {}; calibrations = {}; sizes_s = {}; pages = data['pages']
    detector = cv2.SIFT_create(nfeatures=6000, contrastThreshold=.02)
    for page in pages:
        f = page['folio']; source = args.repo / page['preview_path']; target = args.repo / page['yale_path']
        if sha(source) != page['preview_sha256'] or sha(target) != page['yale_sha256']: raise ValueError('Frozen image changed: ' + f)
        with Image.open(source) as im: a = np.asarray(im.convert('RGB')); sizes_s[f] = im.size
        with Image.open(target) as im: images_t[f] = im.convert('RGB')
        b = np.asarray(images_t[f])
        features_s[f] = detector.detectAndCompute(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY), None)
        features_t[f] = detector.detectAndCompute(cv2.cvtColor(b, cv2.COLOR_RGB2GRAY), None)
        calibrations[f] = calibrate(page, plan)
    pairs = []; mapped = []; composed = {}
    for page in pages:
        for target_page in pages:
            source_folio = page['folio']; target_folio = target_page['folio']
            row = match_images(features_s[source_folio], features_t[target_folio], sizes_s[source_folio], plan)
            pairs.append({'source_folio': source_folio, 'target_folio': target_folio,
                          'correct_folio_pair': source_folio == target_folio, **row})
        same = next(p for p in pairs if p['source_folio'] == page['folio'] == p['target_folio'])
        matrix = None
        if same['accepted'] and calibrations[page['folio']]['accepted']:
            matrix = np.array(same['matrix']) @ np.array(calibrations[page['folio']]['matrix'])
            matrix /= matrix[2, 2]
        composed[page['folio']] = None if matrix is None else matrix.tolist()
        words = mapped_words(page, matrix, images_t[page['folio']].size); mapped.extend(words)
        overlay(images_t[page['folio']], words, args.out / 'overlays' / (page['folio'] + '.jpg'))
        overlay(images_t[page['folio']], words, args.out / 'overlays' / (page['folio'] + '_detail.jpg'), detail=True)
    accepted_correct = sum(p['accepted'] and p['correct_folio_pair'] for p in pairs)
    accepted_wrong = sum(p['accepted'] and not p['correct_folio_pair'] for p in pairs)
    accepted_calibrations = sum(c['accepted'] for c in calibrations.values())
    accepted_all = accepted_correct == 4 and accepted_wrong == 0 and accepted_calibrations == 4
    result = {'status': 'PASS_GEOMETRIC_DEVELOPMENT_CHECKS_WORDS_PROVISIONAL' if accepted_all else 'FAIL_SOME_REGISTRATION_CHECKS',
              'date': plan['date'], 'execution': 'GITHUB_ACTIONS_CPU_NO_KRAKEN_TRAINING' if os.getenv('GITHUB_RUN_ID') else 'LOCAL_CPU_NO_KRAKEN_TRAINING',
              'run_id': os.getenv('GITHUB_RUN_ID'), 'execution_commit': os.getenv('GITHUB_SHA'), 'plan_sha256': sha(args.plan),
              'input_metadata_sha256': sha(inputs_path), 'accepted_correct_image_pairs': accepted_correct,
              'accepted_wrong_image_pairs': accepted_wrong, 'wrong_image_pairs_attempted': 12,
              'accepted_calibrations': accepted_calibrations, 'calibrations': calibrations,
              'pairs': [{k: v for k, v in p.items() if k != 'points'} for p in pairs],
              'composed_xml_to_yale': composed, 'source_words': len(mapped),
              'words_with_candidate_polygons': sum(w['yale_polygon'] is not None for w in mapped),
              'word_geometry_flags': dict(Counter(flag for w in mapped for flag in w['flags'])),
              'seconds': time.perf_counter() - started,
              'environment': {k: importlib.metadata.version(k) for k in ['opencv-python-headless', 'numpy', 'pillow']},
              'scope': plan['scope'], 'boxer_eva_alignment': 'NOT_RUN', 'new_expert_review': 'NOT_REVIEWED',
              'new_recognition_training': 'NOT_RUN', 'translation': 'NOT_RUN'}
    save(args.out / 'correspondences.json', pairs); save(args.out / 'word_polygons.json', mapped)
    save(args.out / 'result.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ['calibrations', 'pairs', 'composed_xml_to_yale']}, ensure_ascii=True))
    if not accepted_all: raise SystemExit(2)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--repo', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    run(p.parse_args())
