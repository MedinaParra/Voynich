#!/usr/bin/env python3
"""Exact Q20 binding-state constraint audit.

Enumerates all 6! = 720 outer-to-inner nestings of the six surviving Q20
bifolia, keeping each bifolium's internal folio orientation fixed.  It tests
three direct paint-transfer facing constraints against two published wormhole
state interpretations.  This is a codicological state audit, not a decipherment
and not a proof of original production order.
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

BIFS = {
    "B103_103|116": (103, 116),
    "B104_104|115": (104, 115),
    "B105_105|114": (105, 114),
    "B106_106|113": (106, 113),
    "B107_107|112": (107, 112),
    "B108_108|111": (108, 111),
}
PAINT = {(104, 105), (114, 115), (115, 116)}
CURRENT = tuple(BIFS)
B103, B104, B105, B106, B107, B108 = tuple(BIFS)
TEXTUAL_PRODUCTION = (B105, B106, B107, B104, B108, B103)


def leaf_order(nesting):
    pairs = [BIFS[x] for x in nesting]
    return [a for a, _ in pairs] + [b for _, b in reversed(pairs)]


def facing_pairs(nesting):
    leaves = leaf_order(nesting)
    return set(zip(leaves, leaves[1:]))


def kendall(a, b):
    pos = {x: i for i, x in enumerate(b)}
    arr = [pos[x] for x in a]
    return sum(arr[i] > arr[j] for i in range(len(arr)) for j in range(i + 1, len(arr)))


def main():
    states = list(itertools.permutations(BIFS))
    paint_states = [p for p in states if PAINT <= facing_pairs(p)]
    old_worm_states = [p for p in states if p[:2] == (B104, B105)]
    final_worm_states = [p for p in states if p[:3] == (B103, B104, B105)]

    best_d = min(kendall(a, b) for a in old_worm_states for b in paint_states)
    pair = next((a, b) for a in old_worm_states for b in paint_states if kendall(a, b) == best_d)

    result = {
        "status": "Q20_BINDING_STATE_CONSTRAINT_AUDIT",
        "model": "six surviving bifolia, fixed internal orientation; enumerate all 6! outer-to-inner nestings",
        "bifolia": {k: list(v) for k, v in BIFS.items()},
        "n_states": len(states),
        "direct_paint_transfers_as_facing_constraints": [["f104v", "f105r"], ["f114v", "f115r"], ["f115v", "f116r"]],
        "paint_compatible_states": len(paint_states),
        "old_wormhole_constraint": {
            "interpretation": "f104|115 outermost, f105|114 immediately inside",
            "compatible_states": len(old_worm_states),
        },
        "final_wormhole_constraint": {
            "interpretation": "f103|116, f104|115, f105|114 are outermost three in that order",
            "compatible_states": len(final_worm_states),
        },
        "intersections": {
            "paint_and_old_wormholes": len(set(paint_states) & set(old_worm_states)),
            "paint_and_final_wormholes": len(set(paint_states) & set(final_worm_states)),
        },
        "minimum_kendall_distance_old_worm_to_paint_state": best_d,
        "minimum_transition_example": {"old_worm_state": list(pair[0]), "paint_state": list(pair[1])},
        "current_nesting": list(CURRENT),
        "current_satisfies_direct_paint_transfers": len(PAINT & facing_pairs(CURRENT)),
        "working_textual_production_candidate_missing_omitted": list(TEXTUAL_PRODUCTION),
        "if_misinterpreted_as_bound_nesting_paint_constraints_satisfied": len(PAINT & facing_pairs(TEXTUAL_PRODUCTION)),
        "guardrails": [
            "The wormhole constraints follow Nick Pelling's interpretation of Wladimir Dulov's observations; they are not direct measurements made in this audit.",
            "Paint transfer constraints only date a contact state if the paint-transfer chronology is independently established.",
            "The textual Q20 candidate is a production/reading-order hypothesis, not automatically an outer-to-inner physical nesting.",
            "The missing 109|110 bifolium is omitted from this six-bifolium bound-state enumeration.",
        ],
        "conclusion": "No single six-bifolium nesting satisfies both the old-wormhole outer-pair interpretation and all three direct paint transfers. At least two physical states are required under these assumptions.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
