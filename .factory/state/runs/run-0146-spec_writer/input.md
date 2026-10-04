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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0146-spec_writer/output.md`

## Ticket (Triage output)

Type: feature

Title: Record decisions made outside archive in `decisions.md`, and give `decisions.md` to the spec writer, critic and planner

Summary:
A decision the operator makes outside an archived spec is never written to the decision log, and the log never reaches the roles that should build on it. The decision log is `decisions.md`, one file per target repo, one dated line per decision tagged with its ticket. Today only `factory archive` writes it. Archive is the harness step that applies an approved spec to the repo's current-truth specs when the parent ticket closes. So an answer given at a NEEDS-HUMAN park lives only in that ticket's request text when the ticket then closes without an archive (a NEEDS-HUMAN park is a ticket stopped until a human answers a question). That happens on a triage REJECT, on `resolve --close`, or when a ticket is closed as applied. Separately, `run compose` (the harness command that builds each role's input) never includes `decisions.md`, so even archived decisions reach the spec writer, critic or planner only if one of them opens the file unprompted. The requester (the Nanobot v3.5 Driver, the session that runs the port on the Nanobot repo) wants three things. (A) A way to append a dated, ticket-tagged line to `decisions.md` at any ticket state, both as a command and from `resolve --close` / `resolve --answer`. (B) `decisions.md` in the spec writer's, critic's and planner's input. (C) A NEEDS-HUMAN question that asks the human whether the answer is a standing decision, so that the `resolve` call can record it.

Evidence:
- Request: "Only `archive` appends to `decisions.md`." Confirmed. `grep -rn decisions factory/` matches only `factory/specstore.py`: `init` creates an empty `decisions.md` (lines 67-70), and `archive` appends to it (lines 328-333). The module docstring (line 6) says "Only `archive` writes current truth and `decisions.md`."
- Request: "`grep -n decisions factory/compose.py` matches nothing." Confirmed: the grep exits 1 on this checkout. In `compose()`, the spec writer and critic get current truth through `add_truth()` (lines 81, 98), but the planner gets only the approved spec and any ruling (lines 106-112). So the planner does not receive current truth today.
- `resolve` in `factory/cli.py` (lines 675-736; parser at 1075-1082) has `--answer`, `--ruling`, `--to`, `--redispatch` and `--close`. `--answer` appends `## Answer N` to the request file. `--close` writes nothing beyond the ticket transition. Neither one touches `decisions.md`.
- The design states the current rule explicitly. `docs/design.md` line 82 says "Only the archive step writes current truth and `decisions.md`." Line 97 says that a parent closed as applied leaves "Current truth and `decisions.md` … not updated". `dev/build-harness.spec.md` lines 193 and 315 say the same.
- Nanobot v3.5 store (read only, to check the evidence), `~/dev/nanobot-upstream/.factory/state`:
  - `tickets/T-0003.yaml`: parked "NEEDS-HUMAN from triage", resolved by `answer: 1`, then moved `ready-for-triage` → `closed` by `workflow` (the triage REJECT the request describes).
  - `requests/T-0003.md` line 87, in Answer 1: "Close it as a recorded decision so that T-0011 (SPEC-06) and T-0013 (BUG-03) build on it."
  - `decisions.md` there is 0 bytes (`wc -c`), so the decision was not recorded centrally.
  - `requests/T-0011.md` line 93 and `requests/T-0013.md` line 169 each carry "Port decision that binds this ticket (added by the v3.5 driver, 2026-10-04)", which is the hand-added copy the request describes.
- Operator note appended to the request: the spec gate is pre-approved for this request. `.factory/answers/queue-preapproval-policy.md` lists "#32 (decisions log)" under "Pre-approved now".

Assumptions (my inferences, not the requester's words):
- The request explicitly asks to relax the design rule that only archive writes `decisions.md`. So the spec amends `docs/design.md` lines 82 and 97 and `dev/build-harness.spec.md` lines 193 and 315 to match, and adds a `docs/changelog.md` entry, following the briefing's convention for design-doc changes.
- Part C changes the NEEDS-HUMAN wording in the triage and spec-writer prompt blocks. That means editing `docs/design.md`, `factory/prompts/`, and re-copying `docs/prompts/` from the design doc. Both `factory/**` and `docs/prompts/**` are protected paths here, so the spec's Risk section has to declare them. The pre-approval policy also says "a standards or prompt change still gets the operator's acceptance test before the runtime moves", and part C is a prompt change.
- A decision line uses the same shape archive writes, `<YYYY-MM-DD> <ticket id> <line>`, so that both writers produce one log format.
- "After current truth" in part B means the spec writer and critic get `decisions.md` right after their current-truth specs. The planner gets no current truth today, so for the planner the position is the spec writer's call. `compose()` already skips files that do not exist (`add()`, line 61), so a store with no `decisions.md` gets no new input.
- The request names no ticket state to refuse, so "at any state" includes closed tickets. Closed tickets are where T-0003's decision ended up.

Open points for the spec writer (not requirements; the request does not settle them):
- This instance has no spec store, because `factory init` was never run here: `.factory/state/decisions.md` does not exist. The spec has to say what `decision add` and `--decision` do when `decisions.md` is absent: create the file, or refuse the way archive refuses with "no spec store". Acceptance commands must be runnable from `~/dev/spec-factory`, so this choice decides how they are written.
- Part C says "the clerk-facing `resolve` call carries `--decision`". In the current store, `resolve` is run by the human (T-0003's history shows `by: dphang`). The clerk is the small agent the workflow script uses to run one `bin/factory` command per record. The spec should name who turns "yes, this is a standing decision" into the `--decision` argument, and where the human's yes/no is read from.
- The request gives no Nanobot-side harness commit for this fix, so there is no as-built reference to verify against.

Suggested priority (a suggestion; priority is the operator's call): high. The operator note says the v3.5 Driver currently has to sweep dependent requests by hand after every NEEDS-HUMAN answer.

Duplicates checked: none. I read `.factory/state/requests/index.yaml` (T-0001 to T-0017; T-0017 is this request) and `dev/issues.md` (#32 is this request, "not in intake"). `grep -l decisions.md` over the store's requests, specs and tickets matches only T-0008, T-0010 and T-0012, which are archive-era spec-store work, plus this ticket. The nearest neighbour is #24 ("role-specific inputs" in `factory/cost.py`), which also changes what `compose` gives each role. It is a separate request about token cost, not about decisions.

Out-of-scope observations:
- Part B does not include triage. A triage run that re-asks a question already settled by a standing decision would still not see that decision. The request does not ask for this, so I left it out.
- #24 (role-specific inputs) and #27 (roles never see a request's attachments) also change `compose()`'s role inputs. If they are built close together, they will touch the same function.

Question for human / Missing info / Reason: n/a (ACCEPT)

STATUS: ACCEPT
CONFIDENCE: high. Every claim in the request was checked against this checkout's code and design text and against the Nanobot store. The remaining gaps are mechanism details the spec writer can settle.
ESCALATIONS: none

## Request (raw)

---
title: "Decisions outside archive are never recorded, and no role is given decisions.md"
labels: "harness"
---
**Where:** `factory/specstore.py` (only `archive` writes `decisions.md`); `factory/compose.py` (no role input includes `decisions.md`); `factory/cli.py` `resolve`.

**Problem:** decisions the operator makes outside an archived spec are lost to the tickets that depend on them, and recorded decisions never reach the roles anyway. Two gaps:
1. **Not written.** Only `archive` appends to `decisions.md`. A decision taken some other way is recorded nowhere central: a request that is purely a decision, answered at a NEEDS-HUMAN park and then closed (a triage REJECT, or `resolve --close`), or a ticket closed as applied. The answer lives only in that ticket's request text.
2. **Not read.** `compose.py` never puts `decisions.md` into any role's input. Even archived decisions reach the spec writer, critic or planner only if one of them happens to open the file.

**Evidence:** Nanobot v3.5 store, T-0003 (SPEC-18, where the lionbot code lives): a pure decision request. The operator answered its park and re-triage closed it REJECT, correctly, since nothing is built. The decision exists only as "Answer 1" in `requests/T-0003.md`. T-0011 and T-0013 build on it and carry no link to it. The Driver appended the decision to both requests by hand. `grep -n decisions factory/compose.py` matches nothing.

**Proposed change:**
- A. `factory decision add T-NNNN "<one line>"` appends a dated, ticket-tagged line to `decisions.md`, at any state. `resolve --close` and `resolve --answer` take an optional `--decision "<line>"` that does the same.
- B. `run compose` puts `decisions.md` into the inputs of the spec writer, critic and planner, after current truth.
- C. The NEEDS-HUMAN question format asks the human to say whether the answer is a standing decision. If it is, the clerk-facing `resolve` call carries `--decision`.

**Out of scope:** a new triage status; backfilling past answers (an operator step per store).

Reported by the Nanobot v3.5 Driver.


---

Operator: spec gate pre-approved (small blast radius; `.factory/answers/queue-preapproval-policy.md`). Priority raised by the Nanobot v3.5 Driver, whose every NEEDS-HUMAN answer currently needs a manual sweep of dependent requests.

## Critic findings on your previous version

## Findings

[BLOCKING] 6 Decisions, first bullet; Operator steps, step 1
Problem: The first bullet of Decisions and the first Operator step use names specific to this system that no earlier human-facing section has glossed: `decision add`, `--decision`, `factory init` and `resolve` (Decisions), and "the runtime" and "the pre-approval policy" (Operator steps); the Problem says what the change does but never names the command or the flag, so the operator reading Decisions has to infer that `decision add` is the new command and `--decision` the new flag on `resolve`.
Evidence: Read Problem, Evidence, Decisions and Operator steps in order as the gate operator. `resolve` first appears in Evidence ("Who runs `resolve`") with no statement of what it does; `factory init` appears nowhere before Decisions; `decision add` and `--decision` first appear in Out of scope and Decisions; "runtime" and "pre-approval policy" appear only in Operator steps. The writing standard (rule 2) asks for a gloss at first use.
Suggested fix: End the Problem's last paragraph with one sentence naming the pieces, for example "It adds a command, `factory decision add <ticket> "<line>"`, and a `--decision "<line>"` flag on `resolve`, the command a human runs to answer or close a ticket; `factory init`, which creates a store's spec tree, is not needed first", and open Operator step 1 with a clause saying what the runtime is (the pinned harness checkout that runs tickets) and that the pre-approval policy requires the operator to read every prompt change before it runs.

[SHOULD-FIX] 1 Evidence, "The real case" bullet; Risk, first paragraph
Problem: The Nanobot store's `decisions.md` is no longer 0 bytes, so the Risk claim "no run changes until someone logs a decision" is false for that target.
Evidence: `wc -c ~/dev/nanobot-upstream/.factory/state/decisions.md` printed `695` today; the file holds four `2026-10-04 T-0012 …` lines written by archive when T-0012 closed (commit `8d2f0e07c` in that repo). T-0003's decision is still absent, so the Problem and the T-0003 evidence stand. After the runtime moves, every Nanobot spec writer, critic and planner run gains those four lines at once.
Suggested fix: Date the `0` observation ("at the time of T-0003's close") and restate the blast radius: the Nanobot target's three roles receive four lines from the first run after the upgrade; this repo's runs change only once a decision is logged here.

[NIT] 6 Proposed change, D.4 (README)
Problem: The README's "Maintaining this page" table row for "Where a human decides" lists the parser arguments that section is derived from (`approve-spec`, `request-changes`, `resolve`, `--accept-harness`) and D.4 adds a Record row without adding `decision` to that derivation row.
Evidence: `README.md` line 446: "| Where a human decides | `factory/cli.py` `build_parser()`: the `approve-spec`, `request-changes`, `resolve`, `--accept-harness` arguments | …".
Suggested fix: Add "the `decision` subparser" to that row in D.4.

## Spot-checks

- Cited paths and lines are real: `factory/specstore.py` docstring line 6, `init()` lines 55-71 (decisions.md at 67-70), `archive()` lines 310-336 (append at 328-333); `factory/compose.py` `compose()` from line 52, `add_truth()` lines 68-70 called at 81 and 98, planner branch 106-112; `factory/cli.py` `resolve()` 675-742 and parser 1075-1082, with `Refused` exiting 2 at line 1116; `docs/design.md` line 82 and line 97 text as quoted; `dev/build-harness.spec.md` line 193 and the `resolve` synopsis as quoted; the three routing rows (design.md lines 103, 107, 114) exist under the names the spec uses; the "Tests to change" line citations (test_shepherd 48/54/69, test_spec_store 60/66/71, test_p0_cli 108/153/172) are exact-sources assertions on stores with no or an empty `decisions.md`, so Decision B leaves them green.
- Acceptance "Spec writer, critic and planner receive the decision log" ran today: printed the four source lists without `'decisions.md'` and `in_input=0` for every role, as verification.md states. It fails for the stated reason and cannot pass against a stub that adds the file without reading it (`in_input` counts the sentinel in the composed input).
- Acceptance "Decision refused alone, with a ruling, and on a second close" ran today: `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=2 state=parked lines=0` / `again=2 lines=0`, matching the today description (first line matches only because the flag is unknown; the valid close fails).
- Acceptance "Documents describe the new writers" printed `old_design=yes old_build=yes design=no build=no readme=no changelog=no`; "design blocks equal their copies" printed `1. Triage SAME` / `2. Spec writer SAME`. `factory log tail --event E` prints one JSON line per event, so the `events=2` count in scenario 1 is well-formed.
- Part C's replacement text matches the current blocks: triage.md lines 12-13 and spec_writer.md lines 34-35 read as the spec quotes them; the harness copies differ from `docs/prompts/` only by the "Acceptance items describe behaviour" rule and `400` for `{400}`, as part C.3 says.
- Archive through `record_decision` (A.1) cannot newly refuse: `decisions_of()` (specstore.py line 280) drops blank lines and joins wrapped continuations, so every line it returns is one non-blank line.
- Open-ticket consistency: `dev/issues.md` lists this as #32 and names #24 and #27 as the other `compose()` changes; the spec's Out-of-scope observation records the conflict.

Prior findings: none (round 1)

STATUS: REVISE
CONFIDENCE: high; every cited path and three acceptance commands checked on `main` at `9a48194`, and the one blocking finding is a gloss gap, not a design defect.
ESCALATIONS: none

## Your previous spec (v1)

=== proposal.md
## Problem

The factory forgets a standing rule that a human sets when answering one of its questions, so later tickets that depend on the rule are written without it. This hurts the AI agents that write, review and plan specs for those later tickets, and the operator, who today copies each such rule by hand into every request it affects.

Some background. The factory is a pipeline of AI agents, each with one fixed role, that turns a written request (a ticket) into merged code. The harness is the code that runs the pipeline and keeps its records. The harness keeps a decision log, `decisions.md`: one file per target repository, holding one dated line per decision, each tagged with the ticket that made it. The log has two gaps.

1. Only one step writes it. That step is archive, which runs when a finished ticket closes. Archive folds the ticket's approved spec into the repository's record of how the system behaves now, and copies the spec's Decisions section into the log. A decision made in any other way is never logged. The common case is a ticket that exists only to get a decision. An agent parks the ticket with a question for a human (the NEEDS-HUMAN status), the human answers, and the ticket closes without building anything. Archive never runs, so the answer stays in that one ticket's request file.
2. No agent receives the log. The harness builds each agent's input from a fixed list of files, and `decisions.md` is not on that list. Three agents need it: the spec writer (writes the spec), the critic (reviews the spec) and the planner (splits an approved spec into pieces that merge separately). Today they see a logged decision only if one of them happens to open the file.

This change does three things. It lets the human log a decision at any point in a ticket's life. It gives the log to those three agents. And it makes the agents' questions to a human ask whether the answer is a standing decision.

## Evidence

Every command below ran from `~/dev/spec-factory` on `main` at `9a48194`, against a throwaway store (`FACTORY_STATE` under `mktemp -d`). The live store was not touched.

- No command logs a decision. `bin/factory decision add T-0001 "…"` printed `factory: error: argument cmd: invalid choice: 'decision'` and exited 2. `bin/factory resolve T-0001 --close --decision "…"` printed `factory: error: unrecognized arguments: --decision …` and exited 2. Answering or closing a ticket cannot log what was decided.
- Archive is the only writer. `grep -rn decisions factory/` matches only `factory/specstore.py`. `init` creates an empty file at lines 67-70. `archive` appends at lines 328-333. The docstring at line 6 says "Only `archive` writes current truth and `decisions.md`."
- No agent receives the log. The scenario "Spec writer, critic and planner receive the decision log" (fixture: a store holding one current-truth spec and a `decisions.md` with one line containing `SENTINEL`) printed these input sources today:
  - triage `['requests/T-0001.md']`
  - spec_writer `['requests/T-0001.md', 'openspec/specs/thing/spec.md']`
  - critic `['specs/T-0001/v1.md', 'openspec/specs/thing/spec.md']`
  - planner `['specs/T-0001/v1.md']`

  Each role's input printed `in_input=0`: the logged line reaches none of them.
- The agents' questions do not ask whether an answer is standing. `grep 'standing decision'` finds nothing in the triage or spec-writer system prompt of a started run, or in `docs/prompts/01-triage.md` or `docs/prompts/02-spec-writer.md`. The triage prompt says only "Write the decision as one question with 2-3 concrete options."
- The design states the current rule. `docs/design.md` line 82 says "Only the archive step writes current truth and `decisions.md`." Line 97 says that a parent closed as applied leaves "Current truth and `decisions.md` … not updated". `dev/build-harness.spec.md` line 193 says "only `factory archive` (K) writes `openspec/specs/` and `decisions.md`", and line 315 repeats the closed-as-applied rule.
- The real case, in the Nanobot target's store (read only, `~/dev/nanobot-upstream/.factory/state`). Ticket T-0003 asked only for a decision about where the port's code lives. Its history shows: parked, then `to: ready-for-triage`, `by: dphang`, `resolve: answer`, then `to: closed`, `by: workflow`. `requests/T-0003.md` line 87 says "Close it as a recorded decision so that T-0011 (SPEC-06) and T-0013 (BUG-03) build on it." `wc -c decisions.md` printed `0`: the decision was never logged. `requests/T-0011.md` line 93 and `requests/T-0013.md` line 169 each carry a hand-added paragraph headed "Port decision that binds this ticket (added by the v3.5 driver, 2026-10-04)".
- Who runs `resolve`. No workflow script calls it: `grep -n resolve factory/workflows/*.js` matches nothing. T-0003's history records `by: dphang`. So the human, or the operator's session acting for them, runs `resolve`. The clerk (the small agent a workflow uses to run one store command) never does.
- The suite is green on base: `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `136 passed`.

## Root cause

- `factory/specstore.py` `archive()` (lines 310-336) is the only code that appends to `decisions.md`. `init()` (lines 55-71) creates the file empty.
- `factory/compose.py` `compose()` (lines 52-169) has no source for `decisions.md`. The spec writer and critic get current truth through `add_truth()` (lines 68-70, called at 81 and 98). The planner gets the approved spec and any ruling (lines 106-112).
- `factory/cli.py` `resolve()` (lines 675-742) and its parser (lines 1075-1082) have no decision argument. No `decision` command exists in `build_parser()`.
- The triage and spec-writer prompt blocks in `docs/design.md` (§1 Triage, §2 Spec writer), their copies in `docs/prompts/01-triage.md` and `02-spec-writer.md`, and the harness prompts `factory/prompts/triage.md` and `spec_writer.md` never ask whether an answer is standing.

## Out of scope

- Backfilling past answers. Each store's operator does that by hand with the new command, if they choose (Operator steps).
- A new triage status.
- Giving the log to triage, implementer, reviewer or verifier. The request names three roles. Triage not seeing standing decisions is noted under Out-of-scope observations.
- Recording a decision from `resolve --ruling`, `--to spec-gate` or `--redispatch`. These refuse `--decision` instead of ignoring it.
- What archive writes and when. Its line format, refusals and current-truth behaviour do not change.
- The harness lock, the routing rules, the merge gate, the gate commands.

## Open questions

none

## Decisions

- When `decisions.md` does not exist, `decision add` and `--decision` create it. The decision log does not depend on the spec tree. Rejected: refusing with "no spec store" as archive does, because archive refuses only since it must apply spec deltas, and a refusal would leave every store that never ran `factory init` (this repo's among them) with no way to log a decision.
- A logged line has archive's shape, `<YYYY-MM-DD> <ticket id> <text>`, with the UTC date and the text stripped of surrounding whitespace. There is one log format, whichever step writes it.
- The text must be one non-blank line, and the ticket must exist; otherwise the command exits 2 and writes nothing. A line break would break one line per decision.
- A decision may be logged against a ticket in any state, closed included. Closed is where T-0003's decision ended up.
- `--decision` is accepted only with `--answer` or `--close`. With any other `resolve` mode, or alone, it exits 2 and writes nothing, so a decision is never silently dropped. It is logged only after that mode's own checks pass: a refused `resolve` writes no decision.
- The human who runs `resolve` decides whether an answer is standing, and passes `--decision`. The harness never infers a decision from the answer file. Rejected: parsing a marker line out of the answer file, which ties a free-text file to the store and silently misses a mistyped marker.
- An empty or whitespace-only `decisions.md` is not given to any role. It carries nothing, and the empty file `factory init` creates would otherwise add an empty section to every input.
- The spec writer and critic get the log right after current truth. The planner gets it right after the approved spec, before any ruling.
- Each logged decision also writes the audit event `decision.recorded` (ticket, who, the text, and which command logged it). The decision is also kept in the `resolve` record and ticket history when `resolve` logs it. The log file itself does not say who decided.

## Risk

Blast radius: every spec writer, critic and planner run in every target whose `decisions.md` is non-empty gets one more input section. Nanobot's log is 0 bytes and this repo has none, so no run changes until someone logs a decision. Each decision costs one line of input tokens per run, for those three roles. `resolve` gains an optional flag, and its existing modes behave as before without it. Archive's behaviour does not change.

Protected and guardrail paths this touches:
- harness (`factory/**`): `factory/cli.py`, `factory/compose.py`, `factory/specstore.py`, and the agent prompts `factory/prompts/triage.md` and `factory/prompts/spec_writer.md`. The ticket's part C asks for the prompt change.
- generated (`docs/prompts/**`): `docs/prompts/01-triage.md` and `docs/prompts/02-spec-writer.md`, each re-copied from its changed `docs/design.md` block, never edited by hand.

Also changed (not protected): `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md`, `README.md`, and one new test file under `tests/factory/`. Not touched: `.factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Rollback: move the runtime back to the previous harness revision. Lines already logged stay in `decisions.md`, in the same format archive writes.

## Operator steps

1. Before the runtime moves to this revision, run your acceptance test of the prompt change (part C), as the pre-approval policy requires for any prompt change: read the new NEEDS-HUMAN wording in `factory/prompts/triage.md` and `factory/prompts/spec_writer.md`.
2. Optional, per store, after the runtime moves: backfill decisions you want later tickets to see. For the Nanobot store that means running `factory decision add T-0003 "<the decision as one line>"` from `~/dev/nanobot-upstream`, and then deciding whether to remove the hand-added paragraphs in T-0011's and T-0013's requests.

## Out-of-scope observations

- Triage does not receive the log. A triage run can therefore re-ask a question that a standing decision already settled. The request does not ask for this.
- Two other queued requests also change what each role receives from the same function, `compose()` in `factory/compose.py`: #24 (role-specific inputs) and #27 (roles never see a request's attachments). If they are built close together, they will conflict there.
- `dev/build-harness.spec.md` line 207 lists the operator commands that need `FACTORY_KEY`, and this tree does not implement that check. This spec does not add `decision add` to that list.

=== design.md
## Proposed change

**A. Log a decision at any ticket state** (`factory/specstore.py`, `factory/cli.py`).
1. Add `specstore.record_decision(root, tid, text, today=None) -> str`. It strips `text`, raises `store.Refused` when the result is empty or contains a line break, and builds `f"{date} {tid} {text}"` with the UTC date archive uses. It appends that line plus a newline to `root / "decisions.md"`, creating the file and its parent if absent, and returns the line. Make `archive()` append each Decisions line through it (same date, same format), so that one function writes the log. Update the module docstring (line 6): archive is the only writer of current truth, and archive, `decision add` and `resolve --decision` write `decisions.md`.
2. New command `factory decision add ID TEXT` (a `decision` subparser with `add`, positional `id` and `text`). It loads the ticket (an unknown id refuses with `no ticket ID`), with no check on its state, then calls `record_decision`. It logs event `decision.recorded` with `ticket`, `by=_by()`, `line`, `via="decision add"`, and prints `{"ok": true, "id": ..., "decision": <line>}`.
3. `resolve` gets `--decision TEXT`. At the top of `resolve()`, before anything is written: if `--decision` is given without `--answer` or `--close`, refuse with `--decision applies only with --answer or --close`. Also validate the text, by calling the same strip and one-line check before any write, so that a bad text refuses before the answer is appended. In the `--answer` and `--close` branches, once that branch's own refusals have passed, call `record_decision`, log `decision.recorded` with `via="resolve --answer"` or `"resolve --close"`, and pass `{"decision": <line>}` in the `extra` given to `move()`. The line then lands in the ticket history, the `resolve-<n>.yaml` record and the printed result. Without `--decision`, every branch behaves exactly as today.

**B. Give the log to the spec writer, critic and planner** (`factory/compose.py`).
Add an `add_decisions()` beside `add_truth()`. When `root / "decisions.md"` exists and holds non-whitespace text, it adds that file under the heading `Decision log (decisions.md): standing decisions, read-only`, with source `decisions.md`. It adds nothing otherwise. Call it right after `add_truth()` in the `spec_writer` and `critic` branches, and right after the approved spec in the `planner` branch, before the rulings loop. Triage and the build roles are unchanged.

**C. Questions to a human ask whether the answer is standing** (`docs/design.md` §1 and §2 blocks, then copies).
1. `docs/design.md` §1 Triage, step 3, the NEEDS-HUMAN item becomes:
   ```
      - NEEDS-HUMAN: it needs a product, priority, or design call. Write the
        decision as one question with 2-3 concrete options, and ask whether
        the answer is a standing decision that later tickets must follow.
   ```
2. `docs/design.md` §2 Spec writer, the "Open questions stay open" rule becomes:
   ```
   - Open questions stay open. Don't resolve product or design ambiguity
     yourself; list it, and the spec goes to NEEDS-HUMAN. For each open
     question, ask whether the answer is a standing decision that later
     tickets must follow.
   ```
3. Re-copy each changed block verbatim to `docs/prompts/01-triage.md` and `docs/prompts/02-spec-writer.md`. Make the same edit in `factory/prompts/triage.md` and `factory/prompts/spec_writer.md`, keeping their existing differences from the copies: the "Acceptance items describe behaviour" rule, and `400` in place of `{400}`.

**D. Documents** (`docs/design.md`, `dev/build-harness.spec.md`, `docs/changelog.md`, `README.md`).
1. `docs/design.md` line 82: replace "Only the archive step writes current truth and `decisions.md`." with text saying that only archive writes current truth, and that `decisions.md` has three writers: archive, `factory decision add <ticket id> "<line>"` at any ticket state, and `resolve --answer` or `--close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`. Extend the sentence on what the spec writer and critic receive: they and the planner also receive a non-empty `decisions.md`. Line 97: archive appends nothing to `decisions.md` for a parent closed as applied, and the human logs any decision with `factory decision add`. Resolution list, the "A question returns to the role that asked" item: when the answer is a standing decision, the human passes `--decision`. Routing table "Receives": add "the decision log" to the Triage ACCEPT → Spec writer row, the Spec writer READY-FOR-CRITIC → Critic row and the Human spec gate Approved → Planner row.
2. `dev/build-harness.spec.md`: at line 193, replace "only `factory archive` (K) writes `openspec/specs/` and `decisions.md`" with the same three-writer rule, naming `factory decision add`. At line 314, add `--decision TEXT` to the `resolve` synopsis, with its one-line effect and refusals. At line 315, apply line 97's change. Add `decision.recorded` to the event list at line 211.
3. `docs/changelog.md`: entry `46.` before "Declined:", in the existing style. It says why (a decision answered at a park and then closed without archive was lost, from the Nanobot T-0003 case), and what changed: the second writer of `decisions.md`, the three roles that receive it, and the question wording.
4. `README.md`, "Where a human decides": add `--decision "<line>"` to the Unstick row, valid with `--answer` or `--close`. Add a row **Record**: `factory decision add T-n "<line>"`, deciding "that a decision binds later tickets". Bump the status-header date, per "Maintaining this page".

**E. Tests** (new file `tests/factory/test_decision_log.py`, black-box through `bin/factory` on a `FACTORY_STATE` throwaway store, as `tests/factory/test_spec_store.py` does). Cover the scenarios of parts A and B, and the design-block-equals-copy check for §1 and §2. No existing test changes.

## Tests to change

none. Existing tests that assert exact input sources (`tests/factory/test_shepherd.py` lines 48, 54 and 69; `tests/factory/test_spec_store.py` lines 60, 66 and 71; `tests/factory/test_p0_cli.py` lines 108, 153 and 172) run on stores with no `decisions.md`, or with the empty one `factory init` creates. Decision B adds no source for either.

=== specs/decision-log/spec.md
## ADDED Requirements

### Requirement: A decision can be logged against a ticket in any state
`factory decision add <ticket id> "<text>"` SHALL append one line `<UTC YYYY-MM-DD> <ticket id> <text, stripped>` to the store's `decisions.md`, creating the file when absent, for a ticket in any state, and SHALL log one `decision.recorded` event per line.

#### Scenario: Decision logged against a closed ticket
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f resolve T-0001 --close >/dev/null; f decision add T-0001 "Lionbot code lives under lionbot/" >/dev/null 2>&1; echo "first=$? state=$(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml)"; f decision add T-0001 "  Second rule  " >/dev/null 2>&1; echo "second=$?"; sed "s/^$(date -u +%F) /TODAY /" $FACTORY_STATE/decisions.md 2>/dev/null; echo "events=$(f log tail -n 50 --event decision.recorded | wc -l | tr -d ' ')"; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  first=0 state=closed
  second=0
  TODAY T-0001 Lionbot code lives under lionbot/
  TODAY T-0001 Second rule
  events=2
  ```

### Requirement: A bad decision is refused and writes nothing
`factory decision add` MUST exit 2 and leave `decisions.md` unchanged when the ticket does not exist or the text is blank or spans more than one line.

#### Scenario: Unknown ticket, blank text and multi-line text are refused
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f decision add T-0009 "x" >/dev/null 2>&1; a=$?; f decision add T-0001 "  " >/dev/null 2>&1; b=$?; f decision add T-0001 "$(printf 'one\ntwo')" >/dev/null 2>&1; c=$?; echo "unknown=$a blank=$b multiline=$c lines=$(cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' ')"; f decision add T-0001 "one" >/dev/null 2>&1; echo "valid=$? lines=$(cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' ')"; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  unknown=2 blank=2 multiline=2 lines=0
  valid=0 lines=1
  ```

### Requirement: Answering or closing a ticket can log a decision
`factory resolve <id> --answer F --decision "<text>"` and `factory resolve <id> --close --decision "<text>"` SHALL do what they do without `--decision`, and SHALL also append the decision line in the same format.

#### Scenario: Answer and close each log a decision
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; st() { sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml; }; printf '# demo\n\nDo it.\n' > $T/r.md; printf 'Use option B.\n' > $T/a.md; f ticket new --file $T/r.md >/dev/null; f ticket park T-0001 --reason "NEEDS-HUMAN from triage" >/dev/null; f resolve T-0001 --answer $T/a.md --decision "Option B is the standing rule" >/dev/null 2>&1; echo "answer=$? state=$(st) answers=$(grep -c '^## Answer ' $FACTORY_STATE/requests/T-0001.md)"; f resolve T-0001 --close --decision "Closed as a recorded decision" >/dev/null 2>&1; echo "close=$? state=$(st)"; sed "s/^$(date -u +%F) /TODAY /" $FACTORY_STATE/decisions.md 2>/dev/null; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  answer=0 state=ready-for-triage answers=1
  close=0 state=closed
  TODAY T-0001 Option B is the standing rule
  TODAY T-0001 Closed as a recorded decision
  ```

### Requirement: A decision on a resolve that cannot carry one is refused
`factory resolve` MUST exit 2, write no decision and leave the ticket unchanged when `--decision` is given alone, with `--ruling`, `--to` or `--redispatch`, or with a `--close` or `--answer` that is itself refused.

#### Scenario: Decision refused alone, with a ruling, and on a second close
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; st() { sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml; }; n() { cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' '; }; printf '# demo\n\nDo it.\n' > $T/r.md; printf 'Ruling.\n' > $T/r2.md; f ticket new --file $T/r.md >/dev/null; f ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; f resolve T-0001 --decision "x" >/dev/null 2>&1; a=$?; f resolve T-0001 --ruling $T/r2.md --decision "x" >/dev/null 2>&1; echo "alone=$a ruling=$? state=$(st) rulings=$(ls $FACTORY_STATE/approvals/T-0001 2>/dev/null | grep -c ruling) lines=$(n)"; f resolve T-0001 --close --decision "Closed with a rule" >/dev/null 2>&1; echo "close=$? state=$(st) lines=$(n)"; f resolve T-0001 --close --decision "Again" >/dev/null 2>&1; echo "again=$? lines=$(n)"; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  alone=2 ruling=2 state=parked rulings=0 lines=0
  close=0 state=closed lines=1
  again=2 lines=1
  ```

### Requirement: The design documents name every writer of the decision log
`docs/design.md`, `dev/build-harness.spec.md` and `README.md` SHALL name `factory decision add` as a writer of `decisions.md`; the two design documents SHALL no longer say that only archive writes it; and `docs/changelog.md` SHALL carry entry 46 about `decisions.md`.

#### Scenario: Documents describe the new writers
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  y() { grep -qF "$1" "$2" && echo yes || echo no; }; echo "old_design=$(y 'Only the archive step writes current truth and `decisions.md`' docs/design.md) old_build=$(y 'only `factory archive` (K) writes `openspec/specs/` and `decisions.md`' dev/build-harness.spec.md) design=$(y 'factory decision add' docs/design.md) build=$(y 'factory decision add' dev/build-harness.spec.md) readme=$(y 'factory decision add' README.md) changelog=$(grep -qE '^46\. .*decisions\.md' docs/changelog.md && echo yes || echo no)"
  ```
- THEN it prints exactly `old_design=no old_build=no design=yes build=yes readme=yes changelog=yes`

=== specs/role-input/spec.md
## ADDED Requirements

### Requirement: Spec writer, critic and planner receive the decision log
`run compose` SHALL add a non-empty `decisions.md` to the input of the spec writer and the critic right after current truth, and to the planner's right after the approved spec, and SHALL NOT add it to triage's input.

#### Scenario: Spec writer, critic and planner receive the decision log
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; S=$FACTORY_STATE; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f init >/dev/null 2>&1; mkdir -p $S/openspec/specs/thing $S/specs/T-0001; printf '# thing\n\n## Requirements\n' > $S/openspec/specs/thing/spec.md; printf 'spec\n' > $S/specs/T-0001/v1.md; printf '2026-10-01 T-0009 SENTINEL keep the old format\n' > $S/decisions.md; f ticket set T-0001 spec.version=1 spec.approved_version=1 >/dev/null; go() { f ticket set T-0001 status=$2 'in_flight=[]' >/dev/null; i=$(f run start --role $1 --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); f run compose $i | python3 -c 'import json,sys; print("'$1'", json.load(sys.stdin)["sources"])'; echo "  in_input=$(grep -c SENTINEL $S/runs/$i/input.md)"; }; go triage ready-for-triage; go spec_writer ready-for-spec-writer; go critic ready-for-critic; go planner ready-for-planner; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  triage ['requests/T-0001.md']
    in_input=0
  spec_writer ['requests/T-0001.md', 'openspec/specs/thing/spec.md', 'decisions.md']
    in_input=1
  critic ['specs/T-0001/v1.md', 'openspec/specs/thing/spec.md', 'decisions.md']
    in_input=1
  planner ['specs/T-0001/v1.md', 'decisions.md']
    in_input=1
  ```

### Requirement: An empty or absent decision log adds nothing to role input
`run compose` MUST NOT add `decisions.md` to any role's input when the file is absent or holds only whitespace.

#### Scenario: Empty and absent decision logs add no input source
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; S=$FACTORY_STATE; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f init >/dev/null 2>&1; mkdir -p $S/specs/T-0001; printf 'spec\n' > $S/specs/T-0001/v1.md; f ticket set T-0001 spec.version=1 spec.approved_version=1 >/dev/null; go() { f ticket set T-0001 status=$2 'in_flight=[]' >/dev/null; i=$(f run start --role $1 --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); f run compose $i | python3 -c 'import json,sys; print("'$3' '$1'", json.load(sys.stdin)["sources"])'; }; printf '\n' > $S/decisions.md; go spec_writer ready-for-spec-writer empty; go critic ready-for-critic empty; go planner ready-for-planner empty; rm $S/decisions.md; go spec_writer ready-for-spec-writer absent; go planner ready-for-planner absent; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  empty spec_writer ['requests/T-0001.md']
  empty critic ['specs/T-0001/v1.md']
  empty planner ['specs/T-0001/v1.md']
  absent spec_writer ['requests/T-0001.md']
  absent planner ['specs/T-0001/v1.md']
  ```

=== specs/needs-human-questions/spec.md
## ADDED Requirements

### Requirement: A question to a human asks whether its answer is a standing decision
The triage and spec-writer prompts, as a run receives them and in their `docs/prompts/` copies, SHALL tell the role to ask, with each NEEDS-HUMAN question, whether the answer is a standing decision.

#### Scenario: Triage and spec-writer prompts ask about standing decisions
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; y() { grep -q 'standing decision' "$1" && echo yes || echo no; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; for r in triage:ready-for-triage spec_writer:ready-for-spec-writer; do f ticket set T-0001 status=${r#*:} 'in_flight=[]' >/dev/null; i=$(f run start --role ${r%%:*} --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); echo "${r%%:*} prompt=$(y $FACTORY_STATE/runs/$i/system-prompt.txt)"; done; for c in 01-triage 02-spec-writer; do echo "$c copy=$(y docs/prompts/$c.md)"; done; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  triage prompt=yes
  spec_writer prompt=yes
  01-triage copy=yes
  02-spec-writer copy=yes
  ```

### Requirement: The triage and spec-writer prompt copies stay verbatim
`docs/prompts/01-triage.md` and `docs/prompts/02-spec-writer.md` MUST each equal the fenced `text` block under its heading in `docs/design.md`.

#### Scenario: Triage and spec-writer design blocks equal their copies
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  python3 -c 'import re; d=open("docs/design.md").read(); F="`"*3; [print(h, "SAME" if re.search(r"^## "+re.escape(h)+r"\n.*?^"+F+r"text\n(.*?)^"+F+"$", d, re.M|re.S).group(1)==open("docs/prompts/"+c).read() else "DIFFERENT") for h, c in (("1. Triage","01-triage.md"),("2. Spec writer","02-spec-writer.md"))]'
  ```
- THEN it prints exactly:
  ```
  1. Triage SAME
  2. Spec writer SAME
  ```

=== verification.md
## Acceptance

Run every command with bash from the root of the `~/dev/spec-factory` checkout under test. The fixtures need `python3` and write only under `mktemp -d`; each runs in a subshell, so its `FACTORY_STATE` does not leak. "Today" means `main` at `9a48194`, where every today output below was observed. `TODAY` stands for the UTC date when the scenario runs. A run that straddles UTC midnight can print the raw date instead; re-run it. No scenario repeats the gate commands (`git diff --check main...HEAD` and the harness suite, `136 passed` today), because the verifier runs them.

- Decision logged against a closed ticket → NEW. Today it prints `first=2 state=closed`, `second=2`, no decision lines, and `events=0`: `decision` is not a command (`invalid choice: 'decision'`).
- Unknown ticket, blank text and multi-line text are refused → NEW. Today it prints `unknown=2 blank=2 multiline=2 lines=0` then `valid=2 lines=0`: the refusals are argparse's, and the valid add also fails, so no line is ever written.
- Answer and close each log a decision → NEW. Today it prints `answer=2 state=parked answers=0` then `close=2 state=parked`, and no decision lines: `--decision` is an unrecognized argument, so neither the answer nor the close happens.
- Decision refused alone, with a ruling, and on a second close → NEW. Today it prints `alone=2 ruling=2 state=parked rulings=0 lines=0`, `close=2 state=parked lines=0`, `again=2 lines=0`. The first line already matches, only because the flag does not exist. The valid close fails, so the second and third lines differ.
- Documents describe the new writers → NEW. Today it prints `old_design=yes old_build=yes design=no build=no readme=no changelog=no`.
- Spec writer, critic and planner receive the decision log → NEW. Today the triage line matches, but spec_writer, critic and planner lack `'decisions.md'` in their sources, and each prints `in_input=0`.
- Empty and absent decision logs add no input source → REGRESSION. Today it prints exactly the expected five lines, and it must still do so after the change (decision: an empty log is not input).
- Triage and spec-writer prompts ask about standing decisions → NEW. Today all four lines print `no`.
- Triage and spec-writer design blocks equal their copies → REGRESSION. Today both lines print `SAME`. It must still pass after part C edits the blocks and re-copies them.

## Responses

none (round 1)
