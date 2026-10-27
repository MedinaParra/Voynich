#!/usr/bin/env python3
"""Fixed spatial residual compensation; all held-out correspondences are scored."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageDraw


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=True, indent=2)+'\n')
def project(points, h):
    p = np.c_[np.asarray(points, dtype=float), np.ones(len(points))] @ np.asarray(h).T
    if np.any(np.abs(p[:, 2]) < 1e-12): raise ValueError('Projection at infinity')
    return p[:, :2]/p[:, 2:]
def block_colors(a, size):
    a = np.asarray(a); cells = np.clip(np.floor(a/np.array(size)*8).astype(int), 0, 7)
    return (cells[:, 0]+2*cells[:, 1]) % 5
def split_guarded(a, size, fold, guard):
    held = np.flatnonzero(block_colors(a, size) == fold)
    fit = np.flatnonzero(block_colors(a, size) != fold)
    if len(held):
        distances = np.linalg.norm(a[fit, None, :] - a[held][None, :, :], axis=2).min(axis=1)
        excluded = fit[distances <= guard]; fit = fit[distances > guard]
    else: excluded = np.array([], dtype=int)
    return fit, held, excluded


def fit_global(a, b, seed):
    import cv2
    cv2.setNumThreads(2); cv2.setRNGSeed(seed)
    if len(a) < 4: return None, np.zeros(len(a), dtype=bool)
    h, mask = cv2.findHomography(a, b, cv2.RANSAC, 3., maxIters=10000, confidence=.999)
    if h is None: return None, np.zeros(len(a), dtype=bool)
    return h, mask.ravel().astype(bool)


def anchors(a, b, h, opts):
    residuals = b-project(a, h)
    keep = np.linalg.norm(residuals, axis=1) <= opts['fit_residual_limit_yale_pixels']
    selected = np.flatnonzero(keep); locations = a[keep]; vectors = residuals[keep]
    if not len(locations): return np.empty((0, 2)), np.empty((0, 2)), selected
    keys, inverse = np.unique(np.rint(locations/opts['source_group_grid_pixels']).astype(np.int64), axis=0, return_inverse=True)
    sources = np.array([np.median(locations[inverse == i], axis=0) for i in range(len(keys))])
    deltas = np.array([np.median(vectors[inverse == i], axis=0) for i in range(len(keys))])
    return sources, deltas, selected


def corrections(query, source, vectors, opts):
    out = []; supports = []; capped = []
    for q in np.asarray(query):
        d = np.linalg.norm(source-q, axis=1)
        idx = np.argsort(d, kind='stable')
        idx = idx[d[idx] <= opts['radius_source_pixels']][:opts['maximum_neighbors']]
        supports.append(len(idx)); delta = np.zeros(2)
        if len(idx) >= opts['minimum_groups']: delta = np.median(vectors[idx], axis=0)
        norm = float(np.linalg.norm(delta)); cap = norm > opts['correction_limit_yale_pixels']
        if cap: delta *= opts['correction_limit_yale_pixels']/norm
        out.append(delta); capped.append(cap)
    return np.asarray(out), supports, capped


def measure(predicted, target):
    error = np.linalg.norm(predicted-target, axis=1)
    return error, {'points': len(error), 'median': float(np.median(error)), 'p90': float(np.percentile(error, 90)),
                   'maximum': float(error.max()), 'within_5_fraction': float((error <= 5).mean())}
def passes(metrics, inliers, span):
    return bool(metrics['points'] >= 10 and inliers >= 50 and min(span) >= .5
                and metrics['median'] <= 2 and metrics['p90'] <= 5 and metrics['within_5_fraction'] >= .8)
def positive_grid(mapped, shape):
    p = np.asarray(mapped).reshape(shape[1], shape[0], 2)
    crosses = []
    def cross(a, b): return a[0]*b[1]-a[1]*b[0]
    for y in range(shape[1]-1):
        for x in range(shape[0]-1):
            a, b, c, d = p[y, x], p[y, x+1], p[y+1, x+1], p[y+1, x]
            crosses.extend([cross(b-a, c-a), cross(c-a, d-a)])
    return bool(min(crosses) > 0), float(min(crosses))


def run(args):
    started = time.perf_counter(); plan = json.loads(args.plan.read_text()); args.out.mkdir(parents=True, exist_ok=True)
    def pinned(path_field, digest_field):
        p = args.repo/plan[path_field]
        if sha(p) != plan[digest_field]: raise ValueError('Frozen input changed: '+path_field)
        return json.loads(p.read_text())
    raw = pinned('correspondences_path', 'correspondences_sha256')
    previous = pinned('previous_result_path', 'previous_result_sha256')
    inputs = pinned('inputs_path', 'inputs_sha256'); pages = {p['folio']: p for p in inputs['pages']}
    if importlib.metadata.version('opencv-python-headless') != '4.12.0.88': raise ValueError('Changed OpenCV')
    if importlib.metadata.version('numpy') != '2.2.6': raise ValueError('Changed NumPy')
    opts = plan['local']; cases = []; pooled = {}
    for page_number, pair in enumerate(p for p in raw if p['correct_folio_pair']):
        folio = pair['source_folio']; a = np.array([p['source'] for p in pair['points']]); b = np.array([p['target'] for p in pair['points']])
        for fold in range(5):
            fit, held, excluded = split_guarded(a, pages[folio]['preview_size'], fold, plan['guard_source_pixels'])
            h, mask = fit_global(a[fit], b[fit], plan['seed']+fold)
            case = {'folio': folio, 'fold': fold, 'fit_indices': fit.tolist(), 'held_indices': held.tolist(),
                    'guard_excluded_indices': excluded.tolist(), 'conditions': {}}
            if h is None or not len(held):
                case['failure'] = 'No global fit or no held-out points'; cases.append(case)
                save(args.out/'cases.json', cases); continue
            inlier_indices = fit[mask]; span = (np.ptp(a[inlier_indices], axis=0)/np.array(pages[folio]['preview_size'])).tolist()
            source, vectors, selected = anchors(a[fit], b[fit], h, opts)
            order = np.random.default_rng(plan['seed']+1000*page_number+fold).permutation(len(source))
            base = project(a[held], h)
            real, support, capped = corrections(a[held], source, vectors, opts)
            shuffled, null_support, null_capped = corrections(a[held], source, vectors[order], opts)
            case.update({'matrix': h.tolist(), 'fit_inlier_indices': inlier_indices.tolist(), 'fit_inlier_span': span,
                         'local_anchor_groups': len(source), 'local_selected_fit_indices': fit[selected].tolist(),
                         'shuffle_order': order.tolist(), 'support_counts': support, 'capped': capped,
                         'shuffled_capped': null_capped})
            for method, pred in [('global', base), ('spatial_median', base+real), ('shuffled_median', base+shuffled)]:
                error, metrics = measure(pred, b[held])
                case['conditions'][method] = {'predictions': pred.tolist(), 'errors': error.tolist(), 'metrics': metrics,
                                               'accepted': passes(metrics, len(inlier_indices), span)}
            cases.append(case); save(args.out/'cases.json', cases)
        selected_cases = [c for c in cases if c['folio'] == folio]
        pooled[folio] = {}
        for method in ['global', 'spatial_median', 'shuffled_median']:
            if any(method not in c['conditions'] for c in selected_cases):
                pooled[folio][method] = None; continue
            errors = np.concatenate([c['conditions'][method]['errors'] for c in selected_cases])
            pooled[folio][method] = {'points': len(errors), 'median': float(np.median(errors)),
                                    'p90': float(np.percentile(errors, 90)), 'maximum': float(errors.max()),
                                    'within_5_fraction': float((errors <= 5).mean()),
                                    'accepted_folds': sum(c['conditions'][method]['accepted'] for c in selected_cases)}
    target_cases = [c for c in cases if c['folio'] == 'f4r']
    target = pooled['f4r']
    cv_accepted = bool(len(target_cases) == 5 and all(c.get('conditions', {}).get('spatial_median', {}).get('accepted', False) for c in target_cases)
                       and target['spatial_median']['p90'] < target['global']['p90']
                       and target['spatial_median']['p90'] < target['shuffled_median']['p90'])
    word_records = []; final_model = None; grid = None; accepted = False
    if cv_accepted:
        pair = next(p for p in raw if p['source_folio'] == 'f4r' == p['target_folio'])
        a = np.array([p['source'] for p in pair['points']]); b = np.array([p['target'] for p in pair['points']])
        h, mask = fit_global(a, b, plan['seed']+10000)
        if h is not None:
            source, vectors, _ = anchors(a, b, h, opts)
            def warp(q): return project(q, h)+corrections(q, source, vectors, opts)[0]
            width, height = pages['f4r']['preview_size']; shape = [17, 25]
            grid_source = np.array([[x, y] for y in np.linspace(0, height, shape[1]) for x in np.linspace(0, width, shape[0])])
            grid_mapped = warp(grid_source); orientation, minimum_area = positive_grid(grid_mapped, shape)
            grid = {'shape': shape, 'source': grid_source.tolist(), 'mapped': grid_mapped.tolist(),
                    'positive_orientation': orientation, 'minimum_double_triangle_area': minimum_area}
            calibration = np.array(previous['calibrations']['f4r']['matrix'])
            target_path = args.repo/pages['f4r']['yale_path']
            if sha(target_path) != pages['f4r']['yale_sha256']: raise ValueError('Frozen Yale image changed')
            with Image.open(target_path) as im: size = im.size
            for w in pages['f4r']['words']:
                x, y, ww, hh = w['xml_bbox']; flags = []; polygon = None
                if ww <= 0 or hh <= 0: flags.append('source_nonpositive_size')
                else:
                    polygon = warp(project([[x,y],[x+ww,y],[x+ww,y+hh],[x,y+hh]], calibration))
                    cross = []
                    for k in range(4):
                        u = polygon[(k+1)%4]-polygon[k]; v = polygon[(k+2)%4]-polygon[(k+1)%4]
                        cross.append(u[0]*v[1]-u[1]*v[0])
                    if min(cross) <= 0: flags.append('nonpositive_or_nonconvex_polygon')
                    if any(u < 0 or v < 0 or u > size[0] or v > size[1] for u, v in polygon): flags.append('outside_yale_frame')
                word_records.append({'folio': 'f4r', 'index': w['index'], 'eva': w['eva'], 'source_xml_bbox': w['xml_bbox'],
                                     'yale_polygon': None if polygon is None else polygon.tolist(), 'flags': flags,
                                     'reading_status': 'SOURCE_TRANSCRIPTION_NOT_EXPERT_REVIEWED'})
            accepted = bool(orientation and len(word_records) == 64 and all(not w['flags'] for w in word_records))
            final_model = {'global_matrix': h.tolist(), 'anchor_sources': source.tolist(), 'anchor_vectors': vectors.tolist(),
                           'calibration_matrix': calibration.tolist(), 'fit_uses_all_correspondences_after_cv': True,
                           'no_independent_score_claimed_for_final_fit': True, 'registration_accepted': accepted}
    if not accepted:
        for w in word_records: w['yale_polygon'] = None; w['flags'].append('final_geometry_or_validation_not_accepted')
    if accepted:
        with Image.open(args.repo/pages['f4r']['yale_path']) as im: out = im.convert('RGB')
        draw = ImageDraw.Draw(out)
        for w in word_records:
            p = [tuple(v) for v in w['yale_polygon']]; draw.line(p+[p[0]], fill='#009970', width=2); draw.text(p[0], str(w['index']), fill='#003fbb')
        out.thumbnail((1100, 1600)); out.save(args.out/'f4r_candidate_overlay.jpg', quality=92)
    result = {'date': plan['date'], 'status': 'F4R_GEOMETRIC_CANDIDATE_ACCEPTED_DEVELOPMENT_ONLY' if accepted else 'F4R_NOT_ACCEPTED_NO_NEW_WORDS',
              'plan_sha256': sha(args.plan), 'correspondences_sha256': plan['correspondences_sha256'],
              'cases': len(cases), 'conditions_per_case': 3, 'pooled': pooled, 'f4r_cross_validation_accepted': cv_accepted,
              'f4r_final_geometry_accepted': accepted, 'new_candidate_word_polygons': 64 if accepted else 0,
              'previous_280_candidates_modified': False, 'all_heldout_points_retained': True,
              'seconds': time.perf_counter()-started, 'run_id': os.getenv('GITHUB_RUN_ID'), 'execution_commit': os.getenv('GITHUB_SHA'),
              'environment': {k: importlib.metadata.version(k) for k in ['opencv-python-headless','numpy','pillow']},
              'scope': plan['scope'], 'expert_review': 'NOT_REVIEWED', 'new_ocr_training': 'NOT_RUN', 'translation': 'NOT_RUN'}
    save(args.out/'word_polygons.json', word_records); save(args.out/'final_model.json', final_model)
    save(args.out/'orientation_grid.json', grid); save(args.out/'result.json', result)
    print('LOCAL_REGISTRATION_RESULT='+json.dumps(result, ensure_ascii=True), flush=True)
    if not accepted: raise SystemExit(2)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--repo', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    run(p.parse_args())
