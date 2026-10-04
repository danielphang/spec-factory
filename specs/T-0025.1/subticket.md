## T-0025-A / init puts a new store on its factory-store branch and refuses from inside the store (parts A, C for A and the gate, D for A)
Depends on: none
Parallel-safe: no (edits `factory/cli.py` `init_cmd`, `README.md` and `docs/changelog.md`, which T-0025-B also edits)

Parent: T-0025 approved spec v5 (issue #46), `.factory/state/specs/T-0025/v5.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Scope:
- Part A, steps A.1 to A.6, in `factory/cli.py` `init_cmd`. Git helpers may go in `factory/gitops.py`.
  - A.1: the two refusals from inside the store checkout, only with `FACTORY_INSTANCE` unset.
  - A.2: load the config in memory, keep #45's `fence` call right after `root`, unconditional, and keep the existing refusals.
  - A.3: for a missing own store only:
    - refuse a path the integration branch has ever tracked;
    - choose the branch source (a local branch, exactly one remote, more than one remote refused, or an orphan);
    - add the worktree, raising any git failure as `Refused`;
    - add the exclude line.
  - A.4: write the instance only after A.1 to A.3.
  - A.5: leave an existing store that is not the checkout of `factory-store` alone, with the stderr hint that matches it (a plain directory, or a detached store worktree).
  - A.6: `store_branch` in the JSON output.
- Part C, the A and merge-gate items, in the new file `tests/factory/test_store_branch.py`:
  - a new store is the branch's checkout, unseen by the integration checkout;
  - a store commit leaves the integration branch where it was;
  - a clone restores the store;
  - two remotes are refused, naming both, with nothing written;
  - a tracked path is refused, with nothing written;
  - `init` from a scratch directory inside the store is refused, with nothing written anywhere, both with the store on its branch and with it on a detached HEAD;
  - with `FACTORY_INSTANCE` set and `FACTORY_STATE` naming a throwaway store, A.1 does not refuse (#45's location rule still refuses an own-store write from there);
  - a separate repository under a run's scratch directory gets its own instance;
  - a failed worktree step (the branch already checked out elsewhere) writes no instance file;
  - an existing plain store is left alone, with `store_branch: null`;
  - a second `init` is a no-op;
  - the merge gate: a sub-ticket merges after a store commit, and is still refused after a code commit.
- Part D, the items that describe A:
  - `docs/design.md`: the role-context paragraph (`:60`), with "never tracked" and the sentence about a command run from a code checkout. The piece 1 row (`:39`) and "Smallest thing that works" (`:76`, twice) change `tickets` to `factory-store`. No prompt block changes.
  - `dev/build-harness.spec.md`: all 16 store-branch mentions of `tickets`.
  - `docs/changelog.md`: create entry 53 with `factory-store`, the worktree at the store path, the never-tracked path rule, and `init`'s new store, restore and refusal from inside the store.
  - `README.md`:
    - the "store branch" row in "Terms used on this page";
    - the target bullet in "Where it runs";
    - step 1 of "Adopting the factory in a repo";
    - the how-to "Committing and pushing the store", with both cautions: `git clean -ffdx` against `-fdx`, and running `init` from the repository root;
    - the "Parallel builds across tickets" paragraph, which drops the clause at `:306-307` and says a store commit no longer moves the integration branch;
    - the status date and ticket count.

Notes for the implementer:
- A.1.2 compares `git rev-parse --path-format=absolute --git-common-dir` at `top` and at `instance.repo_root(found)`. Without that check, the separate-repository scenario fails, and so do the suite's `init` calls under pytest's temporary directory.
- A.3.1's `<branch>`:
  - for an existing instance, `gitops.integration_branch`;
  - for a new instance, the checked-out branch, or `HEAD` when the repo root is detached;
  - an unborn branch counts as never tracked.
- The parent's "today" outputs were captured before #45 merged. Re-run each NEW WHEN on this base before changing code, and record what it prints.

Acceptance (each WHEN verbatim from the parent, run through the wrapper from the worktree root):
- init creates the store on the factory-store branch, out of the integration checkout's sight. NEW.
  WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; echo "branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/state/')")`
  THEN it prints `branch=factory-store seen_by_main=0`
- init on a clone restores the store from the pushed branch. NEW.
  WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/src && cd $T/src && git commit -q --allow-empty -m init && $B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T/src $T/c && cd $T/c && rm -rf .factory/state && $B init >/dev/null 2>&1; echo "exit=$? branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) restored=$(ls .factory/state/decisions.md 2>/dev/null | grep -c .)")`
  THEN it prints `exit=0 branch=factory-store restored=1`
- init on a clone with two remotes carrying the store branch refuses and names both. NEW. GIVEN: the parent's three-file block, as above.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T25/tgt $T25/c && cd $T25/c && git remote add nas $T25/tgt && git fetch -q nas && $B init >/dev/null 2>$T25/err; echo "exit=$? store=$([ -e .factory/state ] && echo written || echo none) local_branch=$(git branch --list factory-store | grep -c .) names=$(grep -c 'origin/factory-store' $T25/err),$(grep -c 'nas/factory-store' $T25/err)")`
  THEN it prints `exit=2 store=none local_branch=0 names=1,1`
- init from a scratch directory inside the store checkout refuses and leaves the store unchanged. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
  THEN it prints `exit=2 phantom=none store=unchanged`, then `found=ready-for-triage`
- init from the store checkout on a detached HEAD refuses. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git -C .factory/state checkout -q --detach && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? detached=$(git -C $T25/tgt/.factory/state symbolic-ref -q HEAD >/dev/null && echo no || echo yes) phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
  THEN it prints `exit=2 detached=yes phantom=none store=unchanged`, then `found=ready-for-triage`
- init in a separate repository under a run's scratch directory still creates its instance. REGRESSION.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && cd .factory/state/runs/run-0001-triage/scratch && git init -q -b main other && cd other && git commit -q --allow-empty -m init && $B init --repo-name other >/dev/null 2>&1; echo "exit=$? instance=$([ -f .factory/instance.yaml ] && echo written || echo none) live=$(cd $T25/tgt && $B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
  THEN it prints `exit=0 instance=written live=ready-for-triage`
- init refuses a once-tracked store path and writes nothing. NEW.
  WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/tgt && cd $T/tgt && mkdir -p .factory/state && echo old > .factory/state/old.md && git add -A && git commit -q -m "old store" && git rm -q -r .factory/state && git commit -q -m "store removed" && $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e .factory ] && echo written || echo none) names_path=$(grep -q '\.factory/state' $T/err && echo 1 || echo 0)")`
  THEN it prints `exit=2 instance=none names_path=1`
- A sub-ticket merges after a store commit. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: rows recorded"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
  THEN it prints `exit=0 refused=0`
- A sub-ticket is refused after a code commit to main. REGRESSION.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && echo y > y.txt && git add y.txt && git commit -q -m "code on main"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
  THEN it prints `exit=2 refused=1`
- The design doc names the store branch and the path rule. NEW.
  WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
  THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`
- The build spec calls the store branch factory-store. NEW.
  WHEN `(Q=$(printf '\140'); echo "old_name=$(grep -c "${Q}tickets${Q}\|refs/heads/tickets\|HEAD:tickets" dev/build-harness.spec.md) new_name=$(grep -c 'factory-store' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
  THEN it prints `old_name=0 new_name=1`
- The changelog records the store branch in one contiguous entry. NEW.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
  THEN it prints `CONTIGUOUS`, then `1`
- Intermediate check: an existing plain store is left alone and pointed to `store migrate` (A.5, A.6). This is the property that lets both real instances keep running until B lands and each instance migrates. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B init > $T25/out 2>$T25/err; echo "exit=$? branch=$(grep -o '"store_branch": null' $T25/out | grep -c .) hint=$(grep -c 'store migrate' $T25/err) dirty=$(git status --porcelain | grep -c .)")`
  THEN it prints `exit=0 branch=1 hint=1 dirty=0`. On `main` at `0b1abad` it prints `exit=0 branch=0 hint=0 dirty=0` (run by this planner).
- Intermediate check: the README describes the store branch, the `-ffdx` caution and the retired clause. This is the parent's README scenario restricted to A's items. NEW.
  WHEN `(echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch')")`
  THEN it prints `store_branch=1 ffdx=1 old_cost=0`
- Intermediate check: the changelog's last entry is 53. NEW.
  WHEN `(grep -E '^[0-9]+\. ' docs/changelog.md | tail -1 | cut -c1-30)`
  THEN it prints `53. After issue #46 (2026-10-0`
- The harness suite passes. REGRESSION.
  WHEN `(P=$(mktemp -d /tmp/t0025-suite.XXXXXX); TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
  THEN it prints one line reporting passed tests and no `failed` or `error`
- The store-branch change adds no whitespace errors. REGRESSION.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`

Tests to change: none
Protected paths: harness (`factory/**`): `factory/cli.py`, and `factory/gitops.py` if helpers go there. This matches the parent's Risk list.
Out of scope:
- Part B (`factory store migrate`) and its tests.
- README's "Moving an existing store onto its branch" how-to.
- The live-store location lines (`:433`, `:448`, `:487`, `:492`) and the diagram's `state/` labels (`:186`, `:191`).
- `merge_cmd`, `ticket_join`, `head_contains` (unchanged).
- How commands other than `init` find their instance.
- The default `state_dir`.
- Any `.factory/**` file.
- The operator's migration steps.

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
