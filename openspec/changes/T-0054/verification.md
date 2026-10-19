## Acceptance

Each NEW item's failure below is what that WHEN printed on `main` at 308d038. Each PR-side THEN was checked on a scratch prototype of parts A to D, except the docs and suite items, which the prototype does not cover.

- A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks → NEW. Today `launch-script` is an invalid choice, so node gets no script: it prints `Error: ENOENT: no such file or directory, open 'no launch copy'` and `copy: checks-in-flight runs=`. The script half already prints its three lines; that half guards the backstop.
- An intake launched from its launch copy runs triage on the instance's model while the clerk retypes it → NEW. Today it prints the same `Error: ENOENT ...` line, then `ready-for-triage runs=`.
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance → NEW. Today it prints `intake: where=none changed=206 revision=0 instance=0 writable=no`, `build: where=none changed=310 revision=0 instance=0 writable=no` and `checkout=unchanged store=unchanged dirs=0`.
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy → NEW. Today it prints `old=gone other=kept fresh=gone new=none dirs=1`: `launch-script` is an invalid choice, so no copy is written. Added at the gate (operator, 2026-10-18); not run on the prototype.
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy → NEW. Today it prints `config=2 launch=2 same=no lock=0 copies=0`: the exit 2 is argparse's usage error, not the lock's refusal.
- A launch copy launched for another instance returns an error naming its own and runs nothing → NEW. Today it prints `refused=0 agents=0 checks-in-flight runs=0`, because no copy exists.
- A build and an intake whose every store reply is relayed pretty-printed reach the ends they reach with one-line replies → NEW. Today it prints `result: no JSON on stdout`, `build: T-0001.1 ready-for-implementer`, `result: no JSON on stdout`, `intake: T-0002 ready-for-triage`: each script stops at its first reply, `factory config`.
- A sub-ticket parked when its implementer's finish did not parse returns to its checks at the branch tip, and the build then merges it → NEW. Today it prints `resolve=2 parked head=other pr=0`, then `parked implementer_runs=1`. The refusal text is `--to accepts only spec-gate`.
- The route back to checks is refused after a BLOCKED run, after a revise, from the checks, on a tripwire park and on a ticket that is not parked → NEW. Today every line reads `exit=2 refused=0 ...`: the command is refused, but by `--to accepts only spec-gate`, not by this route's rule.
- Unmarked writes from inside the target are refused while a run is in flight, init included → REGRESSION. Restated unchanged from current truth; it prints its THEN today.
- The refusal names the throwaway store and not the marker → REGRESSION. Restated unchanged; it prints its THEN today.
- A harness acceptance is refused while a run is in flight → REGRESSION. Restated unchanged; it prints its THEN today.
- A launch copy is written unmarked while a run is in flight, and the target is unchanged → NEW. Today it prints `launch=2 new=2 copies=0 store=unchanged`.
- The README, the design doc and the changelog describe the launch copy and the route back to checks → NEW. Today it prints `start=no unstick=no writes=no list=1 fence=no route=no readme=within`, `CONTIGUOUS`, `entries=0 terms=0`, `exit=0`.
- The suite passes, no existing test changes, and every test file this change adds fails on the base → NEW. On `main` the base is `main` itself, so the second line is `changed=0 added=0` and no file line follows. I ran this command's base-tree mechanics on the prototype with one stand-in test file, which printed `<file> on the base: 1 failed`. The full suite on the prototype printed `594 passed`.

## Responses

- [BLOCKING] Problem, first paragraph → FIXED. Problem now opens with what is wrong and for whom: the clerk miscopies command output, each slip stops a build, and the operator restarts it by hand; four such stops are in this store. The mechanism follows in the second paragraph, which also glosses "store" and "harness" at first use.
- [BLOCKING] Operator steps, step 1 → FIXED. Step 1 now glosses the runtime checkout (`$RUNTIME`, with its path), `--accept-harness` (the flag that lets an instance run on a harness revision it has not used before, given to the first command, per `README.md:537-540`) and the auto-mode classifier. The classifier is glossed at its first use, in Risk. Step 2 names "instance A" as the Nanobot chat-bot repository.
- [SHOULD-FIX] "launch copy" and "protected path" unglossed → FIXED. Problem's last paragraph introduces a launch copy in bold and says what it is. Decision 1 names it as what the command writes and glosses a protected path. Decision 4 also glosses the live-store fence.
- [SHOULD-FIX] README budget → FIXED. I kept the budget (Decision 13, now with the rejected alternative) and named the cut. Part F now gives the line range each README edit replaces: `README.md:699-711` (13 lines) becomes at most 13 lines, with a 13-line draft; the read-only list at 831-832 is rewrapped with no added line; the **Unstick** row is one table line; the run-start paragraph at 249-254 may add the one line. README then ends at 1,109 lines or fewer. Part F also tells the implementer to stop and report if the text cannot fit. I checked `wc -l README.md` (`1108`) and each cited range on `main` at 308d038 this round.
- [NIT] Unstick row and "not yet run on a real ticket" → FIXED. Part F's **Unstick** addition now says `--to checks` has not yet run on a real ticket.
- [NIT] `t0047-moved.py` will count this change → FIXED. Risk now says that scenario measures T-0047's own split and will report this change's definitions on this branch, so a verifier should not read the count as a regression.

No acceptance item changed this round. The harness-docs scenario already checks the 1,110-line bound, and the requirement's wording now says "its 1,110-line budget".

## Critic rounds

round 1 · spec v1 · run-0535-critic · REVISE

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

round 2 · spec v2 · run-0537-critic · APPROVE

# Critic review: T-0054 spec v2 (round 2)

## What I checked

- Changed text only, per the convergence rule, plus the cited lines each change leans on, all on `main` at 308d038.
- README ranges Part F now names: `README.md:9` is the status line; `249-254` is the run-start paragraph, with the "model the clerk misreported" sentence at 251-252; `699-711` is 13 lines, the `paths` block and the paragraph that launches the scripts; `831-832` holds "A write is any command except ... `stats`;"; `859` is the one-line **Unstick** row. `wc -l README.md` prints `1108`. `README.md:537-540` describes `--accept-harness` as the Responses say; `README.md:1096` still documents `factory paths`.
- The 13-line draft in Part F is 13 lines (one sentence, blank, three-line fenced command, blank, seven-line paragraph), so Decision 13's "1,109 lines or fewer" holds if the implementer keeps to it.
- Acceptance command run as written on `main` (harness-docs scenario, no suite): printed `start=no unstick=no writes=no list=1 fence=no route=no readme=within`, `CONTIGUOUS`, `entries=0 terms=0`, `exit=0`, the failure `verification.md` states.
- Fixtures the scenarios reuse exist in current truth: `t0032-checks.sh` (build-dispatch) and `t0023-parent.sh` (human-resolution) are written by the GIVEN blocks the scenarios name.
- Rubric 1 for Part D's moves: no file under `tests/factory` imports `_apply_round` or `ticket_head` directly (grep), so moving them to `store.py` breaks no existing test. "Tests to change: none" still holds.
- `human.py:223-224` and `255-265`, `build.js:225-226`, and `MAX_PR` set at `build.js:226` and read nowhere, as Out of scope says.
- Approved changes not yet archived: none, so rubric 5 raises nothing.

Not checked, as in round 1: the Workflow tool loading a copy from the temporary directory (Risk owns it); the prototype's `594 passed`; the 400-line bound once tests are written.

## Findings

[NIT] 6 proposal.md, Operator steps, step 1
Problem: The gloss of "auto-mode classifier" sits in Risk, which is not one of the sections the gate operator reads, so step 1's "Claude Code's auto-mode classifier" reaches them unglossed.
Evidence: The spec's own Responses say the classifier is glossed "at its first use, in Risk"; the rubric lists Problem, Evidence, Open questions, Decisions and Operator steps as the operator's sections. Step 1's wording ("Claude Code's ... classifier lets it run") is clear enough that I do not block on it.
Suggested fix: Move the gloss into step 1: "Claude Code's auto-mode classifier, its check on what a session running without per-step approval may do".

## Prior findings

- [BLOCKING] Problem, first paragraph → RESOLVED. It now opens with what is wrong (the clerk miscopies command output and each slip stops a build) and for whom (the operator restarts it by hand), with the count of stops in this store. "Store" and "harness" are glossed in the second paragraph.
- [BLOCKING] Operator steps, step 1 → RESOLVED. The runtime checkout, `$RUNTIME` and `--accept-harness` are each glossed in the step; "instance A" became "the Nanobot chat-bot repository this runtime also serves".
- [SHOULD-FIX] "launch copy" and "protected path" unglossed → RESOLVED. Problem's last paragraph introduces the launch copy and says what it is; Decision 1 glosses a protected path; Decision 4 glosses the live-store fence.
- [SHOULD-FIX] README budget → RESOLVED. Part F names the lines each edit replaces and the net growth (at most one line); Decision 13 records the rejected alternative; the implementer is told to stop and report rather than cut or exceed. The ranges and the 13-line count check out.
- [NIT] Unstick row and "not yet run on a real ticket" → RESOLVED.
- [NIT] `t0047-moved.py` counts this change → RESOLVED, in Risk.
