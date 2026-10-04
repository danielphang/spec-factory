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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0226-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0226-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v2)

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

The prototypes below ran in throwaway repos under a throwaway HOME, from this run's scratch scripts `scratch/proto.sh` and `scratch/proto_merge.sh`. The harness clears those when the ticket moves on, so each paragraph gives the git commands it ran.

**Moving the branch but keeping the old path loses records.** The prototype committed a store record at `.factory/state` on `main` (commit PRE). It then untracked the path (`git rm -r --cached`), added `/.factory/state/` to `.git/info/exclude`, and put the record in a `factory-store` worktree at that same path (`git worktree add --orphan -b factory-store .factory/state`). Then:
- It appended `live: 1` to the record and ran `git checkout PRE`, then `git checkout main`. They printed `after_checkout_old: id: T-1` and `after_back_to_main: … No such file or directory`. The uncommitted line was overwritten by the old version without a warning, and then the file was deleted. Git treats ignored files as expendable, and the old commits track that path.
- It merged into `main` a branch that changed the record before the move, as a catch-up merge would. That printed `merge_exit=1 conflict=1`, a modify/delete conflict. `git merge --abort` then printed `store_intact=` empty: the live record was gone.
At a path the integration branch never tracked, neither can happen. Acceptance scenario "A checkout of an older commit leaves the moved store untouched" checks this.

**B1 against B2 on git's own clean command.** In one repo, a B1 store at `.factory/store` (a `factory-store` worktree) and a B2 store at `.factory/b2` (a plain directory) were both listed in `.git/info/exclude`. `git clean -fdxq` in the integration checkout printed `after_clean_fdx: b1=decisions.md b2=gone`. The B1 store survived, because git skips a directory that holds its own `.git`. The B2 store was deleted.

**B1 needs no git identity at creation, and a clone can restore it.** `git worktree add --orphan -b factory-store .factory/store`, run with no git identity configured, printed `orphan_add=0 status_lines=0`. It succeeded, and the integration checkout's `git status --porcelain` showed nothing once the path was in the exclude file. The branch stays unborn until the first commit. After one store commit, a `git clone` followed by `git worktree add .factory/store factory-store` printed `restore=0 branch=factory-store upstream=origin/factory-store file=decisions.md`: the store came back from the pushed branch. This machine runs git 2.54.0.

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
- T-0024 (issue #45, role runs writing the live store) is on its second spec round (run-0224). Its v1 spec (run-0220) refuses every unmarked write to an own store while a role run is in flight there, and lists only read-only commands as exempt. `store migrate` and `init` would therefore fall under that refusal, which agrees with this change: `store migrate` refuses while a run is in flight in any case. Its fixtures delete files under a new instance's `.factory/state`, which stays the default path for a new instance, now as a worktree. This change does not alter how a role's shell finds the store: the walk-up to `.factory/instance.yaml` and `state_dir` is the same.
- Until each instance runs its migration, the README describes this repo's store at `.factory/store`, where it does not yet exist.

## Operator steps

1. Upgrade the runtime to the merged revision. The runtime is the separate checkout of the harness that runs every ticket, `~/dev/spec-factory-harness`, pinned to one commit; a merge into `main` does not change it. Each repository runs only the harness commit it has accepted, recorded in its `.factory/harness.lock`, and refuses its store commands until it accepts a new one with `--accept-harness <sha>`. With no build in progress, run `git -C ~/dev/spec-factory-harness checkout --detach <sha>` and `uv sync --frozen` there, where `<sha>` is the merged commit. Then accept it on this repo with `~/dev/spec-factory-harness/bin/factory --accept-harness <sha> ticket show T-0025`, where T-0025 is this ticket.
2. Move this repo's store. Wait until no ticket has a run in flight. In `~/dev/spec-factory`, commit everything under `.factory/state/` on `main`. Then run `~/dev/spec-factory-harness/bin/factory store migrate --to .factory/store`. Edit `.factory/context.md`: the sentence "The store is tracked on `main` and the operator commits it between steps, so `main` moves even when no ticket merges" becomes a statement that the store at `.factory/store` is a checkout of `factory-store`, committed there and never on `main`. Edit `.factory/README.md` the same way, wherever it gives the live store's path. Review `git status`, commit on `main`, commit the store (`git -C .factory/store add -A && git -C .factory/store commit -m "store: …"`), and push both branches (`git push origin main factory-store`).
   Check: `~/dev/spec-factory-harness/bin/factory paths` prints a `state` ending in `/.factory/store`. `git -C .factory/store symbolic-ref --short HEAD` prints `factory-store`. `git ls-files .factory/state | wc -l` prints `0`, and `git status --porcelain` prints nothing.
3. The Nanobot repo: file a paired ticket there for its Driver session, the operator session that runs the factory on that repo, to run after its in-flight builds merge. A git worktree for that repo's sub-ticket T-0001.1 was live under its store on 2026-10-04, and `store migrate` refuses while one is. The ticket covers the runtime acceptance, the same `store migrate --to .factory/store`, that repo's `context.md`, and which of its remotes (`fork`, `nas`) carries `factory-store`. That repo shares its objects with `~/dev/nanobot`, so the branch appears there too.
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
- `docs/changelog.md`: the next free entry number (52 unless another change takes it first). Put it after entry 51 and before the closing "Declined:" line, with numbering kept contiguous. It reads "After issue #46 (2026-10-04): …" and names `factory-store`, the worktree at the store path, the never-tracked path rule, `init`'s new store and restore, and `store migrate`. Like every entry, it is one line, and it states the path rule with the words "never tracked" (a space, no hyphen).
- `dev/build-harness.spec.md`: every mention of the store branch as `tickets` becomes `factory-store`. That covers `` `tickets` ``, `refs/heads/tickets` and `HEAD:tickets`, on 16 lines: R5, the state line at 152, part A's `factory init`, C, F rule 3, K, items 18 and 91, and Responses. Mentions of the store's `tickets/` directory stay as they are.
- `README.md`, following its "Maintaining this page" rules:
  - "Terms used on this page" gains a "store branch" row.
  - The target bullet in "Where it runs" says the store is a checkout of `factory-store`.
  - Step 1 of "Adopting the factory in a repo" says `init` creates the store on that branch, or restores it on a clone.
  - Two new how-to subsections under "Where it runs":
    - "Committing and pushing the store": the two git commands, and that a store commit never moves the integration branch.
    - "Moving an existing store onto its branch": the preconditions, `factory store migrate --to .factory/store`, and the commits afterwards. Rollback, with no run in flight and the store committed: `rm <store>/.git && git worktree prune` (never `git worktree remove`, which deletes the directory). Then move the directory back, `git add` it on the integration branch, restore `state_dir`, and remove the exclude line.
  - The "Parallel builds across tickets" paragraph under "Running many tickets" drops the clause "and committing the store to the same branch moves it too" (wrapped across two lines today), and says a store commit no longer moves the integration branch.
  - Every place that gives the live store's location names `.factory/store/`: the `.factory/` row of "Where things live", the store sentence of "Related work and history", and the log and ticket paths in the "Maintaining this page" table. The two `state/` labels in the "Where it runs" diagram become `store/`. Re-derive the ticket count and bump the status date. The how-to above may name the old path it moves from.

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
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule, and the build spec SHALL call the store branch only `factory-store`. `docs/changelog.md` SHALL gain one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch and `factory store migrate`, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location. The change MUST add no whitespace errors.

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
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 old_cost=0 old_refs=0`

#### Scenario: The store-branch change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Captured on `main` at `3a3f58c` with a throwaway HOME, running the commands above as written. Round 1 captured every item; round 2 re-ran the one scenario it changed, "The README describes the store branch and the move". `main` has not moved since.

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
- The README describes the store branch and the move → NEW. Today it prints `store_branch=0 migrate=0 old_cost=1 old_refs=4`: no mention of the branch or the command, the retired clause is present, and four lines give `.factory/state/` as the store's location (lines 403, 418, 457, 462).
- The store-branch change adds no whitespace errors → REGRESSION. It prints `exit=0` on `main` today.

## Responses

- [BLOCKING] Operator steps, step 1, "the runtime" and `--accept-harness` unglossed → FIXED. Step 1 now opens by saying what the runtime is (the separate, pinned checkout of the harness that runs every ticket, unchanged by a merge into `main`) and what `--accept-harness <sha>` does (a repository runs only the harness commit recorded in its `harness.lock`, and refuses store commands until it accepts a new one). It then gives both upgrade commands from README "Upgrading the runtime" (`git -C ~/dev/spec-factory-harness checkout --detach <sha>`, `uv sync --frozen`). Step 3 also glosses "Driver session" and the Nanobot sub-ticket id.
- [SHOULD-FIX] README scenario, `old_cost` forbids the phrase the new how-to needs → FIXED, though not with the suggested grep. The suggested `grep -c 'committing the store to the same branch' README.md` already prints `0` on `main` today, because the clause is wrapped across README lines 306 and 307, so it would prove nothing. The scenario now joins the page into one line first: `tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch'` prints `1` today. On a simulated rewrite that drops the clause and adds a how-to about committing the store on `factory-store`, it prints `0`. Design.md D now names that paragraph and says the clause is wrapped.
- [SHOULD-FIX] D's changelog bullet does not ask for the literal words "never tracked" → FIXED. The bullet now says the entry is one line and states the path rule with the words "never tracked", a space and no hyphen.
- [NIT] README scenario, `old_path=0` forbids the old path anywhere, including the how-to → FIXED by narrowing. `old_refs` counts only the four lines that give the live store's location: the parenthesised path in "Where things live" (README line 403), the store sentence in "Related work and history" (line 418), and the `.factory/state/log` and `.factory/state/tickets` paths in the "Maintaining this page" table. It prints `4` today. On the simulated rewrite, whose how-to names `.factory/state/` as the path it moves from, it prints `0`. Design.md D lists those places, and also the two `state/` labels in the "Where it runs" diagram, which no check pins.
- Note on the cleared scratch scripts → FIXED. Evidence now states the git commands each prototype ran and quotes their output. I re-ran all four prototype claims in this run's scratch under a throwaway HOME, with the same results as round 1: checkout overwrote and then deleted the record, the merge abort lost it, `git clean -fdx` kept B1 and deleted B2, and an orphan worktree needs no identity and is restored in a clone.
- Issue number. The operator's relayed note calls this issue "45". This request is GitHub #46; #45 is T-0024's issue. The spec keeps #46.

## Current truth: build-dispatch

# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

## Current truth: store-setup

# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)

## Your prior findings (round 1)

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

STATUS: REVISE
CONFIDENCE: high, every cited path, figure and acceptance command I ran matched the spec, and the one blocking finding is a one-sentence gloss.
ESCALATIONS: none

## Previous spec version (v1)

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
