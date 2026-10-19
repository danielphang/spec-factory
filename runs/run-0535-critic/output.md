# Critic review: T-0054 spec v1 (round 1)

## What I checked

- Cited lines, all as the spec says, on `main` at 308d038: `build.js:47-52` (last-line scan), `build.js:84` (`--model ${MODELS[role]}` to `run start`), `build.js:110` (agent launched on `MODELS[role]`), `build.js:178` (`ticket head` before the checkers), `build.js:225-226` (config through the clerk); `intake.js:56-61` and `146-147` the same; `common.py:12-13` (`out()` prints one line); `human.py:223-224` and `255-265` (the `--ruling`, `--to` and `--redispatch` routes); `gates.py:12-33` (`ticket_head`) and `203-206` (the conflict verdict); `drive.py:469`; `README.md:252`; `docs/design.md` lines 44, 64 and 109; `factory/cli.py` at 891 lines; 12 `gitops.repo_root()` call sites.
- Acceptance command run as written (harness-docs scenario, no suite): printed `start=no unstick=no writes=no list=1 fence=no route=no readme=within`, `CONTIGUOUS`, `entries=0 terms=0`, `exit=0`, exactly the failure `verification.md` states.
- `bin/factory launch-script build` today: argparse's `invalid choice`, exit 2, as the launch-copy items' failures say.
- Tests for the old behaviour (rubric 1): no test pins `--to accepts only spec-gate`, `no JSON on stdout`, or the clerk's line scan (grep over `tests/factory`). `test_live_store_guard.py:62-63` checks a subset of the read-only commands that all stay read-only, so adding `launch-script` breaks nothing. "Tests to change: none" holds.
- Store resolution for the scenarios: `FACTORY_STATE` overrides the instance's own store (`instance.py:14`, `98-99`) and the lock applies only to the instance's own store (`instance.py:143`). So a launch copy whose `ENV` carries both `FACTORY_INSTANCE` and a throwaway `FACTORY_STATE` writes the throwaway store, and `launch-script` run with `FACTORY_STATE` set is not refused by the lock. The scenarios are safe for the live store.
- Decision 8's log query has the fields it needs: `run.started` carries `role` (`cli.py:241`), `run.finished` carries `status` (`cli.py:373`), `ticket.created` carries `status` (`cli.py:76`, `510`), transitions carry `to` (`store.py:162`). `resolve`'s `move` already writes `resolve-<n>.yaml` and a `human.resolved` event with `kind` (`human.py:198-206`), so Decision 9's records come for free.
- harness-code pins: the definition lists of `common.py`, `gates.py`, `human.py` and `setup.py` hold under the placement in design.md; `cli.py` loses `_apply_round` and gains one subparser, staying under 900.
- Approved changes not yet archived: none, so rubric 5 raises nothing.

Not checked: the Workflow tool loading a copy from the temporary directory (the spec's Risk owns this); the prototype's `594 passed`; the 400-line bound once tests are written.

## Findings

[BLOCKING] 6 proposal.md, Problem, first paragraph
Problem: The first paragraph describes how the scripts and the clerk work and never says what is wrong or for whom; that arrives in the second paragraph ("Two of its slips stop a build") and the fourth ("The operator ... pays for each slip").
Evidence: Read as the operator at the gate. Paragraph 1 ends "The script then parses the copied output as JSON and decides the next step." The rubric makes this blocking.
Suggested fix: Open with one or two sentences such as "The clerk, a small agent that copies store command output back to the workflow scripts, sometimes miscopies it. Each slip stops a build, and the operator restarts it by hand." Then keep the mechanism paragraph as it is.

[BLOCKING] 6 proposal.md, Operator steps, step 1
Problem: Its first sentence uses four terms of art no earlier human-facing section glosses: "the runtime upgrade", `--accept-harness`, `$RUNTIME` and "the auto-mode classifier".
Evidence: grep of the spec text: `--accept-harness` appears only here; `$RUNTIME` only here; "auto-mode classifier" here and in Risk, neither glossed; "runtime" is explained only in the harness briefing, which the operator at the gate has not read.
Suggested fix: Gloss each once in the step, for example: "the runtime checkout (`$RUNTIME`), the copy of the harness the factory runs from; `--accept-harness`, the operator's command that lets the instance run on a new harness revision; the auto-mode classifier, Claude Code's check on what an unattended session may run".

[SHOULD-FIX] 6 proposal.md, Problem last paragraph and Decisions 1 and 2
Problem: "Launch copy", the change's central term, is never introduced: Decision 1 says what the command writes without naming it and Decision 2 uses it as known; Decision 1 also says "a protected path" without a gloss.
Evidence: Problem's last paragraph says "Each role's model reaches the script without any model relaying it" and never says a copy of the script is written. The rubric reads an unglossed term in the first paragraph of Decisions as blocking; I hold this to SHOULD-FIX because a careful reader works both out from Decision 1's own words, and the fix lands in the same revision as the two blocking items.
Suggested fix: In Problem's last paragraph: "a launch copy: the script with the instance's models, round limits and store written into one line, so no model relays them"; in Decision 1: "a protected path (one the instance declares no ticket may write without the operator's acceptance)".

[SHOULD-FIX] 4 design.md, Part F README, and Decision 13
Problem: README has 2 lines of slack and Part F adds at least three sentences, so the implementer must either cut other content or exceed the budget, and the spec says which only by "stay within 1,110 lines".
Evidence: `wc -l README.md` on 308d038 prints 1108; the budget is 1,110 (T-0048 standing decision: "A later change that needs more room raises it in its own spec"). Part F adds to "Starting a run" the launch-script command, one sentence on what a launch copy is and why, "not yet run on a real ticket", and "instance in args becomes optional"; the Unstick row grows in place. The prototype did not cover the docs, so nothing shows the text fits.
Suggested fix: Either name the cut in Part F (for example, the new text replaces `README.md:706-708`, "It then calls the Workflow tool ... with the build script", and the two-line comment in the `paths` block, netting at most two lines) or raise the budget in Decision 13 with the new number and the reason.

[NIT] 3 design.md, Part F README, Unstick row
Problem: README's rule (line 1066) says every entry above "Where this can go" says whether it has yet run on a real ticket; Part F says so for the launch copy but not for `--to checks`.
Evidence: `README.md:1065-1067`: "its entry says whether it has yet run on a real ticket".
Suggested fix: Add to the Unstick addition that `--to checks` has not yet fired on a real ticket.

[NIT] 1 proposal.md, Risk, harness-code paragraph
Problem: harness-code's current truth also carries "Splitting the command-line code changes no definition", whose scenario (`t0047-moved.py`) compares `merge-base HEAD main` with HEAD and expects `added=0 removed=0`; on this ticket's branch it will count this change's edits, as it has for every `factory/` change since T-0047 (T-0052 added `_copy_mismatch` to `setup.py`).
Evidence: The scenario text in the harness-code current truth and the pinned `setup.py` list, which already names `_copy_mismatch`.
Suggested fix: One sentence in Risk saying that scenario measures T-0047's own split and will report this change's definitions, so a verifier running current truth does not read it as a regression.

## Prior findings

none (round 1)

STATUS: REVISE
CONFIDENCE: high; every cited line and the one acceptance command checked out, and the two blocking items are writing-standard faults in sections the gate operator reads, each fixable in a sentence.
ESCALATIONS: none
