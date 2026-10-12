Critic review of T-0047 spec v1 (split `factory/cli.py` into modules by job). Round 1.

What I checked, on `~/dev/spec-factory` at `6203096` (clean tree, the commit the spec cites):

- Grounding. `wc -l factory/cli.py` = 2020, `factory/*.py` total 5073. An `ast` walk of `factory/cli.py` (script in my scratch directory) gives the same start and end line for every one of the 74 definitions the spec names, in every part A to E and in Evidence. `shutil.copy2(...)` is at `cli.py:1586`; `fence` calls `instance.is_own_store`, `instance.own_state_root`, `instance.caller_cwd` at 1976-1977; the comment `# local: stats imports ROLES from here` is at 1631; the module docstring reads "P0 subset of the build-harness spec, part B/K". `README.md:9`, `:1170-1173`, `docs/principles.md:106-107`, `:164` read as the spec quotes them. `drive.py:39` imports `cli` and uses only `cli.main` (`:60`); `stats.py:23` imports `ROLES`; `__main__.py:1` imports `main`. `tests/factory/clean_harness_cli.py:25-28` and `test_store_migrate.py:155-164` import `factory.cli`, patch `instance.harness_changes` and the global `shutil.copy2`, and call only `cli.main`. The six cited lines of `openspec/specs/harness-code/spec.md` (17, 45, 49, 53, 57, 65) are the only lines of that spec that name `cli.py`.
- Dependency closure of the move. From the same `ast` walk, every top-level name a moved definition uses is either in its new module or in a module that part says it imports from (`common` for `out`, `_rel`, `_add_spec_version`, `fence`, `_in_flight`; `gates` for `_branch_tip`, `undeclared_protected` in `resolve`). No moved definition uses a name that stays in `factory/cli.py`, so no new module needs `factory.cli`. `fence` does not read `READ_ONLY` (only `main` does), so leaving `READ_ONLY` in `cli.py` is consistent. Every name `cli.py` keeps that uses a moved one is listed as an import in the part that moves it (`run_start` → `_check_drift`, `_check_sibling_tests`; `ticket_transition` → `_parent_close_verified`; `spec_add` → `_add_spec_version`; `main` → `fence`; `spec_tasks`, `run_compose`, `run_last_message` → `_rel`).
- Acceptance commands run as written (no test suite): the `cli.py` line scenario prints `2020 3`; the importer grep prints `factory/__main__.py factory/drive.py factory/stats.py` in that order; the harness-docs scenario prints `0 1 0 1 ` (empty last field, as Acceptance says); the importable-entry-points scenario prints `7 True True`; `import factory.drift` fails with `ModuleNotFoundError: No module named 'factory.drift'`; `uvx ruff check --select F factory` prints `All checks passed!`. The six rewritten harness-code checks print `0 2 2`, `0`, `0 1`, `1 1`, `0`, `0 1 1 1` on base, the same as their current forms. The definition script, written to my scratch directory by the spec's heredoc and run through the wrapper, prints `pairs=0 added=0 removed=0 lines=0` and nothing after it.
- The definition script's pairing. The integration branch is `main` itself (`gitops.integration_branch` returns the checked-out branch; the recent merges `Merge factory/T-0046.1`, `T-0045.1-3` are on `main`), and an implementer branch is cut from it at first dispatch (`cli.py:373-390`). So on a later sibling's head, the `Merge factory/T-0047.<n>` pairs and the `(merge-base HEAD main, HEAD)` pair cover disjoint diffs and the line total is not double-counted. The `--grep` pattern matches the harness's merge message form.
- Expected-name lists in the five module scenarios: each matches the part's definition list in count (7, 6, 14, 18, 13) and in `LC_ALL=C` order.
- MODIFIED requirements against the current `harness-code` spec: `diff` shows only the two requirement sentences gaining the "reads the five modules" clause and the six cited WHEN lines gaining the `cat` of the five modules. No other scenario text changed.
- Tests pinning old behaviour: no test reads `factory/cli.py` as a file, globs `factory/*.py`, or names any `factory.cli` attribute but `main` (grep of `tests/`). "Tests to change: none" holds.
- Docs: a grep of `README.md`, `docs/design.md`, `docs/principles.md`, `docs/prompts`, `factory/prompts`, `factory/workflows`, `agents` and `.factory/instance.yaml` for `cli.py` or `factory.cli` finds only the lines the spec already inventories.
- Consistency: "Approved changes not yet archived" is none. T-0048 and T-0049 (ready-for-triage) are docs tickets. The spec has no seam heading and the planner is triggered only by one, by a writer `NEEDS-SPLIT`, or by an earlier planner run (`cli.py:748-764`); either as one sub-ticket or as the request's one-module-per-sub-ticket, the acceptance holds, since the definition script sums every pair.
- Protected paths: the six `factory/*.py` files are declared under Risk. `README.md` and `docs/principles.md` are not protected.

What I could not check: that the suite passes on the split (the implementer and verifier run it), and the one-off failure of `test_build_step_lines_and_the_status_file_name_the_subticket_in_flight` the writer reports; the spec names it as a known flake, and that is enough for the verifier to recognise it.

Findings

[SHOULD-FIX] 6 Problem, first paragraph
Problem: The first paragraph says what is wrong (one 2,020-line file holds almost every command) but not for whom; the cost to build agents and to reviewers of harness changes arrives only in the third paragraph.
Evidence: Writing standard rule 1 ("a reader who stops after the first paragraph can say what the problem is and who has it"). Read as the gate operator, I knew the fact after paragraph 1 and the harm after paragraph 3. I am not blocking on this: the section is short and the answer is two paragraphs down, so the operator can follow it without inferring.
Suggested fix: End the first paragraph with one sentence from the third, for example "An agent asked to change one gate reads all 2,020 lines into its context, and a reviewer has to find the gate among setup and bookkeeping code."

[NIT] 6 Decisions 7 and 9
Problem: `T-0045` is named twice without saying what it is.
Evidence: Writing standard rule 6; the ticket is the one that moved the test suite's shared helpers into `_fixtures.py` (merges `6ac73f1`, `1c5a152`, `5c1c47d` on `main`).
Suggested fix: On first use write "T-0045, the ticket that moved the test suite's shared helpers".

[NIT] 4 Decision 1, `factory/common.py`
Problem: The request put `_run_dir`, `_by`, `_approval_dir`, `_next_n` and `_text_from` in the common module; the spec keeps each where its only callers are, which is the better rule, but states the rule without saying it departs from the request.
Evidence: `.factory/store/requests/T-0047.md`, "Shared small helpers (...) go to one common module"; the `ast` walk shows `_by`, `_approval_dir`, `_next_n` used only by human-decision functions and `_run_dir`, `_text_from` only by functions that stay in `cli.py`.
Suggested fix: Add one clause to Decision 1: "Rejected: the request's wider common list; a helper with callers in one module stays in that module."

STATUS: APPROVE
CONFIDENCE: high. Every cited line, the dependency closure of the move, the acceptance commands that run no test suite, and the diff of the MODIFIED requirements were checked on the cited commit; only the suite result rests on the writer's prototype.
ESCALATIONS: none
