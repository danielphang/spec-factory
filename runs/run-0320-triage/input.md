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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0320-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0320-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Turn economy for the spec writer and critic: batch reads, read ranges, keep long output in scratch; the critic runs no suites and builds no prototypes"
labels: "harness"
---
**Where:** `factory/prompts/spec_writer.md` and `factory/prompts/critic.md` (with the design doc's §2 and §3 blocks and `docs/prompts/02-spec-writer.md`, `03-spec-critic.md`); possibly one shared line in `factory/prompts/preamble.md`.

**Problem:** the spec writer is the most expensive role. It accounts for 34% of all workflow context tokens: 309M of 866M across this session's 97 workflow runs, counted once per message (2026-10-07). Its cost comes from the number of turns, not from what it runs. Every turn re-sends about 45k tokens of start-up context plus everything read so far. A writer run takes a median of 29 API calls (p90: 73) and 5.3M tokens. The critic takes 9 calls and 0.8M.

**Evidence (2026-10-07, this session's transcripts, factory/cost.py role detection, deduplicated by message id):**

| | Spec writer | Critic |
|---|---|---|
| Runs / calls (median, p90) | 58 / 29, 73 | 54 / 9, 12 |
| Context tokens | 309M (5.3M per run) | 42M (0.8M per run) |
| Start-up context × calls | 101M (33%) | 21M (49%) |
| Tool output carried into later calls | 92M: `grep`/`sed`/`cat`/`git` output 53%, whole-file `Read` 37% (avg 6.4k tokens each), suite runs 8% | 10M: `Read` 78% |
| Test-suite runs | 313 (about 5 per run) | 101 (about 2 per run) |
| Prototype clones | 54 | 17 |

The critic's suite runs and prototype builds go against principle 2 and the spiking section of `docs/principles.md`: the critic grounds a claim with at most two paths and one command, and does not build.

**Proposed change (prompt-only):**
- A. Spec writer, investigation rules:
  - Batch independent reads and commands into one turn.
  - Read line ranges, not whole files, once `grep` has located the lines.
  - Write long command output (suite runs, scenario output) to the run's scratch directory and `grep` or `tail` it, rather than printing it in full.
  - Draft the spec in as few writes as possible.
- B. Critic: no test-suite runs and no prototype builds. Ground each claim with at most two paths and one command. A claim that needs a build becomes a finding for the writer, or a question. The same reading rules as A apply.
- C. Nothing else changes: no rubric item, round limit or required section moves.

**Acceptance:** replay the intake of 2–3 already-approved tickets (the same request and base, scratch store) with the old and the new prompts. Record calls per run, context tokens, suite runs and prototype clones, and show the two specs side by side. Targets: the writer's median calls roughly halve, and the critic runs no suite. As a prompt change, the operator judges the specs' quality side by side before the runtime moves.

**Out of scope:** the fixed start-up context (#65, `--system-prompt-file`); bounded-path short specs (#64); the harness running acceptance commands on the base (#67/#68, after #51).

Operator-approved 2026-10-07 ("yes to (1)"); filed by the Green session.



Issue: https://github.com/danielphang/spec-factory/issues/73
