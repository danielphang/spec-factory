Commit: 8f9c2a96193e4aef8207f6dfd750c334e78f43a5

How this was run. The PR is the worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0428-verifier/wt` at the head commit, with a clean `git status`. The base is a local clone at `scratch/base`, checked out at `98dd74c2ec5165f70bf7f08d9ed38d808ade01e4`, with `main` at that commit. Each checkout ran `uv sync --frozen` through the wrapper first. The GIVEN fixtures were taken unchanged from the store and written with `TMPDIR=scratch/tmp`:
- `t0024-inflight.sh`, `t0024-count.mjs` and `t0024-e2e.mjs` come from the block in `openspec/changes/T-0042/specs/live-store-guard/spec.md`. That block is byte-identical to the briefing's.
- `t0022-sib.sh` and `t0022-build.mjs` come from `openspec/specs/build-dispatch/spec.md` lines 52-101.
- The `t0040-*` files come from the same spec, lines 276-415.

Each WHEN was copied verbatim from the briefing, and `grep -F` confirmed each one against the store's T-0042 spec files. Each ran with `bash`, through the wrapper, from the root of the checkout under test.

Per criterion:
- REGRESSION | Unmarked writes from inside the target are refused while a run is in flight, init included | base: not run | PR: `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` | PASS
- REGRESSION | The refusal names the throwaway store and not the marker | base: not run | PR: `rule=1 state=1 marker=0 json=1 inside=1` | PASS
- REGRESSION | A harness acceptance is refused while a run is in flight | base: not run | PR: `accept=2 store=unchanged` | PASS
- NEW | An unmarked drive starts beside another ticket's run, is refused from a run's directory, and marks only its own store calls | base: `inside_unmarked=2 inside_marked=2 accept=2 unmarked=2 ready-for-triage calls=0 effort=0 dispatch=0` | PR: `inside_unmarked=2 inside_marked=2 accept=2 unmarked=0 closed calls=1 effort=1 dispatch=1` | PASS
- NEW | A drive of a ticket with its own run in flight is refused, marked or not, and writes nothing | base: `unmarked=2 marked=0 named=1 marker=0 json=0 calls=0 store=changed parked` | PR: `unmarked=2 marked=2 named=2 marker=0 json=1 calls=0 store=unchanged ready-for-triage` | PASS
- NEW | A drive of a parent whose sub-ticket has a run in flight is refused and writes nothing | base: `exit=0 named=0 calls=0 store=changed` | PR: `exit=2 named=1 calls=0 store=unchanged` | PASS
- NEW | A recorded live driver blocks a second drive, and an ended or dead one does not | base: `live=0 pid=0 file=changed closed ended=0 closed dead=0 closed calls=3` | PR: `live=2 pid=1 file=unchanged ready-for-triage ended=0 closed dead=0 closed calls=2` | PASS
- NEW | The documents describe the driver's exemption and its same-ticket guard | base: `changelog=CONTIGUOUS last=no step=1 drive=no,no fence=no human=no design=no,no,1 buildspec=no,no whitespace=clean` | PR: `changelog=CONTIGUOUS last=yes step=0 drive=yes,yes fence=yes human=yes design=yes,yes,0 buildspec=yes,yes whitespace=clean` | PASS

Every PR line equals its THEN line exactly. Every base line equals verification.md's "Today it prints" line exactly, so each NEW criterion fails on the base for the reason the spec states.

Gate suite: PASS
  `git diff --check main...HEAD` ran as written from the worktree and exited 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory` ran as written from the worktree. It exited 0 and printed `546 passed in 356.96s (0:05:56)`; the log is `scratch/gate-pytest2.log`.
  My first suite run reported `6 failed, 540 passed`, but that was my own setup, not the change. I had exported `TMPDIR=scratch/tmp`, which sits inside the spec-factory repo and its `.factory/` instance. So tests that need a directory outside any git work tree or instance found one. The failing tests were in test_instance, test_environment_sync and test_spec_drift, with asserts such as "not inside a git work tree" and "no .factory/instance.yaml found". The gate command as written does not set `TMPDIR`. Run that way, with the session's default `/var/folders/...` `TMPDIR`, it passed in full. The failing log is `scratch/gate-pytest.log`.

Probes (on a throwaway `FACTORY_STATE`, with the stand-in `claude` from `t0040-bin`, and each also run on the base for comparison; script `scratch/probe.sh`):
- Two real drivers at once. A drive of T-0001 was started with a triage role that sleeps 6 s, and two more drives were run while it worked. A second drive of T-0001 exited 2 with `T-0001 has runs in flight on it or its sub-tickets: run-0001-triage; drive it again once they finish`. A drive of T-0002 exited 0 with T-0002 `closed`, and the first drive then finished, exit 0, `closed`. On the base the second same-ticket drive exited 0. → OK. This is the reported case, with real concurrent processes rather than a planted record, and the guard is not special-cased to the scenario's planted files.
- An empty `drive/T-0004.yaml` → exit 0, `closed`, the same as the base → OK.
- A quoted live pid, `pid: "<pid of a live sleep>"`, with `ended: null` → no block, exit 0 and `closed`. This matches the spec's "a non-integer pid does not block". The driver itself writes `pid` as an int (`os.getpid()`, `factory/drive.py:656`) → OK.
- A missing ticket, `drive T-0099` → exit 1 with `{"ok": false, "ticket": "T-0099", "error": "no such ticket: no ticket T-0099\n"}`, identical to the base → OK. The "no such ticket" result is unchanged, as the Decisions require.
- A status file that is valid YAML but not a mapping (`- a\n- b\n`) → exit 1, `AttributeError: 'list' object has no attribute 'get'`. On the base the same drive went ahead to `closed`. → CONCERN. No stated criterion covers this, and the implementer listed it under Known gaps. The driver always writes a mapping, so this needs a hand-damaged file. See ESCALATIONS.

Scope check. `git diff --stat base..head` lists only these files: README.md, dev/build-harness.spec.md, docs/changelog.md, docs/design.md, factory/cli.py, factory/drive.py and the new tests/factory/test_drive_guard.py. Nothing under docs/prompts/ or factory/prompts/ changed. The protected paths touched, factory/cli.py and factory/drive.py, are the ones the spec's Risk section declares. The new test file is a new file, and no existing test changed.

STATUS: VERIFIED
CONFIDENCE: high. All 8 acceptance commands printed their THEN lines on the head, the 5 NEW commands printed their stated "Today" lines on the base, both gates passed as written, and a real two-driver probe behaved as the spec intends.
ESCALATIONS:
- A non-mapping `drive/<ticket>.yaml` now stops a drive of that ticket with exit 1 (`AttributeError`). Before this change the drive went ahead. The driver never writes such a file, so this needs a hand-damaged or truncated-then-rewritten file. The spec covers missing, non-integer and dead pids but not a malformed file. The operator decides whether the guard should treat a non-mapping file as "does not block" (follow-up) or leave it as is.
