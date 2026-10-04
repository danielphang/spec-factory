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
