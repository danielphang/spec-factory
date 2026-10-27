# Spec critic, T-0059 (#120), spec v4, round 3

## What I checked

- Cited paths and lines, read from `main` (`db28eb1`): `factory/cli.py` is 899 lines; the `--model` refusal is at `cli.py:183-185`; the implementer worktree and checker `wt` paths are at `cli.py:237` and `:252`; `READ_ONLY` and both `("init", "paths", "stats")` tuples are at `cli.py:863-875`, and every subparser uses `dest="sub"`, so `("truth", "check")` fits `READ_ONLY` as written. `specstore.apply_delta` is at `:385`, `archive` at `:398`, and `lines_outside_fences`, `requirement_blocks`, `parse_delta` and `applies` exist. `drive.py:214` strips only `FACTORY_DISPATCH`. `instance.caller_cwd()` exists. `.factory/instance.yaml` has the two gate commands the spec quotes.
- Store facts: 16 capabilities, 325 scenarios; `openspec/changes/` holds T-0026 and T-0030, both closed, plus the archive with `2026-10-25-T-0057`; the role-escalations fixture passes `--model opus` at its line 28; harness-code's requirement says "under 900"; live-store-guard's two command lists read as the spec says; the harness-docs T-0057 requirement differs from the restated text only in its last sentence and the scenario's growth clause (diffed in my scratch directory).
- README is 1,213 lines; its read-only list, "Counting what each role catches and costs", "## What is built and what is not", "Accepting a harness revision" and "Upgrading the runtime" are where the spec puts them, and the accept-harness sentence in that section is one. `docs/design.md` has the three paragraph openers. The changelog's last entry is 78.
- Tests for old behaviour: `test_small_defects.py:99` and `:121` test `init`, `paths` and `stats` by name; `test_stats.py:419-425` tests `stats` alone; nothing enumerates `READ_ONLY`, counts `cli.py` lines or reads this repo's `.factory/instance.yaml`. "Tests to change: none" holds.
- Acceptance commands run as written from `~/dev/spec-factory` under a fresh HOME: the `cli.py` count prints `899 3`; the gate's last line prints the suite entry, as the Acceptance says; the restated T-0057 scenario prints `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, `CONTIGUOUS`, `entries=1 terms=3`, and `git diff --numstat 7bfbe8f^1 7bfbe8f -- README.md` is `8 7`, as the Evidence says.
- Approved changes not yet archived: none, so no scenario has a merge-order dependency.
- Hand-counted the fixture truth's expected results (16 scenarios; 11/2/3 on `main`, 10/2/4 on the checker's and implementer's checkouts, 10/2/4 with `slow-marker` skipped, folded ids `T-0001, T-0002` on the ticket checkouts and `T-0002` alone on `main`). They follow from design part A and the fixture's ticket statuses.
- Not checked: the wall-time and pass/fail figures, which need the prototype or the built command; the verifier measures them.

## Findings

[SHOULD-FIX] 6 Evidence, first paragraph; Operator steps; Problem, third paragraph
Problem: Three system-specific terms reach the operator unglossed: "design part D" (and "design part A" in the next paragraph) for the lettered parts of this spec's Proposed change, `gate_commands` in the operator step with no word that it is the list in `.factory/instance.yaml`, and "the harness" and "the instance" in the Problem's third paragraph.
Evidence: Read as the gate reader the rubric names. The Problem glosses factory, store, current truth, capability, scenario, verifier and merge gate, but none of these three. By the rubric's letter the first two are in a section's first paragraph and would be BLOCKING; I am not blocking on them because this is round 3 of a spec whose last two revisions the operator directed in person, each fix is a few words, and nothing else in these sections needs a translator.
Suggested fix: write "part D of the Proposed change below" on first use, "`gate_commands`, the gate's command list in `.factory/instance.yaml`" in the operator step, and gloss harness (the factory's code) and instance (one repository's copy of the factory, configured in `.factory/instance.yaml`) where the Problem first uses them.

[NIT] 1 Evidence, "Nothing replays current truth" and design part C
Problem: Two `factory/compose.py` line citations are off: the `{integration}` replacement is `gate_commands()` at `compose.py:109-116`, not `:92-99` (which is gate-entry validation), and the verifier's input is built around `compose.py:359-374`, not `:354` (the planner's sub-ticket list).
Evidence: `git show main:factory/compose.py`, lines 90-100, 109-117 and 352-375.
Suggested fix: change the two line numbers.

[NIT] 4 Design part A, "Inputs" and "Folding"
Problem: Part A resolves the checkout path but says nothing about resolving the store path, and the worktree and `runs/<run>/wt` tests compare the two, so a store given through a symlink (as the Evidence's own clones were) would silently fold nothing.
Evidence: The live store is a plain directory, so the gate entry is unaffected today; the acceptance fixture passes an already-resolved `$S`.
Suggested fix: add "resolved" after `--store PATH` in the Inputs bullet.

## Prior findings (round 2, as the Responses section states them)

- [BLOCKING] 5 T-0057's growth scenario fails under the replay: RESOLVED. The restated scenario measures across T-0057's own merge commit, prints `growth=ok` on `main` today (I ran it), and is the only clause of the requirement that changed; the Acceptance labels it REGRESSION with the failing old form named.
- [SHOULD-FIX] 1 Stale `main` and counts: RESOLVED. Figures are at `7bfbe8f` and `db28eb1`, `main`'s tip; T-0057 is closed and archived; 325 scenarios in 16 capabilities matches the store.
- [SHOULD-FIX] 2 Every figure came from `main`: RESOLVED. Branch figures and the nested gate-commands run are given, with listings named; I could not re-run the prototype.

## Out-of-scope observations

- Three scenarios in the four capabilities the nested gate-commands scenario replays need `node` on `PATH`; the scenario says so. A machine without it fails that scenario in every gate, which Risk already covers.

STATUS: APPROVE
CONFIDENCE: high, every cited path, count and acceptance command I ran matched the spec; the timing figures rest on the writer's listings, which the verifier re-measures
ESCALATIONS: none
