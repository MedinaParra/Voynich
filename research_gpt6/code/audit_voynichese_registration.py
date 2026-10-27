#!/usr/bin/env python3
"""Audit frozen source records and exported geometry without importing OpenCV."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image


def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def apply(points, matrix):
    matrix = np.asarray(matrix); p = np.asarray(points)
    d = matrix[2, 0]*p[:, 0] + matrix[2, 1]*p[:, 1] + matrix[2, 2]
    return np.c_[(matrix[0, 0]*p[:, 0] + matrix[0, 1]*p[:, 1] + matrix[0, 2])/d,
                 (matrix[1, 0]*p[:, 0] + matrix[1, 1]*p[:, 1] + matrix[1, 2])/d]


def audit(bundle, repo):
    plan_path = repo/'data/voynichese_registration_plan.json'; plan = read(plan_path)
    input_path = repo/plan['inputs_path']; data = read(input_path); result = read(bundle/'result.json')
    pairs = read(bundle/'correspondences.json'); words = read(bundle/'word_polygons.json')
    checks = 0; mismatches = []
    def check(name, actual, expected=True):
        nonlocal checks
        checks += 1
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            equal = math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-6)
        elif isinstance(actual, np.ndarray) or isinstance(expected, np.ndarray):
            equal = bool(np.allclose(actual, expected, rtol=1e-9, atol=1e-6))
        else: equal = actual == expected
        if not equal: mismatches.append({'check': name, 'actual': actual.tolist() if isinstance(actual, np.ndarray) else actual,
                                         'expected': expected.tolist() if isinstance(expected, np.ndarray) else expected})
    def check_stats(name, stored, errors):
        errors = np.asarray(errors)
        if not len(errors): check(name, stored, None); return
        values = {'count': len(errors), 'median': float(np.median(errors)), 'p90': float(np.percentile(errors, 90)),
                  'maximum': float(errors.max()), 'within_5_fraction': float((errors <= 5).mean()),
                  'within_6_fraction': float((errors <= 6).mean())}
        for key, value in values.items(): check(name+'/'+key, stored[key], value)
    check('plan_hash', result['plan_sha256'], sha(plan_path))
    check('input_hash', result['input_metadata_sha256'], sha(input_path))
    check('pinned_input_hash', plan['inputs_sha256'], sha(input_path))
    pages = {p['folio']: p for p in data['pages']}; feature_errors = {}; calibration_errors = {}
    check('all_sixteen_pairs', sorted((p['source_folio'], p['target_folio']) for p in pairs), sorted(itertools.product(pages, repeat=2)))
    for f, page in pages.items():
        for field, expected in [('preview_path', 'preview_sha256'), ('yale_path', 'yale_sha256'),
                                ('xml_path', 'xml_sha256'), ('preview_data_path', 'preview_data_sha256')]:
            check(f+'/'+field, sha(repo/page[field]), page[expected])
        xml = ET.fromstring((repo/page['xml_path']).read_bytes()); current = read(repo/page['preview_data_path'])
        check(f+'/xml_frame', [int(xml.attrib['width']), int(xml.attrib['height'])], page['xml_frame'])
        xwords = xml.findall('word')
        check(f+'/word_count_xml', len(xwords), len(page['words']))
        check(f+'/word_count_preview', len(current[1]), len(page['words']))
        for source, newer, w in zip(xwords, current[1], page['words']):
            label = f+'/'+str(w['index'])
            check(label+'/index', int(source.attrib['index']), w['index'])
            check(label+'/xml_text', source.text, w['eva'])
            check(label+'/preview_text', current[0][newer[0]][0], w['eva'])
            check(label+'/xml_box', [int(source.attrib[k]) for k in ['x', 'y', 'width', 'height']], w['xml_bbox'])
            check(label+'/preview_box', newer[1:], w['preview_bbox'])
        cal = result['calibrations'][f]
        valid = {w['index']: w for w in page['words'] if w['xml_bbox'][2] > 0 and w['xml_bbox'][3] > 0}
        if 'matrix' not in cal:
            check(f+'/failed_calibration_not_accepted', cal['accepted'], False); continue
        check(f+'/calibration_point_count', len(cal['points']), len(valid))
        a = []; b = []; held = []
        for pt in cal['points']:
            w = valid[pt['index']]; x, y, width, height = w['xml_bbox']; u, v, ww, hh = w['preview_bbox']
            check(f+'/cal_source/'+str(pt['index']), pt['xml_center'], [x+width/2, y+height/2])
            check(f+'/cal_target/'+str(pt['index']), pt['preview_center'], [u+ww/2, v+hh/2])
            hold = int.from_bytes(hashlib.sha256((f+':'+str(pt['index'])).encode()).digest()[:8], 'big') % 5 == 0
            check(f+'/cal_role/'+str(pt['index']), pt['role'], 'heldout' if hold else 'fit')
            a.append(pt['xml_center']); b.append(pt['preview_center']); held.append(hold)
        a = np.array(a); b = np.array(b); held = np.array(held)
        errors = np.sqrt(((apply(a, cal['matrix'])-b)**2).sum(axis=1))
        for pt, error in zip(cal['points'], errors): check(f+'/cal_error/'+str(pt['index']), pt['error_preview_pixels'], float(error))
        check_stats(f+'/cal_heldout', cal['heldout'], errors[held])
        naive = a/np.array(page['xml_frame'])*np.array(page['preview_size'])
        check_stats(f+'/cal_naive', cal['naive_frame_scaling_heldout'], np.linalg.norm(naive[held]-b[held], axis=1))
        accepted = bool(cal['fit_inliers'] >= 20 and held.sum() >= 8 and np.median(errors[held]) <= 3
                        and np.percentile(errors[held], 90) <= 6 and (errors[held] <= 6).mean() >= .8)
        check(f+'/cal_gate', cal['accepted'], accepted)
        calibration_errors[f] = {'heldout_points': int(held.sum()), 'median_preview_pixels': float(np.median(errors[held])),
                                 'p90_preview_pixels': float(np.percentile(errors[held], 90)), 'accepted': accepted}
    for pair in pairs:
        f = pair['source_folio']; t = pair['target_folio']; label = f+'->'+t
        check(label+'/pair_identity', pair['correct_folio_pair'], f == t)
        if 'matrix' not in pair:
            check(label+'/no_matrix_not_accepted', pair['accepted'], False); continue
        pts = pair['points']; check(label+'/match_points', len(pts), pair['matches'])
        a = np.array([p['source'] for p in pts]); b = np.array([p['target'] for p in pts])
        w, h = pages[f]['preview_size']; col = np.clip((a[:, 0]/w*8).astype(int), 0, 7); row = np.clip((a[:, 1]/h*8).astype(int), 0, 7)
        held = (col+2*row) % 5 == 0
        errors = np.linalg.norm(apply(a, pair['matrix'])-b, axis=1)
        for i, (p, hold, error) in enumerate(zip(pts, held, errors)):
            check(label+'/role/'+str(i), p['role'], 'heldout' if hold else 'fit')
            check(label+'/residual/'+str(i), p['error_yale_pixels'], float(error))
        check_stats(label+'/heldout', pair['heldout'], errors[held])
        accepted = bool(pair['fit_inliers'] >= 50 and held.sum() >= 10 and np.median(errors[held]) <= 2
                        and np.percentile(errors[held], 90) <= 5 and (errors[held] <= 5).mean() >= .8
                        and min(pair['fit_inlier_span_fraction']) >= .5)
        check(label+'/gate', pair['accepted'], accepted)
        feature_errors[label] = {'heldout_points': int(held.sum()), 'accepted': accepted,
                                 'median_yale_pixels': float(np.median(errors[held])) if held.any() else None}
    expected_words = []; matrices = {}
    for f, page in pages.items():
        same = next(p for p in pairs if p['source_folio'] == f == p['target_folio']); cal = result['calibrations'][f]
        matrix = None
        if same['accepted'] and cal['accepted']:
            matrix = np.asarray(same['matrix'])@np.asarray(cal['matrix']); matrix /= matrix[2, 2]
            check(f+'/composition', result['composed_xml_to_yale'][f], matrix)
        else: check(f+'/no_unaccepted_composition', result['composed_xml_to_yale'][f], None)
        matrices[f] = matrix
        with Image.open(repo/page['yale_path']) as im: size = im.size
        for w in page['words']:
            x, y, width, height = w['xml_bbox']; flags = []; polygon = None
            if width <= 0: flags.append('source_nonpositive_width')
            if height <= 0: flags.append('source_nonpositive_height')
            if matrix is None: flags.append('registration_not_accepted')
            elif not flags:
                polygon = apply([[x, y], [x+width, y], [x+width, y+height], [x, y+height]], matrix)
                if any(u < 0 or v < 0 or u > size[0] or v > size[1] for u, v in polygon): flags.append('outside_yale_frame')
            expected_words.append((f, w, flags, polygon))
    check('word_record_count', len(words), len(expected_words))
    for actual, (f, w, flags, polygon) in zip(words, expected_words):
        label = f+'/'+str(w['index'])
        for k, value in {'folio': f, 'index': w['index'], 'eva': w['eva'], 'source_xml_bbox': w['xml_bbox'], 'flags': flags}.items():
            check(label+'/mapped_'+k, actual[k], value)
        check(label+'/polygon', actual['yale_polygon'], polygon)
    correct = sum(p['accepted'] and p['correct_folio_pair'] for p in pairs)
    wrong = sum(p['accepted'] and not p['correct_folio_pair'] for p in pairs)
    calibrations = sum(c['accepted'] for c in result['calibrations'].values())
    check('accepted_correct', result['accepted_correct_image_pairs'], correct)
    check('accepted_wrong', result['accepted_wrong_image_pairs'], wrong)
    check('accepted_calibrations', result['accepted_calibrations'], calibrations)
    check('candidate_polygons', result['words_with_candidate_polygons'], sum(w['yale_polygon'] is not None for w in words))
    check('word_geometry_flags', result['word_geometry_flags'], dict(Counter(flag for w in words for flag in w['flags'])))
    status = 'PASS_GEOMETRIC_DEVELOPMENT_CHECKS_WORDS_PROVISIONAL' if correct == 4 and wrong == 0 and calibrations == 4 else 'FAIL_SOME_REGISTRATION_CHECKS'
    check('reported_experiment_status', result['status'], status)
    return {'status': 'PASS_EXPORTED_GEOMETRY_AUDIT' if not mismatches else 'FAIL', 'checks': checks,
            'mismatches': mismatches, 'calibration': calibration_errors, 'image_registration': feature_errors,
            'scope': 'Original XML/JSON records, image hashes, partitions, projection arithmetic, decisions and polygon exports. Does not rerun SIFT/RANSAC, independently verify the reported robust-fit inlier mask or validate readings.',
            'translation': 'NOT_RUN'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--repo', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); result = audit(args.bundle, args.repo)
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=True))
    if result['mismatches']: raise SystemExit(1)
