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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0245-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0245-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Amend a pinned spec after planning (scenarios broken by another ticket's merge), and a critic check for cross-ticket dependencies"
labels: "harness"
---
**Problem:** once a spec is pinned and its ticket planned, nobody can amend it, even when its scenarios become wrong because another ticket merged first. `approve-spec --edit` works only at `awaiting-spec-gate`, and `planned` has no route back to the gate. The workaround today is a ruling (compose hands rulings to the implementer, the checkers and the parent-close run). But `archive` then writes the unamended scenario text into current truth, where it would fail if re-run.

**Evidence:**
- Nanobot v3.5, 2026-10-04: T-0008 (SPEC-05, typing) was approved while T-0002 (SPEC-20) was unbuilt. T-0002 then merged and made WhatsApp groups fail closed without a policy store. Two of T-0008's pinned scenarios create no store, so they cannot pass, though the code is correct. T-0008.1 BLOCKED (run-0166). The Driver ruled "test setup only: seed a policies.json; THEN lines unchanged" in `approvals/T-0008.1/` and `approvals/T-0008/`. The same seeding is expected in T-0004 (SPEC-01) and T-0007 (SPEC-04).
- spec-factory, 2026-10-03: T-0012's parent close hit a scenario that could not pass as written (whitespace over the store). The Green session amended the pinned `specs/T-0012/v3.md` in place and recorded it in `approvals/T-0012/amendment-1.md`. That was a hand edit, with no command behind it.

**Proposed change:**
- A. `factory spec amend <parent> --file <amended spec> --reason "<line>"`: human-run, at any state after pinning and before archive.
  - It writes a new spec version, re-pins the change folder (the OpenSpec deltas), and records the amendment in `approvals/<parent>/amendment-<n>.md` with a diff summary and a log event.
  - Compose then hands the amended version to every later role run.
  - It refuses when a sub-ticket is in flight. Merged sub-tickets keep their results, and the amendment notes which scenarios changed after they merged.
- B. **The critic's cross-ticket check at the spec gate.** For each scenario, does it depend on behaviour that an approved but unmerged ticket changes? If so, it is a finding: name the ticket and the decision, and require the scenario's setup to hold under both orders. This is the same class as #40 (tests a decision overturns), applied across tickets.

**Gate:** A is a human-only command, but it changes what the spec gate pins. It waits for the operator's approval at the gate. B is a prompt rule (pre-approved class).

Reported by the Nanobot v3.5 Driver.


---

Operator (2026-10-04): parts A and B approved as one ticket; the spec gate is pre-approved (`.factory/answers/operator-decisions-2026-10-04.md`).
