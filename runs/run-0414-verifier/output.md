Commit: 0e99ddad7eb10387369fac62286f8520fd6a1a67

How this was run: the PR worktree `wt` at that head (clean, `main` = base `18fbe88`), and a temporary detached worktree of base `18fbe88` under this run's scratch directory, removed afterwards. Every command ran through the running-code wrapper. `TMPDIR` for the fixtures was `scratch/tmp`. The GIVEN blocks came straight from the store's current truth (`openspec/specs/human-resolution/spec.md` lines 13–65, `openspec/specs/live-store-guard/spec.md` lines 13–67) and from the change spec (`openspec/changes/T-0040/specs/build-dispatch/spec.md` lines 11–148, the same text as input.md lines 262–399 apart from the fence line). The WHEN commands were pulled out of input.md lines 402–471 by script, not retyped, and run under bash from the PR worktree after `uv sync --frozen`. Logs: `scratch/regress.log` and `scratch/pytest.log`.

Per criterion:
- NEW | "The documents describe the driver" (the sub-ticket's WHEN, as written) | base: `starting=no depends=no built=no effort-gap=yes drive-row=no design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean`. This is the spec's "today" line, and it fails for the reason the spec gives. | PR: `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes buildspec=yes dontask-ban=yes whitespace=clean`, the exact THEN line. The same result came from zsh and from bash. | PASS
- REGRESSION | intake parity (input.md:402) | base: not run | PR: `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same` | PASS
- REGRESSION | build parity (:410) | base: not run | PR: `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same` | PASS
- REGRESSION | role argv (:418) | base: not run | PR: `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok` | PASS
- REGRESSION | reply record (:426) | base: not run | PR: `triage=ok spec_writer=ok critic=ok` | PASS
- REGRESSION | concurrency (:434) | base: not run | PR: `parallel=1: calls=4 max=2 parked parked`, `parallel=default: calls=4 max=4 parked parked` | PASS
- REGRESSION | intake step lines (:442) | base: not run | PR: `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1` | PASS
- REGRESSION | build step lines (:447) | base: not run | PR: `untagged=0 sub=yes last=1` | PASS
- REGRESSION | stop and resume (:455) | base: not run | PR: `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, `resumed: exit=0 closed calls=2` | PASS
- REGRESSION | marker and effort (:463) | base: not run | PR: `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2` | PASS
- REGRESSION | Workflow scripts (:471) | base: not run | PR: `T-0001.1 merged T-0001 parked`, `T-0001 awaiting-spec-gate` | PASS
- Intermediate check | `uv run --frozen pytest -q -p no:cacheprovider tests/factory` (wrapped) | base: not run | PR: `520 passed in 350.77s (0:05:50)`, exit 0 | PASS. This was the gate's own run.

Gate suite: PASS
  `git diff --check main...HEAD` (wrapped, exactly as given): no output, exit 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory` (wrapped, exactly as given): `520 passed in 350.77s`, exit 0.

Probes:
The NEW check only greps for keywords. These probes test whether the text behind those keywords is true and whether the change stayed within its scope.
- Prompt blocks in `docs/design.md`: a script pulled out every ```` ```text ```` block on base and on PR → 10 blocks each, identical. `git diff --stat 18fbe88 HEAD -- docs/prompts agents factory bin tests .factory` → empty. → OK. No prompt block, protected path or code changed.
- Is the README's how-to true of the code? Checked against `factory/drive.py` and `factory/cli.py`:
  - The phase states match `INTAKE_STATES`/`BUILD_STATES` (drive.py:35–36).
  - "nothing to dispatch from this state" matches drive.py:271 and :417.
  - `--parallel` defaults to 2 (cli.py:1904).
  - `--effort` is passed only when it is set (drive.py:101–102).
  - The status file is `drive/<ticket>.yaml`, written with `write_yaml` and never deleted (drive.py:132, 139), which matches "kept until the next drive".
  - Exit 2 on an unmarked fence refusal matches `unmarked=2` above.
  - → OK
- "Neither target sets it yet" (effort): `grep effort` on `.factory/instance.yaml` here and in `~/dev/nanobot-upstream/.factory/instance.yaml` (read only) → no match. → OK
- "Five pieces assume Claude Code": counted the `| yes |` rows in that section of the PR README → 5. → OK
- The re-derived README figures "40 tickets and 47 sub-tickets": counted `^T-[0-9]+\.yaml$` and `^T-[0-9]+\.[0-9]+\.yaml$` in `.factory/store/tickets` → 40 and 47. → OK, but they hold only as of today.
- The removed **Not built** bullet: "Per-role effort" now appears only in the Built bullet (README:962). The **Not built** section has 0 lines mentioning effort. → OK. The bullet was removed, not just the phrase the check greps for.
- Changelog: the entries run 65, 66, 67, and then "Declined:" at line 73. Entry 67 cites #65, the T-0027.2 failure, and #22, #28, #47 and #24 as absorbed. → OK

STATUS: VERIFIED
CONFIDENCE: high, because the NEW criterion fails on base exactly as the spec says and passes exactly on the PR, all ten regression scenarios printed their THEN lines on this head, both gates passed, and the probes found the documents' claims match the code. The one thing not checked is the driver's behaviour under a real `claude`, which Operator step 1 covers.
ESCALATIONS: none

Out-of-scope observations:
- The sub-ticket's REGRESSION line says "nine" scenarios, but it names ten and the spec has ten WHENs. All ten were run. The miscount is in the plan text and changes nothing.
- The implementer made four README edits the sub-ticket does not list: the directory tree, the fence bullet, the "Running on another agent host" sentence, and "Related work and history". Each fixes a sentence this change would otherwise have left stale. Whether they are in scope is for the code reviewer to judge, not something the acceptance criteria decide.
