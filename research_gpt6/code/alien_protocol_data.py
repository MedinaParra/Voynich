"""Input and synthetic-data construction for a structural protocol diagnostic.

This module does not fit models or calculate experimental scores.  IVTFF
selection is deliberately conservative: one unsupported token excludes its
entire logical line, so removal cannot manufacture a new adjacent word pair.
Synthetic meanings belong only to the explicit demonstration codebooks; they
are not labels inferred for Voynich.
"""

from collections import Counter
import hashlib
from pathlib import Path
import random
import re


GROUPS = ("cfh", "ckh", "cph", "cth", "ch", "sh")
WORDS = ("abcd", "efgh", "ijkl", "mnop", "qrst", "uvwx", "yzAB", "CDEF")
ACTIONS = ("HEAT", "COOL", "MIX", "WAIT", "FILTER", "GRIND", "ADD", "DRAIN")

_LOCUS = re.compile(
    r"^<(?P<id>(?P<folio>f[^.,>\s]+)\.[^,>\s]+),"
    r"(?P<kind>[^>\s]+)>\s*(?P<payload>.*)$"
)
_PARAGRAPH = re.compile(r"(?:[^,\s])?P[0-9a-z]")
_TOKEN = re.compile(r"[a-z]+")
_ANGLE = re.compile(r"<[^>]*>")


def _logical_records(text):
    """Yield (first physical line number, logical record), resolving / wraps.

    A trailing slash opens a continuation and the next physical line must start
    with a slash.  Only the two framing slashes are removed; payload whitespace
    is not repaired.  Comment records are never opened as continuations merely
    because a comment happens to end with a URL slash.
    """
    pending = None
    first = None
    for number, physical in enumerate(text.splitlines(), 1):
        if pending is not None:
            if not physical.startswith("/"):
                raise ValueError(
                    f"Missing IVTFF continuation after physical line {first}; "
                    f"encountered physical line {number}"
                )
            record = pending + physical[1:]
        else:
            if physical.startswith("/"):
                raise ValueError(f"Orphan IVTFF continuation at physical line {number}")
            first = number
            record = physical
        if record.endswith("/") and not record.lstrip().startswith("#"):
            pending = record[:-1]
            continue
        pending = None
        yield first, record
    if pending is not None:
        raise ValueError(f"Incomplete IVTFF continuation beginning at physical line {first}")


def parse_ivtff(path, commas):
    """Return (rows, inventory) without salvaging tokens from rejected lines.

    ``commas`` is ``split`` (comma becomes a word separator) or ``join`` (comma
    is removed).  Accepted rows have exactly ``id``, ``folio``, ``leaf`` and
    ``words``.  The id before the locus-type comma is preserved verbatim; it is
    never renumbered.  Physical leaves use the leading ``f`` plus digits, so
    recto/verso and foldout subdivisions remain together.

    The inventory records every nonaccepted logical record, including comments,
    page metadata and blanks.  Rejection reasons are exclusive and prioritized
    as listed in the implementation.  Malformed wrapping raises ValueError
    instead of creating an invented logical record.
    """
    if commas not in ("split", "join"):
        raise ValueError("commas must be 'split' or 'join'")
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8-sig")
    rows = []
    reasons = Counter()
    rejected = []
    matched = 0
    logical = 0

    def reject(number, record, reason, locator=None):
        reasons[reason] += 1
        rejected.append({
            "id": locator,
            "start_physical_line": number,
            "reason": reason,
            "record": record,
        })

    for number, record in _logical_records(text):
        logical += 1
        if not record.strip():
            reject(number, record, "blank")
            continue
        if record.lstrip().startswith("#"):
            reject(number, record, "comment")
            continue
        match = _LOCUS.fullmatch(record)
        if match is None:
            reason = "page_metadata" if re.match(r"^<f[^.,>\s]+>", record) else "unrecognized_record"
            reject(number, record, reason)
            continue
        matched += 1
        locator, folio, kind, payload = (
            match.group("id"), match.group("folio"),
            match.group("kind"), match.group("payload"),
        )
        if _PARAGRAPH.fullmatch(kind) is None:
            reject(number, record, "non_paragraph_locus", locator)
            continue
        leaf_match = re.match(r"^f\d+", folio)
        if leaf_match is None:
            reject(number, record, "unsupported_folio", locator)
            continue
        if "<->" in payload or "<~>" in payload:
            reject(number, record, "drawing_gap", locator)
            continue
        payload = _ANGLE.sub("", payload).strip()
        payload = payload.replace(",", "." if commas == "split" else "")
        words = payload.split(".")
        if any(word == "" for word in words):
            reject(number, record, "empty_separator", locator)
            continue
        if any(_TOKEN.fullmatch(word) is None for word in words):
            reject(number, record, "unsupported_payload", locator)
            continue
        if len(words) < 2:
            reject(number, record, "too_few_words", locator)
            continue
        rows.append({
            "id": locator,
            "folio": folio,
            "leaf": leaf_match.group(),
            "words": words,
        })

    inventory = {
        "schema": "alien-protocol-ivtff-inventory-v1",
        "source_name": Path(path).name,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "commas": commas,
        "physical_lines": len(text.splitlines()),
        "logical_records": logical,
        "matched_loci": matched,
        "accepted_lines": len(rows),
        "accepted_words": sum(len(row["words"]) for row in rows),
        "rejected_by_reason": dict(sorted(reasons.items())),
        "rejected_rows": rejected,
        "selection_scope": "Strict complete logical lines; no token salvage or locus reindexing",
    }
    return rows, inventory


def units(raw, mode):
    """Return atomic character units or a greedy, fixed EVA grouping.

    Grouped units are single private-use symbols E100..E105.  They are analysis
    conventions, not authenticated historical glyph segmentation.  Other
    characters, including synthetic uppercase/Greek symbols, remain atomic.
    """
    if mode == "letters":
        return tuple(raw)
    if mode != "groups":
        raise ValueError("mode must be 'letters' or 'groups'")
    out = []
    i = 0
    while i < len(raw):
        for index, group in enumerate(GROUPS):
            if raw.startswith(group, i):
                out.append(chr(0xE100 + index))
                i += len(group)
                break
        else:
            out.append(raw[i])
            i += 1
    return tuple(out)


def split_leaf(leaf, seed):
    """Assign a whole physical leaf, or explicit synthetic leaf, deterministically."""
    value = hashlib.sha256((str(seed) + ":" + leaf).encode("utf-8")).digest()[0]
    return "test" if value % 5 == 0 else "train"


def _rng(seed, label):
    digest = hashlib.sha256((str(seed) + ":alien-protocol-control:" + label).encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest, "big"))


def controls(seed):
    """Return four synthetic row lists; no fitting or metric calculation.

    Each dataset has 60 leaves x 20 lines x 8 words.  iid_layout copies the
    *same* iid concepts, adding a deterministic positional prefix.  echo and
    morphology have independently SHA-derived random streams.  Echo chooses
    the previous concept with probability .85; the otherwise-uniform draw can
    coincidentally choose it too.  The binary morphology state stays with
    probability .9 and flips otherwise; it resets uniformly each line.

    The two synthetic controls involving persistent state do not establish a
    semantic or historical interpretation of any comparable real-text effect.
    """
    iid_rng = _rng(seed, "iid-concepts")
    echo_rng = _rng(seed, "echo-concepts")
    morphology_rng = _rng(seed, "morphology-concepts")
    state_rng = _rng(seed, "morphology-states")
    result = {name: [] for name in ("iid", "iid_layout", "echo", "morphology")}
    for leaf_number in range(60):
        leaf = f"syn{leaf_number:03d}"
        folio = leaf + "r"
        for line_number in range(1, 21):
            iid = [WORDS[iid_rng.randrange(len(WORDS))] for _ in range(8)]
            echo = [WORDS[echo_rng.randrange(len(WORDS))]]
            for _ in range(7):
                echo.append(echo[-1] if echo_rng.random() < .85 else WORDS[echo_rng.randrange(len(WORDS))])
            morphology = []
            state = state_rng.randrange(2)
            for position in range(8):
                if position and state_rng.random() >= .9:
                    state = 1 - state
                morphology.append(WORDS[morphology_rng.randrange(len(WORDS))] + ("Ω", "Ψ")[state])
            dataset_words = {
                "iid": iid,
                "iid_layout": [("Γ" if position == 0 else "Θ" if position == 7 else "Δ") + word
                               for position, word in enumerate(iid)],
                "echo": echo,
                "morphology": morphology,
            }
            for name, words in dataset_words.items():
                result[name].append({
                    "id": f"{folio}.{line_number}",
                    "folio": folio,
                    "leaf": leaf,
                    "words": list(words),
                })
    return result


def semantic_certificate():
    """Return an explicit witness of semantic nonidentifiability, not a decoder.

    Both codebooks are bijections onto the identical eight observed words.
    Their action labels are cyclically rotated.  Decoding the fixed observed
    message therefore gives incompatible action sequences, while each sequence
    encodes back to exactly the same text.  Any diagnostic depending only on
    that text and its layout receives identical input in the two worlds.
    """
    codebook_a = dict(zip(WORDS, ACTIONS))
    rotated = ACTIONS[1:] + ACTIONS[:1]
    codebook_b = dict(zip(WORDS, rotated))
    observed_words = list(WORDS)
    translation_a = [codebook_a[word] for word in observed_words]
    translation_b = [codebook_b[word] for word in observed_words]
    inverse_a = {meaning: word for word, meaning in codebook_a.items()}
    inverse_b = {meaning: word for word, meaning in codebook_b.items()}
    roundtrip_a = [inverse_a[meaning] for meaning in translation_a]
    roundtrip_b = [inverse_b[meaning] for meaning in translation_b]
    observed_text = ".".join(observed_words)
    return {
        "schema": "alien-protocol-semantic-certificate-v1",
        "observed_words": observed_words,
        "observed_text": observed_text,
        "codebook_a": codebook_a,
        "codebook_b": codebook_b,
        "translation_a": translation_a,
        "translation_b": translation_b,
        "roundtrip_a_words": roundtrip_a,
        "roundtrip_b_words": roundtrip_b,
        "roundtrip_a_text": ".".join(roundtrip_a),
        "roundtrip_b_text": ".".join(roundtrip_b),
        "same_observed_text": ".".join(roundtrip_a) == observed_text == ".".join(roundtrip_b),
        "different_translations": translation_a != translation_b,
        "scope": "Explicit synthetic observational equivalence; not candidate Voynich meanings or evidence that a particular historical mechanism was used",
    }
