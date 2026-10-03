Commit: e28db6a255e8cd0032c67ada62b74b6681cd511d

**What this means.** The change does what the ticket asks. All nine acceptance scenarios give the required result on the head and the expected "before" result on the base, under both bash and zsh. `tests/factory` passes 64/64. Lint is clean. Probes with a non-zero head show the check is not tied to the test inputs. The verdict is still FAILED, because the role's rule says any non-zero gate command is FAILED and the full-suite gate exited 1. The 9 failures outside the baseline come from the environment: `neonize` is missing from the lockfile-synced `.venv`. The same 9 tests fail the same way on the base. None of them can reach the diff, which touches only `factory/cli.py` and `tests/factory/`. If the operator accepts the environment explanation, nothing in this PR needs to change. Instead, the gate environment (or the baseline) needs a decision. See ESCALATIONS.

Environment: worktree `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0008-verifier/wt`, detached at `e28db6a25`, clean at start. It had no `.venv` and no `uv.lock`, because `uv.lock` is gitignored in this repo (`.gitignore:61`). I copied green's untracked `/Users/dphang/dev/nanobot-upstream/uv.lock` into the worktree and ran `uv sync --frozen --all-extras`. Note: green's lock differs from the implementer's worktree lock (`cmp`: first difference at line 191). I installed nothing outside the lock. Base: `git archive f8f40e0c550c86d34a5b80ef273c7b4943abf412` extracted to a scratch dir (`.../scratchpad/v8base`) with the same `.venv` symlinked in.

## Per criterion
I saved the nine WHEN commands to files and checked each one with `grep -F` against input.md (all 9 matched exactly). I ran them from the repo root under both bash and zsh. Both shells gave identical output on both trees.

| Kind | Scenario (command = the spec's WHEN, verbatim) | Base f8f40e0c5 | PR e28db6a25 | Result |
|---|---|---|---|---|
| NEW | no-commit-line-is-refused | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS |
| NEW | non-hex-commit-value-is-refused | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS |
| NEW | later-commit-line-naming-another-commit-is-refused | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS |
| NEW | verifier-without-commit-line-writes-no-ci-row | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=2 rows=[] events=0` | PASS |
| REGRESSION | earlier-commit-line-naming-another-commit-is-refused | `exit=2 rows=[] events=0` | `exit=2 rows=[] events=0` | PASS |
| REGRESSION | full-head-sha-is-recorded | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=0 rows=[reviewer.yaml ] events=1` | PASS |
| REGRESSION | abbreviated-sha-in-backticks-is-recorded | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | PASS |
| REGRESSION | killed-without-output-records-killed | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS |
| REGRESSION | killed-with-cut-off-output-records-killed | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS |
| REGRESSION | factory-suite-still-passes: `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` | `55 passed in 63.12s`, exit 0 (base run with `.venv/bin/python -m pytest`, same flags, because the archived base has no lock for `uv run`) | `64 passed in 68.69s`, exit 0 | PASS |
| REGRESSION | Intermediate check: lint + full-suite gate | — | lint clean; gate exit 1 (below) | FAIL (environmental) |

Every NEW criterion fails on base for the reason the spec states (the verdict is recorded), so there is no SPEC-DEFECT.

Additional checks:
- New test file against base code: I copied `tests/factory/test_results_commit.py` into the base tree. Result: `4 failed, 5 passed`. The 4 failures are exactly the 4 NEW scenarios, so the new tests can fail for the thing they claim to pin.
- Part A without part B: I put head's `factory/cli.py` into the base tree, which has the unchanged `test_shepherd.py`. The merge-gate story fails with `results record: Commit: HEAD is not a commit id` (returncode 2). So the one-line fixture change in B is needed and does not hide a defect. `test_shepherd.py:648` confirms the dispatcher writes `output.md` with `Commit: HEAD` replaced by the real head.
- Diff scope (`git diff --stat base head`): `factory/cli.py` (+13/-3 net 17 lines touched), `tests/factory/test_results_commit.py` (new, 131 lines), `tests/factory/test_shepherd.py` (1 line changed). No other existing test, stub or protected path was touched.

## Gate suite: FAIL
- `uv run ruff check nanobot/` → `All checks passed!`, exit 0.
- `uv run scripts/full_suite_gate.py --isolated-home --pytest-args "-n 2 --dist loadfile"` → exit 1:
  ```
  [full-suite-gate] summary: 14 failed, 7158 passed, 25 skipped in 131.36s (0:02:11)
  [full-suite-gate] tests run: 7197
  [full-suite-gate] FAIL: 9 failure(s) NOT in the baseline (full_suite_baseline.txt):
      NEW  tests/lionbot/test_auto_mention.py::TestTheLibraryOwnsTheMentionArray::test_an_over_long_id_is_truncated_into_a_mention_of_someone_else
      NEW  tests/lionbot/test_auto_mention.py::TestTheLibraryOwnsTheMentionArray::test_neonize_still_parses_mentions_out_of_message_text
      NEW  tests/lionbot/test_auto_mention.py::TestTheLibraryOwnsTheMentionArray::test_send_message_still_accepts_the_lid_flag
      NEW  tests/lionbot/test_typing_hooks.py::TestPresenceTransportIsBestEffort::test_a_connected_channel_does_send
      NEW  tests/lionbot/test_upstream_seams.py::TestChannelDependencyInstallSeam::test_message_info_display_name_field_is_pushname_lowercase_n
      NEW  tests/lionbot/test_upstream_seams.py::TestPresenceSeam::test_async_client_still_exposes_send_chat_presence
      NEW  tests/lionbot/test_upstream_seams.py::TestPresenceSeam::test_presence_enum_members_are_the_ones_we_name
      NEW  tests/lionbot/test_upstream_seams.py::TestSpec04AdmissionDocks::test_context_info_is_still_where_mentions_live
      NEW  tests/lionbot/test_upstream_seams.py::TestSpec04AdmissionDocks::test_message_source_still_carries_sender_alt
  ```
- Cause: I re-ran the 3 files directly on head. 8 tests fail with `ModuleNotFoundError: No module named 'neonize'`. The 9th (`test_a_connected_channel_does_send`) fails with `AssertionError: a connected channel sent no presence`, which is the same missing transport. `.venv/bin/python -c "import neonize"` → `ModuleNotFoundError`. `pyproject.toml` does not mention `neonize`.
- Same on base: the same 3 files on the base tree give `9 failed, 56 passed, 1 skipped`, the same 9 node ids. None of the 3 files references `factory` (grep). The diff cannot cause these failures.
- The implementer's 10th failure (`test_mcp_reconnect_crash`, TimeoutError) did not occur here.
- I did not install `neonize` to make the gate pass. That would mean tuning the environment to the check, and the rule makes a non-zero gate FAILED. I report it as-is.

## Probes
I used head `abcdef1234567890abcdef1234567890abcdef12` (not zeros) with a reviewer role unless noted. Each line shows the input, then exit/rows/events and stderr, then my judgement.
- `Commit: ABCDEF1` (uppercase 7-hex prefix) → exit 0, reviewer.yaml, 1 event → OK. Matching ignores case and accepts a prefix.
- `Commit: <head> (feat/x)` (trailing text) → exit 0 → OK (spec: trailing text allowed).
- `Commit: abcdef` (6 hex) → exit 2, nothing written, `Commit: abcdef is not a commit id` → OK.
- `Commit: <head>0` (41 hex) → exit 2, `... is not a commit id` → OK.
- `Commit: bcdef12` (7 hex, not a prefix) → exit 2, `the output says Commit: bcdef12, not the head abcdef123456` → OK.
- empty output file → exit 2, `the output has no Commit: line` → OK.
- only `commit: <head>` (lowercase) → exit 2, no Commit: line → OK (spec: case-sensitive).
- `**Commit:** <head>` → exit 2, no Commit: line → OK per spec. This is the parking risk the parent declared; it is out of scope.
- `Commit: abcdef1234xyz` → exit 2, `not a commit id` → OK.
- `Commit:` with the hex on the next line → exit 2, `Commit:  is not a commit id` (empty value) → OK per spec. The implementer disclosed this.
- `Commit: <head>` then `Commit: abcdef1` (both name the head) → exit 0 → OK.
- CRLF line endings, and a tab after `Commit:` → exit 0 → OK.
- `Commit: <head>` then an indented `  Commit: deadbeef00` → exit 0, recorded → CONCERN (minor). The indented line does not start with `Commit:`, so the spec's grammar ignores it. This is within the spec, not a failure.
- `` Commit: `<head> `` (unbalanced backtick) → exit 0 → OK. This is today's optional-backtick grammar.
- `--killed` + `Commit: deadbeef00` → exit 2, nothing written → OK (today's killed check kept).
- `--killed` + `Commit: HEAD` → exit 0, KILLED row → OK (spec: killed behaviour unchanged).
- verifier, `Commit: <head>`, no `Gate suite:` line → exit 0, `ci.yaml verifier.yaml` → OK. Derived ci row behaviour is unchanged (out of scope).

Nothing shows the fix is tied to the test inputs.

## Out-of-scope observations
- I confirmed the implementer's report that the gate rewrites a protected path. After my gate run, `git status` showed ` M webui/package-lock.json` (43 deletions, including `"node_modules/@radix-ui/react-separator"`), and a new `webui/node_modules/` (gitignored, mtime 19:00, during the gate run). I restored the file with `git checkout -- webui/package-lock.json`. The worktree is clean except for ignored `.venv`, `uv.lock` and `webui/node_modules/`.
- Because `uv.lock` is gitignored, every new worktree has to borrow one, and the implementer's lock already differs from green's. Gate results depend on which lock each role happens to copy.

STATUS: FAILED
CONFIDENCE: high. I ran all nine acceptance commands verbatim on base and head in two shells, plus the factory suite, lint and the gate. The one failure is the gate's exit 1, which I traced to `neonize` missing from the environment and reproduced identically on base.
ESCALATIONS:
- Gate FAIL is environmental, not caused by this PR. A lock-synced `.venv` lacks `neonize`, which is not declared in `pyproject.toml`. The same 9 tests fail at base `f8f40e0c5`. An operator decision is needed: declare `neonize` as a dependency (protected path `pyproject.toml`), add the 9 ids to the gate baseline, or run checkers in green's `.venv`. Once that is settled, re-verification should only need the gate re-run, since every acceptance criterion passed.
- The full-suite gate modifies protected `webui/package-lock.json` during its run (confirmed independently; restored, not committed). Any role that commits with `-a` after the gate would commit a protected-path change.
- `uv.lock` is gitignored (`.gitignore:61`), so "synced from the lock" is not reproducible across worktrees. My copy of green's lock differs from the implementer's.
