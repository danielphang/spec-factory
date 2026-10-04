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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0144-spec_writer/output.md`

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
