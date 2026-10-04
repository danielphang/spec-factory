Type: bug

Title: A role that ends its turn while its own background commands are still running returns no output, and the harness records it as a budget kill and parks the ticket

Summary:
Twice on 2026-10-04 a code reviewer (the agent that judges a change's diff) started long commands in the background and then ended its turn to wait for them. In a workflow, an agent's last message is its output, so each run returned nothing. The harness (the code that dispatches the agents and routes their results) treats any empty output as a "budget kill", meaning a run stopped for exceeding its time or token budget. It then parked the ticket, which stops it until a human acts. Both times the verifier (the agent that runs the checks on the same commit) had passed. The requester needs roles to stop returning empty output this way. When a run does return empty, the record should say what happened rather than "budget kill".

Evidence:
- Request, first case: T-0023.3, reviewer run-0209 (2026-10-04, 15:25 to 15:30Z). Its last message was "Both suite runs are still in progress; I'll write the review once the monitor reports their final lines." The verifier on the same head took 780 s and returned VERIFIED.
- Request, second case: T-0029.1, reviewer run-0288 (2026-10-04, 23:09 to 23:11Z, 122 s). Its last message was "Nothing else is outstanding; waiting on the gate result before writing the review." Re-dispatched by hand.
- The store records match the request. Both `runs/run-0209-reviewer/` and `runs/run-0288-reviewer/` hold `input.md`, `diff.patch`, `meta.yaml` and `system-prompt.txt`, but no `output.md`. Both `meta.yaml` files say `status: KILLED`, and the wall times are 288 s and 122 s. `tickets/T-0023.3.yaml:33` and `tickets/T-0029.1.yaml:30` both record the park reason `'budget kill: reviewer'`. `runs/run-0287-verifier/output.md` ends `STATUS: VERIFIED`, with "both gates exited 0 (310 passed)". I did not read the agent transcripts, so the quoted last messages are the requester's.
- Why "budget kill" appears: `factory/workflows/build.js:109` marks a run killed when the agent's returned text is null or blank (`const killed = out === null || ... out.trim() === ''`). Lines 110-111 then finish the run with `--status-override KILLED`. `factory/cli.py:634-636` parks any ticket with a KILLED reviewer or verifier row as `budget kill: <role>`. The harness holds no time or token budget of its own, so every empty output is reported as a budget kill.
- The same mislabel has been seen before. `.factory/answers/retro-trial-2026-10-04/retro_as_designed.md:23` (item C3 of that trial review): two reviewer runs returned empty because the model's credits ran out, "the harness labels any empty output a budget kill and keeps no error text."
- Nothing in the role prompts covers background commands. `grep -rn -E "EMPTY-OUTPUT|foreground|in the background" factory docs dev tests` printed nothing. `factory/prompts/preamble.md` has no rule about waiting for commands. `factory/prompts/reviewer.md` neither asks the reviewer to run the test suite nor tells it not to.
- No fix exists to copy. The request names no Nanobot-side commit. `~/dev/nanobot-upstream` has no `factory/` directory, and its `.factory/` contains no `EMPTY-OUTPUT` text.
- Duplicate search: none found. Issue #18 (`dev/issues.md:25`) went the other way: a killed checker was labelled a harness bug instead of a budget kill. T-0023 (merged) made park reasons non-blank and made a redispatch keep the other checker's passing results (its spec, `specs/T-0023/v2.md`, items H2 and H4). It did not change how an empty output is labelled. T-0032 is this request's own ticket.

Assumptions:
- Inference: "not stopped for budget" (proposed part C) cannot be detected today. The harness enforces no budget, and the agent call returns only text, so a real budget stop, a model-credit failure (trial item C3) and an early end of turn all look the same. The spec writer has to find out whether the workflow's agent call reports why a run stopped. If it does not, the new label must cover every empty output.
- Inference: reviewers normally run the test suite today. Of 42 reviewer runs in this store, 37 wrote an `output.md`, and 36 of those mention `pytest` or `tests/factory`. I counted mentions, not confirmed runs. Proposed part B would therefore make reviews less thorough than they are now, not only shorter.
- Inference: the design doc lists budget kill among the reasons a ticket parks (`docs/design.md:99`). It says a human decides whether to re-dispatch a budget-killed run (`docs/design.md:106`). An automatic re-dispatch would change both lines, plus `dev/build-harness.spec.md` and the `docs/prompts/` copy of any changed prompt.
- Suggested priority (a suggestion; the operator sets priority): high. Each occurrence parks a commit that has already passed verification, and the build cannot continue until the operator re-dispatches by hand.

Question for human:
The preamble rule (part A: run commands in the foreground and never end the turn with one still running) and a truthful label for an empty output need no decision. How far should the fix go beyond them?
1. Take everything proposed. The reviewer stops running the test suite, because the verifier runs it, and keeps only narrow commands that confirm a specific finding. An empty output is recorded as `EMPTY-OUTPUT` together with the agent's last message, and the harness re-dispatches the same role once on its own before it parks.
2. Label only. Record `EMPTY-OUTPUT` with the last message and still park for a human re-dispatch, as the design says today. The reviewer prompt is unchanged, so the reviewer may still run the suite, in the foreground.
3. Label plus one automatic re-dispatch, with the reviewer prompt unchanged as in option 2.
Is the answer a standing decision that later tickets must follow? Two parts would set lasting policy: whether a checker's empty output is retried automatically, and whether the code reviewer may run the full test suite.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. The mislabel and both parks are confirmed in `build.js:109`, `cli.py:636` and the two run records; only the scope of the fix needs a human decision.
ESCALATIONS: none
