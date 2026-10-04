## T-0025-B / factory store migrate moves a tracked store onto its branch (parts B, C for B, D for B)
Depends on: T-0025-A
Parallel-safe: no (edits `factory/cli.py`, `README.md` and `docs/changelog.md`, which T-0025-A also edits; it runs after A merges)

Parent: T-0025 approved spec v5 (issue #46), `.factory/state/specs/T-0025/v5.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Scope:
- Part B in `factory/cli.py`: the new `store` subcommand group in `build_parser` (`factory/cli.py:1042`) with `migrate --to PATH`.
  - All eight refusals are checked before the first write. Each exits 2 and changes nothing.
  - Steps 1 to 6:
    1. a root commit from the store's last committed tree;
    2. the worktree at PATH;
    3. copy the ignored files;
    4. byte-for-byte verification, undoing its own worktree and branch and exiting 1 on a mismatch;
    5. untrack the old path, add the exclude line, rewrite only the value on the `state_dir:` line, then delete the old directory;
    6. log `store.migrated` and print the JSON and the stderr reminder.
  - It makes no commit on the integration branch and pushes nothing. It is not added to #45's read-only list.
- Part C, the B items:
  - one success case, with the tree carried byte for byte, ignored run files copied, `state_dir` rewritten, the old path untracked and removed, and the store found by later commands;
  - a copy that does not match exits 1, leaves the old store and `instance.yaml` as they were, and leaves no `factory-store` branch or worktree;
  - every refusal, each writing nothing;
  - a checkout of the pre-move commit leaves the new store untouched.
  These go in a new file, `tests/factory/test_store_migrate.py`. See "Departure" below.
- Part D, the items that describe B:
  - `docs/changelog.md`: append the `store migrate` clause to entry 53.
  - `README.md`:
    - the how-to "Moving an existing store onto its branch": the preconditions, `factory store migrate --to .factory/store`, the commits afterwards, the "from before the move" note and the rollback (`rm <store>/.git && git worktree prune`, never `git worktree remove`);
    - every line that gives the live store's location names `.factory/store/` (`:433`, `:448`, `:487`, `:492`);
    - the two diagram labels `state/` become `store/` (`:186`, `:191`);
    - the status date and ticket count.

Departure from the parent's text: part C names one new test file, `tests/factory/test_store_branch.py`. Once T-0025-A merges, that file is an existing test file, and the guardrail forbids modifying existing tests that the parent does not list under "Tests to change". So B's tests go in their own new file. The tests asked for are the same. Only the file they live in differs.

Notes for the implementer:
- Refusal 7 reuses A.3.1's never-tracked test. Reuse the helper A adds rather than writing a second one.
- Refusal 4 is exercised with the marker set. The scenario's in-flight call carries `FACTORY_DISPATCH=1`, so #45's fence lets it through and B's own refusal must name the run (parent Gate edit, M6).
- Step 4's mismatch test needs a test hook or a monkeypatched copy between steps 3 and 4 (parent part C). Do not add a switch that the production CLI honours.

Acceptance (each WHEN verbatim from the parent, run through the wrapper from the worktree root; GIVEN: the parent's three-file block, as above):
- store migrate carries the store to factory-store at the new path. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && mkdir -p .factory/state/runs/run-0001-triage/scratch && echo n > .factory/state/runs/run-0001-triage/scratch/n.txt && $B store migrate --to .factory/store >/dev/null 2>&1; echo "exit=$?"; echo "branch=$(git -C .factory/store symbolic-ref --short HEAD 2>/dev/null) same_tree=$([ "$(git rev-parse -q --verify 'factory-store^{tree}')" = "$(git rev-parse $PRE:.factory/state)" ] && echo yes || echo no) scratch=$(cat .factory/store/runs/run-0001-triage/scratch/n.txt 2>/dev/null) old=$([ -e .factory/state ] && echo kept || echo gone) main_tracks=$(git ls-files .factory/state | grep -c .) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/store/')"; echo "state_dir=$(sed -n 's/^state_dir: *//p' .factory/instance.yaml) ticket=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
  THEN it prints `exit=0`, then `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0`, then `state_dir=.factory/store ticket=ready-for-triage`
- store migrate refuses an uncommitted store and a run in flight. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && echo edit >> .factory/state/decisions.md; $B store migrate --to .factory/store >/dev/null 2>$T25/e1; echo "uncommitted: exit=$? names=$(grep -c 'decisions.md' $T25/e1) branch=$(git branch --list factory-store | grep -c .)"; git checkout -q -- .factory/state/decisions.md && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git add -A && git commit -q -m "run started"; FACTORY_DISPATCH=1 $B store migrate --to .factory/store >/dev/null 2>$T25/e2; echo "in flight: exit=$? names=$(grep -c 'run-0001-triage' $T25/e2) branch=$(git branch --list factory-store | grep -c .) new=$([ -e .factory/store ] && echo written || echo none)")`
  THEN it prints `uncommitted: exit=2 names=1 branch=0`, then `in flight: exit=2 names=1 branch=0 new=none`
- A checkout of an older commit leaves the moved store untouched. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B store migrate --to .factory/store >/dev/null 2>&1 && git commit -q -a -m "store moved to its branch"; (echo live > .factory/store/live.md) 2>/dev/null; git checkout -q $PRE 2>/dev/null && git checkout -q main 2>/dev/null; echo "live=$(cat .factory/store/live.md 2>/dev/null || echo lost) on=$(git symbolic-ref --short HEAD)")`
  THEN it prints `live=live on=main`
- The README describes the store branch and the move. NEW. It first passes in full here.
  WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
  THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`
- The changelog records the store branch in one contiguous entry. REGRESSION, since it passes after T-0025-A.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
  THEN it prints `CONTIGUOUS`, then `1`
- Intermediate check: entry 53 names `store migrate`, and no entry 54 was added. NEW.
  WHEN `(grep -E '^[0-9]+\. ' docs/changelog.md | tail -1 | cut -c1-4; grep -E '^53\. ' docs/changelog.md | grep -c 'store migrate')`
  THEN it prints `53. `, then `1`
- Every T-0025-A acceptance scenario still prints its THEN. REGRESSION. Re-run the eleven parent scenarios listed under T-0025-A, from "init creates the store on the factory-store branch" through "The build spec calls the store branch factory-store", plus T-0025-A's plain-store intermediate check.
- The harness suite passes. REGRESSION.
  WHEN `(P=$(mktemp -d /tmp/t0025-suite.XXXXXX); TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
  THEN it prints one line reporting passed tests and no `failed` or `error`
- The store-branch change adds no whitespace errors. REGRESSION.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`

Tests to change: none
Protected paths: harness (`factory/**`): `factory/cli.py`, and `factory/gitops.py` if helpers go there. This matches the parent's Risk list.
Out of scope:
- Running the migration on this repo or on the Nanobot repo. These are the parent's Operator steps 2 and 3, and the `.factory/context.md` and `.factory/README.md` edits are among them.
- Any `.factory/**` file.
- `init` (T-0025-A).
- Committing or pushing the store from the harness.
- Rewriting history.
- `merge_cmd` and #45's read-only list.

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: the approved spec v5 of T-0025 (issue #46), in this run's input and at `.factory/state/specs/T-0025.md` with its versions under `.factory/state/specs/T-0025/` (`v5.md`).

Two sub-tickets, built one after the other:
- **T-0025-A** covers `init`'s new store (part A), the merge-gate checks and the documents that describe them.
- **T-0025-B** covers `factory store migrate` (part B) and the documents that describe it.

**Why two.** The parent sizes the change at about 470 lines and says each lettered part can be its own sub-ticket (design.md, "Size and seams"). I split at A/B because B is the riskiest code in the change: it deletes the old store directory after copying it. A reviewer should judge it on its own, and it should be possible to revert it alone. I did not split further, for two reasons:
- Part C (tests) has no code of its own. The parent puts each test with the part it covers.
- Part D (documents) cannot trail A and B as a third sub-ticket. README's "Maintaining this page" says: "A sub-ticket that changes a command, a state, a stop or a path updates the sentence that describes it" (`README.md:461-463`). The briefing says the same. So each sub-ticket carries the D items that describe its own part.

This departs from the parent's "D goes last" only in where the document edits land. Every D item is still built, in the same words.

**Each merges on its own.** After A merges alone:
- A new instance's store is a `factory-store` worktree.
- An existing plain store, like both real instances' stores, is left alone (A.5).
- Nothing yet moves a store.
- B's NEW scenarios still print today's argparse refusal.

B needs A only for the documents and for sharing `init`'s never-tracked-path test (A.3.1 is reused by B refusal 7).

**Order.** B depends on A. Neither is parallel-safe: both edit `factory/cli.py`, `README.md` and `docs/changelog.md`. Because B starts only after A merges, no run has to re-verify against a sibling's merge.

**IDs.** The store numbers sub-tickets in plan order, so `T-0025-A` becomes `T-0025.1` and `T-0025-B` becomes `T-0025.2`.

**Checked on `main` at `0b1abad`:**
- #45 (T-0024) has merged: `4f8f1d5 Merge factory/T-0024.1`. Changelog entry 52 is #45's (`docs/changelog.md:56`), so this change's entry is 53, before `Declined:` (`:58`).
- `git diff --stat d2a5143 HEAD -- factory bin tests docs dev README.md agents` shows only #45's eight files: 245 insertions and 9 deletions. The parent's code anchors still hold.
- In `init_cmd` (`factory/cli.py:846`), today's sequence is:
  - `top = _git_toplevel(...)` (`:853`);
  - the new-instance branch writes `instance.yaml` before `cfg = instance.load_config(inst)`;
  - then `root = ...` and `fence(inst, cfg, root)`.
  Part A.2 reorders this, so the template's config is loaded in memory and the yaml is written only at step A.4. The `fence` call stays right after `root`, unconditional.
- These helpers exist:
  - `instance.find` (`factory/instance.py:55`), `repo_root` (`:81`), `own_state_root` (`:93`) and `is_own_store` (`:105`);
  - `gitops.integration_branch` (`factory/gitops.py:22`), `git` (`:31`) and `checkout_of` (`:92`).
- Line numbers have moved since the parent's evidence was taken. The parent's line numbers are references only:
  - design.md: the piece 1 row is at `docs/design.md:39`, the role-context paragraph at `:60` (the parent says 58) and "Smallest thing that works" at `:76` (the parent says 74).
  - README: the retired clause wraps at `README.md:306-307`. The four live-store location lines are now `:433`, `:448`, `:487` and `:492` (the parent says 403, 418, 457 and 462). The diagram's `state/` labels are at `:186` and `:191`.
- `dev/build-harness.spec.md` has 16 lines that name the store branch `tickets` (the build spec's own count).

**Rules for both sub-tickets:**
- Run every command from the root of your worktree, after `uv sync --frozen`, through the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`, under `bash`.
- Before any scenario that names `t0025-old.sh`, `t0025-b1.sh` or `t0025-gate.sh`, run the GIVEN block of the parent's scenario "init on a clone with two remotes carrying the store branch refuses and names both" (`specs/store-setup/spec.md`) once. Run it verbatim, at column 0. It writes the three files under `${TMPDIR:-/tmp}`. Point `TMPDIR` at a directory outside every git repository and remove it afterwards. Your scratch directory lies inside the live store's git worktree, so it would change what `git rev-parse --show-toplevel` reports inside the fixtures.
- Tests that commit set `GIT_AUTHOR_*` and `GIT_COMMITTER_*`. Tests that run store commands with a run in flight on an own store mark them with `FACTORY_DISPATCH=1`, as `tests/factory/test_live_store_guard.py` does (parent part C).
- New tests go in new files. "Tests to change" is none for both. If an existing test breaks, including any test in `tests/factory/test_live_store_guard.py` that asserts #45's location-rule text for `init` from a store's `runs/`, report it. Do not edit it (parent, "Tests to change").
- Changelog entry 53 is one line. A creates it after entry 52 and before the blank line above `Declined:`, starting `53. After issue #46 (2026-10-04),`. B appends its `store migrate` clause to that same line.
- Each sub-ticket re-derives README's ticket count (`ls .factory/state/tickets | wc -l`, the README's own check) and bumps the status date at `README.md:9`.
