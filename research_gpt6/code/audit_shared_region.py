#!/usr/bin/env python3
"""Independent pixel, checkpoint-prefix, geometry and posterior replay audit.

No Torch import, pickle execution, neural inference, or paleographic validation.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import pickletools
import statistics
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from audit_kraken_ctc_posterior import probability_beam
from audit_voynichese_registration import apply
from audit_local_residual_registration import compensate, metrics as geometry_metrics, gate


def raw(path):
    return path.read_bytes() if path.exists() else gzip.decompress(path.with_suffix(path.suffix+'.gz').read_bytes())


def read(path):
    return json.loads(raw(path))


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else raw(value)).hexdigest()


def edit(a, b):
    matrix = [[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(len(a)+1):
        matrix[i][0] = i
    for j in range(len(b)+1):
        matrix[0][j] = j
    for i in range(1, len(a)+1):
        for j in range(1, len(b)+1):
            matrix[i][j] = min(matrix[i-1][j]+1, matrix[i][j-1]+1, matrix[i-1][j-1]+(a[i-1] != b[j-1]))
    return matrix[-1][-1]


def checkpoint_counters(path):
    """Read the two leading Lightning dict integers without unpickling tensors."""
    with zipfile.ZipFile(path) as z:
        member = next(n for n in z.namelist() if n.endswith('/data.pkl'))
        ops = iter(pickletools.genops(z.read(member)))
        keys, values = [], []
        for opcode, arg, pos in ops:
            if opcode.name in ['BINUNICODE', 'SHORT_BINUNICODE', 'UNICODE']:
                keys.append(arg)
                if arg not in ['epoch', 'global_step'] or keys != ['epoch', 'global_step'][:len(keys)]:
                    raise ValueError('Unexpected Lightning checkpoint prefix')
                for value_op, value, _ in ops:
                    if value_op.name in ['BINPUT', 'LONG_BINPUT', 'MEMOIZE']:
                        continue
                    if value_op.name not in ['BININT', 'BININT1', 'BININT2', 'INT', 'LONG', 'LONG1', 'LONG4']:
                        raise ValueError('Non-literal checkpoint counter')
                    values.append(int(value))
                    break
                if len(values) == 2:
                    return dict(zip(keys, values))
    raise ValueError('Checkpoint counters unavailable')


def metric(rows):
    if not rows:
        return None
    n = sum(len(r['reference']) for r in rows)
    return {name: {'errors': sum(edit(r['reference'], r['predictions'][name]) for r in rows), 'eva_characters': n,
                   'cer': sum(edit(r['reference'], r['predictions'][name]) for r in rows)/n,
                   'exact_words': sum(r['reference'] == r['predictions'][name] for r in rows), 'words': len(rows),
                   'exact_word_fraction': sum(r['reference'] == r['predictions'][name] for r in rows)/len(rows)} for name in rows[0]['predictions']}


def audit(repo, bundle, plan_path):
    checks, mismatches = 0, []
    def check(name, a, b=True):
        nonlocal checks
        checks += 1
        if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
            equal = np.asarray(a).shape == np.asarray(b).shape and bool(np.allclose(a, b, rtol=1e-9, atol=1e-6))
        elif isinstance(a, int) and isinstance(b, int):
            equal = a == b
        elif isinstance(a, (float, int)) and isinstance(b, (float, int)):
            equal = math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-8)
        else:
            equal = a == b
        if not equal:
            mismatches.append({'check': name, 'actual': str(a)[:800], 'expected': str(b)[:800]})
    plan = read(plan_path)
    data = read(repo/plan['prepared_dataset_path'])
    training = [r for r in data if r['role'] in ['original_train', 'additional_train']]
    old_eval = [r for r in data if r['role'] in ['historical_development', 'reserved']]
    check('source_model_hash', sha(repo/plan['source_model_path']), plan['source_model_sha256'])
    check('dataset_hash', sha(repo/plan['prepared_dataset_path']), plan['prepared_dataset_sha256'])
    check('training_count', len(training), 442)
    check('old_evaluation_count', len(old_eval), 282)
    prepared = repo/'results/kraken_expansion/followup_prepared'
    if not (prepared/'crops'/Path(training[0]['path']).name).exists():
        from audit_kraken_expansion import restore_inputs
        restore_inputs(repo/'results/kraken_expansion/primary_geometry', prepared, repo)
    masks, canvases, photos = {}, {}, {}
    by_folio = defaultdict(list)
    for r in training:
        by_folio[r['folio']].append(r)
        path = prepared/'crops'/Path(r['mask_path']).name
        check(r['id']+'/source_mask_sha', sha(path), r['mask_sha256'])
        with Image.open(path) as im:
            masks[r['id']] = np.array(im.convert('L')) != 0
    for folio, rows in by_folio.items():
        canvas = np.zeros((max(r['bounds'][3] for r in rows), max(r['bounds'][2] for r in rows)), dtype=np.uint16)
        for r in rows:
            x0, y0, x1, y1 = r['bounds']
            canvas[y0:y1, x0:x1] += masks[r['id']].astype(np.uint16)
        canvases[folio] = canvas
    proofs, selected_counts, actual_counters = {}, {}, {}
    for variant in plan['variants']:
        root = bundle/'runs'/variant
        result = read(root/'result.json')
        views = read(root/'training_views.json')
        records = read(root/'perturbation_records.json')
        proof = read(root/'warmstart_equivalence.json')
        proofs[variant] = proof
        for key, expected in [('variant', variant), ('plan_sha256', sha(plan_path)), ('source_model_sha256', plan['source_model_sha256']),
                              ('training_words', 442), ('training_views', 884), ('epochs', 100), ('checkpoint_epoch', 99), ('optimizer_steps', 5600)]:
            check(variant+'/'+key, result[key], expected)
        for path, key in [('final_epoch.mlmodel', 'model_sha256'), ('training/training.log', 'training_log_sha256'),
                          ('warmstart_equivalence.json', 'warmstart_proof_sha256'), ('training_views.json', 'training_views_sha256'),
                          ('perturbation_records.json', 'perturbation_records_sha256')]:
            check(variant+'/'+path, sha(root/path), result[key])
        checkpoints = list((root/'training/checkpoints').glob('checkpoint_99-*.ckpt'))
        check(variant+'/one_final_checkpoint', len(checkpoints), 1)
        if len(checkpoints) == 1:
            check(variant+'/checkpoint_hash', sha(checkpoints[0]), result['checkpoint_sha256'])
            counters = checkpoint_counters(checkpoints[0])
            actual_counters[variant] = counters
            check(variant+'/literal_checkpoint_epoch', counters['epoch'], 99)
            check(variant+'/literal_checkpoint_steps', counters['global_step'], 5600)
        check(variant+'/source_tensor_count', len(proof['source_tensors']), 14)
        check(variant+'/warmstart_tensor_records', proof['source_tensors'], proof['converted_tensors'])
        check(variant+'/warmstart_codec_flag', proof['codec_equal'])
        check(variant+'/warmstart_file', sha(root/'warmstart.safetensors'), proof['converted_sha256'])
        check(variant+'/trained_codec', read(root/'trained_codec.json'), proof['codec'])
        config = read(root/'training/training_config.json')
        check(variant+'/monitor_training_only', config['train']['evaluation_data'], config['train']['training_data'])
        for key, expected in [('epochs', 100), ('min_epochs', 100), ('batch_size', 16), ('lrate', .001), ('augment', True), ('schedule', 'constant'), ('freeze_backbone', 0)]:
            check(variant+'/config/'+key, config['train'][key], expected)
        check(variant+'/seed', config['seed'], plan['seed'])
        check(variant+'/finished_epochs', 'max_epochs=100` reached' in raw(root/'training/training.log').decode())
        augmentation = read(root/'augmentation.json')
        check(variant+'/augmentation_p', augmentation['p'], .5)
        check(variant+'/augmentation_max_ops', augmentation['max_ops'], 3)
        check(variant+'/augmentation_source', sha(root/'sources/kraken_augment.py'), augmentation['module_sha256'])
        check(variant+'/record_ids', [r['id'] for r in records], [r['id'] for r in training])
        check(variant+'/view_ids', [r['id'] for r in views], [r['id']+'_v'+str(i) for r in training for i in [0, 1]])
        check(variant+'/training_list', [Path(s).stem for s in raw(root/'training/train.lst').decode().splitlines()], [r['id'] for r in views])
        selected_counts[variant] = {}
        with zipfile.ZipFile(root/'selection_masks.zip') as z:
            check(variant+'/all_selection_masks', sorted(z.namelist()), sorted(r['id']+'.png' for r in training))
            for index, (source, record) in enumerate(zip(training, records)):
                name = variant+'/'+source['id']
                original_path = prepared/'crops'/Path(source['path']).name
                original_bytes = original_path.read_bytes()
                check(name+'/source_image', sha(original_bytes), source['image_sha256'])
                with Image.open(io.BytesIO(original_bytes)) as im:
                    rgb = np.array(im.convert('RGB'))
                    gray = np.array(im.convert('L'))
                mask = masks[source['id']]
                x0, y0, x1, y1 = source['bounds']
                shared = mask & (canvases[source['folio']][y0:y1, x0:x1] > 1)
                check(name+'/shared_array', sha(shared.tobytes()), record['overlap_array_sha256'])
                threshold = statistics.median(gray[mask].tolist())-40
                dark = mask & (gray <= threshold)
                n = int((dark & shared).sum())
                key = int.from_bytes(hashlib.sha256((str(plan['seed'])+'/'+source['id']).encode()).digest()[:8], 'big')
                expected_mask = np.zeros(mask.shape, dtype=bool)
                if variant == 'shared_ink':
                    expected_mask = dark & shared
                elif variant == 'random_ink' and n:
                    rng = np.random.Generator(np.random.PCG64(key))
                    expected_mask.flat[rng.choice(np.flatnonzero(dark), n, replace=False)] = True
                selected_bytes = z.read(source['id']+'.png')
                check(name+'/selection_png_hash', sha(selected_bytes), record['selection_mask_sha256'])
                with Image.open(io.BytesIO(selected_bytes)) as im:
                    selected = np.array(im.convert('L')) > 0
                check(name+'/selection_pixels', selected, expected_mask)
                check(name+'/selected_array_hash', sha(selected.tobytes()), record['selected_array_sha256'])
                paper = [round(statistics.median(rgb[:, :, c][mask].tolist())) for c in range(3)]
                check(name+'/paper_rgb', record['paper_rgb'], paper)
                expected = rgb.copy()
                for y, x in zip(*np.nonzero(selected)):
                    expected[y, x] = [(int(rgb[y, x, c])+paper[c]+1)//2 for c in range(3)]
                selected_counts[variant][source['id']] = int(selected.sum())
                for k, v in [('dark_threshold', threshold), ('dark_pixels', int(dark.sum())), ('shared_dark_pixels', n),
                             ('selected_pixels', int(selected.sum())), ('selected_shared_pixels', int((selected & shared).sum())),
                             ('changed_pixels', int(np.any(expected != rgb, axis=2).sum())), ('sample_seed', key)]:
                    check(name+'/'+k, record[k], v)
                for v in [0, 1]:
                    view = views[2*index+v]
                    image_bytes = original_bytes
                    if v == 1 and variant != 'repeat':
                        buffer = io.BytesIO()
                        Image.fromarray(expected).save(buffer, format='PNG')
                        image_bytes = buffer.getvalue()
                    check(name+'/view'+str(v)+'/image_hash', view['image_sha256'], sha(image_bytes))
                    check(name+'/view'+str(v)+'/reference', view['reference'], source['reference'])
                    check(name+'/view'+str(v)+'/label_hash', view['label_sha256'], sha(source['reference'].encode()))
        fits = result['training_predictions']
        check(variant+'/fit_ids', [r['id'] for r in fits], [r['id'] for r in views])
        for r, view in zip(fits, views):
            check(variant+'/fit/'+r['id'], r['errors'], edit(view['reference'], r['prediction']))
        for v in [0, 1]:
            rs = [r for r in fits if r['view'] == v]
            expected = {'words': len(rs), 'errors': sum(edit(r['reference'], r['prediction']) for r in rs), 'exact_words': sum(r['reference'] == r['prediction'] for r in rs)}
            check(variant+'/fit_by_view/'+str(v), result['training_fit_by_view'][str(v)], expected)
        check(variant+'/fit_forward_calls', result['training_inference_calls'], 884)
    check('all_initial_tensor_records_equal', proofs['repeat']['source_tensors'] == proofs['random_ink']['source_tensors'] == proofs['shared_ink']['source_tensors'])
    check('matched_selected_counts', selected_counts['random_ink'], selected_counts['shared_ink'])
    check('repeat_zero_selected', sum(selected_counts['repeat'].values()), 0)

    fresh = bundle/'fresh_data'
    fresh_result = read(fresh/'fresh_result.json')
    fresh_rows = read(fresh/'dataset.json')
    check('fresh/status', fresh_result['status'], 'PASS_FRESH_GEOMETRY_CANDIDATES')
    check('fresh/parent_plan', fresh_result['plan_sha256'], sha(plan_path))
    check('fresh/dataset_hash', sha(fresh/'dataset.json'), fresh_result['dataset_sha256'])
    check('fresh/folios', sorted({r['folio'] for r in fresh_rows}), plan['fresh_folios'])
    acquired = read(fresh/'inputs/acquired_inputs.json')
    source_pages = {r['folio']: r for r in acquired['pages']}
    models = read(fresh/'geometry_models.json')
    for page in plan['fresh_pages']:
        folio = page['folio']
        inputs = source_pages[folio]
        for kind in ['json', 'preview', 'yale', 'xml']:
            check(folio+'/'+kind+'/hash', sha(repo/inputs[kind+'_path']), inputs[kind+'_sha256'])
        check(folio+'/official_photo_hash', inputs['yale_sha256'], page['yale_sha256'])
        words = ET.fromstring(raw(repo/inputs['xml_path'])).findall('word')
        tokens, boxes = read(repo/inputs['json_path'])
        check(folio+'/xml_json_count', len(words), len(boxes))
        for i, (w, box) in enumerate(zip(words, boxes)):
            check(folio+'/word/'+str(i), tokens[box[0]][0], w.text or '')
            check(folio+'/acquired_word/'+str(i), inputs['words'][i]['eva'], tokens[box[0]][0])
            check(folio+'/acquired_index/'+str(i), inputs['words'][i]['index'], i)
            check(folio+'/acquired_box/'+str(i), inputs['words'][i]['preview_bbox'], box[1:])
        with Image.open(repo/inputs['yale_path']) as im:
            photos[folio] = im.convert('RGB')
    for row in fresh_rows:
        folio, identity = row['folio'], row['id']
        page = source_pages[folio]
        word = page['words'][row['index']]
        check(identity+'/reference', row['reference'], word['eva'])
        x, y, w, h = word['preview_bbox']
        q = np.array([[x, y], [x+w, y], [x+w, y+h], [x, y+h]], dtype=float)
        model = models[folio]
        prediction = apply(q, np.array(model['global_matrix']))+compensate(q, np.array(model['anchor_sources']), np.array(model['anchor_vectors']), plan['geometry']['local'])[0]
        check(identity+'/polygon', np.array(row['polygon']), prediction)
        polygon = np.array(row['polygon'])
        bounds = [max(0, math.floor(polygon[:, 0].min())-4), max(0, math.floor(polygon[:, 1].min())-4),
                  min(photos[folio].width, math.ceil(polygon[:, 0].max())+4), min(photos[folio].height, math.ceil(polygon[:, 1].max())+4)]
        check(identity+'/bounds', row['bounds'], bounds)
        x0, y0, x1, y1 = bounds
        mask = Image.new('L', (x1-x0, y1-y0), 0)
        ImageDraw.Draw(mask).polygon([(round(a-x0), round(b-y0)) for a, b in polygon], fill=255)
        mask = mask.filter(ImageFilter.MaxFilter(9))
        crop = Image.composite(photos[folio].crop(bounds), Image.new('RGB', mask.size, 'white'), mask)
        for value, field in [(crop, 'image_sha256'), (mask, 'mask_sha256')]:
            buffer = io.BytesIO()
            value.save(buffer, format='PNG')
            check(identity+'/'+field, sha(buffer.getvalue()), row[field])
        row['role'] = 'fresh_reserved'
    pairs = {r['folio']: r for r in read(fresh/'geometry_correspondences.json')}
    cases = read(fresh/'geometry_cases.json')
    check('fresh/all_ten_folds', sorted((r['folio'], r['fold']) for r in cases), sorted((f, k) for f in plan['fresh_folios'] for k in range(5)))
    for c in cases:
        folio = c['folio']
        points = np.array([p['source'] for p in pairs[folio]['points']])
        targets = np.array([p['target'] for p in pairs[folio]['points']])
        held = c['held_indices']
        width, height = source_pages[folio]['preview_size']
        colors = [(min(7, max(0, math.floor(x/width*8)))+2*min(7, max(0, math.floor(y/height*8)))) % 5 for x, y in points]
        expected_held = [i for i, color in enumerate(colors) if color == c['fold']]
        expected_fit, excluded = [], []
        for i, color in enumerate(colors):
            if color == c['fold']:
                continue
            distance = float(np.sqrt(np.sum((points[expected_held]-points[i])**2, axis=1)).min())
            (excluded if distance <= plan['geometry']['guard_source_pixels'] else expected_fit).append(i)
        check(folio+'/'+str(c['fold'])+'/held_indices', held, expected_held)
        check(folio+'/'+str(c['fold'])+'/fit_indices', c['fit_indices'], expected_fit)
        check(folio+'/'+str(c['fold'])+'/guard_excluded', c['guard_excluded_indices'], excluded)
        check(folio+'/'+str(c['fold'])+'/inliers_only_fit', set(c['fit_inlier_indices']) <= set(expected_fit))
        condition = c['conditions']['spatial_median']
        errors = [math.hypot(*(p-t)) for p, t in zip(np.array(condition['predictions']), targets[held])]
        values = geometry_metrics(errors)
        for k, v in values.items():
            check(folio+'/'+str(c['fold'])+'/'+k, condition['metrics'][k], v)
        span = np.ptp(points[c['fit_inlier_indices']], axis=0)/source_pages[folio]['preview_size']
        check(folio+'/'+str(c['fold'])+'/gate', condition['accepted'], gate(values, len(c['fit_inlier_indices']), span))
        check(folio+'/'+str(c['fold'])+'/passed', condition['accepted'])

    common = bundle/'common_evaluation'
    result = read(common/'result.json')
    expected_rows = old_eval+fresh_rows
    by_id = {r['id']: r for r in expected_rows}
    rows = result['rows']
    check('common/plan_hash', result['plan_sha256'], sha(plan_path))
    check('common/fresh_result_hash', result['fresh_result_sha256'], sha(fresh/'fresh_result.json'))
    check('common/fresh_dataset_hash', result['fresh_dataset_sha256'], sha(fresh/'dataset.json'))
    check('common/row_ids', [r['id'] for r in rows], [r['id'] for r in expected_rows])
    check('common/no_leaf_leakage', not ({r['folio'][:-1] for r in training} & {r['folio'][:-1] for r in rows}))
    check('common/primary_available', result['primary_status'], 'AVAILABLE')
    vocabulary = {r['reference'] for r in training}
    tensor_records = read(common/'tensor_checks.json')
    records = {(r['pass'], r['model'], r['id']): r for r in read(common/'capture_records.json')}
    caches, decoded = {}, {}
    calls = 0
    for model in ['source']+plan['variants']:
        path = repo/plan['source_model_path'] if model == 'source' else bundle/'runs'/model/'final_epoch.mlmodel'
        check(model+'/evaluated_model_hash', result['model_sha256'][model], sha(path))
        for pass_index in [0, 1]:
            filename = 'posterior_pass'+str(pass_index)+'_'+model+'.npz'
            check(filename+'/hash', sha(common/filename), result['posterior_file_sha256'][filename])
            npz = np.load(common/filename, allow_pickle=False)
            cache = {k: npz[k] for k in npz.files}
            npz.close()
            caches[(pass_index, model)] = cache
            check(filename+'/ids', sorted(cache), sorted(by_id))
            manifest = tensor_records[str(pass_index)+'/'+model]
            check(filename+'/unchanged_tensor_records', manifest['before'], manifest['after'])
            if model != 'source':
                check(filename+'/trained_tensor_records', manifest['before'], read(bundle/'runs'/model/'trained_tensor_records.json'))
            codec = {v[0]: k for k, v in manifest['codec'].items()}
            out = []
            for i, row in enumerate(rows):
                identity = row['id']
                p = cache[identity]
                label = filename+'/'+identity
                check(label+'/normalized', bool(np.all(np.abs(p.sum(axis=1, dtype=float)-1) < 1e-5)))
                check(label+'/finite_nonnegative', bool(np.isfinite(p).all() and (p >= 0).all()))
                capture = records[(pass_index, model, identity)]
                check(label+'/matrix_hash', capture['matrix_sha256'], sha(p.astype(np.float32).tobytes()))
                check(label+'/input_image_hash', capture['image_sha256'], by_id[identity]['image_sha256'])
                check(label+'/shape', capture['shape'], list(p.shape))
                path_labels = [max(range(len(t)), key=lambda c: t[c]) for t in p]
                greedy = ''.join(codec[k] for k, _ in itertools.groupby(path_labels) if k != 0)
                sequence, mass = probability_beam(p, 32)
                beam = ''.join(codec[k] for k in sequence)
                actual = result['all_pass_results'][pass_index][model][i]
                check(label+'/greedy', actual['greedy'], greedy)
                check(label+'/beam', actual['beam32'], beam)
                check(label+'/beam_mass', actual['beam_logmass'], mass)
                if pass_index == 0:
                    check(label+'/scored_greedy', row['predictions'][model+'_greedy'], greedy)
                    check(label+'/scored_beam', row['predictions'][model+'_beam32'], beam)
                out.append((greedy, beam))
            decoded[(pass_index, model)] = out
            check(filename+'/forward_calls', result['forward_calls'][pass_index][model], len(rows))
            calls += result['forward_calls'][pass_index][model]
    matrix_diffs = [{'model': m, 'id': r['id']} for m in ['source']+plan['variants'] for r in rows if not np.array_equal(caches[(0, m)][r['id']], caches[(1, m)][r['id']])]
    text_diffs = [{'model': m, 'id': r['id'], 'decoder': d} for m in ['source']+plan['variants'] for i, r in enumerate(rows)
                  for k, d in enumerate(['greedy', 'beam32']) if decoded[(0, m)][i][k] != decoded[(1, m)][i][k]]
    check('common/matrix_replay', result['matrix_replay_differences'], matrix_diffs)
    check('common/text_replay', result['text_replay_differences'], text_diffs)
    check('common/interface_parity', result['interface_parity_differences'], [])
    check('common/interface_count', result['interface_parity_checks'], calls)
    for row in rows:
        source = by_id[row['id']]
        for k in ['folio', 'role', 'reference']:
            check(row['id']+'/'+k, row[k], source[k])
        check(row['id']+'/seen', row['seen_in_training'], row['reference'] in vocabulary)
        training_by_id = {r['id']: r for r in training}
        check(row['id']+'/nearest_label', row['predictions']['nearest_image'], training_by_id[row['nearest_train_id']]['reference'])
        for name, prediction in row['predictions'].items():
            check(row['id']+'/edit/'+name, row['errors'][name], edit(row['reference'], prediction))
    for role in ['historical_development', 'reserved', 'fresh_reserved']:
        rs = [r for r in rows if r['role'] == role]
        groups = {'all': rs, 'seen': [r for r in rs if r['seen_in_training']], 'unseen': [r for r in rs if not r['seen_in_training']],
                  'length_1_4': [r for r in rs if len(r['reference']) <= 4], 'length_5_6': [r for r in rs if 5 <= len(r['reference']) <= 6],
                  'length_7_plus': [r for r in rs if len(r['reference']) >= 7]}
        for name, selected in groups.items():
            expected = metric(selected)
            if expected:
                for method, scores in expected.items():
                    for key, value in scores.items():
                        check(role+'/'+name+'/'+method+'/'+key, result['metrics'][role][name][method][key], value)
            else:
                check(role+'/'+name, result['metrics'][role][name], None)
        for folio in sorted({r['folio'] for r in rs}):
            check(role+'/'+folio+'/metrics', result['metrics'][role]['by_folio'][folio], metric([r for r in rs if r['folio'] == folio]))
    fresh_scored = [r for r in rows if r['role'] == 'fresh_reserved']
    unseen = [r for r in fresh_scored if not r['seen_in_training']]
    check('primary/all', result['primary_fresh_all'], metric(fresh_scored))
    check('primary/unseen', result['primary_fresh_unseen'], metric(unseen))
    alphabet = set(tensor_records['0/source']['codec'])
    for role in ['historical_development', 'reserved', 'fresh_reserved']:
        check(role+'/alphabet_coverage', result['evaluation_character_coverage'][role], dict(Counter(c for r in rows if r['role'] == role for c in r['reference'] if c not in alphabet)))
    exact = {name: [{'id': r['id'], 'reference': r['reference'], 'length': len(r['reference'])} for r in unseen if r['reference'] == r['predictions'][name]] for name in ['source_beam32', 'repeat_beam32', 'random_ink_beam32', 'shared_ink_beam32']}
    return {'status': 'PASS' if not mismatches else 'FAIL', 'checks': checks, 'mismatches': mismatches,
            'plan_sha256': sha(plan_path), 'common_result_sha256': sha(common/'result.json'),
            'checkpoint_counters_read_without_unpickling': actual_counters, 'training_words': len(training),
            'fresh_words': len(fresh_rows), 'fresh_unseen_words': len(unseen), 'posterior_matrices_replayed': len(rows)*8,
            'logged_common_forward_calls': calls, 'matrix_replay_differences': len(matrix_diffs), 'text_replay_differences': len(text_diffs),
            'fresh_all_metrics': metric(fresh_scored), 'fresh_unseen_metrics': metric(unseen), 'fresh_unseen_exact': exact,
            'scope': 'Independent scalar pixel attenuation and PNG reconstruction, additive whole-page mask coverage, static literal Lightning checkpoint counters, fresh geometry/crop/label checks, probability-space beam versus log-space implementation, full-matrix edit and aggregates. Tensor records/file hashes checked; no new neural inference, tensor reload, SIFT fit or paleographic validation.',
            'translation': 'NOT_RUN'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    result = audit(a.repo, a.bundle, a.plan)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ['status', 'checks', 'mismatches', 'posterior_matrices_replayed', 'logged_common_forward_calls']}))
    raise SystemExit(result['status'] != 'PASS')
