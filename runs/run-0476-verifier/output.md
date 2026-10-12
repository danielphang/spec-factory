Commit: b1123b0bb2430ff9d23d9302c34e133b522c5aa2 (branch `factory/T-0046.1`, base 34de412fd5fa7f410654e6f6c496877e9608cad1)

Setup: I ran the PR side in the run worktree (`wt/`, clean, HEAD b1123b0, `main` = base). The base side ran in `scratch/base`, a `git archive` export of 34de412. Every command went through the fresh-HOME wrapper. The GIVEN block was extracted verbatim from `.factory/store/specs/T-0046/v3.md` (55 lines) and written to `scratch/given.sh`. I ran it with `TMPDIR=scratch/tmp`. I extracted the REGRESSION WHEN commands verbatim from the same file into `scratch/r1.sh` to `r6.sh`. The three "prints exactly" outputs were compared to the spec's expected blocks with Python string equality.

Per criterion:
- NEW | Only the store module lists a ticket's runs | base `3` | PR `0` | PASS
- NEW | The CLI and the stats report read the event log through a shared reader | base `3 0` | PR `0 1` | PASS
- NEW | One function records a status transition outside spec approval | base `5 0` | PR `1 1` | PASS
- NEW | Neither spec amend nor the dispatcher builds the in-flight list itself | base `2` | PR `0` | PASS
- NEW | One function reads the integration-branch tip | base `4 0` | PR `1 1` | PASS
- NEW | Record copies, row set-asides, planner-run checks and spec apply checks each have one definition | base `5 2 2 2` | PR `0 1 1 1` | PASS
- NEW | One line formats a failed-command park and one call cleans up a checker | base `18 3 0` | PR `1 1 2` | PASS
- REGRESSION | Status transitions write the same events and history entries | base: not run | PR: 14 lines, byte-identical to the expected block (exit 0) | PASS
- REGRESSION | Spec pinning and planner-run refusals keep their text | base: not run | PR: 4 lines, byte-identical | PASS
- REGRESSION | The dispatcher parks a refused store command with the same reason | base: not run | PR: 3 lines, byte-identical, including the `harness-bug: run start implementer:` prefix that `resolve --ruling` matches | PASS
- REGRESSION | The spec parser gives the same result as the base on every spec in the store | base: not run | PR: `files=272 checks=4034 differ=0`, nothing after it | PASS
- REGRESSION | The refactored harness has no unused imports or variables | base: not run | PR: `All checks passed!`, exit 0. uvx also printed its own download lines for ruff on first use. | PASS
- REGRESSION | The harness suite passes and no existing test file changes | base: not run | PR: `576 passed in 524.88s (0:08:44)`, and the `git diff --diff-filter=DMR ... -- tests` part printed nothing | PASS

Every NEW base value matches what verification.md predicted.

Gate suite: PASS
  `git diff --check main...HEAD`: exit 0, no output.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `576 passed in 479.51s (0:07:59)`. I ran it alone, with nothing else running. The timing test the PR description reported failing once under load (`test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`) passed both times here: in the gate run and in the REGRESSION suite run.

Probes: I wrote one script (`scratch/probe.py`), ran it once against the base package and once against the PR package, and diffed the two outputs.
- Run listing on a store with runs in non-sorted creation order, an unfinished run, another ticket's run, a run directory with no `meta.yaml` and a stray file in `runs/`. I called `compose._last_run_meta` (with and without `exclude`), `specstore.critic_rounds` and `compose.triage_capabilities`. → Identical output on base and PR. → OK
- A run whose `meta.yaml` is empty. → Base raises `AttributeError` in `critic_rounds` and `_last_run_meta`. The PR skips the run and returns `none` / `None`. This is the one behaviour change the spec's Decisions accept. → OK
- No `runs/` directory → identical on base and PR (empty result, and `clear_scratch` does nothing). → OK
- `clear_scratch` on scratch entries of several kinds: a directory, a symlink, a broken symlink, an unfinished run, another ticket's run, a run with no meta. → The same entries were removed and kept on base and PR. The broken symlink is removed on both. → OK
- Event-log readers on a log with two files written out of name order, a malformed line and a blank line. I called `cost._store_paths` (including a `store.migrated` event), `stats._load` and `cli.log_tail` with and without `--event`. → Identical on base and PR. The malformed line is skipped by cost/stats, and the record order is the same. → OK
- A JSON line that is valid JSON but not an object (`[1,2]`) in the log. → `cost._store_paths` raises `AttributeError` on both base and PR. This existed before the PR and was not changed by it. → OK
- `drive._harness_bug` with no `stderr` key, with `stderr: None`, and with stderr text. → `harness-bug: join: `, `harness-bug: join: `, `harness-bug: x y: e\n`. This matches the old inline f-string `{res.get('stderr') or ''}`. → OK

Other checks:
- `grep -n 'harness-bug' factory/drive.py` shows the format string only in `_harness_bug` (line 601). The five "unknown STATUS" parks and the `wait` park are unchanged, as design.md says.
- `_runs_for` appears nowhere in `factory`, `bin`, `agents` or `tests`.
- The PR changes only the eight files the Risk section names, all under the declared protected path `factory/**`.
- The implementer pointed three `cli.py` callers of `compose._runs_for` (`_check_drift`, `_planner_needed`, the conflict counter in `ticket_head`) at `store.ticket_runs(..., finished=True)`, which design.md did not list. I read each one: it keeps the same filter as before (finished runs of that role, in run-id order). The spec's requirement "Every caller MUST use that definition" covers this.

STATUS: VERIFIED
CONFIDENCE: high. All 7 NEW criteria fail on the base and pass on the PR with the predicted values. All 6 REGRESSION scenarios pass, three of them byte-identical to the spec. Both gate commands pass. The probes found no difference from the base outside the empty-meta change the spec accepts.
ESCALATIONS: none
