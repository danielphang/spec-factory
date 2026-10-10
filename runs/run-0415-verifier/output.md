Commit: ae19b1a0a3e7a085da3986d8737542672a60d007

This is a parent-close run for T-0040 (`factory drive`), which covers sub-tickets T-0040.1, T-0040.2 and T-0040.3. The head is `main` at ae19b1a, and `git rev-parse main HEAD` gives the same SHA for both. The base is 37848db, the commit before the first merge. I checked the base out as a detached worktree under scratch and removed that worktree afterwards.

Setup:
- Each checkout: `uv sync --frozen`.
- Every command ran in bash through the harness wrapper (fresh HOME), with `TMPDIR=<run>/scratch/tmp`.
- GIVEN blocks were run once, extracted verbatim:
  - `t0023-*` from `openspec/specs/human-resolution/spec.md`.
  - `t0024-*` from `openspec/specs/live-store-guard/spec.md`.
  - `t0040-*` from input.md lines 198-335. This text is byte-identical to `specs/T-0040/v4.md` lines 161-298 (checked with `diff`).
- Each WHEN command was taken verbatim from input.md. Outputs are in `scratch/pr-sN.out` and `scratch/base-sN.out`.

Per criterion:
- NEW | intake fixtures, same routes as the intake script
  - base: 4 lines `ready-for-triage script=5/5|5/5|2/2|1/1 drive=0/0 differ`. This is the spec's stated failure: there is no `drive` subcommand.
  - PR: `awaiting-spec-gate script=5/5 drive=5/5 same` / `parked script=5/5 drive=5/5 same` / `parked script=2/2 drive=2/2 same` / `parked script=1/1 drive=1/1 same`
  - PASS
- NEW | build fixtures, same routes as the build script
  - base: 4 lines `ready-for-planner script=4/4|6/6|4/4|1/1 drive=0/0 differ`
  - PR: `parked script=4/4 drive=4/4 same` / `planned script=6/6 drive=6/6 same` / `planned script=4/4 drive=4/4 same` / `planned script=1/1 drive=1/1 same`
  - PASS
- NEW | each role runs as one claude process with its prompt, model and tool limits
  - base: two empty lines
  - PR: `critic ok` / `spec_writer ok` / `triage ok` / `implementer ok` / `reviewer ok` / `verifier ok` / `verifier ok`
  - PASS
- NEW | each role run records its process's reply
  - base: `none`
  - PR: `triage=ok spec_writer=ok critic=ok`
  - PASS
- NEW | checkers at once, sub-tickets up to the parallel limit
  - base: `parallel=1: calls=0 max=0 checks-in-flight checks-in-flight`, then the same for `default`
  - PR: `parallel=1: calls=4 max=2 parked parked` / `parallel=default: calls=4 max=4 parked parked`
  - PASS
- NEW | intake step lines and the status file
  - base: `steps=no untagged=0 last=0 status= ignored=0`
  - PR: `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1`
  - PASS
- NEW | build step lines name the sub-ticket
  - base: `untagged=0 sub=no last=0`
  - PR: `untagged=0 sub=yes last=1`
  - PASS
- NEW | stopped driver: role process killed, run recorded as KILLED, resume works
  - base: `stop: exit=2 running=0 run= ready-for-triage in_flight: [] child=gone last=0` / `resumed: exit=2 ready-for-triage calls=`
  - PR: `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1` / `resumed: exit=0 closed calls=2`
  - PASS
- NEW | the driver marks its own store calls, never its roles', and passes a configured effort
  - base: `unmarked=2 marked=2 ready-for-triage calls=0 effort=0 dispatch=0 inside=2`
  - PR: `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2`
  - PASS
- REGRESSION | the Workflow scripts still take both fixtures to the end of their routes
  - base: not run
  - PR: `T-0001.1 merged T-0001 parked` / `T-0001 awaiting-spec-gate`
  - PASS
- NEW | the documents describe the driver
  - base: `starting=no depends=no built=no effort-gap=yes drive-row=no design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean`
  - PR: `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes buildspec=yes dontask-ban=yes whitespace=clean`
  - PASS

Every PR output matches the THEN text exactly. Every base output matches the "Today it prints" text in verification.md exactly, so each NEW criterion fails on base for the reason the spec gives.

Gate suite: PASS
  `git diff --check main...HEAD` exited 0. Head is `main`, so this diff is empty. As an extra check, `git diff --check 37848db HEAD` also exited 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `520 passed in 355.48s`, exit 0.

Probes. The parity probes use `t0040-parity.sh` with plays not in any scenario, comparing the script and the driver side by side:
- Intake parity: all 6 printed `same`, with matching call and run counts.
  - triage NEEDS-HUMAN → parked "NEEDS-HUMAN from triage".
  - triage CLARIFY → waiting-requester.
  - unknown STATUS BOGUS → parked "harness-bug: unknown STATUS BOGUS from triage".
  - spec_writer replying text but writing no output twice → parked "EMPTY-OUTPUT from spec_writer", 3/3 calls.
  - EMPTY-OUTPUT then a write, then critic ESCALATE → parked "ESCALATE from critic", 4/4 calls.
  - critic REVISE ×3 → parked "max rounds" at spec=2.
  - Result: OK.
- Build parity: all 5 printed `same`.
  - verifier FAILED ×2 → "max-round cutoff (verifier FAILED at round 2)", 6/6 calls.
  - REQUEST-CHANGES plus FAILED ×2 → "max-round cutoff (reviewer REQUEST-CHANGES, verifier FAILED at round 2)".
  - implementer process fails → "agent call failed: implementer: boom".
  - reviewer process fails while the verifier passes → "agent call failed: reviewer: rate", 3/3 calls.
  - implementer silent → "EMPTY-OUTPUT from implementer".
  - Result: OK. The routing is not special-cased to the scenario plays.
- A `claude` that prints non-JSON on stdout, writes stderr lines and exits 0:
  - It counts as a failed call. The run is `KILLED` and `meta.yaml` has `claude: null`.
  - `reply.json` holds the raw stdout.
  - The park reason is "agent call failed: triage: Error: some failure here", the last non-blank stderr line, as the design says.
  - Result: OK.
- No `claude` on PATH → parked "agent call failed: triage: cannot start claude: [Errno 2] …", exit 0 → OK.
- Phase and state edges, all OK:
  - `--phase build` on a ready-for-triage ticket printed `{"ticket": "T-0001", "state": "ready-for-triage", "note": "nothing to dispatch from this state", "ok": true}`, exit 0, with no claude call.
  - `--parallel 0` was refused by argparse with exit 2.
  - An unknown ticket gave a JSON error with exit 1.
- `--prompt-mode replace`:
  - argv has `--system-prompt-file` and no `--append-system-prompt-file`, and no `--effort` when none is configured.
  - The triage `--tools` list has no `Edit`.
  - The `--allowedTools` Edit rules are exactly `//<run>/output.md`, `//<run>/scratch/**` and `//<TMPDIR>/**`.
  - Result: OK.
- Real CLI, Claude Code 2.1.289 under a throwaway HOME, no model called:
  - `--tools`, `--allowedTools`, `--effort`, `--permission-mode`, `--add-dir` and `--output-format` are in `--help`.
  - The two hidden flags are accepted: they printed "Append system prompt file not found" and "System prompt file not found", where an unknown flag prints "unknown option".
  - Result: OK. The argv the driver builds is one the installed CLI accepts. Real model runs under `auto` remain Operator steps 1-3, as the spec says.
- Changed files, base..head: README.md, dev/build-harness.spec.md, docs/changelog.md, docs/design.md, factory/cli.py, factory/drive.py (new), factory/instance.template.yaml, factory/store.py, tests/factory/test_drive.py (new), tests/factory/test_drive_build.py (new) and tests/factory/test_run_scratch.py.
  - The only existing test changed is the three `test_run_scratch.py` assertions listed under "Tests to change".
  - The only protected path touched is `factory/**`, which the spec's Risk section declares.
  - `docs/prompts/`, `agents/`, `.factory/` and the two Workflow scripts are untouched.
  - Result: OK.

Out-of-scope observations:
- On macOS, `mktemp -d` with no template ignores `TMPDIR`. So the fixtures' throwaway stores (from `t0023-parent.sh`, `t0040-parity.sh` and the scenario commands) were created in the system temporary directory, not in this run's scratch directory. The spec's fixture text does this, not the driver. The store paths are then outside the "temporary directory" Edit rule whenever `TMPDIR` is changed. This did not affect any result.

STATUS: VERIFIED
CONFIDENCE: high, every scenario ran verbatim on head and base with the exact expected outputs, the full suite passed, and 14 off-script probes gave the same routes as the scripts
ESCALATIONS: none
