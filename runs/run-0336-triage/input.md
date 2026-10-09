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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0336-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0336-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Spec writer, critic and planner receive the whole spec store every turn: send only the ticket's capabilities, index the rest, open on demand (writer input mean 102 KB, max 416 KB on nanobot)"
labels: "harness"
---
**Problem, for the gate:** the spec writer receives the whole spec store as its input, every current-truth capability and the entire decision log, and carries it on every turn of a run that takes a median of 45 model calls. On the nanobot store the writer's composed `input.md` averages 102 KB and the largest is 416 KB, about 104k tokens. In that largest input, 300 KB is "Requirements", the current truth of every one of the store's 20 capabilities, and 51 KB is the whole decision log. The ticket touched one or two capabilities. That input is re-sent on each of the run's calls, so one run can carry several million tokens of specs it never reads.

**Evidence (2026-10-08):**
- `compose.py:current_truth` returns every `openspec/specs/*/spec.md` in the store; the spec writer, critic and planner branches add them all (`compose.py:169`), and `add_decisions` adds the whole `decisions.md` (404 KB of specs and 68 KB of decisions on the nanobot store today, both growing with every archive).
- Writer `input.md` sizes: spec-factory store mean 56 KB, max 217 KB; nanobot store mean 102 KB, max 416 KB (`runs/run-*-spec_writer/input.md`).
- Section sizes of the largest, `run-0276-spec_writer`: ten "Requirements" sections of 72, 43, 26, 25, 19, 15, 13, 10, 10 and 7 KB; "Decision log" 52 KB; the ticket itself 6 KB.
- Writer runs: median 45 API calls, p90 80 (105 transcripts). Carried cost of the input = its tokens × the calls after it is read.
- SWE-agent (Yang et al., NeurIPS 2024, https://arxiv.org/html/2405.15793): showing an agent the full file scored 12.7% against 18.0% for a 100-line window; a search that returns more than 50 results is refused with a request to narrow. Bounded, on-demand context beats complete context.

**Proposed change:** current truth and decisions on demand, for the writer first and the critic and planner the same way.

- A. **Triage names the capabilities.** The triage output gains a `Capabilities:` line listing the current-truth capabilities the request touches (existing names, or `new`). The writer may add to the list in its spec; the critic checks it.
- B. **Compose sends only those.** For the spec writer, critic and planner, `compose.py` adds the full `spec.md` of each named capability, and for every other capability one index line: name, one-sentence purpose (the spec's first paragraph or its heading), size. The decision log is filtered to decisions whose text names a listed capability or the ticket's request, plus an index line per other decision (date, title).
- C. **The rest is one command away.** `factory spec show <capability>` prints a capability's current truth; `factory decision show <id|capability>` prints decisions. The writer prompt's investigation step names both; the role-context block says the index is complete and anything in it can be opened.
- D. **Measure before and after.** `factory stats` (#70) or `factory/cost.py` reports the writer's mean and max `input.md` size and its carried share per run; the acceptance records both figures on the two stores before and after this lands.

**Decisions:** no capability is hidden, only deferred: the index is complete and opening is one command, so a writer that needs a capability it was not given still gets it. The critic sees the same list the writer did plus anything the writer opened (its spec names them under Evidence), so independence is unchanged. Nothing changes for roles that do not receive current truth today.

**Sequencing:** after #24 part C (merged) as its extension to the writer side; independent of #65; before #64, whose short specs would otherwise still carry the whole store.

**Acceptance the writer can make runnable:** a fixture store with three capabilities and a ticket naming one composes a writer input containing that capability's full spec, two index lines, and only the decisions that name it; `factory spec show` on an unnamed capability prints it; on the nanobot store, the mean writer input falls below 40 KB and the largest below 100 KB with the capability list from the last ten tickets, recorded in the spec's Evidence beside the figures above.

**Out of scope:** reads and searches the writer performs itself (#76); the implementer, reviewer and verifier inputs (#24 part C covers them); condensing within a run.

**Risk:** a writer that does not open a capability it needed writes a spec that conflicts with it; the critic's consistency check (rubric 5) and the index line are the mitigation, and D measures whether SPEC-DEFECT or critic rubric-5 findings rise.


## Comments



Issue: https://github.com/danielphang/spec-factory/issues/75
