Commit: e28db6a255e8cd0032c67ada62b74b6681cd511d

Round 1 review of sub-ticket T-0001.1 (ST-1) on branch `factory/T-0001.1`. The head is one commit over `f8f40e0c5`, which is the merge-base with the input's base `b551d97cd` (the integration branch moved past the fork point; the three-dot diff is the three files below and nothing else).

Findings:
- [NIT] factory/cli.py:442: a bare `Commit:` with its value on the next line (or an empty value) is refused with `results record: Commit:  is not a commit id` (empty value, two spaces). → A human reading the parked-ticket reason (`harness-bug: results record <role>: <stderr>`) sees a message that names nothing; `the value is empty` would say what happened. Refusing this output is correct under the parent's Decision (a `Commit:` line's value must parse on that line), and the PR description discloses the change. Not blocking.

Prior findings: none (round 1).

Checks, in the role's order, with what I ran:

1. Test integrity. `git diff --name-status b551d97cd...e28db6a25`: `M factory/cli.py`, `A tests/factory/test_results_commit.py`, `M tests/factory/test_shepherd.py`. The `test_shepherd.py` hunk is `@@ -265,7 +265,7 @@`: one line, 268, and only the `--output` argument changes from `str(red)` to `str(f.store / "runs" / ver.run_id / "output.md")`; the assertions at 269-274 are untouched. That line is the one the parent lists under Tests to change. `test_shepherd.py:648` confirms the dispatcher writes `output.md` with `Commit: HEAD` replaced by the real head, so the story still records a red verifier and a red ci row for the head. Lines 327, 408-409, 489 and `tests/factory/fixtures/stubs/` are not in the diff. The new file's assertions are specific (exact row lists, exact event lists, exact statuses, the refusal reason on stderr); no skip, xfail or swallowed error. The new tests test the change: against a scratchpad copy of base `f8f40e0c5`'s `factory/` and `bin/` (not in the worktree), the new file gives `4 failed, 5 passed`, and the four failures are exactly the four NEW scenarios (`test_no_commit_line_is_refused`, `test_non_hex_commit_value_is_refused`, `test_later_commit_line_naming_another_commit_is_refused`, `test_verifier_without_commit_line_writes_no_ci_row`).

2. Correctness. `factory/cli.py:431-444` at head: with `--killed`, the old first-match check is kept verbatim (431-434); without it, every `^Commit:.*$` line is collected (436), none refuses (437-438), each must parse with the old grammar anchored to its line (440-442) and be a prefix of `--head` (443-444). Every refusal precedes `store.record_result` (446) and `store.log_event` (452), so nothing is written. I ran all nine WHEN scenarios against this head from the worktree root (`bin/factory` resolved to the worktree's `factory/` package; `factory.__file__` printed under `.../run-0013-reviewer/wt/factory/`), each on a fresh store: the five refusals print `exit=2 rows=[] events=0`; full-head prints `exit=0 rows=[reviewer.yaml ] events=1`; abbreviated-sha-in-backticks prints `exit=0 rows=[ci.yaml verifier.yaml ] events=2`; both killed scenarios print `exit=0 rows=[verifier.yaml ] status=KILLED`. Edge cases the spec implies, same method: trailing text after the value is still accepted; two lines both naming the head are accepted; a 41-hex value, a 6-hex value, `**Commit:** <head>` (the Risk's known parking case) and an indented `  Commit: <head>` are refused; `Commit: deadbeef00` under `--killed` is still refused (as today); CRLF output is accepted. `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 python3 -m pytest -q -p no:cacheprovider tests/factory` on the worktree: `64 passed in 81.29s`, no failures (55 + 9 new).

3. Scope. The three files are design parts A, B and C. No other command, role, prompt or `build.js` change.

4. Silent behavior changes. Two, both required by the parent's Requirement text and both disclosed or implied: (a) a `Commit:` whose value sits on the next line was accepted by the old cross-line `\s*` and is now refused (PR's Known gaps); (b) `results record` without `--killed` and without `--output` used to record `UNKNOWN` and is now refused with "no Commit: line" (an empty output has no such line). `build.js` always passes `--output`, so (b) is reachable only by hand.

5. Security and data safety. The checker output is untrusted text run through two bounded regexes (`{7,40}`, no nested quantifiers); no new file writes, no destructive ops; refusals write nothing.

6. Protected paths. None in the diff. `webui/package-lock.json`, `pyproject.toml`, `uv.lock` and `nanobot/api/**` are not touched; the worktree is clean at head (`git status --short` empty). The sub-ticket declares none; this matches.

7. Maintainability. The `--killed` branch repeats the grammar literal of the loop at 440. Two copies of a one-line regex, explained by the comments at 431 and 435; not worth a finding.

Out-of-scope observations (not caused by this diff; not fixed):
- `uv.lock` is gitignored in this repo (`.gitignore:61`, under "Lock files (project policy)") and untracked in the worktree. So the protected path "uv.lock" names a file the repository does not carry; the implementer's "neonize is missing from the lock" observation is about a local, untracked file. The integration branch's `b551d97cd` ("fix(factory/gate): --extra dev and --root .") and the gate command in this input (`--extra dev --with neonize==0.3.18.post0`) already address the environment failures the implementer reported, so the verifier should not see them on this head with the gate as given.
- The implementer reports the full-suite gate rewriting `webui/package-lock.json` during its run. The harness note already says so and says never to commit it; nothing of the kind is in this commit.
- The parent's own observations stand: `--killed --output <missing file>` raises `FileNotFoundError`, and the `results record` call on `wrong.md` at `test_shepherd.py:333` is dead.

STATUS: APPROVE
CONFIDENCE: high — I read the code at head, ran the factory suite (64 passed) and all nine acceptance scenarios on this worktree, confirmed the four NEW tests fail at base, and the only existing-test edit is the one declared line.
ESCALATIONS: none
