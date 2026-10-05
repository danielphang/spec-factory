Sub-ticket: T-0028.1 (parent T-0028, approved spec v1, `.factory/store/specs/T-0028/v1.md`). Branch `factory/T-0028.1`, base `a69aaf4`, head `a074e95923a5d59d40dd408fad22b302b37783df` (3 commits).

Commit: a074e95923a5d59d40dd408fad22b302b37783df

## What changed

Two pieces of redundant work are removed. A spec that needs only one sub-ticket now skips the planner run, the agent that would otherwise split it. A sub-ticket's checkers, the reviewer and verifier, now skip any check command whose declared files the change does not touch. No repository's check configuration changes, so nothing is skipped until an operator scopes a command.

**A. Gate commands (the repository's own checks) may declare the paths they cover.**
- A.1 `factory/compose.py` `gate_entries(cfg)`: reads each `gate_commands` entry as a string, or as a `{command, paths}` mapping. Absent or null counts as empty. The four malformed cases from the spec are refused, naming `gate_commands entry <index>`, and each refusal says that a command that always runs omits `paths`. `gate_commands(cfg)` keeps its signature and its `{integration}` substitution, and now reads through `gate_entries`.
- A.2 `compose.gate_skips(cfg, repo, base, head)`: runs `git diff --name-only base...head -- <paths>` per scoped entry. An empty result gives a `{command, status: SKIPPED, reason}` entry. A git error is refused through `gitops.git`.
- A.3 `factory/cli.py` `run_start`: for the three build roles, `compose.gate_entries(cfg)` runs before `tripwire.baseline`, so a malformed entry refuses with exit 2 before a run id is reserved. `_start_build_run` sets `meta["gate_skipped"]` from `gate_skips` for a reviewer or verifier run that is not a parent close, before the detached worktree is added, and sets `[]` for every other build run.
- A.4 The "Where you work" block in `compose.py` lists only the commands not skipped. The sentence ends `none (every gate command is skipped below)` when all are skipped. One `SKIPPED by the harness for this diff, do not run: ...` line follows for each skipped command. A skip matches only a scoped entry (`paths is None or raw not in gone`), so an unscoped copy of a skipped command still runs. With no `paths` in the instance, the text is byte-identical to before: `test_run_isolation.py::test_implementer_gate_commands_come_wrapped` passes unedited.
- A.5 `results_record`: for an unkilled verifier whose `runs/<run>/meta.yaml` has a non-empty `gate_skipped`, the `ci` row also gets `skipped:`. `store.record_result` gains `extra: dict | None = None`. The `ci` status is still parsed from `Gate suite:`.
- A.6 `factory/instance.template.yaml`: a comment above `gate_commands: []` gives the two forms, the pathspec semantics and the exclude-form advice. The value stays `[]`, and `test_instance.py` passes unedited.
- A.7 New `tests/factory/test_gate_paths.py`, with 26 tests.

**B. A spec that needs one sub-ticket skips the planner.**
- B.1 `factory plan whole-spec PARENT` (`plan_whole_spec` in `cli.py`).
  - Refusals: it refuses a parent that is not `ready-for-planner` (`<id> is <status>, not ready-for-planner`), has a run in flight, or has no approved spec.
  - Planner needed: `_planner_needed` returns the first of four reasons, in the spec's order. If one holds, it prints `"planner": "needed"` with the reason and writes nothing.
  - Change folder: under an active spec store, a missing change folder is refused with `spec tasks`' wording.
  - Planner skipped: otherwise it creates `<id>.1` (`label: whole-spec`, source `plan:whole-spec`, `ready-for-implementer`) with the B.1 text and one `- <name>` line per scenario. It writes the same text to `plans/<id>.md` and sets the parent's `plan`. With a spec store, it also writes `tasks.md` and logs `tasks.written`. It logs `plan.skipped` and prints `"planner": "skipped"`.
  - Refactor: the record-writing loop of `subticket_add` moved into `_create_subtickets`, which both commands call. `subticket_add`'s behaviour is unchanged.
- B.2 `factory/workflows/build.js` phase 1 first runs a clerk command (one store-CLI call run by a small agent) for `plan whole-spec`.
  - A refusal parks the parent with `harness-bug: plan whole-spec: <stderr>`.
  - `skipped` logs the skip and runs no planner.
  - Any other success runs the unchanged planner block, now inside an `else`.
  - Both paths then `transition planned`.
- B.4 New `tests/factory/test_whole_spec_plan.py`, with 18 tests. It includes the parent-close reuse case: the whole-spec sub-ticket's VERIFIED run gets `reuse` from `ticket parent-check`. It is built with `test_parent_close_reuse.py`'s `_build` and `_parent_verifier_runs` helpers.

**C. Documents.**
- C.1 `docs/design.md`: the routing-table row "Human spec gate | Approved" names the whole-spec path, its four conditions, `factory plan whole-spec` and `plan.skipped`. Row 11 (Gate runner) gains the paths and SKIPPED sentences. The `tasks.md` author becomes "Planner, or the harness when it skips the planner". No prompt block changed.
- C.2 `docs/changelog.md` entry 56 covers A and B. It names `paths`, SKIPPED, `plan whole-spec`, NEEDS-SPLIT and seams, and records that part A overturns T-0016's cut.
- C.3 `dev/build-harness.spec.md`:
  - The command list in part B adds `factory plan whole-spec PARENT`.
  - Part H phase 1 starts with that clerk command and its three outcomes.
  - The part L `ci` row paragraph adds `skipped:`.
- C.4 `README.md`:
  - "How a ticket moves" describes the whole-spec path, and the stand-alone "The build workflow runs the planner, which ..." sentence is gone.
  - Step 3 of "Adopting the factory in a repo" explains `paths`.
  - The "Build, local-only" bullet describes SKIPPED.

## Acceptance results

Every command below ran from the worktree under the fresh-HOME wrapper, with `TMPDIR` set to this run's scratch directory. Each WHEN was extracted verbatim from the change folder's spec files into `scratch/acc/NN.sh`, and the fixtures were written by their verbatim `cat > ... EOF` blocks. "Before" is base `a69aaf4`; "after" is `a074e95`.

| Scenario | Label | Before | After |
|---|---|---|---|
| scoped command skipped for a diff touching none of its paths | NEW | `compose=1 run=0 skipped=0 meta=0` | `compose=0 run=1 skipped=1 meta=1` |
| diff touching a scoped command's paths runs it | NEW | `compose=1 run=0 skipped=` | `compose=0 run=1 skipped=0` |
| command with no paths runs on every diff | REGRESSION | (`compose=0 run=1 skipped=0`) | `compose=0 run=1 skipped=0` |
| skipped command recorded on the gate result; merge needs a passing gate | NEW | `FAIL: merge=2 recorded=no` / `PASS: merge=0 recorded=no` | `FAIL: merge=2 recorded=yes` / `PASS: merge=0 recorded=yes` |
| implementer still given every gate command | NEW | `compose=1 both=0 skipped=` | `compose=0 both=1 skipped=0` |
| malformed gate entry refuses a checker's run start, no run | NEW | `exit=0 new_runs=1 named=0` x2 | `exit=2 new_runs=0 named=1` x2 |
| one-sub-ticket spec becomes that sub-ticket, no planner | NEW | `exit=2 planner= subs=T-0001.yaml ` / `state= "ready": [] names= logged=0` | `exit=0 planner=skipped subs=T-0001.1.yaml T-0001.yaml ` / `state=ready-for-implementer "ready": ["T-0001.1"] names=2 logged=1` |
| split spec / already-planned parent still goes to planner | NEW | `exit=2 planner= subs=T-0001.yaml logged=0` x3 | `exit=0 planner=needed subs=T-0001.yaml logged=0` x3 |
| whole-spec step refuses a parent not ready for its planner | NEW | `exit=2 named=0 subs=T-0001.yaml ` | `exit=2 named=1 subs=T-0001.yaml ` |
| qualifying spec reaches implementer with no planner; refusal parks | NEW | `start: planner` / `park: harness-bug: unknown STATUS READY-FOR-REVIEW from planner` / `start: planner` / `park: harness-bug: unknown STATUS undefined from planner` | `start: implementer` / `start: reviewer` / `start: verifier` / `park: stub stop` / `park: harness-bug: plan whole-spec: T-0001 has no approved spec` |
| spec that needs the planner still gets one | REGRESSION | (`start: planner` / `park: harness-bug: subticket add: stub stop`) | `start: planner` / `park: harness-bug: subticket add: stub stop` |
| changelog records the lane as its last entry | NEW | `CONTIGUOUS` / `1` (spec expected `0`; see Known gaps) | `CONTIGUOUS` / `5` |
| design doc, build spec, README describe both skips; no prompt copy changes | NEW | `design=0 gate=0 build=0 readme=0 skipped=0 stale=1 prompts=0` | `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0` |
| no whitespace errors | REGRESSION | (`exit=0`) | `exit=0` |

The two REGRESSION scenarios and the whitespace check also printed the expected text on the base, as the "before" column shows.

The intermediate checks, both REGRESSION, ran on `a074e95`:
- `(git diff --name-only main...HEAD -- .factory | grep -c .)` printed `0`: the branch changes nothing under `.factory/`, so this repository's gate configuration is untouched.
- Gate `(export HOME=...; git diff --check main...HEAD)` exited 0 with no output: the branch adds no whitespace errors.
- Gate `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `354 passed in 302.88s`. That count includes `test_run_isolation.py` and `test_instance.py`, both unedited.

## Tests added/changed

- Added `tests/factory/test_gate_paths.py` (26 tests). They cover the scoped skip, its exact SKIPPED line and the `meta.yaml` entry, and a touched scope running its command. They cover an exclude-only pathspec (`:(exclude)docs/`), which skips a docs-only diff and runs on a `src/` diff and checks the all-skipped `none (...)` text. They check that the implementer gets every command, that the `ci` row's `skipped:` list appears with PASS and with FAIL, and that a row with no skip has no `skipped` key. They check that a malformed entry refuses implementer, reviewer and verifier run starts with no new run. They cover each of 12 malformed shapes by index, null, absent and unscoped-mapping configurations byte-equal to the string form, and an unscoped copy of a skipped command that still runs. They are black-box through `bin/factory`, because `tests/factory/` shadows the `factory` package on import.
- Added `tests/factory/test_whole_spec_plan.py` (18 tests). They cover:
  - the skip itself: the sub-ticket record, text, plan file, log event and ready list;
  - `tasks.md` and `tasks.written` under a spec store, and the missing-change-folder refusal with the store unchanged;
  - NEEDS-SPLIT and three seam headings, which all report `needed` and write nothing;
  - text that names seams in no `##`/`###` heading, which does not trigger: `####`, a fenced heading, `Seamstress`, prose, and a `### Requirement:` line;
  - an earlier planner run, and an existing sub-ticket;
  - the three refusals: wrong state, run in flight, no approved spec;
  - parent-close reuse with no planner run.
- Both files fail on base `a69aaf4`. The two files copied into a plain `git archive` export of the base printed `43 failed`, which was every test at that time. The 26th gate-paths test, added later, failed with only the A.4 matching fix stashed (`1 failed`).
- No existing test was changed.

## Known gaps and uncertainties

- **One NEW check printed a different "before" value than the spec recorded.** On this base the changelog check printed `CONTIGUOUS` then `1`, where the spec's verification.md says `0`. The spec was written when entry 52 was last. Entry 55 has since landed, and it contains the word `paths`. The check still failed before the change, because 1 is not 5, so I treated this as drift from `main` moving rather than a spec defect.
- **`factory/store.py` is touched, and the spec's Risk list does not name it.** A.5 explicitly requires `store.record_result` to gain `extra`. That is a two-line change in `factory/store.py`, which is under the protected `factory/**`. See ESCALATIONS.
- **The README now describes behaviour that has not run on a real ticket.** Its "Ground truth only" rule says such behaviour belongs under "Where this can go", but C.4 requires the present-tense description in "How a ticket moves". I followed the spec and used the README's existing pattern: "is tested, and has not yet run on a real ticket" for the planner skip, and "is tested, and no repo's configuration uses it yet" for the gate skip.
- **The README status date is unchanged.** It already reads 2026-10-04, today, so there was nothing to bump.
- **Line anchors differ from the spec.** The C.3 edits landed at the command list in part B (around line 206), the part H phase 1 text (around line 284) and the part L paragraph (around line 320). The text matched the spec's description at each place.
- **A skipped command is matched by its command text.** Two *scoped* entries with the same command text and different paths would both drop out of the run list if only one is skipped. An unscoped duplicate is safe and tested. I judged the scoped-duplicate case too unlikely to need per-index bookkeeping, and I did not add a marker for it.
- **A skipped command is shown as written.** A SKIPPED line shows `{integration}` unexpanded, because A.2 says to use the command as written.
- **The build-script scenarios are acceptance-only.** They run under node with the T-0023 stub harness, as T-0023 decided, and the pytest suite does not cover them.
- **Exclude-only pathspecs depend on git.** They rely on git treating a pathspec list with no positive entry as matching everything else. The exclude test exercises this on the local git; I did not check other git versions.
- factory: markers added: none.

Callers of the changed functions, found with `grep -rn` over `factory/` and `bin/`:
- `gate_commands` has one caller, `compose.compose`.
- `store.record_result` has two callers, both in `results_record`. Only the `ci` call passes `extra`.
- `_create_subtickets` is called by `subticket_add` and `plan_whole_spec`.
- `gate_entries` is called by `gate_commands`, `gate_skips`, `compose` and `run_start`.
- `gate_skips` is called by `_start_build_run`.

## Out-of-scope observations

- `factory/workflows/build.js` `meta.phases[0].detail` still reads "planner decomposes the pinned spec into sub-tickets". B.2 says nothing else in the script changes, so I left it.
- `dev/issues.md` row 48 still says "T-0028 (spec approved; queued)". The operator updates it at merge.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command prints its expected text on the final head, and both gates pass there (354 tests).
ESCALATIONS:
- `factory/store.py` (protected, class harness) is changed although the spec's Risk list does not name it. The change is the two-line `extra` parameter on `store.record_result` that design part A.5 explicitly asks for. No other code in `store.py` changed. Decide at the gate: accept it as part of A.5, or ask for the row to be written another way.
