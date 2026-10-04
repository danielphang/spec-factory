Commit: 74bc15d3dfae4cb43242ab567558b4a728e779f4 (branch `factory/T-0024.1`, one commit on base `d2a5143`)

## What I checked and how

Checked in the role's order, on the worktree at that head. Every command ran through the fresh-HOME wrapper.

1. **Test integrity.** `git diff --name-only main...HEAD` lists eight files; the only existing test file is `tests/factory/test_instance.py`, and its diff is exactly the two items under "Tests to change": `"FACTORY_DISPATCH"` added to `STRIP` (:21-22) and `FACTORY_DISPATCH="1"` on the `run compose` call (:275). No assertion changed, nothing skipped or deleted. `tests/factory/test_live_store_guard.py` is new. No guardrail path outside that was touched.
2. **Correctness.** Read `factory/cli.py` around `init_cmd` (:846-872), `fence` and `_in_flight` (:1195-1222) and `main()` (:1225-1238), and `factory/instance.py` `caller_cwd` (:41), `own_state_root` (:93) and `is_own_store` (:105). Both paths the location rule compares are `.resolve()`d, so `is_relative_to` is sound. The parser's dests are `cmd` and `sub` (:1047, :1049...), so the `READ_ONLY` lookup matches the design's pairs; `config` and `paths` have no `sub`, and `getattr(a, "sub", None)` covers them. `_in_flight` on a store with no `tickets/` returns `[]`: `Path(...).glob("*.yaml")` on a missing directory yields nothing on the venv's Python 3.14.5 (checked), so `init` on a new repository is not fenced by the in-flight rule, as design A.5 requires. Sub-tickets live at `tickets/<PARENT>.<n>.yaml` (`factory/subtickets.py:4`), so the glob unions them. Order is location, marker, in flight, as Decisions fix it. `Refused` reaches `main()`'s handler for exit 2 and the JSON error.
   I ran all 18 of the spec's scenarios on head, after running the GIVEN block itself (extracted verbatim from the spec, lines 342-397 of my input, run with `sh` into my scratch directory as `TMPDIR`). Each printed exactly its THEN:
   - `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`
   - `rule=1 state=1 marker=0 json=1 inside=1` (the refusal read `role runs may not write the live store (<tgt>/.factory/state; in flight: run-0001-triage); use a throwaway FACTORY_STATE`)
   - `accept=2 store=unchanged`
   - `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`
   - `idle=1 new=2 decision=2 store=unchanged`
   - `show=0 config=0 log=0 results=0 inside=0`
   - `decision=0 finish=0 cleared=1`
   - `init=0 new=0`
   - `new=0 decision=0`
   - `exit=2 lock=1 store=unchanged`
   - `intake: sent unmarked=0`, `build: sent unmarked=0`
   - `returned=closed stored=closed`
   - `CONTIGUOUS`, `5`
   - `design=1 dirs=1 prompts=0`
   - `first=1 command=1 unnamed=1 export=1 rundirs=1`
   - `stale=0 listed=1`
   - `bullet=1 stale=0`
   - `exit=0`
   Gate suite, as written from the worktree after `uv sync --frozen`: `265 passed in 190.32s`, exit 0 (`scratch/suite1.txt`). Again with `FACTORY_DISPATCH=1` exported in the calling shell: `265 passed in 202.87s`, exit 0 (`scratch/suite2.txt`). Both ran with pytest's temporary directory under the system `/var/folders/.../T/`, outside every repository. The worktree's `git status --short` printed nothing after all runs.
3. **Scope.** Every hunk maps to a lettered part: A.1-A.5 in `cli.py` (plus `import os`), A.6 the new test file, B the two `ENV` lines, C the three documents, and the two Tests-to-change items. The README status date was not changed; it already read `2026-10-04` (`README.md:9`), which is today, so "bump the date" is a no-op. Nothing in `factory/instance.py`, `agents/`, prompts, `bin/factory`, `.factory/`, `pyproject.toml` or `uv.lock`.
4. **Silent behaviour changes.** The ones the spec asks for and documents: unmarked writes refused during a run, writes from `runs/`/`worktrees/` always refused, `--accept-harness` fenced. Nothing else: the read-only list is untouched, the lock check is unchanged and still runs after the fence (scenario 10 shows the marker does not lift it).
5. **Security and data safety.** The refusal never prints the marker (`marker=0`), writes nothing (`store=unchanged`, `agents=none`), and happens before the lock rewrite. No new secrets, no destructive operation.
6. **Protected paths.** Touched exactly those the sub-ticket declares; listed under ESCALATIONS.
7. **Coding standard.** `fence` uses only existing helpers (`instance.is_own_store`, `own_state_root`, `caller_cwd`, `store.read_yaml`, `Refused`) and the stdlib. The new test file imports `cli`, `git_repo`, `js` and `tree` from `test_instance.py` instead of re-rolling them. Its `target` fixture and `start_triage` helper are near-duplicates of `test_instance.py`'s `target` (:63) and `_start_triage` (:265), but they differ (the fixture also files a ticket; the helper returns the run id and takes no `--model`), the originals are module-private, and `test_store_setup.py:66` already follows the same per-file pattern. Not tagged. `net: Lean already.` No `factory:` markers needed; the PR description says "markers added: none".
8. **PR description.** What changed glosses "role run", "live store", "dispatcher", "the guard" and "the clerk" at first use and says in words what the fence does before listing where. Known gaps are honest about the status date, the fixture-block workaround, the `_in_flight` non-mapping edge and the unreachable `paths` entry. I ran the literal GIVEN block the implementer could not, so that gap is closed on my side.

## Findings

- [NIT] factory/cli.py:1203: `store.read_yaml(p).get("in_flight")` raises on an empty or non-mapping `tickets/*.yaml`, so such a file turns every fenced write into exit 1 (`factory: AttributeError: ...`) instead of a refusal or a write → the store is still not written, so the failure is safe, but the message would not say which file is bad. The harness writes only mappings, and the implementer already lists this under Known gaps. No change asked.
- [NIT] tests/factory/test_live_store_guard.py:22-43: `target` and `start_triage` re-state `test_instance.py:63` and `:265` with small differences → one more place to update if `init`'s arguments or `run start`'s output change. Repo pattern already (`test_store_setup.py:66`); not a `reuse:` tag.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. I reran all 18 spec scenarios and both gate-suite runs myself on head and each printed its expected output; the diff is confined to the declared files and the two allowed test edits.
ESCALATIONS:
- Protected paths touched, all declared by the sub-ticket: harness `factory/cli.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`; guardrail `tests/factory/test_instance.py`, limited to the two Tests-to-change items. The merge gate needs a human approval for these.
