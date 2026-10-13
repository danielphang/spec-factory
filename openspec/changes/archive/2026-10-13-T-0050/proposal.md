## Problem
A role can run on a model the operator never chose, and the factory's records show that model as if it had been chosen. This affects every run started by the Workflow scripts. In this repository it has already happened to 10 of 92 verifier runs.

Some background. Each agent role in the factory (triage, spec writer, critic, planner, implementer, code reviewer, verifier) runs on a model that the operator picks per role in the repository's instance file, `.factory/instance.yaml`. The factory can be run two ways. The first is the driver, `factory drive`, a Python process. The second is a pair of Workflow scripts, `factory/workflows/intake.js` and `build.js`, which run inside Claude Code's Workflow tool. That tool cannot run a shell command itself. So the scripts hand every store command to the clerk, a small Haiku agent that runs the command and reports what it printed. (The store is the factory's record of tickets and runs.)

The scripts learn each role's model by asking the clerk to run `factory config` and report its JSON. The clerk is a language model, and it sometimes retypes that JSON instead of copying it. On 2026-10-12 it reported the verifier's model as `fable` when the instance file says `opus`. Each role run then starts with `factory run start`, the command that opens the run's record, and the scripts pass it the relayed model as `--model`. `run start` uses any `--model` it is given in place of the instance's model, without a check. It records that model, and the script launches the role agent on it. Nothing ever compares the model with the instance file.

After this change the harness, not the clerk, decides each role's model. `run start` records the model the instance file names for the role. It refuses a `--model` that names a different one, with an error that names both. The Workflow scripts already pass `--model` and launch the agent on the same value. So a misrelayed model now stops the ticket at that role's run start, before any agent starts. The ticket is parked: stopped with a reason, for a human to look at. The driver already reads the model in Python and passes the instance's own value, so it is unaffected.

## Evidence
- The incident, from the request: in build `wf_5a1655a5-8f3` (2026-10-12) the clerk reported `"verifier": "fable"`. The next build, `wf_f3c2453f-a74`, got `"verifier": "opus"` back from the same unchanged file. `.factory/instance.yaml:42` reads `verifier: opus`.
- The store's event log, counted per role and model over `run.started` events (`cat log/*.jsonl | grep '"run.started"' | sed … | sort | uniq -c`, in `.factory/store`). The verifier is the only role ever recorded off its configured model: `10 verifier fable` and `82 verifier opus`. Every other role's count matches the instance file, for example `79 reviewer fable` and `76 implementer opus`. The ten are the runs the request lists. The triage output counted 93 verifier events, but the per-model count is 92. The ten fable runs match either way.
- `run start` lets `--model` win, reproduced on this checkout with a throwaway store whose instance names `triage: opus`:
  ```
  $ bin/factory run start --role triage --ticket T-0001 --model fable
  {"ok": true, "run_id": "run-0001-triage", "role": "triage", "model": "fable", ...}   exit=0
  meta.yaml: model: fable      log: {"event": "run.started", ..., "model": "fable"}
  ```
  The run was accepted and recorded on a model the instance does not name. The cause is `factory/cli.py:220`, `model = a.model or cfg["models"][a.role]`. The option, declared at `factory/cli.py:702`, has no check.
- The whole incident replayed through both Workflow scripts, on this checkout. The stand-in clerk runs each command for real and reports `factory config` with one role's model swapped, as the real clerk did. (This is the fixture `t0050-wf.mjs`, given under the scenarios.)
  - Intake, with the triage model swapped to `fable`: `agent triage T-0001 model=fable`, then `swap=triage=fable closed runs=triage=fable`. The triage agent was launched on fable, and its run was recorded as fable.
  - Build, with the verifier model swapped to `fable`: `agent verifier T-0001.1 model=fable` and `agent verifier T-0001 model=fable`, then `merged runs=reviewer=fable verifier=fable verifier=fable`. This is the incident's pattern: both the sub-ticket's verifier and the parent's final verifier ran on fable.
- Where the scripts take the model, read in the code. `build.js:219` and `intake.js:140` set `MODELS = cfg.models` from the clerk's report. `build.js:79` and `intake.js:88` pass `--model ${MODELS[role]}` to `run start`. `build.js:105` and `intake.js:109` launch the role agent with `model: MODELS[role]`, the same value. The model `run start` returns is not used.
- The driver needs no change. `factory/drive.py:657` reads `models` from config in Python. `drive.py:186` passes `--model self.models[role]` to `run start`. `drive.py:201` launches on `start.get("model") or self.models[role]`.
- A prototype of part A, run in a scratch clone of this checkout, gave these results.
  - The scenarios below print the outputs their THEN lines give.
  - The full suite went from all passing to `569 passed, 7 errors`. All 7 errors come from two module fixtures that start a reviewer run with `--model opus`, while the instance template names `reviewer: fable` (`factory/instance.template.yaml:51`). The error was `model opus refused for reviewer: the instance names fable`. Those fixtures are listed under Tests to change.
  - The triage output assumed that every existing `--model` caller passes the instance's own value. These two fixtures do not. The other three suite callers pass `--model opus` for triage, which matches the instance, and stay unchanged.
- Docs that describe the old behaviour: `dev/build-harness.spec.md:203` gives `run start` as "(`model: M`, default `config.yaml` `models[R]`…)" and lists its guards. `README.md:254` describes what `run start` refuses.
- No reference-harness fix exists to compare with. The request names no Nanobot commit.

## Root cause
`factory/cli.py` `run_start` (line 220) takes the caller's `--model` over the instance's `models[role]`, and nothing compares the two. The Workflow scripts get `models` through the clerk, which can retype it (`build.js:218-219`, `intake.js:139-140`). A retyped value therefore reaches both the run record and the agent launch unchecked.

## Out of scope
- No change to `factory/workflows/build.js` or `intake.js`. They keep passing `--model` and launching on the same value (see Decisions).
- No change to `factory/drive.py`.
- No correction to past run records or to `factory stats`. The ten fable verifier runs stay as recorded, and their verdicts stand.
- Other values the clerk relays, which carry the same risk: `max_rounds`, `state_dir`, and the clerk's own model (`MODELS.clerk`). The request does not ask for these.
- The model table itself (`models:` in either instance file or the template).
- Making `--model` required, or removing it.

## Open questions
none

## Decisions
- The instance file is the only source of a role's model. `run start` records `models[role]` from the instance, and `--model` serves only as a cross-check. This is a standing decision: a later caller, including whatever replaces the Workflow scripts, gets its model from `run start` and never chooses one.
- A `--model` that differs from the instance's model is refused with exit 2, before a run id is reserved, so nothing is written. The error reads exactly `model <given> refused for <role>: the instance names <instance model>`. It contains no backtick, `$` or double quote, because the build script passes a park reason through a shell command. Leaving out `--model` is still accepted.
- The requester's part B is cut: the scripts do not switch to launching on the model `run start` returns. That value also reaches the script through the clerk's report, so launching on it would trust a second relay. Today the scripts launch on the same value they sent as `--model`. With part A, `run start` accepts that value only when it is the instance's model. Rejected: launching on the returned model, which adds a relay. Rejected: comparing the returned model with the sent one, which guards a failure the evidence does not show (the clerk changing the command it runs).
- When the clerk misrelays a model, the Workflow run parks the ticket at that role's run start, with reason `harness-bug: run start <role>: <the refusal>`. The run does not go ahead on the instance's model. Rejected: having the scripts stop sending `--model`. `run start` would then pick the right model, but the agent would still be launched on the misrelayed one.
- The requester's part C (a test) is kept as a new suite test file for `run start`. The two Workflow routes are checked by acceptance scenarios that run the scripts under node, as the standing T-0023 decision does for workflow fixes.

## Risk
- Blast radius: every `factory run start` call, so every role run of either Workflow script and of the driver.
  - The driver always passes the instance's own model, so it is unaffected. The suite's driver parity tests passed on the prototype.
  - A Workflow run whose config report was retyped now parks at the first run start of the affected role, where today it runs that role on the wrong model. The operator restarts the ticket the way any run-start park is restarted today: `resolve --redispatch` for a checker, `resolve --ruling` for an implementer, `ticket transition` for an intake ticket. Then the operator re-launches the workflow.
- Residual, not covered: a clerk that changes the command it is given (for example, by dropping `--model`) would still let the agent launch on a misrelayed model while the record is correct. The evidence shows no such case.
- `factory/cli.py` must stay under 900 lines (a current-truth requirement of harness-code). It is 882 today, and the change adds about 3.
- Protected paths: `factory/cli.py`

## Operator steps
1. After merge and the runtime upgrade (`--accept-harness`), watch the next Workflow build. A park reading `harness-bug: run start <role>: model … refused for <role>` means the clerk misrelayed the config. Restart the ticket as described under Risk.

