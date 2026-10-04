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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0143-triage/output.md`

## Request (raw, with any answers appended)

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
