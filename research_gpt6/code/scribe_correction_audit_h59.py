#!/usr/bin/env python3
import argparse, json
from pathlib import Path

EXPECTED = [
    'H59-f16r-01','H59-f20v-01','H59-f24v-01','H59-f39r-01','H59-f39r-02',
    'H59-f42r-01','H59-f50v-01','H59-f79r-01','H59-f80r-01','H59-f83r-01',
    'H59-f102v2-01','H59-f112r-01'
]
ALLOWED_CONF = {'UNVERIFIED','HIGH','MEDIUM','AMBIGUOUS'}
ALLOWED_MECH = {None,'stroke-addition','overwrite','erasure/scrape','insertion','deletion','other'}
MIN_PRIMARY = 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()

    doc = json.loads(a.audit.read_text())
    rows = doc.get('candidates', [])
    ids = [r.get('candidate_id') for r in rows]
    problems = []
    if ids != EXPECTED:
        problems.append('candidate inventory/order differs from preregistered frozen list')
    if len(set(ids)) != len(ids):
        problems.append('duplicate candidate IDs')
    if doc.get('minimum_primary_events', MIN_PRIMARY) != MIN_PRIMARY:
        problems.append('minimum primary-event threshold differs from preregistration')
    if doc.get('threshold_lowered') is True:
        problems.append('preregistered threshold may not be lowered')

    high = []
    included = []
    for r in rows:
        cid = r.get('candidate_id','?')
        conf = r.get('confidence')
        if conf not in ALLOWED_CONF:
            problems.append(f'{cid}: invalid confidence {conf!r}')
        if r.get('correction_mechanism') not in ALLOWED_MECH:
            problems.append(f'{cid}: invalid correction mechanism')
        if conf == 'HIGH':
            if not r.get('primary_image_verified'):
                problems.append(f'{cid}: HIGH forbidden without primary-image verification')
            required = ['correction_mechanism','visible_final_form','pre_correction_form','reason']
            for k in required:
                if not r.get(k):
                    problems.append(f'{cid}: HIGH missing {k}')
            high.append(cid)
        if r.get('include_primary_test'):
            included.append(cid)
            if conf != 'HIGH':
                problems.append(f'{cid}: primary inclusion requires HIGH confidence')
            if not r.get('primary_image_verified'):
                problems.append(f'{cid}: primary inclusion requires primary-image verification')

    complete_recoverability_audit = (
        doc.get('stage') == 'PRIMARY_RECOVERABILITY_AUDIT'
        and doc.get('status') == 'COMPLETE'
        and len(rows) == len(EXPECTED)
    )

    if problems:
        audit_status = 'INVALID_AUDIT'
        scientific_status = 'BLOCKED'
    elif len(included) >= MIN_PRIMARY:
        audit_status = 'AUDIT_READY_FOR_SCORING'
        scientific_status = 'NOT_RUN'
    elif complete_recoverability_audit:
        audit_status = 'AUDIT_BLOCKED_INSUFFICIENT_RECOVERABLE_EVENTS'
        scientific_status = 'BLOCKED'
    else:
        audit_status = 'DATA_AUDIT_REQUIRED'
        scientific_status = 'NOT_RUN'

    out = {
        'experiment':'H59_BLIND_SCRIBE_CORRECTION_PREDICTION',
        'audit_status':audit_status,
        'scientific_status':scientific_status,
        'candidate_count':len(rows),
        'high_confidence_count':len(high),
        'primary_test_count':len(included),
        'minimum_primary_events':MIN_PRIMARY,
        'complete_recoverability_audit':complete_recoverability_audit,
        'threshold_lowered':False,
        'confirmatory_model_fitting':'NOT_RUN',
        'null_randomizations':'NOT_RUN',
        'problems':problems,
        'language_identification':'NOT_RUN',
        'semantic_identification':'NOT_RUN',
        'translation':'NOT_RUN',
        'decipherment':'NOT_RUN'
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))
    if problems:
        raise SystemExit(2)

if __name__ == '__main__':
    main()
