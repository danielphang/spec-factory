Commit: b3b978dce1d5544c7f346695292b8ef37f64eaae (base 2fbc170453cc3c549c487a6dd2c326b2b636e626)

## Review

Checked in the order the role asks.

1. Test integrity. Two existing test files change: `tests/factory/test_coding_standard.py` (fixture `system_prompts`, line 50) and `tests/factory/test_turn_economy.py` (fixture `run_prompts`, line 105). Both are listed under the spec's Tests to change, and each edit is exactly the one the spec names: the two arguments `"--model", "opus"` dropped from one `run start` call, nothing else. No assertion weakened, nothing skipped. `git diff --stat` on the range lists no other test file but the new `tests/factory/test_run_start_model.py`. Clean.

2. Correctness. `factory/cli.py:203-205`: the model is read from `cfg["models"][a.role]` directly after the unknown-role check and before `store.load_ticket`, and a differing `--model` raises `Refused` with the exact text the spec's Decision fixes (no backtick, `$` or double quote). The `except Refused` handler at `cli.py:873-876` prints it to stderr and returns 2. The check sits before `tripwire.baseline` and `store.next_run_id`, so nothing is reserved or written. `cli.py:223` (old `model = a.model or ...`) is removed, and `meta`, the event and the printed JSON keep the `model` key. Confirmed by running the new file through the fresh-HOME wrapper: `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_run_start_model.py` printed `7 passed in 1.60s`.
   - KeyError concern (Known gaps): `retro` is not in `ROLES` (`cli.py:27`), so the unknown-role guard fires first for it; the template and `.factory/instance.yaml` both name every one of the seven roles. No regression on any existing caller.
   - Other test callers passing `--model opus` for triage (`test_p0_cli.py:72`, `test_instance.py:236`, `test_writing_standard.py:41`) match the template's `triage: opus`, as the PR says.

3. Scope. The diff touches only the parts the spec lists (A.1-A.3, B.1-B.2, C.1-C.2). `factory/cli.py` is 884 lines, under 900. No change to the Workflow scripts or `drive.py`.

4. Silent behavior changes. Only the one the spec asks for: a `--model` that differs is now refused. The order of guards puts the model refusal before the ready-state refusal, which design A.1 orders this way; the PR names it under Known gaps.

5. Security and data safety. Nothing new is read or written; the refusal path writes less than before.

6. Protected paths. `factory/cli.py` is listed under the parent spec's Risk ("Protected paths: `factory/cli.py`"). Recorded under ESCALATIONS for the gate; it does not change the verdict.

7. Coding standard. No helper, class or dependency added; the fix is three lines in the one function every caller reaches (rule 2: the PR names the callers it grepped). No `factory:` marker owed. Lean already.

8. PR description. What changed opens with what was wrong and for whom, glosses `run start`, the clerk and "parked" at first use, and Known gaps names the two real uncertainties. Readable at the gate as it stands.

Findings: none.

Prior findings: none (round 1).

Out-of-scope observations:
- The implementer's own observation stands: `dev/build-harness.spec.md` line 125 (D6, "`run start --model` records it") and line 276 (`runRole`'s park reason) still describe the old relay loosely. Neither contradicts the new text, and the spec scoped the edit to the line-203 entry, so not a finding here.

STATUS: APPROVE
CONFIDENCE: high. The diff is small and matches each lettered part of the spec; the one check I ran (the new test file, 7 passed) confirms the guard's text and ordering, and the only existing-test edits are the two the spec authorises, verbatim.
ESCALATIONS: protected path `factory/cli.py` touched, declared in the approved spec's Risk section (for the record; no action needed)
