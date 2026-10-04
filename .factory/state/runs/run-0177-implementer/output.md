Sub-ticket: T-0019.2 (T-0019-S2, plan field lines), part of T-0019 (issue #36), approved spec v2. Branch `factory/T-0019.2`, head `9300012`, on base `9853737`, which already holds the merged S1 (T-0019.1). Round 2: one fix commit, `9300012`, on top of `381f4c6`.

## What changed

Before this change, the harness silently dropped a planner's `Depends on:` line if it was written as a `- ` list item. The planner is the role that splits an approved spec into sub-tickets, units of work that each become one branch and one merge. The `Depends on:` line names the sub-tickets that must merge first. When the line was dropped, the sub-ticket was recorded with no dependencies and built out of order. A sub-ticket with no `Depends on:` line at all got the same silent default. The harness now reads bulleted field lines. It refuses a plan in which a sub-ticket lacks a `Depends on:` line, and the refusal names that sub-ticket. The planner prompt now shows the lines the harness reads, in the form it reads them.

The code, prompt and changelog changes are the round-1 commit `381f4c6`, unchanged:
- **C1** (`factory/subtickets.py` line 21). `FIELD_RE` now accepts an optional `- ` or `* ` bullet before any bold marks: `^\s*(?:[-*]\s+)?\**\s*([A-Z][A-Za-z -]+?)\s*:\s*\**\s*(.*)$`. This also fixes `* **Depends on:**`, which the old pattern could not read either. Its `\**` took the bullet's `*`, and then the space stopped the match. `HEAD_RE` is unchanged, so a bullet still never starts a sub-ticket.
- **C2** (`parse`, lines 67, 74 and 95-96). Each block records whether it had a `depends on` field line. A block without one raises `ValueError("<label>: no \"Depends on:\" line; write \"Depends on: none\" when it depends on nothing")`. `subticket_add` (`factory/cli.py` lines 394-397) already turns that error into exit 2 before anything is written.
- **C3**. The module docstring now says that field lines may carry a list bullet and that every sub-ticket needs a `Depends on:` line.
- **D**. In the design doc's `## 4. Planner / decomposer` block, the four lines from `For each sub-ticket:` through `  Parallel-safe: yes | no (reason)` are replaced by the spec's eight lines. The block is re-copied into `docs/prompts/04-planner.md` and `factory/prompts/planner.md`.
- **E1, the S2 clause**. S1 had already merged changelog entry 48. As the plan says, I added the S2 clause to that entry as a second sentence, in the spec's wording, with no new number.
- **F2**. New file `tests/factory/test_plan_fields.py`.

Round 2 (`9300012`) changes only the test file. Its `store` fixture no longer copies three of the suite's helpers. It imports `approved_parent` and `ticket_files` from `tests/factory/test_build_startup.py`, and `run` and `js` from `tests/factory/test_subtickets.py`. It keeps only the `add(plan)` closure. The diff is `6 insertions(+), 29 deletions(-)`, and the eight test cases are unchanged.

## Acceptance results

**Method.** The spec's fixture GIVEN block writes four shell scripts that the plan-parsing scenarios source. The permission system refused my run of that block as code taken from an outside file. So this round, the three scenarios that source `t0019-parent.sh` (dash-bulleted, star-bulleted, and refused) were not run verbatim. I checked them instead with a shell function I wrote myself. It runs the same six `bin/factory` steps the fixture runs, on a fresh `mktemp -d` store, and then runs each scenario's own plan text through `bin/factory subticket add T-0001 --file …`. The round-1 runs of those three scenarios, verbatim, are in my round-1 description. The verifier's runs on `381f4c6` are in its report. The code they exercise has not changed since `381f4c6`. Every other command below ran verbatim from the worktree. Every command that runs `bin/factory` or tests ran under `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`.

| Scenario | Kind | Before (base `9853737`, from round 1) | After (`9300012`, this round) |
|---|---|---|---|
| Dash-bulleted field lines keep their dependencies | NEW | All three sub-tickets came out `"state": "ready-for-implementer", "depends_on": [], "parallel_safe": false`, so `ST-2` and `ST-3` could be built at once. | Equivalent form: the exact expected list. `T-0001.1` is `[]`, `false`, ready. `T-0001.2` is `["T-0001.1"]`, `true`, waiting. `T-0001.3` is `["T-0001.2"]`, `true`, waiting. |
| Star-bulleted, bold, indented and plain field lines read as before | REGRESSION | not run | Equivalent form: the exact expected list, ending with `T-0001.3` labelled `T-0001-C`, `["T-0001.2"]`, `parallel_safe: false`. |
| A sub-ticket with no Depends on line is refused | NEW | Success JSON with `T-0001.2` at `"depends_on": []`, then `exit=0`, then `T-0001.1.yaml T-0001.2.yaml T-0001.yaml`. | Equivalent form, with stdout and stderr captured to separate files. stderr: `ST-2: no "Depends on:" line; write "Depends on: none" when it depends on nothing`. stdout: `{"ok": false, "error": …}` with the same text. Then `exit=2`, and the listing is `T-0001.yaml` alone, so nothing was written. |
| The planner prompt shows the parsed lines in every copy | NEW | `0 0 0 0 0` for each file | `docs/design.md 1 1 1 1 1`, `docs/prompts/04-planner.md 1 1 1 1 1`, `factory/prompts/planner.md 1 1 1 1 1`. Each copy shows the three parsed lines once and both new sentences once. |
| The planner block and its copies stay identical | REGRESSION | not run | `SAME`: the design doc block and both copies match byte for byte. |
| The changelog records the change in order | NEW | `1` then `CONTIGUOUS`, because S1 had already merged entry 48. The S2 clause was absent: `grep -cF "A plan's bulleted field lines lost every sub-ticket's dependencies" docs/changelog.md` printed `0`. | `1` then `CONTIGUOUS`: one `After issue #36` entry, numbered with no gap. The same grep prints `1`, so the entry carries the S2 clause. |
| The change adds no whitespace errors | REGRESSION (also the first gate) | not run | `exit=0` only |
| This repo's gate suite passes under a throwaway HOME | REGRESSION (also the second gate) | not run | `190 passed in 135.32s (0:02:15)`, no failures. This includes the 8 cases in `test_plan_fields.py`. |
| Intermediate check: only declared files change | NEW | empty | Exactly `docs/changelog.md`, `docs/design.md`, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`, `factory/subtickets.py`, `tests/factory/test_plan_fields.py`. |

Gates: `git diff --check main...HEAD` ran exactly as written, inside the whitespace scenario. For the suite gate, I ran the wrapped form that the acceptance scenario gives, not the bare `uv run --frozen pytest -q -p no:cacheprovider tests/factory`. The plan's shared notes say never to run tests with the real `HOME`. The verifier ran the bare form on `381f4c6`, and it passed.

## Tests added/changed

Added `tests/factory/test_plan_fields.py`, with 8 cases. Each drives `bin/factory subticket add` on a throwaway store whose T-0001 has passed the spec gate.
- `test_bulleted_field_lines_keep_dependencies_and_parallel_safety` runs with the `- ` and `* ` bullets, each with and without bold.
- `test_a_bullet_never_starts_a_sub_ticket` checks that a `- ST-2 / …` bullet does not become a sub-ticket.
- `test_depends_on_none_still_means_no_dependencies` includes a bulleted, bold `none.` line.
- `test_a_sub_ticket_with_no_depends_on_line_is_refused_by_name` runs with the line missing from the first sub-ticket and from the second. It checks for exit 2, the label and `Depends on:` in stderr, and that only `T-0001.yaml` is in `tickets/`.

After the round-2 fixture change, I ran the new file on a copy of base `9853737` (from `git archive`, plus the new file only). It gave `5 failed, 3 passed`, the same split as round 1: 3 of the 4 bullet cases and both refusal cases fail on base. On the PR head it gives `8 passed`, and `ruff check` on it gives `All checks passed!`. No existing test changed.

## Known gaps and uncertainties

- **Three scenarios were not run verbatim this round.** As explained under Acceptance results, the permission system refused the fixture block, so the plan-parsing scenarios ran in an equivalent form that I wrote. The verbatim runs are round 1's and the verifier's, on `381f4c6`. Since then only the test file has changed.
- **The changelog NEW check passed before the change.** S1 merged the `After issue #36` entry first, so the count-and-order part prints `1` and `CONTIGUOUS` on base, as the plan foresaw. The scenario's added condition, that the entry carries the S2 clause, failed before the change. I checked that with the grep shown in the table.
- **A bulleted field line anywhere in a block is now read.** A bulleted `Depends on:` or `Parallel-safe:` line inside a sub-ticket's Acceptance list would now be read as the field. A later one overrides an earlier one, as unbulleted lines already did. No plan in this store does this.
- **A pairwise answer still reads as an unconditional yes.** A line like `- Parallel-safe: yes with A … Not with B` is now read, and the harness treats it as safe alongside every sibling. The spec keeps this out of scope, and the new prompt line tells the planner to write `no` in that case.
- **The suite gate ran wrapped, not bare**, as explained under Acceptance results.
- **Correction to my round-1 description.** Round 1 said both refusal lines go to stderr. They do not: the `{"ok": false, …}` JSON goes to stdout, and only the plain message goes to stderr. The verifier found this, and my split capture this round confirms it. The criterion needs only that stderr contains `ST-2` and `Depends on:`, which it does.
- **The new test file now depends on two other test modules.** If `approved_parent`, `ticket_files`, `run` or `js` changes shape, this file changes with it. That is what the reviewer asked for, and three other test modules already import helpers this way.

## Out-of-scope observations

- `agents/factory-planner.md` still holds the older planner OUTPUT block, with the indented `ID / Title` example. The spec already notes this, and it is a protected path.
- When `subticket add` refuses a plan, `factory/workflows/build.js` parks the parent with the label `harness-bug:`. After this change, a refusal more often means a malformed plan than a harness bug. The spec already notes this too.

## Responses to findings

- [BLOCKING] reuse, `tests/factory/test_plan_fields.py` lines 21-48 duplicate `run`, `js` and `approved_parent`: FIXED in `9300012`. The fixture now calls `approved_parent(root, tmp_path)` and `run(root, "subticket", "add", tid, …)`, and `subtickets()` decodes through `js`. The refusal test also uses the existing `ticket_files` helper in place of its own listing. Net -23 lines. The 8 cases pass on the head and fail 5-of-8 on base, as before.
- [NIT] "planner" and "sub-ticket" unglossed in What changed: FIXED. Both are glossed in the first paragraph of What changed, in this description.
- Verifier correction, refusal JSON goes to stdout, not stderr: accepted and corrected under Known gaps. No code change was needed.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The only code change this round is the test fixture. The new tests pass on the head and fail on base for the stated faults, and the gate suite passes. The three plan-parsing scenarios ran in an equivalent, not verbatim, form this round.
ESCALATIONS:
- The spec's fixture GIVEN block could not be run in this session. The permission system refused it as code taken from an outside file. A role that must run a spec's fixture block verbatim cannot do so under this permission setting. I checked the three dependent scenarios with equivalent commands that I wrote myself, and I did not try to get around the refusal.
- Protected paths touched, all declared by the sub-ticket: harness `factory/subtickets.py` and `factory/prompts/planner.md`; generated `docs/prompts/04-planner.md`. The merge gate needs a human approval for them.
