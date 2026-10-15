# H91 — Independent label↔object replication gate result

Status: **BLOCKED**

## Evidence
The preregistration at `research_gpt6/123_h91_independent_label_object_replication_gate_preregistration.md` requires evaluating the **complete prespecified candidate inventory**, but it does not freeze any candidate-folio inventory, candidate-family rule, or source manifest from which that inventory can be derived without inspecting new material.

The current repository contains workflows through H90, but no H91 runner/workflow or frozen H91 candidate manifest. Existing H79 infrastructure is specific to f68r1 and fetches an independent f68r star-centre CSV plus Yale f68r1 coordinates; f68r1 and f68r2 are explicitly excluded by H91.

## Classification rationale
Under the preregistered H91 definitions, this is **BLOCKED**, not FAIL: the required complete candidate inventory cannot be evaluated reproducibly from the frozen H91 specification. Creating a candidate list now and then treating it as if it had been prespecified would introduce researcher degrees of freedom after H90 was observed.

No lexical strings, semantic glosses, language hypotheses, translations, or candidate labels were inspected for this determination.

## Required repair before a new confirmatory gate
A successor preregistration (H91b or H93; new hypothesis identifier, not a rewrite of H91) must freeze *before execution*:
1. a source repository/dataset and immutable revision/hash;
2. a deterministic candidate-folio enumeration rule independent of lexical token strings;
3. explicit exclusions fixed before Stage A;
4. the geometry/object extraction rule and its parameters;
5. the Stage-A output schema that contains no lexical strings;
6. only after Stage A is committed, a Stage-B lexical exposure procedure.

H91 itself remains BLOCKED permanently; its thresholds must not be edited post hoc.

## Status ledger
- H91: **BLOCKED**
- H91 infrastructure execution: **BLOCKED** (no valid frozen candidate inventory to execute)
- H92: **NOT_RUN** (H91 did not PASS)
- semantic claim: **NOT_RUN**
- language identification: **NOT_RUN**
- translation: **NOT_RUN**
- decipherment: **NOT_RUN**
