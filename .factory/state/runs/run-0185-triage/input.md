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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0185-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Request (raw, with any answers appended)

---
title: "Roles running in parallel share the session scratchpad and overwrite each other's files"
labels: "harness"
---
**Where:** the role preamble (`docs/design.md` §Shared preamble, `factory/prompts/preamble.md`); `run start` (`factory/cli.py`), which creates the run directory; the store's `.gitignore`.

**Problem:** roles running at the same time overwrite each other's scratch files. Every agent a workflow starts inherits the launching session's scratchpad path, and nothing tells it to keep its files apart. So when several workflows run in one session, which is the parallel intake the README recommends, two roles can write to the same place. One can then run or cite a prototype that another role made. Checkers have a related problem: they also leave files in the dev checkout itself.

**Evidence:**
- Nanobot v3.5 store, 2026-10-04, T-0022's spec writer (run-0068): "My session scratchpad was overwritten during this run by files from other work: a WhatsApp chat-log check and a /summarize check." The files were T-0009's spec writer's, which was running at the same time. The writer moved its prototype into a subdirectory itself. Reported by the Driver.
- Spec-factory retro trial (2026-10-04, escalation H8): run-0062 created `~/dev/spec-factory/.venv` because `uv` walked up from a worktree without `pyproject.toml`. Run-0103 left an untracked throwaway store under the dev checkout. Run-0134 found a stale `scratchpad/base` from another run.

**Proposed change:**
- A. `run start` creates `runs/<run id>/scratch/`, ignored by the store's `.gitignore`.
- B. The preamble: write scratch files only under your run's `scratch/` directory (its absolute path is in your input); never in the session scratchpad, the dev checkout or another run's directory. Checkers make their base clones there.
- C. `run finish` (or `run cleanup`) removes `scratch/` after the run, unless the run parked, so a human can still inspect it.

**Interim operating rule:** no parallel intake on tickets whose roles may prototype in the same subsystem. The README's parallel-intake claim gets this caveat.

**Out of scope:** worktrees the build half already owns (`worktrees/`, `runs/*/wt/`).


---

Operator: spec gate pre-approved under the queue policy (`.factory/answers/queue-preapproval-policy.md`).
