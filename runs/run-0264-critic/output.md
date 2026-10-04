## Review of the spec (v1): small-change lane (gate-command paths, whole-spec sub-ticket)

No blocking finding. The spec is grounded, its NEW scenarios fail today for the reasons it states, and its two mechanisms lose no refusal the pipeline gives today. Three findings below, none of which an implementer needs answered to start.

### What I checked

- Checkout: `~/dev/spec-factory` at `0b1abad` (the revision the spec's Evidence names).
- Cited paths and symbols, all present: `factory/compose.py` `gate_commands` at lines 44-51 and the "Where you work" block at 175-179; `factory/workflows/build.js` phase 1 at 202-218 with the four refusal sites at 209-214, and the parent-close `reuse` at 253-266; `factory/cli.py` `run_start` (198), `_start_build_run` (238), `subticket_add` (393), `results_record` (483), `spec_tasks` (919, refusal text `has no change folder (no pinned version)` at 929), `_reused_subticket_run` (950), `approve-spec --edit` (1156); `BUILD_ROLES` (25); `store.Refused`, `store.subtickets_of`, `store.record_result`; `specstore.PART_RE`, `is_active`, `lines_outside_fences`, `scenario_names`; `compose._runs_for(root, ticket, role, exclude)`; `gitops.git(cwd, *args)`; `tests/factory/test_harness_lock.py` fixture `clone` (108) and `test_ignored_and_non_harness_changes_do_not_count` (260, relies on `.gitignore`d `__pycache__`); `tests/factory/test_run_isolation.py::test_implementer_gate_commands_come_wrapped` (115); `tests/factory/test_instance.py:108` asserting `gate_commands == []`; `tests/factory/test_parent_close_reuse.py`; `.factory/state/specs/T-0016.md` line 70 carrying the quoted cut; `factory/instance.template.yaml:21` `gate_commands: []`; `dev/build-harness.spec.md` lines 206, 284, 320; `README.md` lines 88, 260, 361; `docs/design.md` row 11 (line 49), routing row (120), `tasks.md` row (85). The changelog's last entry is 52.
- Evidence: the run log has 16 planner `run.finished` events (13 in the table plus the three ESCALATEs the spec names); T-0014, T-0015 and T-0018 read 72 s, 139 s and 302 s, as the table says.
- Acceptance commands run on `main` through the fresh-HOME wrapper, with the fixture files written to this run's scratch directory (`TMPDIR` pointed there):
  - "A spec that needs one sub-ticket becomes that sub-ticket without a planner run" printed `exit=2 planner= subs=T-0001.yaml ` then `state= "ready": [] names= logged=0`; stderr was `invalid choice: 'whole-spec' (choose from add)`. Matches verification.md.
  - "A gate command scoped to paths is skipped …" printed `compose=1 run=0 skipped=0 meta=0`; the compose error was `AttributeError: 'dict' object has no attribute 'replace'`. Matches. In that fixture the verifier's `meta.yaml` carries `base` and `head`, the diff lists only `docs/b.md`, and `git diff --name-only <base>...<head> -- ':(exclude)docs/'` prints nothing with exit 0, so the exclude-only pathspec in Decisions behaves as the spec assumes.
  - "The design doc, build spec and README describe both skips …" printed `design=0 gate=0 build=0 readme=0 skipped=0 stale=1 prompts=0`. Matches.
  - "A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error" printed `start: planner`, `park: harness-bug: unknown STATUS READY-FOR-REVIEW from planner`, `start: planner`, `park: harness-bug: unknown STATUS undefined from planner`. Matches.
- Stub resistance: scenario 2 of gate-commands (diff touches `src/a.txt`) fails a stub that marks every scoped command SKIPPED; the three-case "still goes to the planner" scenario fails a stub that always skips; the ci-row scenario needs both `exit 7` and `SKIPPED` in `ci.yaml`. The build-dispatch stub's unstubbed `plan whole-spec` reply (`{"ok": true}`) routes to the planner, which keeps the current-truth scenario "A refused archive or sub-ticket add parks with the refusal text" passing, as B.2 says.
- Refusal preservation (standing decision T-0022): the B.3 table is accurate against `build.js:209-214` and `subticket_add`. The `clerk()` helper (`build.js:52,56`) fills an empty stderr from the JSON `error`, so B.2's park text matches the expected `park: harness-bug: plan whole-spec: T-0001 has no approved spec`.
- Part C reuse: `_reused_subticket_run` requires one sub-ticket and every `scenario_names` of the approved spec to occur in `subticket.md`; the B.1 text's `- <name>` lines satisfy it.

### Findings

[SHOULD-FIX] 5 Risk, "Overlap with other open tickets"
Problem: The overlap list omits T-0026 (`ready-for-planner`), which edits `factory/workflows/build.js` and `intake.js` to add `log()` lines and agent labels, so its sentence "No ordering is needed with any of them" is made over an incomplete list.
Evidence: `.factory/state/requests/T-0026.md` line 9 names both workflow scripts; `.factory/state/tickets/T-0026.yaml` is `ready-for-planner`; the spec's input names T-0022, T-0025 and T-0027 only. Part B.2 edits phase 1 of `build.js`, where T-0026's part A/B log lines also land.
Suggested fix: Add T-0026 to the overlap bullet with the same resolution (a text conflict in `build.js`, resolved by the catch-up run; the new `plan whole-spec` log line is one of the state-change lines T-0026 asks for).

[NIT] 4 design.md A.4, "none (every gate command is skipped below)"
Problem: When every command is skipped, the verifier is still required to print a `Gate suite:` line (`factory/prompts/verifier.md:38`), and `results_record` writes `ci` FAIL with `missing Gate suite line` when it is absent (`factory/cli.py`, `results_record`), so a verifier that reads "none" as "nothing to report" produces a spurious merge refusal.
Evidence: no scenario covers the all-skipped case, and no instance would reach it after Operator step 3 (the `git diff --check` command stays unscoped). A refusal is gained, not lost, so this is not a safety gap.
Suggested fix: Have the all-skipped sentence end with what to report, for example "none (every gate command is skipped below); report `Gate suite: PASS`", or say in Decisions that the case is left to the verifier's judgment.

[NIT] 6 Evidence, first paragraph; Decisions, bullet 5
Problem: Two system-specific names appear in human-facing sections without a gloss: "spec writer" and "parent" in Evidence's first paragraph (both inferable from the Problem's gloss of planner and sub-ticket), and "the `ci` row" in Decisions bullet 5 (glossed only in Root cause, which the operator is not held to read).
Evidence: Problem glosses planner, sub-ticket, verifier, gate commands and refusal; neither "spec writer" nor "`ci` row" gets a gloss before these uses. Not in a first paragraph for `ci` row; "spec writer" is in Evidence's first paragraph but is self-describing, so I do not block on it.
Suggested fix: "the spec writer, the agent that drafts the spec before the gate" at first use, and "the `ci` row, the stored gate result for a commit" in bullet 5.

### Out-of-scope observations

- `.factory/state/specs/T-0016.md` exists beside an empty directory `.factory/state/specs/T-0016/`; the spec cites the file correctly.
- `_reused_subticket_run` compares the verifier's `base` with `parent_base`, which is set at the first merge (`factory/cli.py:560-561`). If the integration branch moves between the whole-spec sub-ticket's verifier start and its merge, the parent close runs its own verifier. Existing behaviour, and T-0025 is removing the store commits that move it.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high, every cited path and four acceptance commands were checked on `0b1abad` and matched the spec's claims; the one open design point (all-skipped gate) cannot arise with the configurations the spec proposes.
ESCALATIONS: none
