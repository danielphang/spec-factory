Commit: ba3fea8154f74ccd5007fd25d18f8215e0b7f000

Method: every GIVEN block and WHEN line was extracted by script, not retyped. The `t0033-gate.sh` block and the 16 WHEN lines came from `specs/T-0033/v2.md`. The `t0023-*` blocks came from the current-truth `openspec/specs/human-resolution/spec.md`, and `t0029-prompt.sh` from `openspec/specs/role-escalations/spec.md`. Each line ran under bash inside the HOME wrapper, with `TMPDIR` set to this run's scratch directory, after `uv sync --frozen`. The PR runs used the worktree at `ba3fea8`. The base runs used a clone in `scratch/base` checked out at `2f7f75f`, where `main` = `2f7f75f`. Logs: `scratch/pr.txt` and `scratch/base.txt`.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
1. NEW | An undeclared protected path is refused at merge, by name, and nothing merges | `exit=0 blocked=0 named=0 declared=0 main=moved merged` | `exit=2 blocked=1 named=2 declared=0 main=unchanged checks-in-flight` | PASS
2. NEW | Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing | `exit=0 named=0 main=moved` x3 | `exit=2 named=1 main=unchanged` x3 | PASS
3. REGRESSION | A declared protected path, or an unprotected one, merges with no further approval | base: not run (`exit=0 merged` x2 seen incidentally) | `exit=0 merged` x2 | PASS
4. NEW | The build parks a merge refused for protected paths with the gate's reason | `park: harness-bug: merge: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py` | `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py` | PASS
5. NEW | Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through | `accept=2 parked rows=3 ruling=missing` / `merge=2 on_main=1` | `accept=0 checks-in-flight rows=3 ruling=kept` / `merge=0 on_main=1` | PASS
6. NEW | Accepting paths is refused on any other park and writes nothing | `accept=2 refused=0 parked rulings=0` | `accept=2 refused=1 parked rulings=0` | PASS
7. NEW | A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling | `ruling=2 parked reason=0` / `in_input=0` | `ruling=0 ready-for-implementer reason=1` / `in_input=1` | PASS
8. NEW | A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling | `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml ` / `in_input=0` | `exit=0 checks-in-flight kept: ci.yaml verifier.yaml ` / `in_input=1` | PASS
9. REGRESSION | All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 | base: not run (same 4 lines seen incidentally) | `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` | PASS
10. NEW | The reviewer run prompt says what the merge gate checks | `gate=0 promise=1` | `gate=1 promise=0` | PASS
11. NEW | Every reviewer prompt copy states what the merge gate checks | `gate=0 promise=1` x3, `copy=SAME fill=unchanged` | `gate=1 promise=0` x3, `copy=SAME fill=unchanged` | PASS
12. NEW | Every spec writer prompt copy gives the declaration line | `reads=0 form=0 braces=0` x3, `copy=SAME fill=unchanged` | `reads=1 form=1 braces=1` x3, `copy=SAME fill=unchanged` | PASS
13. NEW | The design doc and build spec drop the per-PR approval for protected paths | `gates=1 either=1 onpr=1 piece8=0 piece9=1 gaterow=0 stale=1 reviewer_rule=0 old_route=1 build=1 build_new=0` | `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0 build=0 build_new=1` | PASS
14. NEW | The changelog records issue 57's change without a numbering gap | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `5` | PASS
15. NEW | README describes the protected-path check and the new resolve verb | `built=0 unstick=0 merges=0` | `built=1 unstick=1 merges=1` | PASS
16. REGRESSION | The protected-path change adds no whitespace errors | base: not run (trivially `exit=0`) | `exit=0` | PASS

Every NEW criterion failed on the base, in the way `verification.md` predicts, and passes on the PR. No criterion passes on both trees, and none fails on the base for a reason other than the one the spec states.

Gate suite: PASS
  `(export HOME=...; git diff --check main...HEAD)`, run from the worktree: no output, exit 0.
  `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`, run from the worktree: `408 passed in 337.92s (0:05:37)`, exit 0.
  The worktree is still clean after the runs (`git status --short` is empty), and HEAD is `ba3fea8`.

Probes: each ran on the PR head with the spec's own `t0033-gate.sh` fixture (`scratch/probes.sh`, `scratch/probe14.sh`). In the Risk-line inputs, `^` stands for a backtick, as the fixture uses it.
- P1. `core/*` declared; `core/new/c.py` changed → exit 2, names `core/new/c.py`. `*` does not cross directories, as the spec says → OK
- P2. `core/*` declared; `core/b.py` changed → exit 0, merged → OK
- P3. `- Protected paths: ^core/b.py^, ^bin/tool^.` (list marker and full stop); both paths changed → exit 0, merged → OK
- P4. `Protected paths: ^core/b.py^ and ^bin/tool^` (a line in another form) → exit 2, names `core/b.py` → OK
- P5. A correct declaration line under a later `## Other` section, not under Risk → exit 2 → OK
- P6. A correct declaration line inside a fenced block in Risk → exit 2 → OK
- P7. Undeclared deletion of `core/b.py` → exit 2, names it → OK
- P8. Brace list `core/{a,b}.py`; `core/b.py` changed → exit 2 → OK
- P9. Two `Protected paths:` lines, one for each changed file → exit 0. The two lines declare their union → OK
- P10. Move `docs/d.md` into `core/d.md`, undeclared → exit 2, names `core/d.md` → OK
- P11. Only an out-of-repo entry declared (`~/.secret/x`) → exit 2. The entry is skipped and declares nothing → OK
- P12. Lowercase key `protected paths:` → exit 2. The key is case-sensitive, which the spec's regex specifies → OK
- P13. `--accept-paths` on a merge-gate park, after the branch moved past `head` → exit 2, error `... is not the branch tip; run ticket head`, no ruling file written → OK
- P14. After `--accept-paths`, a catch-up merge of a moved `main` into the branch gives a new head. Rows were recorded on that head, and the accepted path still counts → `merge` exit 0. Acceptance holds across heads, as the spec decides → OK

The gate works on inputs beyond the tested ones. Nothing is special-cased to the scenario fixtures.

Protected paths the sub-ticket declares, for the record: the parent's Risk line. The diff touches `factory/cli.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `docs/prompts/02-spec-writer.md` and `docs/prompts/06-code-reviewer.md`, each on that line. It touches no other protected path. Its only test change is the new file `tests/factory/test_merge_protected_paths.py`.

STATUS: VERIFIED
CONFIDENCE: high, every scenario was run as written on both trees with the outputs above, both gates passed on `ba3fea8`, and 14 probes behaved as the spec decides.
ESCALATIONS: none
