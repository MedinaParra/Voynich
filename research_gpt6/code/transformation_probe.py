#!/usr/bin/env python3
"""Bounded affix-rule generation, exploratory and explicitly not a translation.

Fit one shared rule on training captions. Hold out a physical pharma leaf and
purge all its herbal families from training. Generate strings without consulting
held-out caption strings. Score only after saving the predictions.
"""
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import re
import string

BENCHES = ('ckh', 'cth', 'cph', 'cfh', 'ch', 'sh')
ALPHABET = tuple(string.ascii_lowercase) + BENCHES
EOS = '<E>'


def blob_sha(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


@lru_cache(maxsize=150000)
def units(word):
    if not re.fullmatch('[a-z]+', word):
        raise ValueError('Ambiguous/nonliteral EVA word')
    out = []
    while word:
        u = next((u for u in BENCHES if word.startswith(u)), word[0])
        out.append(u)
        word = word[len(u):]
    return tuple(out)


def clean_tokens(raw):
    raw = re.sub(r'<![^>]*>|<%>|<\$>', '', raw).replace('<->', '.')
    return [w for w in raw.split('.') if re.fullmatch('[a-z]{2,}', w)]


def parse(raw):
    pages, labels = {}, []
    for line in raw.splitlines():
        head = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if head:
            folio, meta = head.groups()
            meta = dict(re.findall(r'\$([A-Z])=([^\s>]+)', meta))
            pages[folio] = dict(folio=folio, quire=meta.get('Q', '?'), currier=meta.get('L', '?'),
                hand=meta.get('H', '?'), section=meta.get('I', '?'),
                tokens=[], plant_labels=[])
            continue
        match = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not match or ',' not in match[1]:
            continue
        locus, text = match.groups()
        folio, tag = locus.split('.')[0], locus.split(',', 1)[1]
        if folio not in pages:
            continue
        if tag[1:2] == 'P':
            pages[folio]['tokens'].extend(clean_tokens(text.strip()))
        literal = re.sub(r'<![^>]*>', '', text).strip()
        if 'Lp' in tag:
            pages[folio]['plant_labels'].append(literal)
        if 'Lf' in tag:
            number = re.search(r'<!([0-9]+)([ab]?)(?:/[^>]*)?>', text)
            labels.append(dict(locus=locus, folio=folio, text=literal,
                fragment=number[1] if number else None,
                suffix=number[2] if number else None,
                literal=bool(re.fullmatch('[a-z]{2,}', literal))))
    return pages, labels


def physical_leaf(folio):
    match = re.match(r'f[0-9]+', folio)
    if not match:
        raise ValueError('No physical leaf identifier')
    return match[0]


def build_cases(pages, labels, inventory):
    cases, excluded = [], []
    multiplicity = Counter((r['pharma'], r['fragment']) for r in inventory['relations'])
    for row in inventory['relations']:
        reasons = []
        key = (row['pharma'], row['fragment'])
        if multiplicity[key] != 1:
            reasons.append('One fragment linked to multiple proposed herbal families')
        found = [l for l in labels if (l['folio'], l['fragment']) == key]
        if len(found) != 1:
            reasons.append('No unique raw Lf label carrying the numeric fragment ID')
        elif not found[0]['literal']:
            reasons.append('Caption ambiguous or multiword')
        page = pages.get(row['herbal'])
        if not page or not page['tokens']:
            reasons.append('No strict herbal paragraph tokens')
        pharma_page = pages.get(row['pharma'])
        if page and pharma_page:
            source_group = (page['currier'], page['hand'])
            pharma_group = (pharma_page['currier'], pharma_page['hand'])
            if '?' in source_group + pharma_group or source_group != pharma_group:
                reasons.append('Source and caption differ in Currier or scribal hand, or metadata missing')
        if reasons:
            excluded.append(dict(relation=row, reasons=reasons))
            continue
        label = found[0]
        cases.append(dict(id=row['pharma'] + ':' + row['fragment'],
            entity=row['herbal'], source_folio=row['herbal'],
            source_words=tuple(sorted(set(page['tokens']))),
            source_token_count=len(page['tokens']),
            source_meta=(page['currier'], page['hand'], page['section']),
            source_local_plant_labels=page['plant_labels'],
            pharma=row['pharma'], leaf=physical_leaf(row['pharma']),
            pharma_quire=pharma_page['quire'],
            label=label['text'], label_locus=label['locus'], relation=row))
    return cases, excluded


def affix_splits(seq):
    for left in range(3):
        for right in range(3):
            end = len(seq) - right
            if end - left >= 3:
                yield seq[left:end], seq[:left], seq[end:]


@lru_cache(maxsize=150000)
def pair_rules(word, caption):
    if word == caption:
        return frozenset()
    source = defaultdict(list)
    for middle, prefix, suffix in affix_splits(units(word)):
        source[middle].append((prefix, suffix))
    found = set()
    for middle, new_prefix, new_suffix in affix_splits(units(caption)):
        for old_prefix, old_suffix in source.get(middle, []):
            rule = (old_prefix, old_suffix, new_prefix, new_suffix)
            if (old_prefix, old_suffix) != (new_prefix, new_suffix):
                found.add(rule)
    return frozenset(found)


@lru_cache(maxsize=15000)
def document_rules(words, caption):
    return frozenset(r for w in words for r in pair_rules(w, caption))


def edit_distance(a, b):
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        nxt = [i]
        for j, y in enumerate(b, 1):
            nxt.append(min(nxt[-1] + 1, row[j] + 1, row[j - 1] + (x != y)))
        row = nxt
    return row[-1]


def learn_rule(train):
    supported = defaultdict(list)
    for case in train:
        for rule in document_rules(case['source_words'], case['label']):
            supported[rule].append(case)
    eligible = []
    for rule, rows in supported.items():
        entities = {r['entity'] for r in rows}
        leaves = {r['leaf'] for r in rows}
        if len(entities) >= 2 and len(leaves) >= 2:
            cost = edit_distance(rule[0], rule[2]) + edit_distance(rule[1], rule[3])
            key = (-len(entities), -len(leaves), cost, sum(map(len, rule)), rule)
            eligible.append((key, rule, sorted(entities), sorted(leaves)))
    if not eligible:
        return None, dict(eligible_rules=0, mode='IDENTITY_FALLBACK')
    _, rule, entities, leaves = min(eligible)
    return rule, dict(eligible_rules=len(eligible), mode='ONE_AFFIX_RULE',
        supporting_entities=entities, supporting_leaves=leaves)


def apply_rule(word, rule):
    if rule is None:
        return word
    seq = units(word)
    old_prefix, old_suffix, new_prefix, new_suffix = rule
    if seq[:len(old_prefix)] != old_prefix:
        return None
    if old_suffix and seq[-len(old_suffix):] != old_suffix:
        return None
    end = len(seq) - len(old_suffix)
    middle = seq[len(old_prefix):end]
    if len(middle) < 3:
        return None
    return ''.join(new_prefix + middle + new_suffix)


class CaptionModel:
    def __init__(self, captions):
        self.bigram, self.context, self.lengths = Counter(), Counter(), Counter()
        self.n = len(captions)
        for text in captions:
            seq = ('<B>',) + units(text) + (EOS,)
            self.lengths[len(seq) - 2] += 1
            for a, b in zip(seq, seq[1:]):
                self.bigram[a, b] += 1
                self.context[a] += 1

    def score(self, text):
        seq = ('<B>',) + units(text) + (EOS,)
        logp = sum(math.log((self.bigram[a, b] + .5) /
            (self.context[a] + .5 * (len(ALPHABET) + 1)))
            for a, b in zip(seq, seq[1:])) / (len(seq) - 1)
        return logp + math.log((self.lengths[len(seq) - 2] + 1) / (self.n + 64))


def ranked_generation(words, rule, model):
    generated = {out for w in words if (out := apply_rule(w, rule))}
    return sorted(((word, model.score(word)) for word in generated),
        key=lambda x: (-x[1], x[0]))


def predict(cases):
    predictions, folds = [], []
    for leaf in sorted({c['leaf'] for c in cases}):
        test = [c for c in cases if c['leaf'] == leaf]
        entities = {c['entity'] for c in test}
        raw_train = [c for c in cases if c['leaf'] != leaf]
        train = [c for c in raw_train if c['entity'] not in entities]
        if not train:
            raise ValueError('No training cases after family purge')
        rule, fit = learn_rule(train)
        model = CaptionModel([c['label'] for c in train])
        folds.append(dict(leaf=leaf, test_n=len(test), train_n=len(train),
            purged_shared_entities=len(raw_train) - len(train),
            rule=rule, fit=fit))
        for case in test:
            # No held-out caption value is read here.
            predictions.append(dict(id=case['id'], entity=case['entity'], leaf=leaf,
                source_folio=case['source_folio'],
                learned=ranked_generation(case['source_words'], rule, model),
                identity=ranked_generation(case['source_words'], None, model)))
    return predictions, folds


def rank_exact(outputs, caption):
    lookup = dict(outputs)
    if caption not in lookup:
        return dict(generated=False, rank_min=None, rank_max=None,
            unique_top1=False, conservative_top5=False)
    score = lookup[caption]
    better = sum(s > score + 1e-12 for _, s in outputs)
    tied = sum(abs(s - score) <= 1e-12 for _, s in outputs)
    return dict(generated=True, rank_min=better + 1, rank_max=better + tied,
        unique_top1=better == 0 and tied == 1, conservative_top5=better + tied <= 5)


def score_predictions(predictions, cases):
    actual = {c['id']: c for c in cases}
    rows = []
    for pred in predictions:
        case = actual[pred['id']]
        row = dict(id=pred['id'], entity=case['entity'], caption=case['label'])
        for method in ('learned', 'identity'):
            row[method] = dict(rank_exact(pred[method], case['label']),
                generated_candidates=len(pred[method]), first5=[w for w, _ in pred[method][:5]])
        rows.append(row)
    summary = {'n': len(rows)}
    for method in ('learned', 'identity'):
        summary[method] = {metric: sum(r[method][metric] for r in rows)
            for metric in ('generated', 'unique_top1', 'conservative_top5')}
        counts = sorted(r[method]['generated_candidates'] for r in rows)
        summary[method]['candidate_counts'] = counts
    return rows, summary


def control_pools(pages, cases, inventory):
    used = {r['herbal'] for r in inventory['relations']}
    pools = {}
    for case in cases:
        entity, meta, n = case['entity'], case['source_meta'], case['source_token_count']
        pools[entity] = sorted(p['folio'] for p in pages.values()
            if p['folio'] not in used and p['tokens']
            and (p['currier'], p['hand'], p['section']) == meta
            and .8 * n <= len(p['tokens']) <= 1.2 * n)
    return pools


def sample_assignment(pools, rng):
    shuffled = {e: rng.sample(pool, len(pool)) for e, pool in pools.items()}
    owned = {}

    def assign(entity, seen):
        for page in shuffled[entity]:
            if page in seen:
                continue
            seen.add(page)
            if page not in owned or assign(owned[page], seen):
                owned[page] = entity
                return True
        return False

    for entity in sorted(pools, key=lambda e: (len(pools[e]), e)):
        if not assign(entity, set()):
            raise ValueError('No injective matched wrong-herbal assignment')
    return {entity: page for page, entity in owned.items()}


def run(corpus, inventory, plan, predictions_path):
    if blob_sha(corpus) != inventory['source_blob'] or blob_sha(corpus) != plan['source_blob']:
        raise ValueError('Frozen corpus mismatch')
    pages, labels = parse(corpus.decode())
    cases, excluded = build_cases(pages, labels, inventory)
    predictions, folds = predict(cases)
    # This artifact is written before the held-out captions are scored.
    predictions_path.write_text(json.dumps(dict(classification='PREDICTIONS_NOT_TRANSLATIONS',
        folds=folds, predictions=predictions), separators=(',', ':')) + '\n')
    rows, summary = score_predictions(predictions, cases)
    pools = control_pools(pages, cases, inventory)
    rng = random.Random(plan['random_seed'])
    controls, blocked = [], None
    try:
        for _ in range(plan['wrong_correspondence_trials']):
            mapping = sample_assignment(pools, rng)
            wrong = [dict(c, source_folio=mapping[c['entity']],
                source_words=tuple(sorted(set(pages[mapping[c['entity']]]['tokens'])))) for c in cases]
            pred, _ = predict(wrong)
            _, score = score_predictions(pred, wrong)
            controls.append(score)
    except ValueError as error:
        blocked = str(error)
    benchmark = dict(requested=plan['wrong_correspondence_trials'], completed=len(controls),
        blocked=blocked, eligible_control_pages={e: len(p) for e, p in pools.items()},
        classification='EXPLORATORY_WRONG_MATCH_BENCHMARK_NOT_P_VALUE')
    if controls:
        benchmark['distribution'] = {method: {metric: {
            'mean': sum(x[method][metric] for x in controls) / len(controls),
            'max': max(x[method][metric] for x in controls),
            'fraction_at_least_observed': sum(x[method][metric] >= summary[method][metric]
                for x in controls) / len(controls)}
            for metric in ('generated', 'unique_top1', 'conservative_top5')}
            for method in ('learned', 'identity')}
    contrasts = inventory.get('eligible_semantic_contrasts', [])
    return dict(status='PASS_EXECUTED', classification='BOUNDED_TEXT_RULE_PILOT_NOT_TRANSLATION',
        source_blob=blob_sha(corpus), inventory_relations=len(inventory['relations']),
        usable_pairs=len(cases), distinct_herbal_entities=len({c['entity'] for c in cases}),
        physical_source_leaves=sorted({c['leaf'] for c in cases}),
        pharmaceutical_quires=sorted({c['pharma_quire'] for c in cases}),
        raw_source_plant_labels_found=sum(bool(c['source_local_plant_labels']) for c in cases),
        excluded_relations=excluded, folds=folds, observations=rows, summary=summary,
        wrong_correspondence_benchmark=benchmark,
        independently_verified_part_contrast_families=len(contrasts),
        semantic_gate='BLOCKED', semantic_reason='No independently verified localized root/leaf contrasts; source inputs are paragraphs, not established plant names',
        transformation_claim='Exploratory only; see exact predictions and identity baseline',
        translation='NOT_RUN', novelty='NOT_ESTABLISHED', environment={'python': platform.python_version()},
        limitations=['Visual identities remain tentative and selection is not blinded',
            'All usable pharma captions come from one quire (S / quire 19)',
            'Known corpus reused; held-out leaf generation is not fresh semantic validation',
            'EVA bench segmentation is a convention, not recovered phonology',
            'One affix rule with a preserved middle tests only a restricted channel',
            'Root/leaf effects cannot be inferred from herbal-to-pharma section differences',
            'Wrong-match assignments are constrained and not uniform formal permutations'])


def main():
    ap = argparse.ArgumentParser()
    for name in ('corpus', 'inventory', 'plan', 'predictions', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    a = ap.parse_args()
    inventory_bytes, plan_bytes = a.inventory.read_bytes(), a.plan.read_bytes()
    plan = json.loads(plan_bytes)
    if hashlib.sha256(inventory_bytes).hexdigest() != plan['inventory_sha256']:
        raise ValueError('Frozen inventory mismatch')
    result = run(a.corpus.read_bytes(), json.loads(inventory_bytes), plan, a.predictions)
    result['inventory_sha256'] = hashlib.sha256(inventory_bytes).hexdigest()
    result['plan_sha256'] = hashlib.sha256(plan_bytes).hexdigest()
    result['predictions_sha256'] = hashlib.sha256(a.predictions.read_bytes()).hexdigest()
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
        if k not in ('excluded_relations', 'observations')}, indent=2))
    for row in result['observations']:
        print(row['entity'], row['caption'], 'learned', row['learned']['unique_top1'],
            row['learned']['rank_min'], 'identity', row['identity']['unique_top1'],
            row['identity']['rank_min'])


if __name__ == '__main__':
    main()
