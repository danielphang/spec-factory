## ST-1 / Small-change lane: gate commands may declare paths, and a one-sub-ticket spec skips the planner
Depends on: none
Parallel-safe: yes

Parent: T-0028, approved spec v1 (`.factory/store/specs/T-0028/v1.md`, change folder `.factory/store/openspec/changes/T-0028/`). Read it for context. Do NOT implement parts outside this sub-ticket.

One sub-ticket. The spec sizes the change at about 380 lines, half of them tests, and says it fits one reviewable merge (design.md, Proposed change, opening paragraph). Splitting A from B looks possible but buys nothing and breaks a scenario:
- A and B both edit `factory/cli.py`, `README.md`, `docs/design.md` and `dev/build-harness.spec.md`, so two sub-tickets could not run in parallel and the second would need a catch-up run anyway.
- C.2 asks for one changelog entry covering both parts. The scenario "The changelog records the small-change lane as its last entry" needs the last entry to name all five of `paths`, `SKIPPED`, `plan whole-spec`, `NEEDS-SPLIT` and `seams`. Under a split, the first sub-ticket either fails that check or writes the second's entry ahead of its code.
- The operator can still drop part A at the gate, as the Decisions say, by deleting it and its scenarios from the spec. A split is not needed for that.

(Under the rule this ticket adds, this spec would itself have skipped the planner: no NEEDS-SPLIT, no seam heading, no earlier planner run.)

Scope: parts A (A.1 to A.7), B (B.1 to B.4) and C (C.1 to C.4) of the parent's Proposed change, all of it.

Anchors re-checked on `main` at `a69aaf4`. The spec was written at `0b1abad`, and some line numbers have moved; the named functions and texts are unchanged:
- `factory/compose.py:44` `gate_commands`; `:177` the "Gate commands (run each from …" sentence; `:14` `_runs_for`.
- `factory/cli.py:198` `run_start`, `:267` `_start_build_run`, `:422` `subticket_add`, `:512` `results_record`; the `plan` subparser's `add` at `:1377`.
- `factory/store.py:228` `subtickets_of`, `:244` `record_result`; `factory/gitops.py:31` `git`; `factory/specstore.py:52` `is_active`, `:77` `lines_outside_fences`, `:155` `scenario_names`.
- `factory/workflows/build.js:207-213` phase 1 (the spec says 202-217).
- `README.md:89` is "The build workflow runs the planner, which …" (the spec says line 88).
- `dev/build-harness.spec.md:206` is the command list.
- `factory/instance.template.yaml:21` is `gate_commands: []`.
- `docs/changelog.md`: the last numbered entry is now 55 (#49), not 52. The new entry takes the next free number at merge (Risk, last bullet). The scenario checks only that the numbering is contiguous.
- `tests/factory/test_gate_paths.py` and `tests/factory/test_whole_spec_plan.py` do not exist yet. `tests/factory/test_parent_close_reuse.py` exists, and B.4 uses it as the model.

Acceptance: every scenario of the parent, with its `verification.md` label. Run commands from the repo root after `uv sync --frozen`, with `node` on `PATH`, under the fresh-HOME wrapper, and with `TMPDIR` set to the run's scratch directory for the fixtures. Take each WHEN verbatim from the named spec file. Several are too long to restate here without risking a transcription error, so for those this list gives the opening and the THEN.

Fixtures (GIVEN blocks, written once, verbatim):
- `${TMPDIR:-/tmp}/t0028-sub.sh`: the `cat > … <<'EOF' … EOF` block in `specs/gate-commands/spec.md`, scenario "A gate command scoped to paths is skipped for a diff that touches none of them".
- `${TMPDIR:-/tmp}/t0028-plan.sh`: the block in `specs/sub-ticket-planning/spec.md`, scenario "A spec that needs one sub-ticket becomes that sub-ticket without a planner run".
- `${TMPDIR:-/tmp}/t0023-wf.mjs`: the build-dispatch scenarios reuse it. It is defined in another ticket's spec, T-0023's approved v2 (`.factory/store/specs/T-0023/v2.md`), in the GIVEN of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling". The `cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'` block starts at line 228.

From `specs/gate-commands/spec.md`:
- A gate command scoped to paths is skipped for a diff that touches none of them (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && echo "compose=$COMPOSE run=… skipped=… meta=…")`, verbatim.
  - THEN it prints exactly `compose=0 run=1 skipped=1 meta=1`.
- A diff that touches a scoped command's paths runs that command (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh src/a.txt scoped && echo "compose=$COMPOSE run=… skipped=…")`, verbatim.
  - THEN it prints exactly `compose=0 run=1 skipped=0`.
- A gate command with no paths runs on every diff, as today (REGRESSION).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md plain && echo "compose=$COMPOSE run=… skipped=…")`, verbatim.
  - THEN it prints exactly `compose=0 run=1 skipped=0`.
- A skipped gate command is recorded on the gate result, and the merge still needs a passing gate (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && for g in FAIL PASS; do … done)`, verbatim.
  - THEN it prints exactly `FAIL: merge=2 recorded=yes`, then `PASS: merge=0 recorded=yes`.
- The implementer is still given every gate command (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && $B run compose $I >/dev/null 2>&1; echo "compose=$? both=… skipped=…")`, verbatim.
  - THEN it prints exactly `compose=0 both=1 skipped=0`.
- A malformed gate entry refuses a checker's run start and creates no run (NEW).
  - WHEN `(for bad in '{command: "true", path: ["src/"]}' '{command: "true", paths: "src/"}'; do … done)`, verbatim.
  - THEN it prints exactly `exit=2 new_runs=0 named=1`, twice.

From `specs/sub-ticket-planning/spec.md`:
- A spec that needs one sub-ticket becomes that sub-ticket without a planner run (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B plan whole-spec T-0001 > $T/o 2>&1; echo "exit=$? …"; echo "state=…")`, verbatim.
  - THEN it prints exactly `exit=0 planner=skipped subs=T-0001.1.yaml T-0001.yaml `, then `state=ready-for-implementer "ready": ["T-0001.1"] names=2 logged=1`.
- A spec the writer split, or a parent a planner already ran on, still goes to the planner and nothing is written (NEW).
  - WHEN `(for c in 'NEEDS-SPLIT|' 'READY-FOR-CRITIC|### Size and seams' 'READY-FOR-CRITIC|planner-ran'; do … done)`, verbatim.
  - THEN it prints exactly `exit=0 planner=needed subs=T-0001.yaml logged=0`, three times.
- The whole-spec step refuses a parent that is not ready for its planner (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B ticket transition T-0001 --to planned --by t >/dev/null && $B plan whole-spec T-0001 >/dev/null 2>$T/err; echo "exit=$? named=$(grep -c 'not ready-for-planner' $T/err) subs=$(ls $T/store/tickets | tr '\n' ' ')")`
  - THEN it prints exactly `exit=2 named=1 subs=T-0001.yaml `.

From `specs/build-dispatch/spec.md` (node, with the T-0023 fixture):
- A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error (NEW).
  - WHEN the two `node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '<stub JSON>'` calls, verbatim.
  - THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, `park: harness-bug: plan whole-spec: T-0001 has no approved spec`, one per line.
- A spec that needs the planner still gets a planner run (REGRESSION).
  - WHEN the one `node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '<stub JSON>'` call with `"planner": "needed"`, verbatim.
  - THEN it prints exactly `start: planner`, then `park: harness-bug: subticket add: stub stop`.

From `specs/harness-docs/spec.md`:
- The changelog records the small-change lane as its last entry (NEW).
  - WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e 'paths' -e SKIPPED -e 'plan whole-spec' -e NEEDS-SPLIT -e seams | sort -u | grep -c .)`
  - THEN it prints `CONTIGUOUS`, then `5`.
- The design doc, build spec and README describe both skips, and no prompt copy changes (NEW).
  - WHEN `(echo "design=… gate=… build=… readme=… skipped=… stale=… prompts=…")`, verbatim.
  - THEN it prints exactly `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0`.
- The small-change lane adds no whitespace errors (REGRESSION).
  - WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  - THEN it prints only `exit=0`.

Intermediate checks. These are not parent scenarios; they guard what the spec says stays unchanged:
- The harness suite, including the two new files (REGRESSION).
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
  - THEN every test passes.
  - In particular, `tests/factory/test_run_isolation.py::test_implementer_gate_commands_come_wrapped` passes unedited, which shows A.4's text is byte-identical when no command has `paths`. `tests/factory/test_instance.py` passes unedited, which shows the template value stays `gate_commands: []`.
- This repository's own gate configuration is untouched (REGRESSION).
  - WHEN `(git diff --name-only main...HEAD -- .factory | grep -c .)`
  - THEN it prints `0`.

Tests to change: none (the parent's list is none). New tests go in the new files `tests/factory/test_gate_paths.py` (A.7) and `tests/factory/test_whole_spec_plan.py` (B.4).

Protected paths, all from the parent's Risk list, class harness:
- `factory/compose.py`
- `factory/cli.py`
- `factory/workflows/build.js`
- `factory/instance.template.yaml` (comments only)

The new test files under `tests/factory/` are also on the Risk list. Unprotected documents: `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md` and `README.md`.

Out of scope, as the parent lists it:
- Any repository's `gate_commands`, including `.factory/instance.yaml` and the Nanobot fork's.
- The implementer's gate list and the parent-close verifier's, which keep every command.
- Every prompt: the `docs/design.md` prompt blocks, `docs/prompts/**`, `factory/prompts/**` and `agents/**`.
- `factory merge`, `ticket join`, redispatch, and how the `ci` row's PASS or FAIL is read.
- `resolve --replan` and planner-ESCALATE rulings.
- Part C of the request, which has already shipped.
- Having the harness run gate commands itself.
- `bin/factory`, `pyproject.toml`, `uv.lock` and the Nanobot fork. `~/.nanobot/**` is never touched.

Coverage map: parent scenario → sub-ticket ID
- A gate command scoped to paths is skipped for a diff that touches none of them → ST-1
- A diff that touches a scoped command's paths runs that command → ST-1
- A gate command with no paths runs on every diff, as today → ST-1
- A skipped gate command is recorded on the gate result, and the merge still needs a passing gate → ST-1
- The implementer is still given every gate command → ST-1
- A malformed gate entry refuses a checker's run start and creates no run → ST-1
- A spec that needs one sub-ticket becomes that sub-ticket without a planner run → ST-1
- A spec the writer split, or a parent a planner already ran on, still goes to the planner and nothing is written → ST-1
- The whole-spec step refuses a parent that is not ready for its planner → ST-1
- A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error → ST-1
- A spec that needs the planner still gets a planner run → ST-1
- The changelog records the small-change lane as its last entry → ST-1
- The design doc, build spec and README describe both skips, and no prompt copy changes → ST-1
- The small-change lane adds no whitespace errors → ST-1
