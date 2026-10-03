Commit: e28db6a255e8cd0032c67ada62b74b6681cd511d

## What I reviewed and how

Worktree `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0011-reviewer/wt`, branch `factory/T-0001.1`, HEAD `e28db6a255e8cd0032c67ada62b74b6681cd511d`. The worktree had no `.venv`; I ran everything with the green checkout's venv first on PATH (`/Users/dphang/dev/nanobot-upstream/.venv/bin`), so `bin/factory` resolved to a Python with the deps. I created nothing in the worktree (`git status --short` is empty after the review; the ignored `uv.lock` there, mtime 21:15:23, predates my run and is gitignored at `.gitignore:61`).

**Topology.** The harness names base `b7d09a8db`, the PR description names base `f8f40e0c5`. Both are right in their own sense: `e28db6a25^ == f8f40e0c5`, and `b7d09a8db` is the current `feat/lionbot-v3` tip, 4 commits ahead of `f8f40e0c5` (`git merge-base b7d09a8 e28db6a` = `f8f40e0c5`; `b7d09a8` is not an ancestor of head). So a two-dot `git diff b7d09a8 e28db6a` shows 12 files including `factory/config.yaml`, `factory/workflows/build.js`, `scripts/full_suite_gate.py` and deleted tests in `test_shepherd.py` and `test_spec_store.py`; those are the integration branch's own commits being *absent* from this branch, not changes the PR makes. The PR's actual change is `git show --stat e28db6a25`: `factory/cli.py` (+14/-3), `tests/factory/test_results_commit.py` (+131, new), `tests/factory/test_shepherd.py` (+1/-1). That matches the three-dot diff in my input exactly. No protected path is touched by the commit.

**1. Test integrity.** `tests/factory/test_shepherd.py` changed in exactly one line, 268: `--output str(red)` → `--output str(f.store / "runs" / ver.run_id / "output.md")`. That is the one line the sub-ticket's "Tests to change" allows. The assertion on line 269 (`{"reviewer": "APPROVE", "verifier": "FAILED", "ci": "FAIL"}`) and the rest of the story are unchanged, and the dispatcher at `test_shepherd.py:648` writes the same `red.md` content into that `output.md` with `Commit: HEAD` replaced by the real head, so the behaviour under test (red verifier + red ci block the merge) is preserved. Lines 327, 408-409, 489 still carry `Commit: HEAD`; the 10 stub files under `tests/factory/fixtures/stubs/` still start with `Commit: HEAD`; none is in the commit. No assertion weakened, no skip, no swallowed error. PASS.

**2. Correctness against the spec.** `factory/cli.py:431-444` at head. Without `--killed`: `re.findall(r"^Commit:.*$", text, re.M)` collects the lines; none → `Refused("...has no Commit: line")`; each line is matched with the existing grammar anchored to the line; non-match → `Refused("Commit: <value> is not a commit id")`; match but not a prefix of `a.head` → the pre-existing mismatch message. All three raise before `store.record_result` (line 446) and `store.log_event` (line 453), so nothing is written and no `ci` row derives (`:447-450` is after). With `--killed` the old three lines are kept verbatim (`:432-434`). `Refused` exits 2 via `main()` at `:936-939`.

Verified by running:
- All nine WHEN commands from the parent spec, verbatim under bash from the worktree root: every THEN held (`exit=2 rows=[] events=0` for the five refusals; `exit=0 rows=[reviewer.yaml ] events=1`; `exit=0 rows=[ci.yaml verifier.yaml ] events=2`; `exit=0 rows=[verifier.yaml ] status=KILLED` twice).
- `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 python -m pytest -q -p no:cacheprovider tests/factory`: `64 passed in 82.45s`, exit 0. 64 = 55 + 9 new tests, as the acceptance criterion requires. The new file alone: `9 passed`.
- `ruff check nanobot/`: `All checks passed!` (the commit does not touch `nanobot/`, so this is trivially the base result). `ruff check factory/cli.py tests/factory/test_results_commit.py tests/factory/test_shepherd.py`: `All checks passed!`.
- Edge probes the spec implies but does not list (through `bin/factory`, head = forty zeros unless noted):
  - CRLF line endings: accepted (exit 0, row written). `.*$` under re.M keeps the `\r`, `\b` still holds after the hex.
  - Trailing text after the value (`Commit: 0000000 (reviewed the diff)`): accepted, as the spec's Decisions require.
  - 41 hex chars and 6 hex chars: both refused as `is not a commit id`. Correct: neither is a 7-40 hex id.
  - Uppercase abbreviated value against a lowercase head (`Commit: A000000` vs head `a000...`): accepted; the `.lower()` prefix check is kept.
  - `commit:` (lowercase), `  Commit:` (indented) and `**Commit:**`: all refused with `has no Commit: line`. The spec's Decisions say case-sensitive, line-start, and the bold form is explicitly out of scope.
  - Two `Commit:` lines that both name the head (full then abbreviated): accepted.
  - `--killed` with `Commit: deadbeef00`: refused with the old mismatch message; `--killed` with `Commit: HEAD`: accepted as KILLED. Today's killed behaviour is intact in both directions.
  - Verifier output with `Commit: deadbeef00` plus `Gate suite: PASS`: exit 2, no rows. The refusal precedes the `ci` derivation.
- The implementer's flagged behaviour change (a bare `Commit:` line with the hex on the next line, which the old `\s*` could match across the newline): now refused with `results record: Commit:  is not a commit id`. Under the spec's grammar (a line starting with `Commit:` whose value is 7-40 hex) this is the required outcome, not a deviation. It is a correct, if awkwardly worded, refusal; see NIT below.

I did not re-run the red step (the new file against `f8f40e0c5`); doing so would mean checking out another commit in this worktree. The parent spec's verification.md records the "today" results on `f8f40e0c5`, which is this head's parent, and they match the implementer's red-step claim (the four NEW scenarios are the ones that changed).

**3. Scope.** Only parts A, B, C. No other `factory` command, no `--head` validation change, no stale-rule change, no `build.js`. PASS.

**4. Silent behaviour changes.** The one not literally listed in the spec is the bare-`Commit:`-then-hex-on-next-line case above; it falls inside the spec's stated grammar and the implementer disclosed it. Nothing else: accepted outputs still produce the same rows, statuses, `ci` derivation and events (confirmed by the two accept scenarios and the `ci.yaml` status `PASS` assertion in `test_abbreviated_sha_in_backticks_is_recorded`).

**5. Security / data safety.** The change only adds refusals before any write. Error messages echo the offending `Commit:` value from the checker's output back to stderr; that text already flows into the park reason via `build.js`, as the spec's Risk section describes. No new input reaches a shell, a path or a store key.

**6. Protected paths.** None touched by the commit. The implementer reports that running the gate rewrote `webui/package-lock.json` in its worktree and that it restored it; the commit confirms it is not included.

**7. Maintainability.** The new test file is self-contained, drives the real CLI, asserts exit code 2 specifically plus the reason text plus "no rows" plus "no events", and the accept tests assert exact row lists and statuses. It is the right level of specificity; nothing hard-coded to output.

**Mergeability note (not a finding).** The branch does not contain the integration tip `b7d09a8`, so `factory merge` will report `head does not contain main` and route a conflict run; that is the shepherd's normal path. A read-only `git merge-tree f8f40e0c5 b7d09a8 e28db6a25` produces 0 conflict markers, and the integration-side `cli.py` changes (`_start_build_run`, `ticket_ready_implementers`) do not overlap `results_record`, so the rebase/merge should be mechanical.

## Findings

- [NIT] `factory/cli.py:440`: for a `Commit:` line with an empty value the message reads `results record: Commit:  is not a commit id` (double space, nothing between). → A human reading the park reason has to guess that the value was empty. Quoting the value (`Commit: '' is not a commit id`) would make it legible. Not blocking; the refusal itself is correct and spec-conformant.

No BLOCKING or SHOULD-FIX findings.

## Prior findings

None. Round 1.

## Out-of-scope observations

- The two environment problems the implementer hit (the gate rewriting `webui/package-lock.json` through a real webui install, and `neonize`/`mcp` drift making a lock-synced `.venv` fail the gate) are already addressed on the integration branch since this PR branched: `dc8e0b3a3` and `b7d09a8db` set `NANOBOT_SKIP_WEBUI_BUILD=1` for the gate, and `65842a90b` tests branches in the integration branch's environment (`gitops.copy_environment_files`, which is what placed the ignored `uv.lock` in this reviewer worktree). The verifier's `Gate suite` result on this head will still depend on which environment it runs in, as the implementer warned, until the branch is rebased onto `b7d09a8`.
- Carried forward from the parent, unchanged: `--killed --output <missing file>` crashes with `FileNotFoundError` (exit 1), and the `results record` call on `wrong.md` at `test_shepherd.py:333` is dead.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance WHEN held when I ran it verbatim at head, `tests/factory` is 64 passed / exit 0, the only existing-test edit is the one declared line, and the commit touches exactly the three files parts A-C name.
ESCALATIONS: none
