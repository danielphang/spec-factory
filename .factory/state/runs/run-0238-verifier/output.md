Commit: 74bc15d3dfae4cb43242ab567558b4a728e779f4 (branch `factory/T-0024.1`, one commit on base d2a51436922119790099d7c6ea6cb8f59bb87b9f)

How I ran it. PR: the run's worktree at head `74bc15d`, `git status` clean before and after, `uv sync --frozen` done under a fresh HOME. Base: a `git clone --no-checkout` of the worktree into this run's scratch directory, checked out at `d2a5143`, with a local `main` at `origin/main` (= `d2a5143`) and its own `uv sync --frozen`. The GIVEN block was run once, verbatim: I extracted lines 342-396 of `input.md` with `sed` into `scratch/given.sh` and ran it with `sh` under the fresh-HOME wrapper and `TMPDIR` set to this run's scratch directory. The three fixture files landed in scratch, and every line of each matched `input.md` by `grep -xF`. The 18 WHEN commands are in `scratch/run_all.sh`; each `( ... )` line was checked verbatim against `input.md` with `grep -F` before running. Each checkout's run went through the fresh-HOME wrapper with `TMPDIR` set to scratch. As the spec writer and implementer saw, `mktemp -d` ignored `TMPDIR` on this machine and put the scratch targets under `/var/folders/.../T/`; they are throwaway targets. Logs: `scratch/pr.txt`, `scratch/base.txt`, `scratch/gate1.txt`, `scratch/gate2.txt`, `scratch/probes.txt`.

Per criterion:
- NEW | Unmarked writes from inside the target are refused while a run is in flight, init included | base `init=0 new=0 transition=0 decision=0 store=changed agents=written` | PR `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` | PASS
- NEW | The refusal names the throwaway store and not the marker | base `rule=0 state=0 marker=0 json=0 inside=0` | PR `rule=1 state=1 marker=0 json=1 inside=1` | PASS
- NEW | A harness acceptance is refused while a run is in flight | base `accept=0 store=changed` | PR `accept=2 store=unchanged` | PASS
- NEW | Marked writes from a run's scratch directory or a worktree directory are refused, init included | base `scratch_decision=0 scratch_init=0 worktree_new=0 store=changed agents=written` | PR `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none` | PASS
- NEW | Writes from a finished run's scratch directory are refused with no run in flight | base `idle=1 new=0 decision=0 store=changed` | PR `idle=1 new=2 decision=2 store=unchanged` | PASS
- REGRESSION | Read commands still answer while a run is in flight | base `show=0 config=0 log=0 results=0 inside=0` (run alongside; not required) | PR `show=0 config=0 log=0 results=0 inside=0` | PASS
- REGRESSION | A marked write from the repository root still writes while a run is in flight | base `decision=0 finish=0 cleared=1` | PR `decision=0 finish=0 cleared=1` | PASS
- REGRESSION | A throwaway store is not fenced, even from a run's scratch directory | base `init=0 new=0` | PR `init=0 new=0` | PASS
- REGRESSION | With no run in flight, unmarked commands write as before | base `new=0 decision=0` | PR `new=0 decision=0` | PASS
- REGRESSION | A marked write from a harness checkout with an uncommitted edit is still refused | base `exit=2 lock=1 store=unchanged` | PR `exit=2 lock=1 store=unchanged` | PASS
- NEW | Every clerk command of both workflows carries the marker (`node t0024-count.mjs`) | base `intake: sent unmarked=6` / `build: sent unmarked=2` | PR `intake: sent unmarked=0` / `build: sent unmarked=0` | PASS
- REGRESSION | An intake run against a real store reaches its end with its run in flight (`node t0024-e2e.mjs`) | base `returned=closed stored=closed` | PR `returned=closed stored=closed` | PASS
- NEW | The changelog records the guard as its last entry | base `CONTIGUOUS` / `2` | PR `CONTIGUOUS` / `5` | PASS
- NEW | The design doc names the marker and the run-directory rule, and no prompt copy changes | base `design=0 dirs=0 prompts=0` | PR `design=1 dirs=1 prompts=0` | PASS
- NEW | README tells the operator how to write during a run, first thing under Where a human decides | base `first=0 command=0 unnamed=0 export=0 rundirs=0` | PR `first=1 command=1 unnamed=1 export=1 rundirs=1` | PASS
- NEW | README says the final verifier run is listed as in flight | base `stale=1 listed=0` | PR `stale=0 listed=1` | PASS
- NEW | README no longer says the factory's capabilities never entered the spec store | base `bullet=1 stale=1` | PR `bullet=1 stale=0` | PASS
- REGRESSION | The guard change adds no whitespace errors (`git diff --check main...HEAD`) | base `exit=0` | PR `exit=0` | PASS

Every NEW criterion fails on base with the spec's stated "today" value and passes on the PR, so none is a SPEC-DEFECT. Every REGRESSION criterion passed on the PR.

Gate suite: PASS
- `(export HOME=...; git diff --check main...HEAD)` from the worktree: no output, exit 0.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` from the worktree, `TMPDIR` inherited as `/var/folders/1t/.../T/` (outside every repository), `FACTORY_DISPATCH` unset: `265 passed in 203.89s`. The new `tests/factory/test_live_store_guard.py` is among them (254 existing + 11 new).
- Second run, same command, with `FACTORY_DISPATCH=1` exported in the calling shell: `265 passed in 177.64s`. The `STRIP` change takes effect: an exported marker changes no result.
- uv printed a warning that the shell's `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` was ignored in favour of the project `.venv`; the suite ran on the worktree's own environment.

Probes (all on the PR head, fixture target with one triage run in flight unless said otherwise):
- `FACTORY_DISPATCH=01`, `" 1"`, `true` on `decision add` from the target root → each exit 2; `FACTORY_DISPATCH=1` → exit 0 → OK (only the exact value `1` is the marker).
- Marked `decision add` from `<store>/runsfoo/`, a sibling directory whose name starts with `runs` → exit 0 → OK (the location rule is path-segment based, not a string prefix; a real `runs/` subdirectory is refused, see criteria).
- Marked `decision add` from a symlink outside the store that points at the run's scratch directory → exit 2, stderr says `called from inside its runs/` → OK (`caller_cwd()` resolves, `factory/instance.py:41-42`).
- Run in flight on T-0002 only (T-0001's run finished): unmarked `decision add T-0001` → exit 2, refusal names T-0002's run id; after that run is finished, the same command → exit 0 → OK (the in-flight union spans every ticket, and the fence drops when the store goes idle).
- Nothing in flight, marked `--accept-harness <lock> ticket show` from the run's scratch directory → exit 2, `store=unchanged` → OK (`--accept-harness` is a write and the location rule holds with an idle store and the marker).
- `ticket set` and `run compose` unmarked while in flight → exit 2 each; `paths` and `status parse` from inside `runs/` → exit 0 each → OK.
- A stray `tickets/zz-empty.yaml` (empty) or `tickets/zz-list.yaml` (a YAML list) in the store, then unmarked `decision add` from the root → exit 1 with `factory: AttributeError: 'NoneType' object has no attribute 'get'` / `'list' object has no attribute 'get'` → CONCERN, outside the criteria. `_in_flight` (`factory/cli.py:1200-1202`) assumes every `tickets/*.yaml` is a mapping. The harness writes only mappings, and the implementer disclosed this under Known gaps. On base the same command succeeds because nothing reads the other ticket files. See ESCALATIONS.

Side effects: the worktree's `git status` is clean. `~/dev/spec-factory/.claude` does not exist. The dev checkout's uncommitted store changes are other tickets' runs (run-0234 to run-0239) and this run's own directory; nothing of mine wrote the live store.

STATUS: VERIFIED
CONFIDENCE: high. All 18 acceptance commands were run verbatim on base and head and printed exactly the spec's values; the gate suite passed 265/265 twice, with and without the marker exported; six probes found no special-casing, and the one concern is a malformed-store crash outside the criteria that the implementer already disclosed.
ESCALATIONS:
- Not a failure of a criterion, for a follow-up: with a non-mapping file in `<store>/tickets/` (empty, or a YAML list), every fenced write on the own store exits 1 with a Python `AttributeError` from `_in_flight` instead of a refusal or a clear error. The harness never writes such a file, so this needs a hand-made or corrupted store. It is a new crash route this change adds, and base writes normally in that state.
