**Verdicts**

- **T-0024 / #45 (dispatcher fence): APPROVE WITH CHANGES.** The design is sound and fail-safe; one SHOULD-FIX closes the two leak routes the spec itself lists as open (copied/exported marker), and two NOTEs.
- **T-0025 / #46 (store on `factory-store` worktree): REVISE.** B1 is the right layout and the migration is careful, but one BLOCKING interaction with `init` reopens the exact #45 incident route inside the live store, and the spec's claim that it "does not alter how a role's shell finds the store" (v2.md:89) is false for `init`. Three SHOULD-FIXes, several NOTEs.
- **Build order: #45 first, then #46 rebased on it.**

Evidence base: both specs read in full; harness at `~/dev/spec-factory-harness` @ `0273393` (`factory/cli.py`, `instance.py`, `gitops.py`, `store.py`, `workflows/*.js`, `tests/factory/test_instance.py`); git behaviour probed in a throwaway repo in my scratchpad (no factory command run, nothing edited).

---

**Q1. #45 fence gaps; is "in flight on any ticket" the right trigger?**

Yes. The tool cannot tell who is calling (`factory/instance.py:55-64` resolves purely from cwd), so "any run in flight on this store" is the only signal it has, and leaving the fence up for a dead run is the fail-safe direction (v3.md:64). Gap assessment:

- Write between runs: open, acknowledged (v3.md:76). Window is seconds; acceptable.
- Run dies, left in flight: fence stays up until a marked `run finish --status-override KILLED`. Correct behaviour.
- Role subprocess writing store files directly: out of scope, only the protected-path rule limits it (v3.md:80). Acceptable; #37 is the real answer.
- Clerk commands for other tickets during a run: all clerk commands are marked (`intake.js:26-27`, `build.js:21-23` after part B). Fine.
- NOTE: the suite route from the incident still *fails* the test after #45 (just safely). On base it also failed (v3.md:25: `1 failed` with `agents=written`). So #45 adds no new gate flakiness; the suite-guard issue (run-0198) should still be filed so instance B's verifier doesn't trip on it when a role sets `TMPDIR` into scratch.

**Q2. "Every command except a fixed read-only list" as default: right?**

Right, and the list is correctly classified. I checked each: `ticket show` (`cli.py:84-94`), `ticket join` (`:579-617`, pure decision via `out()`), `results show` (`:519-524`), `config` (`:1019`), `status parse` (`:1023`), `log tail` (`:1027-1037`) call no writer; `paths` and `init` bypass `main()` anyway (`:1196`). The three "look like reads but write" cases (`ready-implementers`, `parent-check`, `spec tasks`) are correctly fenced. Default-deny for new commands is right; `store migrate` from #46 will be fenced automatically.

NOTE (usability, not a defect): with parallel builds something is nearly always in flight, so the operator will type the marker on most commands and the spec's own warned failure mode (exporting it, v3.md:79) becomes tempting. The Q3 change mitigates this.

**Q3. Marker copyability: cheap stronger option the spec missed.**

SHOULD-FIX for #45 (`factory/cli.py` fence function, design A.3): add a second trigger that does not depend on the marker at all. The fence already has `instance.caller_cwd()`. If the caller's cwd lies under `<own store>/runs/` or `<own store>/worktrees/`, refuse the write **even when `FACTORY_DISPATCH=1` is set**. Why: a role's scratch dir and the checker/implementer checkouts are always under the store (`cli.py:247`, `:259`; `store.py:49-52`); the operator and the clerk never run from there (the clerk runs from the harness repo root, `intake.js:52`). This positively identifies "I am inside a run" and would have stopped the incident (cwd was `TMPDIR` inside scratch) regardless of a copied marker or a shell that exported it, which are the two routes the spec leaves open (v3.md:79, :65). Cost: ~5 lines, no new scenario machinery (the existing fixture already leaves the shell in `sub/scratch`; add one case inside the store). It still is not a security boundary, and the spec should keep saying so.

NOTE: the refusal text "use a throwaway FACTORY_STATE" is wrong advice for the operator, the only human who will ever read it, and the marker is deliberately unnamed. Acceptable given the decision (v3.md:58), but the README paragraph must be unmissable; expect one confused first encounter per runner session.

**Q4. #46: does the `factory-store` worktree at `.factory/store` break anything? Migration safe/reversible?**

Probed in a scratch repo (git 2.54): a store worktree with store `.gitignore` present.
- Build worktrees and checker checkouts nested *inside* the store worktree (`<store>/worktrees/T-x`, `<store>/runs/<id>/wt`): `git worktree add` works for both, and the store's status stays clean because `worktrees/` and `runs/*/wt/` are already ignored (`store.py:49`). OK.
- Gate commands: unaffected. Nanobot's `{integration}/.factory/channel-requirements.txt` is tracked on the integration branch, not in the store (confirmed via `git ls-files .factory` on green). OK.
- `git clean -fdx` in the integration checkout: store kept. **`git clean -ffdx`: store deleted** (nested-repo override). NOTE: README how-to must say "never `-ff`"; the spec only tests `-fdx` (v2.md:46).
- Fresh clone: `init` restores from `origin/factory-store`. OK for spec-factory (one remote). **SHOULD-FIX for nanobot:** A.3 (v2.md:121-122) says "exactly one remote-tracking `<remote>/factory-store`", else create an orphan. Green has two remotes, `fork` and `nas`; once both carry the branch, a clone/second checkout with no local branch would silently get a *new empty orphan* `factory-store`. Change A.3 to: if more than one remote has it and no local branch exists, refuse and name the remotes.
- Pushes: fine. On nanobot, `~/dev/nanobot` and `~/dev/nanobot-upstream` are worktrees of one repo (`git worktree list` shows both), so `factory-store` and the shared `.git/info/exclude` line appear in blue too. Harmless, but the paired ticket should say so.
- Nanobot instance: `store migrate` will refuse until the live worktree and uncommitted store files clear. Right now green has worktree **`.factory/state/worktrees/T-0004.1`** (the spec says T-0001.1, v2.md:97, stale) and 11 uncommitted files under `.factory/state`. Correct the fact; the refusal logic is right.
- Migration safety: preconditions are good. NOTE: step 4's `git -C <PATH> status --porcelain` check (v2.md:146) cannot see ignored files, so the step-3 copy of scratch/tripwire files is never verified before step 5 deletes the old directory. Compare the two `ls-files -o -i` lists (or file counts) before deleting.
- Reversibility: the README rollback (v2.md:175) is correct, including the `git worktree remove` warning. After rollback, post-move store history stays on `factory-store`; main gets one re-add commit. Acceptable.
- NOTE: checking out a pre-move commit at the repo root recreates `.factory/state/` and an `instance.yaml` saying `state_dir: .factory/state`; any factory command during that checkout hits the stale copy. Transient; worth a line in README.
- Positive side effect: today `init` run from inside the runtime checkout (`~/dev/spec-factory-harness`, a worktree with a tracked stale `.factory/state`) would write into that stale copy; under #46 it fails loudly ("already used by worktree", probed). Good.

**Q5. Interaction after #46 lands; code conflicts; build order.**

How `bin/factory` finds the store: unchanged in principle. `bin/factory` exports the caller's cwd (`bin/factory:9`), `instance.find()` walks up to the nearest `.factory/instance.yaml` (`instance.py:60-63`), and `state_dir` names the store (`instance.py:93-95`). From a role's scratch dir *inside the store worktree*, the walk passes `.factory/store` (no `.factory/instance.yaml` there) and finds the live instance, so #45's fence fires correctly for ordinary commands. From a code checkout (implementer worktree, checker checkout), it finds the checkout's tracked `instance.yaml`, whose own store `<checkout>/.factory/store` does not exist, so no tickets, no fence; stray writes land in a directory the shared `info/exclude` hides, and cannot reach the live store. That is strictly better than today's "tracked copy that could merge" (v3.md:78).

**BLOCKING for #46: `init` is the exception.** `init_cmd` does not use the walk-up; it uses `git rev-parse --show-toplevel` (`cli.py:821-825`, `:853`). From a scratch dir inside the store worktree that returns **the store worktree root**, not the repo root (probed: `A toplevel from scratch inside store: .../repo/.factory/store`). So the exact incident command, `bin/factory init --repo-name x` run from a `TMPDIR` under scratch (`tests/factory/test_instance.py:132-135`), would: find no `instance.yaml` at `<store>/.factory/`, create a **new phantom instance inside the live store worktree** (`<store>/.factory/instance.yaml`, `context.md`, `harness.lock`, `<store>/.claude/agents/*`, and a nested store `<store>/.factory/state/` with its own spec store). #45's fence does not fire because a brand-new instance has no tickets (v3.md:111). Those files are not ignored by the store's `.gitignore`, so the operator's `git -C .factory/store add -A` commits them. And from then on, every role command run from any scratch dir walks up to the phantom instance first, so roles silently talk to the wrong store. Fix (small): in `init_cmd`, resolve the main worktree instead of the toplevel (e.g. parent of `git rev-parse --git-common-dir`, or refuse when the toplevel is `gitops.checkout_of(repo, "factory-store")` or when `caller_cwd()` lies under an instance found by the walk-up). Then an existing instance is found and #45's `init` fence applies. Add a scenario: `init --repo-name x` from `<store>/runs/<id>/scratch` with a run in flight prints `exit=2`, store unchanged.

Conflicts: both specs edit `init_cmd` (#45 inserts a fence call after `cfg`/`root` load; #46 adds the A.2 refusal before the `instance.yaml` write and restructures store creation) and `build_parser`/`main()` (#45 fence call at `cli.py:1201-1202`; #46 adds a `store` subparser). Textual conflict in `init_cmd` is certain; semantic conflict is nil as long as #46's implementer keeps #45's fence and the ordering "fence before any write". Both add a changelog entry and both already handle "whichever merges first". Minor ordering NOTE for #46 part A: on an existing instance in a code checkout, A.3's `git worktree add` fails ("already used by worktree") *after* agent files were copied (`cli.py:883-887`); do the worktree step first so the failure is a clean refusal.

Build order: **#45 first.** It is 20 lines, closes a hazard that has fired twice, and needs no migration window. Then **#46 on top of #45**, carrying: the `init` main-worktree fix (BLOCKING), the multi-remote rule (SHOULD-FIX), the copy verification before delete (NOTE), the `-ffdx` and pre-move-checkout README lines (NOTE), the T-0004.1 correction (NOTE), and a sentence saying `store migrate` is fenced by #45's default and that migration runs with nothing in flight (already true by its own precondition 4).

**Q6. Other things the operator should know before approving**

- #45: `FACTORY_DISPATCH=1` will be in `intake.js`/`build.js`, which instance B's roles read as their subject matter. The spec is honest about this (v3.md:65). The Q3 location check is what makes that acceptable rather than cosmetic.
- #45 Evidence relies on `run_start` appending the parent-close verifier to `in_flight` (`cli.py:231`); README:102 says otherwise. Code wins, README is stale; the spec notes it (v3.md:96). Fix README in #45 since it already touches it.
- #46: the Nanobot instance's `protected_paths.infra` lists specific files, not `.factory/**` (green `instance.yaml`), so neither `.factory/state` today nor `.factory/store` tomorrow is a protected path for nanobot roles. Pre-existing; the paired ticket should add `.factory/store/**`.
- #46 reduces the blast radius of a stray role write in a code checkout to an excluded, invisible directory; that is a quiet failure. Acceptable, but say so in the design doc so nobody is surprised by `no ticket T-xxxx` from inside a checkout.

**Findings list (severity, spec, anchor)**

1. BLOCKING, #46: `init` from a cwd inside the store worktree resolves the store as the repo (`cli.py:821-825`, `:853`) and creates a phantom instance inside the live store, unfenced by #45; spec claim at v2.md:89 is false for `init`.
2. SHOULD-FIX, #45: add a cwd-under-`<store>/runs|worktrees` trigger that refuses regardless of the marker (design A.3, v3.md:104-107); closes v3.md:79 and :65.
3. SHOULD-FIX, #46: A.3 "exactly one remote" (v2.md:121) silently creates an empty orphan `factory-store` when two remotes carry it (nanobot: `fork`, `nas`); refuse instead.
4. SHOULD-FIX, #46: stale operator fact, live worktree is `T-0004.1` not `T-0001.1` (v2.md:97); 11 uncommitted store files on green today.
5. NOTE, #46: migration step 4 cannot verify ignored-file copy before step 5 deletes the old store (v2.md:145-147).
6. NOTE, #46: `git clean -ffdx` deletes the store worktree (only `-fdx` tested, v2.md:46); README must say so.
7. NOTE, #46: part A should run the worktree step before the agent-file copy (`cli.py:883-887`) so a "branch already checked out" failure writes nothing.
8. NOTE, #46: checking out a pre-move commit recreates `.factory/state` and an old `state_dir`; commands during that checkout hit the stale copy.
9. NOTE, #45: refusal text hint ("throwaway FACTORY_STATE") misleads the operator by design; README paragraph is load-bearing.
10. NOTE, #45: file the suite-guard issue (run-0198) alongside; the test still fails (safely) when `TMPDIR` is inside scratch.
11. NOTE, nanobot: `.factory/store/**` is not a protected path on instance A; add in the paired ticket.

**Recommended build order:** T-0024 (#45) → T-0025 (#46) rebased on it with findings 1, 3, 4 applied to the spec before planning.