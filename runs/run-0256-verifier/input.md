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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0256-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0256-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0256-verifier/wt` (branch `factory/T-0025.1`, base `0b1abad474cb9c583ed8445fc33617f9f0bdc37b`, head `d001090e9b0a535d55599ce5819c497572e07cf4`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

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

## PR description (the implementer's output)

Sub-ticket: T-0025.1 (T-0025-A, parent T-0025 approved spec v5, issue #46). Branch `factory/T-0025.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0025.1`, on base `0b1abad`. Commits: `fdf4436` and `939552d` (run-0241, the first build), then `878c68b` and `d001090` (this run).

**This change is ready for review. The full suite now passes: 280 of 280 tests.** The first build of this sub-ticket (run-0241) was blocked on two existing tests. Those tests checked the wrong message after the change: they still expected the older refusal text, although `init` was still refused with exit 2 and wrote nothing. A human ruling then allowed exactly those two tests to change. This run makes that change and nothing else in the tests, re-derives one README number, and re-runs every acceptance command and both gates.

## What changed

Terms used below:
- **store**: the directory of files where the factory keeps its ticket records.
- **instance**: a target repo's `.factory/` directory, the factory's per-repository setup.
- **integration branch**: the branch finished work merges into. Here that is `main`.
- **store branch**: `factory-store`, the branch the store now lives on. It is checked out as a git worktree (a second working directory of the same repository) at the store's path.

**This run (`878c68b`, `d001090`):**
- `tests/factory/test_live_store_guard.py`, in exactly the two tests the human ruling names. Each test now checks the `init` call against the new refusal (part A.1). The checks are: exit code 2, A.1's message (`is inside the store checkout <store> (branch factory-store); run init from the repository root`), and the usual JSON error shape. Before, each test checked for the location-rule text that T-0024 (#45) added. Every other assertion in the two tests is unchanged. That includes the non-`init` commands, which still check the location-rule text, and each test's before/after store snapshot.
- `README.md:481`: the ticket count is now 52. That is what README's own check, `ls .factory/state/tickets | wc -l`, prints today. Run-0241 had written 49, and tickets have been added since.

**Already built in run-0241 and unchanged here:**
- **Part A: `init` (`factory/cli.py` `init_cmd`, with helpers in `factory/gitops.py`).**
  - A.1: when `FACTORY_INSTANCE` is unset, `init` refuses in two cases. The first is when the caller's git top level has `factory-store` checked out. The second is when that top level is the store of the instance found by walking up from the caller, or lies under that store in the same repository (the same `--git-common-dir`).
  - A.2: the config is loaded in memory. #45's fence call stays right after `root` and runs unconditionally.
  - A.3: this applies only to a missing own store. `init` refuses a path the integration branch has ever tracked. It then checks out the store branch: a local branch if one exists, or exactly one remote's copy. It refuses when more than one remote carries the branch and names each one. With no branch anywhere, it creates an orphan. Any git failure becomes a refusal before anything is written. It also adds the exclude line.
  - A.4: `instance.yaml` and the other instance files are written only after A.1 to A.3.
  - A.5: an existing store that is not the `factory-store` checkout is left alone. A hint on stderr tells a plain directory apart from a detached store worktree.
  - A.6: the JSON output gains `store_branch`.
- **Part C:** `tests/factory/test_store_branch.py`, 15 new tests. These cover the A items and the merge gate.
- **Part D:**
  - `docs/design.md`: the piece 1 row, "Smallest thing that works" (twice), and the role-context paragraph, which now has "never tracked" and the code-checkout sentence. No prompt block changed.
  - `dev/build-harness.spec.md`: all 16 store-branch mentions of `tickets` now say `factory-store`.
  - `docs/changelog.md`: entry 53.
  - `README.md`: the "store branch" term, the target bullet, adoption step 1, the "Committing and pushing the store" how-to with both cautions, the "Parallel builds" paragraph, and the status date.

The diff from base `0b1abad` touches 8 files, with 524 insertions and 54 deletions.

## Acceptance results

How I ran them: from the worktree root, through the HOME wrapper, under `bash`. `TMPDIR` pointed at a fresh `/tmp/t0025acc.*` directory, which lies outside every git repository. The parent's GIVEN block was written there verbatim, and the directory was removed afterwards. Script: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0247-implementer/scratch/acc.sh`.

"Before" is base `0b1abad`, as run-0241 captured it. Code has not changed since. "After" is this run, on `878c68b` for the scenario rows and on `d001090` for the gate and the last three rows.

| Scenario | Kind | Before | After |
|---|---|---|---|
| init creates store on factory-store | NEW | `branch=main seen_by_main=6` | `branch=factory-store seen_by_main=0` |
| clone restores store | NEW | git's "nothing to commit", then `exit=1 branch=main restored=1` | `exit=0 branch=factory-store restored=1` |
| two remotes refused | NEW | `exit=0 store=written local_branch=0 names=0,0` | `exit=2 store=none local_branch=0 names=1,1` |
| init from scratch inside store | NEW | `exit=0 phantom=written store=changed` / `found=` | `exit=2 phantom=none store=unchanged` / `found=ready-for-triage` |
| init from detached store | NEW | `exit=0 detached=yes phantom=written store=changed` / `found=` | `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage` |
| separate repo under scratch | REGRESSION | — | `exit=0 instance=written live=ready-for-triage` |
| once-tracked path refused | NEW | `exit=0 instance=written names_path=0` | `exit=2 instance=none names_path=1` |
| merge after store commit | NEW | `exit=2 refused=1` | `exit=0 refused=0` |
| refused after code commit | REGRESSION | — | `exit=2 refused=1` |
| design doc | NEW | `store_branch=0 tickets_branch=2 never_tracked=0` | `store_branch=1 tickets_branch=0 never_tracked=1` |
| build spec | NEW | `old_name=16 new_name=0` | `old_name=0 new_name=1` |
| changelog contiguous | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `1` |
| old plain store (intermediate) | NEW | `exit=0 branch=0 hint=0 dirty=0` | `exit=0 branch=1 hint=1 dirty=0` |
| README (intermediate) | NEW | `store_branch=0 ffdx=0 old_cost=1` | `store_branch=1 ffdx=1 old_cost=0` |
| changelog last entry (intermediate) | NEW | `52. After issue #45 (2026-10-0` | `53. After issue #46 (2026-10-0` |
| harness suite (with `TMPDIR`) | REGRESSION | — | `280 passed in 223.39s` |
| whitespace | REGRESSION | — | `exit=0` |

What the table shows:
- Every "after" matches its THEN.
- Every NEW "before" failed as the spec said it would.
- Both REGRESSION scenarios print what they printed on the base.

Gate commands, run exactly as written:
- `git diff --check main...HEAD`: prints `exit=0` on `d001090`. The change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: prints `280 passed in 223.51s` on `878c68b`, and `280 passed in 223.88s` on `d001090`, the final head. No test fails.
- `tests/factory/test_live_store_guard.py` alone: `11 passed`. Both changed tests pass.

## Tests added/changed

- Added (run-0241): `tests/factory/test_store_branch.py`, 15 tests. On the base, 14 of them fail and one passes: the regression that a code commit is still refused. All 15 pass on HEAD.
- Changed (this run, under the human ruling):
  - `test_live_store_guard.py::test_marked_writes_from_a_runs_scratch_directory_are_refused`
  - `test_live_store_guard.py::test_marked_writes_from_under_worktrees_are_refused`

  The change was needed for this reason. Each test runs `init` from inside a store's `runs/` or `worktrees/`, and the store is now a `factory-store` checkout. So A.1 refuses the call before #45's location rule runs. The behaviour the tests protect still holds: the call exits 2, and the before/after snapshot of `.factory` and `.claude` is unchanged. Only the refusal message differs. Each test still checks its non-`init` commands against the location-rule text.

## Known gaps and uncertainties

- **The two edited tests check part of A.1's message, not all of it.** They do not compare the caller's directory at the start of the message. The harness gets that directory from `instance.caller_cwd()`, which may come back resolved or unresolved, so matching it exactly would make the tests brittle. The tests do check the store path, the branch and the instruction.
- **The A.5 hint names a command that does not exist yet.** It points to `factory store migrate --to PATH`, which comes with T-0025.2. Until that merges, the hint is ahead of the code. The spec requires the hint (A.5), and the intermediate check expects `hint=1`.
- **`store_branch` describes only the own store.** With `FACTORY_STATE` naming a throwaway store, it is always `null`. That is my reading of "when the own store is that branch's checkout".
- **One case raises an error instead of counting as never tracked.** For an existing instance, A.3.1 uses `gitops.integration_branch`. When no branch is configured and HEAD is unborn at the repo root, that call raises git's error as a refusal. A new instance on an unborn branch is handled.
- **The README describes behaviour no real ticket has used yet.** README's "Ground truth only" rule says a thing should appear only after it has run. Spec part D requires the "Committing and pushing the store" section anyway. The section says that both existing stores are still plain directories.
- **The README ticket count, 52, includes tickets nobody has committed yet.** The `ls` in the live dev checkout includes ticket files the operator has not committed. The tracked copy at `0b1abad` holds 46 tickets.
- **The diff is larger than the parent estimated.** It has 524 insertions and 54 deletions. The parent estimated about 70 lines for part A and 210 for part C. The test file alone is 296 lines.
- **My scratch files are not all in the scratch directory.** The acceptance fixtures used `/tmp/t0025acc.*`, which I removed, because the plan requires a `TMPDIR` outside every git repository. The HOME wrapper also leaves empty `mktemp -d` directories in the system temp directory.

## Out-of-scope observations

- `gitops.integration_branch` raises an error on an unborn HEAD when no branch is configured. That affects every caller, not only `init`.
- Some lines in README still give `.factory/state/` as the store's location: the "Where things live" row and the "Maintaining this page" table. Those lines belong to T-0025.2.

## Responses to findings

No review findings yet. Response to the human ruling on run-0241's escalation: FIXED in `878c68b`. Only the two named tests changed, and only their `init` assertions changed. A.1's ordering and message are as the spec states.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN on this head, and both gate commands passed on the final commit `d001090`.
ESCALATIONS: none

## Diff `0b1abad474cb9c583ed8445fc33617f9f0bdc37b...d001090e9b0a535d55599ce5819c497572e07cf4`

diff --git a/README.md b/README.md
index fca1ac0..c2579f0 100644
--- a/README.md
+++ b/README.md
@@ -73,6 +73,7 @@ a command is allowed.
 | current truth | one document per capability saying what the system does now; the pipeline keeps it |
 | target | a repo the factory works on |
 | instance | a target's `.factory/` directory: its config, its briefing for the roles, its store |
+| store branch | `factory-store`, the target's branch for its store; checked out as a git worktree at the store's path and never merged into the integration branch |
 | runtime | the pinned checkout of the harness that runs tickets; distinct from the dev checkout |
 
 ## How a ticket moves
@@ -163,9 +164,13 @@ Three places:
   mid-run.
 - Each **target** holds only a `.factory/` directory, its instance: `instance.yaml` (config),
   `context.md` (the briefing every role reads first), the store, and `harness.lock`, the one
-  harness commit this target has agreed to run with. Today this repo is the only target on the
-  runtime; a chat-bot repo is a target that still runs its own in-tree copy of the harness until
-  its cutover.
+  harness commit this target has agreed to run with. The store is the target's record of every
+  ticket. A store that `factory init` creates is a git worktree of the store branch,
+  `factory-store`, at a path the integration branch has never tracked, so committing the store
+  never moves the integration branch. This repo's store and the chat-bot repo's predate that and
+  are still plain directories committed on their integration branches. Today this repo is the only
+  target on the runtime; a chat-bot repo is a target that still runs its own in-tree copy of the
+  harness until its cutover.
 
 ```mermaid
 flowchart TB
@@ -252,9 +257,15 @@ the dev checkout is where you merge.
 
 From inside the target repo, with `R` the runtime (`~/dev/spec-factory-harness`):
 
-1. `$R/bin/factory init --repo-name NAME`. Creates `.factory/` at the repo's top level
-   (`instance.yaml`, `context.md`, `harness.lock`, the store) and copies the role agents into
-   `.claude/agents/`. Idempotent.
+1. `$R/bin/factory init --repo-name NAME`, from the repository root. Creates `.factory/` at the
+   repo's top level (`instance.yaml`, `context.md`, `harness.lock`) and copies the role agents into
+   `.claude/agents/`. It creates the store as a checkout of a new `factory-store` branch, and adds
+   the store's path to the repo's git exclude file so the integration checkout does not see it.
+   On a clone where `factory-store` already exists, locally or on one remote, it checks that
+   branch out instead, which restores the store. When more than one remote carries the branch it
+   refuses and names each; pick one with `git branch factory-store <remote>/factory-store` and run
+   `init` again. It also refuses from inside the store, and at a store path the integration branch
+   has ever tracked. Idempotent.
 2. Restart the Claude Code session so the agents register.
 3. Fill in `.factory/context.md`, the briefing every role reads first: which repo this is, how to
    run its tests, what kind of request to expect. Set `gate_commands` and `protected_paths` in
@@ -263,6 +274,28 @@ From inside the target repo, with `R` the runtime (`~/dev/spec-factory-harness`)
 
 The repo is now a target. "Starting a run" is the rest.
 
+### Committing and pushing the store
+
+The store is its own checkout of `factory-store`, so its records are committed there, never on the
+integration branch. Set `S` to the store's path (`state_dir` in `instance.yaml`; `.factory/state`
+for a new instance), then:
+
+```
+git -C "$S" add -A && git -C "$S" commit -m "store: <what changed>"
+git push origin factory-store
+```
+
+A store commit never moves the integration branch, so it never sends a sub-ticket that is waiting
+to merge back for a catch-up run.
+
+Two cautions:
+
+- In the integration checkout, `git clean -fdx` keeps the store, because git skips a directory
+  that holds its own `.git`. `git clean -ffdx`, with a doubled `-f`, deletes it, uncommitted
+  records included.
+- Run `factory init` from the repository root. From inside the store it refuses, because there
+  it would build a second instance inside the live store.
+
 ## Starting a run
 
 A Claude Code session in the target repo asks the runtime where things are:
@@ -303,9 +336,9 @@ real ticket.
 
 **Parallel builds across tickets have not been tried.** Each sub-ticket builds in its own worktree,
 merges into the integration branch one at a time under a lock, and gets a catch-up run if the branch
-moved under it. Two builds at once also move the branch under each other, and committing the store
-to the same branch moves it too; both cost catch-up runs. Until a real run shows the cost, run one
-build at a time per target.
+moved under it. Two builds at once also move the branch under each other, which costs catch-up runs.
+A store committed on its store branch no longer moves the integration branch. Until a real run
+shows the cost, run one build at a time per target.
 
 **Moving the runtime** happens only when no build is in flight on any target, because every target
 runs from the same runtime. Each target's runner then accepts the new revision between its builds.
@@ -443,9 +476,9 @@ A). Instance A still runs its in-tree copy of the harness; its cutover to the sh
 planned, not done. Open work named above: `factory report`
 (#17); current-truth seeding and the README overview this page stands in for (#21); per-role
 effort (#22); prompt changes borrowed from the ponytail project (#20); the documentation standard
-this page was rewritten to (#23). Each run's own scratch directory came from #35. The design
+this page was rewritten to (#23). Each run's own scratch directory came from #35, and the store branch from #46. The design
 document is `docs/design.md`, its changelog `docs/changelog.md`; the working documents from
-building the harness are under `dev/`; the issue index is `dev/issues.md`. The store holds 18 tickets at `.factory/state/`; the runtime is at
+building the harness are under `dev/`; the issue index is `dev/issues.md`. The store holds 52 tickets at `.factory/state/`; the runtime is at
 `~/dev/spec-factory-harness`, revision `010d1b0`, equal to this repo's `harness.lock`.
 
 ## Maintaining this page
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 46feb11..4019123 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -114,7 +114,7 @@ Rows marked "ruling" are decided; rows marked "default" are mine and repeat unde
 | R2 | Git server | Bare repo `~/factory-remote/nanobot.git`, pre-receive hook, one deploy key per role; GitHub remote untouched | ruling + addendum 1 |
 | R3 | **Dispatcher** | Claude Code **Workflow tool**: `factory/workflows/intake.js` and `factory/workflows/build.js`; fresh context per `agent()`; join, round counters and routing are plain code in the script. The three v0 limits of doc §Harness table piece 2 apply: (1) no filesystem or clock, so the clerk calls the store CLI and the guards live in the CLI (B); (2) the piece-3 kill is post-hoc (I.5); (3) fresh context, not isolation: every `agent()` call shares the session's checkout, credentials and git identity (Risk R1, R6). The cron/`factory loop` dispatcher of v1 is **deferred to a later ticket** | addendum 1 |
 | R4 | Isolated run | Implementer and retro: `agent(..., {isolation: 'worktree'})` on `~/factory/clone`; checkers: fresh context, read + shell, checkout of the head made by the clerk in `~/factory/runs/<run_id>/wt`; Docker deferred | ruling + E7 |
-| R5 | Tracker / human surface | `tickets/` YAML + `queue.md` on branch `tickets` of the bare repo (v3 called it `factory/state`; same checkout `~/factory/state`); approved specs also exported to `knowledge_vault/sanitized_specs/<ID>.md` | ruling + addendum 2 (location: default) |
+| R5 | Tracker / human surface | `tickets/` YAML + `queue.md` on branch `factory-store` of the bare repo (v3 called it `factory/state`; same checkout `~/factory/state`); approved specs also exported to `knowledge_vault/sanitized_specs/<ID>.md` | ruling + addendum 2 (location: default) |
 | R6 | Permissions | Never `bypassPermissions` (nor `dontAsk`). Role agent definitions carry `tools:` allowlists: checkers and read-only authors Read/Grep/Glob/Bash, no Edit/Write; implementer and retro add Edit/Write; clerk Bash only, allowed `Bash(factory *)`, `Bash(git *)`. Real runs: the operator's session runs `/factory` with `--permission-mode acceptEdits` and `--allowedTools "Bash(factory *)" "Bash(git *)" "Bash(pytest *)" "Bash(ruff *)" "Bash(mypy *)" Read Grep Glob Edit Write Skill Workflow`; anything outside that list prompts the operator (the session is attended in v0). With the per-role keys (E) this is the fence for v0 limit (3), shared identity and credentials. See Risk R6 | ruling; mode/allowlist: default (critic S3) |
 | R7 | Faux-SPEC input / sanitized output | `knowledge_vault/specs/*.md` → `knowledge_vault/sanitized_specs/` | addendum 2 |
 | D1 | Trunk | The bare repo's `main`, seeded once from `feat/lionbot-v3` by `factory init` | default |
@@ -149,7 +149,7 @@ pyproject.toml                                adds the `factory` console script
 AGENTS.md                                     adds a "Factory" section (A)
 ```
 
-State on branch `tickets` of the bare repo (the ticket store, doc §Harness table piece 1; never merged into `main`, never subject to the merge gate; v3: `factory/state`), checked out at `~/factory/state`: `tickets/`, `specs/`, `openspec/`, `decisions.md`, `requests/`, `results/`, `approvals/`, `log/`, `runs/`, `audits/`, `retros/`, `queue.md`. Keys in `~/factory-remote/keys/` (part E).
+State on branch `factory-store` of the bare repo (the ticket store, doc §Harness table piece 1; never merged into `main`, never subject to the merge gate; v3: `factory/state`), checked out at `~/factory/state`: `tickets/`, `specs/`, `openspec/`, `decisions.md`, `requests/`, `results/`, `approvals/`, `log/`, `runs/`, `audits/`, `retros/`, `queue.md`. Keys in `~/factory-remote/keys/` (part E).
 
 ### A. Skeleton, agent definitions, entry skill
 
@@ -157,7 +157,7 @@ State on branch `tickets` of the bare repo (the ticket store, doc §Harness tabl
 - `factory/cli.py`: subcommands per part; exit 0 success, 2 refused precondition, 1 error; one audit event (C) per state change.
 - `factory render`: reads `docs/design.md`, which is in the same repo as the harness (`render` reads no other path and still has no `--doc` option), and writes `docs/prompts/` and the `agents/` templates from its prompt blocks, plus **one added rule in the Triage and Spec-writer definitions** (addendum 2): "Acceptance items describe behaviour (a command a user or operator could run, or Given/When/Then) and never name a test function, class, or internal symbol; symbols belong under Root cause and Proposed change." The placeholders (`{repo name}`, protected paths, `{2}`, `{400}`, `{gate commands}`, `{3}`, `{5}`, `{force-push allowed}`) are filled per instance from `.factory/instance.yaml` when a run starts; `{writing standard}` is filled at the same time from the running harness checkout, not from `instance.yaml`, with the absolute path of its `docs/writing.md`, and `{coding standard}`, in the implementer and code-reviewer prompts, with the absolute path of its `docs/coding.md`. The doc text itself is copied verbatim and otherwise never edited by this ticket; `factory render --check` diffs the rendered bodies back against `docs/design.md` (the verbatim check the plan's BH-4 cites; item 82).
 - `.claude/skills/factory/SKILL.md`: how to run `factory intake`, then `Workflow({scriptPath: 'factory/workflows/intake.js', args: {ticket: ID, stubs?: dir}})`, approve at the gate, then `Workflow({scriptPath: 'factory/workflows/build.js', args: {ticket: ID}})`; the human commands (`queue`, `approve-*`, `request-changes`, `resolve`, `merge`, `gate-run`, `audit-sample`, `retro`), all run with `FACTORY_KEY` set (B). Not verified: whether the Workflow registry can address these as named workflows; `scriptPath` is what the reference documents, so that is what the skill uses.
-- `factory init`: creates `~/factory-remote/nanobot.git` (bare), seeds `main` from `feat/lionbot-v3`, creates the `tickets` branch and its checkout, mints keys (E), installs the hook (`factory install-hook`: copies the installed package to `~/factory-remote/hook-env/`, writes the shim with an absolute `FACTORY_HOOK_PYTHON`, so a pushed edit to `factory/hook.py` changes nothing until a human reinstalls). It never touches `knowledge_vault/ProjectNotes/SPEC_MAINTENANCE_WORKFLOW.md`, `webui/package-lock.json`, `port_state.json`, or `scripts/` (E9).
+- `factory init`: creates `~/factory-remote/nanobot.git` (bare), seeds `main` from `feat/lionbot-v3`, creates the `factory-store` branch and its checkout, mints keys (E), installs the hook (`factory install-hook`: copies the installed package to `~/factory-remote/hook-env/`, writes the shim with an absolute `FACTORY_HOOK_PYTHON`, so a pushed edit to `factory/hook.py` changes nothing until a human reinstalls). It never touches `knowledge_vault/ProjectNotes/SPEC_MAINTENANCE_WORKFLOW.md`, `webui/package-lock.json`, `port_state.json`, or `scripts/` (E9).
 - `AGENTS.md`: the layout, the gates, and that `.claude/agents/factory-*`, `.claude/skills/factory*` and `factory/prompts/**` are guardrail paths.
 
 ### B. Ticket store (piece 1), requests, change proposal (piece 5)
@@ -208,7 +208,7 @@ CLI (the **store CLI** of doc §Harness table piece 1 — read, transition, reco
 
 ### C. Audit log and run artifacts (piece 10)
 
-`log/<YYYY-MM>.jsonl` and `runs/<run_id>/{meta.yaml,input.md,system-prompt.txt,output.md}` on `tickets`. Events: `request.created`, `ticket.created`, `ticket.transition`, `run.started`, `run.finished`, `run.killed`, `result.recorded`, `result.stale-discarded`, `approval.recorded`, `merge.refused`, `merge.done`, `escalation.queued`, `reply.sent`, `human.resolved`, `harness-bug`, `spec.exported`, `change.pinned`, `change.archived`, `decision.recorded`. `meta.yaml`: role, ticket, head, base, model, spec_version, budget_usd, resolution, started, finished, wall_s, status, escalations_note, workflow_run_id. Append-only enforced by the hook (F.3). `factory log tail [-n N] [--ticket ID] [--event E]`.
+`log/<YYYY-MM>.jsonl` and `runs/<run_id>/{meta.yaml,input.md,system-prompt.txt,output.md}` on `factory-store`. Events: `request.created`, `ticket.created`, `ticket.transition`, `run.started`, `run.finished`, `run.killed`, `result.recorded`, `result.stale-discarded`, `approval.recorded`, `merge.refused`, `merge.done`, `escalation.queued`, `reply.sent`, `human.resolved`, `harness-bug`, `spec.exported`, `change.pinned`, `change.archived`, `decision.recorded`. `meta.yaml`: role, ticket, head, base, model, spec_version, budget_usd, resolution, started, finished, wall_s, status, escalations_note, workflow_run_id. Append-only enforced by the hook (F.3). `factory log tail [-n N] [--ticket ID] [--event E]`.
 
 ### D. Commit-bound results table (piece 6)
 
@@ -222,7 +222,7 @@ CLI (the **store CLI** of doc §Harness table piece 1 — read, transition, reco
 
 ```yaml
 roles:
-  harness:     {may_push: [refs/heads/main, refs/heads/tickets]}
+  harness:     {may_push: [refs/heads/main, refs/heads/factory-store]}
   implementer: {may_push: [refs/heads/ticket/*]}
   retro:       {may_push: [refs/heads/retro/*]}
   reviewer: {may_push: []}   verifier: {may_push: []}   triage: {may_push: []}
@@ -234,11 +234,11 @@ One deploy key per identity that may push (`harness`, `implementer`, `retro`, `d
 
 ### F. Pre-receive hook: permissions, merge gate, guardrail and protected paths (pieces 4, 7, 8)
 
-Runtime: `factory/hooks/pre-receive` is a `#!/bin/sh` shim installed into `~/factory-remote/nanobot.git/hooks/` by `factory install-hook`; it `exec`s the hook-env python with `-m factory.hook`, cwd = the bare repo. The hook reads **only server-side state**: `factory/identities.yaml` and `factory/paths.yaml` via `git cat-file -p refs/heads/main:<path>` as stored **before** the push; `factory/config.yaml` (`force_push_allowed`) the same way; `tickets/`, `results/`, `approvals/` via `refs/heads/tickets` as stored before the push. Nothing is read from the pushed objects except the diff being judged. For each `old new ref` on stdin, identity `P` = `$FACTORY_IDENTITY` (unset → `anonymous`):
+Runtime: `factory/hooks/pre-receive` is a `#!/bin/sh` shim installed into `~/factory-remote/nanobot.git/hooks/` by `factory install-hook`; it `exec`s the hook-env python with `-m factory.hook`, cwd = the bare repo. The hook reads **only server-side state**: `factory/identities.yaml` and `factory/paths.yaml` via `git cat-file -p refs/heads/main:<path>` as stored **before** the push; `factory/config.yaml` (`force_push_allowed`) the same way; `tickets/`, `results/`, `approvals/` via `refs/heads/factory-store` as stored before the push. Nothing is read from the pushed objects except the diff being judged. For each `old new ref` on stdin, identity `P` = `$FACTORY_IDENTITY` (unset → `anonymous`):
 
-1. **Identity.** Human: `refs/heads/tickets`, `refs/heads/ticket/*`, `refs/heads/retro/*`, `refs/heads/revert/*`; refused on `main` (`refs/heads/main: identity daniel may not push`). Role: only its `may_push`, else `refs/heads/X: identity P may not push`. `anonymous`: all refused.
+1. **Identity.** Human: `refs/heads/factory-store`, `refs/heads/ticket/*`, `refs/heads/retro/*`, `refs/heads/revert/*`; refused on `main` (`refs/heads/main: identity daniel may not push`). Role: only its `may_push`, else `refs/heads/X: identity P may not push`. `anonymous`: all refused.
 2. **`refs/heads/ticket/<ID>`** by `implementer`: refused unless `tickets/<ID>.yaml` `in_flight` names a run with role `implementer` (`ticket/<ID>: no implementer run in flight`). Deletion refused; non-fast-forward refused unless server-side `config.yaml` `force_push_allowed: true` (D9, the rebase form of the conflict run).
-3. **`refs/heads/tickets`** (the store; harness and human identities only, per rule 1; never judged by rule 4): `approvals/**` added or changed → `P` human (`approval rows need a human pusher`); `log/*.jsonl` append-only and `runs/**` existing files unchanged (`<path> is append-only`); `results/**` → only `harness` (`results/ may only be written by harness`).
+3. **`refs/heads/factory-store`** (the store; harness and human identities only, per rule 1; never judged by rule 4): `approvals/**` added or changed → `P` human (`approval rows need a human pusher`); `log/*.jsonl` append-only and `runs/**` existing files unchanged (`<path> is append-only`); `results/**` → only `harness` (`results/ may only be written by harness`).
 4. **`refs/heads/main`** (merge gate). Only `harness`; fast-forward only. `H = new`; ticket with `head == H`. Normal conditions, first failure named:
    - `results/H/{ci,reviewer,verifier}.yaml` = `PASS`,`APPROVE`,`VERIFIED` (`missing: ci, reviewer, verifier for H`);
    - `git merge-base --is-ancestor old H` (`head H does not contain main <old>`);
@@ -306,7 +306,7 @@ No API key in any run: the CLI authenticates from the owner's login. Keys only i
 
 ### K. Human surface and approval records (piece 9)
 
-- Humans record every decision by pushing a row to the `tickets` branch under their own identity: `approve-*`, `request-changes`, `resolve` and `queue apply` run as the human with `FACTORY_KEY=<human>` (E); the CLI commits the row and pushes it with that key, and the hook accepts an approval row only from a human pusher (F.3). `queue.md` is notification and discussion only; nothing in it is a decision until the command runs.
+- Humans record every decision by pushing a row to the `factory-store` branch under their own identity: `approve-*`, `request-changes`, `resolve` and `queue apply` run as the human with `FACTORY_KEY=<human>` (E); the CLI commits the row and pushes it with that key, and the hook accepts an approval row only from a human pusher (F.3). `queue.md` is notification and discussion only; nothing in it is a decision until the command runs.
 - `queue.md` regenerated by `factory queue`: sections "Parked" (reason, question or output paths, oldest first), "Spec gate", "Protected PRs", "Guardrail gate", "Waiting on requester"; each entry ends with a `Decision:` line (`approve`, `approve --edit FILE`, `changes FILE`, `answer FILE`, `ruling FILE`, `redispatch`, `close`, `to-spec-gate`). `factory queue apply` turns filled lines into the commands below, run as the human identity, and clears them. A note without `Decision:` records nothing.
 - `factory approve-spec ID [--version N] [--edit FILE]`: pins `approved_version` (edited text saved as a new version first), copies "Tests to change" and Risk paths into the ticket, `approvals/ID/spec-v<N>.yaml`, writes the pinned version as the change folder (B; event `change.pinned`; exit 2 with nothing written when the version is malformed (B) or a delta does not apply to current truth: an ADDED requirement name already in `openspec/specs/<capability>/spec.md`, or a MODIFIED or REMOVED name not in it), → `ready-for-planner`, and **exports** the pinned text to `knowledge_vault/sanitized_specs/<ID>.md` (`factory export ID`; event `spec.exported`; the export directory is a config key for the later `specs/` → `tickets/` rename).
 - `factory request-changes ID --notes FILE`: `round.spec: 0`, → `ready-for-spec-writer`.
@@ -361,10 +361,10 @@ Setup: `git clone $O w; cd w; git commit --allow-empty -m c`.
 13. With `T-0001` `in_flight` holding an implementer run (`factory ticket set T-0001 status=ready-for-implementer`, then item 9's `run start` with `--role implementer`): `AS implementer git push $O HEAD:ticket/T-0001` → exit 0. With `in_flight: []`: a new commit pushed the same way → exit 1, stderr `ticket/T-0001: no implementer run in flight` [NEW]
 14. `AS implementer git push --force $O HEAD~1:ticket/T-0001` → exit 1, stderr `non-fast-forward refused`; `AS implementer git push $O :ticket/T-0001` → exit 1, `deletion refused` [NEW]
 15. `AS retro git push $O HEAD:retro/2026-w40` → exit 0; `AS retro git push $O HEAD:ticket/T-0001` → exit 1 [NEW]
-16. `AS harness git push $O HEAD:tickets` → exit 0; `AS implementer git push $O HEAD:tickets` → exit 1 [NEW]
+16. `AS harness git push $O HEAD:factory-store` → exit 0; `AS implementer git push $O HEAD:factory-store` → exit 1 [NEW]
 17. `AS daniel git push $O HEAD:main` → exit 1, stderr `refs/heads/main: identity daniel may not push` [NEW]
-18. On `tickets`: commit `approvals/T-0001/pr-H.yaml`; `AS harness git push $O HEAD:tickets` → exit 1, `approval rows need a human pusher`; the same commit `AS daniel` → exit 0 [NEW]
-19. On `tickets`: edit the first line of `log/2026-10.jsonl`, push `AS daniel` → exit 1, `log/2026-10.jsonl is append-only`; append a line instead → exit 0 [NEW]
+18. On `factory-store`: commit `approvals/T-0001/pr-H.yaml`; `AS harness git push $O HEAD:factory-store` → exit 1, `approval rows need a human pusher`; the same commit `AS daniel` → exit 0 [NEW]
+19. On `factory-store`: edit the first line of `log/2026-10.jsonl`, push `AS daniel` → exit 1, `log/2026-10.jsonl is append-only`; append a line instead → exit 0 [NEW]
 20. **Hook reads server-side refs (S4):** `AS implementer git push $O HEAD:ticket/T-0001` where the commit edits `factory/identities.yaml` to grant `implementer` `refs/heads/main` → exit 0 (ticket branch, allowed); then `AS implementer git push $O HEAD:main` → exit 1, `refs/heads/main: identity implementer may not push` [NEW]
 
 ### Merge gate (S2) ⟨bare⟩
@@ -475,7 +475,7 @@ Driver: `claude -p … "/factory run build T-0001 --stubs tests/factory/fixtures
 88. ⟨bare⟩ **Change folder at the gate:** `specs/T-0001/v1.md` in the four-part FORMAT of doc §2, its delta part `=== specs/status-parser/spec.md` holding `## ADDED Requirements` with `### Requirement: trailer-read` and one scenario: `AS daniel factory approve-spec T-0001 --version 1` → `openspec/changes/T-0001/` holds `proposal.md`, `design.md`, `specs/status-parser/spec.md` and `verification.md`, each equal to its part of `v1.md` except that `verification.md` also ends with `## Critic rounds`, one entry per critic run of T-0001; `change.pinned` logged; `openspec/specs/` and `decisions.md` unchanged. A `v2.md` whose delta has `## MODIFIED Requirements` with `### Requirement: no-such-req`: `AS daniel factory approve-spec T-0001 --version 2` → exit 2, stderr names `no-such-req`, `approved_version: 1`, no `approvals/T-0001/spec-v2.yaml` [NEW]
 89. ⟨wf⟩⟨bare⟩ **Archive at parent close:** case `plan-three` on item 88's T-0001, after item 77's VERIFIED: `openspec/changes/T-0001` is gone; `openspec/changes/archive/<date>-T-0001/` holds item 88's four files and `tasks.md`, equal to the planner run's `output.md` above its last `STATUS:` line; its `verification.md` ends with `## Verifier results`, one line per verifier row of `T-0001.1`–`.3` and `T-0001`; `openspec/specs/status-parser/spec.md` contains `### Requirement: trailer-read` and its scenario; `decisions.md` gained one `<date> T-0001 …` line per `## Decisions` line of the proposal; in the log `change.archived` precedes the transition to `closed`. A second parent, pinned before T-0001 archived with a delta that also ADDs `trailer-read`, reaching its parent-close VERIFIED → `status: parked`, `parked.reason` starts `archive:`, and `openspec/specs/`, `decisions.md` and its change folder are unchanged [NEW]
 90. ⟨wf⟩⟨bare⟩ **Current truth in writer and critic input:** after item 89, `factory request new --file r.md` (a new ticket `T-000k`) and case `accept-approve` run on `T-000k` → its spec writer run's and its critic run's `input.md` each contain `### Requirement: trailer-read`, and each of those runs' `meta.yaml` `input_sources` lists `openspec/specs/status-parser/spec.md` besides the sources item 42 names for that role. Item 42 holds as written because `openspec/specs/` is empty after `factory init` [NEW]
-91. ⟨bare⟩ **Archive refusals without a change folder (K):** T-0001 pinned as in item 88's first half (`specs/T-0001/v1.md`, `AS daniel factory approve-spec T-0001 --version 1`). (a) On the `tickets` checkout, `rm -rf openspec/changes/T-0001`; then `factory archive T-0001` → exit 2, stderr `T-0001 has no change folder to archive`. (b) Then `mv openspec ../openspec.aside` on the `tickets` checkout; `factory archive T-0001` → exit 2, stderr `no spec store (factory init not run)`. In (a) and (b) the `tickets` checkout's `git rev-parse HEAD` and `git status --porcelain` are the same after the command as before it, and `factory log tail --event change.archived` gained no line [NEW]
+91. ⟨bare⟩ **Archive refusals without a change folder (K):** T-0001 pinned as in item 88's first half (`specs/T-0001/v1.md`, `AS daniel factory approve-spec T-0001 --version 1`). (a) On the `factory-store` checkout, `rm -rf openspec/changes/T-0001`; then `factory archive T-0001` → exit 2, stderr `T-0001 has no change folder to archive`. (b) Then `mv openspec ../openspec.aside` on the `factory-store` checkout; `factory archive T-0001` → exit 2, stderr `no spec store (factory init not run)`. In (a) and (b) the `factory-store` checkout's `git rev-parse HEAD` and `git status --porcelain` are the same after the command as before it, and `factory log tail --event change.archived` gained no line [NEW]
 
 ### Gates (every seam)
 
@@ -515,7 +515,7 @@ Blast radius: new files under `factory/`, `.claude/agents/factory-*`, `.claude/s
 
 - **R1 Identity is advisory in v0** (doc §Harness table piece 2, v0 limit (3): every `agent()` call shares the session's checkout, credentials and git identity). E4: the hook inherits the pusher's environment under the local transport and `update-ref` runs no hook; with ssh forced commands the identity comes from the key, but every key is readable by the one Unix user. Mitigations: no key for checkers; tool allowlists in the agent definitions; worktree per mutating run; the implementer branch cannot be checked out twice (E3). Docker closes it.
 - **R2 Baseline to beat (E9):** docs/product churn ratio under 2x and at most one fix commit per unit. The factory records what it needs to measure this (`merge.done` per sub-ticket, implementer rounds in `round.pr`, diff stats in `meta.yaml`), and `audit-sample` prints both numbers for the period; they are not acceptance items because the baseline is a property of the pipeline's output over time, not of this build.
-- The hook reads `tickets` and `main` server-side; a bug blocks every merge (fail-closed).
+- The hook reads `factory-store` and `main` server-side; a bug blocks every merge (fail-closed).
 - The dispatcher is a Workflow script with no filesystem access (E7; doc §Harness table piece 2, v0 limit (1)): every state change is a clerk agent running a `factory` command, so a clerk that misreads its instruction can skip a transition. Mitigation: the command is given verbatim, the clerk relays its `stdout`, `exit` and `stderr` and the script parses the JSON itself (H), so the clerk never re-types the store's answer and a refusal or a reply with no JSON parks instead of routing; the round limit, the legal edges and the one-run-per-branch rule are CLI guards (B, items 68–70), so a disobedient clerk gets exit 2 and an unchanged store; items 35–53 check the store, not the script. Residual: the clerk can still miscopy `stdout`; a miscopy that breaks the JSON parks, one that still parses is not caught by the script.
 - **R6 Permission mode in real runs** (ruling row R6): `--permission-mode acceptEdits` with the allowlist `Bash(factory *)`, `Bash(git *)`, `Bash(pytest *)`, `Bash(ruff *)`, `Bash(mypy *)`, Read, Grep, Glob, Edit, Write, Skill, Workflow; a tool call outside it prompts the operator, so an unattended session stalls rather than widens. Checkers have no key in their environment (item 56); `bypassPermissions` and `dontAsk` appear nowhere (item 54).
 - **Bootstrap.** The seams (the plan's BH-1..BH-7) must land before the gate and `build.js` exist to merge them. Until BH-2 (bare repo, hook, `factory init`) lands, the operator merges with his normal git flow on `feat/lionbot-v3`; after BH-2, `factory init` seeds the bare repo and its `main` is the trunk; BH-3 and BH-4 (results table; agent definitions and workflows) get their `results record` rows written by hand `AS harness` from a reviewer and a verifier the operator runs himself; from then on item 67 runs on the bare repo's `main` and every later seam merges through `factory merge`.
@@ -530,7 +530,7 @@ Round 4, to the human gate's amendments A–N (round reset; the gate amended the
 - **C FIXED.** `merge` records `merge: {base_before, main_after}` on the ticket (B schema, G); the revert rule in F.4 compares `git diff old H` with `git diff main_after base_before` of the reverted ticket, and the `git diff X X^` rule is gone (E5 annotated: it still evidences the patch equality). Piece 8 on a revert exempts files the reverted PR added and tests its pinned spec listed under "Tests to change", the guardrail approval being their row (F.4). Exception failure: `merge` exits 2, ticket `closed` with `closed_reason`, `escalation.queued`, listed in `queue.md` (F.4, G). Items 74, 75; 30(a)(b), 31 amended; 32 kept as the extra-hunk negative.
 - **D FIXED.** The join in H names `ci FAIL` as a trigger alongside REQUEST-CHANGES and FAILED, fires only once all three rows exist, and counts it as a round; no separate CI-fail path exists. Item 76; 47 unchanged (its FAIL arrives via the verifier and already behaves this way).
 - **E FIXED.** `merge` records `parent_base` at a parent's first sub-ticket merge and moves a parent whose sub-tickets have all merged to `ready-for-parent-verify` (B schema and states, G); `build.js` dispatches one verifier run with the inputs doc v5 declares — pinned parent spec, head = current `main`, base = `parent_base`, `{gate commands}` — composed by `run compose`, the verifier definition taking the head and base it is given (H); VERIFIED closes, FAILED/SPEC-DEFECT parks the parent, as does a sub-ticket the human closes; resolution is `resolve --amend-spec` (re-plan) or `--close` on the parent (K). Items 77, 84; 34 amended (the parent no longer closes at merge).
-- **F FIXED.** The store branch is `tickets` (was `factory/state`; same checkout path), restricted by rule 1 to harness and humans and never judged by rule 4 (E, F.3, R5); B names the store CLI as the home of the round and routing guards (items 68–70); operator commands without `FACTORY_KEY` refuse with `set FACTORY_KEY` (B). Item 78; 16, 18, 19 amended.
+- **F FIXED.** The store branch is `factory-store` (was `factory/state`; same checkout path), restricted by rule 1 to harness and humans and never judged by rule 4 (E, F.3, R5); B names the store CLI as the home of the round and routing guards (items 68–70); operator commands without `FACTORY_KEY` refuse with `set FACTORY_KEY` (B). Item 78; 16, 18, 19 amended.
 - **G FIXED.** The `ready-implementers` rule in H: a `parallel_safe: false` sub-ticket runs alone — listed only when no sibling of the same parent is in flight (any role) and nothing else is listed with it; while it is in flight no sibling is listed. Item 79 asserts both directions, which doc v5's Planner row now states.
 - **H FIXED.** D9 `force_push_allowed` (default false) fills `{force-push allowed}` in the rendered implementer definition (A); the hook lifts its non-fast-forward refusal on `ticket/*` only when it is true (F.2); the conflict run is the same-round `head does not contain main` route with `resolution: conflict` (G, H). Item 80; 52 referenced.
 - **I FIXED.** Parser note in H: severities are not parsed; every stub that models REVISE or REQUEST-CHANGES carries a `[BLOCKING]` line. Items 38, 44, 46 amended.
@@ -539,7 +539,7 @@ Round 4, to the human gate's amendments A–N (round reset; the gate amended the
 - **L FIXED.** Item 42 keeps the store assertions and drops the source grep. `ticket new --type retro --output FILE` writes `retros/<date>.yaml`; `retro-input` reads `retros/*.yaml` for previous proposals (B, M). Items 53, 66 amended.
 - **M FIXED.** `resolve --redispatch --budget USD` sets `budget_usd` on the ticket, copied into the redispatched run's `meta.yaml` (recorded, not enforced in v0, E7; Out of scope says so); `run compose` pins `spec_version` in `meta.yaml`, so in-flight siblings keep their version after `--amend-spec` (B, K). Item 83.
 - **N FIXED.** Risk gains a one-paragraph Bootstrap note: the operator's git flow until BH-2, `factory init` after it, hand-written `results record` rows for BH-3/BH-4, item 67 on the bare repo's `main` from then on.
-- **Doc v5 deltas folded in** (no new amendment letters): parent-close run inputs and `parent_base` (E); parent parks on a parent-close failure or a closed sub-ticket, resolved by re-plan or close (E, item 84); both-way parallel-safe exclusion (G); the routing dispatches `gate-run` (B); humans record approvals by pushing to `tickets` as themselves, stated once under K (F); ruling rows R3 and R6 and Risk R1 cite the doc's three numbered v0 limits.
+- **Doc v5 deltas folded in** (no new amendment letters): parent-close run inputs and `parent_base` (E); parent parks on a parent-close failure or a closed sub-ticket, resolved by re-plan or close (E, item 84); both-way parallel-safe exclusion (G); the routing dispatches `gate-run` (B); humans record approvals by pushing to `factory-store` as themselves, stated once under K (F); ruling rows R3 and R6 and Risk R1 cite the doc's three numbered v0 limits.
 - No DISAGREEs; no scope beyond A–N. STATUS stays NEEDS-SPLIT: the seams are unchanged and the amendments are assigned to them under "Size and seams".
 
 STATUS: NEEDS-SPLIT
diff --git a/docs/changelog.md b/docs/changelog.md
index 9a0fa26..b5694f9 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -54,5 +54,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 50. After issue #35 (2026-10-04), where runs at the same time shared one session scratchpad and a verifier mixed another run's stale checkout into its base results (`23 failed, 103 passed` from two trees): every run gets its own scratch directory, `runs/<run id>/scratch/` in the store. `run start` creates it for every role after every guard has passed, and always makes sure the store's `.gitignore` excludes it; `ensure_gitignore` now writes its commented block only to an absent or empty file and otherwise appends only the lines a file lacks, never a second copy. The composer names the directory's absolute path in a "Scratch directory" section after "Running code". The shared preamble gains SCRATCH FILES, between RUNNING CODE and GUARDRAIL PATHS: put every file made for the run's own use there, never in a session scratchpad, a repository checkout or another run's directory, and this takes precedence over any other instruction to use a session scratchpad. Saving a ticket whose status changes to anything but `parked` removes the scratch directory of each finished run of that ticket, so a parked ticket keeps its files for the human and they go once it moves on.
 51. After issue #39 (2026-10-04), a batch of harness defects found in real runs: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested. `resolve --ruling` also takes an implementer's BLOCKED park and returns the sub-ticket to its implementer at the same round, with the ruling in its input. `resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner, with F as a ruling and the existing sub-tickets listed in its input. Sub-tickets that a later plan adds take the next free ids and may depend on merged ones. A park reason always ends with the failing command's error text. The workflows fall back to the refusal's JSON `error`, then to the exit code. A redispatch sets aside only the rows that did not pass, and the build re-runs only the checkers with no row on the commit. The store's `.gitattributes` marks run records `-whitespace`, written by `init` and `run start`. `init` refuses to create an instance on a throwaway store, and a missing `context.md` refuses a compose with exit 2. A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory.
 52. After issue #45 (2026-10-04), where a spec writer's test run executed `init` from inside its scratch directory and initialised this repository's live store, writing a spec store, `decisions.md` and six agent files: the store CLI fences an instance's own store. A write run from inside the store's `runs/` or `worktrees/` is refused, with or without the marker and with or without a run in flight. While any run is in flight on the store, a write without `FACTORY_DISPATCH=1` in its environment is refused. The read-only commands stay open, and any command given `--accept-harness` counts as a write. Both workflow scripts put `FACTORY_DISPATCH=1` in front of every clerk command; the operator puts it in front of one command at a time and never exports it. A refusal is exit 2, writes nothing, and advises a throwaway `FACTORY_STATE` without naming the marker. The fence is checked before the harness lock, so the marker cannot get past the lock. Declined from the request: a preamble line telling roles to use a throwaway store, because the incident came from the test suite rather than a command the role typed; and a tripwire on the store root, because role runs and other tickets' clerk commands legitimately write the store during a run, so a comparison could not tell whose write it saw.
+53. After issue #46 (2026-10-04), where each store commit on the integration branch sent every sub-ticket waiting to merge back for a catch-up merge and a second round of checks that could not change the verdict: the store moves to its own branch, `factory-store`, checked out as a git worktree at the store's path and never merged into the integration branch, so a store commit no longer moves that branch; the merge gate is unchanged. A store path must be one the integration branch has never tracked, because at a once-tracked path a checkout of an older commit overwrites live records and a checkout back deletes them. `init` creates a missing own store as a worktree of an unborn `factory-store` branch, which needs no commit, or checks out the branch where it exists locally or on exactly one remote, which restores the store on a clone, and adds the store to the repo's git exclude file. It refuses when more than one remote carries the branch, naming each, and at a once-tracked path. With `FACTORY_INSTANCE` unset it refuses from inside the store checkout, on its branch or on a detached HEAD, so it can no longer build a phantom instance inside the live store; a separate repository under a run's scratch directory still gets its own instance. Every refusal comes before the first write. An existing store that is a plain directory is left alone, and `init` reports `store_branch` in its JSON.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index c0ece7e..2f9781d 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -36,7 +36,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 | # | Piece | What it must do | GitHub gives you | Minimum portable substitute |
 |---|---|---|---|---|
-| 1 | Ticket store | One record per ticket and sub-ticket: status, type, spec text and version, PR link, round counter, history. The spec gate pins the version the human approved, including any edits made at the gate. This is the state machine's memory. A store CLI (read, transition, record) fronts it: the dispatcher chooses the transition, the CLI rejects any not in the routing table and any round past the cutoff, and the clerk goes through it too | Issues + labels | Any tracker (Jira, Linear) or a table in a DB. A `tickets` branch of YAML works to start: the pre-receive hook restricts it to harness and human identities and exempts it from the merge gate |
+| 1 | Ticket store | One record per ticket and sub-ticket: status, type, spec text and version, PR link, round counter, history. The spec gate pins the version the human approved, including any edits made at the gate. This is the state machine's memory. A store CLI (read, transition, record) fronts it: the dispatcher chooses the transition, the CLI rejects any not in the routing table and any round past the cutoff, and the clerk goes through it too | Issues + labels | Any tracker (Jira, Linear) or a table in a DB. A `factory-store` branch of YAML works to start: the pre-receive hook restricts it to harness and human identities and exempts it from the merge gate |
 | 2 | Event dispatcher | Notice a state change and start the right role with the right inputs. Routes on the `STATUS:` line of the last output, per the routing table | Webhooks + Actions `on:` events | A loop (cron, every 1–5 min) that queries the store for tickets in a "ready for X" state and launches X. Polling is fine; nothing here is latency-sensitive. For a v0 inside one Claude Code session, a Workflow script: each agent() call is a fresh context, the fan-out, join, and round counters are plain code, and the same routing table lifts into the loop later. Three v0 limits. (1) The script has no filesystem or clock, so store reads and writes go through a clerk agent calling the CLI; the guards live in the CLI, not the clerk. The clerk never restates a command's output: it returns stdout verbatim with the exit code and stderr, and the script parses the JSON itself, since a schema shaped like the command's output lets the clerk re-type the answer and still validate. A non-zero exit is a refusal and no JSON on stdout is a failed store call; neither is ever read as an answer. (2) A hung agent blocks the join until a human skips it, so the piece-3 kill is post-hoc. (3) v0 gives fresh context, not isolation: every agent() call shares the session's checkout, credentials, and git identity. Use a worktree per call, run the clerk's CLI under a harness identity that has no verb for approval rows (humans write those directly), and treat v0 as exercising the routing table, not as producing trusted merges |
 | 3 | Isolated run per role | Every role invocation starts in a clean checkout with no memory of earlier runs and only its declared inputs. This is what "fresh context per checker" means in practice | Actions job on a fresh runner | A container or VM per run (Docker, Firecracker, K8s Job). Run `claude -p` with the preamble + role prompt as the system prompt and the inputs on stdin. Destroy the environment after. A run that exceeds {time budget, token budget} is killed, recorded as a result row for that head and role so no join waits on it, and its ticket parked |
 | 4 | Scoped credentials | Each role gets only the access its rules allow. Implementer: push to its own branch. Triage, spec writer, critic, planner, reviewer, verifier, and gate runner: read-only clone plus a shell, with no secrets in the environment, since they run PR code before any security check has passed (model access through a proxy sidecar that holds the key, so the container has none to leak; no git write token; restricted egress). Retro: push a branch and open a PR, nothing else. No role can push to main. Only the harness identity and humans write the ticket store; role outputs enter it through the dispatcher, and the merge gate accepts an approval row only if a human identity pushed it, judged by the server's pusher identity, not the commit author | Job-level `permissions:` on a per-job `GITHUB_TOKEN` | One git user or deploy key per role, with server-side rights set on the git host. Secrets injected per job from a vault or env, never baked into the image |
@@ -57,7 +57,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
-**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell with `HOME` set to a fresh temporary directory, exporting any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
+**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell with `HOME` set to a fresh temporary directory, exporting any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
 
 **Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception.
 
@@ -73,7 +73,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | Retro | Fable | Rare, high leverage, writes the rules |
 | Clerk, parsing, routing | Haiku, or no model | Code where possible |
 
-**Smallest thing that works.** A git server with per-user permissions and a pre-receive hook (pieces 4, 7, 8), a `tickets` branch of YAML as the store (1, 5, 6, 10), a cron loop that reads it and launches `claude -p` in a fresh container (2, 3); implementer and retro containers get secrets via env, every other role's container gets model access only through a proxy sidecar and no env secrets (12; the one extra component), the verifier running the gates (11), and your existing tracker as the human surface (9). Humans record approvals by pushing a row to the `tickets` branch under their own identity (the store CLI's record verb, run as themselves); the tracker is for notification and discussion only. Audit and retro counts come from the append-only log. A few hundred lines of harness. Move the store to a real DB when you want cost-per-issue numbers in one place.
+**Smallest thing that works.** A git server with per-user permissions and a pre-receive hook (pieces 4, 7, 8), a `factory-store` branch of YAML as the store (1, 5, 6, 10), a cron loop that reads it and launches `claude -p` in a fresh container (2, 3); implementer and retro containers get secrets via env, every other role's container gets model access only through a proxy sidecar and no env secrets (12; the one extra component), the verifier running the gates (11), and your existing tracker as the human surface (9). Humans record approvals by pushing a row to the `factory-store` branch under their own identity (the store CLI's record verb, run as themselves); the tracker is for notification and discussion only. Audit and retro counts come from the append-only log. A few hundred lines of harness. Move the store to a real DB when you want cost-per-issue numbers in one place.
 
 **Spec store: the `spec-factory` schema.** The ticket store (piece 1) keeps specs in OpenSpec's tree (Fission-AI, MIT; layout and grammar as its `docs/concepts.md` and `docs/customization.md` give them), under a schema forked from OpenSpec's built-in `spec-driven` and named `spec-factory` (`openspec/schemas/spec-factory/schema.yaml`, selected by `openspec/config.yaml`). Current truth is `openspec/specs/<capability>/spec.md`: what each capability does now, as `### Requirement: <name>` blocks, each one SHALL or MUST sentence followed by `#### Scenario: <name>` items whose WHEN is a runnable command and THEN its expected result. A ticket's change is the folder `openspec/changes/<ticket id>/`:
 
diff --git a/factory/cli.py b/factory/cli.py
index f08aaec..8465a39 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -843,35 +843,132 @@ def _revision() -> str:
     return rev
 
 
+def _refuse_inside_store(cwd: Path, top: Path) -> None:
+    """Refuse `init` from inside the store checkout, where it would build a second instance inside
+    the live store (design A.1). Called only with FACTORY_INSTANCE unset."""
+    head = subprocess.run(["git", "-C", str(top), "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True)
+    if head.stdout.strip() == f"refs/heads/{gitops.STORE_BRANCH}":  # an unborn branch too
+        raise Refused(f"factory init: {cwd} is inside the store checkout {top} (branch {gitops.STORE_BRANCH}); "
+                      "run init from the repository root")
+    # Whatever the store has checked out (a detached HEAD, another branch): the instance found by
+    # walking up names its store, and a checkout of the same repository at or under it is that store.
+    found = instance.find()
+    if found is None:
+        return
+    try:
+        cfg = instance.load_config(found)
+    except (OSError, yaml.YAMLError):  # an unreadable config names no store: nothing to compare
+        return
+    if not isinstance(cfg, dict) or not isinstance(cfg.get("state_dir"), str):
+        return
+    own = instance.own_state_root(found, cfg)
+    if top == own or (top.is_relative_to(own)
+                      and gitops.common_dir(top) == gitops.common_dir(instance.repo_root(found))):
+        raise Refused(f"factory init: {cwd} is inside the store {own} of the instance {found}; "
+                      "run init from the repository root")
+
+
+def _head_branch(repo: Path) -> str:
+    """The branch checked out at `repo`, or HEAD when it is detached."""
+    cp = subprocess.run(["git", "symbolic-ref", "-q", "--short", "HEAD"], cwd=repo, capture_output=True, text=True)
+    return cp.stdout.strip() or "HEAD"
+
+
+def _add_store_checkout(repo: Path, root: Path, branch: str, cfg_path: Path) -> None:
+    """Make the missing own store `root` a checkout of the store branch (design A.3): refused at a
+    path `branch` has ever tracked; the branch comes from a local branch, else the one remote that
+    carries it, else a new orphan, which needs no commit and so no git identity."""
+    store_branch = gitops.STORE_BRANCH
+    rel = root.relative_to(repo).as_posix() if root.is_relative_to(repo) else None
+    if rel is not None:
+        sha = gitops.last_tracked(repo, branch, rel)
+        if sha:
+            raise Refused(f"factory init: {branch} has tracked files under {rel} (last in commit {sha}); a checkout "
+                          f"of any older commit would overwrite a store kept there; set another state_dir in {cfg_path}")
+    local = subprocess.run(["git", "rev-parse", "-q", "--verify", f"refs/heads/{store_branch}"], cwd=repo,
+                           capture_output=True).returncode == 0
+    remotes = [] if local else gitops.remote_branches(repo, store_branch)
+    if len(remotes) > 1:
+        raise Refused(f"factory init: no local branch {store_branch}, and more than one remote carries it "
+                      f"({', '.join(remotes)}); run git branch {store_branch} <remote>/{store_branch} for the one "
+                      "to use, then init again")
+    if local:
+        args = ["worktree", "add", "-q", str(root), store_branch]
+    elif remotes:
+        args = ["worktree", "add", "-q", "--track", "-b", store_branch, str(root), remotes[0]]
+    else:
+        args = ["worktree", "add", "-q", "--orphan", "-b", store_branch, str(root)]
+    try:
+        gitops.git(repo, *args)
+    except Refused as e:
+        raise Refused(f"factory init: cannot check out the store at {root}: {e}") from None
+    if rel is not None:  # the integration checkout ignores the store through the repo's exclude file
+        exclude = Path(gitops.git(repo, "rev-parse", "--git-path", "info/exclude"))
+        exclude = exclude if exclude.is_absolute() else repo / exclude
+        have = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
+        line = f"/{rel}/"
+        if line not in have.splitlines():
+            store.write_text(exclude, have + ("" if not have or have.endswith("\n") else "\n") + line + "\n")
+
+
+def _store_hint(repo: Path, root: Path) -> None:
+    """An existing own store that is not the store branch's checkout is left alone (design A.5)."""
+    top = gitops.git(root, "rev-parse", "--show-toplevel", check=False)
+    if top and Path(top).resolve() == root.resolve() and gitops.common_dir(root) == gitops.common_dir(repo):
+        detached = subprocess.run(["git", "-C", str(root), "symbolic-ref", "-q", "HEAD"],
+                                  capture_output=True).returncode != 0
+        if detached:
+            print(f"the store worktree {root} is on a detached HEAD; check out {gitops.STORE_BRANCH} there",
+                  file=sys.stderr)
+        return
+    print(f"the store {root} is not on its branch {gitops.STORE_BRANCH}; factory store migrate --to PATH moves it",
+          file=sys.stderr)
+
+
 def init_cmd(a):
     """Create whatever of the instance is missing (design B.5); idempotent. The instance is
-    FACTORY_INSTANCE, else `.factory/` at the git top level of the working directory. Its pieces
-    (instance.yaml, context.md, harness.lock, agent files) are written only when the store in use
-    is the instance's own: a run on a throwaway store (FACTORY_STATE elsewhere, as every test
-    does) initialises that store and nothing else. So creating an instance while FACTORY_STATE
-    names another store is refused before anything is written: it would leave an instance.yaml
-    with no context.md."""
-    top = _git_toplevel(instance.caller_cwd())
+    FACTORY_INSTANCE, else `.factory/` at the git top level of the working directory, which may not
+    be inside the store checkout (A.1). Its pieces (instance.yaml, context.md, harness.lock, agent
+    files) are written only when the store in use is the instance's own: a run on a throwaway store
+    (FACTORY_STATE elsewhere, as every test does) initialises that store and nothing else. So
+    creating an instance while FACTORY_STATE names another store is refused before anything is
+    written: it would leave an instance.yaml with no context.md. A missing own store becomes a git
+    worktree of the store branch (A.3) before any instance file is written, so a refusal or a
+    failed git step leaves nothing behind."""
+    cwd = instance.caller_cwd()
+    top = _git_toplevel(cwd)
+    if instance.env_path("FACTORY_INSTANCE") is None:
+        _refuse_inside_store(cwd, top)
     inst = instance.env_path("FACTORY_INSTANCE") or top / instance.DIRNAME
     created: list[str] = []
     cfg_path = inst / instance.CONFIG_NAME
-    if not cfg_path.exists():
+    new_text = None
+    if cfg_path.exists():
+        cfg = instance.load_config(inst)
+    else:
         if not a.repo_name:
             raise Refused(f"factory init: {cfg_path} does not exist; pass --repo-name NAME to create it")
-        text = _new_instance_yaml(a.repo_name)
-        new_cfg = yaml.safe_load(text)
-        root = instance.state_root(inst, new_cfg)
-        if not instance.is_own_store(inst, new_cfg, root):
+        new_text = _new_instance_yaml(a.repo_name)
+        cfg = yaml.safe_load(new_text)
+    root = instance.state_root(inst, cfg)
+    fence(inst, cfg, root)
+    own = instance.is_own_store(inst, cfg, root)
+    if new_text is not None:
+        if not own:
             raise Refused(f"factory init: {inst} has no {instance.CONFIG_NAME}, and FACTORY_STATE names another "
                           f"store ({root}); create the instance with FACTORY_STATE unset, then init that store")
         _revision()  # refuse before writing anything if the lock cannot be written
-        store.write_text(cfg_path, text)
+    repo = instance.repo_root(inst)
+    existed = root.exists()
+    if own and not existed:
+        branch = _head_branch(repo) if new_text is not None else gitops.integration_branch(cfg, repo)
+        _add_store_checkout(repo, root, branch, cfg_path)
+    if new_text is not None:
+        store.write_text(cfg_path, new_text)
         created.append(str(cfg_path))
-    cfg = instance.load_config(inst)
-    root = instance.state_root(inst, cfg)
-    fence(inst, cfg, root)
     agents: list[str] = []
-    if instance.is_own_store(inst, cfg, root):
+    store_branch = None
+    if own:
         ctx = inst / "context.md"
         if not ctx.exists():
             store.write_text(ctx, instance.CONTEXT_TEMPLATE.read_text(encoding="utf-8"))
@@ -880,12 +977,17 @@ def init_cmd(a):
         if not lock.exists():
             store.write_text(lock, _revision() + "\n")
             created.append(str(lock))
-        dest = instance.repo_root(inst) / ".claude" / "agents"
+        dest = repo / ".claude" / "agents"
         for src in sorted(instance.AGENTS.glob("factory-*.md")):
             if not (dest / src.name).exists():
                 (dest / src.name).parent.mkdir(parents=True, exist_ok=True)
                 shutil.copyfile(src, dest / src.name)
                 agents.append(str(dest / src.name))
+        checkout = gitops.checkout_of(repo, gitops.STORE_BRANCH)
+        if checkout is not None and checkout.resolve() == root:
+            store_branch = gitops.STORE_BRANCH
+        elif existed:
+            _store_hint(repo, root)
     had_gitignore, had_gitattributes = (root / ".gitignore").exists(), (root / ".gitattributes").exists()
     store.ensure_gitignore(root)
     store.ensure_gitattributes(root)
@@ -899,7 +1001,7 @@ def init_cmd(a):
     if agents:
         print("restart the session so the agents register", file=sys.stderr)
     out({"ok": True, "written": written, "active": True, "instance": str(inst), "state": str(root),
-         "created": created, "agents": agents})
+         "created": created, "agents": agents, "store_branch": store_branch})
 
 
 def paths_cmd(a):
diff --git a/factory/gitops.py b/factory/gitops.py
index 99542c9..f8c3d23 100644
--- a/factory/gitops.py
+++ b/factory/gitops.py
@@ -100,6 +100,32 @@ def checkout_of(repo: Path, branch: str) -> Path | None:
     return None
 
 
+STORE_BRANCH = "factory-store"
+
+
+def common_dir(path: Path) -> str | None:
+    """The absolute git common directory of the repository at `path`, None outside one: two
+    checkouts of one repository share it, a separate repository has its own."""
+    cp = subprocess.run(["git", "-C", str(path), "rev-parse", "--path-format=absolute", "--git-common-dir"],
+                        capture_output=True, text=True)
+    return cp.stdout.strip() if cp.returncode == 0 and cp.stdout.strip() else None
+
+
+def last_tracked(repo: Path, ref: str, path: str) -> str | None:
+    """The last commit in `ref`'s history that touched a file under `path` (relative to `repo`),
+    or None. A ref with no commit yet (an unborn branch) has tracked nothing."""
+    if subprocess.run(["git", "rev-parse", "-q", "--verify", f"{ref}^{{commit}}"], cwd=repo,
+                      capture_output=True).returncode != 0:
+        return None
+    return git(repo, "log", "-1", "--format=%H", ref, "--", path) or None
+
+
+def remote_branches(repo: Path, branch: str) -> list[str]:
+    """Every remote-tracking ref named `branch`, as `<remote>/<branch>`."""
+    refs = git(repo, "for-each-ref", "--format=%(refname)", "refs/remotes/").splitlines()
+    return [r.removeprefix("refs/remotes/") for r in refs if r.endswith(f"/{branch}")]
+
+
 class MergeLock:
     """One merge at a time per target repo: a lock directory (mkdir is atomic). Two sibling
     sub-tickets that reach the merge gate together must not run `git merge` in one checkout at once."""
diff --git a/tests/factory/test_live_store_guard.py b/tests/factory/test_live_store_guard.py
index c98e23e..e1d410c 100644
--- a/tests/factory/test_live_store_guard.py
+++ b/tests/factory/test_live_store_guard.py
@@ -141,8 +141,14 @@ def test_marked_writes_from_a_runs_scratch_directory_are_refused(target, tmp_pat
     before = snapshot(target)
     for argv in (("decision", "add", "T-0001", "x"), ("init", "--repo-name", "x"),
                  ("ticket", "new", "--file", request(tmp_path))):
-        assert_refused(cli(scratch, *argv, FACTORY_DISPATCH="1"),
-                       f"{state(target).resolve()}; called from inside its runs/")
+        cp = cli(scratch, *argv, FACTORY_DISPATCH="1")
+        if argv[0] == "init":  # refused first by T-0025's A.1: the store is a factory-store checkout
+            assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
+            assert (f"is inside the store checkout {state(target).resolve()} (branch factory-store); "
+                    "run init from the repository root") in cp.stderr
+            assert js(cp) == {"ok": False, "error": cp.stderr.strip()}
+            continue
+        assert_refused(cp, f"{state(target).resolve()}; called from inside its runs/")
     assert snapshot(target) == before
 
 
@@ -152,8 +158,14 @@ def test_marked_writes_from_under_worktrees_are_refused(target, tmp_path):
     wt.mkdir(parents=True)
     before = snapshot(target)
     for argv in (("ticket", "new", "--file", request(tmp_path)), ("init",)):
-        assert_refused(cli(wt, *argv, FACTORY_DISPATCH="1"),
-                       f"{state(target).resolve()}; called from inside its worktrees/")
+        cp = cli(wt, *argv, FACTORY_DISPATCH="1")
+        if argv[0] == "init":  # refused first by T-0025's A.1: the store is a factory-store checkout
+            assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
+            assert (f"is inside the store checkout {state(target).resolve()} (branch factory-store); "
+                    "run init from the repository root") in cp.stderr
+            assert js(cp) == {"ok": False, "error": cp.stderr.strip()}
+            continue
+        assert_refused(cp, f"{state(target).resolve()}; called from inside its worktrees/")
     assert snapshot(target) == before
 
 
diff --git a/tests/factory/test_store_branch.py b/tests/factory/test_store_branch.py
new file mode 100644
index 0000000..510e798
--- /dev/null
+++ b/tests/factory/test_store_branch.py
@@ -0,0 +1,296 @@
+"""`init` puts a new store on its own branch, `factory-store` (T-0025, part A; issue #46).
+
+A missing own store becomes a git worktree of `factory-store` at the store path, ignored by the
+integration checkout through the repo's exclude file, so a store commit never moves the
+integration branch and the merge gate no longer sends a sub-ticket back for one. `init` refuses
+from inside the store checkout, whatever it has checked out, and at a store path the integration
+branch has ever tracked; every refusal writes nothing.
+
+Black-box through `bin/factory` in scratch target repos, with the instance resolved from the
+working directory (test_instance.cli strips the conftest's FACTORY_* variables). Commits carry
+their identity in GIT_AUTHOR_* / GIT_COMMITTER_*, because the suite runs under a throwaway HOME.
+"""
+from __future__ import annotations
+
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+
+from .test_instance import cli, git_repo, js, tree
+
+BRANCH = "factory-store"
+IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
+RULE = "role runs may not write the live store"
+
+
+def git(cwd: Path, *argv: str, check: bool = True) -> str:
+    env = {**os.environ, **IDENT}
+    cp = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, env=env)
+    if check:
+        assert cp.returncode == 0, (argv, cp.stderr)
+    return cp.stdout.strip()
+
+
+def state(t: Path) -> Path:
+    return t / ".factory" / "state"
+
+
+def exclude(t: Path) -> Path:
+    p = Path(git(t, "rev-parse", "--git-path", "info/exclude"))
+    return p if p.is_absolute() else t / p
+
+
+def files(t: Path) -> dict[str, bytes]:
+    """Every file under the target, its git directory aside, plus the exclude file."""
+    snap = {k: v for k, v in tree(t).items() if not k.startswith(".git/")}
+    ex = exclude(t)
+    snap["<exclude>"] = ex.read_bytes() if ex.exists() else b""
+    return snap
+
+
+def init(t: Path, *argv: str, **env: str):
+    return cli(t, "init", *argv, **env)
+
+
+@pytest.fixture
+def target(tmp_path: Path) -> Path:
+    t = git_repo(tmp_path / "target")
+    cp = init(t, "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    return t
+
+
+def request(tmp_path: Path) -> str:
+    p = tmp_path / "r.md"
+    p.write_text("# demo\n\nDo the thing.\n")
+    return str(p)
+
+
+def start_triage(t: Path, tmp_path: Path) -> Path:
+    assert cli(t, "ticket", "new", "--file", request(tmp_path)).returncode == 0
+    cp = cli(t, "run", "start", "--role", "triage", "--ticket", "T-0001")
+    assert cp.returncode == 0, cp.stderr
+    return state(t) / "runs" / js(cp)["run_id"] / "scratch"
+
+
+def ticket_status(cwd: Path) -> str | None:
+    cp = cli(cwd, "ticket", "show", "T-0001", "--json")
+    return js(cp).get("state") if cp.returncode == 0 else None
+
+
+# ----- a new store ----------------------------------------------------------------------------
+
+def test_a_new_store_is_the_checkout_of_its_branch_unseen_by_the_integration_checkout(tmp_path):
+    t = git_repo(tmp_path / "target")
+    cp = init(t, "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["store_branch"] == BRANCH
+    assert git(state(t), "symbolic-ref", "HEAD") == f"refs/heads/{BRANCH}"
+    assert (state(t) / "decisions.md").is_file() and (state(t) / ".gitignore").is_file()
+    seen = git(t, "status", "--porcelain", "--untracked-files=all").splitlines()
+    assert seen and not [ln for ln in seen if ".factory/state" in ln], seen
+    assert "/.factory/state/" in exclude(t).read_text().splitlines()
+
+
+def test_a_store_commit_leaves_the_integration_branch_where_it_was(target):
+    git(target, "add", "-A")
+    git(target, "commit", "-q", "-m", "instance")
+    main = git(target, "rev-parse", "main")
+    git(state(target), "add", "-A")
+    git(state(target), "commit", "-q", "-m", "store: first")
+    assert git(target, "rev-parse", "main") == main
+    assert git(target, "rev-parse", f"{BRANCH}~0") == git(state(target), "rev-parse", "HEAD")
+    assert git(target, "ls-files", ".factory/state") == ""
+
+
+def test_a_clone_restores_the_store_from_the_branch(target, tmp_path):
+    git(target, "add", "-A")
+    git(target, "commit", "-q", "-m", "instance")
+    git(state(target), "add", "-A")
+    git(state(target), "commit", "-q", "-m", "store: first")
+    clone = tmp_path / "clone"
+    git(tmp_path, "clone", "-q", str(target), str(clone))
+    assert not state(clone).exists()
+    cp = init(clone)
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["store_branch"] == BRANCH
+    assert git(state(clone), "symbolic-ref", "--short", "HEAD") == BRANCH
+    assert git(state(clone), "rev-parse", "--abbrev-ref", "@{upstream}") == f"origin/{BRANCH}"
+    assert (state(clone) / "decisions.md").read_bytes() == (state(target) / "decisions.md").read_bytes()
+    assert js(cp)["written"] == []
+
+
+def test_two_remotes_carrying_the_branch_are_refused_naming_both(target, tmp_path):
+    git(target, "add", "-A")
+    git(target, "commit", "-q", "-m", "instance")
+    git(state(target), "add", "-A")
+    git(state(target), "commit", "-q", "-m", "store: first")
+    clone = tmp_path / "clone"
+    git(tmp_path, "clone", "-q", str(target), str(clone))
+    git(clone, "remote", "add", "nas", str(target))
+    git(clone, "fetch", "-q", "nas")
+    before = files(clone)
+    cp = init(clone)
+    assert cp.returncode == 2, cp.stderr
+    assert f"origin/{BRANCH}" in cp.stderr and f"nas/{BRANCH}" in cp.stderr
+    assert len(cp.stderr.strip().splitlines()) == 1
+    assert not state(clone).exists() and files(clone) == before
+    assert git(clone, "branch", "--list", BRANCH) == ""
+
+
+def test_a_store_path_the_integration_branch_once_tracked_is_refused(tmp_path):
+    t = git_repo(tmp_path / "target")
+    state(t).mkdir(parents=True)
+    (state(t) / "old.md").write_text("old\n")
+    git(t, "add", "-A")
+    git(t, "commit", "-q", "-m", "old store")
+    git(t, "rm", "-q", "-r", ".factory/state")
+    git(t, "commit", "-q", "-m", "store removed")
+    removed = git(t, "rev-parse", "HEAD")
+    before = files(t)
+    cp = init(t, "--repo-name", "demo")
+    assert cp.returncode == 2, cp.stderr
+    assert ".factory/state" in cp.stderr and removed in cp.stderr and "state_dir" in cp.stderr
+    assert len(cp.stderr.strip().splitlines()) == 1
+    assert not (t / ".factory").exists() and files(t) == before
+    assert git(t, "branch", "--list", BRANCH) == ""
+
+
+def test_a_failed_worktree_step_writes_no_instance_file(tmp_path):
+    t = git_repo(tmp_path / "target")
+    git(t, "branch", BRANCH)
+    git(t, "worktree", "add", "-q", str(tmp_path / "elsewhere"), BRANCH)
+    before = files(t)
+    cp = init(t, "--repo-name", "demo")
+    assert cp.returncode == 2, cp.stderr
+    assert "factory init: cannot check out the store" in cp.stderr
+    assert not (t / ".factory").exists() and not (t / ".claude").exists() and files(t) == before
+
+
+# ----- init from inside the store -------------------------------------------------------------
+
+@pytest.mark.parametrize("detached", [False, True], ids=["on-branch", "detached"])
+def test_init_from_inside_the_store_is_refused_and_writes_nothing(target, tmp_path, detached):
+    if detached:
+        git(state(target), "add", "-A")
+        git(state(target), "commit", "-q", "-m", "store: first")
+        git(state(target), "checkout", "-q", "--detach")
+    scratch = start_triage(target, tmp_path)
+    before = files(target)
+    cp = init(scratch, "--repo-name", "x")
+    assert cp.returncode == 2, cp.stderr
+    assert "run init from the repository root" in cp.stderr and len(cp.stderr.strip().splitlines()) == 1
+    assert (f"inside the store {state(target).resolve()} of the instance" if detached
+            else f"inside the store checkout {state(target).resolve()} (branch {BRANCH})") in cp.stderr
+    assert files(target) == before and not (state(target) / ".factory").exists()
+    assert ticket_status(scratch) == "ready-for-triage"
+
+
+def test_with_factory_instance_set_a1_does_not_apply(target, tmp_path):
+    """A.1 applies only with FACTORY_INSTANCE unset. With it set and FACTORY_STATE naming a
+    throwaway store, init from a run's scratch directory initialises that store; with the own store,
+    #45's location rule still refuses it."""
+    scratch = start_triage(target, tmp_path)
+    inst = str(target / ".factory")
+    before = files(target)
+    other = tmp_path / "throwaway"
+    cp = init(scratch, FACTORY_INSTANCE=inst, FACTORY_STATE=str(other))
+    assert cp.returncode == 0, cp.stderr
+    assert (other / "decisions.md").is_file() and js(cp)["store_branch"] is None
+    cp = init(scratch, FACTORY_INSTANCE=inst, FACTORY_DISPATCH="1")
+    assert cp.returncode == 2 and RULE in cp.stderr and "called from inside its runs/" in cp.stderr
+    assert files(target) == before
+
+
+def test_init_in_a_separate_repository_under_a_runs_scratch_directory_makes_its_instance(target, tmp_path):
+    scratch = start_triage(target, tmp_path)
+    other = git_repo(scratch / "other")
+    before = {k: v for k, v in files(target).items() if "/scratch/other/" not in k}
+    cp = init(other, "--repo-name", "other")
+    assert cp.returncode == 0, cp.stderr
+    assert (other / ".factory" / "instance.yaml").is_file() and js(cp)["store_branch"] == BRANCH
+    assert {k: v for k, v in files(target).items() if "/scratch/other/" not in k} == before
+    assert ticket_status(target) == "ready-for-triage"
+
+
+# ----- an existing store ----------------------------------------------------------------------
+
+def test_an_existing_plain_store_is_left_alone_and_pointed_to_store_migrate(tmp_path):
+    t = git_repo(tmp_path / "target")
+    state(t).mkdir(parents=True)
+    cp = init(t, "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["store_branch"] is None
+    assert "factory store migrate --to PATH" in cp.stderr
+    assert not (state(t) / ".git").exists() and git(t, "branch", "--list", BRANCH) == ""
+    assert "/.factory/state/" not in (exclude(t).read_text() if exclude(t).exists() else "")
+    before = files(t)
+    again = init(t)
+    assert again.returncode == 0 and js(again)["store_branch"] is None and "store migrate" in again.stderr
+    assert files(t) == before
+
+
+def test_a_detached_store_worktree_is_left_alone_with_its_own_hint(target):
+    git(state(target), "add", "-A")
+    git(state(target), "commit", "-q", "-m", "store: first")
+    git(state(target), "checkout", "-q", "--detach")
+    before = files(target)
+    cp = init(target)
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["store_branch"] is None
+    assert "detached HEAD" in cp.stderr and "store migrate" not in cp.stderr
+    assert files(target) == before
+
+
+def test_a_second_init_is_a_no_op(target):
+    before = files(target)
+    cp = init(target)
+    assert cp.returncode == 0, cp.stderr
+    out = js(cp)
+    assert (out["written"], out["created"], out["agents"], out["store_branch"]) == ([], [], [], BRANCH)
+    assert files(target) == before
+    assert exclude(target).read_text().splitlines().count("/.factory/state/") == 1
+
+
+# ----- the merge gate -------------------------------------------------------------------------
+
+@pytest.fixture
+def checked(target, tmp_path) -> Path:
+    """T-0001 on branch factory/T-0001 with gate PASS, reviewer APPROVE and verifier VERIFIED on its
+    head, the instance committed on main."""
+    git(target, "add", "-A")
+    git(target, "commit", "-q", "-m", "instance")
+    git(target, "checkout", "-q", "-b", "factory/T-0001")
+    (target / "x.txt").write_text("x\n")
+    git(target, "add", "x.txt")
+    git(target, "commit", "-q", "-m", "work")
+    head = git(target, "rev-parse", "HEAD")
+    git(target, "checkout", "-q", "main")
+    assert cli(target, "ticket", "new", "--file", request(tmp_path)).returncode == 0
+    assert cli(target, "ticket", "set", "T-0001", "status=checks-in-flight", "branch=factory/T-0001",
+               f"head={head}").returncode == 0
+    for role, body, rid in (("verifier", "Gate suite: PASS\nSTATUS: VERIFIED", "run-0001-verifier"),
+                            ("reviewer", "STATUS: APPROVE", "run-0002-reviewer")):
+        p = tmp_path / f"{role}.md"
+        p.write_text(f"Commit: {head}\n{body}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+        cp = cli(target, "results", "record", "T-0001", "--head", head, "--role", role, "--output", str(p), "--run", rid)
+        assert cp.returncode == 0, cp.stderr
+    return target
+
+
+def test_a_sub_ticket_merges_after_a_store_commit(checked):
+    git(state(checked), "add", "-A")
+    git(state(checked), "commit", "-q", "-m", "store: rows recorded")
+    cp = cli(checked, "merge", "T-0001", **IDENT)
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["state"] == "merged"
+
+
+def test_a_sub_ticket_is_still_refused_after_a_code_commit(checked):
+    (checked / "y.txt").write_text("y\n")
+    git(checked, "add", "y.txt")
+    git(checked, "commit", "-q", "-m", "code on main")
+    cp = cli(checked, "merge", "T-0001", **IDENT)
+    assert cp.returncode == 2 and "head does not contain main" in cp.stderr

## Human ruling

Ruling (Green session, operator-delegated: "keep iterating ... don't need to raise to me if they haven't cleared it"), 2026-10-04, on run-0241's escalation.

Tests to change, added for this sub-ticket: `tests/factory/test_live_store_guard.py::test_marked_writes_from_a_runs_scratch_directory_are_refused` and `::test_marked_writes_from_under_worktrees_are_refused`. In each, the `init` call's assertion accepts A.1's refusal instead of #45's location-rule text: exit 2, A.1's message, and the store snapshot unchanged. Every other assertion in the two tests stays exactly as it is, including the non-`init` commands and their location-rule text. A.1's ordering stands. The behaviour the tests protect (an `init` from inside a run's directory is refused and writes nothing) is unchanged; only which check refuses first changes, as the parent spec's Risk anticipated. No other test may change.
