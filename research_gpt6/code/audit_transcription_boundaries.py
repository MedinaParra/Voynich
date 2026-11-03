#!/usr/bin/env python3
"""Independent graph audit of source-letter alignments and exact token bridges.

No imports from the main comparison, no neural inference or paleographic review.
An optimal state (i,j) means i VT and j ZL letters have been consumed on at least
one globally minimum-cost unit-Levenshtein path. This is not a glyph alignment.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import heapq
import itertools
import json
from pathlib import Path


def raw(path):
    if path.exists():
        data = path.read_bytes()
        return gzip.decompress(data) if path.suffix == '.gz' else data
    return gzip.decompress(path.with_suffix(path.suffix + '.gz').read_bytes())


def read(path):
    return json.loads(raw(path))


def shortest_graph(a, b):
    """Find optimal grid vertices with two Dijkstra traversals, not edit DP."""
    n, m = len(a), len(b)
    width = m + 1
    vertices = (n + 1) * width
    infinity = n + m + 1

    def distances(reverse):
        start = vertices - 1 if reverse else 0
        dist = [infinity] * vertices
        dist[start] = 0
        todo = [(0, start)]
        while todo:
            cost, vertex = heapq.heappop(todo)
            if cost != dist[vertex]:
                continue
            i, j = divmod(vertex, width)
            neighbors = []
            if reverse:
                if i:
                    neighbors.append((vertex - width, 1))
                if j:
                    neighbors.append((vertex - 1, 1))
                if i and j:
                    neighbors.append((vertex - width - 1, int(a[i-1] != b[j-1])))
            else:
                if i < n:
                    neighbors.append((vertex + width, 1))
                if j < m:
                    neighbors.append((vertex + 1, 1))
                if i < n and j < m:
                    neighbors.append((vertex + width + 1, int(a[i] != b[j])))
            for target, weight in neighbors:
                candidate = cost + weight
                if candidate < dist[target]:
                    dist[target] = candidate
                    heapq.heappush(todo, (candidate, target))
        return dist

    forward, backward = distances(False), distances(True)
    optimum = forward[-1]
    vt_states = [[] for _ in range(n + 1)]
    zl_states = [[] for _ in range(m + 1)]
    for vertex in range(vertices):
        if forward[vertex] + backward[vertex] == optimum:
            i, j = divmod(vertex, width)
            vt_states[i].append(j)
            zl_states[j].append(i)
    return {'distance': optimum, 'vt_states': vt_states, 'zl_states': zl_states}


def enumerate_paths(a, b):
    """Enumerate every edit-grid path for tiny control strings only."""
    n, m = len(a), len(b)
    minimum = n + m + 1
    optimum_nodes = set()
    paths = 0

    def visit(i, j, cost, nodes):
        nonlocal minimum, optimum_nodes, paths
        if i == n and j == m:
            paths += 1
            if cost < minimum:
                minimum, optimum_nodes = cost, set(nodes)
            elif cost == minimum:
                optimum_nodes.update(nodes)
            return
        if i < n:
            visit(i + 1, j, cost + 1, nodes + [(i + 1, j)])
        if j < m:
            visit(i, j + 1, cost + 1, nodes + [(i, j + 1)])
        if i < n and j < m:
            visit(i + 1, j + 1, cost + int(a[i] != b[j]), nodes + [(i + 1, j + 1)])

    visit(0, 0, 0, [(0, 0)])
    return minimum, optimum_nodes, paths


class Checks:
    def __init__(self):
        self.count = 0
        self.mismatches = []

    def check(self, name, actual, expected=True):
        self.count += 1
        if actual != expected:
            self.mismatches.append({'check': name, 'actual': actual, 'expected': expected})


def controls(checks):
    strings = [''.join(s) for size in range(4) for s in itertools.product('ab', repeat=size)]
    total_paths = 0
    pairs = 0
    for a in strings:
        for b in strings:
            label = 'exhaustive/' + repr((a, b))
            graph = shortest_graph(a, b)
            distance, nodes, paths = enumerate_paths(a, b)
            total_paths += paths
            pairs += 1
            checks.check(label + '/distance', graph['distance'], distance)
            for i in range(len(a) + 1):
                checks.check(label + '/VT/' + str(i), graph['vt_states'][i],
                             [j for j in range(len(b) + 1) if (i, j) in nodes])
            for j in range(len(b) + 1):
                checks.check(label + '/ZL/' + str(j), graph['zl_states'][j],
                             [i for i in range(len(a) + 1) if (i, j) in nodes])

    # Explicit boundary-state regression cases supplement exhaustive binary paths.
    examples = [
        ('', '', 0, [[0]], [[0]]),
        ('', 'ab', 2, [[0, 1, 2]], [[0], [0], [0]]),
        ('ab', '', 2, [[0], [0], [0]], [[0, 1, 2]]),
        ('a', 'aa', 1, [[0, 1], [1, 2]], [[0], [0, 1], [1]]),
        ('ab', 'ba', 2, [[0, 1], [0, 1, 2], [1, 2]], [[0, 1], [0, 1, 2], [1, 2]]),
        ('abc', 'abc', 0, [[0], [1], [2], [3]], [[0], [1], [2], [3]]),
    ]
    for index, (a, b, distance, vt, zl) in enumerate(examples):
        checks.check('explicit_boundaries/' + str(index), shortest_graph(a, b),
                     {'distance': distance, 'vt_states': vt, 'zl_states': zl})
    return {'exhaustive_binary_pairs_length_0_to_3': pairs,
            'complete_edit_paths_enumerated': total_paths,
            'explicit_boundary_and_tie_cases': len(examples),
            'scope': 'Software controls, not scientific iterations or decipherment attempts'}


def audit(repo):
    checks = Checks()
    control_summary = controls(checks)
    control_checks = checks.count
    bundle = repo / 'results/transcription_boundaries'
    comparison_path = bundle / 'comparison.json'
    comparison_bytes = raw(comparison_path)
    comparison = json.loads(comparison_bytes)
    loci = comparison['loci']
    checks.check('loci_are_list', isinstance(loci, list))
    ids = [row['id'] for row in loci]
    checks.check('unique_locus_ids', len(ids), len(set(ids)))
    statuses = Counter()
    grid_states_checked = 0
    ambiguous_vt_positions = 0
    for row in loci:
        label = 'locus/' + row['id']
        statuses[row['status']] += 1
        if row['status'] != 'compared':
            checks.check(label + '/not_aligned_when_excluded_or_unpaired', row.get('alignment') is None)
            continue
        a, b = row['vt']['chars'], row['zl']['chars']
        checks.check(label + '/VT_literal_lowercase', isinstance(a, str) and all('a' <= c <= 'z' for c in a))
        checks.check(label + '/ZL_literal_lowercase', isinstance(b, str) and all('a' <= c <= 'z' for c in b))
        expected = shortest_graph(a, b)
        actual = row['alignment']
        for key in ['distance', 'vt_states', 'zl_states']:
            checks.check(label + '/' + key, actual[key], expected[key])
        for source in ['vt', 'zl']:
            length = len(row[source]['chars'])
            for index, boundary in enumerate(row[source]['boundaries']):
                checks.check(label + '/' + source + '/boundary/' + str(index) + '/kind',
                             boundary['kind'] in ['.', ',', '<->', '<~>'])
                checks.check(label + '/' + source + '/boundary/' + str(index) + '/offset',
                             type(boundary['offset']) is int and 0 <= boundary['offset'] <= length)
        # Test every grid vertex explicitly, including absent and ambiguous states.
        # This also checks consistency of the two representations of the relation.
        if len(actual['vt_states']) == len(a) + 1 and len(actual['zl_states']) == len(b) + 1:
            for i in range(len(a) + 1):
                ambiguous_vt_positions += int(len(expected['vt_states'][i]) > 1)
                for j in range(len(b) + 1):
                    permitted = j in expected['vt_states'][i]
                    checks.check(label + '/vertex/' + str(i) + ',' + str(j),
                                 (j in actual['vt_states'][i], i in actual['zl_states'][j]),
                                 (permitted, permitted))
                    grid_states_checked += 1

    bridges = comparison['bridges']
    bridge_statuses = Counter()
    checks.check('bridges_are_list', isinstance(bridges, list))
    checks.check('unique_bridge_folios', len(bridges), len({b['folio'] for b in bridges}))
    for bridge in bridges:
        label = 'bridge/' + bridge['folio']
        bridge_statuses[bridge['status']] += 1
        checks.check(label + '/status_known', bridge['status'] in ['exact_token_sequence', 'unmapped'])
        for source in ['vp_tokens', 'vt_tokens']:
            checks.check(label + '/' + source + '/strings',
                         isinstance(bridge[source], list) and all(isinstance(s, str) for s in bridge[source]))
        if bridge['status'] == 'exact_token_sequence':
            checks.check(label + '/complete_folio_sequence_equal', bridge['vp_tokens'], bridge['vt_tokens'])

    # Verify that preserved original source bytes match preregistered Git blob IDs.
    # This is a source-preservation check, not a second transcription parser.
    plan_path = repo / 'data/transcription_boundaries_plan.json'
    plan_bytes = raw(plan_path)
    plan = json.loads(plan_bytes)
    wanted = {v['expected_git_blob'] for v in plan['sources'].values()}
    found = {sha: [] for sha in wanted}
    for path in sorted(bundle.rglob('*')):
        if not path.is_file():
            continue
        data = raw(path)
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob in found:
            found[blob].append({'path': str(path.relative_to(bundle)), 'bytes': len(data),
                                'sha256': hashlib.sha256(data).hexdigest()})
    source_checks = {}
    for name, source in plan['sources'].items():
        matches = found[source['expected_git_blob']]
        checks.check('original_source/' + name + '/pinned_git_blob_preserved', bool(matches))
        source_checks[name] = {'expected_git_blob': source['expected_git_blob'], 'matches': matches}

    return {'status': 'PASS' if not checks.mismatches else 'FAIL', 'checks': checks.count,
            'mismatches': checks.mismatches, 'control_checks': control_checks,
            'controls': control_summary,
            'comparison_sha256': hashlib.sha256(comparison_bytes).hexdigest(),
            'plan_sha256': hashlib.sha256(plan_bytes).hexdigest(),
            'loci': len(loci), 'locus_statuses': dict(sorted(statuses.items())),
            'optimal_grid_vertices_checked': grid_states_checked,
            'ambiguous_VT_letter_positions': ambiguous_vt_positions,
            'bridge_statuses': dict(sorted(bridge_statuses.items())),
            'preserved_original_sources': source_checks,
            'scope': 'Dijkstra graph optimal states versus exported alignment; exhaustive tiny-path controls; exact complete token bridges; pinned original bytes. Does not independently parse IVTFF/XML, decide correct readings, or approve crop boundaries.',
            'training': 'NOT_RUN', 'new_neural_inference': 'NOT_RUN',
            'independent_expert_review': 'NOT_REVIEWED', 'translation': 'NOT_RUN'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    if args.controls_only:
        checks = Checks()
        summary = controls(checks)
        result = {'status': 'PASS' if not checks.mismatches else 'FAIL', 'checks': checks.count,
                  'mismatches': checks.mismatches, 'controls': summary}
    else:
        if args.repo is None or args.out is None:
            parser.error('--repo and --out are required unless --controls-only is used')
        result = audit(args.repo)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'checks', 'mismatches']}))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
