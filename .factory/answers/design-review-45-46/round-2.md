**Design review, round 2 — T-0024 (#45) v4 and T-0025 (#46) v3**

Evidence base: round 1, both change requests and both new specs read in full; harness `~/dev/spec-factory-harness` @ `0273393` (`factory/cli.py` init_cmd/main, `instance.py`, `gitops.py`, `store.py`, `tests/factory/test_instance.py`); git behaviour re-probed in a throwaway repo in my scratchpad (store worktree, nested checker worktree, detached store HEAD). No factory command run, nothing edited.

---

**Round-1 findings**

| # | Finding | Status | Resolving text |
|---|---|---|---|
| 1 | BLOCKING #46: `init` from inside the store worktree builds a phantom instance | **RESOLVED** (one caveat, N2) | v3.md:145 (A.1 refusal on `symbolic-ref HEAD` = `refs/heads/factory-store`, `FACTORY_INSTANCE` unset); v3.md:89 (Decision, with the reason the `--git-common-dir` option was rejected — correct: nanobot's main worktree is `~/dev/nanobot`); scenario v3.md:282-285 (`exit=2 phantom=none store=unchanged`, then `found=ready-for-triage`); Risk v3.md:105 replaces the false "does not alter how a role's shell finds the store" claim. Probe confirms: toplevel from `<store>/runs/r1/scratch` is the store root and `symbolic-ref -q HEAD` prints `refs/heads/factory-store` on the unborn branch. |
| 2 | SHOULD-FIX #45: cwd-under-`runs/`/`worktrees/` trigger, marker-independent | **RESOLVED** | v4.md:125 (design A.3 Location rule, first in order, holds whatever `FACTORY_DISPATCH` says); Decision v4.md:68-69; requirement v4.md:243-254 (two NEW scenarios: marked `decision add`/`init` from scratch and marked `ticket new` from under `worktrees/` → all 2; finished-run scratch with idle store → 2); marked write from repo root still passes v4.md:264-267; "not a security boundary" kept v4.md:22, :76, :104. Evidence v4.md:33 reproduces the incident route with marker exported and store idle → refused by location rule alone. |
| 3 | SHOULD-FIX #46: two remotes → silent orphan | **RESOLVED** | v3.md:149 (A.3.2 refuse, name each `<remote>/factory-store`); Decision v3.md:88; requirement + scenario v3.md:230-277 (`exit=2 store=none local_branch=0 names=1,1`); Evidence v3.md:52 shows git itself refuses the ambiguous `worktree add`. |
| 4 | SHOULD-FIX #46: stale T-0001.1 fact | **RESOLVED** | v3.md:115 names no worktree, states both conditions held on 2026-10-04 and makes the two checks the paired ticket's first step. |
| 5 | NOTE #46: step 4 can't see ignored files | **RESOLVED** | v3.md:173-174 (per-file byte compare + count + `status`; on mismatch remove worktree and branch, exit 1, old store untouched); Decision v3.md:93; test v3.md:184. |
| 6 | NOTE #46: `-ffdx` deletes the store | **RESOLVED** | Evidence v3.md:48 (verified), Risk v3.md:106, README D v3.md:202, scenario `ffdx=1` v3.md:361-362. |
| 7 | NOTE #46: worktree step before agent copy | **RESOLVED** | v3.md:143-152 (A in code order, "already used by worktree" raised before any write); Decision v3.md:90; test v3.md:183. |
| 8 | NOTE #46: pre-move checkout brings back stale store | **RESOLVED** | Risk v3.md:107, README v3.md:203 ("from before the move"), scenario `premove=1` v3.md:362. |
| 9 | NOTE #45: README marker paragraph load-bearing | **RESOLVED** | v4.md:146-151 (first paragraph, bold opener, exact command form, "deliberately does not name the marker", never export, write from repo root, KILLED clearing command); scenario v4.md:314-316. |
| 10 | NOTE #45: name suite-guard follow-up | **RESOLVED** | v4.md:115. |
| 11 | NOTE nanobot: `.factory/store/**` not protected | **RESOLVED** | v3.md:118 (paired-ticket bullet). |
| Q6 | #45: README:102 verifier in-flight line | **RESOLVED** | v4.md:45, :153, scenario v4.md:318-320. |
| Q5 | Build order / rebase, two call sites | **RESOLVED** | v4.md:131 ("keep it to these two call sites"), v4.md:99-103; v3.md:126, :146, :158, :104. |

---

**New findings**

**N1. SHOULD-FIX, #46 (v3.md:213 "Tests to change: none"; conflicts with v4.md:269-272).** #45's REGRESSION scenario "A throwaway store is not fenced, even from a run's scratch directory" runs `cd $W && FACTORY_STATE=$T/s $B init` and expects `init=0`. Under #46's layout `$W` lies inside the `factory-store` worktree, so `init_cmd`'s `_git_toplevel` (`cli.py:853`) returns the store root and `inst = <store>/.factory`, which has no `instance.yaml`; `init` without `--repo-name` is then refused at `cli.py:857` ("pass --repo-name"), and #46's own A.1 refuses it too. The scenario will print `init=2 new=0` once #46 lands. The two specs disagree on a line that will be in current truth, and #46 claims nothing changes. Fix either way: (a) #46 adds a MODIFIED requirement to `specs/live-store-guard/spec.md` restating that scenario with the throwaway `init` run from the repository root (or expecting `init=2` and saying why), or (b) cheaper, #45 changes that one WHEN before build: `(cd $T/tgt && FACTORY_STATE=$T/s $B init)` for the `init` half, keeping `ticket new` from `$W`. The spec's point (throwaway stores are not fenced) survives either. I recommend (b) since #45 builds first; if the operator prefers not to reopen #45, (a) belongs in #46.

**N2. NOTE, #46 (v3.md:145).** A.1 keys on `symbolic-ref -q HEAD`. With the store worktree on a detached HEAD (probed: `git -C .factory/store checkout --detach` → `symbolic-ref` rc=1), the refusal does not fire and the phantom route reopens. Low likelihood (operator inspecting store history by checkout), but a branch-agnostic second condition closes it for ~3 lines: also refuse when `instance.find()` from `caller_cwd()` returns an instance whose `own_state_root` equals, or contains, `top`. That names the live store directly, whatever branch it has out.

**N3. NOTE, #46 (v3.md:146) / #45 (v4.md:123).** #46's clone-restore and two-remote scenarios run `init` on an existing instance whose own store directory does not exist yet; #45's fence then runs with `root` absent. #45's "union of `in_flight` over `tickets/*.yaml`" must treat a missing `tickets/` as empty rather than raise. `Path.glob` on a missing dir already does, but say so in #45's A.2 or #46's A.2, since no #45 scenario exercises a missing own store.

**N4. NOTE, #46 (v3.md:146).** "For an existing instance, #45's fence runs here" reads as a conditional. #45 places one unconditional call after `root` (v4.md:131); keep it unconditional (it is a no-op on a new instance) so #46's rebase does not reintroduce a branch #45's tests never saw.

**N5. NOTE, #46 (v3.md:291-292).** `names_path=$(grep -c '\.factory/state' $T/err)` counts lines, so A.3.1's refusal must put the path on exactly one line; A.3.1's prose (v3.md:148) asks the message to say three things, which an implementer might wrap. Say "one line" there or loosen the check to `grep -q`.

**N6. NOTE, #46, no action.** Checked the embedded-repo hazard: `git -C <store> add -A` with a checker checkout nested at `runs/<id>/wt` adds it as a gitlink unless ignored; `store.STORE_GITIGNORE` (`store.py:49`) ignores `worktrees/` and `runs/*/wt/`, and the migrated tree carries that `.gitignore`. Fine as specified.

**Cross-spec agreement (init_cmd, main(), fence order).** Agreed, with N1 the only disagreement. `init_cmd`: #46 A.1 → A.2 (config in memory, `root`, #45 fence) → A.3 (store refusals, worktree add) → A.4 writes; #45's "fence right after `root`" is preserved and moved ahead of the new-instance `instance.yaml` write, which is strictly earlier than #45's own placement (`cli.py:865` writes `instance.yaml` before `:870`). `main()`: #45 fences before `instance.guard`; #46 only adds the `store` subparser, and `store migrate` is fenced by #45's default (v3.md:158, v4.md:73) with its own in-flight refusal for a marked call (v3.md:164). Fence internal order location → marker → in-flight (v4.md:69, :125-127) is untouched by #46. Both scenario sets reuse each other's conventions (`FACTORY_DISPATCH=1` on in-flight writes in #46's tests, v3.md:187).

---

**Verdicts**

- **T-0024 / #45: CLEAR.** No BLOCKING or SHOULD-FIX open against it on its own base. One-line scenario tweak (N1 option b) recommended before build; N3 is a sentence.
- **T-0025 / #46: NOT CLEAR** — N1 (SHOULD-FIX) open. Clears with either a MODIFIED live-store-guard requirement in #46 or the #45 tweak landing first; N2-N5 are NOTEs for the writer/implementer.

**Build order:** T-0024 (#45) first, then T-0025 (#46) rebased on it, with N1 settled (preferably in #45's scenario before it builds) and N2/N3/N4/N5 folded into #46 before planning.