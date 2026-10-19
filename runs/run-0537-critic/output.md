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

STATUS: APPROVE
CONFIDENCE: high; every change answers its finding, each newly cited README range and the acceptance command check out on main, and no test pins the definitions Part D moves.
ESCALATIONS: none
