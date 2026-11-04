#!/usr/bin/env python3
"""Independent post-reveal audit of fixed homophonic and bijective controls.

No imports from generator, solver, evaluator or NumPy. PASS means accounting
and commitments agree, not that a recovery gate passed or Voynich was decoded.
Run only after prediction publication and explicit authorization to reveal.
"""
import argparse
import array
import base64
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
import re
from pathlib import Path
import statistics
import sys

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


def raw(path):
    if path.exists():
        data = path.read_bytes()
        return gzip.decompress(data) if path.suffix == '.gz' else data
    return gzip.decompress(path.with_suffix(path.suffix + '.gz').read_bytes())


def read(path):
    return json.loads(raw(path))


def sha(path):
    return hashlib.sha256(raw(path)).hexdigest()


def letters(text):
    if not isinstance(text, str) or any(c not in ALPHABET+' ' for c in text):
        raise ValueError('Expected lowercase cipher/plaintext and literal spaces only')
    return text.replace(' ', '')


def apply_key(ciphertext, key):
    if not isinstance(key, str) or len(key) != 26 or any(c not in ALPHABET for c in key):
        raise ValueError('Expected 26 lowercase cipher-to-plain assignments')
    return ''.join(' ' if c == ' ' else key[ord(c)-97] for c in ciphertext)


def quantized_score(text, model):
    values = [ord(c)-97 for c in letters(text)]
    total = 0
    for i in range(len(values)-3):
        a,b,c,d = values[i:i+4]
        total += model[((a*26+b)*26+c)*26+d]
    return total


def recovery_metrics(ciphertext, plaintext, truth_key, predicted_key):
    expected = letters(plaintext)
    candidate = letters(apply_key(ciphertext, predicted_key))
    if len(expected) != len(candidate) or not expected:
        raise ValueError('Expected equal, nonzero plaintext lengths')
    correct = sum(a == b for a,b in zip(expected, candidate))
    observed = ''.join(sorted(set(letters(ciphertext))))
    key_correct = sum(predicted_key[ord(c)-97] == truth_key[ord(c)-97] for c in observed)
    return {'character_accuracy':correct/len(expected),
            'characters_correct':correct, 'characters_total':len(expected),
            'all_exact':correct == len(expected),
            'observed_symbol_key_accuracy':key_correct/len(observed),
            'observed_symbols_correct':key_correct,
            'observed_symbols_total':len(observed),
            'unobserved_cipher_symbols':''.join(c for c in ALPHABET if c not in observed)}


def bijective_ceiling(ciphertext, plaintext):
    cipher, plain = letters(ciphertext), letters(plaintext)
    if len(cipher) != len(plain):
        raise ValueError('Unequal plaintext/ciphertext lengths')
    counter = Counter(zip(cipher, plain))
    owner = defaultdict(set)
    for c,p in counter:
        owner[c].add(p)
    if any(len(values) != 1 for values in owner.values()):
        raise ValueError('Ceiling shortcut needs disjoint fixed homophone groups')
    by_plain = defaultdict(list)
    for (c,p),n in counter.items():
        by_plain[p].append(n)
    return sum(max(values) for values in by_plain.values())


class Checks:
    def __init__(self):
        self.count = 0
        self.mismatches = []
    def check(self, name, actual, expected=True):
        self.count += 1
        equal = math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12) if isinstance(actual,float) or isinstance(expected,float) else actual == expected
        if not equal:
            self.mismatches.append({'check':name,'actual':actual,'expected':expected})



EXPECTED_LM_SHA256 = '9206bde5bb6252ddb4de70dd2ea28aef6cc0ca5f59effbc2deac3e34546eae77'
EXPECTED_CONFIG_BLOB = '19e4eac0fa0b28150bd9a132385f32b14fcf3213'
EXPECTED_SOURCE_COMMIT = '960254605ab910ed90af8d3a8cc7278bbb202185'
EXPECTED_LATIN_BLOB = '78cac8d327438695cd226a62529ad7ac078f59d1'
ROLES = ('monoalphabetic_positive', 'homophonic_positive', 'frequency_matched_null')
METHODS = ('bijective', 'many_to_one')


def git_blob_bytes(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()


def git_blob(path):
    return git_blob_bytes(raw(path))


def normalize_source(payload):
    lines = payload.decode('utf-8').splitlines()
    return ''.join(re.findall('[a-z]+', ' '.join(line for line in lines[1:] if not line.isupper()).lower()))


def index_rows(document, checks, label):
    rows = document['cases']
    checks.check(label+'/cases_is_list', isinstance(rows, list))
    checks.check(label+'/no_duplicate_ids', len(rows), len({r['id'] for r in rows}))
    return {r['id']:r for r in rows}


def checked_key(key):
    if not isinstance(key, str) or len(key) != 26 or any(c not in ALPHABET for c in key):
        raise ValueError('Key must have exactly 26 lowercase assignments; repetitions are allowed')
    return key


def observed_key_ceiling(ciphertext, plaintext):
    cipher, plain = letters(ciphertext), letters(plaintext)
    # Also validates unique ownership before using the shortcut.
    bijective_ceiling(cipher, plain)
    return len(set(plain)), len(set(cipher))


def controls(checks):
    shifted = ALPHABET[7:]+ALPHABET[:7]
    m = recovery_metrics('abc abc', 'hij hij', shifted, shifted)
    checks.check('control/known_shift', m['all_exact'])
    checks.check('control/observed_only', m['observed_symbols_total'], 3)
    changed = list(shifted); changed[25] = 'a'
    m2 = recovery_metrics('abc abc', 'hij hij', shifted, ''.join(changed))
    checks.check('control/absent_assignment_is_not_error', m2['observed_symbols_correct'], 3)
    key = 'xxy'+ALPHABET[3:]
    checks.check('control/repeated_assignments_valid', apply_key('aaabbc', key), 'xxxxxy')
    checks.check('control/weighted_bijective_ceiling', bijective_ceiling('aaabbc', 'xxxxxy'), 4)
    attainable = 'xzy'+ALPHABET.replace('x','').replace('z','').replace('y','')
    candidate = apply_key('aaabbc', attainable)
    checks.check('control/ceiling_attained_by_bijection', ''.join(sorted(attainable)), ALPHABET)
    checks.check('control/ceiling_attained_character_count', sum(a==b for a,b in zip(candidate,'xxxxxy')), 4)
    checks.check('control/equal_alias_tie_ceiling', bijective_ceiling('aabbcc', 'xxxxzz'), 4)
    checks.check('control/mono_ceiling_is_all_characters', bijective_ceiling('ababa', 'xyxyx'), 5)
    checks.check('control/observed_key_ceiling', observed_key_ceiling('aaabbc', 'xxxxxy'), (2,3))
    rejected = False
    try: bijective_ceiling('aa', 'xy')
    except ValueError: rejected = True
    checks.check('control/nonfixed_owner_rejected', rejected)
    model = array.array('i', [0])*(26**4)
    for i,v in [(731,11),(19006,23),(37181,5),(52756,-2)]: model[i] = v
    checks.check('control/manual_quadgram_overlap_index', quantized_score('abcd abcd',model), 48)
    checks.check('control/short_plaintext_unscored', quantized_score('abc',model), 0)
    wrong = list(shifted); wrong[0],wrong[1] = wrong[1],wrong[0]
    m = recovery_metrics('abc abc', 'hij hij', shifted, ''.join(wrong))
    checks.check('control/character_hamming', m['characters_correct'], 2)
    checks.check('control/observed_key_hamming', m['observed_symbols_correct'], 1)
    return {'description':'Known substitution and repeated assignments; absent symbols; attainable bijective ceilings, ties and invalid ownership; manually indexed overlapping quadgrams.',
            'scope':'Mathematical controls only; no new Latin or Voynich cases.'}


def location(repo, path):
    relative = Path(path)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Source hash path must be repository-relative')
    # Accept --repo as either git root or research_gpt6, without reading outside it.
    if (repo/relative).exists() or (repo/relative).with_suffix((repo/relative).suffix+'.gz').exists():
        return repo/relative
    if relative.parts and relative.parts[0] == repo.name:
        return repo/Path(*relative.parts[1:])
    raise FileNotFoundError('Source hash path absent: '+str(path))


def objective_diagnostic(exact, predicted_score, gold_score, representable):
    if exact: return 'exact_plaintext_recovered'
    if not representable: return 'gold_outside_bijective_family'
    if predicted_score < gold_score: return 'representable_gold_outranks_candidate'
    if predicted_score > gold_score: return 'candidate_outranks_different_gold'
    return 'objective_tie_with_wrong_text'


def audit(repo, bundle, lm_path=None, prior_path=None, latin_path=None):
    checks = Checks()
    control_summary = controls(checks)
    public_path = bundle/'public/ciphertexts.json'
    manifest_path = bundle/'public/manifest.json'
    truth_path = bundle/'reveal/truth.json'
    pred_path = bundle/'predictions.json'
    freeze_path = bundle/'freeze.json'
    lm_path = lm_path or repo/'results/known_cipher_recovery/model/lm_int32.bin'
    prior_path = prior_path or repo/'results/known_cipher_recovery/reveal/truth.json'
    latin_path = latin_path or repo/'data/latin_sources.json'
    public, manifest, truth, predictions, freeze = map(read, [public_path,manifest_path,truth_path,pred_path,freeze_path])
    public_rows = index_rows(public, checks, 'public')
    true_rows = index_rows(truth, checks, 'truth')
    checks.check('schema/public', public['schema'], 'mapping-freedom-cases-v1')
    checks.check('schema/manifest', manifest['schema'], 'mapping-freedom-public-v1')
    checks.check('schema/truth', truth['schema'], 'mapping-freedom-truth-v1')
    checks.check('schema/predictions', predictions['schema_version'], 1)
    checks.check('schema/experiment', truth['experiment'], 88)
    checks.check('schema/manifest_case_count', manifest['case_count'], 9)
    checks.check('schema/manifest_length', manifest['letters_per_case'], 2000)
    checks.check('schema/manifest_spacing', manifest['spacing'], 'none')
    checks.check('schema/manifest_alphabet', manifest['alphabet'], ALPHABET)
    checks.check('case_ids/public_equal_truth', sorted(public_rows), sorted(true_rows))
    checks.check('case_ids/exact_nine', sorted(true_rows), ['U%02d'%i for i in range(1,10)])
    checks.check('hash/public_manifest_git_blob', git_blob(manifest_path), freeze['public_manifest_git_blob'])
    checks.check('hash/public_ciphertexts_git_blob', git_blob(public_path), manifest['ciphertexts_git_blob_sha1'])
    checks.check('hash/revealed_truth_git_blob', git_blob(truth_path), manifest['truth_git_blob_sha1'])
    checks.check('hash/predictions_git_blob', git_blob(pred_path), freeze['predictions_git_blob'])
    checks.check('hash/predictions_sha256', sha(pred_path), freeze['prediction_sha256'])
    checks.check('config/freeze_equals_predictions', freeze['config_git_blob'], predictions['config_git_blob'])
    checks.check('config/frozen_preregistered_plan', predictions['config_git_blob'], EXPECTED_CONFIG_BLOB)
    checks.check('config/known_language_assumption', predictions['language_assumption'], 'known Latin')
    checks.check('source/pinned_model_commit', predictions['model_source_commit'], EXPECTED_SOURCE_COMMIT)
    checks.check('source/pinned_truth_commit', truth['source_commit'], EXPECTED_SOURCE_COMMIT)
    checks.check('hash/model_from_plan', sha(lm_path), EXPECTED_LM_SHA256)
    checks.check('hash/model_from_manifest', sha(lm_path), manifest['lm_sha256'])
    checks.check('hash/prior_truth_from_manifest', git_blob(prior_path), manifest['prior_truth_git_blob_sha1'])
    checks.check('hash/prior_truth_from_truth', git_blob(prior_path), truth['prior_truth_git_blob_sha1'])
    # Hash consistency cannot prove historical publication order or human isolation.
    checks.check('freeze/publication_commit_is_sha1', isinstance(freeze['publication_commit'],str) and len(freeze['publication_commit'])==40 and all(c in '0123456789abcdef' for c in freeze['publication_commit']))
    source_hashes = predictions['source_hashes']
    checks.check('source_hashes/nonempty', isinstance(source_hashes,dict) and bool(source_hashes))
    for path,expected in sorted(source_hashes.items()):
        checks.check('source_hash/'+path, sha(location(repo,path)), expected)
    data = raw(lm_path)
    checks.check('model/exact_int32_byte_count', len(data), 4*26**4)
    model = array.array('i')
    if model.itemsize != 4: raise ValueError('Host signed int is not 32 bits')
    model.frombytes(data)
    if sys.byteorder != 'little': model.byteswap()
    latin = read(latin_path)
    checks.check('hash/pinned_latin_bundle', git_blob(latin_path), EXPECTED_LATIN_BLOB)
    checks.check('hash/public_latin_bundle', git_blob(latin_path), manifest['source_bundle_git_blob_sha1'])
    checks.check('hash/truth_latin_bundle', git_blob(latin_path), truth['source_bundle_git_blob_sha1'])
    checks.check('source/original_latin_commit', truth['latin_source_commit'], latin['commit'])
    entries = latin['files']
    checks.check('source/no_duplicate_paths', len(entries), len({entry['path'] for entry in entries}))
    source_text = {}
    for entry in entries:
        payload = base64.b64decode(''.join(entry['base64'].split()), validate=True)
        checks.check('source/'+entry['path']+'/git_blob', git_blob_bytes(payload), entry['sha'])
        checks.check('source/'+entry['path']+'/byte_size', len(payload), entry['size'])
        source_text[entry['path']] = normalize_source(payload)
    prior = read(prior_path)
    prior_intervals = [(r['source_path'],r['letter_start'],r['letter_end_exclusive']) for r in prior['cases']]
    grouped_truth = defaultdict(list)
    ceilings = {}
    for name,t in sorted(true_rows.items()):
        label = 'truth/'+name+'/'
        cipher,plain,key = t['ciphertext'],t['plaintext'],checked_key(t['decryption_key_cipher_to_plain'])
        checks.check(label+'role_allowed', t['role'] in ROLES)
        checks.check(label+'variant', t['variant'], 'no_spaces')
        checks.check(label+'pair_id', t['pair_id'] in ('P1','P2','P3'))
        checks.check(label+'cipher_public_unchanged', cipher, public_rows[name]['ciphertext'])
        checks.check(label+'cipher_2000_letters_without_spaces', len(cipher)==2000 and letters(cipher)==cipher)
        checks.check(label+'plaintext_2000_letters_without_spaces', len(plain)==2000 and letters(plain)==plain)
        checks.check(label+'truth_stream', plain, t['letters_plaintext'])
        checks.check(label+'declared_length', t['letters_total'], 2000)
        checks.check(label+'true_key_decodes_cipher', apply_key(cipher,key), plain)
        observed = ''.join(sorted(set(cipher)))
        checks.check(label+'observed_symbols', t['observed_cipher_symbols'], observed)
        checks.check(label+'declared_interval_2000', t['letter_end_exclusive']-t['letter_start'], 2000)
        checks.check(label+'declared_interval_nonnegative', isinstance(t['letter_start'],int) and t['letter_start']>=0)
        original = source_text[t['source_path']]
        checks.check(label+'interval_within_source', t['letter_end_exclusive']<=len(original))
        source_window = original[t['letter_start']:t['letter_end_exclusive']]
        if t['role']!='frequency_matched_null':
            checks.check(label+'exact_source_window', plain, source_window)
        else:
            checks.check(label+'null_preserves_source_letter_counts', dict(Counter(plain)), dict(Counter(source_window)))
        overlaps = [(s,a,b) for s,a,b in prior_intervals if s==t['source_path'] and max(a,t['letter_start'])<min(b,t['letter_end_exclusive'])]
        checks.check(label+'disjoint_all_previous_intervals', overlaps, [])
        ceiling = bijective_ceiling(cipher,plain)
        ceilings[name] = ceiling
        checks.check(label+'declared_bijective_ceiling', t['bijective_ceiling_correct_letters'], ceiling)
        if t['role']=='monoalphabetic_positive':
            checks.check(label+'mono_true_key_bijection', ''.join(sorted(key)), ALPHABET)
            encryption = checked_key(t['encryption_key_plain_to_cipher'])
            checks.check(label+'mono_encryption_bijection', ''.join(sorted(encryption)), ALPHABET)
            checks.check(label+'mono_encrypt_plaintext', apply_key(plain,encryption), cipher)
            checks.check(label+'mono_inverse_keys', ''.join(key[ord(c)-97] for c in encryption), ALPHABET)
            checks.check(label+'mono_ceiling_full', ceiling, 2000)
        else:
            aliases = t['aliases_plain_to_cipher']
            flattened = [c for group in aliases.values() for c in group]
            checks.check(label+'aliases_cover_cipher_alphabet_once', ''.join(sorted(flattened)), ALPHABET)
            checks.check(label+'aliases_match_true_key', all(p in ALPHABET and isinstance(group,list) and bool(group) and all(key[ord(c)-97]==p for c in group) for p,group in aliases.items()))
            checks.check(label+'actual_observed_homophony', ceiling<2000)
        grouped_truth[t['pair_id']].append(t)
    role_counts = Counter(t['role'] for t in true_rows.values())
    checks.check('design/exact_role_counts', dict(role_counts), {role:3 for role in ROLES})
    checks.check('design/three_content_pairs', sorted(grouped_truth), ['P1','P2','P3'])
    pairs = []
    for pair_id, group in sorted(grouped_truth.items()):
        by_role = {t['role']:t for t in group}
        checks.check('pair/'+pair_id+'/three_roles_once', sorted(t['role'] for t in group), sorted(ROLES))
        mono,homo,null = [by_role[r] for r in ROLES]
        checks.check('pair/'+pair_id+'/same_positive_plaintext', mono['plaintext'], homo['plaintext'])
        for field in ['source_path','letter_start','letter_end_exclusive']:
            checks.check('pair/'+pair_id+'/same_source_'+field, mono[field], homo[field])
            checks.check('pair/'+pair_id+'/null_parent_source_'+field, null[field], homo[field])
        checks.check('pair/'+pair_id+'/null_parent_id', null['parent_homophonic_id'], homo['id'])
        checks.check('pair/'+pair_id+'/null_preserves_cipher_counts', dict(Counter(null['ciphertext'])), dict(Counter(homo['ciphertext'])))
        checks.check('pair/'+pair_id+'/null_is_different_order', null['ciphertext']!=homo['ciphertext'])
        checks.check('pair/'+pair_id+'/null_same_decryption', null['decryption_key_cipher_to_plain'], homo['decryption_key_cipher_to_plain'])
        checks.check('pair/'+pair_id+'/null_same_aliases', null['aliases_plain_to_cipher'], homo['aliases_plain_to_cipher'])
        checks.check('pair/'+pair_id+'/null_same_ceiling', ceilings[null['id']], ceilings[homo['id']])
        pairs.append({'pair_id':pair_id,'mono_id':mono['id'],'homophonic_id':homo['id'],'null_id':null['id'],
                      'independent_content_units':1,'same_positive_plaintext':True})
    positive_intervals = [next(t for t in group if t['role']=='monoalphabetic_positive') for group in grouped_truth.values()]
    checks.check('design/one_content_per_pinned_caesar_book', sorted(t['source_path'] for t in positive_intervals), ['caesar/gall1.txt','caesar/gall2.txt','caesar/gall3.txt'])
    checks.check('design/distinct_positive_source_intervals', len({(t['source_path'],t['letter_start'],t['letter_end_exclusive']) for t in positive_intervals}), 3)
    for i,t1 in enumerate(positive_intervals):
        for t2 in positive_intervals[i+1:]:
            overlap = t1['source_path']==t2['source_path'] and max(t1['letter_start'],t2['letter_start'])<min(t1['letter_end_exclusive'],t2['letter_end_exclusive'])
            checks.check('design/new_contents_do_not_overlap/'+t1['pair_id']+'/'+t2['pair_id'], not overlap)
    models = predictions['models']
    checks.check('methods/exactly_two_once', sorted(m['name'] for m in models), sorted(METHODS))
    observations = []
    proposals = polish_checks = 0
    for method in models:
        method_name = method['name']
        predicted_rows = index_rows(method,checks,'predictions/'+method_name)
        checks.check('case_ids/'+method_name, sorted(predicted_rows), sorted(true_rows))
        for name,t in sorted(true_rows.items()):
            p = predicted_rows[name]
            label = method_name+'/'+name+'/'
            key = checked_key(p['key'])
            checks.check(label+'key_length_lowercase', len(key), 26)
            if method_name=='bijective': checks.check(label+'key_is_bijection', ''.join(sorted(key)), ALPHABET)
            expected_candidate = apply_key(t['ciphertext'],key)
            checks.check(label+'candidate_matches_reported_key', expected_candidate, p['plaintext'])
            checks.check(label+'reported_plaintext_stream', p['plaintext'], p['letters_plaintext'])
            checks.check(label+'candidate_2000_no_spaces', len(p['plaintext'])==2000 and letters(p['plaintext'])==p['plaintext'])
            metrics = recovery_metrics(t['ciphertext'],t['plaintext'],t['decryption_key_cipher_to_plain'],key)
            checks.check(label+'exact_plaintext_agrees_with_exact_observed_key', metrics['all_exact'], metrics['observed_symbols_correct']==metrics['observed_symbols_total'])
            score = quantized_score(expected_candidate,model)
            gold_score = quantized_score(t['plaintext'],model)
            checks.check(label+'reported_score_is_integer', type(p['score']) is int)
            checks.check(label+'reported_integer_score', p['score'], score)
            checks.check(label+'eight_restart_scores', len(p['restart_scores']), 8)
            checks.check(label+'restart_scores_are_integer', all(type(n) is int for n in p['restart_scores']))
            checks.check(label+'candidate_best_restart_score', p['score'], max(p['restart_scores']))
            checks.check(label+'expected_proposals', p['annealing_proposals'], 400000)
            checks.check(label+'nonnegative_polish_count', type(p['polish_pair_checks']) is int and p['polish_pair_checks']>=0)
            checks.check(label+'accepted_count_bounds', type(p['accepted']) is int and 0<=p['accepted']<=p['annealing_proposals'])
            checks.check(label+'seed_is_integer', type(p['seed']) is int)
            proposals += p['annealing_proposals']; polish_checks += p['polish_pair_checks']
            ceiling = ceilings[name]
            key_ceiling,key_denominator = observed_key_ceiling(t['ciphertext'],t['plaintext'])
            if method_name=='bijective':
                checks.check(label+'accuracy_within_exact_bijective_ceiling', metrics['characters_correct']<=ceiling)
                checks.check(label+'observed_key_within_ceiling', metrics['observed_symbols_correct']<=key_ceiling)
            representable = method_name=='many_to_one' or ceiling==2000
            observations.append({'method':method_name,'id':name,'role':t['role'],'pair_id':t['pair_id'],**metrics,
                'score':score,'oracle_true_plaintext_score':gold_score,'candidate_minus_true_score':score-gold_score,
                'gold_representable_in_method':representable,
                'objective_diagnostic':objective_diagnostic(metrics['all_exact'],score,gold_score,representable),
                'distinct_decoded_letters':len(set(expected_candidate)),'distinct_gold_letters':len(set(t['plaintext'])),
                'best_bijective_correct_letters':ceiling,'best_bijective_character_accuracy':ceiling/2000,
                'best_bijective_observed_symbols_correct':key_ceiling,'best_bijective_observed_symbol_key_accuracy':key_ceiling/key_denominator,
                'gap_below_bijective_ceiling':(ceiling-metrics['characters_correct'])/2000,
                'annealing_proposals':p['annealing_proposals'],'polish_pair_checks':p['polish_pair_checks']})
    checks.check('budget/eighteen_searches', len(observations), 18)
    checks.check('budget/total_annealing_proposals', proposals, 7200000)
    summary = []
    for method in METHODS:
        for role in ROLES:
            group = [r for r in observations if r['method']==method and r['role']==role]
            summary.append({'method':method,'role':role,'case_count':len(group),
                'all_exact_count':sum(r['all_exact'] for r in group),
                'mean_character_accuracy':statistics.mean(r['character_accuracy'] for r in group),
                'pooled_character_accuracy':sum(r['characters_correct'] for r in group)/sum(r['characters_total'] for r in group),
                'mean_observed_symbol_key_accuracy':statistics.mean(r['observed_symbol_key_accuracy'] for r in group),
                'mean_score':statistics.mean(r['score'] for r in group),
                'mean_distinct_decoded_letters':statistics.mean(r['distinct_decoded_letters'] for r in group)})
    gates = {}
    for method in METHODS:
        gates[method] = {}
        for role in ROLES[:2]:
            group = [r for r in observations if r['method']==method and r['role']==role]
            gates[method][role] = len(group)==3 and all(r['all_exact'] and r['observed_symbols_correct']==r['observed_symbols_total'] for r in group)
    row_index = {(r['method'],r['id']):r for r in observations}
    paired_comparisons = []
    for pair in pairs:
        for name in [pair['mono_id'],pair['homophonic_id'],pair['null_id']]:
            b,m = row_index[('bijective',name)],row_index[('many_to_one',name)]
            paired_comparisons.append({'pair_id':pair['pair_id'],'id':name,'role':b['role'],
                'many_to_one_minus_bijective_accuracy':m['character_accuracy']-b['character_accuracy'],
                'many_to_one_minus_bijective_score':m['score']-b['score']})
    return {'schema':'independent-homophonic-audit-v1',
        'status':'PASS' if not checks.mismatches else 'FAIL','checks':checks.count,'mismatches':checks.mismatches,
        'control_summary':control_summary,'cases':observations,'summary':summary,'strict_gates_recomputed':gates,
        'primary_many_to_one_homophonic_gate':gates['many_to_one']['homophonic_positive'],
        'independent_positive_content_units':3,'positive_presentations':6,'null_controls':3,
        'content_pairs':pairs,'paired_method_comparisons':paired_comparisons,
        'total_annealing_proposals':proposals,'total_polish_neighbor_checks':polish_checks,
        'unobserved_key_mapping_evaluated':False,'null_detection_or_abstention_demonstrated':False,
        'input_hashes':{str(p):sha(p) for p in [public_path,manifest_path,truth_path,pred_path,freeze_path,lm_path,prior_path,latin_path]},
        'scope':'Independent commitments, source normalization/windows and disjointness, key application, exact Hamming, observed mappings, integer LM and gold scoring, fixed-homophone ceilings, paired and null controls. Does not rerun search, prove global optimality, independently certify publication chronology/human isolation, identify a historical language, or translate Voynich. Equal proposal counts are not equal compute.',
        'voynich_translation':'NOT_RUN'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo',type=Path); p.add_argument('--bundle',type=Path); p.add_argument('--out',type=Path)
    p.add_argument('--lm',type=Path); p.add_argument('--prior-truth',type=Path); p.add_argument('--latin',type=Path)
    p.add_argument('--controls-only',action='store_true'); a = p.parse_args()
    if a.controls_only:
        checks=Checks(); summary=controls(checks)
        result={'status':'PASS' if not checks.mismatches else 'FAIL','checks':checks.count,'mismatches':checks.mismatches,'control_summary':summary}
    else:
        if a.repo is None or a.bundle is None or a.out is None: p.error('--repo --bundle --out required after reveal')
        result=audit(a.repo,a.bundle,a.lm,a.prior_truth,a.latin)
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ['status','checks','mismatches']}))
    raise SystemExit(0 if result['status']=='PASS' else 1)


if __name__=='__main__': main()
