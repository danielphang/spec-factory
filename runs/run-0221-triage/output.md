Type: feature (a design change to where each instance keeps its store; it removes wasted runs rather than fixing wrong output)

Title: Isolate the store from the integration branch: store commits move main and force catch-up runs

Summary:
Every commit to the store forces a catch-up run on any sub-ticket that is mid-check, and none of those commits can change what the checks tested. The store (`.factory/state/`, the factory's ticket, approval and run records for one repository) is tracked on the integration branch, the branch sub-tickets merge into. The merge gate (the step that merges a sub-ticket once its checks pass) refuses a head that does not contain that branch. So a store-only commit makes the implementer merge the branch in and both checkers re-run, at about 10 to 20 minutes and about 1M tokens each time. The requester wants the store moved onto its own branch, still versioned and pushed, so the integration branch moves only on merges. The spec should compare B1 (a store branch checked out as a worktree at the store path) with B2 (a store branch written through git plumbing, with no working copy) on: migrating both instances' existing store history and paths, what `init` sets up, how worktrees and checker checkouts see the store, how operators and runners push, what breaks, and rollback.

Evidence:
- Request: retro trial escalation C1 counted 4 catch-up runs caused this way: run-0082, run-0085, run-0099, run-0122. All four run directories exist under `.factory/state/runs/` (`run-0082-implementer`, `run-0085-implementer`, `run-0099-implementer`, `run-0122-implementer`). I did not find the retro trial's C1 write-up itself in this repo. Other documents only refer to it: `.factory/state/requests/T-0023.md:18` and `.factory/state/plans/T-0018.md`.
- Request: on 2026-10-04 T-0023.3's merge was refused with "head does not contain main" after store commit `5ea66e9`. Verified: `git log` shows `5ea66e9 store(T-0023): .1 and .2 merged; ...` followed by `a1b2718 Merge main into factory/T-0023.3 (conflict run: store commits only)`. `git show --name-only --format= a1b2718 | grep -v '^\.factory/state/'` prints nothing. That means the catch-up merge brought in only store files, so it could not have changed what the checkers tested.
- The refusal is in the gate code. `factory/cli.py:546-550` sets `merge_refused = "head does not contain main"` and raises `Refused(... merge it into {branch} and re-check)`. `factory/cli.py:594` parks the ticket after `MAX_CONFLICT_RUNS` such runs.
- The operator decision record the request cites exists: `.factory/answers/T-0023.3-operator-decision.md`.
- Instance A (the Nanobot fork, `~/dev/nanobot-upstream`, branch `feat/lionbot-v3.5`) also tracks its store on its integration branch: `git ls-files .factory/state` there lists approvals and other records. So the change applies to both instances, as the request says.
- T-0023 deferred this explicitly. `.factory/state/requests/T-0023.md:18` says: "Moving the store off `main` is a design change."
- Operator, relayed with this run: "it's basically option A or B. Worktree and/or branch ; your A is simulating B". This matches the request's framing. Option A, a gate exception for store-only commits, is set aside because it only imitates a separate branch. The choice between B1 and B2 is left open.

Assumptions (mine, not stated by the requester):
- Option A is out of scope as a solution. The spec may describe it only as the rejected comparison. This follows from the operator's relayed note and the request's "(for comparison, not preferred)".
- "Worktree and/or branch" means the operator has not yet chosen between B1 and B2. It may also allow a hybrid. The spec weighs them and recommends one, and the operator decides at the spec gate. No separate triage question is needed, because the request already sends that choice to the spec gate.
- The spec changes the design doc and the harness, given the labels "harness, design-doc". Under this repo's conventions that means a `docs/changelog.md` entry, a consistent `dev/build-harness.spec.md`, and a README update for any changed path or command.
- Migrating instance A's store happens on instance A, driven by its own Driver session. It follows the T-0012 pattern (a paired ticket there) and is not done from this repo, which treats `~/dev/nanobot-upstream/**` as read-only.
- Suggested priority (a suggestion; priority is the operator's call): high. Each occurrence costs about 1M tokens. The 2026-10-04 occurrence also led to the hand-edited-results incident.

Reason:
No duplicate. Searched the GitHub issues (`gh issue list --state all`), `dev/issues.md`, and the store's tickets, requests, specs and plans for "catch-up", "integration branch", "store branch" and "orphan". The only matches were T-0023's explicit deferral of this exact change and this ticket's own request. The nearest issue is #45 / T-0024 ("Roles can write the live instance store"). That is a different problem: a role writing the store, not store commits moving the branch.

The intent is clear and the product decision is already made: real isolation on a separate branch, not a gate exception. The remaining B1-or-B2 choice is a design trade-off the request sends to the spec, and the gate is not pre-approved. The operator decides it there.

Out-of-scope observations:
- Issue number. The operator's note calls this "45". On GitHub this request is #46 ("Isolate the store from the integration branch...", opened 2026-10-04T17:50:05Z), and this ticket's source file is named `46_store_branch.md`. #45 is the roles-writing-the-store issue (T-0024). `dev/issues.md` indexes up to #45 and has no #46 row yet.
- Overlap with T-0024 (#45), whose spec writer is in flight (run-0220). B1 would make the live store a separate worktree, which changes where the store lives and how a role's shell could reach it. The two specs should not contradict each other. The spec writer for this ticket should read T-0024's spec, and the planner may need a cross-ticket dependency.

STATUS: ACCEPT
CONFIDENCE: high. The cited commits, gate code, run directories and decision record exist, and the operator's relayed note settles the only product question; the one gap is that the retro C1 write-up was not found in this repo.
ESCALATIONS: none
