Commit: 9a99851bd15fe781c814231bb952513d1b597438 (branch `factory/T-0027.1`, worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0382-verifier/wt`, clean). Base 89290547a33a6091860c850fdda7ff285b409fa0, which is also `main` and the merge base.

How I ran it: I took the GIVEN block and the seven WHEN commands for the "spec-amendment" capability straight from the pinned spec `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`, so nothing was retyped. I ran each one with bash, through the running-code wrapper, from the root of the tree under test, after `uv sync --frozen`. The GIVEN block ran once per tree. For the base I extracted `git archive 8929054` into `scratch/base` and made it its own git repository. Without that, `factory init` refuses the snapshot because it sits inside the store checkout, and no spec store is created. Diff scope (`git diff --stat main...HEAD`): `factory/cli.py` +97, `factory/specstore.py` +70, and a new file `tests/factory/test_spec_amend.py` +346. Both protected paths are declared in the sub-ticket.

Per criterion:
- NEW | intent-unchanged amendment re-pins and keeps tasks | base: `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged` | PR: `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged` | PASS
- NEW | later implementer run gets the amended spec; the record lists the changes | base: `changed=0 merged=0 reason=0 logged=0` / `amended=0 old=1 run_version=1` | PR: `changed=1 merged=1 reason=1 logged=1` / `amended=1 old=0 run_version=2` | PASS
- NEW | archive after an amendment | base: `archive=0 hello=0 hi=1` | PR: `archive=0 hello=1 hi=0` | PASS
- NEW | intent declared or found changed is refused, with a restart note | base: `intent=changed exit_json=0 restart=0 decision=0 merged=0 pending=0 paths=0` / the same for `intent=unchanged` / `"approved_version": 1 versions=1 records=0` | PR: `intent=changed exit_json=1 restart=1 decision=0 merged=1 pending=1 paths=1` / `intent=unchanged exit_json=1 restart=1 decision=1 merged=1 pending=1 paths=1` / `"approved_version": 1 versions=1 records=0` | PASS
- NEW | amendment after archive is refused | base: `late=0 changes=archive hello=0` | PR: `late=1 changes=archive hello=1` | PASS
- NEW | malformed version, sub-ticket target and two-line reason are refused | base: `malformed=0 subticket=0 reason=0 "approved_version": 1 v2=0 records=0` | PR: `malformed=1 subticket=1 reason=1 "approved_version": 1 v2=0 records=0` | PASS
- NEW | refused while a sub-ticket's run is in flight, naming the run | base: `exit=2 names_run=0 "approved_version": 1 v2=0 pinned_old=1 records=0` | PR: `exit=2 names_run=1 "approved_version": 1 v2=0 pinned_old=1 records=0` | PASS
- REGRESSION | `uv sync --frozen && uv run --frozen pytest -q -p no:cacheprovider tests/factory` | base: not run | PR: `446 passed in 310.11s`. `main` collects 418 (`--collect-only` on the base snapshot) and the new file collects 28; 418 + 28 = 446 | PASS
- REGRESSION | `(git diff --check main...HEAD; echo "exit=$?")` | base: not run | PR: `exit=0` only | PASS

Every base output matches the "today" output in the spec's `verification.md` exactly. So each NEW criterion fails on base for the stated reason (`amend` is not a command) and passes on the PR.

Gate suite: PASS
  `git diff --check main...HEAD` exited 0, and `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `446 passed`. Both ran in the worktree through the wrapper.

Probes (on the PR head, with the spec's fixture):
- Amend while a sub-ticket is parked (the motivating case), with a reason that has a trailing newline → `ok: true`, v2; the parked sub-ticket's `spec` moved to `{"version": 2, "approved_version": 2}`; `planned_from: 1` unchanged in both sub-ticket yamls → OK
- Second amendment in a row that renames the scenario and reflows the requirement statement's whitespace → `ok: true`, v3, `amendment-2.md` lists `- added: Greeting is shown` and `- removed: Greeting is printed` → OK
- Problem body changed (`x` to `y`) against the approved v3 → exit 2, `intent changed (the Problem section)`, restart note lists the unmerged sub-tickets `ready-for-implementer` and `parked` with all five commands → OK
- Statement case change (`SHALL greet` to `SHALL Greet`) → refused, `requirement restated: demo ADDED Greets`; a new requirement → refused, `requirement added: demo ADDED Waves`; a Decisions line changed only in whitespace, plus a design-text edit → accepted → OK (the check is not limited to the tested Decisions/Problem cases)
- Whitespace-only reason and a reason holding `\r` → both refused, `--reason is one non-blank line of text`, nothing written → OK
- A `--file` path that does not exist → exit 1, not exit 2, nothing written. The PR lists this as a known gap, and the spec's refusal list does not cover it → OK (noted)
- An amendment identical to the approved version is accepted. It writes a new version with no changed scenarios, as the PR's known gaps say. The spec does not ask for a refusal → OK (noted)

Out-of-scope observations:
- The fixture's `mktemp -d` ignored `TMPDIR` on this machine. The throwaway stores went to the system temp dir (`/var/folders/.../T/tmp.*`), not the scratch dir. They contain only fixture data.
- No workflow script or role prompt names `spec amend` (`grep -rn 'spec amend' factory/workflows factory/prompts agents` found nothing). This is consistent with the human-only decision.

STATUS: VERIFIED
CONFIDENCE: high. All seven NEW commands print the exact expected lines on the PR and the spec's stated "today" lines on base, both gates pass (446 = 418 + 28), and probes outside the tested inputs behave as the spec says.
ESCALATIONS: none
