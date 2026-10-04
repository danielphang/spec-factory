# Plan: T-0024 (#45), live-store guard

One sub-ticket. The change is small: about 25 lines in `factory/cli.py`, one line in each workflow script, one new test file, one existing test and its helper's `STRIP` tuple, and the documents. It cannot be split into parts that each merge cleanly:
- Part A without part B breaks dispatch. With the fence in place and no marker in `intake.js`, the scenario "An intake run against a real store reaches its end with its run in flight" prints `returned=parked stored=ready-for-triage` (spec Evidence, negative controls). Main would then hold a harness that parks every intake.
- Part B without part A adds an environment variable that nothing reads. It is harmless, but its NEW scenario would be the only thing it proves.
- Part C cannot trail A and B. The briefing requires a change to a command, state, stop or path to update `README.md` in the same ticket, and the README paragraph documents the refusal that A adds.
- The existing-test change (`FACTORY_DISPATCH="1"` on the `run compose` call, and `"FACTORY_DISPATCH"` in `STRIP`) has to land with A. Without it the gate suite fails on A, because the in-flight rule refuses that call.

Splitting would add a merge and a re-verify and would make no review or rollback easier.

Checked on this checkout (`~/dev/spec-factory`, HEAD `d2a5143`):
- `git diff abaa75a HEAD --stat -- factory bin tests README.md docs dev` prints nothing, so the spec's base still holds for the code and documents.
- `factory/instance.py` defines `caller_cwd` (:41), `find` (:55), `own_state_root` (:93), `is_own_store` (:105) and `guard` (:141).
- In `factory/cli.py`, `main()` has `root = store.state_root(cfg)` followed by `instance.guard(...)`, and `init_cmd` has `root = instance.state_root(inst, cfg)`. These are the two call sites in design A.4 and A.5.
- `intake.js` and `build.js` both build `ENV` and then `BIN` as the spec describes.
- `tests/factory/test_instance.py:21` is `STRIP`, and `:271` is `test_composed_input_opens_with_the_instance_context`, with its `run compose` call at `:274`.
- The last changelog entry is 51.
- README has the stale sentence at :102 and "never entered it" at :367.
- `FACTORY_DISPATCH` appears nowhere under `factory`, `bin`, `docs`, `dev`, `tests` or `README.md`.
- `tests/factory/test_live_store_guard.py` does not exist yet.

### T-0024-1 / Live-store fence, dispatcher marker and its documents
Depends on: none
Parallel-safe: yes

Parent: T-0024 (#45), approved spec v5 (`.factory/state/specs/T-0024/`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: all of the parent's design:
- A.1 to A.6: the read-only set, the in-flight union, `fence()` with the order location, then marker, then in flight, the call in `main()` before `instance.guard`, the call in `init_cmd` right after `root`, and the new test file.
- B: `'FACTORY_DISPATCH=1'` at the start of `ENV` in `factory/workflows/intake.js` and `factory/workflows/build.js`.
- C: the `docs/design.md` paragraph, the `docs/changelog.md` entry, and the README edits (the opening paragraph of "Where a human decides", the "Built" bullet, the in-flight sentence, the "Current truth" bullet and the status date).
- Tests to change.

Acceptance: run every command from the root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`, and each one through the fresh-HOME wrapper. Run the GIVEN fixture block from "Unmarked writes from inside the target are refused while a run is in flight, init included" once, first.
- NEW: Unmarked writes from inside the target are refused while a run is in flight, init included.
  - WHEN its `t0024-inflight.sh` command with `init`, `ticket new`, `ticket transition` and `decision add`
  - THEN `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`
- NEW: The refusal names the throwaway store and not the marker.
  - THEN `rule=1 state=1 marker=0 json=1 inside=1`
- NEW: A harness acceptance is refused while a run is in flight.
  - THEN `accept=2 store=unchanged`
- NEW: Marked writes from a run's scratch directory or a worktree directory are refused, init included.
  - THEN `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`
- NEW: Writes from a finished run's scratch directory are refused with no run in flight.
  - THEN `idle=1 new=2 decision=2 store=unchanged`
- REGRESSION: Read commands still answer while a run is in flight.
  - THEN `show=0 config=0 log=0 results=0 inside=0`
- REGRESSION: A marked write from the repository root still writes while a run is in flight.
  - THEN `decision=0 finish=0 cleared=1`
- REGRESSION: A throwaway store is not fenced, even from a run's scratch directory.
  - THEN `init=0 new=0`
- REGRESSION: With no run in flight, unmarked commands write as before.
  - THEN `new=0 decision=0`
- REGRESSION: A marked write from a harness checkout with an uncommitted edit is still refused.
  - THEN `exit=2 lock=1 store=unchanged`
- NEW: Every clerk command of both workflows carries the marker.
  - WHEN `node t0024-count.mjs` on each workflow
  - THEN `intake: sent unmarked=0`, then `build: sent unmarked=0`
- REGRESSION: An intake run against a real store reaches its end with its run in flight.
  - WHEN `node t0024-e2e.mjs`
  - THEN `returned=closed stored=closed`
- NEW: The changelog records the guard as its last entry.
  - THEN `CONTIGUOUS`, then `5`
- NEW: The design doc names the marker and the run-directory rule, and no prompt copy changes.
  - THEN `design=1 dirs=1 prompts=0`
- NEW: README tells the operator how to write during a run, first thing under Where a human decides.
  - THEN `first=1 command=1 unnamed=1 export=1 rundirs=1`
  - Note: the scenario reads line 3 of the section, so the bold marker sentence must sit on the line right after the heading's blank line.
- NEW: README says the final verifier run is listed as in flight.
  - THEN `stale=0 listed=1`
- NEW: README no longer says the factory's capabilities never entered the spec store.
  - THEN `bullet=1 stale=0`
- REGRESSION: The guard change adds no whitespace errors.
  - WHEN `git diff --check main...HEAD`
  - THEN `exit=0`
- Gate suite (the parent's intermediate check, not a separate scenario):
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, with pytest's temporary directory under `/tmp`, as the current-truth suite command sets it
  - THEN every test passes, the new `tests/factory/test_live_store_guard.py` included
  - Run it a second time with `FACTORY_DISPATCH=1` exported in the calling shell. Every test must still pass, which shows that the `STRIP` change takes effect.

Tests to change:
- `tests/factory/test_instance.py::test_composed_input_opens_with_the_instance_context`: pass `FACTORY_DISPATCH="1"` to the `run compose` `cli(...)` call.
- `tests/factory/test_instance.py`: add `"FACTORY_DISPATCH"` to the `STRIP` tuple (:21).

Protected paths:
- harness: `factory/cli.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`
- guardrail: `tests/factory/test_instance.py`, limited to the two items under Tests to change

Out of scope:
- `factory/instance.py`. The fence is added in `factory/cli.py`, and it only calls the existing `instance.is_own_store`, `own_state_root` and `caller_cwd`.
- `agents/**`, `factory/prompts/**`, `docs/prompts/**`, `dev/build-harness.spec.md`, `bin/factory`, `.factory/**`, `pyproject.toml` and `uv.lock`.
- `test_init_refused_outside_a_git_work_tree` and the suite's assumption that its temporary directory lies outside every repository.
- Parts B and C of the request (the preamble line and the tripwire): the spec cuts both.
- Logging refused attempts.
- Any call site beyond the two in `main()` and `init_cmd`. The store-branch change (#46, T-0025) rebases on exactly these two.

Coverage map:
| Parent scenario | Sub-ticket |
|---|---|
| Unmarked writes from inside the target are refused while a run is in flight, init included | T-0024-1 |
| The refusal names the throwaway store and not the marker | T-0024-1 |
| A harness acceptance is refused while a run is in flight | T-0024-1 |
| Marked writes from a run's scratch directory or a worktree directory are refused, init included | T-0024-1 |
| Writes from a finished run's scratch directory are refused with no run in flight | T-0024-1 |
| Read commands still answer while a run is in flight | T-0024-1 |
| A marked write from the repository root still writes while a run is in flight | T-0024-1 |
| A throwaway store is not fenced, even from a run's scratch directory | T-0024-1 |
| With no run in flight, unmarked commands write as before | T-0024-1 |
| A marked write from a harness checkout with an uncommitted edit is still refused | T-0024-1 |
| Every clerk command of both workflows carries the marker | T-0024-1 |
| An intake run against a real store reaches its end with its run in flight | T-0024-1 |
| The changelog records the guard as its last entry | T-0024-1 |
| The design doc names the marker and the run-directory rule, and no prompt copy changes | T-0024-1 |
| README tells the operator how to write during a run, first thing under Where a human decides | T-0024-1 |
| README says the final verifier run is listed as in flight | T-0024-1 |
| README no longer says the factory's capabilities never entered the spec store | T-0024-1 |
| The guard change adds no whitespace errors | T-0024-1 |
| Gate suite (Tests to change and the new test file) | T-0024-1 |
