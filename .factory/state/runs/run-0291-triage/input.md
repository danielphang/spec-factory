## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0291-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0291-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "A role can end its turn waiting on background commands and return no output (mislabelled budget kill)"
labels: "harness"
---
**Where:** the role preamble (`docs/design.md` §Shared preamble, `factory/prompts/preamble.md`); the reviewer prompt; the harness's handling of an empty role output (`build.js`, `results record --killed`).

**Problem:** a role can end its turn while still waiting on commands it started in the background, and so return with no output. In a workflow, an agent's final message is its output. When a role starts a long command in the background and then ends its turn "until the monitor reports", it returns empty. The harness then records a KILLED row labelled "budget kill", which is wrong.

**Evidence:** spec-factory T-0023.3, reviewer run-0209 (2026-10-04, 15:25–15:30Z). It started both suite runs in the background and ended with: "Both suite runs are still in progress; I'll write the review once the monitor reports their final lines." The transcript ends there (`end_turn`), no `output.md` was written, and the ticket parked "budget kill: reviewer". The verifier on the same head took 780 s and VERIFIED. The retro trial's escalation C3 had already found that the harness calls any empty output a budget kill.

**Proposed change:**
- A. Preamble: run every command in the foreground and wait for it. Never end your turn while a command you started is still running. Your final message is your output.
- B. Reviewer prompt: the reviewer judges the diff. It does not run the test suite; the verifier does. It may run a narrow command to confirm a specific finding.
- C. Harness: an empty output from a role that was not stopped for budget is recorded as `EMPTY-OUTPUT` with the agent's last message, not "budget kill". It re-dispatches the same role once before parking.



**Second occurrence:** spec-factory T-0029.1, reviewer run-0288 (2026-10-04, 23:09–23:11Z), 122 s. Its final message: "Nothing else is outstanding; waiting on the gate result before writing the review." No output.md; recorded KILLED "budget kill: reviewer"; the piece parked although the verifier on the same head (run-0287) returned VERIFIED with both gates passing (310 tests). Re-dispatched by hand.

GitHub: https://github.com/danielphang/spec-factory/issues/41


## Answer 1

# T-0032 (#41): answer to triage's scope question

Option 1: take everything proposed.

- A. Preamble: run every command in the foreground and wait for it; never end the turn while a command you started is still running; your final message is your output.
- B. The code reviewer judges the diff and does not run the test suite or the gate; the verifier does. It may run a narrow command to confirm a specific finding.
- C. An empty output is recorded as EMPTY-OUTPUT with the agent's last message, never as a budget kill. If the workflow's agent call cannot say why a run stopped, the label covers every empty output. The harness re-dispatches the same role once on its own; a second empty output parks as today.

Standing: yes, both parts.

Source: the operator approved the efficiency ledger, #41 included, as proposed ("approve everything", 2026-10-04, `.factory/answers/operator-decisions-2026-10-04.md`). B also falls under the standing decision in decisions.md that removing clearly redundant work is pre-approved provided every refusal the pipeline gives today still fires: the verifier still runs both gates on every head, and the reviewer keeps every diff check. C does not overturn the operator's "keep the stops" ruling: that ruling covers decisions a human must make, and an empty output carries no decision. A second empty output still stops for a human.

Answered by the Green session on the operator's delegation.

## Your previous Triage output (the question you asked is answered above)

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
