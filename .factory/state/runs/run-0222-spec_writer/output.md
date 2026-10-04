=== proposal.md
## Problem

Each time the operator commits the factory's records, any piece of work that is waiting to merge has to be checked again from the start, although nothing it was checked against has changed. This costs the operator time and tokens on both repositories the factory runs on, and it has already led one session to hand-edit checker results to get past the gate.

The factory keeps its records in a directory of files called the **store**: one file per ticket with its state, the operator's approvals, each agent run's input and output, the checkers' verdicts and an append-only log. Each repository the factory works on has its own store. The store is committed to git on purpose, so it is versioned, reviewable and pushed. Today it is committed to the **integration branch**, the branch that finished pieces of work are merged into: `main` in this repo and `feat/lionbot-v3.5` in the Nanobot repo. The operator commits the store between steps, after an approval, a close or a new record. So the integration branch moves even when no code changed.

A planned ticket is built as **sub-tickets**, each a separately mergeable branch written by an implementer agent and judged by two checker agents, a code reviewer and a verifier. The **merge gate** is the step that merges a sub-ticket once both checkers pass it. It refuses a branch that does not contain the current integration branch, so that the code that was checked is the code that merges. A store commit made while a sub-ticket is being checked therefore sends it back. Its implementer merges the integration branch in, which is a **catch-up run**, and both checkers run again. That takes 10 to 20 minutes. The requester estimates it at about a million tokens. It cannot change the verdict, because the merge it makes brings in only store files. This has happened four times in this repo and at least once in the Nanobot repo.

The operator has decided that the fix is a separate branch, not a gate exception. A gate rule that ignores store-only commits would only imitate a separate branch. The store moves to its own branch, `factory-store`, and is still committed and pushed. The integration branch then moves only when work merges. This spec recommends checking that branch out as a git worktree at the store's path (option B1) rather than writing it through git plumbing with no working copy (option B2). It also moves the store to a path that the integration branch has never tracked. At the old path, an ordinary `git checkout` of an older commit overwrites the live records.

## Evidence

All commands were run from `~/dev/spec-factory` on `main` at `3a3f58c`, except where a path says otherwise.

**The gate refusal.** `factory/cli.py:544-550`, in `merge_cmd`, refuses with `head does not contain main (<branch> moved; merge it into <branch> and re-check)` when `gitops.head_contains` (`factory/gitops.py:79`) finds the integration branch is not an ancestor of the checked head. `ticket_join` (`factory/cli.py:592-595`) turns that refusal into a catch-up run, and parks the ticket after `MAX_CONFLICT_RUNS = 2` such runs (`factory/cli.py:576`). Any commit on the integration branch triggers this, whatever it touches.

**The store is on the integration branch in both repos.** `git ls-files .factory/state | wc -l` prints `1282` here, and `1106` in `~/dev/nanobot-upstream` on `feat/lionbot-v3.5`. Both stores are tracked on the branch their sub-tickets merge into. Here, 35 non-merge commits on `main` touch the store, and 19 of them touch nothing else (`git log --no-merges -- .factory/state`, each classified by `git show --name-only`).

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

**Moving the branch but keeping the old path loses records.** I prototyped option B1 at the old path, in throwaway repos under this run's scratch directory (`scratch/b1.sh`, `scratch/b1b.sh`). The store was committed on `main` at `.factory/state`, then moved to a `factory-store` worktree at that same path, with the path ignored on `main`. Then:
- Writing `live: 1` into a store record, running `git checkout <pre-move commit>`, and then `git checkout main` printed `after_checkout_old: T-1=[id: T-1]` and `after_back_to_main: T-1=[cat: … No such file or directory]`. The uncommitted record was first overwritten with its old version and then deleted. Git treats ignored files as expendable, and the old commits track that path.
- Merging into `main` a branch that carried a store change made before the move (as catch-up merges do) failed with a modify/delete conflict. `git merge --abort` then deleted the live store file (`store_intact=` printed empty).
At a path the integration branch never tracked, neither can happen. Acceptance scenario "A checkout of an older commit leaves the moved store untouched" checks this.

**B1 against B2 on git's own clean command.** In throwaway repos (`scratch/init.sh`, `scratch/b2.sh`), `git clean -fdxq` in the integration checkout left a B1 store in place (`after_clean_fdx: store=decisions.md`), because git skips a directory that holds its own `.git`. It deleted a B2 store, which is a plain ignored directory (`after_clean_fdx: store_exists=no`).

**B1 needs no git identity at creation, and a clone can restore it.** `git worktree add --orphan -b factory-store .factory/state`, run under a throwaway HOME with no git identity, printed `orphan_add=0`. The branch stays unborn until the first commit. The integration checkout's `git status --porcelain` was empty once the path was in the repo's exclude file. In a clone, `git worktree add .factory/state factory-store` printed `restore=0 … branch=factory-store upstream=origin/factory-store`, so the store came back from the pushed branch. This machine runs git 2.54.0.

**Code checkouts do not need the store.** Roles get the live store's absolute paths in their composed input. `compose.py` reads from the store root, and ticket records name store files by store-relative paths (`factory/cli.py:741`, `root / t["request"]`). Implementer worktrees (`factory/cli.py:247`) and checker checkouts (`factory/cli.py:259`) carry a stale copy of the store today only because their branches start from the integration branch. Nothing reads that copy.

## Root cause

The store sits inside the target repo, at `.factory/state`, as a plain directory (`factory/instance.template.yaml:10`, `factory/instance.py` `own_state_root`). `init_cmd` (`factory/cli.py:845`) creates it there and does nothing more with git, and the operator commits it on the integration branch. The merge gate's containment check (`factory/cli.py:545`) counts every commit on that branch. So a store commit forces a catch-up run. The design's separate `tickets` branch (`docs/design.md:39`, `dev/build-harness.spec.md:152`) was never built in the local version of the build half.

## Out of scope

- A merge-gate exception for store-only commits (option A). The operator set it aside because it only imitates a separate branch. `merge_cmd`, `ticket_join` and `head_contains` do not change.
- Catch-up runs caused by operator commits of documents to the integration branch, such as run-0122's `dev/issues.md`.
- The harness committing or pushing the store by itself. Operators and runner sessions keep committing it by hand, now in the store's own checkout.
- Moving the Nanobot repo's store from this repo. That is a paired ticket on that repo, run by its own Driver session (the session that runs the factory there). This repo treats `~/dev/nanobot-upstream/**` as read-only.
- Rewriting either branch's history. Store history up to the move stays on the integration branch.
- The default `state_dir` for new instances. It stays `.factory/state`, which a new repo has never tracked.
- Role runs that write the live store (T-0024, issue #45).
- Records under `.factory/answers/` and `.factory/green-pilot/`. They stay on the integration branch.

## Open questions

none

## Decisions

- The store lives on its own branch, `factory-store`, checked out as a git worktree at the store's path (B1). This is for the operator to confirm at the spec gate. Rejected: B2, the branch written through git plumbing with no working copy. It needs new harness commands to snapshot, show and restore the store, and `git clean -fdx` in the integration checkout deletes the store (Evidence). Rejected: A, a gate exception (operator, 2026-10-04).
- A store path must be one the integration branch has never tracked. Both existing stores move from `.factory/state` to `.factory/store`. Rejected: keeping `.factory/state`, where checking out an older commit overwrote an uncommitted record and checking `main` out again deleted it (Evidence).
- The branch is named `factory-store`, and the design doc and build spec drop the name `tickets` for it. Rejected: `tickets`, a generic name in a target repo whose branches serve other work, such as the Nanobot repo, which shares its objects with another checkout.
- `init` creates a new store as a worktree on an unborn `factory-store` branch, and the operator makes the first commit. On a clone where the branch already exists, `init` checks it out, which restores the store. Rejected: `init` committing, which needs a git identity, and the suite runs under a throwaway HOME that has none.
- The integration checkout ignores the store through the repo's git exclude file, which `init` and `store migrate` write. Rejected: a line in the target's tracked `.gitignore`. That would change the target's code to record a fact about one clone.
- A new command, `factory store migrate --to PATH`, moves an existing store. It refuses unless the store is idle and committed, and it leaves the integration-branch side uncommitted for the operator to review. Rejected: a hand procedure, untested, run once on each repo by a different session.
- The store branch starts with one commit whose tree is the store as last committed on the integration branch, and whose message names that commit. Earlier history stays readable with `git log <that commit> -- .factory/state`. Rejected: rewriting history with a subtree split. It would follow only part of the store's past, which began at `intake/state`, and it adds nothing that `main`'s history does not already keep.
- An instance whose store is still a plain directory keeps working unchanged. `init` leaves such a store alone and points to `store migrate`. The harness reads and writes the store only through `state_dir`, so it runs with either layout.

## Risk

- Blast radius: where every instance keeps its store, and how operators commit and push it. Code that reads or writes store files is unchanged. The merge gate is unchanged. Merges into the integration branch run in the integration checkout as before (`gitops.merge_no_ff`), and that checkout no longer holds store files.
- Protected paths this change touches: harness (`factory/**`), in `factory/cli.py` and, if helpers go there, `factory/gitops.py`. It touches no `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock` or `docs/prompts/**` file. No prompt block of the design doc changes. The operator's migration (Operator steps) changes `.factory/**` on each instance, at the operator's command.
- Moving a store while it is in use would lose records. `store migrate` refuses while any run is in flight, while a git worktree lies under the store, or while store files are uncommitted. It removes the old directory only after the new checkout holds every file.
- A sub-ticket branch cut before the move still tracks the old path. Merging it after the move fails with a conflict if it carried store changes. It cannot reach the new path. The operator moves a store only when no build is in progress.
- `init` needs `git worktree add --orphan`. It is present in this machine's git 2.54.0, and an older git refuses with git's own error.
- T-0024 (issue #45, role runs writing the live store) has its spec in flight (run-0220). Its list of store-writing commands should include `store migrate`. This change does not alter how a role's shell finds the store: the walk-up to `.factory/instance.yaml` and `state_dir` is the same.
- Until each instance runs its migration, the README describes this repo's store at `.factory/store`, where it does not yet exist.

## Operator steps

1. After merge, with no build in progress, move the runtime to the merged revision. Accept it on this repo with `~/dev/spec-factory-harness/bin/factory --accept-harness <sha> ticket show T-0025`.
2. Move this repo's store. Wait until no ticket has a run in flight. In `~/dev/spec-factory`, commit everything under `.factory/state/` on `main`. Then run `~/dev/spec-factory-harness/bin/factory store migrate --to .factory/store`. Edit `.factory/context.md`: the sentence "The store is tracked on `main` and the operator commits it between steps, so `main` moves even when no ticket merges" becomes a statement that the store at `.factory/store` is a checkout of `factory-store`, committed there and never on `main`. Edit `.factory/README.md` the same way, wherever it gives the live store's path. Review `git status`, commit on `main`, commit the store (`git -C .factory/store add -A && git -C .factory/store commit -m "store: …"`), and push both branches (`git push origin main factory-store`).
   Check: `~/dev/spec-factory-harness/bin/factory paths` prints a `state` ending in `/.factory/store`. `git -C .factory/store symbolic-ref --short HEAD` prints `factory-store`. `git ls-files .factory/state | wc -l` prints `0`, and `git status --porcelain` prints nothing.
3. The Nanobot repo: file a paired ticket there for its Driver session, to run after its in-flight builds merge. A git worktree for T-0001.1 was live under its store on 2026-10-04. The ticket covers the runtime acceptance, the same `store migrate --to .factory/store`, that repo's `context.md`, and which of its remotes (`fork`, `nas`) carries `factory-store`. That repo shares its objects with `~/dev/nanobot`, so the branch appears there too.
4. From then on, commit store changes in the store checkout and push `factory-store`. The integration branch moves only on merges and document commits.

=== design.md
## Proposed change

### Choice of layout: B1 and B2 compared

The request asks for the two layouts to be weighed on six points. Both put the store on a branch that is never merged into the integration branch, and both need the new store path (Decisions).

| Point | B1: worktree at the store path (proposed) | B2: branch written by plumbing, no working copy |
|---|---|---|
| Moving an existing store | `store migrate` (part B): the branch starts from the store's last committed tree, a worktree is added at the new path, ignored run files are copied, and the old path is untracked | Same branch creation. The directory moves as a plain directory. |
| What `init` sets up | A worktree on an unborn `factory-store` branch, or the existing branch on a clone, which restores the store | A plain directory. Restoring on a clone needs a new extract command. |
| Implementer worktrees and checker checkouts | Hold no store copy. Code branches never track the store path. | Same |
| How operators and runners commit and push | Plain git in the store: `git -C <store> add -A && git -C <store> commit`, `git push origin factory-store`. `git status` and `git diff` show pending store changes. | A new harness command per commit (temporary index, `write-tree`, `commit-tree`, `update-ref`), and another to show pending changes |
| What breaks | `git log -- .factory/state` on the integration branch ends at the move, and later history is `git log factory-store`. Records quoting the old path are history. | Same. Also no `git status` over the store, and `git clean -fdx` in the integration checkout deletes it (Evidence). |
| Rollback | Detach and re-track (part D, README how-to). The harness needs no rollback. | Move back and re-track |

### A. `init` puts a new store on its branch (`factory/cli.py` `init_cmd`; git helpers may go in `factory/gitops.py`)

1. This applies only to the instance's own store (`instance.is_own_store`). A throwaway store, where `FACTORY_STATE` names another directory, stays a plain directory, as today.
2. Refuse first: if the own store path does not exist, and the integration branch has ever tracked a file under it, refuse with exit 2 and write nothing. That covers `instance.yaml` for a new instance, so the check runs before that write, using `state_dir` from the template. The test is `git log -1 --format=%H <branch> -- <state_dir>` at the repo root. `<branch>` is `gitops.integration_branch` for an existing instance, and the checked-out branch for a new one. The message names the path and that commit. It says that a checkout of any older commit would overwrite a store kept there, and asks for another `state_dir`.
3. When the own store path does not exist:
   - If a local branch `factory-store` exists, or exactly one remote-tracking `<remote>/factory-store` does, run `git worktree add <path> factory-store`. On a clone this restores the store.
   - Otherwise, run `git worktree add --orphan -b factory-store <path>`. This creates no commit, so it needs no git identity.
   - Then, when the path lies inside the repo root, add `/<path relative to the repo root>/` to the exclude file (`git rev-parse --git-path info/exclude`), unless that line is already there.
   - The existing store writes (`.gitignore`, `.gitattributes`, the spec store) then land in the new checkout.
4. When the own store path exists and is not the checkout of `factory-store` (`gitops.checkout_of(repo, "factory-store")`), leave it exactly as today. Also print on stderr that the store is not on its branch and that `factory store migrate --to PATH` moves it.
5. The JSON output gains `store_branch`: `"factory-store"` when the own store is that branch's checkout, otherwise `null`. `written`, `created` and `agents` keep their current meanings and do not list the checkout. A second `init` changes nothing.

### B. `factory store migrate --to PATH` (new `store` subcommand group in `build_parser`)

PATH is relative to the repo root, as `state_dir` is, and it becomes the new `state_dir`.

Refusals. Each exits 2 and changes nothing (no branch, no PATH, no file touched). Check all of them before the first write:
1. The store in use is not the instance's own (`FACTORY_STATE` names another).
2. The store is already the checkout of `factory-store`, or a local branch `factory-store` exists.
3. The integration branch is not checked out at the repo root.
4. A ticket in the store has a run in flight (`in_flight` not empty). Name each run id.
5. A git worktree lies under the store (implementer worktrees, checker checkouts). Name each one.
6. `git status --porcelain -- <state_dir>` at the repo root is not empty. Name the files and ask for them to be committed on the integration branch first.
7. PATH exists, or the integration branch has ever tracked a file under it (the same test as A.2).
8. `instance.yaml` has no `state_dir:` line.

Steps:
1. Create the branch at one root commit: `git commit-tree <branch>:<state_dir> -m "store: carried over from <branch> at <sha>; earlier history: git log <sha> -- <state_dir>"`, then `git branch factory-store <commit>`. This uses the operator's git identity.
2. `git worktree add <PATH> factory-store`.
3. Copy every file that git ignores under the old store into the same relative path under PATH. These are run scratch directories and tripwire baselines, listed by `git ls-files --others --ignored --exclude-standard -- <state_dir>` at the repo root.
4. Check that `git -C <PATH> status --porcelain` is empty. If it is not, exit 1 and leave the old store and the integration branch untouched.
5. At the repo root: run `git rm -r -q --cached <state_dir>`, add `/<PATH>/` to the exclude file, and rewrite only the value on `instance.yaml`'s `state_dir:` line to PATH, keeping its comments. Then delete the old store directory.
6. Log `store.migrated` (`from`, `to`, `branch`, `carried_from`, `copied`) in the new store. Print `{"ok": true, "from", "to", "branch": "factory-store", "carried_from", "copied"}`. On stderr, remind the operator to commit the integration-branch changes, then commit the store in PATH and push `factory-store`.

It makes no commit on the integration branch and pushes nothing.

### C. Tests

Add a new file, `tests/factory/test_store_branch.py`, covering:
- A: a new store is the checkout of `factory-store`, and the integration checkout does not see it. A store commit leaves the integration branch where it was. A clone restores the store from the branch. A tracked path is refused with nothing written. An existing plain store is left alone, with `store_branch: null`. A second `init` is a no-op.
- B: one success case, with the tree carried byte for byte, ignored run files copied, `state_dir` rewritten, the old path untracked and removed, and the store found by later commands. Every refusal, each writing nothing. A checkout of the pre-move commit leaving the new store untouched.
- The merge gate: after a store commit, a sub-ticket with passing rows merges. After a code commit to the integration branch, it is still refused.

Tests that commit set the git identity through `GIT_AUTHOR_*` and `GIT_COMMITTER_*`, because the suite runs under a throwaway HOME.

### D. Documents

- `docs/design.md`:
  - Role-context block paragraph (line 58), the sentence listing what `.factory/` holds: "and the store" becomes the store as a git worktree of the repo's `factory-store` branch. That branch is never merged into the integration branch, so a store commit never moves it. The same sentence states that the store's path is one the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. Use the words "never tracked".
  - Piece 1 row (line 39) and "Smallest thing that works" (line 74, twice): `tickets` branch becomes the store branch `factory-store`.
  - No prompt block changes, so `docs/prompts/` is not re-copied.
- `docs/changelog.md`: the next free entry number (52 unless another change takes it first). Put it after entry 51 and before the closing "Declined:" line, with numbering kept contiguous. It reads "After issue #46 (2026-10-04): …" and names `factory-store`, the worktree at the store path, the never-tracked path rule, `init`'s new store and restore, and `store migrate`.
- `dev/build-harness.spec.md`: every mention of the store branch as `tickets` becomes `factory-store`. That covers `` `tickets` ``, `refs/heads/tickets` and `HEAD:tickets`, on 16 lines: R5, the state line at 152, part A's `factory init`, C, F rule 3, K, items 18 and 91, and Responses. Mentions of the store's `tickets/` directory stay as they are.
- `README.md`, following its "Maintaining this page" rules:
  - "Terms used on this page" gains a "store branch" row.
  - The target bullet in "Where it runs" says the store is a checkout of `factory-store`.
  - Step 1 of "Adopting the factory in a repo" says `init` creates the store on that branch, or restores it on a clone.
  - Two new how-to subsections under "Where it runs":
    - "Committing and pushing the store": the two git commands, and that a store commit never moves the integration branch.
    - "Moving an existing store onto its branch": the preconditions, `factory store migrate --to .factory/store`, and the commits afterwards. Rollback, with no run in flight and the store committed: `rm <store>/.git && git worktree prune` (never `git worktree remove`, which deletes the directory). Then move the directory back, `git add` it on the integration branch, restore `state_dir`, and remove the exclude line.
  - The runner-sessions paragraph drops "and committing the store to the same branch moves it too".
  - "Where things live", "Related work and history" and the "Maintaining" table name `.factory/store/`. Re-derive the ticket count and bump the status date.

### Size and seams

About 400 changed lines in total: A about 40, B about 110, C about 200, D about 70. Each lettered part can be its own sub-ticket. C's tests go with the part they cover. D goes last, because it describes A and B.

## Tests to change

none. No existing test asserts that an own store is a plain directory, that the template gains a key, or that `init`'s `written` or `created` lists change. If an existing test breaks, the implementer reports it rather than editing it.

=== specs/store-setup/spec.md
## ADDED Requirements

### Requirement: A new instance's store is a checkout of its own branch
`factory init` SHALL create a missing own store as a git worktree of branch `factory-store`, which the integration checkout does not see. It SHALL check that branch out when it already exists locally or on one remote, so that a store commit never moves the integration branch.

#### Scenario: init creates the store on the factory-store branch, out of the integration checkout's sight
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; echo "branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/state/')")`
- THEN it prints `branch=factory-store seen_by_main=0`

#### Scenario: init on a clone restores the store from the pushed branch
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/src && cd $T/src && git commit -q --allow-empty -m init && $B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T/src $T/c && cd $T/c && rm -rf .factory/state && $B init >/dev/null 2>&1; echo "exit=$? branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) restored=$(ls .factory/state/decisions.md 2>/dev/null | grep -c .)")`
- THEN it prints `exit=0 branch=factory-store restored=1`

### Requirement: init refuses a store path the integration branch has tracked
`factory init` MUST refuse with exit 2, writing nothing and naming the path, when it would create the own store at a path under which the integration branch has ever tracked a file.

#### Scenario: init refuses a once-tracked store path and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/tgt && cd $T/tgt && mkdir -p .factory/state && echo old > .factory/state/old.md && git add -A && git commit -q -m "old store" && git rm -q -r .factory/state && git commit -q -m "store removed" && $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e .factory ] && echo written || echo none) names_path=$(grep -c '\.factory/state' $T/err)")`
- THEN it prints `exit=2 instance=none names_path=1`

### Requirement: store migrate moves a tracked store onto its branch and keeps every record
`factory store migrate --to PATH` on an idle, fully committed own store that is tracked on the integration branch SHALL do all of the following:
- put the store's last committed tree on a new `factory-store` branch, checked out at PATH;
- copy the store's ignored run files to PATH;
- untrack and remove the old path;
- set `state_dir` to PATH, so that later commands use the moved store.

#### Scenario: store migrate carries the store to factory-store at the new path
- GIVEN the two fixture files written by the block below, run once at column 0 as shown. Every later scenario of this change that names them reuses them.

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

- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && mkdir -p .factory/state/runs/run-0001-triage/scratch && echo n > .factory/state/runs/run-0001-triage/scratch/n.txt && $B store migrate --to .factory/store >/dev/null 2>&1; echo "exit=$?"; echo "branch=$(git -C .factory/store symbolic-ref --short HEAD 2>/dev/null) same_tree=$([ "$(git rev-parse -q --verify 'factory-store^{tree}')" = "$(git rev-parse $PRE:.factory/state)" ] && echo yes || echo no) scratch=$(cat .factory/store/runs/run-0001-triage/scratch/n.txt 2>/dev/null) old=$([ -e .factory/state ] && echo kept || echo gone) main_tracks=$(git ls-files .factory/state | grep -c .) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/store/')"; echo "state_dir=$(sed -n 's/^state_dir: *//p' .factory/instance.yaml) ticket=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0`, then `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0`, then `state_dir=.factory/store ticket=ready-for-triage`

### Requirement: store migrate refuses while the store is in use or uncommitted
`factory store migrate` MUST refuse with exit 2, creating no branch and no new path, when a store file is uncommitted or a run is in flight. The refusal MUST name the uncommitted files or the runs in flight.

#### Scenario: store migrate refuses an uncommitted store and a run in flight
Needs the GIVEN block of "store migrate carries the store to factory-store at the new path" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && echo edit >> .factory/state/decisions.md; $B store migrate --to .factory/store >/dev/null 2>$T25/e1; echo "uncommitted: exit=$? names=$(grep -c 'decisions.md' $T25/e1) branch=$(git branch --list factory-store | grep -c .)"; git checkout -q -- .factory/state/decisions.md && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git add -A && git commit -q -m "run started"; $B store migrate --to .factory/store >/dev/null 2>$T25/e2; echo "in flight: exit=$? names=$(grep -c 'run-0001-triage' $T25/e2) branch=$(git branch --list factory-store | grep -c .) new=$([ -e .factory/store ] && echo written || echo none)")`
- THEN it prints `uncommitted: exit=2 names=1 branch=0`, then `in flight: exit=2 names=1 branch=0 new=none`

### Requirement: A checkout of an older commit leaves a moved store untouched
After `store migrate`, checking out a commit from before the move in the integration checkout, and then checking out the integration branch again, MUST leave every file of the moved store as it was, uncommitted ones included.

#### Scenario: A checkout of an older commit leaves the moved store untouched
Needs the GIVEN block of "store migrate carries the store to factory-store at the new path" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B store migrate --to .factory/store >/dev/null 2>&1 && git commit -q -a -m "store moved to its branch"; (echo live > .factory/store/live.md) 2>/dev/null; git checkout -q $PRE 2>/dev/null && git checkout -q main 2>/dev/null; echo "live=$(cat .factory/store/live.md 2>/dev/null || echo lost) on=$(git symbolic-ref --short HEAD)")`
- THEN it prints `live=live on=main`

=== specs/merge-gate/spec.md
## ADDED Requirements

### Requirement: A store commit does not hold back a merge
On an instance whose store is the checkout of `factory-store`, a store commit made after a sub-ticket's checks SHALL NOT stop `factory merge` from merging that sub-ticket.

#### Scenario: A sub-ticket merges after a store commit
Needs the GIVEN block of "store migrate carries the store to factory-store at the new path" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: rows recorded"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=0 refused=0`

### Requirement: A commit to the integration branch still holds back a merge
`factory merge` MUST still refuse, with `head does not contain main`, a sub-ticket whose head does not contain a commit made to the integration branch after its checks.

#### Scenario: A sub-ticket is refused after a code commit to main
Needs the GIVEN block of "store migrate carries the store to factory-store at the new path" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && echo y > y.txt && git add y.txt && git commit -q -m "code on main"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=2 refused=1`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule, and the build spec SHALL call the store branch only `factory-store`. `docs/changelog.md` SHALL gain one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch and `factory store migrate`. The change MUST add no whitespace errors.

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
- WHEN `(echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') old_cost=$(grep -c 'committing the store' README.md) old_path=$(grep -c '\.factory/state' README.md)")`
- THEN it prints `store_branch=1 migrate=1 old_cost=0 old_path=0`

#### Scenario: The store-branch change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Captured on `main` at `3a3f58c` with a throwaway HOME, running the commands above as written (scripts in this run's `scratch/final.sh`).

- init creates the store on the factory-store branch, out of the integration checkout's sight → NEW. Today it prints `branch=main seen_by_main=6`: the store is a plain directory inside `main`'s checkout, and its six files show as untracked there.
- init on a clone restores the store from the pushed branch → NEW. Today it prints `exit=1 branch=main restored=1`: the store was already committed on `main` by `git add -A`, so the store commit fails with "nothing to commit" and no store branch exists.
- init refuses a once-tracked store path and writes nothing → NEW. Today it prints `exit=0 instance=written names_path=0`.
- store migrate carries the store to factory-store at the new path → NEW. Today it prints `exit=2`, then `branch= same_tree=no scratch= old=kept main_tracks=9 seen_by_main=0`, then `state_dir=.factory/state ticket=ready-for-triage`: `store` is not a command (argparse `invalid choice`), and nothing moves.
- store migrate refuses an uncommitted store and a run in flight → NEW. Today it prints `uncommitted: exit=2 names=0 branch=0`, then `in flight: exit=2 names=0 branch=0 new=none`: both exits come from argparse, which names neither the file nor the run.
- A checkout of an older commit leaves the moved store untouched → NEW. Today it prints `live=lost on=main`: no store can be moved, so `.factory/store` does not exist.
- A sub-ticket merges after a store commit → NEW. Today it prints `exit=2 refused=1`: the store commit lands on `main`, and the gate refuses with `head does not contain main`.
- A sub-ticket is refused after a code commit to main → REGRESSION. It prints `exit=2 refused=1` today, and must still print it.
- The design doc names the store branch and the path rule → NEW. Today it prints `store_branch=0 tickets_branch=2 never_tracked=0`.
- The build spec calls the store branch factory-store → NEW. Today it prints `old_name=16 new_name=0`.
- The changelog records the store branch in one contiguous entry → NEW. Today it prints `CONTIGUOUS`, then `0`.
- The README describes the store branch and the move → NEW. Today it prints `store_branch=0 migrate=0 old_cost=1 old_path=4`.
- The store-branch change adds no whitespace errors → REGRESSION. It prints `exit=0` on `main` today.

STATUS: READY-FOR-CRITIC
CONFIDENCE: medium. The mechanism and both data-loss hazards were reproduced in throwaway repos, and every acceptance command was run on today's code with the output shown. The proposed `init` and `store migrate` are not prototyped as harness code, and the total size estimate of about 400 lines sits at the limit.
ESCALATIONS:
- The request's evidence counts one catch-up run that this change would not have prevented. T-0014.1's catch-up merge (`89e8b7d`, run-0122) brought in only `dev/issues.md`, an operator document commit, not the store. Operator commits of documents to the integration branch will still cause catch-up runs after this change. That needs its own ticket if it matters.
- The B1-or-B2 choice and the store's new path (`.factory/store`) are recorded as Decisions for the operator to confirm at the spec gate, as the request asks. They are not Open questions.
- T-0024 (issue #45, role runs writing the live store) has its spec in flight (run-0220). Its list of store-writing commands should include the new `store migrate`. The planner may need to order the two tickets.
