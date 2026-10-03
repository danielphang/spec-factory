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
`/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0001-triage/output.md`

## Request (raw, with any answers appended)

# Harness: a checker result with no Commit: line, or a non-SHA one, is recorded as if it checked the current commit

GitHub: https://github.com/danielphang/spec-factory/issues/16

**Problem.** When the reviewer or verifier finishes, the factory records its verdict (APPROVE, VERIFIED, and so on) against the exact git commit it checked, and the merge only goes ahead when every verdict on the branch's current commit is green. Each checker states which commit it looked at on a `Commit:` line in its output. Today the harness only refuses an output whose `Commit:` line names a *different* commit; an output with no `Commit:` line at all, or with a non-commit value such as `Commit: HEAD`, is accepted and recorded as if it checked the current commit. So a checker that looked at an older commit, or didn't say, can still count toward a merge. This affects anyone relying on the merge gate's guarantee that every approval is for the code being merged.

**Evidence.** Found by an independent validator on the build half (green `e2f612272` re-check): "A missing `Commit:` line is accepted. `Commit: HEAD` (not hex) is accepted. Only the first `Commit:` line is checked." The build spec (part H) says the checker's `Commit:` line must equal the current head. The current check is in `factory/cli.py`, `results_record`.

**Proposed fix.** `factory results record` refuses (exit 2, nothing written) an output that has no `Commit:` line, whose `Commit:` value is not a hex commit id, or whose last `Commit:` line does not name the head being recorded. A KILLED run (no output) is unchanged.

**Scope.** `factory/cli.py` and one new test file. No change to roles, prompts or routing.
