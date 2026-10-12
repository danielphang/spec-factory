## ST-3 / Record `factory stats` in README, the design, the principles, the build spec and the changelog
Depends on: ST-2
Parallel-safe: no (its design-doc figures are printed by ST-2's command)

Parent: T-0043, spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part E, all of it.
- `README.md`: the read-only list in "Where a human decides", the sentence in "Accepting a harness revision", the new `### Counting what each role catches and costs` subsection, the "What depends on Claude Code" row, the **Built** bullet and the status date. Read its "Maintaining this page" section first.
- `docs/design.md`: the fence paragraph's read-only list, the role-context paragraph's lock clause, and the model-per-role paragraph's citation of `factory stats`, with the figures it prints over both stores with `--until 2026-10-07T12:00 --transcripts <transcripts dir>`. The §8 prompt block is unchanged.
- `docs/principles.md` §4: 3 BLOCKING findings in place of 1; the "Implemented by:" and "Planned:" lines.
- `dev/build-harness.spec.md`: the `**`factory stats`**` paragraph after the `**`factory drive`**` paragraph.
- `docs/changelog.md`: entry 70, in the form of entries 66 to 69.

Acceptance:
- NEW. "The documents record factory stats". WHEN the spec's command (the `y()`/`j()` greps over README.md, docs/design.md, docs/principles.md and dev/build-harness.spec.md, the changelog numbering `awk`, the last entry's `#70`/`#61`/`factory stats`/`message id` count, and `git diff --check main...HEAD`) THEN it prints exactly `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no buildspec=yes prompts=0`, then `CONTIGUOUS`, then `4`, then `clean`.
- REGRESSION (made true by ST-2). "Stats reproduces the hand count on the two live stores": the spec's command and its eight THEN lines, unchanged. It confirms that the command whose figures the design doc quotes still prints them.
- REGRESSION (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory` THEN the whole suite passes.

Interim tests: none
Tests to change: none
Protected paths: none
Out of scope: any code or test change; any file under `docs/prompts/` or `factory/prompts/`, including the §8 retro block and its copy; feeding the figures into the retro's input (issue #42); restating figures quoted from `factory/cost.py` before this change, such as changelog entries 58 and 67.

---

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v2) already names its three seams (design.md, "Proposed change": ST-1 is part A, ST-2 is parts B and C, ST-3 is part E, with part D's tests split between them). This plan follows those seams and does not split further: each one is a single reviewable change, and a fourth would only add a re-verify cycle. The three run in a chain, because each needs the previous one's code or output.

Checked on this checkout (`main` at `5215c5f`, the revision verification.md was captured on): `factory/cost.py` exists and has `tally()` at line 47 and no `transcript_usage`, `match_transcripts` or `gate_failures`; `factory/cli.py` has `build_parser()` at line 1753, `READ_ONLY` at line 1939, `main()` at line 1969 and no `"stats"`; `factory/stats.py`, `tests/factory/test_cost_once.py` and `tests/factory/test_stats.py` do not exist; `tests/factory/test_live_store_guard.py` exists; no file under `tests/factory/` mentions `factory.cost`, `tally` or `READ_ONLY`; and the log shows no earlier plan or sub-ticket for T-0043.

---
