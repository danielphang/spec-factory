Commit: c01e7c2cf8bdef4f73fd8443744906b9ea89db74

Setup. I checked the PR head in this run's worktree (`wt`, branch `factory/T-0032.1`, clean, HEAD `c01e7c2`). For the base, I made a fresh clone at `97becfd` (= `main`) in `scratch/base`, and ran `uv sync --frozen` in both checkouts. I extracted the GIVEN fixture blocks verbatim from current truth (`openspec/specs/human-resolution`, `build-dispatch`, `role-escalations`) and from the pinned spec `specs/T-0032/v1.md`. The T-0032 block in the pinned spec is identical to the one in this input and in `openspec/changes/T-0032`. I wrote the blocks with `TMPDIR=scratch/tmp`. The 14 WHEN commands were extracted verbatim from `specs/T-0032/v1.md` (`grep '^- WHEN'`, 14 lines) and each was run in `bash -c` with a fresh HOME and the same TMPDIR, from the checkout root. Raw output: `scratch/pr.out`, `scratch/base.out`.

Per criterion:
1. NEW | Reviewer ends its turn waiting: re-dispatched once, then parks | base: `park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` / `verifier: VERIFIED ` / `kept=0 "rows": {"ci": "PASS", "verifier": "VERIFIED", "reviewer": "KILLED"}` | PR: `park T-0001.1: EMPTY-OUTPUT from reviewer` / `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` / `verifier: VERIFIED ` / `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` | PASS
2. NEW | One empty reviewer run followed by a real one routes on the real one | base: `park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` | PR: `park T-0001.1: SPEC-DEFECT from verifier` / `reviewer: EMPTY-OUTPUT APPROVE ` | PASS
3. NEW | Implementer returns nothing twice | base: `park T-0001.2: budget kill: implementer` / `implementer: KILLED ` | PR: `park T-0001.2: EMPTY-OUTPUT from implementer` / `implementer: EMPTY-OUTPUT EMPTY-OUTPUT ` | PASS
4. NEW | Intake role's second empty output parks | base: `start: triage` / `park: harness-bug: unknown STATUS EMPTY-OUTPUT from triage` | PR: `start: triage` / `start: triage` / `park: EMPTY-OUTPUT from triage` | PASS
5. REGRESSION | A reviewer that writes its output runs once | base: not run | PR: `park T-0001.1: SPEC-DEFECT from verifier` / `reviewer: APPROVE ` | PASS
6. NEW | Preamble copies carry the wait rule and stay identical | base: `fg=0 end=0` x3 / `verbatim` | PR: `fg=1 end=1` x3 / `verbatim` | PASS
7. NEW | Run prompts: wait rule for all three, judge rule for the reviewer only | base: `implementer fg=0 judge=0` / `reviewer fg=0 judge=0` / `verifier fg=0 judge=0` | PR: `implementer fg=1 judge=0` / `reviewer fg=1 judge=1` / `verifier fg=1 judge=0` | PASS
8. NEW | Reviewer copies carry the rule, keep every line, verifier prompt unchanged | base: `judge=0 narrow=0` x3 / `copy=SAME fill=unchanged removed=0 verifier_changed=0` | PR: `judge=1 narrow=1` x3 / `copy=SAME fill=unchanged removed=0 verifier_changed=0` | PASS (the last line passes on base by design; the `judge`/`narrow` lines fail there, as verification.md states)
9. NEW | Reviewer input no longer lists the gate commands | base: `reviewer gates=1 told=0` / `verifier gates=1 told=0` / `implementer gates=1 told=0` | PR: `reviewer gates=0 told=1` / `verifier gates=1 told=0` / `implementer gates=1 told=0` | PASS
10. NEW | Design doc states the rule, rows and park | base: `rule=0 rows=0 parks=0 kill=0` | PR: `rule=1 rows=2 parks=1 kill=1` | PASS
11. NEW | Build spec describes EMPTY-OUTPUT, no KILLED condition | base: `stale=3 empty=0 note=0` | PR: `stale=0 empty=1 note=1` | PASS
12. NEW | README drops the budget park | base: `budget=2 built=0 unstick=0` | PR: `budget=0 built=1 unstick=1` | PASS
13. NEW | Changelog records issue 41 without a gap | base: `CONTIGUOUS` / `0` | PR: `CONTIGUOUS` / `5` | PASS
14. REGRESSION | No whitespace errors | base: not run | PR: `exit=0` | PASS

Every base result matches the "fails today" text in verification.md, and each fails for the reason the spec gives. No NEW criterion passes on both.

Gate suite: PASS
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)` from the worktree: exit 0, no output.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` from the worktree: exit 0, `360 passed in 215.27s (0:03:35)`.

Probes:
- Reviewer returns a 4500+ character last message, padded with spaces, with apostrophes, `$HOME`, backticks, a literal `\n` and a real newline, then is empty a second time → both runs `EMPTY-OUTPUT`, park `EMPTY-OUTPUT from reviewer`, and each `last-message.md` is byte-identical to the last 4000 characters of the trimmed text plus a newline (4001 bytes, `cmp` equal, head marker absent) → OK. The shell quoting survives a real `sh -c`.
- Reviewer returns whitespace-only text twice (an accidental case from my first, mis-quoted probe) → both runs `EMPTY-OUTPUT`, no `last-message.md` written → OK. This matches "non-blank text" only.
- Reviewer returns non-blank text with no file, then writes APPROVE; verifier SPEC-DEFECT → `reviewer: EMPTY-OUTPUT APPROVE`, one last message kept, routed `SPEC-DEFECT from verifier` → OK.
- Implementer returns `null`, then writes BLOCKED → `implementer: EMPTY-OUTPUT BLOCKED`, park `BLOCKED from implementer` → OK. The retry routes on the real status for a role other than the reviewer.
- Intake: triage EMPTY-OUTPUT, then ACCEPT, then spec_writer EMPTY-OUTPUT twice (stub store) → `start: triage` x2, `start: spec_writer` x2, `park: EMPTY-OUTPUT from spec_writer` → OK. The count is per role call: a different role's earlier empty output does not count toward the park.
- `run finish` on an output with text and no trailer → `"status": "UNKNOWN"`, not EMPTY-OUTPUT → OK. A malformed output is not mistaken for an empty one, and is not retried.
- `run last-message` on a run still in flight → exit 2, `run-0001-triage is running, not EMPTY-OUTPUT: no last message to keep`, no file → OK.
- Ruling item 3 (outside the scenarios): composing a reviewer and a verifier input with the suite's own `Target` helper, for a diff that skips the scoped command → each has 1 `SKIPPED by the harness …` line and 1 `gate_skipped` entry. The reviewer's paragraph says the verifier runs the gate and lists no commands; the verifier's lists them → OK.

Notes:
- Protected paths the diff touches, all declared in the parent's Risk list: `factory/cli.py`, `factory/compose.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `factory/prompts/preamble.md`, `factory/prompts/reviewer.md`, `docs/prompts/00-preamble.md`, `docs/prompts/06-code-reviewer.md`. `git diff --name-status 97becfd...c01e7c2` shows no other protected path.
- The diff changes one existing test, `tests/factory/test_gate_paths.py`, by one line (`t.checker("reviewer")` → `t.checker()`; `git diff 679dccc c01e7c2` shows only it and `factory/compose.py`). The parent's "Tests to change" is none. The change follows the operator's ruling of 2026-10-06, which is recorded in the store at `approvals/T-0032.1/ruling-2.md`. That test now checks the verifier input. For the reviewer, the case where the diff touches the scoped command's paths is covered by the reviewer-gets-no-commands scenario (9). The implementer's Known gaps already state that no suite test pins the reviewer's SKIPPED lines.
- The fixtures' `mktemp -d` calls created their throwaway stores in the system temp directory, not under `scratch/tmp`. The fixture text reads only the `TMPDIR` fixture paths from scratch. No protected path was written.

STATUS: VERIFIED
CONFIDENCE: high, all 14 scenarios ran verbatim on both checkouts, every NEW one fails on base for the stated reason and passes on the PR, both gates pass (360 tests), and the boundary probes found no special-casing.
ESCALATIONS: none
