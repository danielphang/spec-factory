Sub-ticket: T-0019.2 (T-0019-S2, plan field lines), part of T-0019 (issue #36), approved spec v2. Branch `factory/T-0019.2`, commit `381f4c6`, on base `9853737`, which already holds the merged S1 (T-0019.1).

## What changed

Before this change, a planner's `Depends on:` line written as a `- ` list item was silently dropped. The sub-ticket was then recorded with no dependencies and built out of order. A sub-ticket with no `Depends on:` line at all got the same silent default. The harness now reads bulleted field lines and refuses such a plan, naming the sub-ticket. The planner prompt now shows the lines the harness reads, in the form it reads them.

- **C1** (`factory/subtickets.py` line 21). `FIELD_RE` now accepts an optional `- ` or `* ` bullet before any bold marks: `^\s*(?:[-*]\s+)?\**\s*([A-Z][A-Za-z -]+?)\s*:\s*\**\s*(.*)$`. This also fixes `* **Depends on:**`, which the old pattern did not read either: its `\**` took the bullet's `*`, and then the space stopped the match. `HEAD_RE` is unchanged, so a bullet still never starts a sub-ticket.
- **C2** (`parse`, lines 67, 74 and 95-96). Each block records whether it had a `depends on` field line. A block without one raises `ValueError("<label>: no \"Depends on:\" line; write \"Depends on: none\" when it depends on nothing")`. `subticket_add` (`factory/cli.py` lines 394-397) already turns that error into exit 2 before anything is written.
- **C3**. The module docstring now says that field lines may carry a list bullet and that every sub-ticket needs a `Depends on:` line.
- **D**. In the design doc's `## 4. Planner / decomposer` block, the four lines from `For each sub-ticket:` through `  Parallel-safe: yes | no (reason)` are replaced by the spec's eight lines. I re-copied the block with the spec's own awk extraction into `docs/prompts/04-planner.md`, and copied that file to `factory/prompts/planner.md`. In each file only that hunk changed.
- **E1, the S2 clause**. S1 had already merged changelog entry 48 with its own clause. As the plan says, I added the S2 clause to that entry as a second sentence, in the spec's wording. I did not add a new number.
- **F2**. New file `tests/factory/test_plan_fields.py`, described under Tests added.
- **Callers (coding rule 2).** `grep -rn` finds `subtickets.parse` called only from `factory/cli.py:395` (`subticket_add`) and `tests/factory/test_subtickets.py:185`. `FIELD_RE` is used only inside `parse`. The fix belongs in `parse` because both the pattern and the missing-line default live there.

## Acceptance results

The fixture GIVEN block was run once, verbatim. Every `bin/factory` scenario was run as `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <WHEN>)`, from the worktree, after `uv sync --frozen`.

| Scenario | Kind | Before (base `9853737`) | After (`381f4c6`) |
|---|---|---|---|
| Dash-bulleted field lines keep their dependencies | NEW | All three sub-tickets came out `"state": "ready-for-implementer", "depends_on": [], "parallel_safe": false`. This is the fault: `ST-2` and `ST-3` could be built at once. | The exact expected list. `T-0001.1`: `[]`, `false`, ready. `T-0001.2`: `["T-0001.1"]`, `true`, waiting. `T-0001.3`: `["T-0001.2"]`, `true`, waiting. |
| Star-bulleted, bold, indented and plain field lines read as before | REGRESSION | not run (runs after only) | The exact expected list, ending with `T-0001.3` labelled `T-0001-C`: `["T-0001.2"]`, `parallel_safe: false`. |
| A sub-ticket with no Depends on line is refused | NEW | Success JSON with `T-0001.2` at `"depends_on": []`, then `exit=0`, then `T-0001.1.yaml T-0001.2.yaml T-0001.yaml`. The plan was accepted silently. | stderr `ST-2: no "Depends on:" line; write "Depends on: none" when it depends on nothing` plus the refusal JSON. Then `exit=2`, then `T-0001.yaml` alone, so nothing was written. I confirmed with `2>&1 >/dev/null` that both refusal lines go to stderr. |
| The planner prompt shows the parsed lines in every copy | NEW | `0 0 0 0 0` for each of the three files | `docs/design.md 1 1 1 1 1`, `docs/prompts/04-planner.md 1 1 1 1 1`, `factory/prompts/planner.md 1 1 1 1 1` |
| The planner block and its copies stay identical | REGRESSION | not run | `SAME`: the design doc block and both copies match byte for byte. |
| The changelog records the change in order | NEW | `1` then `CONTIGUOUS`. This already passed before my change, because S1 had merged entry 48 (see Known gaps). The S2 clause was absent: `grep -cF "A plan's bulleted field lines lost every sub-ticket's dependencies"` printed `0`. | `1` then `CONTIGUOUS`, and the same grep prints `1`. Entry 48 carries the S2 clause, and the numbering has no gap. |
| The change adds no whitespace errors | REGRESSION (also the first gate) | not run | `exit=0` only |
| This repo's gate suite passes under a throwaway HOME | REGRESSION (also the second gate) | not run | `190 passed in 108.10s (0:01:48)`, `exit=0`. This includes the 8 cases in `test_plan_fields.py`. |
| Intermediate check: only declared files change | NEW | empty (no commits yet) | Exactly `docs/changelog.md`, `docs/design.md`, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`, `factory/subtickets.py`, `tests/factory/test_plan_fields.py` |

Gates: `git diff --check main...HEAD` ran exactly as written, inside the whitespace scenario above, with result `exit=0`. For the suite gate I ran the wrapped form that the scenario above prescribes, not the bare `uv run --frozen pytest -q -p no:cacheprovider tests/factory` listed in my input. The plan's shared notes say never to run tests with the real `HOME`, and the spec says the wrapped command replaces a bare run of the suite.

## Tests added/changed

Added `tests/factory/test_plan_fields.py`, with 8 cases. Each drives `bin/factory subticket add` on a throwaway store whose T-0001 has passed the spec gate.
- `test_bulleted_field_lines_keep_dependencies_and_parallel_safety`, run with the `- ` and `* ` bullets, each with and without bold. Before the fix, 3 of the 4 failed. Only the plain `* ` form already passed.
- `test_a_bullet_never_starts_a_sub_ticket`: a `- ST-2 / …` bullet does not become a sub-ticket.
- `test_depends_on_none_still_means_no_dependencies`, which includes a bulleted, bold `none.` line.
- `test_a_sub_ticket_with_no_depends_on_line_is_refused_by_name`, run with the line missing from the first sub-ticket and from the second. It checks for exit 2, the label and `Depends on:` in stderr, and that only `T-0001.yaml` is in `tickets/`. Before the fix, both cases failed.

I ran the new file before the fix: `5 failed, 3 passed`. The 3 that passed already pass on base, as their scenarios require. After the fix, the new file and `test_subtickets.py` together gave `14 passed`. No existing test changed.

## Known gaps and uncertainties

- **The changelog NEW check passed before the change.** S1 merged the `After issue #36` entry first, so the count-and-order part prints `1` and `CONTIGUOUS` on base. This is the case the plan describes. The scenario's added condition, that the entry carries the S2 clause, did fail before the change, which I checked with the grep shown in the table. I do not treat this as a spec defect.
- **A bulleted field line anywhere in a block is now read.** A bulleted `Depends on:` or `Parallel-safe:` line inside a sub-ticket's Acceptance list would now be read as the field. A later one overrides an earlier one, as unbulleted lines already did. I saw no plan that does this.
- **A pairwise answer still reads as unconditional yes.** A line like `- Parallel-safe: yes with A … Not with B` is now read, and it reads as `yes` with every sibling. The spec keeps this out of scope: the parser reads only a leading `yes`, and the new prompt line tells the planner to write `no` in that case.
- **The suite gate was run wrapped, not bare**, as explained under Acceptance results.
- **One probe ran under the real HOME.** I re-ran the refusal scenario once without the throwaway-HOME wrapper to see which stream each line goes to. That command only runs `bin/factory` against a `mktemp -d` scratch store. It runs no tests and touches nothing under `~`.
- **uv directories.** `uv sync --frozen`, and the first test run of the new file, ran under a throwaway HOME with `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` pointed at this machine's real uv directories. Those are the values the spec's Operator step 3 proposes for `run_env`, and they kept uv's managed Python 3.12. The full gate and the acceptance scenarios ran without those two variables, exactly as written.
- No `factory:` markers were added.

## Out-of-scope observations

- `agents/factory-planner.md` still holds the older planner OUTPUT block, with the indented `ID / Title` example. The spec already notes this, and it is a protected path.
- When `subticket add` refuses a plan, `factory/workflows/build.js` parks the parent with the label `harness-bug:`. After this change, a refusal more often means a malformed plan than a harness bug. The spec already notes this too.

## Responses to findings

None: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates were run on `381f4c6` and printed the expected output, and the new tests failed on base for the stated faults.
ESCALATIONS: none
