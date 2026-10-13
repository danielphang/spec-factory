Type: bug

Title: `run start` takes each role's model from the instance and refuses a `--model` that differs, so a Workflow run cannot start on a model the instance never named

Summary:
A role can run on a model the operator never chose, and the store records it as if it were configured. The cause is in the two Workflow scripts (`build.js`, `intake.js`), which are one of the two ways to run the factory. They learn each role's model from `factory config` through the clerk. The clerk is a small haiku agent that runs store commands and relays their output. Being a model, it sometimes retypes that output instead of copying it. `run start` then accepts whatever `--model` it is given and records it. The requester needs the harness, not the clerk, to own the model. `run start` should use the role's model from the instance file and record that model. The role agent should be launched on the model `run start` returns. A `--model` that disagrees with the instance should be refused, and the error should name both models.

Evidence:
- Request: in build `wf_5a1655a5-8f3` (T-0047, 2026-10-12) the clerk relayed `"verifier": "fable"`, while the next build (`wf_f3c2453f-a74`) got `"verifier": "opus"` from the same file.
- Verified: `.factory/instance.yaml:42` reads `verifier: opus`. `git log -- .factory/instance.yaml` shows its last change is `a69aaf4`.
- Verified: the store's event log `.factory/store/log/2026-10.jsonl` has 93 verifier `run.started` events. Ten of them record `"model": "fable"`: run-0057, 0060, 0193, 0238, 0287, 0334, 0422, 0483, 0486 and 0487. That matches the request's list exactly. 82 record `opus`.
- Verified: `factory/cli.py:220` (`run_start`) sets `model = a.model or cfg["models"][a.role]`, so any `--model` wins over the instance. `factory/cli.py:702` declares `--model` with no check.
- Verified: `factory/workflows/build.js:219` and `intake.js:140` set `MODELS = cfg.models` from the clerk-relayed config. `build.js:79` and `intake.js:88` pass `--model ${MODELS[role]}` to `run start`. `build.js:105` and `intake.js:109` launch the role agent with `model: MODELS[role]`, not the model `run start` returned.
- Verified, with a correction to the request's line number: the driver (`factory drive`) reads `models` straight from config in Python (`factory/drive.py:657`), so no clerk is involved. It launches the role on the model `run start` returned at `factory/drive.py:201` (`start.get("model") or self.models[role]`). The request cites line 186, which is the `run start` call itself.
- #2 (T-0002, closed) told the clerk to relay raw output. The request says that does not stop a model from retyping it, and the evidence above shows the retyping still happens.
- No reference-harness fix exists. `~/dev/nanobot-upstream` has no `factory/cli.py` and no model-related harness commit, and the request names no Nanobot commit.

Capabilities: build-dispatch

Assumptions:
- (inference) No caller depends on `--model` overriding the instance. I checked every `--model` use in `tests/factory` and the driver, and each passes the instance's own value. So refusing a differing value breaks no current route. The spec writer should confirm this against the full suite.
- (inference) The ten past runs on fable stay as recorded. The request says "those verdicts stand" and asks for no correction to store records or to `factory stats`.
- (inference) Parts A–C of the request (refuse in `run start`, launch on the returned model, add a test) are the requester's suggested fix, not requirements. The requirement is that a role run cannot start on, or be recorded as, a model the instance does not name for that role.
- (inference) The request notes that other clerk-relayed config values carry the same risk. It does not ask for them to be fixed, so this ticket covers the model only.
- (suggestion, priority is a human call) The issue index marks #107 as p1. The requester asks for it next after T-0047 (#100) and before the docs round (#101, T-0048), because it affects every Workflow run until #89 retires the scripts.

Question for human / Missing info / Reason: none

STATUS: ACCEPT
CONFIDENCE: high. Every evidence item was checked against the code, the instance file and the store's event log, and the counts match the request exactly.
ESCALATIONS: none
