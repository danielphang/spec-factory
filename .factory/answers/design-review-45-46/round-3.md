**Design review, round 3 — T-0025 (#46) v4 only**

Evidence base: round 2, `changes-2.md`, #45 v5 and #46 v4 read in full; harness `~/dev/spec-factory-harness` @ `0273393` (`cli.py` `_git_toplevel`/`init_cmd`/`main`, `instance.py`, `gitops.checkout_of`/`integration_branch`, `store.STORE_GITIGNORE`); git re-probed in a throwaway linked-worktree layout under my scratchpad (blue main worktree, green linked worktree holding the instance, store worktree under green, nested throwaway repo under a run's scratch, detached store HEAD). No factory command run, nothing edited.

---

**Round-2 findings**

| # | Status | Resolving text |
|---|---|---|
| N1 (SHOULD-FIX, #45 scenario flips under #46) | **RESOLVED** | #45 v5:275 runs the throwaway `init` from `$T/tgt`; #46 v4:109 (Risk) walks all five #45 `init` WHENs and v4:222-224 keeps "Tests to change: none" with the reason. The writer's correction of the request's premise is right: v5:252 still runs `init` from `$W`, and I confirm its output is unchanged (A.1.1 fires on `refs/heads/factory-store`, exit 2, nothing written, so `scratch_init=2 store=unchanged agents=none` holds; only the message text moves from #45's location rule to A.1). v5:234 (`sub/scratch`, in the code checkout) is still refused by #45's in-flight rule after A.1 passes; v5:287 and v5:302 run from the root. |
| N2 (NOTE, detached store HEAD) | **RESOLVED** | v4:151-153 (A.1.2), Decision v4:93, Evidence v4:56 and :58, scenarios v4:298-306, Risk v4:110. The same-repository qualifier is correct and necessary: probed on the nanobot-shaped layout, `--path-format=absolute --git-common-dir` from the store worktree and from the green repo root both print `blue/.git`; from a throwaway repo under `runs/r1/scratch` it prints that repo's own `.git`. Detached store: `symbolic-ref -q HEAD` rc=1, `--show-toplevel` is still the store root, so `top == own` catches it. |
| N3 (NOTE, missing `tickets/`) | **RESOLVED** | v4:155 points at #45 A.2 (v5:127) in one clause and does not restate it. |
| N4 (NOTE, unconditional fence) | **RESOLVED** | v4:155 ("stays unconditional: on a new instance it does nothing"), v4:108. |
| N5 (NOTE, `grep -c` line count) | **RESOLVED** | v4:154 and v4:157 ("one line"), scenario v4:312 uses `grep -q`. |

---

**New findings**

**M1. SHOULD-FIX, #46 `design.md` part C (v4:192).** "`init` from a scratch directory inside the store worktree … with `FACTORY_INSTANCE` set it is not refused." Once #45 lands this is false as written: with `FACTORY_INSTANCE` naming the live instance and `FACTORY_STATE` unset, A.1 is skipped, A.2 resolves `root` as the own store, and #45's fence (`init_cmd` call, v5:135) refuses by the location rule because `caller_cwd()` lies under `own/runs/` (v5:129), marker or not, run in flight or not. The test is only satisfiable with `FACTORY_STATE` naming a throwaway store (then `is_own_store` is false and the fence is skipped), or with `FACTORY_INSTANCE` naming another instance. The requirement text (v4:291) is fine ("with `FACTORY_INSTANCE` unset"); only this test-list clause contradicts #45. Fix, one clause: "with `FACTORY_INSTANCE` set and `FACTORY_STATE` naming a throwaway store, A.1 does not refuse it (#45's location rule still refuses an own-store write from there)". Same class as round-2 N1, so the same grade.

**M2. NOTE, #46 (v4:153, Risk v4:110-111).** A.1.2 reaches the live instance only because the store lies under the repo root, so the walk-up from inside it passes through `<repo>/.factory/instance.yaml`. A.3.4 ("when the path lies inside the repo root") allows a `state_dir` outside the repo; for such a store on a detached HEAD, `find()` returns None, A.1.2 lapses and the phantom route reopens. Both real instances use `.factory/store`, so no action beyond a Risk sentence: the second condition assumes an in-repo store.

**M3. NOTE, #46 (v4:162-163, A.5/A.6).** `gitops.checkout_of` (`gitops.py:92`) keys on a `branch refs/heads/factory-store` line; for a detached store, `git worktree list --porcelain` prints `detached` instead (probed). So `init` from the repo root with the store detached prints the A.5 stderr "store is not on its branch … `store migrate --to PATH` moves it" and reports `store_branch: null`, while `store migrate` would refuse it (B refusal 2, local branch exists). Say "a plain directory" rather than "not the checkout of `factory-store`" for the warning, or test "a worktree of this repository at the store path" (common dir equal) and reserve the migrate hint for a plain directory.

**M4. NOTE, #46 (v4:157, A.3.1).** For a new instance `<branch>` is "the checked-out branch"; a repo root on a detached HEAD has none and `gitops.integration_branch`'s `--abbrev-ref HEAD` prints `HEAD`. Say "or `HEAD` when detached", which `git log -1 HEAD -- <state_dir>` accepts.

**M5. NOTE, #46 (v4:153).** "whose config loads" is not enough for `instance.own_state_root`, which indexes `cfg["state_dir"]` (`instance.py:94`); a config without the key raises `KeyError`, not `Refused`. Add "and has `state_dir`" to the lapse clause, or let it refuse.

**M6. NOTE, #46 (v4:332, scenario "store migrate refuses an uncommitted store and a run in flight").** The in-flight half runs `store migrate` unmarked with a run in flight on the own store, so after #45 it is refused by #45's fence (`… in flight: run-0001-triage`), not by B refusal 4. The expected output still holds (exit 2, one line naming the run, no branch, no PATH), so nothing breaks, but B.4 is never exercised by a scenario. Part C's rule (v4:196, "mark them as #45's tests do") would have the WHEN carry `FACTORY_DISPATCH=1`; the output is unchanged either way.

**M7. NOTE, no action.** Re-checked N6 against the separate-repo scenario: `runs/*/scratch/` is in `STORE_GITIGNORE` (`store.py:49-52`), so the throwaway repo a role creates there is invisible to `git -C <store> add -A`. (A store built by git alone without that `.gitignore`, as in my probe, fails `add -A` on a nested repo with no commit; the fixtures run `init`, which writes the `.gitignore`, before any nested repo exists.)

---

**Cross-spec agreement with #45 v5**

- `init_cmd` order: #46 A.1 → A.2 (config in memory, `root`, #45 fence, existing refusals) → A.3 (store refusals, `worktree add`) → A.4 writes. #45's "fence right after `root`" (v5:135) is kept and moved ahead of the new-instance `instance.yaml` write, which is earlier than #45's own placement (`cli.py:865` writes before `:870`). Agreed.
- Unconditional fence: v4:155 and v4:108 match v5:135. Agreed.
- `main()`: #46 adds only the `store` subparser; `store migrate` is fenced by #45's default (v4:167, v5:134). Agreed.
- Scenarios once both land: all five #45 `init` WHENs plus the fixture `init` and the e2e intake (v5:302) keep their outputs; v5:252 changes only its refusal text. #46's scenarios under #45's fence: the clone-restore and two-remote `init`s hit #45 A.2 with no `tickets/` (v5:127) and pass; the separate-repo `init` is fenced on `other`'s own store with nothing in flight and passes; every `ticket new`/`run start` in the three fixtures runs from the root before a run is in flight; the migrate success scenario runs on an idle store. The one line that breaks is M1.

---

**Verdict: NOT CLEAR** — M1 (SHOULD-FIX) open, a one-clause correction to part C (v4:192) that the operator can take as a gate edit, as #45's N1/N3 were. M2-M6 are NOTEs for the writer or implementer. Build order unchanged: T-0024 (#45) first, T-0025 (#46) rebased on it.