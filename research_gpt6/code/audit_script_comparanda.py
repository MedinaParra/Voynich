#!/usr/bin/env python3
"""Independent geometry/pixel/record audit for exploratory script comparanda.

Does not import the renderer or interpret, recognize, or assign values to glyphs.
External original H/F photographs are not re-fetched by this offline audit.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
from PIL import Image

LABELS = ('strong', 'partial', 'different', 'insufficient')
ROLES = ('same_source', 'H', 'F', 'distractor')
CASES = ('P01', 'P02', 'P03', 'P04')
CANDIDATES = ('B', 'C', 'D', 'E')


class Checks:
    def __init__(self):
        self.count = 0
        self.total_mismatches = 0
        self.mismatches = []

    def check(self, label, actual, expected=True):
        self.count += 1
        if actual != expected:
            self.total_mismatches += 1
            if len(self.mismatches) < 50:
                def describe(value):
                    if isinstance(value, bytes):
                        return {'bytes': len(value), 'sha256': hashlib.sha256(value).hexdigest()}
                    return value
                self.mismatches.append({'check': label, 'actual': describe(actual), 'expected': describe(expected)})


def read(path):
    return json.loads(path.read_bytes())


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgb_sha(image):
    return hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()


def safe(base, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('Unsafe relative input path: ' + str(relative))
    return base / p


def repo_path(repo, relative):
    parts = Path(relative).parts
    if parts and parts[0] == repo.name:
        relative = str(Path(*parts[1:]))
    return safe(repo, relative)


def size(box):
    return [box[2] - box[0], box[3] - box[1]]


def valid_box(box, pixels):
    return (isinstance(box, list) and len(box) == 4 and
            all(type(x) is int for x in box) and
            0 <= box[0] < box[2] <= pixels[0] and
            0 <= box[1] < box[3] <= pixels[1])


def overlaps(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def control_checks(c):
    c.check('control/end_exclusive_size', size([3, 4, 8, 11]), [5, 7])
    c.check('control/bounds_valid', valid_box([0, 0, 2, 2], [2, 2]))
    c.check('control/bounds_invalid', valid_box([0, 0, 3, 2], [2, 2]), False)
    c.check('control/touching_edges_do_not_overlap', overlaps([0, 0, 2, 2], [2, 0, 4, 2]), False)
    c.check('control/positive_area_overlap', overlaps([0, 0, 2, 2], [1, 1, 3, 3]))
    im = Image.new('RGB', (2, 2))
    im.putdata([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)])
    enlarged = im.resize((4, 4), Image.Resampling.NEAREST)
    c.check('control/nearest_top_left_orientation', enlarged.getpixel((0, 0)), (255, 0, 0))
    c.check('control/nearest_bottom_right_orientation', enlarged.getpixel((3, 3)), (255, 255, 255))
    c.check('control/lossless_crop_pixel', im.crop((1, 0, 2, 1)).getpixel((0, 0)), (0, 255, 0))
    return {'checks': 8, 'scope': 'Synthetic coordinate and pixel-orientation checks, not paleographic gold'}


def keyed(rows, field, c, label):
    index = {r[field]: r for r in rows}
    c.check(label + '/unique', len(index), len(rows))
    return index


def review_audit(bundle, mapping, c, input_hashes):
    paths = [bundle/'reviews/a.json', bundle/'reviews/b.json', bundle/'summary.json']
    present = [p.exists() for p in paths]
    if not any(present):
        return {'status': 'NOT_AVAILABLE', 'judgments_checked': 0,
                'scope': 'No review outcomes exist yet; no visual judgment was audited'}
    c.check('reviews/all_three_records_present', present, [True, True, True])
    if not all(present):
        return {'status': 'INCOMPLETE', 'judgments_checked': 0}
    reviews = {}
    distributions = {}
    for reader, path in zip(('A', 'B'), paths[:2]):
        document = read(path)
        input_hashes['reviews/' + path.name] = sha_file(path)
        c.check('reviews/' + reader + '/schema', document['schema'], 'script-comparanda-review-v1')
        c.check('reviews/' + reader + '/reviewer', document['reviewer'], reader)
        rows = keyed(document['cases'], 'case_id', c, 'reviews/' + reader)
        c.check('reviews/' + reader + '/case_order', [r['case_id'] for r in document['cases']], list(CASES))
        c.check('reviews/' + reader + '/case_set', sorted(rows), list(CASES))
        indexed = {}
        for case_id in CASES:
            candidates = rows[case_id]['candidates']
            c.check('reviews/' + reader + '/' + case_id + '/candidate_set', sorted(candidates), list(CANDIDATES))
            for candidate in CANDIDATES:
                row = candidates[candidate]
                c.check('reviews/' + reader + '/' + case_id + '/' + candidate + '/label', row['label'] in LABELS)
                for field in ('shared_features', 'differences', 'uncertainty'):
                    c.check('reviews/' + reader + '/' + case_id + '/' + candidate + '/' + field,
                            isinstance(row[field], str))
                indexed[(case_id, candidate)] = row['label']
        c.check('reviews/' + reader + '/judgment_count', len(indexed), 16)
        reviews[reader] = indexed
        count = Counter(indexed.values())
        distributions[reader] = {label: count[label] for label in LABELS}
    by_role = {role: {reader: {label: 0 for label in LABELS} for reader in ('A', 'B')} for role in ROLES}
    paired = []
    for case_id in CASES:
        for candidate in CANDIDATES:
            info = mapping[case_id]['candidates'][candidate]
            a, b = reviews['A'][(case_id, candidate)], reviews['B'][(case_id, candidate)]
            for reader, label in (('A', a), ('B', b)):
                by_role[info['role']][reader][label] += 1
            paired.append({'case_id': case_id, 'candidate': candidate, 'role': info['role'],
                           'sample_id': info['sample_id'], 'A': a, 'B': b, 'agree': a == b})
    agreements = sum(row['agree'] for row in paired)
    summary = read(paths[2]); input_hashes['summary.json'] = sha_file(paths[2])
    c.check('summary/schema', summary['schema'], 'script-comparanda-summary-v1')
    c.check('summary/reviewers', summary['reviewers'], ['A', 'B'])
    c.check('summary/comparisons', summary['comparisons'], 16)
    c.check('summary/judgments', summary['judgments'], 32)
    c.check('summary/agreement', summary['agreement'],
            {'exact_label_agreements': agreements, 'disagreements': 16 - agreements})
    c.check('summary/distribution_by_reviewer', summary['distribution_by_reviewer'], distributions)
    c.check('summary/by_role', summary['by_role'], by_role)
    c.check('summary/paired_rows', summary['paired_rows'], paired)
    return {'status': 'RECORDS_CHECKED', 'judgments_checked': 32,
            'exact_label_agreements': agreements, 'disagreements': 16 - agreements,
            'distribution_by_reviewer': distributions, 'by_role': by_role,
            'scope': 'Record consistency only; natural-language interpretations, paleographic accuracy and historical relationships are not validated'}


def audit(repo, bundle):
    c = Checks(); controls = control_checks(c)
    plan_path = repo/'data/script_comparanda_plan.json'
    regions_path, render_path, mapping_path = [bundle/name for name in
        ('regions.json', 'render_manifest.json', 'presentation_mapping.json')]
    plan, regions, render, presentation = map(read, (plan_path, regions_path, render_path, mapping_path))
    input_hashes = {'plan': sha_file(plan_path), 'regions': sha_file(regions_path),
                    'render_manifest': sha_file(render_path), 'presentation_mapping': sha_file(mapping_path)}
    c.check('schema/plan', plan['schema'], 'script-comparanda-plan-v1')
    c.check('schema/regions', regions['schema'], 'script-comparanda-regions-v1')
    c.check('schema/render', render['schema'], 'script-comparanda-render-v1')
    c.check('schema/mapping', presentation['schema'], 'script-comparanda-mapping-v1')
    c.check('plan/stage', plan['stage'], 92)
    c.check('plan/comparison_count', plan['sample']['total_pair_judgments_per_reader'], 16)
    c.check('plan/two_readers', plan['sample']['readers'], 2)
    c.check('plan/no_translation', plan['translation'], 'NOT_RUN')
    sources = keyed(regions['source_rasters'], 'id', c, 'source_rasters')
    planned_sources = keyed(plan['sources'], 'id', c, 'plan_sources')
    c.check('source_ids', sorted(sources), ['F', 'H', 'V'])
    originals = {}
    for name in ('V', 'H', 'F'):
        c.check('source/' + name + '/dimensions', sources[name]['pixels'], planned_sources[name]['delivered_pixels'])
        c.check('source/' + name + '/hash', sources[name]['sha256'], planned_sources[name]['sha256'])
        if 'image' in planned_sources[name]:
            location = repo_path(repo, planned_sources[name]['image'])
            c.check('source/' + name + '/original_file_hash', sha_file(location), planned_sources[name]['sha256'])
            originals[name] = Image.open(location).convert('RGB')
            c.check('source/' + name + '/original_pixels', list(originals[name].size), sources[name]['pixels'])
    samples = keyed(regions['samples'], 'id', c, 'samples')
    c.check('sample_count', len(samples), 16)
    c.check('samples_per_source', dict(Counter(s['source_id'] for s in samples.values())), {'V': 8, 'H': 4, 'F': 4})
    tiles, glyphs = {}, {}
    for name, sample in samples.items():
        label = 'sample/' + name + '/'
        source = sources[sample['source_id']]
        page, context, inner = sample['page_bbox'], sample['context_page_bbox'], sample['glyph_in_tile']
        c.check(label + 'page_bounds', valid_box(page, source['pixels']))
        c.check(label + 'context_bounds', valid_box(context, source['pixels']))
        c.check(label + 'context_contains_glyph', context[0] <= page[0] < page[2] <= context[2] and
                context[1] <= page[1] < page[3] <= context[3])
        c.check(label + 'page_to_tile_translation', inner,
                [page[0]-context[0], page[1]-context[1], page[2]-context[0], page[3]-context[1]])
        tile_path = safe(bundle, sample['tile_path'])
        tile = Image.open(tile_path).convert('RGB')
        c.check(label + 'tile_file_hash', sha_file(tile_path), sample['tile_file_sha256'])
        c.check(label + 'tile_pixels', list(tile.size), sample['tile_pixels'])
        c.check(label + 'context_size', list(tile.size), size(context))
        c.check(label + 'tile_rgb_hash', rgb_sha(tile), sample['tile_rgb_sha256'])
        c.check(label + 'inner_bounds', valid_box(inner, list(tile.size)))
        glyph = Image.open(bundle/'glyphs'/(name+'.png')).convert('RGB')
        expected = tile.crop(inner)
        c.check(label + 'glyph_dimensions', list(glyph.size), size(page))
        c.check(label + 'lossless_glyph_pixels', glyph.tobytes(), expected.tobytes())
        if sample['source_id'] in originals:
            original = originals[sample['source_id']]
            c.check(label + 'context_matches_preserved_original', tile.tobytes(), original.crop(context).tobytes())
        tiles[name], glyphs[name] = tile, glyph
        input_hashes['rgb:' + sample['tile_path']] = rgb_sha(tile)
        input_hashes['rgb:glyphs/' + name + '.png'] = rgb_sha(glyph)
    queries = keyed(regions['queries'], 'id', c, 'queries')
    mapping = keyed(presentation['cases'], 'case_id', c, 'mapping')
    sheets = keyed(render['cases'], 'case_id', c, 'render')
    for label, index in (('queries', queries), ('mapping', mapping), ('sheets', sheets)):
        c.check(label + '/case_set', sorted(index), list(CASES))
    font = repo/'results/assisted_paleography/sources/DejaVuSans.ttf'
    c.check('render/font_sha256', sha_file(font), render['font_sha256'])
    comparisons = 0
    for case_id in CASES:
        q, mp, sheet = queries[case_id], mapping[case_id], sheets[case_id]
        prefix = 'sheet/' + case_id + '/'
        c.check(prefix + 'query_mapping', mp['query_sample'], q['query'])
        c.check(prefix + 'family_mapping', mp['family'], q['family'])
        c.check(prefix + 'candidate_set', sorted(mp['candidates']), list(CANDIDATES))
        c.check(prefix + 'roles_once', sorted(x['role'] for x in mp['candidates'].values()), sorted(ROLES))
        panel = Image.open(safe(bundle, sheet['path'])).convert('RGB')
        c.check(prefix + 'panel_size', list(panel.size), sheet['pixels'])
        c.check(prefix + 'panel_rgb_sha', rgb_sha(panel), sheet['rgb_sha256'])
        input_hashes['rgb:' + sheet['path']] = rgb_sha(panel)
        placements = keyed(sheet['placements'], 'label', c, prefix + 'placements')
        c.check(prefix + 'placement_labels', sorted(placements), ['A', 'B', 'C', 'D', 'E'])
        rectangles = []
        for label in ('A', 'B', 'C', 'D', 'E'):
            slot = placements[label]
            role, sample_id = ('query', q['query']) if label == 'A' else (
                mp['candidates'][label]['role'], mp['candidates'][label]['sample_id'])
            if label != 'A':
                comparisons += 1
                c.check(prefix + label + '/role_sample', sample_id, q[role])
            c.check(prefix + label + '/role', slot['role'], role)
            c.check(prefix + label + '/sample_id', slot['sample_id'], sample_id)
            for kind, source in (('glyph', glyphs[sample_id]), ('context', tiles[sample_id])):
                destination = slot[kind + '_destination']
                c.check(prefix + label + '/' + kind + '/destination_bounds', valid_box(destination, list(panel.size)))
                target_size = size(destination)
                c.check(prefix + label + '/' + kind + '/native_pixels', slot['native_' + kind + '_pixels'], list(source.size))
                if kind == 'glyph':
                    c.check(prefix + label + '/common_glyph_height', target_size[1], 120)
                    c.check(prefix + label + '/glyph_ratio_rounding', target_size[0], round(Fraction(source.width*120, source.height)))
                else:
                    scale = min(Fraction(320, source.width), Fraction(110, source.height))
                    c.check(prefix + label + '/context_ratio_rounding', target_size,
                            [max(1, round(source.width*scale)), max(1, round(source.height*scale))])
                expected = source.resize(tuple(target_size), Image.Resampling.NEAREST)
                c.check(prefix + label + '/' + kind + '/display_pixels',
                        panel.crop(destination).tobytes(), expected.tobytes())
                rectangles.append((label + '/' + kind, destination))
        for (a, first), (b, second) in combinations(rectangles, 2):
            c.check(prefix + 'no_overlap/' + a + '/' + b, overlaps(first, second), False)
    c.check('total_pair_comparisons', comparisons, 16)
    review_result = review_audit(bundle, mapping, c, input_hashes)
    return {'schema': 'script-comparanda-integrity-v1',
            'status': 'PASS' if not c.total_mismatches else 'FAIL',
            'checks': c.count, 'mismatch_count': c.total_mismatches, 'mismatches': c.mismatches,
            'control_summary': controls,
            'counts': {'source_rasters': 3, 'native_samples': len(samples), 'sheets': len(sheets),
                       'comparisons_per_reader': comparisons},
            'preserved_originals_pixel_verified': sorted(originals),
            'external_originals_not_reacquired': sorted(set(sources)-set(originals)),
            'reviews': review_result, 'input_sha256': dict(sorted(input_hashes.items())),
            'input_hash_scope': 'JSON bytes and font bytes; RGB pixel bytes for PNG render inputs/outputs. Source tile file hashes checked separately against regions.',
            'scope': 'Offline coordinate, pixel and review-record integrity only; not historical-source authentication, paleographic accuracy, glyph reading or related-script evidence.',
            'translation_validated': False, 'expert_gold_accuracy_validated': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    result = audit(a.repo, a.bundle)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'checks', 'mismatch_count')}, sort_keys=True))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
