# Plan for T-0002 (approved spec v1): ESCALATE, because the spec is already applied on main

## Why this escalates instead of planning

The input contradicts the codebase. Parts A–G of the pinned spec are already on `main`. They landed as commit `d2866d2` ("T-0002: the clerk relays stdout, exit and stderr verbatim; the script parses the JSON"; `git merge-base --is-ancestor d2866d2 main` → on-main). Current HEAD is `4cd8d12` on branch `main`. The ticket store still shows T-0002 as `ready-for-planner` with `plan: null` (`intake/state/tickets/T-0002.yaml`). So the store and the repo disagree.

The landed text also differs from the pinned spec in three places. The Planner cannot fix these without changing what the spec asks for:

1. **Changelog number (part B).** The spec says to append item `34.`, but commit `d2866d2` added it as `35.`. Item 34 already existed before that commit (`git show d2866d2^:docs/spec-factory.md` has `34. After two real runs parked valid verdicts as harness bugs…`, from T-0001). Main now has 38 Changelog items.
2. **Part D wording.** The spec says "`factory merge`'s `head does not contain main`, matched in the relayed text". `specs/build-harness.md:269` says "matched in the relayed `stdout` or `stderr`". It means the same thing, but the text is not the verbatim NEW block.
3. **Part F addition.** `specs/build-harness.md:277` adds "(that first call runs on the doc's clerk default, Haiku; later calls on `MODELS.clerk`)". The spec has no such text; this is the spec's own Out-of-scope observation 3, resolved without approval.

## What I ran and saw

I ran the parent's Acceptance commands from `~/dev/spec-factory` on `main` HEAD `4cd8d12`:

| Item | Expected | Actual |
|---|---|---|
| 1 limit (1) phrases | 7 `ok:` | 7 `ok:` |
| 2 old clerk wording | `0`,`0`,`0` | `0`,`0`,`0` |
| 3 H paragraph phrases | 6 `ok:` | 6 `ok:` |
| 4 runRole parses `run_id` | `1` | `1` |
| 5 `factory config` | `1`,`0` | `1`,`0` |
| 6 Output contract | 3 lines | `last line of stdout`, `ticket show ID [--json]`, `factory config` |
| 7 Risk bullet | 3 lines | `relays`, `parses the JSON itself`, `Residual` |
| **8 Changelog** | **`34`, `1`** | **`38`, `0`** (fails; T-0002's entry is item 35, and that one greps `1` for `clerk`) |
| 9 guards stay in CLI | `1` | `1` |
| 10 row cells | `7` | `7` |
| 11–13 `main HEAD` diffs | unchanged / empty / exit 0 | pass, but trivially: `HEAD` is `main`, so the diff is empty |

What this means:
- Items 1–7 and 9–10 already pass on main, so a sub-ticket held to them proves nothing. The input says the same thing: "a NEW criterion that already passes on this checkout proves nothing".
- Item 8 cannot pass on main as written. Making it pass would mean renumbering T-0001's Changelog entries or rewriting history. Both are outside this spec and would break other entries.
- If a sub-ticket re-applied A–G, every OLD string would fail to match, because the OLD text is gone.

## Decision needed (human)

Pick one:
- **(a) Close T-0002 as already applied.** Record `d2866d2` as its landing commit and accept the three differences above. Item 8 is then read as "item 35 mentions clerk", which passes today (`grep -E '^35\. ' | grep -cF clerk` → `1`). Recommended: the substance of every part is on main, and the reference harness already behaves this way.
- **(b) Spec v2.** Re-pin the spec to match main: item 8 → `^35\. ` with a count of 38 or a count-free check, plus the D wording and the F parenthetical. Then plan it as a verify-only ticket. This adds process but no change to what ships.
- **(c) Revert `d2866d2` and re-apply exactly v1 through the pipeline.** Not recommended, because item 8 would still fail at item 34.

## If the decision is to plan anyway (conditional, not dispatched)

The spec fits one PR (two documents, about 10 lines), so the plan would be one sub-ticket. Splitting it would only add re-verification.

**T-0002-1 / Docs: clerk relays stdout, exit and stderr; script parses the JSON; output contract in spec B**
- Parent: `intake/state/specs/T-0002/v1.md`. Read it for context. Do NOT implement parts outside this sub-ticket.
- Depends on: none
- Parallel-safe: yes (it is the only sub-ticket)
- Scope: A, B, C, D, E, F, G
- Acceptance: parent Acceptance items 1–13 exactly as written, run from `~/dev/spec-factory` on the PR head with `main` as the base. Item 8 cannot pass against current main (see above).
- Tests to change: none
- Protected paths: none
- Out of scope: everything in the parent's Out of scope and Out-of-scope observations 1–4 (`run finish --output-file -`, plans/ amendments, the first config call's model, the merge refusal on stdout vs stderr)

Coverage map (conditional plan): items 1–13 → T-0002-1.

## Out-of-scope observations

- `d2866d2` reached main without the T-0002 ticket passing the planner, implementer or checkers. The store (`plan: null`, `in_flight: [run-0030-planner]`) does not reflect that. Someone should find out how a pinned spec got applied outside the pipeline before T-0003 and later tickets hit the same thing.
- Some parent Acceptance items compare `main HEAD` and are only meaningful from a branch whose HEAD is not `main`. On `main` itself they pass trivially.

STATUS: ESCALATE
CONFIDENCE: high, because I ran every parent Acceptance command on main and read the `d2866d2` diff and its parent's Changelog.
ESCALATIONS: (1) The input contradicts the codebase: approved spec T-0002 v1 is already applied on main as `d2866d2`, while the store still has the ticket at `ready-for-planner`. (2) Parent Acceptance item 8 (Changelog `34`, `1`) cannot pass on main (actual `38`, `0`; the entry is item 35). (3) The landed text differs from the pinned spec in part D (wording) and part F (an extra parenthetical). A human must choose (a) close as applied, (b) spec v2, or (c) revert and re-apply.
