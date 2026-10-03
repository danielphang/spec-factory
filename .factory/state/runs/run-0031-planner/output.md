# Plan: T-0003 (spec v1): no sub-tickets, escalated

## Summary

There is nothing left to build, so I wrote no plan. The approved spec v1 has already been applied to `main` outside the planner and implementer flow. Commit `eed7751` ("T-0003: an answered question returns to the asker with its own previous output") was merged as `32cf6f6` ("Merge apply/T-0003 … (closes issue draft 03)"). Today `main` is at `4cd8d12`. The spec's evidence was taken at `1384157`.

When that commit applied the spec, it renumbered two of its items, and its message says so: "Changelog entry 36 (spec: 34), acceptance item 86 (spec: 85; T-0001's trailer parser took 85)". So acceptance criteria 4 and 7, as written, fail on `main` today.

Any sub-ticket I write now would be one of two things:
- **A no-op.** Parts A to D are already on `main`.
- **A change to what the spec asks for.** It would either rewrite criteria 4 and 7 to say 36 and 86, or add a duplicate entry 34 / item 85 so that the old numbers pass.

My role rules say to escalate in both cases rather than quietly change the spec, so I am escalating.

## Evidence

I ran every command from `~/dev/spec-factory` on `main` at `4cd8d12`.

- `git log --oneline 1384157..HEAD` includes `32cf6f6 Merge apply/T-0003 …` and `eed7751 T-0003: …`.
- `git show --stat eed7751` shows `docs/spec-factory.md | 5 ++++-` and `specs/build-harness.md | 12 ++++++++----`. These are the only two files the spec allows.
- `meta.yaml` for this run shows `ticket: T-0003`, `spec_version: 1`, `input_sources: [specs/T-0003/v1.md]`. The ticket yaml shows `status: ready-for-planner`, `plan: null`. The ticket state was never advanced past planning, even though the change has merged.

Each spec acceptance criterion against current `main`:

| # | Kind | Output on `main` | Result |
|---|------|------------------|--------|
| 1 | NEW | `1` (rule now at `docs/spec-factory.md:79`) | pass |
| 2 | NEW | `1` (row at `:97`) | pass |
| 3 | NEW | `1` (row at `:98`) | pass |
| 4 | NEW | `0`. Entry `^34\.` is T-0001's trailer entry (`:652`). The T-0003 text is entry `36.` (`:654`). Grepping `^36\.` gives `1`. | **fails as written** |
| 5 | NEW | `1` (`specs/build-harness.md:312`) | pass |
| 6 | NEW | `1` then `1` (`:276`, `:277`) | pass |
| 7 | NEW | `1` then `0`. Item `^85\.` is T-0001's "Trailer shapes" (`:459`). The T-0003 item is `86.` (`:463`). Grepping `^86\.` gives `1`. | **second half fails as written** |
| 8 | REGRESSION | `1` then `1` | pass |
| 9 | REGRESSION | `main...HEAD` is vacuous after the merge. Rerun against the applying commit, `git diff eed7751^ eed7751 -- docs/spec-factory.md \| grep -E '^-\|'` gives no output, exit 1. | pass (on the applying commit) |
| 10 | REGRESSION | `01-triage same`, `02-spec-writer same`. `git diff --stat eed7751^ eed7751 -- prompts/` is empty. | pass |
| 11 | REGRESSION | `git diff --check eed7751^ eed7751` exits 0 | pass |

The content the spec intends is fully on `main`. Only the item numbers that criteria 4 and 7 pin have drifted.

## Sub-tickets

None.

If T-0003 had not already landed, it would have been a single sub-ticket: about 17 changed lines in two documents, every criterion is a grep, and there is no seam where splitting helps review or rollback. That is not the situation now, so I am not issuing it.

## Coverage map

Not applicable, because no sub-tickets were issued. For the operator, criteria 1–3, 5, 6, 8 and 10 already hold on `main`. Criteria 9 and 11 hold on `eed7751`. Criteria 4 and 7 hold only under the renumbering (36 / 86).

## Out-of-scope observations

- **Ticket state is out of sync.** The ticket yaml still says `ready-for-planner` with `plan: null`, and this run was dispatched on it even though the work merged in `32cf6f6`. The dispatcher has no record that a ticket was applied by hand.
- **Fixed numbers in criteria break when other specs land first.** Criteria 4 and 7 pin Changelog and acceptance-item numbers. Any spec that lands earlier and takes the next number breaks them. T-0001 did exactly that here.
- **The plans file count is now one further off.** The spec's out-of-scope note about `plans/P0-intake-skeleton.md:42` ("the spec's 1–84") still applies. The highest item is now 86, not 85.

STATUS: ESCALATE
CONFIDENCE: high. I ran every acceptance command against `main` at `4cd8d12`. The applying commit and its message saying it renumbered the items were read from `git show eed7751`.
ESCALATIONS:
- **T-0003's approved spec v1 is already applied on `main`** (`eed7751`, merged as `32cf6f6`), but the ticket is still `ready-for-planner`. Planning it again would produce no-op work. An operator decision is needed: close T-0003 as applied by hand and move it from `ready-for-planner` to closed, or re-route it some other way.
- **Acceptance criteria 4 and 7 contradict `main`.** Entry 34 and item 85 belong to T-0001. T-0003's text is at entry 36 and item 86. Meeting the criteria as written would mean either changing the approved criteria, which is a spec revision for a human, or adding duplicate numbered entries, which would game the check. I did neither. If verification against the spec is still wanted, a human has to amend criteria 4 and 7 to `^36\.` and `^86\.`. Those versions pass today.
