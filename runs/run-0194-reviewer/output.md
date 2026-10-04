Commit: 82d516be16b1e7590150012e0299669604b4e9a7 (branch `factory/T-0021.1`, base `a32f90e8495bb8574110954fd9b18767ea6a0d41`)

## What I checked, in the role's order

1. Test integrity. `git diff --name-only a32f90e HEAD -- tests/` lists two files: the new `tests/factory/test_run_scratch.py` and `tests/factory/test_tripwire.py`. `git diff -U0 a32f90e HEAD -- tests/factory/test_tripwire.py` has one hunk, `@@ -230,2 +230,2 @@`, inside `test_no_tripwire_key_writes_and_prints_what_it_did_before`: the expected run listing gains `scratch`, and the `.gitignore` assertion becomes "`runs/*/scratch/` is a line of it". That is exactly the edit the parent lists under Tests to change. The test still asserts no `tripwire.yaml` and the unchanged `run finish` JSON keys. No other existing test changed, nothing skipped or weakened.

2. Correctness, against the spec's intent. I read the worktree code (not only the diff) and ran every acceptance scenario verbatim through the wrapper from the worktree root, saved as script files:
   - scenario 1 (bash and zsh): `run-0001-triage dir=yes heading=1 own=1 other=0` / `run-0002-triage dir=yes heading=1 own=1 other=0`: each run's input names only its own scratch directory.
   - scenario 2 (bash and zsh): `1`: the precedence clause is in the system prompt once.
   - scenario 3: `SAME`: the three preamble copies are identical.
   - scenario 4: `untracked_scratch=0`: git ignores a scratch file in a fresh store.
   - scenario 5: `1 1 1 1`: the operator's `# kept` line survives and each ignore line appears once.
   - scenario 6: `after_finish A=kept` / `after_move A=removed B=kept`: finish clears nothing, the move clears only that ticket's finished run.
   - scenario 7: `parked=kept` / `resumed=removed`: park keeps, a human sending it on clears.
   - scenario 8: `0 1 2`: the README caveat is gone, the changelog and build spec carry the change.
   Code paths I traced beyond the scenarios: `factory/cli.py:198-235` creates `scratch/` after every `Refused` guard and after `meta.yaml`, so a refused start writes nothing (and `test_a_refused_run_start_writes_no_run_and_no_scratch` checks that). `store.ensure_gitignore` (`factory/store.py:56-70`) writes the full block only for an absent or whitespace-only file, otherwise appends the non-comment lines the file lacks, through `write_text`, which also creates the store directory, so dropping the old `root.mkdir` is safe for `init` (`cli.py:857`). `save_ticket` (`store.py:106-113`) compares the stored status with the new one; `ticket new` has no stored record (no clear), `run start`/`run finish` leave status unchanged (no clear), `park_ticket` (`store.py:137`) and the tripwire park write `parked` (no clear). `clear_scratch` (`store.py:116-129`) filters on `meta["ticket"] == tid` and a non-null `finished`, unlinks a symlink rather than following it, and touches no path outside `runs/*/scratch`. Every ticket record gets a `status` at creation (`store.py:185`), so the `read_yaml(p)["status"]` lookup cannot miss on a store the harness wrote.

3. Scope. The eleven changed files are the parts A to F the sub-ticket names plus the one listed test edit. No file outside them.

4. Silent behaviour changes. One, and the spec asks for it: every `run start` now writes the store `.gitignore`, so an older store with the three-line block gains `runs/*/scratch/` (without its comment line) at the first start. The parent's Operator step 2 says to commit that. Nothing else a caller would notice: `run start`'s printed JSON, `run finish`, and `run cleanup` are unchanged.

5. Security and data safety. The only deletion is `shutil.rmtree` on `runs/<id>/scratch` of a finished run of the ticket being saved; a symlinked scratch is unlinked, not followed (`test_a_scratch_symlink_is_removed_without_touching_its_target`). No secrets, no new input reaches a shell.

6. Protected paths. The PR touches harness (`factory/cli.py`, `factory/compose.py`, `factory/store.py`, `factory/prompts/preamble.md`) and generated (`docs/prompts/00-preamble.md`). The sub-ticket declares all five, as the parent's Risk list does. Neither instance's store `.gitignore` is in the diff. Listed under ESCALATIONS for the merge gate's human approval.

7. Coding standard. Rule 1: `ensure_gitignore` now calls `write_text` (the standard's own "before" example is this function); `clear_scratch` uses `Path.glob` and `shutil.rmtree`, and the repo has no directory-removal helper to reuse (`gitops.remove_worktree` is a `git worktree remove`, the wrong tool for a plain directory). Rule 2: the PR description names the callers of `ensure_gitignore` (three) and `save_ticket` (19 in `cli.py` plus `park_ticket`), which matches my grep. Rule 3: the one `factory:` marker (`store.py:127`) names its limit and trigger and is listed in Known gaps. Rule 5: `scratch`, `parked`, `run`, `store` are the spec's names. Rule 6: the new tests are black-box through `bin/factory` with `FACTORY_STATE` under `tmp_path`; nothing is patched by name. Lean already.

8. PR description. What changed opens with what the change is and for whom, glosses run, store and parked at first use, and names the mechanism second. Known gaps lists the marker, the per-save read cost, the no-op date bump and the README placement question. Readable by the operator at the gate as written.

Gates on 82d516b, from the worktree, each wrapped as given: `git diff --check main...HEAD` exited 0 with no output; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `215 passed in 165.30s` and exited 0.

## Findings

- [NIT] README.md:298-300: the new sentence states "Each run has its own scratch directory in the store" in the present tense, under "Starting a run", above "Where this can go", while adding "this is tested but has not yet run on a real ticket". The page's own rule ("Ground truth only above 'Where this can go'", README.md:427) puts untried behaviour below that heading. → A first-time reader may take it as what runs today, when the runtime checkout has not yet moved to this revision. The implementer followed the parent's explicit part E instruction and the Tripwire precedent at README.md:347, and flagged the tension in Known gaps, so this is for the operator to rule on, not a change I ask of the code: leave as the approved spec wrote it, or move the sentence under "Where this can go" until the first real run.

No BLOCKING or SHOULD-FIX findings. I looked for and did not find: a path where a parked ticket's scratch is cleared, a path where another ticket's or an in-flight run's scratch is removed, a duplicate ignore line on repeated starts, a write before a guard, or a weakened existing assertion.

Prior findings: none (round 1).

## Out-of-scope observations

- `docs/design.md` §Role-context block still ends "Each run leaves its temporary directory behind", about the wrapper's throwaway `HOME`. Next to the new "Scratch directory per run" paragraph a reader may read it as the scratch directory, which is cleared. The implementer noted the same; a two-word gloss ("its throwaway `HOME`") would remove the ambiguity. Not in this sub-ticket's parts.
- Runs that never finish keep their scratch for ever, as the parent puts out of scope; `save_ticket` re-reads `meta.yaml` for each such run on every status change, so the cost grows with them until the in-flight cleanup work lands.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance scenario printed its THEN line on the committed head when I ran it myself, both gates passed, the only existing-test edit is the one the spec lists, and I traced each clearing and guard path in the worktree code rather than in the diff alone.
ESCALATIONS: protected paths touched, all declared by the sub-ticket and the parent's Risk list: harness (`factory/cli.py`, `factory/compose.py`, `factory/store.py`, `factory/prompts/preamble.md`) and generated (`docs/prompts/00-preamble.md`, re-copied from the design doc block and identical to it per scenario 3). The merge gate needs a human approval for these; the code itself earns APPROVE.
