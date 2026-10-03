# Plan: T-0001 (spec v1): trailer read by its labels

## Finding first: this spec is already applied on `main`

I can't plan new work for this spec, because `main` already contains the change. Any PR cut from `main` today would be empty. Even so, criteria 1–9, 11 and 13 would pass on it, as would 10 and 12 once they are scoped to that PR's own diff. So a sub-ticket would pass without a single line being written. This is exactly the check-without-goal case the rules forbid, so I am escalating instead of issuing a ticket.

Evidence (checkout `~/dev/spec-factory`, `main` at `4cd8d12`, which descends from the spec's base `9458a7b`):
- `fdefa22 Merge apply/T-0001: trailer read by its labels (closes issue draft 01)` merges `79fdb24` (`T-0001: trailer read by its labels; none + prose routes as none, prose kept as escalations_note`). `git diff --name-only 9c0367c fdefa22` → `docs/spec-factory.md`, `specs/build-harness.md` only.
- `3bd8641 fix(T-0001): item 85(b) reads escalations_note from a finished run; every non-note shape writes null` came after the merge and touches only `specs/build-harness.md`.
- `intake/README.md:40` says: "T-0001..T-0007: spec approved at the gate and applied on `main`".
- The store disagrees. `intake/state/tickets/T-0001.yaml:7` still reads `status: ready-for-planner`, with `plan: null`, and this run is listed in `in_flight`.

I ran the spec's Acceptance commands on `4cd8d12`. Base `9458a7b` was used where a command needs one.

| # | Result on `main` today | Expected |
|---|---|---|
| 1 | `0` | `0` |
| 2 | `misclassified: []` | same |
| 3 | `**last** continuation escalations_note parse failure verbatim` | same |
| 4 | `8` | `8` |
| 5 | `0` | `0` |
| 6 | `1` | `1` |
| 7 | `1` | `1` |
| 8 | `2` | `2` |
| 9 | `1` | `1` |
| 10 | with base `9458a7b`: exit 1, because `prompts/02-spec-writer.md` and `03-spec-critic.md` differ (T-0005/T-0007 merges, not T-0001). Scoped to the T-0001 merge, `git diff --exit-code 9c0367c fdefa22 -- prompts/` exits 0. The grep gives `docs/spec-factory.md:1`, `prompts/00-preamble.md:1` | exit 0, `:1` / `:1` |
| 11 | `0` with base `9458a7b`; also `0` on `9c0367c..fdefa22` and on `3bd8641` | `0` |
| 12 | with base `9458a7b`: lists about 120 `intake/**`, `issues/**`, `plans/`, `prompts/` paths from other tickets. Scoped to the T-0001 commits, `9c0367c..fdefa22` touches the two allowed files and `3bd8641` touches `specs/build-harness.md` | no output |
| 13 | exit 0 with base `9458a7b`; `git show --check 3bd8641` also exits 0 | exit 0 |

So every parent criterion is met by the commits already on `main`, as long as 10 and 12 are read against the T-0001 commits rather than the whole `9458a7b...HEAD` range, which now includes other tickets' merges.

One difference from the approved text. `3bd8641` reworded item 85 after the merge, beyond spec v1 part C. Word diff: `{+the list is empty and+}`, `{+every other shape, including+}`, `[-`none`, or an empty head,-]` → `{+`none` and a `none` head with lines below it,+}`, `[-that run's-]` → `{+`factory run finish <run_id> --output-file t.md` on a run started as in item 9 → its+}`. The commit message credits validator notes. Criterion 4 still returns `8`. I can't tell whether the gate approved this change. It is the operator's call, not the planner's.

## The plan this spec would get (for the record; do not dispatch)

If `main` did not already contain the change, the spec would fit in one PR. It is about 16 lines in two documents, the parts are tightly linked (A's paragraph, B's cross-references, C's item 85, and D/E's doc text all describe one rule), and splitting it would only force re-verification between siblings. So the plan is one sub-ticket.

**T-0001.1 / Trailer read by its labels; `none` + prose routes as none and is kept as `escalations_note`**
Parent: `intake/state/specs/T-0001/v1.md`. Read it for context. Do NOT implement parts outside this sub-ticket.
Depends on: none
Parallel-safe: yes. It is the only sub-ticket, so it has no siblings to conflict with.
Scope: parent parts A, B, C, D, E
Acceptance: parent criteria 1–13 as written, run from `~/dev/spec-factory` with the PR branch checked out and `main` as base. Each must give the result the parent states.
Tests to change: none
Protected paths: none. `prompts/**` must stay unchanged (criterion 10). `intake/**`, `~/dev/nanobot-upstream/**` and `~/.nanobot/**` are not touched.
Out of scope: the preamble OUTPUT block and `prompts/`; item 8; last-STATUS-wins and the missing-label parse failure; the harness-bug routing row; both `status.py` copies (green follow-up); `plans/`; the `run.finished` payload.

Coverage map:
- Criteria 1, 2, 3 (part A) → T-0001.1
- 4, 7 (part C) → T-0001.1
- 5, 6 (part B) → T-0001.1
- 8 (part D) → T-0001.1
- 9 (part E) → T-0001.1
- 10, 11, 12, 13 (regressions) → T-0001.1

Each of these is already satisfied on `main` by `fdefa22` and `3bd8641` (see the table above).

## Out-of-scope observations
- Criteria 10 and 12 use `main...HEAD`. Once `main` has moved on, that range no longer isolates one ticket, so any after-the-fact check should name the ticket's own commits. This affects how applied tickets are verified in general, not only T-0001.
- The README says T-0002..T-0007 are also applied. Planner runs `run-0030` (T-0002) and `run-0031` (T-0003) were dispatched today and may have the same mismatch. I did not read their outputs.

STATUS: ESCALATE
CONFIDENCE: high. Every claim comes from `git log`, `git diff`, or the spec's own Acceptance commands run on this checkout. The outputs are quoted above.
ESCALATIONS:
1. The input contradicts the codebase. Spec v1 for T-0001 is already applied on `main` (`fdefa22` and the follow-up `3bd8641`), but the ticket is `ready-for-planner` with `plan: null`. A dispatched sub-ticket would be an empty PR that passes its checks. The operator decides how to close the ticket without a new PR: record the existing merge as its plan/merge, or close it as applied out-of-band.
2. `3bd8641` changed item 85 after the merge, beyond the approved spec v1 part C text. The operator should confirm whether that wording is accepted. The other options are a spec v2, or reverting to the approved text.
3. Criteria 10 and 12 fail with base `9458a7b` only because of other tickets' merges. If the ticket's verification is recorded, it should cite the T-0001 commit ranges used above.
