## Findings

[BLOCKING] 6 proposal.md, Operator steps, item 1
Problem: The first operator step uses two terms specific to this system, "the runtime moves" and "the queue policy", that no human-facing section has glossed, so the operator at the gate cannot tell what event the step precedes or where the required test is defined.
Evidence: Problem, Evidence, Decisions and Open questions never mention a runtime or a queue policy. The policy exists at `.factory/answers/queue-preapproval-policy.md:10` ("a standards or prompt change still gets the operator's acceptance test before the runtime moves"), but the spec gives neither the path nor what the test is. `grep -rni "queue policy" README.md docs/design.md` finds nothing, so a reader new to the system has nowhere else to look.
Suggested fix: Rewrite item 1 as one sentence that glosses both terms, for example "Before the upgrade step moves the factory's running copy (the runtime checkout, `~/dev/spec-factory-harness`) to this revision, run the operator's acceptance test that `.factory/answers/queue-preapproval-policy.md` requires for a prompt change", and gloss "the runtime moves" the same way at its first use in Risk and items 2-3.

[SHOULD-FIX] 2 specs/run-scratch/spec.md, scenario "a run's system prompt carries the scratch rule"
Problem: The oracle `grep -c 'session scratchpad'` with THEN "1 or more" passes against a stub that mentions a session scratchpad anywhere in the preamble, without the rule or its precedence clause.
Evidence: Ran the command on a throwaway store at `d15d833`: it prints `0` today, as stated. Any single sentence containing the phrase would make it print `1`.
Suggested fix: Grep for the clause the requirement actually asserts, `takes precedence over any other instruction to use a session scratchpad`, and make the THEN an exact `1`.

[NIT] 4 proposal.md, Decisions, third bullet
Problem: The decision says scratch is removed when the ticket next changes state, but does not say the consequence that matters at the gate: a spec writer's prototype is gone by the time the critic and the gate operator read the spec, since the ticket moves to `ready-for-critic` before either reads it.
Evidence: Design D clears on every transition except to `parked`; the workflow transitions after `run finish`. This spec's own Evidence cites a prototype no later reader can inspect.
Suggested fix: Add one sentence to the bullet saying that a prototype survives only while the ticket is parked, so a writer who wants the gate to see one must say so in the spec instead.

## What I checked

- Cited paths and lines exist and say what the spec says: `factory/cli.py:198` (`run_start`, no scratch directory, `ensure_gitignore` only under `if baseline` at `:223` and inside `_start_build_run` at `:242`), `factory/cli.py:266` (`run_cleanup` removes only a checker worktree), `factory/store.py:49-63` (`STORE_GITIGNORE` with three lines; `ensure_gitignore` appends the whole block when any line is missing, as Root cause states), `factory/compose.py:85-90` (Output file and Running code sections, nothing on temporary files), `factory/prompts/preamble.md:40,50` (RUNNING CODE and GUARDRAIL PATHS), `tests/factory/test_tripwire.py:230-231` (the two assertions named under Tests to change), `README.md:298-300` (the "#35" caveat), `dev/build-harness.spec.md:203,301`, `docs/design.md:54` (Tripwire paragraph) and `:164` (Shared preamble).
- Evidence rows: `run-0134-verifier/output.md:38`, `run-0062-verifier/output.md:28`, `retro_with_efficiency.md:159`, and `~/dev/nanobot-upstream/.factory/state/runs/run-0068-spec_writer/output.md:576` each contain the quoted or paraphrased text. `.venv` is dated Oct 3 01:12; run-0062's `meta.yaml` has `started: '2026-10-03T08:11:34+00:00'`, so "a minute after the run started" holds.
- Ran scenarios 1, 2, the preamble-identity check and the parked-ticket scenario through the Running code wrapper on a throwaway store from `~/dev/spec-factory` at `d15d833`. Outputs: `run-0001-triage dir=no heading=0 own=0 other=0` and the same for run-0002; `0`; `SAME`; `parked=kept` then `resumed=kept`. All match the "today" values in verification.md, so the NEW items fail today for the stated reason.
- `docs/changelog.md` has no `#35` and `dev/build-harness.spec.md` has no `runs/<run_id>/scratch/`, matching the documents scenario's `1 0 0`.
- Design D's reading of the code holds: `store.save_ticket` is a one-line YAML write (`factory/store.py:98`); `park_ticket` sets `parked` through it (`:102-110`); `run_finish` saves the ticket without changing its status (`factory/cli.py:319`); `ticket transition` sets the new status before saving (`:171-175`).
- Scope: about 210 changed lines, one PR, out-of-scope list present and sensible; `dev/issues.md:42` lists #35 as "not in intake", and I found no open ticket that owns the same surface.
- Risk declares the harness and generated paths the PR touches. The two store `.gitignore` files it names are rewritten by the harness at run time, not by the PR, and the spec says so.

## Out-of-scope observations

- The run-0062 `.venv` case is correctly deferred; nothing in this spec would have stopped it.

STATUS: REVISE
CONFIDENCE: high. Every cited path and the four acceptance commands I ran match the spec; the one blocking finding is a gloss gap the rubric names explicitly, and the fix is one sentence.
ESCALATIONS: none
