## Review of T-0025 spec v3 (round 3, after the spec gate's change request `approvals/T-0025/changes-1.md`)

Reviewed per convergence rules: the nine items of the gate's change request against the text that changed from v2 to v3 (`diff .factory/state/specs/T-0025/v2.md v3.md`), plus the new scenarios. Unchanged text was not re-reviewed except where a changed part depends on it.

### What I checked

- Cited paths (all on `main` at `abaa75a`, same as the spec): `factory/cli.py:544-550` (`merge_cmd` refusal text `head does not contain main`), `:576` (`MAX_CONFLICT_RUNS = 2`), `:592-595` (`ticket_join` conflict decision), `:821-824` (`_git_toplevel`), `:853` (`top = _git_toplevel(...)` in `init_cmd`), `:881-886` (agent-file copy before store writes), `factory/gitops.py:79` (`head_contains`), `factory/instance.py:55-64` (walk-up `find`), `factory/instance.template.yaml:10` (`state_dir: .factory/state`), `docs/design.md:39,58,74`, `dev/build-harness.spec.md:152`, `tests/factory/test_instance.py:193` (suite `init` with `FACTORY_INSTANCE` set). All exist and say what the spec says. `grep -c` of the three `tickets`-branch spellings in the build spec prints `16`, as the spec states; all 16 lines refer to the branch, none to the `tickets/` directory.
- `.factory/store` was never tracked on either integration branch (`git log -1 main -- .factory/store` empty here; same for `feat/lionbot-v3.5` in `~/dev/nanobot-upstream`), so B refusal 7 would not fire on the real migrations.
- Acceptance commands run today under a throwaway HOME, with the fixture files written to this run's scratch directory: "init from a scratch directory inside the store checkout" printed `exit=0 phantom=written store=changed` then `found=` (the phantom is real); "two remotes" printed `exit=0 store=written local_branch=0 names=0,0`; "store migrate carries the store" printed `exit=2` / `branch= same_tree=no scratch= old=kept main_tracks=9 seen_by_main=0` / `state_dir=.factory/state ticket=ready-for-triage`; the design-doc scenario printed `store_branch=0 tickets_branch=2 never_tracked=0`; the README scenario printed `store_branch=0 migrate=0 ffdx=0 premove=0 old_cost=1 old_refs=4`. Each matches the "today" line in verification.md, for the reason stated.
- The in-flight interaction with #45: T-0024 v3 (`.factory/state/specs/T-0024/v3.md:62-63`) lists `ticket show` as read-only and gives the fence's refusal text as `role runs may not write the live store (<store>; in flight: <run ids>)`. So the phantom scenario's `found=ready-for-triage` (a `ticket show` with a run in flight) and the migrate scenario's `names=1` both hold on a base that contains #45.
- The store's `.gitignore` (`factory/store.py:49-52`) ignores `runs/*/scratch/`, so the migrate success scenario's `n.txt` is an ignored file as the scenario assumes, and `same_tree=yes` is reachable.
- "Tests to change: none": the own-store `init` tests in `tests/factory/test_instance.py` (lines 66, 83, 118, 126, 159) assert the `.factory/` listing, agent files and `written`/`created` lists; none asserts the store is a plain directory or that `git status` sees it. `test_instance.py:193` sets `FACTORY_INSTANCE`, which A.1 exempts.

### Gate items against v3

1. BLOCKING phantom `init` → addressed. A.1 refuses when the caller's top level is a `factory-store` checkout and `FACTORY_INSTANCE` is unset; Evidence reproduces the phantom; new requirement and scenario run from `<store>/runs/<id>/scratch` with a run in flight; Risk replaces the false v2 claim. The spec's reason for not taking `--git-common-dir` is correct: for `~/dev/nanobot-upstream` the common dir is `/Users/dphang/dev/nanobot/.git`.
2. Two remotes → A.3.2 refuses and names each `<remote>/factory-store`; scenario added; Decisions records it.
3. Stale Nanobot fact → removed; Operator step 3 now gives the two checks to run before migrating. Observed now: 4 worktrees under that store and 16 uncommitted store files, so the "changing from hour to hour" wording is accurate.
4. Verify the ignored-file copy → B step 4 compares bytes and counts, and undoes worktree and branch on mismatch; C adds a test.
5. `git clean -ffdx` → Evidence, Risk, README how-to and the `ffdx=1` check.
6. Worktree step before any instance write → Part A is in code order; Decisions records it.
7. Pre-move checkout → README how-to with the words "from before the move" (`premove=1`), and Risk.
8. Nanobot `protected_paths` → Operator step 3; its `infra` list today names five paths and no store path (read from `~/dev/nanobot-upstream/.factory/instance.yaml`).
9. Rebase on #45 → design preamble, A.2, B's fence note, Risk and the changelog number 53. The changelog scenario does not pin the number, so a different landing order does not break it.

### Findings

[NIT] 2 specs/store-setup/spec.md, scenario "store migrate refuses an uncommitted store and a run in flight"
Problem: On the real base the in-flight half is answered by #45's fence, not by B's refusal 4, which only a marked call reaches; the scenario passes either way but does not exercise refusal 4.
Evidence: T-0024 v3 refusal text names the run ids (`.factory/state/specs/T-0024/v3.md:63`); B says "Refusal 4 below covers a marked call"; C says the suite marks such tests.
Suggested fix: None required; the suite test in C covers the marked path. Optionally say in the scenario's lead-in that the in-flight half is #45's refusal on an unmarked call.

[NIT] 2 specs/store-setup/spec.md, scenario "init refuses a once-tracked store path and writes nothing"
Problem: `names_path=1` counts stderr lines containing `.factory/state`, so a refusal message split over two lines that both name the path prints `2`.
Evidence: `Refused` prints its text on one stderr line today (`factory/cli.py:1205-1206`); A.3.1's message is described as naming the path, the commit, the hazard and a request for another `state_dir`, which an implementer might wrap.
Suggested fix: Say in A.3.1 that the message is one line, or change the check to `grep -c '\.factory/state' | awk '{print ($1 > 0)}'`.

[NIT] 3 design.md D, `dev/build-harness.spec.md` bullet
Problem: The `old_name=0` check forces the closed amendment record at `dev/build-harness.spec.md:533` ("F FIXED. The store branch is `tickets` (was `factory/state` ...)") to be rewritten, which edits a historical log line.
Evidence: `grep -n` of the three spellings; line 533 is in the amendments section, the other 15 are live text.
Suggested fix: Accept as is (the line still reads truthfully as "is `factory-store` (was `factory/state`)") or let D say that line gets "(now `factory-store`)" appended and exclude it from the count.

### Prior findings

- Round 2 [NIT] `old_refs` alternative `at `.factory/state/`` constrains the how-to's phrasing → UNRESOLVED, still a NIT. The writer kept the regex; D's how-to bullet still permits naming the old path, and the implementer can write it without a preceding "at". Not blocking.
- Round 1 and 2 BLOCKING / SHOULD-FIX items were all RESOLVED in round 2 and the text they covered is unchanged in v3.

### Out-of-scope observations

- The Nanobot instance's `protected_paths.infra` does not cover `.factory/state/**` today either, so its live store is unprotected until the paired ticket runs. Step 3 names the new path; the paired ticket could also add the old one while the migration waits.

STATUS: APPROVE
CONFIDENCE: high, every gate item is answered in the changed text, each NEW scenario I ran fails today for the stated reason, and the #45 interaction holds against T-0024 v3's refusal text and read-only list.
ESCALATIONS: none
