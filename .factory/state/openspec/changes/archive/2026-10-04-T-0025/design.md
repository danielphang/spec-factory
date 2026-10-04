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

