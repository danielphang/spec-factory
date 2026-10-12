Sub-ticket: T-0043.2 (ST-2 of T-0043, spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`). Branch `factory/T-0043.2`, head `41417c1789d40b26370b10f2bdcae6a84f903a9d`, base `a0f77c9`, in worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0043.2`.

## What changed

This change adds `factory stats`, a command that reads one or more factory stores and writes nothing. A store is the factory's file record for one target repository: its role runs, their outputs and an event log. The command prints four Markdown tables, A to D: runs and verdicts, parks, spec defects caught after approval, and cost. It can run while a run is in flight and under a harness lock that names another revision, because it skips the instance lookup, the live-store fence and the lock check, as `paths` does.

**Part B: `factory/stats.py` (new, 235 lines).**
- `report(stores, since, until, transcripts) -> str` prints the header (`# factory stats`, `Stores: ...`, a `Window:` line with the number of in-flight runs left out) and then sections A to D. It uses the spec's headings and column orders.
- Module constants:
  - `CHANGED` is the six verdicts that change an outcome.
  - `BLOCKING` is the regex for a finding line: optional spaces, then an optional `-`, `*` or `1.` marker, then `[BLOCKING]`. Lines containing `RESOLVED` are excluded where it is used.
  - `PARK_RULES` is the step-2 replacement list: run id to `<run>`, `T-…` ticket id to `<ticket>`, and a 7-to-40-character lowercase hex string with a letter to `<sha>`.
- `normalise()` applies the four normalisation steps.
- `_parks()` applies `park.corrected` events dated before `until`, in time order. Each one replaces the reason of the latest earlier park of the same ticket whose current reason equals `previous`.
- Rows follow `cli.ROLES` (triage … verifier), then any other role by name, then the model.
- Section C looks up `spec.added` sources and critic runs over the whole store, with no window. "Approved specs" counts `(store, ticket)` pairs with a spec approval in the window. "Caught downstream" means a section C catch on that ticket that started after the ticket's first approval in the window.
- Section D takes cost from `claude.usage`/`claude.total_cost_usd` in the run record. Without a record it uses `cost.transcript_usage` on the transcript `cost.match_transcripts` places on the run. Without either, the run counts under `none`.
- The implementer gate column uses `cost.gate_failures`. A run is "read" only when it has both a placed transcript and an `input.md` with a gate line.
- Every one of ST-1's functions is called unchanged, and `factory/cost.py` is not edited.

**Part C: `factory/cli.py` (+42/-3).**
- The `stats` subparser takes `--store` and `--transcripts` (both repeatable), `--since` and `--until`.
- `stats_cmd(a)` resolves relative paths from `instance.caller_cwd()`, because `bin/factory` changes into the harness checkout.
- With no `--store`, it reads `FACTORY_STATE`, else the state root of the instance found from the caller's directory.
- Three cases raise `Refused` (exit 2): no store found, a path with neither `runs/` nor `log/`, and a WHEN that does not parse (`stats.parse_when`).
- `main()` runs `stats` with `init` and `paths`, before `instance.require()`, the fence and `instance.guard()`, so `--accept-harness` is ignored.
- `("stats", None)` is added to `READ_ONLY`. The comments on `READ_ONLY`, `fence()` and `main()` are updated.
- `stats_cmd` imports `factory.stats` inside the function, because `stats` imports `ROLES` from `cli`. `factory/store.py` already uses the same local-import pattern.

**Part D (ST-2's share): `tests/factory/test_stats.py` (new, 20 tests).** The tests run the real `bin/factory`, as a separate process:
- each section's rows on a Python port of the acceptance fixture. Store s1's run records have quoted timestamps (YAML reads strings) and s2's are unquoted (YAML reads datetimes).
- the header, the role order, and `unknown` as the writer of a version with no `spec.added`.
- the window: `--since`, `--since` inclusive and `--until` exclusive at an exact start time, and events windowed by `ts`.
- each normalisation step.
- the correction rule: a matching correction, the latest earlier park only, one dated after `--until` (and the same one applied with no `--until`), one whose `previous` matches no park, and one dated before every park.
- the three refusals, relative paths, and `FACTORY_STATE`.
- an own store with a triage run in flight, read from the target and from `runs/<run>/`, under a lock of all zeros, with and without `--accept-harness`. The store is unchanged, and `ticket show` is still refused.

## Acceptance results

Each WHEN was run through the briefing's wrapper with `bash`, from the worktree. The GIVEN blocks were run once, extracted verbatim from input.md.

| Scenario | Before (base `a0f77c9`) | After (`41417c1`) |
|---|---|---|
| NEW: Runs and verdicts … fixed gate failures | `exit=2` | `exit=0` and the seven rows exactly as specified, ending `\| verifier \| opus \| 1 \| 0 \| 1 \| SPEC-DEFECT 1 \| - \| - \|` |
| NEW: A window bounds the count … writes nothing | `exit=2 store=unchanged since=0` | `exit=0 store=unchanged since=1` |
| NEW: Parks are grouped by normalised reason … | `exit=2` | the seventeen lines exactly, `exit=0` through `\| archive refused \| 2 \|` |
| NEW: Each downstream spec catch … | `exit=2` | `exit=0`, `\| run-0007-implementer \| BLOCKED \| T-0001.1 \| 2 \| run-0005-spec_writer \| run-0006-critic \| 1 \|`, `\| run-0011-verifier \| SPEC-DEFECT \| T-0001.1 \| 3 \| human \| none \| 1 \|`, `\| yes \| 1 \| 1 \|`, `\| no \| 1 \| 0 \|` |
| NEW: Cost comes from the run record, else the transcript … | `exit=2` | the eight lines exactly, through `\| verifier \| opus \| 1 \| 120 \| 0 \| 0 \| 0.00 \| record 0, transcript 0, none 1 \|` |
| NEW: Stats reproduces the hand count on the two live stores | `exit=2` | `exit=0`, then the critic, implementer, reviewer and two verifier rows, `\| NEEDS-HUMAN from triage \| 30 \|` and `\| all parks \| 82 \|`, all exactly as specified |
| NEW: Stats reads a live store with a run in flight and an unaccepted harness … | `here=2 inside=2 store=unchanged own=0 locked=2` | `here=0 inside=0 store=unchanged own=1 locked=2` (measured after commit; before commit the GIVEN block's `init` was refused by the uncommitted-edit check, as expected) |
| REGRESSION: Unmarked writes from inside the target are refused … | not run | `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` |
| REGRESSION: The refusal names the throwaway store and not the marker | not run | `rule=1 state=1 marker=0 json=1 inside=1` |
| REGRESSION: A harness acceptance is refused while a run is in flight | not run | `accept=2 store=unchanged` |
| REGRESSION (ST-1): The transcript cost report counts each message once | `\| critic \| fable-5 \| 1 \| 2 \| 310 \| 17 \|` | `\| critic \| fable-5 \| 1 \| 2 \| 310 \| 17 \|` |
| NEW (intermediate): `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_stats.py` | 20 failed (`stats` not a command) | `20 passed in 1.76s` |
| REGRESSION (intermediate) and gate: `uv run --frozen pytest -q -p no:cacheprovider tests/factory` | not run | `577 passed in 348.46s` (exit 0) |
| Gate: `git diff --check main...HEAD` | not run | exit 0, no output |

The fixture scenario and the in-flight scenario were also run once under `zsh -c`. They printed the same first lines and `here=0 inside=0 store=unchanged own=1 locked=2`. `ruff check` on the three files reports `All checks passed!`.

## Tests added/changed

- Added `tests/factory/test_stats.py`, a new file, for part D as listed under What changed.
- Changed: none. No existing test file was touched.

## Known gaps and uncertainties

- **Rules the spec leaves open.** I chose each one below, and no scenario pins any of them.
  - BLOCKING findings and the gate column count runs with a verdict, not killed runs. The column cell reads "not recorded" for runs without a transcript or gate line.
  - "Critiqued by" ignores killed and in-flight critic runs.
  - "Caught downstream" compares a catch's `started` with the ticket's first spec approval in the window.
  - Corrections chain: a second correction matches against the already-corrected reason.
  - The `1.` marker is matched literally, as the spec says, so `2. [BLOCKING]` would not count. On the two live stores no such line exists: `grep -E '^\s*[0-9]+\.\s*\[BLOCKING\]'` over reviewer and critic outputs printed nothing.
  - The ticket-id rule matches `T-<digits>` only, the one prefix `store.next_ticket_id` is called with.
  - The `<sha>` rule is lowercase hex only.
  - An empty verdicts cell prints `-`.
- **Duplicated context-token sum.** Section D adds up a record's input, cache-read and cache-creation tokens inline, which repeats the one-line sum inside `cost.transcript_usage`. `factory/cost.py` exposes no helper for a usage dict, and editing it is out of scope for this sub-ticket.
- **Inputs that would break or crash the command.**
  - A `started` value that does not parse raises `ValueError` and exits 1 rather than skipping the run. Every run in both live stores parses.
  - A park or merge-refusal reason containing `|`, or a merge-refusal reason containing a newline, would break a table row. Park reasons are cut to their first line. No such reason exists in the live stores today.
- **The live-store scenario depends on store contents outside the checkout.** It passed against both stores as they stand today.
- **Not in this change, by design.** The README does not mention `stats` until ST-3 merges, and the documents' read-only list is ST-3's change.
- factory: markers added: none.

## Out-of-scope observations

- `tests/factory/test_instance.py`'s `cli` helper routes every command except `init` and `paths` through `clean_harness_cli.py`. It does not list `stats`. That is harmless, since `stats` skips the lock either way, but the new tests call `bin/factory` directly so that they test the exemption itself.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN lines exactly, both gates passed on `41417c1`, and the new tests failed on the base before the change.
ESCALATIONS: none. The protected paths `factory/cli.py` and `factory/stats.py` are declared by the sub-ticket, and the change does only what parts B and C describe.
