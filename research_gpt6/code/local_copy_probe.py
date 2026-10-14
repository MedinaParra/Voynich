#!/usr/bin/env python3
"""Exploratory generative mechanism comparison. No decoded meanings or language.

All parameter fitting uses training leaves. Teacher-forced next-token scores and
free string generation are distinct outputs. Character units are literal EVA.
"""
import argparse
import bisect
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import re
import statistics
import string

SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'
ALPHABET = string.ascii_lowercase
STRATA = (('A', '1'), ('B', '2'), ('B', '3'))
KINDS = ('independent', 'edge', 'edge_copy')


def blob_sha(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def physical_leaf(folio):
    m = re.match(r'^f[0-9]+', folio)
    return m[0] if m else None


def parse(raw, commas):
    rows, audit, meta = [], Counter(), {}
    for line in raw.splitlines():
        if re.match(r'^<[^>.,]+>\s*<!', line):
            meta = dict(re.findall(r'\$([A-Z])=([^\s>]+)', line))
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m[1] or not re.search(r'P[0-9a-z]', m[1].split(',', 1)[1]):
            continue
        locus, text = m.groups()
        folio = locus.split('.')[0]
        leaf = physical_leaf(folio)
        if leaf is None:
            audit['unmapped_physical_loci'] += 1
            continue
        group = (meta.get('L', '?'), meta.get('H', '?'))
        if group not in STRATA:
            audit['outside_fixed_strata_loci'] += 1
            continue
        audit['retained_paragraph_loci'] += 1
        text = re.sub(r'<[^>]*>', '', text.replace('<->', '|'))
        text = re.sub(r'\s+', '.', text.strip()).replace(',', '.' if commas == 'split' else '')
        run = []
        def save():
            if run:
                rows.append(dict(locus=locus, folio=folio, leaf=leaf,
                    group=group, quire=meta.get('Q', '?'), section=meta.get('I', '?'), words=run[:]))
        for token in re.split(r'([.|])', text):
            if not token or token == '.':
                continue
            if token != '|' and re.fullmatch('[a-z]{1,64}', token):
                run.append(token)
            else:
                save()
                run.clear()
                audit['drawing_breaks' if token == '|' else 'uncertain_chunks'] += 1
        save()
    return rows, dict(audit)


def band(i, n):
    return min(3, 4 * i // n)


def location(i, n):
    return 'first' if i == 0 else 'last' if i == n - 1 else 'middle'


@lru_cache(maxsize=100000)
def edit_events(a, b):
    """All one-edit paths; repeated characters can yield several paths."""
    if a == b:
        return (('identity', 0, ''),)
    if len(b) == len(a):
        mismatch = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        return (('substitution', mismatch[0], b[mismatch[0]]),) if len(mismatch) == 1 else ()
    if len(b) == len(a) + 1:
        return tuple(('insertion', i, b[i]) for i in range(len(b)) if b[:i] + b[i + 1:] == a)
    if len(b) == len(a) - 1:
        return tuple(('deletion', i, '') for i in range(len(a)) if a[:i] + a[i + 1:] == b)
    return ()


class Sampler:
    def __init__(self, weights):
        self.items, self.cumulative = [], []
        total = 0.0
        for item, weight in sorted(weights.items()):
            if weight > 0:
                total += weight
                self.items.append(item)
                self.cumulative.append(total)
        if not self.items:
            raise ValueError('Empty sampling distribution')
        self.total = total

    def draw(self, rng):
        return self.items[bisect.bisect_right(self.cumulative, rng.random() * self.total)]


class Mechanism:
    def __init__(self, rows, alphabet=ALPHABET, maximum=64):
        self.alphabet, self.maximum = alphabet, maximum
        self.words, self.bands, self.firsts = Counter(), defaultdict(Counter), defaultdict(Counter)
        self.chars, self.starts, self.transitions = Counter(), Counter(), defaultdict(Counter)
        self.links, self.operations = defaultdict(Counter), Counter()
        self.positions, self.newchars = defaultdict(Counter), defaultdict(Counter)
        self.pairs = []
        for row in rows:
            words = row['words']
            for i, w in enumerate(words):
                if not w or len(w) > maximum or any(c not in alphabet for c in w):
                    raise ValueError('Invalid training word')
                b = band(i, len(words))
                self.words[w] += 1
                self.bands[b][w] += 1
                self.firsts[b][w[0]] += 1
                self.starts[w[0]] += 1
                self.chars.update(w)
                for x, y in zip(w, w[1:] + '$'):
                    self.transitions[x][y] += 1
                if i:
                    previous = words[i - 1]
                    self.links[b, previous[-1]][w[0]] += 1
                    self.pairs.append((previous, w, b))
                    events = edit_events(previous, w)
                    for kind, pos, new in events:
                        weight = 1 / len(events)
                        self.operations[kind] += weight
                        if kind != 'identity':
                            size = len(previous) + (kind == 'insertion')
                            self.positions[kind][location(pos, size)] += weight
                        if kind == 'insertion':
                            self.newchars['insert'][new] += weight
                        elif kind == 'substitution':
                            self.newchars[previous[pos]][new] += weight
        if not self.words:
            raise ValueError('No training words')
        total = sum(self.chars.values())
        self.char_prior = {c: (self.chars[c] + .5) / (total + .5 * len(alphabet)) for c in alphabet}
        nt = sum(self.words.values())
        self.start_p = {c: (self.starts[c] + .5) / (nt + .5 * len(alphabet)) for c in alphabet}
        self.inside = {c: {d: (self.transitions[c][d] + .5) /
            (sum(self.transitions[c].values()) + .5 * (len(alphabet) + 1))
            for d in alphabet + '$'} for c in alphabet}
        self.char_samplers = {c: Sampler(p) for c, p in self.inside.items()}
        self.start_sampler = Sampler(self.start_p)
        self.word_samplers, self.byfirst_samplers, self.base_first, self.edge_p = {}, {}, {}, {}
        self.band_totals = {}
        for b in range(4):
            if not self.bands[b]:
                self.bands[b] = self.words.copy()
                self.firsts[b] = Counter()
                for w, n in self.words.items():
                    self.firsts[b][w[0]] += n
            n = sum(self.bands[b].values())
            self.band_totals[b] = n
            self.word_samplers[b] = Sampler(self.bands[b])
            self.base_first[b] = {c: .95 * self.firsts[b][c] / n + .05 * self.start_p[c] for c in alphabet}
            for c in alphabet:
                pool = {w: count for w, count in self.bands[b].items() if w[0] == c}
                if pool:
                    self.byfirst_samplers[b, c] = Sampler(pool)
            for c in alphabet:
                counts = self.links[b, c]
                self.edge_p[b, c] = {d: (counts[d] + 20 * self.base_first[b][d]) /
                    (sum(counts.values()) + 20) for d in alphabet}
        self.edge_samplers = {k: Sampler(v) for k, v in self.edge_p.items()}
        self.char_prob_cache, self.path_cache, self.match_cache = {}, {}, {}
        self.edit_char_cache = {}
        self.gamma = .1
        pq = [(self.edge_probability(w, a, b), self.copy_probability(w, a)) for a, w, b in self.pairs]
        for _ in range(30):
            self.gamma = (sum(self.gamma * q / ((1 - self.gamma) * p + self.gamma * q)
                for p, q in pq) / len(pq)) if pq else 0.0

    def character_probability(self, word):
        if word not in self.char_prob_cache:
            p = self.start_p[word[0]]
            for a, b in zip(word, word[1:]):
                p *= self.inside[a][b]
            if len(word) < self.maximum:
                p *= self.inside[word[-1]]['$']
            self.char_prob_cache[word] = p
        return self.char_prob_cache[word]

    def base_probability(self, word, b):
        return .95 * self.bands[b][word] / self.band_totals[b] + .05 * self.character_probability(word)

    def edge_probability(self, word, previous, b):
        p = self.base_probability(word, b)
        return p if previous is None else p * self.edge_p[b, previous[-1]][word[0]] / self.base_first[b][word[0]]

    def copy_paths(self, previous):
        if previous not in self.path_cache:
            n = len(previous)
            kinds = ['identity', 'substitution']
            if n > 1:
                kinds.append('deletion')
            if n < self.maximum:
                kinds.append('insertion')
            mass = sum(self.operations[k] + 1 for k in kinds)
            kinds_p = {k: (self.operations[k] + 1) / mass for k in kinds}
            positions = {}
            for k in kinds:
                if k != 'identity':
                    size = n + (k == 'insertion')
                    counts = self.positions[k]
                    weights = {i: counts[location(i, size)] + 1 for i in range(size)}
                    # Location mass is divided among positions in that location.
                    members = Counter(location(i, size) for i in range(size))
                    weights = {i: w / members[location(i, size)] for i, w in weights.items()}
                    total = sum(weights.values())
                    positions[k] = {i: w / total for i, w in weights.items()}
            self.path_cache[previous] = kinds_p, positions
        return self.path_cache[previous]

    def edited_characters(self, old=None):
        if old in self.edit_char_cache:
            return self.edit_char_cache[old]
        counts = self.newchars['insert' if old is None else old]
        weights = {c: counts[c] + 20 * self.char_prior[c] for c in self.alphabet if c != old}
        n = sum(weights.values())
        probabilities = {c: w / n for c, w in weights.items()}
        self.edit_char_cache[old] = probabilities
        return probabilities

    def copy_probability(self, word, previous):
        events = edit_events(previous, word)
        if not events:
            return 0.0
        kinds, positions = self.copy_paths(previous)
        p = 0.0
        for k, pos, new in events:
            if k not in kinds:
                continue
            value = kinds[k]
            if k != 'identity':
                value *= positions[k][pos]
            if k in ('insertion', 'substitution'):
                value *= self.edited_characters(previous[pos] if k == 'substitution' else None)[new]
            p += value
        return p

    def probability(self, word, previous, b, kind):
        if kind == 'independent' or previous is None:
            return self.base_probability(word, b)
        p = self.edge_probability(word, previous, b)
        return p if kind == 'edge' else (1 - self.gamma) * p + self.gamma * self.copy_probability(word, previous)

    def character_sample(self, rng, first=None):
        w = first if first is not None else self.start_sampler.draw(rng)
        while len(w) < self.maximum:
            c = self.char_samplers[w[-1]].draw(rng)
            if c == '$':
                break
            w += c
        return w

    def base_sample(self, b, rng, first=None):
        empirical_p = .95 if first is None else (.95 * self.firsts[b][first] /
            self.band_totals[b] / self.base_first[b][first])
        if rng.random() < empirical_p:
            return (self.word_samplers[b] if first is None else self.byfirst_samplers[b, first]).draw(rng)
        return self.character_sample(rng, first)

    def copy_sample(self, previous, rng):
        kinds, positions = self.copy_paths(previous)
        k = Sampler(kinds).draw(rng)
        if k == 'identity':
            return previous
        i = Sampler(positions[k]).draw(rng)
        if k == 'deletion':
            return previous[:i] + previous[i + 1:]
        new = Sampler(self.edited_characters(previous[i] if k == 'substitution' else None)).draw(rng)
        return previous[:i] + new + previous[i + (k == 'substitution'):]

    def sample(self, previous, b, kind, rng):
        if kind == 'edge_copy' and previous is not None and rng.random() < self.gamma:
            return self.copy_sample(previous, rng)
        if kind == 'independent' or previous is None:
            return self.base_sample(b, rng)
        first = self.edge_samplers[b, previous[-1]].draw(rng)
        return self.base_sample(b, rng, first)

    def matched_context_sampler(self, previous):
        if previous not in self.match_cache:
            weights = {w: c for w, c in self.words.items() if w != previous and
                len(w) == len(previous) and w[-1] == previous[-1]}
            self.match_cache[previous] = Sampler(weights) if weights else None
        return self.match_cache[previous]


def information(pairs):
    counts, left, right = Counter(pairs), Counter(), Counter()
    for (a, b), n in counts.items():
        left[a] += n
        right[b] += n
    total = sum(counts.values())
    return sum(n / total * math.log2(n * total / (left[a] * right[b]))
        for (a, b), n in counts.items()) if total else 0.0


def metrics(runs, rng, shuffles=19):
    pairs = [(a, b) for r in runs for a, b in zip(r, r[1:])]
    words = [w for r in runs for w in r]
    edge = information((a[-1], b[0]) for a, b in pairs)
    null = []
    for _ in range(shuffles):
        shuffled = []
        for r in runs:
            r = r[:]
            rng.shuffle(r)
            shuffled.append(r)
        null.append(information((a[-1], b[0]) for r in shuffled for a, b in zip(r, r[1:])))
    transitions, contexts = Counter(), Counter()
    for w in words:
        transitions.update(zip(w, w[1:]))
    for (a, _), n in transitions.items():
        contexts[a] += n
    total = sum(transitions.values())
    h1 = -sum(n / total * math.log2(n / contexts[a]) for (a, b), n in transitions.items()) if total else 0.0
    vocabulary = Counter(words)
    return dict(edge_mi=edge, edge_excess=edge - statistics.mean(null), internal_h1=h1,
        repeat_rate=sum(a == b for a, b in pairs) / len(pairs),
        edit_le1_rate=sum(bool(edit_events(a, b)) for a, b in pairs) / len(pairs),
        mean_length=statistics.mean(map(len, words)),
        hapax_type_fraction=sum(n == 1 for n in vocabulary.values()) / len(vocabulary))


def summarize_simulations(draws, observed):
    out = {}
    for key, value in observed.items():
        values = sorted(x[key] for x in draws)
        lo, hi = values[1], values[-2]
        out[key] = dict(median=statistics.median(values), simulation_range=[lo, hi],
            observed=value, observed_in_range=lo <= value <= hi)
    return out


def evaluate(model, rows, rng):
    leaves, contexts, blocked = defaultdict(lambda: Counter()), [], 0
    for row in rows:
        for i in range(1, len(row['words'])):
            previous, word = row['words'][i - 1:i + 1]
            b = band(i, len(row['words']))
            stats = leaves[row['leaf']]
            stats['pairs'] += 1
            for kind in KINDS:
                stats[kind] -= math.log2(model.probability(word, previous, b, kind))
            sampler = model.matched_context_sampler(previous)
            if sampler is None:
                blocked += 1
                continue
            real = model.probability(word, previous, b, 'edge_copy')
            controls = [sampler.draw(rng) for _ in range(5)]
            if any(model.edge_probability(word, c, b) != model.edge_probability(word, previous, b) for c in controls):
                raise AssertionError('Matched context changed edge baseline')
            gain = math.log2(real) - statistics.mean(math.log2(model.probability(word, c, b, 'edge_copy')) for c in controls)
            contexts.append(gain)
    total = sum(r['pairs'] for r in leaves.values())
    nll = {kind: sum(r[kind] for r in leaves.values()) / total for kind in KINDS}
    leaf_rows = [dict(leaf=leaf, pairs=r['pairs'],
        bits_per_token={k: r[k] / r['pairs'] for k in KINDS},
        copy_gain_bits=(r['edge'] - r['edge_copy']) / r['pairs']) for leaf, r in sorted(leaves.items())]
    return dict(pairs=total, bits_per_token=nll, copy_gain_bits=nll['edge'] - nll['edge_copy'],
        leaf_balanced_copy_gain_bits=statistics.mean(x['copy_gain_bits'] for x in leaf_rows),
        leaves=leaf_rows, matched_context=dict(evaluated_pairs=len(contexts), blocked_pairs=blocked,
            actual_vs_counterfeit_gain_bits=statistics.mean(contexts) if contexts else None))


def validate_plan(plan):
    expected = {
        'source_blob': SOURCE_BLOB, 'strata': [list(x) for x in STRATA], 'seed': 20261007,
        'models': list(KINDS), 'version': 1,
    }
    if any(plan.get(k) != v for k, v in expected.items()):
        raise ValueError('Unsupported frozen plan')
    gates = [plan['reserve']['folds'] == 5, plan['reserve']['generation_fold'] == 0,
        plan['reserve']['minimum_training_tokens_per_stratum'] == 500,
        plan['word_base']['empirical_weight'] == .95,
        plan['word_base']['open_character_markov_weight'] == .05,
        plan['word_base']['character_alpha'] == .5,
        plan['word_base']['alphabet'] == ALPHABET,
        plan['word_base']['max_characters'] == 64,
        plan['word_base']['position_bands'] == 4,
        plan['edge']['shrinkage_to_base_first_character'] == 20,
        plan['copy']['kind_and_location_alpha'] == 1,
        plan['copy']['replacement_shrinkage_to_training_character_frequency'] == 20,
        plan['copy']['mixture_fit'] == '30 EM iterations, initial copy weight 0.1; all pairs from training only',
        plan['matched_context_probe']['draws_per_pair'] == 5,
        plan['simulation']['draws_per_model'] == 30,
        plan['simulation']['shuffles_per_draw_for_edge_excess'] == 19]
    if not all(gates):
        raise ValueError('Frozen plan parameters changed; implement a separate experiment')


def run(corpus, plan, out, simulations_out):
    validate_plan(plan)
    binary = corpus.read_bytes()
    if blob_sha(binary) != SOURCE_BLOB or hashlib.sha256(binary).hexdigest() != plan['source_sha256']:
        raise ValueError('Frozen corpus mismatch')
    leaves = sorted({physical_leaf(r['folio']) for r in parse(binary.decode(), 'split')[0]})
    assignment = {leaf: i % 5 for i, leaf in enumerate(leaves)}
    result = dict(status='PASS_EXECUTED', classification='EXPLORATORY_LOCAL_COPY_MECHANISM_NOT_TRANSLATION',
        source_blob=SOURCE_BLOB, plan_sha256=hashlib.sha256(json.dumps(plan, indent=2, ensure_ascii=False).encode() + b'\n').hexdigest(),
        environment=dict(python=platform.python_version(), dependencies='Python standard library only'),
        leaf_assignment=assignment, modes={}, semantic_gate='BLOCKED', translation='NOT_RUN', novelty='NOT_ESTABLISHED')
    generated = dict(classification='GENERATED_MECHANISTIC_TEXT_NOT_TRANSLATION',
        examples_scope='First five runs per stratum in first draw only; metrics use all generated runs', modes={})
    for mode_index, mode in enumerate(('split', 'join')):
        rows, audit = parse(binary.decode(), mode)
        folds, generation_models, test_geometry = [], {}, []
        for fold in range(5):
            fold_results = []
            for group_index, group in enumerate(STRATA):
                train = [r for r in rows if r['group'] == group and assignment[r['leaf']] != fold]
                test = [r for r in rows if r['group'] == group and assignment[r['leaf']] == fold]
                if sum(len(r['words']) for r in train) < 500 or not any(len(r['words']) > 1 for r in test):
                    raise ValueError('Predefined stratum blocked in fold: ' + str((fold, group)))
                model = Mechanism(train)
                evaluated = evaluate(model, test, random.Random(20261007 + 1000 * mode_index + 100 * fold + group_index))
                evaluated.update(group=list(group), training_tokens=sum(len(r['words']) for r in train),
                    training_copy_weight=model.gamma, training_copy_operations=dict(model.operations))
                fold_results.append(evaluated)
                if fold == 0:
                    generation_models[group] = model
                    test_geometry.extend(test)
            pairs = sum(g['pairs'] for g in fold_results)
            gain = sum(g['copy_gain_bits'] * g['pairs'] for g in fold_results) / pairs
            leaf_gains = defaultdict(list)
            for g in fold_results:
                for leaf in g['leaves']:
                    leaf_gains[leaf['leaf']].append(leaf)
            balanced = statistics.mean(sum(x['copy_gain_bits'] * x['pairs'] for x in ls) /
                sum(x['pairs'] for x in ls) for ls in leaf_gains.values())
            folds.append(dict(fold=fold, pairs=pairs, physical_leaves=len(leaf_gains),
                pooled_copy_gain_bits=gain, leaf_balanced_copy_gain_bits=balanced, strata=fold_results))
            print(mode, 'fold', fold, 'copy_gain_bits', round(gain, 9), 'leaf_balanced', round(balanced, 9), flush=True)
        total = sum(f['pairs'] for f in folds)
        pooled = sum(f['pooled_copy_gain_bits'] * f['pairs'] for f in folds) / total
        balanced = sum(f['leaf_balanced_copy_gain_bits'] * f['physical_leaves'] for f in folds) / sum(f['physical_leaves'] for f in folds)
        observed = metrics([r['words'] for r in test_geometry], random.Random(20261007))
        draws, examples, raw_draws = {}, {}, {}
        for kind_index, kind in enumerate(KINDS):
            samples, sample_sizes = [], []
            for draw in range(30):
                rng = random.Random(20261007 + 100000 * mode_index + 1000 * kind_index + draw)
                runs = []
                for row in test_geometry:
                    model, words = generation_models[row['group']], []
                    for i in range(len(row['words'])):
                        words.append(model.sample(words[-1] if words else None, band(i, len(row['words'])), kind, rng))
                    runs.append(words)
                samples.append(metrics(runs, rng))
                sample_sizes.append(dict(tokens=sum(map(len, runs)), types=len({w for r in runs for w in r})))
                if draw == 0:
                    selected, counts = [], Counter()
                    for r, w in zip(test_geometry, runs):
                        if counts[r['group']] < 5:
                            selected.append(dict(locus=r['locus'], group=list(r['group']), words=w))
                            counts[r['group']] += 1
                    examples[kind] = selected
            draws[kind] = summarize_simulations(samples, observed)
            raw_draws[kind] = dict(metrics=samples, vocabulary_sizes=sample_sizes)
            print(mode, kind, 'metrics_in_simulation_range', sum(x['observed_in_range'] for x in draws[kind].values()), '/7', flush=True)
        numeric = pooled > 0 and balanced > 0 and all(f['pooled_copy_gain_bits'] > 0 for f in folds)
        result['modes'][mode] = dict(parser_audit=audit, tokens=sum(len(r['words']) for r in rows), pairs=total,
            physical_leaves=len(assignment), pooled_copy_gain_bits=pooled, leaf_balanced_copy_gain_bits=balanced,
            positive_gain_every_fold=all(f['pooled_copy_gain_bits'] > 0 for f in folds), copy_channel_numeric_support=numeric,
            folds=folds, simulation=dict(fold=0, draws=30, geometry_tokens=sum(len(r['words']) for r in test_geometry),
                observed=observed, controls=draws, raw_draws=raw_draws))
        generated['modes'][mode] = examples
    result['copy_channel_numeric_support_both_modes'] = all(x['copy_channel_numeric_support'] for x in result['modes'].values())
    simulations_out.parent.mkdir(parents=True, exist_ok=True)
    simulations_out.write_text(json.dumps(generated, ensure_ascii=False, separators=(',', ':')) + '\n')
    result['generated_samples_sha256'] = hashlib.sha256(simulations_out.read_bytes()).hexdigest()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(status=result['status'], classification=result['classification'],
        plan_sha256=result['plan_sha256'], generated_samples_sha256=result['generated_samples_sha256'],
        copy_channel_numeric_support_both_modes=result['copy_channel_numeric_support_both_modes'],
        modes={m: {k: v[k] for k in ('tokens', 'pairs', 'physical_leaves', 'pooled_copy_gain_bits',
            'leaf_balanced_copy_gain_bits', 'positive_gain_every_fold')} for m, v in result['modes'].items()},
        semantic_gate=result['semantic_gate'], translation=result['translation'], novelty=result['novelty']), indent=2), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--corpus', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--samples', type=Path, required=True)
    args = p.parse_args()
    run(args.corpus, json.loads(args.plan.read_text()), args.out, args.samples)


if __name__ == '__main__':
    main()
