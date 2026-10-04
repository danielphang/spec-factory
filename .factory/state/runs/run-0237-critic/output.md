## Critic review, T-0025 v4 (round 4)

Scope of this round: the second change request (`approvals/T-0025/changes-2.md`, N1 to N5), the text that changed between v3 and v4 (`diff` of `specs/T-0025/v3.md` and `v4.md`), and my own earlier findings. Unchanged text was not re-reviewed.

### What I checked

- Citations, all present at the lines given on `d2a5143`: `factory/cli.py:544-550` (gate refusal text and `head_contains`), `:576` (`MAX_CONFLICT_RUNS = 2`), `:592-595` (`ticket_join` conflict decision), `:821-824` (`_git_toplevel`), `:853` (`top = _git_toplevel(...)` in `init_cmd`), `:741`, `:247`, `:259`; `factory/gitops.py:79` (`head_contains`); `factory/instance.py:55-64` (`find`); `factory/instance.template.yaml:10`; `docs/design.md:39`, `:58`, `:74`; `dev/build-harness.spec.md:152`. Every symbol A.1 and A.2 name exists: `instance.own_state_root` (`instance.py:93`), `instance.repo_root` (`:81`), `instance.is_own_store` (`:105`), `gitops.integration_branch` (`gitops.py:22`), `gitops.checkout_of` (`:92`), `_new_instance_yaml` (`cli.py:828`), `_revision` (`:838`).
- `git diff --stat abaa75a d2a5143 -- . ':!.factory'` prints nothing, as Evidence says.
- Acceptance commands run as written under a throwaway HOME, with `TMPDIR` set to this run's scratch directory:
  - "init from the store checkout on a detached HEAD refuses" (NEW) printed `exit=0 detached=yes phantom=written store=changed`, then `found=`. Matches verification.md. A fix with only A.1's first condition still prints this, so the item discriminates.
  - "init in a separate repository under a run's scratch directory still creates its instance" (REGRESSION) printed `exit=0 instance=written live=ready-for-triage`. An unqualified "store contains the top level" rule would refuse it, since the walk-up from `scratch/other` finds the live instance, so it guards the qualifier the spec adds.
  - The design-doc, build-spec and README `old_refs` commands printed `store_branch=0 tickets_branch=2 never_tracked=0`, `old_name=16 new_name=0` and `old_refs=4` (README lines 403, 418, 457, 462). All match.
- N1's correction of the gate's premise is right. `.factory/state/specs/T-0024/v5.md` has five WHEN commands that run `init` (lines 234, 252, 275, 287, 302). Line 252 runs it from `$W`, which its fixture sets to `$S/runs/$R/scratch` (v5 line 187), inside the store. Three run from `$T/tgt`, one (234) from `tgt/sub/scratch`, a code-checkout subdirectory. v5's own Risk (lines 99-102) expects #46 to make that `init` resolve the live instance so the fence refuses it; A.1 refusing first with the same exit code and nothing written keeps the scenario's output `scratch_init=2 store=unchanged agents=none`. The spec says exactly this in Risk and Tests to change.
- N2: A.1.2 as written catches the detached case (`top == own`, where `own` is the live instance's `state_dir` resolved), and the same-common-dir qualifier is what keeps the separate-repository case working. Both conditions are branch-agnostic as the request asked, and Risk honestly names the one case neither sees (a phantom that already exists).
- N3, N4, N5: A.2 now refers to #45's part A.2 in one clause; the fence call is described as unconditional in A.2 and Risk; A.3.1 says one line and the scenario uses `grep -q`.

### Findings

No BLOCKING or SHOULD-FIX findings on the changed text.

[NIT] 6 proposal.md, Decisions, A.1 bullet
Problem: The bullet is one of the longest in the section and carries two "Rejected" clauses plus the attribution "(operator, round 2 change request N2)"; an operator new to the system can follow it, but it reads as two decisions (the refusal rule and the rejected repository-resolution approach) folded into one.
Evidence: Read as the gate operator; every term in it is glossed earlier (store, instance, worktree, repository), so it does not meet the blocking bar.
Suggested fix: Optional; split the "parent of `--git-common-dir`" rejection into its own bullet.

### Prior findings

- Round 3 [NIT] "init refuses a once-tracked store path": `names_path` could count a wrapped message twice → RESOLVED (A.3.1 says one line; the check is `grep -q`; N5).
- Round 3 [NIT] "store migrate refuses an uncommitted store and a run in flight": the in-flight half is answered by #45's fence on the real base, not by refusal 4 → UNRESOLVED, still a NIT. Text unchanged; C's suite test covers the marked path. Not blocking.
- Round 3 [NIT] `old_name=0` forces a rewrite of the closed amendment line at `dev/build-harness.spec.md:533` → UNRESOLVED, still a NIT. Text unchanged; the rewritten line still reads truthfully.
- Round 2 [NIT] `old_refs` alternative constrains the README how-to's phrasing → UNRESOLVED, still a NIT.
- Round 3 BLOCKING (phantom `init`) and all earlier BLOCKING / SHOULD-FIX items stay RESOLVED; v4 strengthens the phantom fix rather than reopening it.

### Out-of-scope observations

- The round counter in run metadata restarted at 1 after the gate's first change request (`run-0232-critic/meta.yaml` says `round: 1` for what the spec calls round 3). Harmless here, but a reader following "Round 4" through the store will not find a run numbered so.

STATUS: APPROVE
CONFIDENCE: high, every changed item was reproduced or read against the cited file, and the two new scenarios print today's output and discriminate between the qualified and unqualified fix
ESCALATIONS: none
