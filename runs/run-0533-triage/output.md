Type: bug

Title: Workflow builds stop parking on the clerk's relays: the harness writes each role's model into a launch copy of the script, the scripts parse a reformatted reply, and `resolve` has a route back from a park after a finished implementer (#109, #112)

Summary:
The Workflow scripts (`factory/workflows/build.js`, `intake.js`) learn everything through the clerk. The clerk is a cheap model that runs one CLI command and relays its stdout. It has changed what it relays in two ways, and each one parks a sub-ticket and needs a human to resume it. In 5 of 8 builds on 2026-10-12 and 2026-10-13 it retyped the verifier's model in `factory config` from `opus` to `fable`. That is #109; `run start` (#107) refuses the wrong model, so the sub-ticket parks. On 2026-10-14 it pretty-printed `run finish`'s one-line JSON. That is #112: the script found no JSON and parked a sub-ticket whose implementer had already finished READY-FOR-REVIEW, and no `resolve` route covers that park.

The operator asks for four things:
- (A) A harness command writes a launch copy of the workflow script at each launch. The copy carries the instance's models, and the other values the script now reads from `factory config`, as a literal. It records the harness revision and the instance it was written for. The command runs `config`'s harness-acceptance check and refuses where `config` would. It writes outside the live store and needs no commit.
- (B) `clerk()` in both scripts tries `JSON.parse` on the whole trimmed stdout before its last-line scan.
- (C) A `resolve` route takes a sub-ticket parked from ready-for-implementer, whose last implementer run finished READY-FOR-REVIEW, to checks-in-flight. It reads the branch tip and leaves the round unchanged.
- (D) Tests for all three, a README how-to for launching the copy, and a changelog entry.

`run start`'s model refusal stays as the backstop. `factory drive` is not changed, and the clerk stays for every other relay.

Evidence:
- From the request: #109's body (clerk transcripts: the Bash result said `"verifier": "opus"` and the StructuredOutput said `"fable"`, every other byte the same), and #112's body and comment. T-0052.1 parked three times this way and was finished only by `factory drive`. #112's park was resumed by hand with `ticket head`, then `ticket transition --to checks-in-flight --round pr:init`, then a relaunch.
- Checked on this checkout (`~/dev/spec-factory`, `main`):
  - `factory/workflows/build.js:41-58` is `clerk()`. It splits the trimmed stdout into lines and calls `JSON.parse` on each line, last line first (lines 46-50). It returns `error: 'no JSON on stdout'` if no line parses. `intake.js:50-59` has the same function.
  - `build.js:225-226` sets the models from the clerk's relay: `const cfg = await clerk(\`${BIN} config\`…)`, then `MODELS = cfg.models; MAX_PR = cfg.max_rounds.pr; if (!STATE) STATE = cfg.state_dir`. `build.js:84` passes `--model ${MODELS[role]}` to `run start`. `intake.js:146` reads `config` the same way.
  - `factory/common.py:12-13`: `out()` prints `json.dumps(obj, ensure_ascii=False)`, with no indent. A multi-line reply therefore comes from the clerk, not the CLI.
  - `factory/human.py` `resolve`: `--redispatch` accepts only a park from `checks-in-flight` or `ready-for-merge`. `--ruling` covers a park from `ready-for-implementer` only when the reason starts `harness-bug: run start implementer:`. No route moves a sub-ticket parked after its implementer's `run finish` to checks-in-flight, which matches #112's claim.
  - `dev/issues.md:112` (#109) and `:115` (#112) are both "not in intake", and `:93` (#89, retire the clerk) is gated.
- Reference harness (`~/dev/nanobot-upstream`, read only): the request names no Nanobot-side fix. Recent commits on `feat/lionbot-v3.5`, plus a search of all branches for "clerk", "pretty", "#109" and "#112", show only harness-acceptance commits. No as-built fix exists there to check against.
- Duplicates: none. T-0054 is this request. The only other open tickets are T-0031.1 (parked; environment sync) and T-0049 (README diagram, #104). T-0040 (`factory drive`, closed) mentions the same pretty-print failure on 2026-10-09 (T-0027.2). It fixed that failure only for the driver, not for the Workflow scripts.

Capabilities: build-dispatch, human-resolution, harness-docs, harness-suite

Assumptions:
- (Inference) "The other values the script now reads from `factory config`" means at least `models`, `max_rounds.pr` and `state_dir` in `build.js` (line 226), plus whatever `intake.js` takes from line 146. Listing them exactly is the spec writer's job.
- (Inference) Requirement A covers both scripts, because both read `config` through the clerk. The request names both scripts in its first line, but requirement A does not say "both" explicitly.
- (Inference) The models stay `run start`'s to check. The launch copy only stops the script from asking for a model it learned from a clerk.
- (Correction to the request) Requirement D says "the suite has no such test yet". The suite does run `build.js` under node already: `tests/factory/_fixtures.py:67-74` (`BUILD_DRIVER`, used by `test_sibling_tests.py`) drives the script with real clerk commands and stand-in role runs. What the suite lacks is a test with a clerk that retypes models or pretty-prints a reply. The spec can build on that driver.
- (Suggestion only; priority is the operator's call) p1. The requester asks for this "next, ahead of #104 and #105", and `dev/issues.md` marks #109 and #112 p1.
- The design calls the requester leaves to the spec: the command's name and where it writes the copy (outside the live store, no commit), the `resolve` flag's name, and how the launch copy is told apart from a hand-edited script, which the request lists as a Risk for the auto-mode classifier. The request settles the product choices: a launch copy, not a digest; no `args`; no encoded relay.
- (Inference) This changes protected harness paths (`factory/**`, maybe `bin/factory`), so the spec's Risk section must declare them.

Question for human / Missing info / Reason: none. The intent is clear, the operator has made the product decisions, and every choice left open is delegated to the spec.

STATUS: ACCEPT
CONFIDENCE: high. Each code claim checked out at the cited lines (`build.js:41-58, 225-226`, `common.py:12-13`, `human.py` `resolve`), and the one inaccurate claim, about the suite having no node driver, does not change what is asked.
ESCALATIONS: none
