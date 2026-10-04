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
  `harness.lock`, and closed records (`answers/`, `green-pilot/`). Its live store is still
  `intake/state/` until an operator step moves it.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3`), is instance A: it
still runs its own in-tree copy of the harness, from which this repo's harness was imported. Read
it only to observe what a fix does there today; never write there, and never copy its test names,
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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0135-triage/output.md`

## Request (raw, with any answers appended)

---
title: "Build speed: run each test suite only where it can change the verdict"
labels: "harness"
---
**Where:** `factory/prompts/implementer.md` and `verifier.md` (and their `docs/design.md` / `docs/prompts/` copies), the build half's parent-close step (`factory/cli.py` join/close, `factory/workflows/build.js`), and the gate commands' use in the verifier prompt.

**Problem:** one sub-ticket runs the target's full test suite four or five times, and most of those runs cannot change the outcome. For spec-factory that costs a few minutes per ticket. For the Nanobot v3.5 port, about 7,600 tests with every extra installed, it is the largest cost of each build, multiplied by 32 tickets.

**Evidence (spec-factory runs, 2026-10-03):**
- T-0015's implementer took 431 s. About 103 s went to running the suite and the acceptance checks *before* editing, and about 85 s to running them again after. `main` had already passed the same suite at its last merge, so the before-run of a regression check proves nothing. Only checks labelled NEW need a before-run, because they must fail first.
- T-0013: the parent-close verifier re-ran the same scenarios and the same suite on the merge of the one sub-ticket's checked head into an unchanged `main`. That took 5.5 min, 20% of the build.
- T-0014 and T-0015 changed only docs and prompts. The suite ran at every stage, though no test can observe those files.

**Proposed change:**
- A. The implementer runs the checks labelled NEW before and after the edit, and the REGRESSION checks and gate commands after only.
- B. The verifier runs the checks labelled NEW on base and head, and the REGRESSION checks and gate commands on head only.
- C. Parent close reuses the sub-ticket's VERIFIED result, without a new verifier run, when all of these hold: the parent has exactly one sub-ticket; `main` has not moved since that sub-ticket's merge; and the sub-ticket's acceptance list contains every scenario of the parent. Otherwise parent close runs as today.
- D. A gate command can declare the paths it covers. When a branch's diff touches none of them, the command is skipped and the `ci` row records the skip and the reason. Instance B: the suite covers `factory/**`, `bin/factory`, `tests/**`, `pyproject.toml` and `uv.lock`.

**Acceptance:** B and C are measured on the next real build, against T-0015's timings. Every refusal the gate gives today still happens: a failing NEW check, a failing regression, a failing suite on a code diff.

**Out of scope:** the clerk (deferred by the operator, #24); typed role agents (#24 part A).
