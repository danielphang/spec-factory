Sub-ticket: T-0012.6 (parent `intake/state/specs/T-0012/v3.md`), branch `factory/T-0012.6`, worktree `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.6`

Fix round 2. Head is now `3d5afc0`: one fix commit on top of `302f70b`. The branch's merge-base with `main` is still `f4be7ec`.

## Why this round ran
The reviewer approved `302f70b` (run-0095) and the verifier verified it (run-0094). The fix round was triggered by the line "Gate suite on your previous head: FAIL / missing Gate suite line". That FAIL comes from parsing, not from the gate. The harness reads the verifier's output with `re.search(r"^Gate suite:\s*(PASS|FAIL)\b(.*)$", text, re.M)` (`intake/harness/factory/cli.py:450-451`; `factory/cli.py:453-454` matches). The verifier wrote the line as a heading, `## Gate suite: PASS`, so the regex found no match. The verifier's own gate run passed: `git diff --check main...HEAD` exited 0, and the suite gave `116 passed in 101.19s`. The reviewer saw the same: `116 passed in 90.16s`. I re-ran both gates on the new head (below). I also fixed the two wording findings the checkers raised.

## What changed (this round, commit `3d5afc0`)
- **E.6, `README.md` "How updates work"**: the old text said targets refuse "uncommitted edits to the harness's code, until you run a command with `--accept-harness <sha>`". That is wrong: per parent C.4, `--accept-harness` does not lift that refusal (verifier probe 7). The new text says it in two parts:
  - an unaccepted revision is refused until `--accept-harness`, which is logged;
  - a runtime with uncommitted harness edits is refused, `--accept-harness` does not clear that, and the edits must be committed or discarded first.
- **E.4, `.factory/README.md`**: one sentence added to the same paragraph: "Uncommitted harness edits cannot be accepted: commit or discard them first." The old wording did not claim the opposite, but it was open to the same misreading.
- **E.2, `.factory/context.md` Output paragraph**: this was the reviewer's NIT. The old line "That is the only file you may create or modify" contradicted the implementer role. It is replaced with the existing wording of `factory/context.template.md`: for every role but the implementer, the output file is the only file it may change, and the implementer also changes files and commits in its own worktree, and nowhere else.
  - Scope check: E.2 says the briefing "keeps the existing rules on acceptance commands and design-doc conventions". Both of those paragraphs are unchanged. The Output paragraph is neither of them.
- No other file changed: `git diff --name-only 302f70b HEAD` gives exactly `.factory/README.md`, `.factory/context.md` and `README.md`.

Unchanged from round 1 (`302f70b`): E.1 `.factory/instance.yaml`, E.3 `.factory/harness.lock` (`010d1b00c5835c7022a72771c63f63f8b6ab3707`), the removals, and the pure renames `intake/answers` → `.factory/answers` and `intake/green-pilot` → `.factory/green-pilot`.

## Acceptance results
**How I ran them.** I extracted every command verbatim from the input with a script: the parent scenarios' `- WHEN` lines and the intermediate checks. Nothing was retyped.
- Shell: bash, from the worktree, after `uv sync --frozen` (`uvsync=0`).
- `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD` and `VIRTUAL_ENV` were unset.
- `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, the `parent_base` at `intake/state/tickets/T-0012.yaml:74`.
- The "Before" column is the verifier's run on base `600b8d4` (run-0094). I did not re-run the base this round.

| Label | Check | Before (base, run-0094) | After (head `3d5afc0`, this run) |
|---|---|---|---|
| NEW | intake-holds-only-live-store | `left=168` | `left=0` |
| NEW | pilot-store-and-answers-kept-byte-identical | `kept=0 of 135` | `kept=135 of 135` |
| NEW | instance-b-opens-every-ticket | `tickets=0 failed=0` | `tickets=18 failed=0` |
| NEW | instance-b-config | `no instance config` / `context=` | `True True True` / `context=3` |
| NEW | readme-has-install-and-layout | five `missing:` lines, then `checked` | `checked` |
| REGRESSION | no-old-paths-in-live-files | `exit=1` | `exit=1` |
| NEW | lock-is-base-revision | `lock=stale` / `harness_paths_changed=0` | `lock=current` / `harness_paths_changed=0` |
| NEW | instance-b-keys | `FileNotFoundError` | `False [] intake/state True` / `True True` |
| NEW | records-moved-as-pure-renames | `0` / `pilot=0 of 148 answers=0 of 14` | `0` / `pilot=148 of 148 answers=14 of 14` |
| REGRESSION | live-store-untouched | `0` | `0` |
| REGRESSION | role-prompt-text-unchanged | `changed=0 of 14` | `changed=0 of 14` |
| REGRESSION | harness-files-in-repo | `agents=6 green_only=0` | `agents=6 green_only=0` |
| REGRESSION | harness-history-carried | `0` | `0` |
| REGRESSION | docs-moved-and-split | `old_tracked=0` | `old_tracked=0` |
| REGRESSION | changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | same |
| REGRESSION | design-text-kept | `0` | `0` |
| REGRESSION | prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` | same |
| REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `116 passed` | `sync=0` / `116 passed in 80.49s (0:01:20)` |
| REGRESSION | green-harness-still-present | `green keeps its harness` | same |
| REGRESSION | whitespace (sub-ticket diff) | `exit=0` | `exit=0` |

**Gate commands**, each run from the worktree exactly as written:
- `git diff --check main...HEAD` → exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 83.16s (0:01:23)`, exit 0.
- `git status --porcelain` is empty afterwards.

**Extra check on the new text.** `git grep -nE '[^/a-z_]prompts/|^prompts/'` over `README.md` and `.factory/` (excluding the moved records) prints nothing, rc=1. So the edits add no bare `prompts/`.

## Tests added/changed
None this round. No existing test was touched. `harness_paths_changed=0`, which also covers `tests/factory`.

## Known gaps and uncertainties
- The "Gate suite FAIL" that triggered this round is a harness parsing artifact (explained above), not a defect in this branch. Nothing in this PR changes how that line is parsed, and changing it is out of scope.
- `kept=135 of 135`, not the THEN's literal `134 of 134`. Both checkers traced the 135th blob to `intake/answers/T-0012-gate-edit.md`, which was added at the parent base. The real condition, both numbers equal, holds.
- The head still does not contain `main` `600b8d4`. That commit touches only `intake/state/**`; this branch touches no path there, and `600b8d4` touches no harness path, so the lock stays current. I did not merge `main`: per my role, merging `main` belongs to a conflict run, not a fix round.
- The parent-level `whitespace-clean` (`git diff --check "$BASE" HEAD` with the parent base) was not re-run. It is not this sub-ticket's gate. As reported in round 1, store run records already committed to `main` would trip it. That is a parent-close concern.

## Out-of-scope observations
- The verifier's output format (`## Gate suite: PASS` as a heading) does not match the harness regex `^Gate suite:`. A verifier prompt or parser hardening would stop approved work from coming back as a fix round. That is harness or prompt territory and not touched here.
- `dev/issues.md:26` still says #19 is "not in intake yet" (operator step 4).

## Responses to findings
- Reviewer [NIT] `.factory/context.md:43-45`, the Output paragraph contradicts the implementer role → FIXED `3d5afc0`. It now uses `factory/context.template.md`'s wording, which exempts the implementer's worktree commits. E.2's kept rules (acceptance commands, design-doc conventions) are unchanged.
- Verifier ESCALATION 1, `README.md` implies `--accept-harness` clears the uncommitted-edit refusal → FIXED `3d5afc0`. `README.md` now states that it does not, and `.factory/README.md` gained the matching sentence.
- Verifier ESCALATION 2, head lacks `main` `600b8d4` → no change. A main merge belongs to a conflict run, not a fix round. The gap touches only `intake/state/**`, so the merge is clean and the lock stays current.
- Verifier ESCALATION 3, count 135 vs 134 → no change. This is count drift from the parent-base gate edit, and the THEN's equality condition holds.
- "Gate suite on your previous head: FAIL / missing Gate suite line" → DISAGREE that the gate failed. Evidence:
  - the parser regex at `intake/harness/factory/cli.py:450-451` requires a line starting `Gate suite:`;
  - the verifier wrote `## Gate suite: PASS`;
  - both gates passed for the verifier, for the reviewer, and again here on `3d5afc0` (`exit 0`; `116 passed in 83.16s`).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 20 acceptance commands were extracted verbatim and run on `3d5afc0`, both gates were run as written and exited 0, and the diff since the approved head is 3 doc files and 10 lines.
ESCALATIONS: protected path `intake/**` (infra) is touched as the sub-ticket declares, unchanged from round 1:
- `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed;
- `intake/answers/` and `intake/green-pilot/` are pure renames to `.factory/`;
- `intake/state/**` and `intake/.gitignore` are untouched.
The merge gate needs the human approval this declaration implies. Also flagged: the harness turned an approved and verified head into a fix round because of the verifier's heading format. That needs operator attention, not implementer action.
