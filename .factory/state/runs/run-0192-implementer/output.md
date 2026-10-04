Sub-ticket: T-0021.1 (parent T-0021, issue #35). Branch `factory/T-0021.1`, commit `82d516b` on base `a32f90e`, worktree `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0021.1`.

## What changed

Every run now gets its own directory for temporary files. A run is one start of a role (one of the factory's agents) on one ticket, and the store is the factory's on-disk record of tickets and runs. The new directory is `runs/<run id>/scratch/` in the store. The run's input names it, every role's prompt tells the agent to use it, git ignores it, and the harness deletes it once the ticket moves on to a new state. It is kept while the ticket is parked, which means stopped for a human.

- **A. Run start** (`factory/cli.py` `run_start`, `factory/store.py`). After `meta.yaml` is written, `run_start` now calls `store.ensure_gitignore(root)` for every role and creates `runs/<id>/scratch/`. Before this change it did that only when a tripwire baseline existed. Every guard runs before this point, so a refused start still writes nothing. `STORE_GITIGNORE` gains a comment line and `runs/*/scratch/`. `ensure_gitignore` writes the full commented block only when the file is absent or empty. Otherwise it appends only the lines the file lacks, so the operator's own lines and comments stay. It now writes through `write_text`, as `docs/coding.md` rule 1 asks. Its callers are `cli.py` `_start_build_run`, `run_start` and `init` (`:856`); for all three, the only change is the dedupe. I left the call in `_start_build_run` in place, because it runs before that function creates any worktree.
- **B. Input** (`factory/compose.py`). Directly after Running code, every role's input gets a `## Scratch directory` section with the text from part B. The path is `root / "runs" / run_id / "scratch"`. It is not added to `input_sources`.
- **C. Preamble.** The SCRATCH FILES block, taken verbatim from part C, sits between RUNNING CODE and GUARDRAIL PATHS in `docs/design.md`, `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md`. The precedence clause is on one line, and the longest line is still 79 characters.
- **D. Clearing** (`factory/store.py`). Before writing, `save_ticket` reads the ticket's stored status. If a stored status existed and the new status is different and is not `parked`, it calls the new `clear_scratch(root, tid)`. That function walks `runs/*/scratch` and removes the directory of each run whose `meta.yaml` names that ticket and has `finished` set. If a scratch path is a symlink, only the link is removed, never its target. Callers of `save_ticket`, found by grep: 19 call sites in `factory/cli.py`, plus `store.park_ticket`, which `ticket park` and `tripwire.py:102` use. Putting the check in the one place that writes a ticket record covers every state change without editing any of those callers.
- **E. Documents.**
  - `docs/design.md`: a new "Scratch directory per run" paragraph after "Tripwire on live files".
  - `docs/changelog.md`: entry 50, which mentions #35, placed before `Declined:`.
  - `dev/build-harness.spec.md`: the `factory run start` bullet and after-run item 6 now mention `runs/<run_id>/scratch/`.
  - `README.md`: the "One caveat until #35 lands" sentence is replaced by one sentence that ends "this is tested but has not yet run on a real ticket", the same pattern the README's Tripwire entry uses. #35 moves to "Related work and history".
- **F. Tests.** New file `tests/factory/test_run_scratch.py` with 12 black-box tests through `bin/factory`.

## Acceptance results

Every command was run verbatim through the wrapper from the worktree root, saved as script files and run with `bash` (and with `zsh` where noted).

| Scenario | Kind | Before (`a32f90e`) | After (`82d516b`) |
|---|---|---|---|
| two runs, separate scratch | NEW | `run-0001-triage dir=no heading=0 own=0 other=0`, and the same for run-0002 | `run-0001-triage dir=yes heading=1 own=1 other=0`, `run-0002-triage dir=yes heading=1 own=1 other=0` (bash and zsh) |
| system prompt carries the rule | NEW | `0` | `1` (bash and zsh) |
| three preamble copies identical | REGRESSION | — | `SAME` |
| scratch file ignored by git | NEW | `untracked_scratch=1` | `untracked_scratch=0` |
| existing `.gitignore` gains only the missing line | NEW | `1 1 1 0` | `1 1 1 1` |
| moving a ticket clears its finished run's scratch only | NEW | `after_finish A=kept` / `after_move A=kept B=kept` | `after_finish A=kept` / `after_move A=removed B=kept` |
| parked ticket keeps scratch | NEW | `parked=kept` / `resumed=kept` | `parked=kept` / `resumed=removed` |
| documents carry the change | NEW | `1 0 0` | `0 1 2` |
| harness suite | REGRESSION | — | `215 passed in 143.46s`, exit 0 (this was also the gate run) |
| refused `run start` leaves no `runs/` entry | intermediate, NEW | — | `uv run … tests/factory/test_run_scratch.py`: `12 passed`. `test_a_refused_run_start_writes_no_run_and_no_scratch` moves T-0001 to `ready-for-spec-writer`, then starts a triage run. It asserts exit 2, no entry under `runs/` and no `scratch` anywhere in the store. |
| edited test keeps its point | intermediate, REGRESSION | — | `-k test_no_tripwire_key_writes_and_prints_what_it_did_before`: `1 passed`. `git diff -U0 main -- tests/factory/test_tripwire.py` shows one hunk only, `@@ -230,2 +230,2 @@`. |

Gates, exactly as written, on `82d516b`:

- `git diff --check main...HEAD` exited 0 with no output.
- The suite printed `215 passed` and exited 0 (203 existing tests plus 12 new).

## Tests added/changed

- **Added: `tests/factory/test_run_scratch.py`**, 12 tests. They cover:
  - each run gets its own scratch directory, and its input names only that one, in the exact section text, directly after Running code, and not as a source;
  - the system prompt holds the rule once, between RUNNING CODE and GUARDRAIL PATHS;
  - the rule is in all three preamble copies;
  - a refused start writes nothing;
  - git ignores files under scratch;
  - a new `.gitignore` is the full block, written once over repeated starts;
  - an existing `.gitignore` keeps its own lines and gains only the missing ones, including when its last line has no final newline;
  - a status change clears a finished run's scratch, but not the scratch of a run still in flight on the same ticket or of another ticket's run, and leaves the run's other files alone;
  - park keeps scratch and resume clears it;
  - `ticket set status=` to the same status clears nothing, and to a new status clears;
  - a symlinked scratch is unlinked and its target survives.

  Before the change, 10 of the first 11 tests failed. The refusal test passed already, as a guard test should. I also checked the symlink test against a mutation: with the symlink branch removed, it fails (`1 failed, 11 passed`). I then restored the file with `git checkout`.
- **Changed: `tests/factory/test_tripwire.py:230-231`**, the one test listed under Tests to change. The expected listing is now `["meta.yaml", "output.md", "scratch", "system-prompt.txt"]`. Line 231 now asserts that `runs/*/scratch/` is a line of the store's `.gitignore`. Part A creates both by design. The test still checks that no `tripwire.yaml` is written and that the JSON `run finish` prints is unchanged.

## Known gaps and uncertainties

- One `factory:` marker was added, at `factory/store.py` `clear_scratch`. A plain `shutil.rmtree` fails on a read-only directory inside scratch, such as a Go module cache. If that happens, the ticket's new status is already written, and the command then exits with a traceback. The upgrade trigger is the first run that leaves such a directory; the fix is a chmod-and-retry handler.
- `save_ticket` now reads the ticket file before each write, and `clear_scratch` reads `meta.yaml` only for runs whose scratch directory still exists. The cost grows with runs that never finish, which the parent puts out of scope.
- The README status header already reads 2026-10-04, which is today, so the date bump the parent asks for changed nothing.
- The new README sentence sits above "Where this can go" while saying the feature is untried. The README's "Maintaining this page" rule puts untried features below that heading. I followed the parent's explicit instruction and the precedent of the README's Tripwire entry, which also says "tested, and has not yet fired". The reviewer may judge it differently.
- No test can check that an agent obeys the preamble rule; the parent says the same.
- For transparency: I kept this run's own scenario scripts in my session scratchpad. This run's input has no Scratch directory section yet, because this ticket is the change that adds it.

## Out-of-scope observations

- The "Role-context block" paragraph in `docs/design.md` still ends "Each run leaves its temporary directory behind." That sentence is about the wrapper's throwaway `HOME`, so it stays accurate. A reader may still confuse it with the new scratch directory.
- Neither instance's store `.gitignore` was edited, as the plan requires. Each one is regenerated at its first `run start` after the runtime checkout moves (parent Operator step 2).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN line on the committed head, and both gates passed on it.
ESCALATIONS: none
