Commit: 380924577a12c60b93e59591f9aa7f53c0474d5c (branch `factory/T-0052.1`). Base given: 43a289e000c971ecc22d5303d387e3669bf5d987, which is current `main`. `git merge-base HEAD main` is now `43a289e`, so round 1's stale-base problem is gone. The head is a merge of `main` plus one fix commit.

How I ran things:
- I ran every command through the running-code wrapper, with a fresh temporary HOME each time, after `uv sync --frozen` (exit 0 in both checkouts).
- I ran the PR side in the worktree at `3809245`. I ran the base side in a scratch clone checked out at `43a289e` (`scratch/base`).
- I copied each scenario command from my input into `scratch/sc/s<n>.sh`. I confirmed with `grep -qF` that each one appears verbatim in `specs/T-0052/v2.md` (8 of 8). I ran each with `bash`.
- Logs: `scratch/pr.log`, `scratch/pr3.log`, `scratch/base.log`, `scratch/base3.log`, `scratch/gate2.log`, `scratch/probe.log`.

Per criterion:
- NEW | Every role agent template's frontmatter parses and carries name, description, model and tools | base: clerk and stub `keys=ok`; planner, spec-critic, spec-writer and triage `keys=unparsed` | PR: all six `keys=ok`, in the order the spec gives | PASS
- NEW | The four fixed templates keep their description's words and every other line | base: each of the four prints `text=changed rest=same`, then `others=same` | PR: `planner text=same rest=same`, `spec-critic text=same rest=same`, `spec-writer text=same rest=same`, `triage text=same rest=same`, `others=same` | PASS
- NEW | The suite fails on a template with broken frontmatter and names it | base: `suite=passed clerk=0 stub=0` | PR: `suite=failed clerk=1 stub=1` | PASS
  - I re-ran the same steps with the pytest log kept (`scratch/s3keep/log`). Only the two new cases fail, `[factory-clerk.md]` (a YAML `ScannerError`) and `[factory-stub.md]`, giving `2 failed, 592 passed`. The failure comes from the new test and from nothing else in the suite.
- NEW | init reports an edited agent copy and leaves it as it is | base: `exit=0 stale=absent kept=yes named=0 others=0` | PR: `exit=0 stale=factory-planner.md kept=yes named=1 others=0` | PASS
- REGRESSION | init still creates a missing agent copy and lists no matching copy | base: not run | PR: `exit=0 created=factory-triage.md stale=0 same=6 differs=0` | PASS
- NEW | README describes init's report of a differing agent copy | base: `row=0 step=0 missing=1` | PR: `row=1 step=1 missing=1` | PASS
- NEW | The changelog records issue 108 in one entry without a numbering gap | base: `CONTIGUOUS`, `0`, `0` | PR: `CONTIGUOUS`, `1`, `3` | PASS
  - The head now contains `main`'s entry `73. After issue #110`, so this result is real: the #108 entry is 74, with no collision.
- REGRESSION | README stays within its line budget and both documents pass the whitespace check | base: not run | PR: `readme=within`, `check=0` | PASS

Gate suite: PASS
  `git diff --check main...HEAD`: no output, exit 0. The merge-base is `43a289e`, so this covers the whole change against current `main`.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `594 passed in 92.19s`.

Probes (on the PR head, each in a fresh target):
- A directory in place of `factory-stub.md` (round 1's crash) → exit 0. `stale=factory-stub.md`, one stderr line, and the directory is left in place → OK. The round-1 concern is fixed.
- Three changes in one init: a one-byte change to clerk (an appended `\r`), `model` edited in spec-writer, and planner deleted → exit 0. `agents=factory-planner.md`, `stale=factory-clerk.md,factory-spec-writer.md`, one stderr line for each stale copy plus the restart line (because a copy was created). Both edited copies are byte-identical afterwards → OK. Any byte difference is reported, and the report is not tied to the tested planner case.
- A second init on that target → `agents=` (empty), the same two stale copies reported again, no restart line → OK.
- An extra non-template file, `.claude/agents/factory-foo.md` → exit 0, `stale=` (empty), nothing on stderr → OK. This matches the spec's Out of scope list.
- A copy with no read permission (`chmod 000 factory-triage.md`) → exit 1, `factory: PermissionError`, and no JSON output. On base, the same setup exits 0 and skips the copy silently → CONCERN, outside the criteria. The implementer disclosed it under Known gaps. It is the same kind of regression as round 1's directory crash. It is under ESCALATIONS, not FAILED.

Protected paths this change touches: `agents/**` (four templates) and `factory/**` (`factory/setup.py`). The spec's Risk section declares both.

STATUS: VERIFIED
CONFIDENCE: high. All eight commands printed their THEN exactly on `3809245`, and every NEW command printed the spec's stated "today" output on `43a289e`. Both gates passed, and the broken-template run fails on exactly the two new cases.
ESCALATIONS:
- Outside the criteria: `factory init` now exits 1 with `PermissionError`, and prints no JSON, when a `.claude/agents/factory-*.md` copy exists but cannot be read. Before this change it skipped such a copy silently and exited 0. The input is unusual and the implementer disclosed it. It is the same shape as round 1's directory case, which this round fixed by listing the path. Whether to treat an unreadable copy the same way is the operator's call.
