---
title: Routing table: a re-asked role's "Receives" column omits its own prior output
labels: design-doc, routing
---
**Where:** design doc §Routing table, resolution rule *"A question returns to the role that asked, with the answer"*, and the Triage row's Receives column: *"The request, ticket search"*.

**What happened (P0 run, 2026-10-01):** Triage asked a three-option scope question (NEEDS-HUMAN). After the human's `--answer`, the rule returns the ticket to Triage with the answer appended to the request. Per the table as written, the re-run Triage receives only the request + answer: it does not receive the question it asked, so it must re-derive the three options (and the ~3M context tokens of investigation behind them) before it can read the answer as an answer.

**Proposed fix:** in §Routing rules, "A question returns to the role that asked, with the answer **and that role's prior output**" and add the same to the Receives column for Triage and Spec writer NEEDS-HUMAN re-entries (the Spec writer round-2 row already does this for the critic loop; the human-question path should be symmetric).

**Fix as implemented on the Nanobot side:** `factory/compose.py` (triage sources: request + last Triage output) at `0f2e29136`.
