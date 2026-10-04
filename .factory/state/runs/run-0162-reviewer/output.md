Commit: 7a4967a055bc40e3839c65fc00416299d90db350

Reviewed in the worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0162-reviewer/wt` (branch `factory/T-0018.1`, base `d0300d3`). `git log` confirms one commit on top of the base; `git diff --stat d0300d3...HEAD` lists the ten files the PR description names and no others.

## Checks, in order

1. **Test integrity.** No existing test file is in the diff (`git diff --stat`: the only `tests/` path is the new `tests/factory/test_build_startup.py`). No assertion weakened, no skip, no hard-coded expected output. The new test file imports `PLAN_LETTERS`, `js`, `run`, `ticket` from `test_subtickets.py`; all four exist there (lines 15, 75, 70, 102). Clean.

2. **Correctness.** I re-ran, on head, every runnable acceptance scenario from the parent's `verification.md`, with the GIVEN block extracted from `.factory/state/specs/T-0018/v2.md` lines 153-201 into a scratch `TMPDIR`, and the two gate commands:
   - Intake on an approved ticket: `returned ready-for-planner`, `ticket T-0001 ready-for-planner in_flight=0 reason=-`, runs end at `run-0003-critic`. No planner run. PASS.
   - Build repairs a planned parent with no sub-tickets: `ticket T-0001.1 parked … reason=budget kill: implementer`, `run run-0005-implementer KILLED`, `source: plan:run-0004-planner`. PASS.
   - Build parks a parent it cannot repair: `returned parked`, `ticket T-0001 parked in_flight=0 reason=no sub-tickets, and none could be created from the recorded plan: no recorded planner run found for T-0001 (latest plan.added source: tests/…/planner-1.md); …`, no `T-0001.1` line. PASS.
   - `subticket add T-0001` with no source: last JSON line `"ok": true` naming `T-0001.1`, `exit=0`, `source: plan:run-0004-planner`. PASS. With a `--file` plan: refusal text, `exit=2`, no `TypeError`, listing `T-0001.yaml` alone. PASS.
   - Thrown `agent()` in intake (triage): `returned parked`, `reason=agent call failed: triage: agent type 'factory-triage' not found`, `run run-0001-triage KILLED`. PASS.
   - Thrown `agent()` in the build (implementer): `ticket T-0001.1 parked … reason=agent call failed: implementer: agent type 'factory-implementer' not found`, `run run-0005-implementer KILLED`. PASS.
   - The reviewer-left behaviour C2 cleanup: with the driver throwing on `verifier`, `run run-0007-verifier KILLED`, the sub-ticket parked with `agent call failed: verifier: …`, and `ls runs/run-0007-verifier/` shows `diff.patch input.md meta.yaml system-prompt.txt` with no `wt/`. `run cleanup` ran on the throw path (`factory/cli.py:261-267` removes the worktree for reviewer/verifier roles).
   - Gate lines: the four marked forms give `PASS|`, `PASS|`, `PASS|`, `FAIL|2 failed`; the plain forms and the prose line give `PASS|`, `FAIL|1 failed`, `FAIL|missing Gate suite line`. PASS.
   - Documents: `docs/design.md 1 1 0`, `docs/prompts/07-verifier.md 1 1 0`, `factory/prompts/verifier.md 1 1 0`; the awk/diff prints `SAME`; README greps `1` then `0`; changelog greps `1` then `1`; build spec grep `1`. PASS.
   - `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `171 passed in 130.87s`, exit 0. `git diff --check main...HEAD`: no output, exit 0.

   Reading-only checks the spec leaves to the reviewer:
   - C1 (`build.js:233-234`): `!pc.ok` now parks `parent-check refused: <stderr>` and returns `parked`; a successful check in another state returns as before. Correct and not silent.
   - B3 once-per-run (`build.js:208-223`): `first` is cleared inside the repair branch and again right after it, so the repair runs at most once. If the repair succeeds but creates zero sub-tickets, the next iteration breaks out of the loop and `parent-check` refuses with `has no sub-tickets` (`cli.py` parent-check), which C1 now parks. Still not silent.
   - B1 (`cli.py:366-377`): log files are named `YYYY-MM.jsonl` (`store.py:78`), so `sorted(glob)` is chronological and "latest `plan.added`" is the last match in file order. `plan_add` writes `source=a.from_run or a.file` (`cli.py:360`), so a `--from-run` source is the bare run id and a `--file` source is a path; the `"/" in source` and `runs/<source>/meta.yaml` tests refuse the latter. The store is unchanged on refusal (the test asserts the log byte-for-byte).
   - D1 (`cli.py:496-497`): `(.*)` under `re.M` stops at the newline, so `**Gate suite: FAIL** 2 failed` yields detail `2 failed` after stripping ` \t\r*`. The implementer's Known gap is right that a verdict split across two lines (`Gate suite:\nPASS`) no longer matches; the spec pinned `[ \t*]*`, and the new prompt text puts the failing output "on the lines below it", so the one-line form is now the contract. Not a finding.
   - C2 moved stub seam (`build.js:98-103`): the seam now runs after the `try` under `args.stubs && role === 'implementer' && start.worktree`, which is the same condition as before (it was inside `if (args.stubs)` and `if (role === 'implementer' && start.worktree)`). `stubCount[role]` is still only incremented in the stub branch, so the seam reads the same `<role>-<n>.sh`. Equivalent.

3. **Scope.** Every hunk maps to a lettered part. The parser help line on `subticket add` (`cli.py:1075-1076`) is a one-line extra documenting B1's new default; I would not ask for its removal.

4. **Silent behaviour changes.** `ready-implementers` gains a key (B2, spec'd); existing readers are unaffected (`test_subtickets.py`, `test_shepherd.py` still pass). `intake.js` `meta.phases` loses `Plan` and `meta.description` loses `-> Planner` (A, spec'd). Nothing else a caller would notice.

5. **Security and data safety.** No new destructive operation, no secret. The one exposure is pre-existing: `park()` in both scripts (`build.js:60`, `intake.js:69`) puts the reason inside a double-quoted shell argument and escapes only `"`, and the new `agent call failed: <role>: <error>` reason carries a runtime error message. The spec's Decisions direct "Pass the reason through the existing `park()`", so this is by design here, and the implementer disclosed it. Noted under Out-of-scope observations.

6. **Protected paths.** `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/cli.py`, `factory/prompts/verifier.md` (harness; the last also an agent prompt) and `docs/prompts/07-verifier.md` (generated, re-copied: the awk/diff check prints `SAME`). All are declared in the parent's Risk section and the sub-ticket. Listed under ESCALATIONS; the merge gate needs a human approval.

7. **Coding standard.** Rule 2: the PR description names the callers of `runRole`, `results record`, `ready-implementers` and `subticket add`; I confirmed `runRole` is called from `build.js` lines 125, 148, 191, 248 and each returns on `null`. Rule 3: no shortcut needing a `factory:` marker; the linear log scan is the same shape as `log_tail` and the description says so. Rule 5: the names used (`parked`, `KILLED`, `subtickets`, `plan.added`) are the store's existing names. Rule 1/4: see the NIT below.

8. **PR description.** What changed opens with the problem and who has it, glosses "park" and "the clerk" at first use, and says in words what each part does. Known gaps names the two-line gate form, the log scan, the README present-tense rule and the driver-only check of the throw path, each with what is uncertain. Readable at the gate. No finding.

## Findings

- [NIT] `factory/cli.py:369-372`: `_recorded_plan_run` repeats `log_tail`'s read-the-log loop (`cli.py:982-985`: sorted glob of `log/*.jsonl`, `read_text`, `splitlines`, `json.loads`) → a later change to the log layout (a new file name pattern, a different encoding) must be made twice. Not a `reuse:` finding: the repo has no shared log-reading helper to call, and extracting one would edit `log_tail`, which the sub-ticket's parts do not cover. A follow-up `_log_lines(root)` used by both would remove about 3 lines.

Over-building pass: no tagged finding. Lean already, bar the NIT.

## Prior findings

n/a: round 1.

## Out-of-scope observations

- `park()` shell quoting (`build.js:60`, `intake.js:69`): a reason containing `` ` ``, `$(` or `$VAR` would be expanded by the clerk's shell. The new `agent call failed: …` reason makes a runtime-supplied message reach that argument, and the new `no sub-tickets…` and `parent-check refused: …` reasons carry CLI stderr, which echoes the `plan.added` source path. Every existing `harness-bug: …: ${stderr}` reason has the same shape. Worth an issue; not this ticket's.
- Park reasons built from stderr keep stderr's trailing newline, so the driver listing shows a blank line after the `no sub-tickets…` reason (seen in my run). Cosmetic and pre-existing for the `harness-bug:` reasons.
- `dev/build-harness.spec.md` line 285 now describes `parent-check` twice in step 2 (once as "When nothing is left to build … a refusal parks", once as "When the parent reaches `ready-for-parent-verify` … `parent-check` first"). The code calls it once (`build.js:232`). Accurate but redundant; a later doc pass can fold them.

STATUS: APPROVE
CONFIDENCE: high. Every NEW and REGRESSION acceptance scenario, both gate commands and the reviewer-left C2 cleanup were re-run by me on head `7a4967a` and matched the spec's THEN lines; C1 and the B3 once-per-run limit were checked by reading the code at the cited lines. No existing test changed.
ESCALATIONS:
- Protected paths touched, all declared in the parent's Risk section and the sub-ticket: harness `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/cli.py`, `factory/prompts/verifier.md` (also a guardrail path, an agent prompt; the parent asks for this exact two-line change); generated `docs/prompts/07-verifier.md` (re-copied from the changed `docs/design.md` block; the identity check prints `SAME`). The merge gate requires a human approval.
