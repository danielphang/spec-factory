## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0241-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0241-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0025.1` (branch `factory/T-0025.1`, base `0b1abad474cb9c583ed8445fc33617f9f0bdc37b`, head `0b1abad474cb9c583ed8445fc33617f9f0bdc37b`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0025.1

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

## Parent spec (v5, pinned)

=== proposal.md
## Problem

Each time the operator commits the factory's records, any piece of work that is waiting to merge has to be checked again from the start, although nothing it was checked against has changed. This costs the operator time and tokens on both repositories the factory runs on, and it has already led one session to hand-edit checker results to get past the gate.

The factory keeps its records in a directory of files called the **store**: one file per ticket with its state, the operator's approvals, each agent run's input and output, the checkers' verdicts and an append-only log. Each repository the factory works on has its own store. The store is committed to git on purpose, so it is versioned, reviewable and pushed. Today it is committed to the **integration branch**, the branch that finished pieces of work are merged into: `main` in this repo and `feat/lionbot-v3.5` in the Nanobot repo. The operator commits the store between steps, after an approval, a close or a new record. So the integration branch moves even when no code changed.

A planned ticket is built as **sub-tickets**, each a separately mergeable branch written by an implementer agent and judged by two checker agents, a code reviewer and a verifier. The **merge gate** is the step that merges a sub-ticket once both checkers pass it. It refuses a branch that does not contain the current integration branch, so that the code that was checked is the code that merges. A store commit made while a sub-ticket is being checked therefore sends it back. Its implementer merges the integration branch in, which is a **catch-up run**, and both checkers run again. That takes 10 to 20 minutes. The requester estimates it at about a million tokens. It cannot change the verdict, because the merge it makes brings in only store files. This has happened four times in this repo and at least once in the Nanobot repo.

The operator has decided that the fix is a separate branch, not a gate exception. A gate rule that ignores store-only commits would only imitate a separate branch. The store moves to its own branch, `factory-store`, and is still committed and pushed. The integration branch then moves only when work merges. This spec recommends checking that branch out as a git worktree (a second working directory of the same repository) at the store's path (option B1), rather than writing the branch through git plumbing with no working copy (option B2). It also moves the store to a path that the integration branch has never tracked. At the old path, an ordinary `git checkout` of an older commit overwrites the live records.

Putting the store in its own worktree has one side effect that this spec closes. The factory's `init` command, which creates an instance (the factory's per-repository setup) where none exists, decides which repository it is in from the git checkout around the caller's directory. Agents run in scratch directories inside the store. From there, the checkout around them would be the store's own worktree, so a stray `init` would build a second, phantom instance inside the live store, and later commands from those directories would talk to that phantom. After this change, `init` refuses to run from inside the store's worktree, whichever commit that worktree has checked out.

## Evidence

All commands were run from `~/dev/spec-factory` on `main` at `abaa75a`, except where a path says otherwise. Round 4 ran its new probes on `d2a5143`. Between the two, only the store changed: `git diff --stat abaa75a d2a5143 -- . ':!.factory'` prints nothing. Both are before T-0024 (issue #45) is built; see Risk for how #45 bears on these results.

**The gate refusal.** `factory/cli.py:544-550`, in `merge_cmd`, refuses with `head does not contain main (<branch> moved; merge it into <branch> and re-check)` when `gitops.head_contains` (`factory/gitops.py:79`) finds the integration branch is not an ancestor of the checked head. `ticket_join` (`factory/cli.py:592-595`) turns that refusal into a catch-up run, and parks the ticket after `MAX_CONFLICT_RUNS = 2` such runs (`factory/cli.py:576`). Any commit on the integration branch triggers this, whatever it touches.

**The store is on the integration branch in both repos.** `git ls-files .factory/state | wc -l` printed `1340` here, and `1149` in `~/dev/nanobot-upstream` on `feat/lionbot-v3.5`. Both stores are tracked on the branch their sub-tickets merge into. Here, 38 non-merge commits on `main` touch the store, and 20 of them touch nothing else (`git log --no-merges -- .factory/state`, each classified by `git show --name-only`).

**What each catch-up merge brought in.** This store has six implementer runs with `resolution: conflict` (`grep -l "resolution: conflict" .factory/state/runs/*/meta.yaml`). For each run's catch-up merge commit, `git diff --name-only <merge>^1 <merge>` lists the files that the merge brought into the sub-ticket's branch:

| Catch-up run | Sub-ticket | Merge commit | What the merge brought in |
|---|---|---|---|
| run-0082 | T-0012.5 | `aeb684d` | 108 store files, nothing else |
| run-0085 | T-0012.4 | `a5f1329` | 108 store files, nothing else |
| run-0088 | T-0012.4 | `be292ad` | 3 documents from a sibling sub-ticket's merge (a real catch-up) |
| run-0099 | T-0012.6 | `2d86d96` | 101 store files, nothing else |
| run-0122 | T-0014.1 | `89e8b7d` | `dev/issues.md` only (an operator index commit) |
| run-0212 | T-0023.3 | `a1b2718` | 67 store files, nothing else |

Four of the six catch-up runs (run-0082, run-0085, run-0099, run-0212) existed only because of store commits. This change removes that kind of run. The request's count includes run-0122, but that run's merge brought in only `dev/issues.md`, which is an operator commit of a document. Moving the store would not have prevented it (Out of scope). The retro trial's write-up of these runs ("escalation C1") is not in this repo. `.factory/state/requests/T-0023.md:18` and `.factory/state/plans/T-0018.md` only refer to it.

**The cost of one.** T-0023.3's catch-up run took 251 s (`run-0212-implementer/meta.yaml`, `wall_s`). It was followed by a verifier run of 362 s and a reviewer run of 413 s, which ran side by side (run-0213, run-0214). That is about 11 minutes, for a merge that brought in only store files. Token cost was not measured here. The figure of about a million tokens is the requester's estimate. Before that catch-up, a session reinstated earlier checker rows by hand to get past the gate (`.factory/answers/T-0023.3-operator-decision.md`).

**The same happens on the Nanobot repo.** In `~/dev/nanobot-upstream`, `6e98ae250 Merge feat/lionbot-v3.5 (25276be84) into factory/T-0008.1` is a catch-up merge after a store commit. `git diff --name-only 6e98ae250^1 6e98ae250` lists 40 files, and all of them are under `.factory/state/`.

**The design already calls for a separate branch.** `docs/design.md:39` (harness piece 1, the ticket store) says "A `tickets` branch of YAML works to start: the pre-receive hook restricts it to harness and human identities and exempts it from the merge gate". `docs/design.md:74` repeats it. `dev/build-harness.spec.md:152` says "State on branch `tickets` … never merged into `main`, never subject to the merge gate … checked out at `~/factory/state`". The as-built harness kept the store as a plain directory inside each repo's `.factory/` (`factory/instance.template.yaml:10`, `state_dir: .factory/state`), and the operator commits it on the integration branch. The change brings the build into line with the design.

The prototypes below ran in throwaway repos under a throwaway HOME. The harness clears this run's scratch directory when the ticket moves on, so each paragraph gives the git commands it ran.

**Moving the branch but keeping the old path loses records.** The prototype committed a store record at `.factory/state` on `main` (commit PRE). It then untracked the path (`git rm -r --cached`), added `/.factory/state/` to `.git/info/exclude`, and put the record in a `factory-store` worktree at that same path (`git worktree add --orphan -b factory-store .factory/state`). Then:
- It appended `live: 1` to the record and ran `git checkout PRE`, then `git checkout main`. They printed `after_checkout_old: id: T-1` and `after_back_to_main: … No such file or directory`. The uncommitted line was overwritten by the old version without a warning, and then the file was deleted. Git treats ignored files as expendable, and the old commits track that path.
- It merged into `main` a branch that changed the record before the move, as a catch-up merge would. That printed `merge_exit=1 conflict=1`, a modify/delete conflict. `git merge --abort` then printed `store_intact=` empty: the live record was gone.
At a path the integration branch never tracked, neither can happen. Acceptance scenario "A checkout of an older commit leaves the moved store untouched" checks this.

**B1 against B2 on git's own clean command.** In one repo, a B1 store at `.factory/store` (a `factory-store` worktree) and a B2 store at `.factory/b2` (a plain directory) were both listed in `.git/info/exclude`. `git clean -fdxq` in the integration checkout printed `after_clean_fdx: b1=decisions.md b2=gone`. The B1 store survived, because git skips a directory that holds its own `.git`. The B2 store was deleted. A second probe committed one file in a B1 store and ran `git clean -ffdxq`: it printed `after -ffdx: ls: .factory/store: No such file or directory`. The doubled `-f` tells git to delete nested repositories too, so it deletes a B1 store as well. `git worktree list` still listed the store afterwards, as a stale entry.

**B1 needs no git identity at creation, and a clone can restore it.** `git worktree add --orphan -b factory-store .factory/store`, run with no git identity configured, printed `orphan_add=0 status_lines=0`. It succeeded, and the integration checkout's `git status --porcelain` showed nothing once the path was in the exclude file. The branch stays unborn until the first commit, and `git worktree list --porcelain` already shows the worktree as `branch refs/heads/factory-store`. After one store commit, a `git clone` followed by `git worktree add .factory/store factory-store` printed `restore=0 branch=factory-store upstream=origin/factory-store file=decisions.md`: the store came back from the pushed branch. This machine runs git 2.54.0.

**A clone with two remotes carrying the branch.** In a clone of a repo whose `factory-store` had one commit, `git remote add nas <src> && git fetch nas` left two remote-tracking refs, `refs/remotes/nas/factory-store` and `refs/remotes/origin/factory-store`. `git worktree add .factory/store factory-store` then printed `fatal: invalid reference: factory-store` and exited 128. Git does not guess between two remotes. The Nanobot repo has three remotes (`git -C ~/dev/nanobot-upstream remote` lists `fork`, `nas` and `origin`).

**`init` from inside a store worktree builds a phantom instance.** A throwaway target was given a store at `.factory/state` that is a `factory-store` worktree, built with git alone. `bin/factory init --repo-name demo` created the instance, `ticket new` and `run start --role triage --ticket T-0001` made a run with a scratch directory. From `.factory/state/runs/run-0001-triage/scratch`, `git rev-parse --show-toplevel` printed the store worktree's root, `<target>/.factory/state`, not the target's root. `bin/factory init --repo-name x` from there exited 0. It wrote `.factory/instance.yaml`, `context.md`, `harness.lock` and a nested `state/` under the store, and six agent files under `<store>/.claude/agents/`, all visible to `git -C .factory/state status`. `init_cmd` takes its instance from that top level (`factory/cli.py:853`, through `_git_toplevel` at `factory/cli.py:821-824`). Every other command finds its instance by walking up from the caller's directory to the nearest `.factory/instance.yaml` (`factory/instance.py:55-64`), so after the phantom exists they stop at it first. Acceptance scenario "init from a scratch directory inside the store checkout refuses and leaves the store unchanged" reproduces this: it prints `exit=0 phantom=written store=changed`, then `found=`, because `ticket show T-0001` from the scratch directory now reads the phantom's empty store.

**The store checkout is not always on its branch.** A check that asks git which branch the top level has checked out misses a store worktree on a detached HEAD, for example after an operator checks out an older store commit to inspect it. On the same fixture, after one store commit and `git -C .factory/state checkout --detach`, `git symbolic-ref -q HEAD` in the store prints nothing and exits 1. `init --repo-name x` from the run's scratch directory again exited 0 and built the phantom. The probe printed `exit=0 detached=yes phantom=written store=changed`, then `found=`. Acceptance scenario "init from the store checkout on a detached HEAD refuses" reproduces it. Walking up from the scratch directory still finds the live instance, because the store holds no `.factory/instance.yaml` of its own. That instance's store path is exactly the top level git reports, so comparing the two names the live store whatever the store has checked out.

**A separate repository under a run's scratch directory is not the live store.** A role may create a throwaway git repository in its scratch directory, which lies inside the live store, and run `init` there. A test suite does this when its temporary directory is set to the scratch directory. From such a repository, walking up also finds the live instance, and its store contains the repository's top level. But `git rev-parse --path-format=absolute --git-common-dir` prints `<scratch>/other/.git` there, while the store worktree and the integration checkout both print `<target>/.git`. So it is a different repository, and `init` there builds that repository's own instance, not one inside the live store. Today that `init` succeeds: the probe printed `exit=0 instance=written live=ready-for-triage`. Acceptance scenario "init in a separate repository under a run's scratch directory still creates its instance" keeps it so. The suite has 14 `init` calls through helpers that remove `FACTORY_INSTANCE` (`grep -nE 'cli\([^)]*"init"'` over `tests/factory/test_instance.py`, `test_harness_lock.py` and `test_coding_standard.py`), most of them in fresh repositories under pytest's temporary directory.

**Why `init` cannot take the main worktree instead.** One suggested fix was to resolve the repository from `git rev-parse --git-common-dir`, whose parent is the repository's main worktree. That is the wrong checkout for both instances. The Nanobot instance lives in a linked worktree: `git -C ~/dev/nanobot-upstream rev-parse --git-common-dir` prints `/Users/dphang/dev/nanobot/.git`, so its main worktree is `~/dev/nanobot`, a different checkout on a different branch. The runtime checkout `~/dev/spec-factory-harness` is likewise a linked worktree of this repo (`--git-common-dir` prints `/Users/dphang/dev/spec-factory/.git`).

**Code checkouts do not need the store.** Roles get the live store's absolute paths in their composed input. `compose.py` reads from the store root, and ticket records name store files by store-relative paths (`factory/cli.py:741`, `root / t["request"]`). The workflow scripts pass the instance and store to every store command explicitly (`FACTORY_INSTANCE`, `FACTORY_STATE`; `factory/workflows/build.js:21-22`, `factory/workflows/intake.js:26-27`). Implementer worktrees (`factory/cli.py:247`) and checker checkouts (`factory/cli.py:259`) carry a stale copy of the store today only because their branches start from the integration branch. Nothing reads that copy.

## Root cause

The store sits inside the target repo, at `.factory/state`, as a plain directory (`factory/instance.template.yaml:10`, `factory/instance.py` `own_state_root`). `init_cmd` (`factory/cli.py:845`) creates it there and does nothing more with git, and the operator commits it on the integration branch. The merge gate's containment check (`factory/cli.py:545`) counts every commit on that branch. So a store commit forces a catch-up run. The design's separate `tickets` branch (`docs/design.md:39`, `dev/build-harness.spec.md:152`) was never built in the local version of the build half.

The phantom-instance hazard comes from `init_cmd` alone: it takes the instance from `git rev-parse --show-toplevel` of the caller's directory (`factory/cli.py:853`), which inside a store worktree is that worktree, not the target.

## Out of scope

- A merge-gate exception for store-only commits (option A). The operator set it aside because it only imitates a separate branch. `merge_cmd`, `ticket_join` and `head_contains` do not change.
- Catch-up runs caused by operator commits of documents to the integration branch, such as run-0122's `dev/issues.md`.
- The harness committing or pushing the store by itself. Operators and runner sessions keep committing it by hand, now in the store's own checkout.
- Moving the Nanobot repo's store from this repo. That is a paired ticket on that repo, run by its own Driver session (the session that runs the factory there). This repo treats `~/dev/nanobot-upstream/**` as read-only.
- Rewriting either branch's history. Store history up to the move stays on the integration branch.
- The default `state_dir` for new instances. It stays `.factory/state`, which a new repo has never tracked.
- Role runs that write the live store (T-0024, issue #45). This change keeps #45's fence as built (Risk).
- How commands other than `init` find their instance. The walk-up to `.factory/instance.yaml` does not change.
- Records under `.factory/answers/` and `.factory/green-pilot/`. They stay on the integration branch.

## Open questions

none

## Decisions

- The store lives on its own branch, `factory-store`, checked out as a git worktree at the store's path (B1). This is for the operator to confirm at the spec gate. Rejected: B2, the branch written through git plumbing with no working copy. It needs new harness commands to snapshot, show and restore the store, and `git clean -fdx` in the integration checkout deletes the store (Evidence). Rejected: A, a gate exception (operator, 2026-10-04).
- A store path must be one the integration branch has never tracked. Both existing stores move from `.factory/state` to `.factory/store`. Rejected: keeping `.factory/state`, where checking out an older commit overwrote an uncommitted record and checking `main` out again deleted it (Evidence).
- The branch is named `factory-store`, and the design doc and build spec drop the name `tickets` for it. Rejected: `tickets`, a generic name in a target repo whose branches serve other work, such as the Nanobot repo, which shares its objects with another checkout.
- `init` creates a new store as a worktree on an unborn `factory-store` branch, and the operator makes the first commit. On a clone where the branch already exists, `init` checks it out, which restores the store. Rejected: `init` committing, which needs a git identity, and the suite runs under a throwaway HOME that has none.
- When no local `factory-store` exists and more than one remote carries it, `init` refuses and names each `<remote>/factory-store`. The operator picks one with `git branch factory-store <remote>/factory-store` and runs `init` again. Rejected: creating a new empty branch, which would silently start a second store history beside the pushed one. Also rejected: preferring `origin`, a guess about which remote is canonical.
- With `FACTORY_INSTANCE` unset, `init` refuses, writing nothing, when the caller's git top level is a checkout of `factory-store`. It also refuses when the instance found by walking up from the caller's directory has a store that is that top level, or that contains it in the same repository (the same git common directory). These are the cases where it would build a phantom instance inside the live store. The second condition does not depend on which branch or commit the store has checked out, so a detached store HEAD does not open the route again (operator, round 2 change request N2). The same-repository qualifier keeps `init` working in a separate throwaway repository under a run's scratch directory (Evidence). Rejected: "contains" without that qualifier, which would refuse every suite `init` run with pytest's temporary directory inside a store. Rejected: taking the repository from the parent of `--git-common-dir`. That is the main worktree, which for the Nanobot instance is `~/dev/nanobot`, another checkout on another branch, and for the runtime checkout is `~/dev/spec-factory` (Evidence).
- In `init`, every refusal and the store-worktree step come before any instance file is written, so a failed worktree step (for example, git's "already used by worktree" when `init` runs in a code checkout of a repo whose store branch is checked out elsewhere) leaves nothing behind.
- The integration checkout ignores the store through the repo's git exclude file, which `init` and `store migrate` write. Rejected: a line in the target's tracked `.gitignore`. That would change the target's code to record a fact about one clone.
- A new command, `factory store migrate --to PATH`, moves an existing store. It refuses unless the store is idle and committed, and it leaves the integration-branch side uncommitted for the operator to review. Rejected: a hand procedure, untested, run once on each repo by a different session.
- `store migrate` deletes the old store directory only after it has checked that every ignored file (run scratch directories, tripwire baselines) was copied byte for byte. If the check fails, it undoes its own worktree and branch and leaves the old store as it was. Rejected: relying on `git status` in the new checkout, which cannot see ignored files.
- The store branch starts with one commit whose tree is the store as last committed on the integration branch, and whose message names that commit. Earlier history stays readable with `git log <that commit> -- .factory/state`. Rejected: rewriting history with a subtree split. It would follow only part of the store's past, which began at `intake/state`, and it adds nothing that `main`'s history does not already keep.
- An instance whose store is still a plain directory keeps working unchanged. `init` leaves such a store alone and points to `store migrate`. The harness reads and writes the store only through `state_dir`, so it runs with either layout.

## Risk

- Blast radius: where every instance keeps its store, how operators commit and push it, and where `init` will run. Code that reads or writes store files is unchanged. The merge gate is unchanged. Merges into the integration branch run in the integration checkout as before (`gitops.merge_no_ff`), and that checkout no longer holds store files.
- Protected paths this change touches: harness (`factory/**`), in `factory/cli.py` and, if helpers go there, `factory/gitops.py`. It touches no `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock` or `docs/prompts/**` file. No prompt block of the design doc changes. The operator's migration (Operator steps) changes `.factory/**` on each instance, at the operator's command.
- Moving a store while it is in use would lose records. `store migrate` refuses while any run is in flight, while a git worktree lies under the store, or while store files are uncommitted. It removes the old directory only after it has verified the copy.
- A sub-ticket branch cut before the move still tracks the old path. Merging it after the move fails with a conflict if it carried store changes. It cannot reach the new path. The operator moves a store only when no build is in progress.
- `init` needs `git worktree add --orphan`. It is present in this machine's git 2.54.0, and an older git refuses with git's own error.
- Built on #45 (T-0024), which merges first. #45 adds a fence: while a role run is in flight on an instance's own store, every store command except a fixed read-only list is refused unless marked with `FACTORY_DISPATCH=1`. It also calls that fence in `init_cmd`, unconditionally, right after the store root is resolved and before any write; on a new instance the call finds nothing in flight and does nothing. Both changes edit `init_cmd` and `main()`, so this change is rebased on #45 and keeps its fence call, unconditional and in the order "fence before any write". `store migrate` is a new command, so #45's default fences it while a run is in flight; its own in-flight refusal still covers a marked call. #45's fence does not cover the phantom `init`, because the instance it is handed is the phantom's, not the live one; the refusals in part A.1 do.
- #45's acceptance scenarios after this change. Read in #45's approved spec (`.factory/state/specs/T-0024/v5.md`), five of its WHEN commands run `init`, besides its fixture's own `init` at the target's root. Three run it from the target's repository root (the throwaway-store scenario now among them, `(cd $T/tgt && FACTORY_STATE=$T/s $B init ...)`) and one from a subdirectory of the target's code checkout. None of these has the store checkout as its top level or lies inside the store, so A.1 does not apply and their outputs are unchanged. One scenario still runs `init` from a run's scratch directory: "Marked writes from a run's scratch directory or a worktree directory are refused, init included" (`cd $W && FACTORY_DISPATCH=1 $B init --repo-name x`, expecting `scratch_init=2`, `store=unchanged` and `agents=none`). After this change its store is a `factory-store` checkout, so A.1 refuses that `init` before #45's fence runs. The exit code is still 2 and nothing is written, so its output is unchanged; only the refusal's text differs from #45's location rule. Its other two commands do not run `init` and are unaffected. #45's own Risk section expects this change's `init` to resolve the live instance, so that #45's location rule refuses it; A.1 refuses it first instead, with the same exit code and nothing written.
- A phantom instance that already exists inside a store is not caught by A.1's second condition, because walking up from inside the store stops at the phantom's `.factory/instance.yaml` first. One could only come from a harness older than this change run against a moved store; the operator steps upgrade the runtime before any store moves. The first condition still refuses while the store is on its branch.
- How a role's shell finds the store changes for `init` only. Every other command still walks up from the caller's directory to `.factory/instance.yaml`. From a scratch directory inside the store worktree that walk passes the store (no `.factory/instance.yaml` there) and finds the live instance. From inside a code checkout (an implementer worktree or a checker checkout) it finds that checkout's tracked `instance.yaml`, whose store path does not exist there, so a stray command reports no such ticket instead of reaching the live store. Today it reaches the checkout's stale tracked copy. `init` from inside the store worktree is refused (A.1), whichever commit the store has checked out.
- `git clean -ffdx` in the integration checkout deletes the store worktree, uncommitted records included (Evidence). `git clean -fdx` keeps it. The README says so.
- After the move, checking out a commit from before the move in the integration checkout brings back the old `.factory/state` and an `instance.yaml` whose `state_dir` names it. Commands run during that checkout use that stale copy. Checking the integration branch out again removes it. The README says so.
- Until each instance runs its migration, the README describes this repo's store at `.factory/store`, where it does not yet exist.

## Gate edit (Green session, operator-delegated, 2026-10-04)

From the Fable design review round 3 (`.factory/answers/design-review-45-46/round-3.md`). M1 (SHOULD-FIX): part C's test-list clause now matches #45's location rule. Notes: M3, the A.5 warning distinguishes a plain directory from a detached store worktree; M4, `HEAD` when the repo root is detached; M5, the A.1.2 lapse clause requires `state_dir`; M6, the in-flight `store migrate` WHEN carries the marker, so B refusal 4 is the one exercised. M2 (an out-of-repo `state_dir` with a detached store escapes A.1.2) is accepted as a Risk: both real instances keep the store inside the repo.

## Operator steps

1. Upgrade the runtime to the merged revision. The runtime is the separate checkout of the harness that runs every ticket, `~/dev/spec-factory-harness`, pinned to one commit; a merge into `main` does not change it. Each repository runs only the harness commit it has accepted, recorded in its `.factory/harness.lock`, and refuses its store commands until it accepts a new one with `--accept-harness <sha>`. With no build in progress, run `git -C ~/dev/spec-factory-harness checkout --detach <sha>` and `uv sync --frozen` there, where `<sha>` is the merged commit. Then accept it on this repo with `~/dev/spec-factory-harness/bin/factory --accept-harness <sha> ticket show T-0025`, where T-0025 is this ticket.
2. Move this repo's store. Wait until no ticket has a run in flight. In `~/dev/spec-factory`, commit everything under `.factory/state/` on `main`. Then run `~/dev/spec-factory-harness/bin/factory store migrate --to .factory/store`. Edit `.factory/context.md`: the sentence "The store is tracked on `main` and the operator commits it between steps, so `main` moves even when no ticket merges" becomes a statement that the store at `.factory/store` is a checkout of `factory-store`, committed there and never on `main`. Edit `.factory/README.md` the same way, wherever it gives the live store's path. This repo's `protected_paths` already covers `.factory/**`, so the new path is protected with no edit. Review `git status`, commit on `main`, commit the store (`git -C .factory/store add -A && git -C .factory/store commit -m "store: …"`), and push both branches (`git push origin main factory-store`).
   Check: `~/dev/spec-factory-harness/bin/factory paths` prints a `state` ending in `/.factory/store`. `git -C .factory/store symbolic-ref --short HEAD` prints `factory-store`. `git ls-files .factory/state | wc -l` prints `0`, and `git status --porcelain` prints nothing.
3. The Nanobot repo: file a paired ticket there for its Driver session, the operator session that runs the factory on that repo, to run after its in-flight builds merge. `store migrate` refuses while any git worktree lies under the store or any store file is uncommitted, and on 2026-10-04 that repo had both, changing from hour to hour. So the ticket's first step is to check `git worktree list` and `git status --porcelain -- .factory/state` there and wait until neither shows anything under the store. The ticket covers:
   - the runtime acceptance and the same `store migrate --to .factory/store`;
   - that repo's `context.md`;
   - adding `.factory/store/**` to `protected_paths.infra` in its `instance.yaml`, which today lists specific `.factory/` files and so does not protect the store at either path;
   - which of its remotes (`fork`, `nas`, `origin`) carries `factory-store`. If more than one does, a later clone's `init` refuses until the operator picks one;
   - that the repo shares its objects with `~/dev/nanobot`, so the branch and the exclude line appear there too.
4. From then on, commit store changes in the store checkout and push `factory-store`. The integration branch moves only on merges and document commits.

=== design.md
## Proposed change

This change is built on #45 (T-0024), which merges first. Keep #45's fence and its place in `main()` and `init_cmd`; nothing here moves or bypasses it.

### Choice of layout: B1 and B2 compared

The request asks for the two layouts to be weighed on six points. Both put the store on a branch that is never merged into the integration branch, and both need the new store path (Decisions).

| Point | B1: worktree at the store path (proposed) | B2: branch written by plumbing, no working copy |
|---|---|---|
| Moving an existing store | `store migrate` (part B): the branch starts from the store's last committed tree, a worktree is added at the new path, ignored run files are copied and verified, and the old path is untracked | Same branch creation. The directory moves as a plain directory. |
| What `init` sets up | A worktree on an unborn `factory-store` branch, or the existing branch on a clone, which restores the store. Refuses from inside the store worktree. | A plain directory. Restoring on a clone needs a new extract command. |
| Implementer worktrees and checker checkouts | Hold no store copy. Code branches never track the store path. | Same |
| How operators and runners commit and push | Plain git in the store: `git -C <store> add -A && git -C <store> commit`, `git push origin factory-store`. `git status` and `git diff` show pending store changes. | A new harness command per commit (temporary index, `write-tree`, `commit-tree`, `update-ref`), and another to show pending changes |
| What breaks | `git log -- .factory/state` on the integration branch ends at the move, and later history is `git log factory-store`. Records quoting the old path are history. `git clean -ffdx` deletes the store. | Same. Also no `git status` over the store, and even `git clean -fdx` in the integration checkout deletes it (Evidence). |
| Rollback | Detach and re-track (part D, README how-to). The harness needs no rollback. | Move back and re-track |

### A. `init` puts a new store on its branch (`factory/cli.py` `init_cmd`; git helpers may go in `factory/gitops.py`)

The order below is the order of the code. Every refusal is a `Refused` (exit 2) raised before the first write.

1. Refuse from inside the store worktree. After `_git_toplevel` resolves the caller's top level `top`, and only when `FACTORY_INSTANCE` is unset, refuse on either of two conditions:
   1. `git -C <top> symbolic-ref -q HEAD` prints `refs/heads/factory-store`. Refuse with `factory init: <caller's directory> is inside the store checkout <top> (branch factory-store); run init from the repository root`. This holds for an unborn branch too.
   2. `instance.find()` returns an instance `found` whose config loads and has `state_dir`, and with `own = instance.own_state_root(found, cfg)`, either `top == own`, or `top` lies under `own` and `git -C <top> rev-parse --path-format=absolute --git-common-dir` and the same command at `instance.repo_root(found)` resolve to the same path. Refuse with `factory init: <caller's directory> is inside the store <own> of the instance <found>; run init from the repository root`. This catches a store checkout on a detached HEAD or another branch. When `find()` returns nothing, or the config cannot be read, this condition does not apply. A separate repository under the store has its own git common directory and is not refused.
   Each message is one line.
2. Load the config: from `instance.yaml` for an existing instance, or from the template text in memory for a new one (`_new_instance_yaml`), without writing it yet. Resolve `root` and whether it is the own store (`instance.is_own_store`). #45's fence call comes right after `root`, as #45 placed it, and stays unconditional: on a new instance it does nothing, and #45's part A.2 covers an existing instance whose store directory is not there yet. Keep the existing refusals (no `--repo-name`; a new instance on a throwaway store; `_revision()`).
3. The following applies only to the instance's own store, and only when that path does not exist. A throwaway store, where `FACTORY_STATE` names another directory, stays a plain directory, as today.
   1. Refuse if the integration branch has ever tracked a file under the path. The test is `git log -1 --format=%H <branch> -- <state_dir>` at the repo root. `<branch>` is `gitops.integration_branch` for an existing instance, and the checked-out branch for a new one, or `HEAD` when the repo root is on a detached HEAD. An unborn branch counts as never tracked. The message is one line. It names the path and that commit, says that a checkout of any older commit would overwrite a store kept there, and asks for another `state_dir`.
   2. Choose the branch source. If a local branch `factory-store` exists, use it. Otherwise count the remote-tracking refs `refs/remotes/*/factory-store`. With exactly one, use it; `git worktree add` creates the local branch from it. With more than one, refuse, naming each as `<remote>/factory-store`, and say to run `git branch factory-store <remote>/factory-store` for the chosen one and then `init` again. With none, create an orphan.
   3. Run `git worktree add <path> factory-store`, or `git worktree add --orphan -b factory-store <path>` for an orphan. The orphan form creates no commit, so it needs no git identity. A git failure here (for example, "already used by worktree") is raised as `Refused`, and nothing has been written yet.
   4. When the path lies inside the repo root, add `/<path relative to the repo root>/` to the exclude file (`git rev-parse --git-path info/exclude`), unless that line is already there.
4. Only now write the instance: `instance.yaml` for a new instance, then `context.md`, `harness.lock` and the agent files, as today. Then the store writes (`.gitignore`, `.gitattributes`, the spec store), which land in the new checkout.
5. When the own store path exists and is not the checkout of `factory-store` (`gitops.checkout_of(repo, "factory-store")`), leave it exactly as today. If it is a plain directory (not a worktree of this repository), print on stderr that the store is not on its branch and that `factory store migrate --to PATH` moves it; if it is a worktree of this repository on a detached HEAD, print that the store worktree is detached and to check out `factory-store` there.
6. The JSON output gains `store_branch`: `"factory-store"` when the own store is that branch's checkout, otherwise `null`. `written`, `created` and `agents` keep their current meanings and do not list the checkout. A second `init` changes nothing.

### B. `factory store migrate --to PATH` (new `store` subcommand group in `build_parser`)

PATH is relative to the repo root, as `state_dir` is, and it becomes the new `state_dir`. It is not on #45's read-only list, so #45's fence refuses it while a run is in flight and it is unmarked. Refusal 4 below covers a marked call.

Refusals. Each exits 2 and changes nothing (no branch, no PATH, no file touched). Check all of them before the first write:
1. The store in use is not the instance's own (`FACTORY_STATE` names another).
2. The store is already the checkout of `factory-store`, or a local branch `factory-store` exists.
3. The integration branch is not checked out at the repo root.
4. A ticket in the store has a run in flight (`in_flight` not empty). Name each run id.
5. A git worktree lies under the store (implementer worktrees, checker checkouts). Name each one.
6. `git status --porcelain -- <state_dir>` at the repo root is not empty. Name the files and ask for them to be committed on the integration branch first.
7. PATH exists, or the integration branch has ever tracked a file under it (the same test as A.3.1).
8. `instance.yaml` has no `state_dir:` line.

Steps:
1. Create the branch at one root commit: `git commit-tree <branch>:<state_dir> -m "store: carried over from <branch> at <sha>; earlier history: git log <sha> -- <state_dir>"`, then `git branch factory-store <commit>`. This uses the operator's git identity.
2. `git worktree add <PATH> factory-store`.
3. Copy every file that git ignores under the old store into the same relative path under PATH. These are run scratch directories and tripwire baselines, listed by `git ls-files --others --ignored --exclude-standard -- <state_dir>` at the repo root.
4. Verify before deleting anything. Every file listed in step 3 must exist under PATH with the same bytes, the number of files copied must equal the number listed, and `git -C <PATH> status --porcelain` must be empty. If any of these fails, remove the new worktree (`git worktree remove --force <PATH>`) and the branch (`git branch -D factory-store`), and exit 1 naming the first file that differs. The old store and the integration branch are untouched.
5. At the repo root: run `git rm -r -q --cached <state_dir>`, add `/<PATH>/` to the exclude file, and rewrite only the value on `instance.yaml`'s `state_dir:` line to PATH, keeping its comments. Then delete the old store directory.
6. Log `store.migrated` (`from`, `to`, `branch`, `carried_from`, `copied`) in the new store. Print `{"ok": true, "from", "to", "branch": "factory-store", "carried_from", "copied"}`. On stderr, remind the operator to commit the integration-branch changes, then commit the store in PATH and push `factory-store`.

It makes no commit on the integration branch and pushes nothing.

### C. Tests

Add a new file, `tests/factory/test_store_branch.py`, covering:
- A: a new store is the checkout of `factory-store`, and the integration checkout does not see it. A store commit leaves the integration branch where it was. A clone restores the store from the branch. Two remotes carrying the branch with no local branch are refused, naming both, with nothing written. A tracked path is refused with nothing written. `init` from a scratch directory inside the store worktree is refused, with no file written anywhere, both with the store on its branch and on a detached HEAD; with `FACTORY_INSTANCE` set and `FACTORY_STATE` naming a throwaway store, A.1 does not refuse it (#45's location rule still refuses an own-store write from there). `init` in a separate git repository under a run's scratch directory creates that repository's instance. A failed worktree step (the branch already checked out elsewhere) writes no instance file. An existing plain store is left alone, with `store_branch: null`. A second `init` is a no-op.
- B: one success case, with the tree carried byte for byte, ignored run files copied, `state_dir` rewritten, the old path untracked and removed, and the store found by later commands. A copy that does not match (for example, a copied file altered between step 3 and step 4 through a test hook or a monkeypatched copy) exits 1, leaves the old store and `instance.yaml` as they were, and leaves no `factory-store` branch or worktree. Every refusal, each writing nothing. A checkout of the pre-move commit leaving the new store untouched.
- The merge gate: after a store commit, a sub-ticket with passing rows merges. After a code commit to the integration branch, it is still refused.

Tests that commit set the git identity through `GIT_AUTHOR_*` and `GIT_COMMITTER_*`, because the suite runs under a throwaway HOME. Tests that run store commands with a run in flight on an own store mark them as #45's tests do.

### D. Documents

- `docs/design.md`:
  - Role-context block paragraph (line 58), the sentence listing what `.factory/` holds: "and the store" becomes the store as a git worktree of the repo's `factory-store` branch. That branch is never merged into the integration branch, so a store commit never moves it. The same sentence states that the store's path is one the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. Use the words "never tracked". Add one sentence: a command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store.
  - Piece 1 row (line 39) and "Smallest thing that works" (line 74, twice): `tickets` branch becomes the store branch `factory-store`.
  - No prompt block changes, so `docs/prompts/` is not re-copied.
- `docs/changelog.md`: the next free entry number (53 if #45's entry, 52, has landed, as planned). Put it after the last numbered entry and before the closing "Declined:" line, with numbering kept contiguous. It reads "After issue #46 (2026-10-04): …" and names `factory-store`, the worktree at the store path, the never-tracked path rule, `init`'s new store, restore and refusal from inside the store, and `store migrate`. Like every entry, it is one line, and it states the path rule with the words "never tracked" (a space, no hyphen).
- `dev/build-harness.spec.md`: every mention of the store branch as `tickets` becomes `factory-store`. That covers `` `tickets` ``, `refs/heads/tickets` and `HEAD:tickets`, on 16 lines: R5, the state line at 152, part A's `factory init`, C, F rule 3, K, items 18 and 91, and Responses. Mentions of the store's `tickets/` directory stay as they are.
- `README.md`, following its "Maintaining this page" rules:
  - "Terms used on this page" gains a "store branch" row.
  - The target bullet in "Where it runs" says the store is a checkout of `factory-store`.
  - Step 1 of "Adopting the factory in a repo" says `init` creates the store on that branch, or restores it on a clone, and refuses when more than one remote carries the branch.
  - Two new how-to subsections under "Where it runs":
    - "Committing and pushing the store": the two git commands, and that a store commit never moves the integration branch. Two cautions: `git clean -ffdx` (a doubled `-f`) in the integration checkout deletes the store worktree, uncommitted records included, while `git clean -fdx` keeps it; and run `init` from the repository root, since it refuses from inside the store.
    - "Moving an existing store onto its branch": the preconditions, `factory store migrate --to .factory/store`, and the commits afterwards. A note that checking out a commit from before the move brings back the old `.factory/state` and a `state_dir` naming it, so commands during that checkout use a stale copy until the integration branch is checked out again; the words "from before the move" appear in it. Rollback, with no run in flight and the store committed: `rm <store>/.git && git worktree prune` (never `git worktree remove`, which deletes the directory). Then move the directory back, `git add` it on the integration branch, restore `state_dir`, and remove the exclude line.
  - The "Parallel builds across tickets" paragraph under "Running many tickets" drops the clause "and committing the store to the same branch moves it too" (wrapped across two lines today), and says a store commit no longer moves the integration branch.
  - Every place that gives the live store's location names `.factory/store/`: the `.factory/` row of "Where things live", the store sentence of "Related work and history", and the log and ticket paths in the "Maintaining this page" table. The two `state/` labels in the "Where it runs" diagram become `store/`. Re-derive the ticket count and bump the status date. The how-to above may name the old path it moves from.

### Size and seams

About 470 changed lines in total: A about 70, B about 120, C about 210, D about 70. Each lettered part can be its own sub-ticket of under 400 lines. C's tests go with the part they cover. D goes last, because it describes A and B.

## Tests to change

none. No existing test asserts that an own store is a plain directory, that `init`'s `written` or `created` lists change, or that `init` succeeds with a `factory-store` checkout as its top level or from inside its own instance's store. The suite's `init` calls in fresh repositories under pytest's temporary directory are not refused, even when that directory lies inside a store, because each is a separate repository (A.1.2).

#45 (T-0024) builds first, so its tests are existing tests by then. Its approved acceptance scenarios keep their outputs (Risk, "#45's acceptance scenarios after this change"): no #45 scenario's expected output changes, though one, "Marked writes from a run's scratch directory or a worktree directory are refused, init included", still runs `init` from a run's scratch directory and is now refused by A.1 rather than by #45's location rule. #45's suite file is not written yet. If one of its tests runs `init` from inside a store's `runs/` and asserts the location rule's message text rather than exit 2 with nothing written, it will see A.1's message instead. The implementer reports that test rather than editing it. The same applies to any other existing test that breaks.

=== specs/store-setup/spec.md
## ADDED Requirements

### Requirement: A new instance's store is a checkout of its own branch
`factory init` SHALL create a missing own store as a git worktree of branch `factory-store`, which the integration checkout does not see. It SHALL check that branch out when it already exists locally or on exactly one remote, so that a store commit never moves the integration branch.

#### Scenario: init creates the store on the factory-store branch, out of the integration checkout's sight
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; echo "branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/state/')")`
- THEN it prints `branch=factory-store seen_by_main=0`

#### Scenario: init on a clone restores the store from the pushed branch
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/src && cd $T/src && git commit -q --allow-empty -m init && $B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T/src $T/c && cd $T/c && rm -rf .factory/state && $B init >/dev/null 2>&1; echo "exit=$? branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) restored=$(ls .factory/state/decisions.md 2>/dev/null | grep -c .)")`
- THEN it prints `exit=0 branch=factory-store restored=1`

### Requirement: init refuses when more than one remote carries the store branch
`factory init` MUST refuse with exit 2, creating no store and no local branch, when the own store is missing, no local `factory-store` exists and more than one remote carries it; the refusal MUST name each `<remote>/factory-store`.

#### Scenario: init on a clone with two remotes carrying the store branch refuses and names both
- GIVEN the three fixture files written by the block below, run once at column 0 as shown. Every later scenario of this change that names them reuses them.

```sh
cat > ${TMPDIR:-/tmp}/t0025-old.sh <<'EOF'
# Sourced from the repo root: a target whose store is a plain directory tracked on main, as both
# instances keep it today. Leaves the shell in the target; PRE is the commit that last tracked it.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
mkdir -p .factory/state && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
git add -A && git commit -q -m "instance, with its store on main" && PRE=$(git rev-parse HEAD)
EOF
cat > ${TMPDIR:-/tmp}/t0025-b1.sh <<'EOF'
# Sourced from the repo root: a target whose store at .factory/state is already a git worktree of
# an unborn factory-store branch, built with git alone (so it is the same layout whatever the
# harness does), then given an instance by init. Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
git worktree add -q --orphan -b factory-store .factory/state && echo /.factory/state/ >> "$(git rev-parse --git-path info/exclude)"
$B init --repo-name demo >/dev/null 2>&1
EOF
cat > ${TMPDIR:-/tmp}/t0025-gate.sh <<'EOF'
# Sourced from the repo root: a target made by init, its instance committed on main, and T-0001 on
# branch factory/T-0001 with reviewer APPROVE, verifier VERIFIED and gate PASS on its head H.
# Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
$B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance
git checkout -q -b factory/T-0001 && echo x > x.txt && git add x.txt && git commit -q -m work
H=$(git rev-parse HEAD) && git checkout -q main
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
$B ticket set T-0001 status=checks-in-flight branch=factory/T-0001 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/rv.md
$B results record T-0001 --head $H --role verifier --output $T25/v.md --run run-0001-verifier >/dev/null
$B results record T-0001 --head $H --role reviewer --output $T25/rv.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T25/tgt $T25/c && cd $T25/c && git remote add nas $T25/tgt && git fetch -q nas && $B init >/dev/null 2>$T25/err; echo "exit=$? store=$([ -e .factory/state ] && echo written || echo none) local_branch=$(git branch --list factory-store | grep -c .) names=$(grep -c 'origin/factory-store' $T25/err),$(grep -c 'nas/factory-store' $T25/err)")`
- THEN it prints `exit=2 store=none local_branch=0 names=1,1`

### Requirement: init refuses to run from inside the store checkout
`factory init`, run with `FACTORY_INSTANCE` unset from a directory whose git top level is a checkout of `factory-store`, or is the store of the instance found from that directory or a checkout of the same repository inside that store, MUST refuse with exit 2 and write nothing, whichever commit the store has checked out, so that it never creates an instance inside the live store; other commands run from there SHALL still find the live instance, and `init` in a separate repository under the store SHALL still create that repository's instance.

#### Scenario: init from a scratch directory inside the store checkout refuses and leaves the store unchanged
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init from the store checkout on a detached HEAD refuses
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git -C .factory/state checkout -q --detach && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? detached=$(git -C $T25/tgt/.factory/state symbolic-ref -q HEAD >/dev/null && echo no || echo yes) phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 detached=yes phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init in a separate repository under a run's scratch directory still creates its instance
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && cd .factory/state/runs/run-0001-triage/scratch && git init -q -b main other && cd other && git commit -q --allow-empty -m init && $B init --repo-name other >/dev/null 2>&1; echo "exit=$? instance=$([ -f .factory/instance.yaml ] && echo written || echo none) live=$(cd $T25/tgt && $B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 instance=written live=ready-for-triage`

### Requirement: init refuses a store path the integration branch has tracked
`factory init` MUST refuse with exit 2, writing nothing and naming the path, when it would create the own store at a path under which the integration branch has ever tracked a file.

#### Scenario: init refuses a once-tracked store path and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/tgt && cd $T/tgt && mkdir -p .factory/state && echo old > .factory/state/old.md && git add -A && git commit -q -m "old store" && git rm -q -r .factory/state && git commit -q -m "store removed" && $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e .factory ] && echo written || echo none) names_path=$(grep -q '\.factory/state' $T/err && echo 1 || echo 0)")`
- THEN it prints `exit=2 instance=none names_path=1`

### Requirement: store migrate moves a tracked store onto its branch and keeps every record
`factory store migrate --to PATH` on an idle, fully committed own store that is tracked on the integration branch SHALL do all of the following:
- put the store's last committed tree on a new `factory-store` branch, checked out at PATH;
- copy the store's ignored run files to PATH, and verify the copy before removing anything;
- untrack and remove the old path;
- set `state_dir` to PATH, so that later commands use the moved store.

#### Scenario: store migrate carries the store to factory-store at the new path
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && mkdir -p .factory/state/runs/run-0001-triage/scratch && echo n > .factory/state/runs/run-0001-triage/scratch/n.txt && $B store migrate --to .factory/store >/dev/null 2>&1; echo "exit=$?"; echo "branch=$(git -C .factory/store symbolic-ref --short HEAD 2>/dev/null) same_tree=$([ "$(git rev-parse -q --verify 'factory-store^{tree}')" = "$(git rev-parse $PRE:.factory/state)" ] && echo yes || echo no) scratch=$(cat .factory/store/runs/run-0001-triage/scratch/n.txt 2>/dev/null) old=$([ -e .factory/state ] && echo kept || echo gone) main_tracks=$(git ls-files .factory/state | grep -c .) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/store/')"; echo "state_dir=$(sed -n 's/^state_dir: *//p' .factory/instance.yaml) ticket=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0`, then `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0`, then `state_dir=.factory/store ticket=ready-for-triage`

### Requirement: store migrate refuses while the store is in use or uncommitted
`factory store migrate` MUST refuse with exit 2, creating no branch and no new path, when a store file is uncommitted or a run is in flight. The refusal MUST name the uncommitted files or the runs in flight.

#### Scenario: store migrate refuses an uncommitted store and a run in flight
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && echo edit >> .factory/state/decisions.md; $B store migrate --to .factory/store >/dev/null 2>$T25/e1; echo "uncommitted: exit=$? names=$(grep -c 'decisions.md' $T25/e1) branch=$(git branch --list factory-store | grep -c .)"; git checkout -q -- .factory/state/decisions.md && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git add -A && git commit -q -m "run started"; FACTORY_DISPATCH=1 $B store migrate --to .factory/store >/dev/null 2>$T25/e2; echo "in flight: exit=$? names=$(grep -c 'run-0001-triage' $T25/e2) branch=$(git branch --list factory-store | grep -c .) new=$([ -e .factory/store ] && echo written || echo none)")`
- THEN it prints `uncommitted: exit=2 names=1 branch=0`, then `in flight: exit=2 names=1 branch=0 new=none`

### Requirement: A checkout of an older commit leaves a moved store untouched
After `store migrate`, checking out a commit from before the move in the integration checkout, and then checking out the integration branch again, MUST leave every file of the moved store as it was, uncommitted ones included.

#### Scenario: A checkout of an older commit leaves the moved store untouched
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B store migrate --to .factory/store >/dev/null 2>&1 && git commit -q -a -m "store moved to its branch"; (echo live > .factory/store/live.md) 2>/dev/null; git checkout -q $PRE 2>/dev/null && git checkout -q main 2>/dev/null; echo "live=$(cat .factory/store/live.md 2>/dev/null || echo lost) on=$(git symbolic-ref --short HEAD)")`
- THEN it prints `live=live on=main`

=== specs/merge-gate/spec.md
## ADDED Requirements

### Requirement: A store commit does not hold back a merge
On an instance whose store is the checkout of `factory-store`, a store commit made after a sub-ticket's checks SHALL NOT stop `factory merge` from merging that sub-ticket.

#### Scenario: A sub-ticket merges after a store commit
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: rows recorded"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=0 refused=0`

### Requirement: A commit to the integration branch still holds back a merge
`factory merge` MUST still refuse, with `head does not contain main`, a sub-ticket whose head does not contain a commit made to the integration branch after its checks.

#### Scenario: A sub-ticket is refused after a code commit to main
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && echo y > y.txt && git add y.txt && git commit -q -m "code on main"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=2 refused=1`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule, and the build spec SHALL call the store branch only `factory-store`. `docs/changelog.md` SHALL gain one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch, `factory store migrate`, the `git clean -ffdx` hazard and a checkout from before the move, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location. The change MUST add no whitespace errors.

#### Scenario: The design doc names the store branch and the path rule
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
- THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`

#### Scenario: The build spec calls the store branch factory-store
- WHEN `(Q=$(printf '\140'); echo "old_name=$(grep -c "${Q}tickets${Q}\|refs/heads/tickets\|HEAD:tickets" dev/build-harness.spec.md) new_name=$(grep -c 'factory-store' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints `old_name=0 new_name=1`

#### Scenario: The changelog records the store branch in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The README describes the store branch and the move
`old_cost` joins the page into one line first, because the retired clause is wrapped across two lines. `old_refs` counts only the places that give the live store's location, so a how-to may still name the path a store moves from.
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`

#### Scenario: The store-branch change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
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
