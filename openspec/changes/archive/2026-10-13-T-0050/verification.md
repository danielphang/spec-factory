## Acceptance
- A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model → NEW. Today it prints `refused: exit=0  runs=1 started=1`, because the wrong model is accepted and a run is reserved. It then prints `default: exit=2 returned= recorded=opus logged=opus`: the second start is refused because the first is in flight, and the run is recorded on opus, not on the instance's sonnet.
- A run start given the instance's own model is accepted and records it → REGRESSION
- An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it → NEW. The first two lines already pass today. The swapped half prints `agent triage T-0001 model=fable`, then `swap=triage=fable closed runs=triage=fable`: triage is launched on fable, recorded as fable, and the ticket closes.
- A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model → NEW. Today it prints `agent reviewer T-0001.1 model=fable`, `agent verifier T-0001 model=fable`, `agent verifier T-0001.1 model=fable`, `park T-0001: archive: no spec store (factory init not run)`, `merged runs=reviewer=fable verifier=fable verifier=fable`. Both the sub-ticket's verifier and the parent's final verifier run on fable and are recorded as fable, which is the incident.
- The harness suite passes with only the two fixtures that passed a wrong model changed → REGRESSION. Without the two fixture edits, the change makes 7 tests error, all with `model opus refused for reviewer: the instance names fable`. With part A applied in a scratch clone, the suite reported `569 passed, 7 errors`.
- The build spec and the README describe the model check → NEW. Today it prints `old=1 guard=0 readme=0`.

Also re-run these current-truth scenarios from build-dispatch. They cover the driver, which passes `--model` with the instance's value, and the scripts' unchanged routes. All must still pass:
- "The driver takes the build fixtures through the same routes as the build script"
- "Each role runs as one claude process with its prompt, model and tool limits"
- "The Workflow scripts still take both fixtures to the end of their routes"

## Critic rounds

round 1 · spec v1 · run-0498-critic · APPROVE

Spec critic, round 1 (v1). No blocking findings.

What I checked
- Cited code: `factory/cli.py:220` is `model = a.model or cfg["models"][a.role]`; `--model` is declared at `factory/cli.py:702` with no check; the unknown-role check sits at the top of `run_start` (cli.py:200-201), so part A.1's placement is real. `factory/cli.py` is 882 lines. `Refused` prints the bare message on stderr and exits 2 (cli.py:871-874), so the park reason `harness-bug: run start <role>: model … refused …` that the scenarios expect is what intake.js:89 / build.js builds from `start.stderr`.
- Cited scripts and driver: `build.js:79,105,218-219` and `intake.js:88,109,139-140` pass and launch on `MODELS[role]` from the clerk's `factory config` report; `drive.py:186,201,657` read `models` in Python. All as the spec says.
- Instance files: `.factory/instance.yaml:42` reads `verifier: opus`; `factory/instance.template.yaml:46,51,52` read `triage: opus`, `reviewer: fable`, `verifier: opus`.
- Store counts: `cat .factory/store/log/*.jsonl | grep '"run.started"' | sed … | sort | uniq -c` gives `76 implementer opus`, `79 reviewer fable`, `10 verifier fable`, `82 verifier opus`, matching Evidence.
- Rubric 1, tests pinning the old behaviour: every `--model` caller in `tests/factory/` is `test_coding_standard.py:50` and `test_turn_economy.py:105` (reviewer with `opus`, refused under the new rule; both listed under Tests to change) and `test_instance.py:236`, `test_p0_cli.py:72`, `test_writing_standard.py:41` (triage with `opus`, which the template names). `test_drive_build.py:100` compares the driver's `--model` argv to the run's recorded model, which stays equal. No other test asserts a recorded model that differs from the instance.
- Acceptance commands run as given (no suite): the harness-docs scenario prints `old=1 guard=0 readme=0` today, and the README range `/^### The intake workflow, step by step/,/sequenceDiagram/` spans lines 252-260. The first build-dispatch scenario prints today `refused: exit=0  runs=1 started=1` then `default: exit=2 returned= recorded=opus logged=opus`, exactly the failure verification.md states, and the throwaway instance did take `triage: sonnet`.
- Fixtures the build scenario reuses: `t0023-parent.sh` is written by the human-resolution GIVEN (spec.md:13) and `t0032-checks.sh` by the build-dispatch GIVEN (input line 396). `resolve --redispatch` accepts a sub-ticket parked from `checks-in-flight` (human.py:264-265) and `ticket transition` exists (cli.py:673), so the restart path under Risk is real.
- Rubric 5: no approved changes await archive; nothing conflicts.

Findings

[SHOULD-FIX] 6 proposal.md, Problem, first paragraph
Problem: "10 of 92 verifier runs" uses the role name before the second paragraph lists the roles, so a reader new to the system meets a term of art unglossed in the paragraph that must stand alone.
Evidence: Problem paragraph 1 vs paragraph 2 ("Each agent role in the factory (triage, …, verifier)"). The structure makes it readable without a translator, so I am not blocking on it.
Suggested fix: write "10 of the 92 runs of the verifier, the role that checks a finished change" or move the figure to the second paragraph.

[SHOULD-FIX] 6 proposal.md, Operator steps, step 1
Problem: "the runtime upgrade (`--accept-harness`)" is a term of art specific to this system that no human-facing section glosses.
Evidence: grep of the Problem, Evidence, Decisions and Risk sections for "runtime", "upgrade", "accept-harness": only this line. The operator who performs that step knows it, which is why this is not blocking.
Suggested fix: "After the merge is accepted into the running harness (`--accept-harness`, the step that moves the runtime checkout to the merged revision), watch the next Workflow build."

[NIT] 1 proposal.md, Evidence, second bullet
Problem: the counting command is given with its `sed` elided (`sed …`), so it cannot be re-run as written.
Evidence: I reproduced the four counts with `sed -n 's/.*"role": "\([a-z_]*\)".*"model": "\([a-z]*\)".*/\1 \2/p'`.
Suggested fix: give the sed expression.

Not checked
- The build scenario's exact line set and final state (`parked runs=reviewer=fable`) depend on the reviewer finishing after the verifier's refused start parks the sub-ticket, both dispatched together by build.js. That needs part A built; the writer reports it from the prototype and the intake and run-start scenarios I could reason about hold, so I take it as plausible rather than verified.
- The claim that only those 7 tests error without the fixture edits: consistent with my grep of `--model` callers, not confirmed by a suite run.

## Verifier results

b3b978dce1d5544c7f346695292b8ef37f64eaae · T-0050.1 · VERIFIED · run-0501-verifier
