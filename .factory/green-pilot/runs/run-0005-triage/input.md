## Context for this run (composed by the harness, not part of the request)

Repository: `nanobot`, the lionbot fork. This checkout is the TARGET generation: branch
`feat/lionbot-v3` at `~/dev/nanobot-upstream` (upstream base tag `lionbot-v3-base`). The
REFERENCE generation is the production fork at `~/dev/nanobot` (branch `feat/lionbot-next`,
"blue"): read it only to observe what the feature does today; never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Running things here: `uv run <cmd>` from the repo root (never pip). Tests run serially with
`PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider <path>`.
Lint: `uv run ruff check nanobot/`. Acceptance commands must be runnable as written on this checkout.

The request is a legacy "faux spec": a document that mixes the durable intent (what the
operator needs the bot to do) with one generation's implementation record (test names,
file:line citations, commit SHAs, ledger status, verification narrative, a prior
implementation profile). Treat the implementation record as evidence of what the reference
generation did, not as requirements. Carry forward only what the requester needs; anything
that can be re-derived from the code at build time does not belong in the spec. Where the
request's status says the capability is already built on this checkout, verify that before
writing NEW criteria; a NEW criterion that already passes proves nothing.

Build half, as this repo runs it today: there is no remote and no CI service. "Open a PR" means
commit on your branch in your worktree and return the PR description; "push" means commit; the
"CI result" is the gate suite (the gate commands in your input: lint, and the full-suite gate,
which passes when no test fails outside the port's known-failure baseline), which the verifier
runs on the head and reports as `Gate suite: PASS|FAIL`. A merged sub-ticket is a local
`--no-ff` merge into the integration branch. Never push, never touch another worktree.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0005-triage/output.md`

## Request (raw, with any answers appended)

# Harness: a killed checker run parks as a harness bug instead of a budget kill

GitHub: https://github.com/danielphang/spec-factory/issues/18

Note: operator, 2026-10-03: this fix is approved at the spec gate in advance; it is built after #16 (the first pilot) merges, because both change results_record in factory/cli.py.

**Problem.** When a reviewer or verifier run is killed (it returned nothing, for example on a budget or session limit), the build loop should park the sub-ticket with reason `budget kill: <role>`, so the operator knows to re-dispatch it. Instead, recording the kill crashes and the sub-ticket parks as `harness-bug: results record <role>`, which reads as a factory defect and hides the real cause.

**Evidence.** Found by the spec writer on the first end-to-end pilot (#16, out-of-scope observation). `factory/workflows/build.js` calls `results record … --output <run>/output.md … --killed` for every checker, but a killed run has no `output.md` (`run finish --status-override KILLED` writes none). `factory/cli.py` `results_record` reads `--output` before looking at `--killed`, so it raises `FileNotFoundError` (exit 1). Reproduced by the writer.

**Proposed fix.** `results_record` does not read `--output` when `--killed` is given (a killed row needs no output); or `build.js` omits `--output` for a killed run. The first keeps the dispatcher unchanged and makes the command robust to either caller. One test: a killed checker parks as `budget kill: <role>`.
