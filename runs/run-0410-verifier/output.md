Commit: 4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8

How I ran it. The PR side ran in the given worktree at 4bfedc7. The base side ran in a clean export of 2ad4d8c (`git archive | tar -x` into `scratch/base`). Each side had its own `uv sync --frozen`. The GIVEN blocks were extracted verbatim from the store's specs: `openspec/specs/human-resolution/spec.md` (t0023-*), `openspec/specs/live-store-guard/spec.md` (t0024-*) and `openspec/changes/T-0040/specs/build-dispatch/spec.md` (t0040-*). The t0040 block is byte-identical to the one in `specs/T-0040/v4.md` (checked with `diff`). Each block was run once with `TMPDIR=scratch/tmp`. Each WHEN command was copied by line number from input.md into `scratch/cmd/*.sh`. Each was run unchanged under bash through the running-code wrapper, with that `TMPDIR`. Outputs are in `scratch/pr-new.txt`, `scratch/pr-reg.txt`, `scratch/base-new.txt`, `scratch/pytest.txt`, `scratch/probes1.txt` and `scratch/probes2.txt`.

Per criterion:
- NEW | "The driver takes the build fixtures through the same routes as the build script" | base: `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=6/6 drive=0/0 differ`, `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=1/1 drive=0/0 differ` | PR: `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same` | PASS
- NEW | "Each role runs as one claude process with its prompt, model and tool limits" | base: `critic ok`, `spec_writer ok`, `triage ok`, then a blank line (the build half starts no process; the intake half already passed after A, as the sub-ticket says) | PR: `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok` | PASS
- NEW | "The checkers run at once, and sub-tickets up to the parallel limit" | base: `parallel=1: calls=0 max=0 checks-in-flight checks-in-flight`, `parallel=default: calls=0 max=0 checks-in-flight checks-in-flight` | PR: `parallel=1: calls=4 max=2 parked parked`, `parallel=default: calls=4 max=4 parked parked` | PASS
- NEW | "Build step lines name the sub-ticket they concern" | base: `untagged=0 sub=no last=0` | PR: `untagged=0 sub=yes last=1` | PASS
- REGRESSION | "The driver takes the intake fixtures through the same routes as the intake script" | base: not run | PR: `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same` | PASS
- REGRESSION | "Each role run records its process's reply" | base: not run | PR: `triage=ok spec_writer=ok critic=ok` | PASS
- REGRESSION | "Every intake step line names its ticket and title, and the status file shows the end" | base: not run | PR: `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1` | PASS
- REGRESSION | "A stopped driver ends its role process, records the run as killed and resumes from the stored state" | base: not run | PR: `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, `resumed: exit=0 closed calls=2` | PASS
- REGRESSION | "The driver marks its own store calls, never its roles', and passes a configured effort" | base: not run | PR: `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2` | PASS
- REGRESSION | "The Workflow scripts still take both fixtures to the end of their routes" | base: not run | PR: `T-0001.1 merged T-0001 parked`, `T-0001 awaiting-spec-gate` | PASS
- Intermediate check | `uv run --frozen pytest -q -p no:cacheprovider tests/factory` | base: not run | PR: `520 passed in 439.10s (0:07:19)`, exit 0 (this is the gate run below) | PASS

Each NEW criterion fails on base for the reason verification.md states: the base driver refuses every build state, so the drive side starts no process. On base, every printed line matches verification.md's "today" figures.

Gate suite: PASS
- `git diff --check main...HEAD`: exit 0, no output (`main` is 2ad4d8c, the base).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `520 passed in 439.10s (0:07:19)`, exit 0.

Probes. Each parity probe runs the build script under node and `factory drive --phase build` on identical fixtures, as `t0040-parity.sh` does, using a scratch variant of it (`scratch/probe-parity.sh`). None of these routes is in the acceptance fixtures.
- Two sub-tickets, where ST-2 depends on ST-1, with all roles succeeding. Result: `parked script=7/7 drive=7/7 same`. The dependency order and the second `ready-implementers` pass match the script. OK
- Planner route, with a spec that has a `## Seams` heading so the planner is not skipped. The planner returns ESCALATE. Result: `parked script=1/1 drive=1/1 same`. OK
- Planner returns PLANNED with no plan text, so `subticket add` is refused. Result: `parked script=1/1 drive=1/1 differ`. The only differing record is the park reason. The driver stores the harness's real message, ``harness-bug: subticket add: no sub-tickets found (a head line `<id> / Title`, …, then `Depends on:` and `Parallel-safe:`)``. The script stores the same text with every backticked span missing, because its clerk passes the reason through `sh -c`, where backticks are command substitution. The driver is the correct one here, and the cause is in the script. Still, the parent's Decision says park reasons match the scripts byte for byte, and on this route they do not. CONCERN (see ESCALATIONS; not a FAIL)
- Implementer process fails (`fail`: exit 1, `is_error`). Result: `planned script=1/1 drive=1/1 same`. OK
- Verifier process fails while the reviewer approves. Result: `planned script=3/3 drive=3/3 same`. Both checkers' runs are recorded as in the script. OK
- Three independent sub-tickets waiting at `checks-in-flight`, with checkers that sleep 3 s. Results: default `calls=6 max=4`; `--parallel 3` `calls=6 max=6`. All three sub-tickets are parked, and no stdout line is untagged. The bound follows N and is not tied to the two-sub-ticket fixture. OK
- `--parallel 0`, `-1` and `x`. Each exits 2 with argparse's "is less than 1" or "invalid … value" error, before any store call. OK

Out-of-scope observations
- On this machine, `mktemp -d` ignores the exported `TMPDIR`, so the scenarios' throwaway stores went to the system temp directory. The fixture files themselves were read from `scratch/tmp`, as intended. This does not affect any result.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command was run as written on both heads and printed exactly the expected lines on the PR. Both gates passed. The probes reached five build branches the fixtures do not reach, and only one showed a difference, which comes from the script.
ESCALATIONS:
- On the planner route where `subticket add` is refused, the driver's park reason does not match the script's. The script drops every backticked span from the reason, because its clerk runs the park command through `sh -c`. The driver records the harness's message intact. This breaks the parent's Decision that park reasons match the scripts byte for byte, but here the script is the one in error. No acceptance fixture reaches this route. Someone should decide whether to file it against the Workflow script's `park()` quoting, or to leave it until the retirement ticket.
