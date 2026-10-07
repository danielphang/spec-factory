## Acceptance

Every scenario below was run on this checkout (`a69aaf4`) and on the scratch prototype, with a throwaway HOME and `TMPDIR` set to this run's scratch directory. The "fails today" text is the actual output on `a69aaf4`.

- A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows → NEW. It fails today with `park T-0001.1: budget kill: reviewer`, `reviewer: KILLED `, `verifier: VERIFIED `, `kept=0 "rows": {"ci": "PASS", "verifier": "VERIFIED", "reviewer": "KILLED"}`: one reviewer run, labelled a budget kill, with no last message kept. This is the incident.
- One empty reviewer run followed by a real one routes on the real one → NEW. It fails today with `park T-0001.1: budget kill: reviewer`, `reviewer: KILLED `: the `null` return is never retried.
- An implementer that returns nothing twice parks as EMPTY-OUTPUT → NEW. It fails today with `park T-0001.2: budget kill: implementer`, `implementer: KILLED `.
- An intake role's second empty output in a row parks as EMPTY-OUTPUT → NEW. It fails today with `start: triage`, `park: harness-bug: unknown STATUS EMPTY-OUTPUT from triage`: no retry, and the status is unknown to the intake script.
- A reviewer that writes its output runs once → REGRESSION. It prints `park T-0001.1: SPEC-DEFECT from verifier`, `reviewer: APPROVE ` both today and on the prototype.
- Every preamble copy carries the wait rule and the copies stay identical → NEW. It fails today with three lines `fg=0 end=0`, then `verbatim`.
- Implementer, reviewer and verifier run prompts carry the wait rule, and only the reviewer's carries the judge-the-diff rule → NEW. It fails today with `implementer fg=0 judge=0`, `reviewer fg=0 judge=0`, `verifier fg=0 judge=0`.
- Every reviewer copy carries the rule, keeps every existing line, and the verifier prompt is unchanged → NEW. It fails today with three lines `judge=0 narrow=0`; its last line already prints `copy=SAME fill=unchanged removed=0 verifier_changed=0`.
- The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do → NEW. It fails today with `reviewer gates=1 told=0`; the verifier and implementer lines already print as expected.
- The design doc states the EMPTY-OUTPUT rule, its rows and its park → NEW. It fails today with `rule=0 rows=0 parks=0 kill=0`.
- The build spec describes EMPTY-OUTPUT and no longer a KILLED condition → NEW. It fails today with `stale=3 empty=0 note=0`.
- README drops the budget park and describes the empty-output retry → NEW. It fails today with `budget=2 built=0 unstick=0`.
- The changelog records issue 41 without a numbering gap → NEW. It fails today with `CONTIGUOUS`, then `0`.
- The empty-output change adds no whitespace errors → REGRESSION.

## Critic rounds

round 1 · spec v1 · run-0297-critic · APPROVE

## Review of T-0032 spec v1 (empty role output)

Spot-checks performed on `a69aaf4` (this checkout), throwaway HOME, `TMPDIR` set to this run's scratch directory:

- Cited paths and lines: `factory/cli.py:329-330` (empty output → `KILLED`, "empty output") and `:634-636` (`budget kill: <roles>` park) are as described. `factory/workflows/build.js:109-111` (killed condition and override), `:137` (implementer budget-kill park), `:169` (`--killed` row); `factory/workflows/intake.js:106-109`; `factory/compose.py:175-179` (one "Where you work" paragraph with gate commands for all three roles). `docs/design.md:99, 106, 126, 132, 218, 611`, both preamble copies line 44 (identical), both reviewer copies line 4, `dev/build-harness.spec.md:205, 275, 300, 410`, `README.md:107, 149, 437, 477`: every line holds the text the spec says. `grep -rn "time_budget\|budget_usd" factory/*.py` prints nothing; `grep -c "RUNNING CODE" agents/*.md` prints 0 for each of six files. Store: the five named reviewer runs are `KILLED` with no `output.md`; `log/2026-10.jsonl:1059-1060` is run-0209's `run.killed` and `result.recorded`. `decisions.md:52` holds the T-0032 standing line. T-0030 is `ready-for-planner` and its spec names `factory/compose.py` and `agents/`, so the overlap note is right.
- Agent-call claims: the Workflow script reference says `agent()` returns `null` on a user skip or terminal API error and that calls throw once the turn's token ceiling is spent. Matches the Evidence.
- `resolve --redispatch` (`factory/cli.py:794-819`) checks only that the park came from `checks-in-flight` or `ready-for-merge`, not the reason text, so an `EMPTY-OUTPUT from reviewer` park re-dispatches as the spec says. `run start` leaves the ticket's status unchanged and only appends to `in_flight`, so a second same-role start after `run finish` is accepted.
- Acceptance commands run on this checkout. Build scenarios 1, 2, 3 and 5 and intake scenario 4 print exactly the "fails today" text in verification.md (`park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` / `kept=0 ...`; `park T-0001.2: budget kill: implementer`; `park: harness-bug: unknown STATUS EMPTY-OUTPUT from triage`; the regression scenario prints `SPEC-DEFECT from verifier`, `reviewer: APPROVE `). All seven document scenarios print the stated fails-today values (`fg=0 end=0` ×3 + `verbatim`; `rule=0 rows=0 parks=0 kill=0`; `stale=3 empty=0 note=0`; `budget=2 built=0 unstick=0`; `CONTIGUOUS` then `0`; `judge=0 narrow=0` ×3 then `copy=SAME fill=unchanged removed=0 verifier_changed=0`).
- Tests to change = none: every existing test that pins `KILLED` uses `--status-override KILLED` or `results record --killed` (`test_p0_cli.py:122`, `test_tripwire.py:115`, `test_results_commit.py:120-131`, `test_shepherd.py:693-696`). Suite on this checkout: `310 passed in 147.89s`.

No BLOCKING findings.

Findings:

[SHOULD-FIX] 6 proposal.md, Problem, first paragraph
Problem: "parked" is a factory state name used before its gloss, which arrives only in paragraph 3 ("Parking stops the ticket until a human acts").
Evidence: Read as the gate operator new to the system; "parked for a human" is nearly self-explaining, which is why this is not blocking.
Suggested fix: Write "can be parked (stopped until a human acts) because..." in the first sentence and drop the later gloss.

[SHOULD-FIX] 6 proposal.md, Evidence, first paragraph
Problem: "this repo's store" and "the workflow journals" are system terms with no gloss anywhere in the human-facing sections, and the journal path lies outside the repository without saying so.
Evidence: Problem glosses role, run, harness, code reviewer and verifier; nothing glosses the store (the directory of run records and ticket state the harness keeps) or the journals (the session's record of each agent call's return value).
Suggested fix: Add one clause each on first use, and say the journals are in the operator's session directory, not in the repo.

[SHOULD-FIX] 6 proposal.md, Operator steps
Problem: "upgrade the runtime" and "in each instance" are unglossed system terms in the one section the operator acts on.
Evidence: Risk uses them too, with no gloss; the briefing explains them but the spec does not.
Suggested fix: "upgrade the runtime (the checkout the factory runs from) and accept the new harness revision in each instance (each repo's `.factory/`)".

[SHOULD-FIX] 4 proposal.md, Risk; design.md C.3
Problem: Up to 4000 characters of a role's final message are embedded, as a shell word, in the clerk agent's prompt ("Run exactly this one shell command ... and nothing else"), so untrusted role text reaches another agent's instructions; Risk does not name this.
Evidence: `build.js:41-45` builds the clerk prompt from the command string; a role's last message is model output, which the preamble classes as data, not instructions. The spec does say a failure of this call is ignored and never changes the route, which bounds the damage to the kept message.
Suggested fix: Add one sentence under Risk naming that the last message passes through the clerk's prompt, that the clerk runs with `effort: 'low'` and a fixed schema, and that a mangled or refused call loses only the kept message.

[NIT] 5 design.md D.1, line 106 edit
Problem: After this change the design still says "A budget-killed run ... re-dispatches", though the harness no longer produces a budget kill; only a hand-recorded `KILLED` row can.
Evidence: Decisions keep the `budget kill` join reason for hand-recorded rows, so the sentence is not false, only easy to misread as a live route.
Suggested fix: Optional: "A run a human recorded as KILLED, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches".

Out-of-scope observations:
- `tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed` is misnamed today: it passes `--status-override KILLED`. After C.1 the name reads as the opposite of the behaviour. Not a test this change breaks; a rename belongs to a later cleanup.
- `dev/build-harness.spec.md:300` still says `run finish` sets `KILLED` when `wall_s > time_budget_s`; D.2 rewrites I.5, which covers it.

## Verifier results

c01e7c2cf8bdef4f73fd8443744906b9ea89db74 · T-0032.1 · VERIFIED · run-0306-verifier
