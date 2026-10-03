Commit: 2d86d96440218508f3f7ba8bf66d5987458d71a7 (branch `factory/T-0012.6`; merge of `3d5afc0` and `main` `600b8d4`; merge-base with `main` is now `600b8d4` itself, `git merge-base --is-ancestor main HEAD` → true)

## Review

Round 2 (fix round + conflict run). Checked in the worktree `intake/state/runs/run-0101-reviewer/wt`, bash, with `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD`, `FACTORY_INTEGRATION_BRANCH` and `VIRTUAL_ENV` unset, after `uv sync --frozen` (`uvsync=0`; it writes only the gitignored `.venv/`). `git status --porcelain` was empty before and after everything below.

**Changed lines since the approved head `302f70b`.**
- `git diff --name-only 302f70b 3d5afc0` → exactly `.factory/README.md`, `.factory/context.md`, `README.md`. I read the full diff: three prose edits, no key, path or command changed.
  - `README.md:59-65` ("How updates work"): now says an unaccepted revision is refused until `--accept-harness <sha>` (logged), and separately that a runtime with uncommitted harness edits is refused and `--accept-harness` does not clear that. Checked against the code, not the PR text: `factory/instance.py:130-154` (`guard`) refuses `harness_changes()` first (line 137-139), before it looks at `accept` at all (line 145). The new sentence is correct.
  - `.factory/README.md:68-72`: one sentence added, "Uncommitted harness edits cannot be accepted: commit or discard them first." Same code path; correct.
  - `.factory/context.md:43-47`: the Output paragraph now reads, word for word, as the last paragraph of `factory/context.template.md` (I printed the template and compared): every role but the implementer may change only its output file; the implementer also commits in its own worktree and nowhere else. E.2's kept rules (acceptance commands at lines 35-38, design-doc conventions at 36-38) are unchanged.
- `git diff --name-only 3d5afc0 2d86d96 | grep -v '^intake/state/'` prints nothing (101 files, all under `intake/state/`, all from `main`). The merge commit is a clean mechanical merge: `git merge-tree --write-tree 3d5afc0 600b8d4` gives tree `593e8ce8e24b9c808eee736f176212fd00c0146a`, which equals `HEAD^{tree}`. Nothing was hand-edited in the merge.

**1. Test integrity.** `git diff --name-only main...HEAD -- tests factory bin/factory agents pyproject.toml uv.lock` → `0`. `git diff --name-status -M main...HEAD | grep -v '^R100'` lists the same ten entries as round 1 (`A` ×3 under `.factory/`, `R062 intake/instance/config.yaml → .factory/instance.yaml`, `M README.md`, five `D` under `intake/`). No test file touched, no harness code touched.

**2–5. Correctness, scope, silent behaviour, security** on the changed lines: prose only, all three statements verified against `factory/instance.py` as above; no new path, key or command; no scope change beyond E.2/E.4/E.6 files. Round 1's checks on the unchanged files (yaml key diff, lock SHA, rename counts, lock-enforcement probe) stand; the lock SHA `010d1b00c5835c7022a72771c63f63f8b6ab3707` is still the harness revision at HEAD (lock-is-base-revision below).

**Gates, run as written from the worktree:**
- `git diff --check main...HEAD` → exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 97.19s (0:01:37)`, exit 0.

**Acceptance, re-run by me on `2d86d96`.** Every WHEN was extracted from the input by a script matching `- WHEN \`` lines (nothing retyped); `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f` for the parent scenarios.

| Check | Result |
|---|---|
| intake-holds-only-live-store | `left=0` |
| pilot-store-and-answers-kept-byte-identical | `kept=135 of 135` (equal; the 135th blob is `T-0012-gate-edit.md` from the parent base, as both checkers traced in round 1) |
| instance-b-opens-every-ticket | `tickets=18 failed=0` |
| instance-b-config | `True True True` / `context=3` |
| readme-has-install-and-layout | `checked` only |
| no-old-paths-in-live-files (REGRESSION) | `exit=1` |
| lock-is-base-revision | `lock=current` / `harness_paths_changed=0` |
| instance-b-keys | `False [] intake/state True` / `True True` |
| records-moved-as-pure-renames | `0` / `pilot=148 of 148 answers=14 of 14` |
| live-store-untouched | `0` (the merge brings `main`'s store commits in, but `main...HEAD` shows the branch adds nothing there) |
| role-prompt-text-unchanged | `changed=0 of 14` |
| harness-files-in-repo | `agents=6 green_only=0` |
| harness-history-carried | `0` |
| docs-moved-and-split | `old_tracked=0` |
| changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` |
| design-text-kept | `0` |
| prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` |
| harness-suite-passes-after-uv-sync | covered by the gate run above (`116 passed`) |
| green-harness-still-present | `green keeps its harness` |
| whitespace (sub-ticket diff) | `exit=0`; with `-c diff.renames=false` the flagged lines are "new blank line at EOF" in the moved `.factory/green-pilot/` records, paired away by rename detection as the ticket predicts |

**6. Protected paths.** `intake/**` (infra) touched exactly as the sub-ticket declares; unchanged from round 1. Listed under ESCALATIONS.

**On the implementer's DISAGREE ("Gate suite FAIL" that triggered this round).** Accepted on the evidence: `factory/cli.py:453-454` (and the running copy `intake/harness/factory/cli.py:450-451`) match `^Gate suite:\s*(PASS|FAIL)` and fall back to `("FAIL", "missing Gate suite line")`; the round-1 verifier wrote the line as a heading, `## Gate suite: PASS`, so the parser missed it. The gate itself passed for the verifier, for me in round 1, and again here. Nothing in this branch should change for that.

## Findings

none

## Prior findings

- [NIT] `.factory/context.md:43-45` Output paragraph contradicts the implementer role → RESOLVED in `3d5afc0`: the paragraph now carries `factory/context.template.md`'s wording, which exempts the implementer's worktree commits.
- Verifier ESCALATION 1 (`README.md` implied `--accept-harness` clears the uncommitted-edit refusal) → RESOLVED in `3d5afc0`; wording now matches `factory/instance.py:132-139`.
- Verifier ESCALATION 2 (head did not contain `main` `600b8d4`) → RESOLVED by the conflict-run merge `2d86d96`; clean re-merge, tree verified.
- Verifier ESCALATION 3 (135 vs the THEN's 134) → WITHDRAWN as a defect (count drift from the parent-base gate edit; the equality condition holds).

## Out-of-scope observations

- The verifier's `## Gate suite: PASS` heading does not match the harness regex `^Gate suite:` (`factory/cli.py:453`), so an approved and verified head came back as a fix round. A verifier-prompt or parser hardening belongs to a harness ticket, not this branch.
- `dev/issues.md:26` still says #19 is "not in intake yet" (operator step 4).
- The parent-level `whitespace-clean` (`git diff --check "$BASE" HEAD`, BASE=`cdb1c67`) is not this sub-ticket's gate and I did not re-run it; it remains a parent-close concern, as noted in round 1.

STATUS: APPROVE
CONFIDENCE: high. The three changed files are prose edits that I checked against the lock code in `factory/instance.py`; the merge commit's tree equals a fresh `git merge-tree` of its parents; both gates and all 20 acceptance items were re-run as written on `2d86d96` and gave the THEN output.
ESCALATIONS: protected path `intake/**` (infra) touched, as declared in the sub-ticket (removals of `intake/README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*`; pure renames of `intake/answers/` and `intake/green-pilot/` to `.factory/`; `intake/state/**` and `intake/.gitignore` unchanged by the branch). The merge gate needs the human approval the declaration implies. No `generated`, `reference_harness` or `credentials` path was written; `~/dev/nanobot-upstream` was read only through the read-only `git -C` commands the parent scenarios prescribe.
