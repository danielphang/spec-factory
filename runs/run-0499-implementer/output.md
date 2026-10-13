Sub-ticket: T-0050.1 (parent T-0050, approved spec v1, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0050/v1.md`)
Branch: `factory/T-0050.1`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0050.1`
Commit: b3b978dce1d5544c7f346695292b8ef37f64eaae (base 2fbc170453cc3c549c487a6dd2c326b2b636e626)

## What changed

Before this change, a role could start, and be recorded, on a model the instance file never named. The model now comes only from the instance file, and `run start` refuses a different one. `run start` is the store command that opens a role run's record. The Workflow scripts already passed it a `--model` value that reached them through the clerk, the Haiku agent that runs store commands for them and can retype what it reports. `run start` used that value unchecked. Now it records the instance's `models[role]`. It refuses a `--model` naming another model with exit 2, and writes nothing. When the clerk misreports a model, the Workflow script parks the ticket at that role's run start, before any agent of that role is launched. A parked ticket is one stopped for a human.

A. `factory/cli.py` `run_start`
1. Directly after the unknown-role check, before the ticket is loaded, it reads `model = cfg["models"][a.role]`. When `a.model is not None and a.model != model`, it raises `Refused(f"model {a.model} refused for {a.role}: the instance names {model}")`. The existing `except Refused` handler (cli.py:871-874) prints that to stderr and exits 2. The check comes before `store.next_run_id`, so no run directory, `in_flight` entry or `run.started` event is written.
2. The line `model = a.model or cfg["models"][a.role]` is removed. `meta.yaml`, the `run.started` event and the printed JSON still carry `model`, now always the instance's.
3. `--model` has the help text "must match the instance's model for the role". `factory/cli.py` grows from 882 to 884 lines, so it stays under the 900-line limit.

I grepped the callers of `run start` (coding standard rule 2):
- `factory/drive.py:186` passes `self.models[role]`. That value comes from the driver's own Python `call("config")` (drive.py:657), so it is always the instance's value.
- `factory/workflows/intake.js:88` and `factory/workflows/build.js:79` pass `MODELS[role]`, the value the clerk relays. They park on a failed start (intake.js:89, build.js:84) with `harness-bug: run start <role>: <stderr>`. The new refusal therefore reaches the park reason unchanged. Neither script was changed, as the spec requires.
- `factory/human.py:223` already treats a `harness-bug: run start implementer:` park as resolvable by `resolve --ruling`.
- Test callers: the two listed fixtures, plus `test_p0_cli.py:72`, `test_instance.py:236` and `test_writing_standard.py:41`. Those three pass `--model opus` for triage, which the fixture instance also names, so they still pass.

The fix sits in `run_start` because every caller reaches that one function.

B. Tests
1. New file `tests/factory/test_run_start_model.py`, with 7 tests. Each uses a throwaway store and `FACTORY_INSTANCE` pointing at a copy of `factory/instance.template.yaml` whose triage model is `sonnet`, a model no other role uses. The tests cover:
   - a differing `--model`: exit 2 with the exact error, and no run directory, `run.started` event or `in_flight` entry;
   - the instance's own model: accepted and recorded;
   - no `--model`: the instance's model is recorded in `meta.yaml`, in the event and in the printed JSON;
   - reviewer, verifier and critic, each checked against its own entry, by refusal;
   - critic accepted on its own model (`fable`).
2. The two fixture edits from Tests to change: `"--model", "opus"` was dropped from the `run start` call in each fixture, and nothing else changed.

C. Docs
1. `dev/build-harness.spec.md`, the `run start` entry (line 203). The model text now reads "(`model:` the instance's `models[R]`, which `--model M` only cross-checks; …)". The first item of **Guards** is now the refusal, with its error `model <M> refused for <R>: the instance names <model>`.
2. `README.md`, the role-call paragraph under "The intake workflow, step by step". It now says that `run start` takes the role's model from `instance.yaml` and records it, and refuses a `--model` that names another model, so a model the clerk misreported parks the ticket before the agent starts. The status-header date was already 2026-10-12, today, so there was nothing to bump.
3. `docs/design.md` is unchanged, as the spec says. So there is no changelog entry and no `docs/prompts/` copy.

## Acceptance results

All commands ran from the worktree through the fresh-HOME wrapper, with `TMPDIR` set to this run's scratch directory. The GIVEN fixture blocks were run once beforehand: t0023 from human-resolution, t0032 from build-dispatch, and t0050 from this change. "Before" ran on the base 2fbc170. "After" ran on b3b978d.

- A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model (NEW).
  - Before: `refused: exit=0  runs=1 started=1` / `default: exit=2 returned= recorded=opus logged=opus`. This matches the "today" output in verification.md: the wrong model was accepted and a run was reserved.
  - After: `refused: exit=2 model opus refused for triage: the instance names sonnet runs=0 started=0` / `default: exit=0 returned=sonnet recorded=sonnet logged=sonnet`. This is exactly the THEN.
- A run start given the instance's own model is accepted and records it (REGRESSION). After: `exit=0 returned=sonnet recorded=sonnet`. This is exactly the THEN. It printed the same on the base.
- An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it (NEW).
  - Before: `agent triage T-0001 model=opus` / `swap=none closed runs=triage=opus` / `agent triage T-0001 model=fable` / `swap=triage=fable closed runs=triage=fable`. Triage was launched on fable, recorded as fable, and the ticket closed.
  - After: `agent triage T-0001 model=opus` / `swap=none closed runs=triage=opus` / `park T-0001: harness-bug: run start triage: model fable refused for triage: the instance names opus` / `swap=triage=fable parked runs=`. This is exactly the THEN: no triage agent was launched and no run was recorded.
- A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model (NEW).
  - Before: `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001 model=fable` / `agent verifier T-0001.1 model=fable` / `park T-0001: archive: no spec store (factory init not run)` / `merged runs=reviewer=fable verifier=fable verifier=fable`. Both verifiers ran on fable. That is the incident, and it matches verification.md.
  - After: `agent reviewer T-0001.1 model=fable` / `park T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus` / `parked runs=reviewer=fable`. This is exactly the THEN.
- The harness suite passes with only the two fixtures that passed a wrong model changed (REGRESSION). After: `583 passed in 388.87s (0:06:28)`, then `tests/factory/test_coding_standard.py` and `tests/factory/test_turn_economy.py`. The THEN holds: no failures or errors, and only the two listed files are modified under `tests/`. The new file is an addition, so `--diff-filter=DMR` does not list it.
- The build spec and the README describe the model check (NEW). Before: `old=1 guard=0 readme=0`. After: `old=0 guard=1 readme=1`, which matches the THEN with n=1.

These current-truth build-dispatch scenarios were re-run after the change, as verification.md asks. The GIVEN block of "The driver takes the intake fixtures through the same routes as the intake script" was run first. All three printed exactly their THEN:
- "The driver takes the build fixtures through the same routes as the build script": `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`. The driver and the build script still take the same routes.
- "Each role runs as one claude process with its prompt, model and tool limits": `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`. Every role process was still launched with the run's model.
- "The Workflow scripts still take both fixtures to the end of their routes": `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`.

Gate commands were run from the worktree exactly as written:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `583 passed in 378.91s (0:06:18)` and exited 0.

New tests before the fix: `4 failed, 3 passed`. The failures were the differing-model refusal and the three per-role refusals. Before the fix, those three were refused only by the ready-state guard, with the wrong error. The 3 that passed check behaviour the base already had: no `--model` records the default, and a matching model is accepted. After the fix, all 7 pass inside the suite run above. `ruff check factory/cli.py tests/factory/test_run_start_model.py` printed `All checks passed!`.

## Tests added/changed
- Added `tests/factory/test_run_start_model.py` (part B.1).
- Changed `tests/factory/test_coding_standard.py`, fixture `system_prompts`. It is listed under Tests to change. Its reviewer start passed `--model opus` against the template's `reviewer: fable`, so the start would now be refused and both parametrised tests would error.
- Changed `tests/factory/test_turn_economy.py`, fixture `run_prompts`. It is listed under Tests to change, for the same reason: the reviewer start would be refused.

## Known gaps and uncertainties
- The refusal is checked before the ticket is loaded, so a run start that is wrong in two ways reports the model error first. For example, a wrong `--model` on a ticket in the wrong state reports the model refusal, not the state refusal. The spec orders it this way (design A.1).
- `cfg["models"][a.role]` is now read on every start. Before, when `--model` was given, it was not read. An instance with no `models` entry for a role would now fail that role's start with an unhandled KeyError, reported through the generic exception handler, even when `--model` is given. Without `--model`, the base already failed this way. The template and both instance files name every role. The spec's design A.2 asks for exactly this line.
- The residual risk the spec names under Risk is not covered, by design. A clerk that drops `--model` from the command would let the agent launch on a misrelayed model while the record shows the right one.
- factory: markers added: none.

## Out-of-scope observations
- Three other passages in `dev/build-harness.spec.md` still describe the old relay:
  - line 125 (decision D6): "`run start --model` records it in `meta.yaml`";
  - line 276 (`runRole`): "exit 2 from a guard → park `harness-bug: <stderr>`", where the scripts' actual reason is `harness-bug: run start <role>: <stderr>`;
  - line 534 (a round-4 response).

  Line 125 is still true for an accepted start, and the spec scoped the doc edit to line 203. None is contradicted outright, so I left all three unchanged.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW scenario printed its "today" text on the base and exactly its THEN after the change, and the suite, both gates and the three driver and script parity scenarios pass.
ESCALATIONS: none
