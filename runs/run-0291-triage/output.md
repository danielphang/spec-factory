Type: bug

Title: A role that ends its turn while its own background commands are still running returns no output, and the harness records it as a budget kill and parks the ticket

Summary:
Twice on 2026-10-04, a code reviewer (the agent that judges a change's diff) started long commands in the background and then ended its turn to wait for them. In a workflow, an agent's last message is its output, so each run returned nothing. The harness (the code that dispatches the agents and routes their results) calls any empty output a "budget kill", meaning a run stopped for going over its time or token budget, and parks the ticket until a human acts. Both times, the verifier (the agent that runs the checks on the same commit) had passed. The operator chose option 1, the full proposal, and made it standing policy:
- A. The shared preamble tells every role to run commands in the foreground and wait for them, and never to end its turn while a command it started is still running, because its final message is its output.
- B. The code reviewer judges the diff and does not run the test suite or the gate (the set of checks a change must pass), because the verifier runs them. The reviewer may still run a narrow command to confirm a specific finding.
- C. An empty output is recorded as `EMPTY-OUTPUT` together with the agent's last message, never as a budget kill. The harness re-dispatches the same role once on its own. A second empty output parks the ticket, as an empty output does today.

Evidence:
- Request, first case: T-0023.3, reviewer run-0209 (2026-10-04, 15:25 to 15:30Z). Its last message was "Both suite runs are still in progress; I'll write the review once the monitor reports their final lines." The verifier on the same head took 780 s and returned VERIFIED.
- Request, second case: T-0029.1, reviewer run-0288 (2026-10-04, 23:09 to 23:11Z, 122 s). Its last message was "Nothing else is outstanding; waiting on the gate result before writing the review." The verifier on the same head (run-0287) returned VERIFIED with 310 tests passing. The reviewer was re-dispatched by hand.
- Store records, checked in the previous triage run: neither `runs/run-0209-reviewer/` nor `runs/run-0288-reviewer/` holds an `output.md`. Both `meta.yaml` files say `status: KILLED`. `tickets/T-0023.3.yaml` and `tickets/T-0029.1.yaml` both record the park reason `'budget kill: reviewer'`. The quoted last messages are the requester's, because I did not read the agent transcripts.
- Where the mislabel comes from, re-read in this run: `factory/workflows/build.js:109` sets `const killed = out === null || (typeof out === 'string' && out.trim() === '')`, and lines 110-111 then finish the run with `--status-override KILLED`. `factory/cli.py:634-636` parks any ticket that has a KILLED reviewer or verifier row as `budget kill: <role>`.
- The same mislabel was found before: `.factory/answers/retro-trial-2026-10-04/retro_as_designed.md:23` (item C3 of the retro trial, a trial review of the pipeline) says "the harness labels any empty output a budget kill and keeps no error text".
- What the design says now: `docs/design.md:99` lists a budget kill among the reasons a ticket parks. `docs/design.md:106` says a human re-dispatches a budget-killed run or closes the ticket.
- The operator's answer: `.factory/answers/T-0032-answer.md` chose option 1 and made both parts standing. It cites the operator's approval of the efficiency ledger with #41 included ("approve everything", `.factory/answers/operator-decisions-2026-10-04.md`). That file's lines 8 and 18 schedule #41 among the current small fixes.
- Duplicate search found no duplicate. In `dev/issues.md`, line 25 (#18) is the reverse mislabel, a killed checker labelled a harness bug, and line 48 is this request (#41). Of the open tickets T-0026 to T-0031, none covers empty outputs, background commands or what the reviewer runs.
- No Nanobot-side fix exists to copy. The request names no commit, and the previous run found no `EMPTY-OUTPUT` text under `~/dev/nanobot-upstream/.factory/`.

Assumptions:
- Inference: the harness cannot tell "stopped for budget" from any other empty return today. It enforces no budget of its own, and the agent call returns only text. The answer covers this case: if the workflow's agent call cannot say why a run stopped, `EMPTY-OUTPUT` labels every empty output. The spec writer should find out what the agent call reports before deciding which case applies.
- Inference: the one automatic re-dispatch changes `docs/design.md:99` and `:106` (and the routing table, if it names budget kills). The design-doc conventions then apply: a `docs/changelog.md` entry, matching text in `dev/build-harness.spec.md`, and fresh copies of any changed prompt block under `docs/prompts/`. The README's current-state page changes too, if it describes park reasons or the `KILLED` status.
- Inference: part B changes what reviewers do today. In the previous run's count, 36 of the 37 reviewer outputs in this store mention `pytest` or `tests/factory`. Per the answer, this falls under the standing decision that removing clearly redundant work is pre-approved, provided every refusal the pipeline gives today still fires. The spec should therefore show that the verifier still runs both gates on every head and that the reviewer keeps every diff check.
- Inference: the answer says "never as a budget kill". If the spec keeps any real budget-kill path, it has to name the signal that tells it apart. Otherwise the `budget kill` park reason stops being produced.
- Adjacent work, not a duplicate: T-0030 (#24 A+C, ready for the planner) changes per-role agent definitions and what goes into each role's input, the reviewer's included. The two tickets may both edit `factory/prompts/reviewer.md` and the matching `docs/design.md` block. The planner should order them or note the overlap.
- Suggested priority (a suggestion; the operator sets priority): high. Each occurrence parks a commit that has already passed verification, and the operator has scheduled #41 among the current small fixes.

Reason: The intent is clear, and the scope question asked in the previous run is answered (option 1, standing for both parts). No further product decision is needed.

STATUS: ACCEPT
CONFIDENCE: high. The mislabel is confirmed in `build.js:109-111` and `cli.py:634-636`, and the operator's recorded answer settles the scope.
ESCALATIONS: none
