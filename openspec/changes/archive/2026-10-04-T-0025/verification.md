## Acceptance

Captured on `main` at `d2a5143` with a throwaway HOME, running the GIVEN block and then every WHEN above as written under `bash` (round 4: all 17 re-run; every output carried over from round 3 matched, and the two new scenarios printed what is shown below). `d2a5143` does not yet contain #45 (T-0024), which merges before this change, so the verifier's base will. #45 does not change any "today" output below: `store` is rejected by argument parsing before #45's fence runs, and #45 does not fence the phantom `init`, because the instance `init` resolves there is the phantom's, which has no runs in flight and whose own store does not contain the caller. The separate-repository scenario is a new instance in its own repository, which #45 does not fence either. The verifier re-runs each NEW item on its actual base.

- init creates the store on the factory-store branch, out of the integration checkout's sight → NEW. Today it prints `branch=main seen_by_main=6`: the store is a plain directory inside `main`'s checkout, and its six files show as untracked there.
- init on a clone restores the store from the pushed branch → NEW. Today it prints git's `On branch main` and `nothing to commit, working tree clean`, then `exit=1 branch=main restored=1`: the store was already committed on `main` by `git add -A`, so the store commit fails and no store branch exists.
- init on a clone with two remotes carrying the store branch refuses and names both → NEW. Today it prints `exit=0 store=written local_branch=0 names=0,0`: `init` ignores the branch and creates a plain store.
- init from a scratch directory inside the store checkout refuses and leaves the store unchanged → NEW. Today it prints `exit=0 phantom=written store=changed`, then `found=`: `init` builds a phantom instance inside the store, and `ticket show` from the scratch directory then reads the phantom's empty store.
- init from the store checkout on a detached HEAD refuses → NEW. Today it prints `exit=0 detached=yes phantom=written store=changed`, then `found=`: the same phantom, built from a store checkout that is on no branch.
- init in a separate repository under a run's scratch directory still creates its instance → REGRESSION. It prints `exit=0 instance=written live=ready-for-triage` today, and must still print it: a refusal keyed on "the found instance's store contains the top level" without the same-repository check would refuse it.
- init refuses a once-tracked store path and writes nothing → NEW. Today it prints `exit=0 instance=written names_path=0`.
- store migrate carries the store to factory-store at the new path → NEW. Today it prints `exit=2`, then `branch= same_tree=no scratch= old=kept main_tracks=9 seen_by_main=0`, then `state_dir=.factory/state ticket=ready-for-triage`: `store` is not a command (argparse `invalid choice`), and nothing moves.
- store migrate refuses an uncommitted store and a run in flight → NEW. Today it prints `uncommitted: exit=2 names=0 branch=0`, then `in flight: exit=2 names=0 branch=0 new=none`: both exits come from argparse, which names neither the file nor the run.
- A checkout of an older commit leaves the moved store untouched → NEW. Today it prints `live=lost on=main`: no store can be moved, so `.factory/store` does not exist.
- A sub-ticket merges after a store commit → NEW. Today it prints `exit=2 refused=1`: the store commit lands on `main`, and the gate refuses with `head does not contain main`.
- A sub-ticket is refused after a code commit to main → REGRESSION. It prints `exit=2 refused=1` today, and must still print it.
- The design doc names the store branch and the path rule → NEW. Today it prints `store_branch=0 tickets_branch=2 never_tracked=0`.
- The build spec calls the store branch factory-store → NEW. Today it prints `old_name=16 new_name=0`.
- The changelog records the store branch in one contiguous entry → NEW. Today it prints `CONTIGUOUS`, then `0`.
- The README describes the store branch and the move → NEW. Today it prints `store_branch=0 migrate=0 ffdx=0 premove=0 old_cost=1 old_refs=4`: no mention of the branch, the command or either caution, the retired clause is present, and four lines give `.factory/state/` as the store's location (lines 403, 418, 457, 462).
- The store-branch change adds no whitespace errors → REGRESSION. It prints `exit=0` on `main` today.

## Responses

Round 4 answers the spec gate's second change request (`approvals/T-0025/changes-2.md`, from `.factory/answers/design-review-45-46/round-2.md`). Round 3's responses to the first request are in v3.

1. N1 (SHOULD-FIX), settled on #45's side → FIXED, with one correction to the request's premise. I read #45's approved v5 (`.factory/state/specs/T-0024/v5.md`). Its throwaway-store scenario now runs `init` from the target root, so it stays true here. But it is not the case that no #45 scenario runs `init` from inside a run's scratch directory: "Marked writes from a run's scratch directory or a worktree directory are refused, init included" still does (`cd $W && FACTORY_DISPATCH=1 $B init --repo-name x`). Its expected output (`scratch_init=2`, `store=unchanged`, `agents=none`) still holds after this change, because A.1 refuses that `init` with exit 2 before anything is written; only the refusal's text changes. The other four `init` WHENs in #45 run from the target root or a subdirectory of its code checkout, where A.1 does not apply. So "Tests to change: none" holds for #45's scenarios and for this repo's current suite. Risk has a new bullet listing all five, and Tests to change says so. One thing I cannot check yet: #45's suite file is not written. If one of its tests asserts the location rule's message for `init` from a store's `runs/`, it will see A.1's message instead; Tests to change tells the implementer to report it, not edit it.
2. N2: detached store HEAD → FIXED. Reproduced first: with the store worktree detached, `init --repo-name x` from a run's scratch directory still built the phantom (`exit=0 detached=yes phantom=written store=changed`, `found=`; Evidence). A.1 now has a second condition: refuse when `instance.find()` returns an instance whose own store is the top level, or contains it in the same repository. I added the same-repository qualifier to the requested "equals or contains". Without it, `init` in a separate throwaway repository under a run's scratch directory would be refused, and the suite runs 14 `init` calls in fresh repositories under pytest's temporary directory, which a role may place in its scratch (Evidence). The requirement is restated. There is a new NEW scenario, "init from the store checkout on a detached HEAD refuses", and a REGRESSION scenario, "init in a separate repository under a run's scratch directory still creates its instance". Part C names both cases, and a Decisions line records the condition and the rejected unqualified form. Risk states the one case the second condition does not see: a phantom that already exists.
3. N3: rely on #45 for a store with no `tickets/` → FIXED. A.2 now points to #45's part A.2 in one clause and does not restate it.
4. N4: #45's fence call unconditional → FIXED. A.2 says the call comes right after `root` and is unconditional, a no-op on a new instance. The Risk bullet on #45 says the same. Neither ties the call to an existing instance any more.
5. N5: A.3.1's refusal on one line → FIXED both ways. A.3.1 says the message is one line (A.1's two messages are one line each, too), and the scenario's check is now `grep -q`, so a wrapped message still counts once. Today's output is unchanged (`names_path=0`).

## Critic rounds

round 1 · spec v1 · run-0223-critic · REVISE

## Critic review: T-0025 spec v1 (store on its own branch, `factory-store`)

### What I checked

Spot-checks, all from `~/dev/spec-factory` on `main` at `3a3f58c`, with a throwaway HOME:

- Cited code: `factory/cli.py:544-550` is the gate refusal `head does not contain main (...)` behind `gitops.head_contains` (`factory/gitops.py:79`); `ticket_join` at `cli.py:592-595` turns it into a `conflict` decision, `MAX_CONFLICT_RUNS = 2` at `cli.py:576`; `init_cmd` at `cli.py:845`; `gitops.checkout_of` at `gitops.py:92`; `instance.own_state_root` / `is_own_store` at `instance.py:93/105`; `instance.template.yaml:10` is `state_dir: .factory/state`; `cli.py:741`, `:247`, `:259` are as described. All exist and say what the spec says.
- Cited documents: `docs/design.md:39` and `:74` name the `tickets` branch; `:58` is the role-context paragraph; `dev/build-harness.spec.md:152` is the state line; the old-name grep hits 16 lines; `docs/changelog.md` ends at entry 51 before the `Declined:` line; README has the "Maintaining this page", "Where it runs" and "Terms used on this page" sections and 4 `.factory/state` mentions; `.factory/answers/T-0023.3-operator-decision.md` exists; `.factory/context.md` holds the sentence Operator step 2 rewrites.
- Cited figures: `git ls-files .factory/state | wc -l` = 1282; six `resolution: conflict` runs; `a1b2718` and `aeb684d` bring in store files only (the latter under the store's older path `intake/state/`, which the spec's Decisions acknowledge); `89e8b7d` brings in `dev/issues.md` only; run-0212 `wall_s: 251`; `~/dev/nanobot-upstream` commit `6e98ae250` brings in 40 files, all under `.factory/state/` (read only); git 2.54.0. GitHub issue #46 is this request's title and #45 is the role-writes issue, so the spec's numbers are right.
- Acceptance commands run as written (fixture written to this run's scratch directory via `TMPDIR`): "A sub-ticket is refused after a code commit to main" prints `exit=2 refused=1` (REGRESSION holds). "A sub-ticket merges after a store commit" prints `exit=2 refused=1` today, for the reason the spec gives. A control with no commit at all prints `exit=0`, so the fixture itself can merge: the NEW scenario would fail against a stub and pass only when a store commit stops moving `main`. The design-doc and changelog scenarios print `store_branch=0 tickets_branch=2 never_tracked=0` and `CONTIGUOUS` / `0`, matching the verification section.
- The writer's prototypes: the scratch scripts it cites (`scratch/b1.sh` and others) are gone, because the harness cleared run-0222's scratch when the ticket moved on. I re-ran the three claims in throwaway repos: `git worktree add --orphan -b factory-store` with no git identity exits 0 and the integration checkout's status is empty once the path is excluded; `git clean -fdxq` leaves the nested worktree's file in place; at the old path, checking out the pre-move commit overwrote the uncommitted record and checking `main` out again deleted it. All three hold.
- "Tests to change: none": the suite's own-store `init` calls (`tests/factory/test_instance.py`, `test_harness_lock.py`) run in git repos and compare file trees that stay stable with a worktree at the store path; every other case uses a throwaway `FACTORY_STATE` store. I found no test that asserts an own store is tracked on the integration branch.

### Findings

[BLOCKING] 6 Operator steps, step 1
Problem: The first paragraph of Operator steps uses "the runtime" and `--accept-harness` with no gloss, and none of Problem, Evidence or Decisions glosses them earlier; the writing standard's own example for its rule 2 is this very flag.
Evidence: `grep -n -i "runtime\|accept"` over the proposal's Problem, Evidence and Decisions finds neither term; `~/dev/spec-factory-harness/docs/writing.md` §2 uses `--accept-harness` as its "before" case.
Suggested fix: Open step 1 with one sentence of the form "The factory runs each repository from a separate checkout pinned to a harness revision the operator has accepted; after the merge, point that checkout at the merged revision and accept it with `--accept-harness <sha>`."

[SHOULD-FIX] 2 specs/harness-docs/spec.md, scenario "The README describes the store branch and the move"
Problem: `old_cost=$(grep -c 'committing the store' README.md)` must print 0, yet the requirement text and design.md D ask the README to "describe committing the store on its branch", so the natural wording of the new how-to fails the check.
Evidence: `grep -n 'committing the store' README.md` hits only line 306 today, inside the clause D removes ("and committing the store to the same branch moves it too").
Suggested fix: Grep for the retired clause itself, `committing the store to the same branch`, so the check pins the removal and not a phrase the new text needs.

[SHOULD-FIX] 2 design.md D (`docs/changelog.md`) against the scenario "The changelog records the store branch in one contiguous entry"
Problem: The scenario needs the literal words `never tracked` on the entry's line, but D tells the implementer only to name "the never-tracked path rule", so an entry written as D says can fail the check.
Evidence: D's design.md bullet says "Use the words 'never tracked'"; the changelog bullet does not; the scenario greps `'never tracked'` (space) on the entry line.
Suggested fix: Add to the changelog bullet that the entry uses the words "never tracked" and stays on one line, as the design.md bullet does.

[NIT] 2 specs/harness-docs/spec.md, same README scenario, `old_path=0`
Problem: The how-to "Moving an existing store onto its branch" will naturally name the path it moves from, `.factory/state`, which this check forbids anywhere in the README.
Evidence: `grep -c '\.factory/state' README.md` is 4 today; D's rollback steps say "move the directory back" without naming either path.
Suggested fix: Either let D say the how-to names no old path, or narrow the grep to the three places D rewrites ("Where things live", "Related work and history", the "Maintaining" table).

### Notes, not findings

- The writer's prototypes cannot be re-read from the cited `scratch/` files (cleared by the harness), but the Evidence paragraphs quote their outputs and the claims reproduce. A future spec could inline the few commands instead of citing scratch paths.
- The relayed request calls the store-commit issue "45". GitHub #46 carries this request's title and #45 is the role-writes issue; the spec's Out-of-scope and changelog references use the right numbers. No change needed.
- Scope, decisions and consistency look right: the operator's A/B framing is honoured (A rejected as imitation of B), B1 over B2 is argued with evidence and left for the gate, protected paths are declared, and the four seams are named for the planner.

round 2 · spec v2 · run-0226-critic · APPROVE

## Critic review: T-0025 spec v2 (store on its own branch, `factory-store`), round 2

### What I checked

Round 2 scope: my round-1 findings and the text that changed. All from `~/dev/spec-factory` on `main` at `3a3f58c` (unchanged since round 1; `git status` shows only uncommitted store files), with a throwaway HOME and `TMPDIR` set to this run's scratch directory.

- README scenario, as rewritten: prints `store_branch=0 migrate=0 old_cost=1 old_refs=4` today, matching verification.md. The four `old_refs` hits are README lines 403, 418, 457 and 462, the places design.md D now lists. The retired clause is wrapped across lines 306-307, so the writer's point against my suggested single-line grep stands; the `tr '\n' ' '` join is the right fix. The "Where it runs" diagram holds exactly two `state/` labels (lines 186, 191), as D says.
- Operator steps, step 1: the two upgrade commands match README "Upgrading the runtime" (`git -C ~/dev/spec-factory-harness checkout --detach <sha>`, `uv sync --frozen`). Read cold, the paragraph now says what the runtime is, why a merge does not change it, and what `--accept-harness` does. Step 3 glosses "Driver session" and names T-0001.1 as a sub-ticket.
- Risk bullet on T-0024: `run-0224-spec_writer/meta.yaml` is T-0024's second spec round; run-0220's output (its v1 spec) refuses unmarked writes to a live store while a run is in flight there and exempts only a fixed read-only list, so `init` and `store migrate` would fall under it as the bullet says. The standing decisions in `decisions.md` (the `FACTORY_DISPATCH=1` marker) agree.
- Acceptance commands re-run as written: "init refuses a once-tracked store path" prints `exit=0 instance=written names_path=0`; "init on a clone restores the store" prints `exit=1 branch=main restored=1`. Both match verification.md.
- Evidence prototypes, now inlined: I re-ran the orphan-worktree and `git clean -fdxq` claims in this run's scratch. `git worktree add --orphan -b factory-store` with no identity exits 0 and the excluded path leaves `git status --porcelain` empty; after `git clean -fdxq` the B1 store keeps `decisions.md` and the B2 directory is gone. Both match the Evidence paragraphs.

### Prior findings

- [BLOCKING] 6, Operator steps step 1, "the runtime" and `--accept-harness` unglossed → RESOLVED.
- [SHOULD-FIX] 2, README scenario `old_cost` forbids a phrase the new how-to needs → RESOLVED. The writer's evidence against my suggested grep is right (the clause is wrapped), and the join fixes it properly.
- [SHOULD-FIX] 2, changelog bullet in D lacks the literal words "never tracked" → RESOLVED.
- [NIT] 2, README scenario `old_path=0` forbids the old path anywhere → RESOLVED by narrowing to `old_refs`.

### Findings

[NIT] 2 specs/harness-docs/spec.md, scenario "The README describes the store branch and the move", `old_refs`
Problem: The alternative `at `.factory/state/`` still forbids the most natural phrasing in the new how-to and its rollback ("the store back at `.factory/state/`"), which D permits to name the old path.
Evidence: D's how-to bullet says it "may name the old path it moves from"; the regex matches that phrase wherever it appears; today's four hits do not include the how-to because it does not yet exist.
Suggested fix: Add one clause to D's how-to bullet saying the how-to writes the old path without a preceding "at", or names it as `.factory/state` with no trailing slash.

### Notes, not findings

- The relayed operator note calls this issue "45" and frames the choice as "worktree and/or branch". The spec's Responses already record that this request is GitHub #46 and #45 is T-0024's. The spec's B1 (worktree checkout of the branch) and B2 (branch with no working copy) are the operator's two readings of "worktree and/or branch", and B1 is left for the operator to confirm at the gate; option A is recorded as rejected for the operator's stated reason.
- No new issue on unchanged text.

round 1 · spec v3 · run-0232-critic · APPROVE

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

round 1 · spec v4 · run-0237-critic · APPROVE

## Critic review, T-0025 v4 (round 4)

Scope of this round: the second change request (`approvals/T-0025/changes-2.md`, N1 to N5), the text that changed between v3 and v4 (`diff` of `specs/T-0025/v3.md` and `v4.md`), and my own earlier findings. Unchanged text was not re-reviewed.

### What I checked

- Citations, all present at the lines given on `d2a5143`: `factory/cli.py:544-550` (gate refusal text and `head_contains`), `:576` (`MAX_CONFLICT_RUNS = 2`), `:592-595` (`ticket_join` conflict decision), `:821-824` (`_git_toplevel`), `:853` (`top = _git_toplevel(...)` in `init_cmd`), `:741`, `:247`, `:259`; `factory/gitops.py:79` (`head_contains`); `factory/instance.py:55-64` (`find`); `factory/instance.template.yaml:10`; `docs/design.md:39`, `:58`, `:74`; `dev/build-harness.spec.md:152`. Every symbol A.1 and A.2 name exists: `instance.own_state_root` (`instance.py:93`), `instance.repo_root` (`:81`), `instance.is_own_store` (`:105`), `gitops.integration_branch` (`gitops.py:22`), `gitops.checkout_of` (`:92`), `_new_instance_yaml` (`cli.py:828`), `_revision` (`:838`).
- `git diff --stat abaa75a d2a5143 -- . ':!.factory'` prints nothing, as Evidence says.
- Acceptance commands run as written under a throwaway HOME, with `TMPDIR` set to this run's scratch directory:
  - "init from the store checkout on a detached HEAD refuses" (NEW) printed `exit=0 detached=yes phantom=written store=changed`, then `found=`. Matches verification.md. A fix with only A.1's first condition still prints this, so the item discriminates.
  - "init in a separate repository under a run's scratch directory still creates its instance" (REGRESSION) printed `exit=0 instance=written live=ready-for-triage`. An unqualified "store contains the top level" rule would refuse it, since the walk-up from `scratch/other` finds the live instance, so it guards the qualifier the spec adds.
  - The design-doc, build-spec and README `old_refs` commands printed `store_branch=0 tickets_branch=2 never_tracked=0`, `old_name=16 new_name=0` and `old_refs=4` (README lines 403, 418, 457, 462). All match.
- N1's correction of the gate's premise is right. `.factory/state/specs/T-0024/v5.md` has five WHEN commands that run `init` (lines 234, 252, 275, 287, 302). Line 252 runs it from `$W`, which its fixture sets to `$S/runs/$R/scratch` (v5 line 187), inside the store. Three run from `$T/tgt`, one (234) from `tgt/sub/scratch`, a code-checkout subdirectory. v5's own Risk (lines 99-102) expects #46 to make that `init` resolve the live instance so the fence refuses it; A.1 refusing first with the same exit code and nothing written keeps the scenario's output `scratch_init=2 store=unchanged agents=none`. The spec says exactly this in Risk and Tests to change.
- N2: A.1.2 as written catches the detached case (`top == own`, where `own` is the live instance's `state_dir` resolved), and the same-common-dir qualifier is what keeps the separate-repository case working. Both conditions are branch-agnostic as the request asked, and Risk honestly names the one case neither sees (a phantom that already exists).
- N3, N4, N5: A.2 now refers to #45's part A.2 in one clause; the fence call is described as unconditional in A.2 and Risk; A.3.1 says one line and the scenario uses `grep -q`.

### Findings

No BLOCKING or SHOULD-FIX findings on the changed text.

[NIT] 6 proposal.md, Decisions, A.1 bullet
Problem: The bullet is one of the longest in the section and carries two "Rejected" clauses plus the attribution "(operator, round 2 change request N2)"; an operator new to the system can follow it, but it reads as two decisions (the refusal rule and the rejected repository-resolution approach) folded into one.
Evidence: Read as the gate operator; every term in it is glossed earlier (store, instance, worktree, repository), so it does not meet the blocking bar.
Suggested fix: Optional; split the "parent of `--git-common-dir`" rejection into its own bullet.

### Prior findings

- Round 3 [NIT] "init refuses a once-tracked store path": `names_path` could count a wrapped message twice → RESOLVED (A.3.1 says one line; the check is `grep -q`; N5).
- Round 3 [NIT] "store migrate refuses an uncommitted store and a run in flight": the in-flight half is answered by #45's fence on the real base, not by refusal 4 → UNRESOLVED, still a NIT. Text unchanged; C's suite test covers the marked path. Not blocking.
- Round 3 [NIT] `old_name=0` forces a rewrite of the closed amendment line at `dev/build-harness.spec.md:533` → UNRESOLVED, still a NIT. Text unchanged; the rewritten line still reads truthfully.
- Round 2 [NIT] `old_refs` alternative constrains the README how-to's phrasing → UNRESOLVED, still a NIT.
- Round 3 BLOCKING (phantom `init`) and all earlier BLOCKING / SHOULD-FIX items stay RESOLVED; v4 strengthens the phantom fix rather than reopening it.

### Out-of-scope observations

- The round counter in run metadata restarted at 1 after the gate's first change request (`run-0232-critic/meta.yaml` says `round: 1` for what the spec calls round 3). Harmless here, but a reader following "Round 4" through the store will not find a run numbered so.

## Verifier results

267ef3b4861ff29564a468c471d26f77c7f510e0 · T-0025.2 · VERIFIED · run-0270-verifier
d001090e9b0a535d55599ce5819c497572e07cf4 · T-0025.1 · VERIFIED · run-0256-verifier
fb72f7a7284a3208150c72ea20fe31299c9fdd4e · T-0025.1 · VERIFIED · run-0268-verifier
