Commit: 3d5afc012b5a22fed48de58e7af9c8206c7c9fff (branch `factory/T-0012.6`, one fix commit on the approved `302f70b`; merge-base with `main` still `f4be7ec`)

## Review

Round 2. Checked in the worktree `intake/state/runs/run-0098-reviewer/wt`, with `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD` and `VIRTUAL_ENV` unset, after `uv sync --frozen` (`uvsync=0`). `git status --porcelain` is empty before and after everything below. Per the convergence rule I checked the prior findings and the changed lines; I did not re-read the 162 pure renames or the unchanged E.1/E.3 files beyond the acceptance commands that cover them.

**Changed lines.** `git diff --name-status 302f70b HEAD` is exactly `M .factory/README.md`, `M .factory/context.md`, `M README.md`; `git show --stat 3d5afc0` says 10 insertions, 6 deletions. The full diff is three paragraph edits:

- `README.md:60-65` ("How updates work"): the old sentence made `--accept-harness` the cure for both the unaccepted revision and the uncommitted-edit refusal. The new text separates them: unaccepted revision → refused until `--accept-harness <sha>`, logged; uncommitted harness edits → refused, `--accept-harness` does not clear it, commit or discard first. I probed the behaviour in a scratch clone of this head rather than trusting the description: `init` a throwaway target, append a line to `<clone>/factory/__init__.py`, then `bin/factory --accept-harness <current rev> ticket new …` → `accept_dirty_exit=2 tickets=0 names=1 uncommitted=1` (exit 2, nothing written, stderr names `factory/__init__.py` and says uncommitted). The new README text is what the code does; the old text was wrong, as the verifier's probe 7 found. This is E.6's "refuses uncommitted harness edits, until `--accept-harness`" read the way parent C.4 defines it, not a scope expansion.
- `.factory/README.md:71-72` (E.4 "Running"): one added sentence, "Uncommitted harness edits cannot be accepted: commit or discard them first." Same correction, same probe.
- `.factory/context.md:43-47` (E.2 Output paragraph): the round-1 NIT. The new four lines are textually identical to `factory/context.template.md:17-21` (read both). The acceptance-commands paragraph (`:35-38`) and the design-doc-conventions sentence (`:36-38`) that E.2 says to keep are untouched in this commit.

**1. Test integrity.** No test, harness, or agent path changed in this round or on the branch: `harness_paths_changed=0` over `factory bin/factory agents pyproject.toml uv.lock tests/factory`. Tests to change: none; none changed.

**2. Correctness.** All three edits are documentation that now states what the code does. Acceptance items whose inputs the edits touch, re-run as written on `3d5afc0`:

| Check | Result |
|---|---|
| readme-has-install-and-layout | `checked` only |
| instance-b-config | `True True True` / `context=3` |
| no-old-paths-in-live-files (REGRESSION, full pathspec) | `exit=1` |
| bare `prompts/` (`[^/a-z_]prompts/|^prompts/`) over `README.md`, `.factory/README.md`, `.factory/context.md`, `.factory/instance.yaml` | rc=1 (no match) |
| old-path patterns over `.factory/README.md` (outside the pathspec) | rc=1 |
| whitespace gate `git diff --check main...HEAD` | `exit=0` |

Items the edits cannot affect, re-run anyway because they are cheap and are this PR's core claims: intake-holds-only-live-store `left=0`; records-moved-as-pure-renames `0` / `pilot=148 of 148 answers=14 of 14`; live-store-untouched `0`; lock-is-base-revision `lock=current` / `harness_paths_changed=0`; instance-b-keys `False [] intake/state True` / `True True`; instance-b-opens-every-ticket `tickets=18 failed=0` with the store unchanged afterwards; pilot-store-and-answers-kept-byte-identical with `BASE=cdb1c67` `kept=135 of 135`.

Gate commands, from the worktree exactly as written: `git diff --check main...HEAD` → exit 0; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 134.21s (0:02:14)`, exit 0.

**3. Scope.** The three files are E.6, E.4 and E.2 respectively. Nothing else moved.

**4. Silent behavior changes.** None; prose only. No runtime path changes between `302f70b` and `3d5afc0`.

**5. Security.** No secrets, no new paths.

**6. Protected paths.** Unchanged from round 1: `intake/**` (infra) touched exactly as the sub-ticket declares, nothing else. This round's commit touches no protected path (`.factory/**` is listed as infra in the new `instance.yaml`, and E.1–E.4 declare it as the files this ticket creates).

**Base drift (verifier ESCALATION 2).** `main` is `600b8d4`, merge-base `f4be7ec`; `git diff --name-only f4be7ec main | grep -v '^intake/state/'` prints nothing. The one extra commit is store bookkeeping; the merge will be clean and the lock stays current. I agree with the implementer that merging `main` is the conflict run's job, not a fix round's.

**The "Gate suite FAIL" that triggered this round.** The implementer DISAGREEs that the gate failed. Checked on the evidence: `factory/cli.py:453-454` (and the running copy `intake/harness/factory/cli.py:450-451`) is `re.search(r"^Gate suite:\s*(PASS|FAIL)\b(.*)$", text, re.M)` with fallback `("FAIL", "missing Gate suite line")`; the verifier's `run-0094-verifier/output.md:36` is `## Gate suite: PASS`, which that regex cannot match. Both gates passed for the verifier (`116 passed in 101.19s`), for me in round 1 (`116 passed in 90.16s`), and for me now. I accept the DISAGREE: the FAIL was a parse miss, not a gate failure, and this branch is not the place to fix it.

## Findings

none.

## Prior findings

- [NIT] `.factory/context.md:43-45` Output paragraph contradicts the implementer role → RESOLVED at `3d5afc0`: replaced with `factory/context.template.md:17-21` verbatim, which exempts the implementer's own worktree.
- Verifier ESCALATION 1 (`README.md` implied `--accept-harness` clears the uncommitted-edit refusal) → RESOLVED at `3d5afc0`: `README.md:60-65` and `.factory/README.md:71-72` now say it does not; probe confirms exit 2 with the flag present.
- Verifier ESCALATION 2 (head lacks `main` `600b8d4`) → UNRESOLVED by design; not a defect in this PR. The gap is `intake/state/**` only; the merge step's conflict run handles it.
- Verifier ESCALATION 3 (count 135 vs THEN's 134) → WITHDRAWN as a finding: count drift from `intake/answers/T-0012-gate-edit.md` at the parent base; the THEN's stated condition, both numbers equal, holds (`kept=135 of 135`).

## Out-of-scope observations

- The verifier wrote its gate line as a heading (`## Gate suite: PASS`) and the harness's `^Gate suite:` regex missed it, so an approved and verified head came back as a fix round. Either the verifier prompt should say the line is a bare line, or the parser should tolerate a leading `#`. Harness/prompt territory, flagged under ESCALATIONS for the operator.
- `dev/issues.md:26` still says #19 is "not in intake yet" (operator step 4).
- The parent-level `whitespace-clean` with `BASE=cdb1c67` is not this sub-ticket's gate and I did not re-run it; round 1 noted it trips on store run records already on `main`. Parent-close concern.

STATUS: APPROVE
CONFIDENCE: high. The round-2 diff is 10 lines of prose in three files; I read all of it, probed the behaviour the new text describes (exit 2 with `--accept-harness` on a dirty harness), re-ran every acceptance item the edits could touch plus the core E.5/E.3 checks, and ran both gate commands on `3d5afc0` as written.
ESCALATIONS: protected path `intake/**` (infra) touched as the sub-ticket declares, unchanged from round 1 (removals of `intake/README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*`; pure renames of `intake/answers/` and `intake/green-pilot/` to `.factory/`; `intake/state/**` and `intake/.gitignore` unchanged). Merge gate needs the human approval the declaration implies. Also for the operator: the harness turned a verified head into a fix round because the verifier's `Gate suite:` line was a markdown heading and the parser regex (`factory/cli.py:453`) requires it at column 0; no action in this PR.
