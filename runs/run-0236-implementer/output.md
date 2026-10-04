Sub-ticket: T-0024.1 (parent T-0024, issue #45, spec v5): Live-store fence, dispatcher marker and its documents
Branch: `factory/T-0024.1`, base `d2a51436922119790099d7c6ea6cb8f59bb87b9f`, head `74bc15d3dfae4cb43242ab567558b4a728e779f4` (one commit)

## What changed

A role run is an agent the factory starts to work on one ticket. Before this change, a role run could write the live store, which holds the factory's live records for a repository under `.factory/state/`, by running `bin/factory` from anywhere inside that repository. That is how a spec writer's test suite initialised this repository's store on 2026-10-04. After this change, the tool refuses such writes in two cases. The first is a write run from inside the store's run directories (`runs/`) or code checkouts (`worktrees/`). The second is a write made without the dispatcher's marker, `FACTORY_DISPATCH=1`, while any run is in flight. The dispatcher is the workflow script that starts role runs, and it now puts the marker on every command it sends.

- **A.1–A.5, the fence, in `factory/cli.py`.**
  - `READ_ONLY` is the set of `(command, subcommand)` pairs that are never fenced: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`.
  - `_in_flight(root)` returns the union of the `in_flight` lists over `tickets/*.yaml`, sub-tickets included. A store with no `tickets/` directory has nothing in flight.
  - `fence(inst, cfg, root)` acts only when `instance.is_own_store(...)` is true. It checks in this order:
    1. Location: if `instance.caller_cwd()` lies under `own_state_root/runs` or `own_state_root/worktrees`, the write is refused, whatever the marker says.
    2. Marker: if `FACTORY_DISPATCH == "1"`, the write goes through.
    3. In flight: if any run is in flight, the write is refused.

    Both refusals use the spec's text, `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. Neither names the marker.
  - `main()` calls the fence between `root = store.state_root(cfg)` and `instance.guard(...)`, for any command outside `READ_ONLY` and for any command given `--accept-harness`. The guard is the harness lock check. `init_cmd` calls the fence on the line right after `root = instance.state_root(inst, cfg)`. These are the only two call sites. `import os` was added.
  - Callers, per coding rule 2. `main()` is called by `python -m factory` (`bin/factory`) and by `tests/factory/clean_harness_cli.py:28`. `init_cmd` is reached only through the parser's `set_defaults(fn=init_cmd)` (`factory/cli.py:1146`). `fence` is called only at `cli.py:872` and `:1235`.
- **A.6, the new test file.** `tests/factory/test_live_store_guard.py` has 11 tests. They cover:
  - unmarked writes refused while a run is in flight, from the target root and from a subdirectory: `ticket new`, `ticket transition`, `decision add`, `ticket set`;
  - `init` refused without rewriting the agent files;
  - `--accept-harness` refused without changing the store;
  - reads that still answer, from the root and from a run's scratch directory;
  - a marked write from the root that goes through;
  - a value other than `1` (`FACTORY_DISPATCH=yes`) that is not taken as the marker;
  - idle unmarked writes that go through;
  - a throwaway store that is not fenced;
  - marked writes refused from a run's scratch directory (`decision add`, `init`, `ticket new`) and from under `worktrees/` (`ticket new`, `init`);
  - writes from a finished run's scratch directory refused while nothing is in flight.

  The file reuses `cli`, `git_repo`, `js` and `tree` from `test_instance.py`. That `cli` now drops `FACTORY_DISPATCH` from the inherited environment, so a runner shell that exported the marker cannot change a result.
- **B, the marker.** In `factory/workflows/intake.js:26` and `factory/workflows/build.js:21`, `ENV` now starts with `'FACTORY_DISPATCH=1'`. Every clerk command is built from `BIN`, so each one carries the marker. The clerk is the helper agent that runs one store command at a time for the workflow.
- **C, the documents.**
  - `docs/design.md`: a new one-line paragraph after "**Tripwire on live files.**", titled "**Only the dispatcher writes a live store during a run.**". It covers the location rule, the in-flight rule, the read-only list and `--accept-harness`, the marker and the operator's per-command use of it, and the refusal. It also says the fence is checked before the lock, and that it guards against accidents and is not isolation.
  - `docs/changelog.md`: entry 52, placed after 51 and before the "Declined:" line. It names `FACTORY_DISPATCH`, in flight, `runs/` and `worktrees/`, the throwaway store and exit 2. It says why the request's preamble line and its store-root tripwire were declined.
  - `README.md`, in five places:
    - "Where a human decides" now opens with the bold marker sentence on line 3 of the section. After it come a gloss of "in flight", the read-only list, the command form in a code block, the deliberately-unnamed-marker explanation, "Never export the marker", the rule to write from the repository root and not from `runs/` or `worktrees/`, and the command that clears a stale run.
    - A "Live-store fence" bullet under Built. It says the fence is tested and has not yet fired on a real ticket.
    - The sentence about the final verifier run now says it is listed as in flight like any other run.
    - The "Current truth for the factory itself" bullet is rewritten without "never entered it" and without a count.
    - The status date: see Known gaps.
- **Tests to change.** In `tests/factory/test_instance.py`, `"FACTORY_DISPATCH"` was added to `STRIP`. The tuple is wrapped onto a second line because it is longer than before. `test_composed_input_opens_with_the_instance_context` now passes `FACTORY_DISPATCH="1"` to its `run compose` call. No other existing test changed.

## Acceptance results

All commands ran from the worktree root after `uv sync --frozen`, through the fresh-HOME wrapper, with `TMPDIR` set to this run's scratch directory. The three GIVEN fixture files went there too. I wrote them with the Write tool, not by running the spec's `cat >` block, because the permission classifier refused my first attempt: it extracted the block with `sed` and ran it with `sh`. A line-by-line `grep -xF` against `input.md` confirmed that the three files and all 18 WHEN commands match the spec verbatim. As the spec writer also saw, `mktemp -d` ignored `TMPDIR`, so the scratch targets were created under `/var/folders/.../T/`. Logs: `scratch/base.txt` is base `d2a5143`; `scratch/after.txt` is head `74bc15d`.

| Scenario | Kind | Before (base) | After (head) |
|---|---|---|---|
| Unmarked writes refused while in flight, init included | NEW | `init=0 new=0 transition=0 decision=0 store=changed agents=written` | `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` |
| Refusal names throwaway store, not marker | NEW | `rule=0 state=0 marker=0 json=0 inside=0` | `rule=1 state=1 marker=0 json=1 inside=1` |
| Harness acceptance refused while in flight | NEW | `accept=0 store=changed` | `accept=2 store=unchanged` |
| Marked writes from scratch / worktree refused | NEW | `scratch_decision=0 scratch_init=0 worktree_new=0 store=changed agents=written` | `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none` |
| Finished run's scratch refused, nothing in flight | NEW | `idle=1 new=0 decision=0 store=changed` | `idle=1 new=2 decision=2 store=unchanged` |
| Reads answer while in flight | REGRESSION | `show=0 config=0 log=0 results=0 inside=0` | `show=0 config=0 log=0 results=0 inside=0` |
| Marked write from repo root goes through | REGRESSION | `decision=0 finish=0 cleared=1` | `decision=0 finish=0 cleared=1` |
| Throwaway store not fenced | REGRESSION | `init=0 new=0` | `init=0 new=0` |
| Idle unmarked writes go through | REGRESSION | `new=0 decision=0` | `new=0 decision=0` |
| Marker does not lift the lock | REGRESSION | `exit=2 lock=1 store=unchanged` | `exit=2 lock=1 store=unchanged` |
| Every clerk command carries the marker | NEW | `intake: sent unmarked=6` / `build: sent unmarked=2` | `intake: sent unmarked=0` / `build: sent unmarked=0` |
| Intake e2e reaches its end with its run in flight | REGRESSION | `returned=closed stored=closed` | `returned=closed stored=closed` |
| Changelog's last entry records the guard | NEW | `CONTIGUOUS` / `2` | `CONTIGUOUS` / `5` |
| Design doc names marker and run dirs; no prompt copy changes | NEW | `design=0 dirs=0 prompts=0` | `design=1 dirs=1 prompts=0` |
| README opens "Where a human decides" with the marker | NEW | `first=0 command=0 unnamed=0 export=0 rundirs=0` | `first=1 command=1 unnamed=1 export=1 rundirs=1` |
| README: final verifier listed as in flight | NEW | `stale=1 listed=0` | `stale=0 listed=1` |
| README: no "never entered it" | NEW | `bullet=1 stale=1` | `bullet=1 stale=0` |
| No whitespace errors | REGRESSION | `exit=0` | `exit=0` |

What the results mean:
- Every NEW scenario printed its spec's "today" value on base and its expected value on head.
- Every REGRESSION scenario printed its expected value on head, so no REGRESSION scenario needed a base re-run.
- On head, `store=unchanged` and `agents=none` show that a refused write left the target's `.factory/` and `.claude/` byte-for-byte unchanged.
- `marker=0` shows that no stderr or JSON output contains `FACTORY_DISPATCH`.
- `returned=closed` shows that the dispatcher's own marked `run finish` still goes through while its run is in flight.

Gate commands, run on head `74bc15d` from the worktree, each exactly as written:
- `(export HOME=...; git diff --check main...HEAD)` gave exit 0 and no output.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` gave `265 passed in 222.59s`. `TMPDIR` was inherited as `/var/folders/.../T/`, which is outside every repository. That is 254 existing tests plus the 11 new ones.
- The same suite with `FACTORY_DISPATCH=1` exported in the calling shell and `TMPDIR` set to a fresh `/tmp/t0024-suite.XXXXXX` gave `265 passed in 222.52s`. An exported marker therefore changes no result. That run used `TMPDIR=$P uv run ...`, so it is an extra run and not the gate command as written.

TDD record: before the `cli.py` change, the new test file gave `7 failed, 4 passed`. The 4 that passed are the regression cases: reads, a marked write from the root, idle writes, and the throwaway store. After the change it gave `11 passed`.

Side-effect check: during my runs this worktree's `git status` stayed clean apart from my own edits. The live store's log grew from 1192 to 1196 lines. The 4 new lines are another ticket's workflow (T-0025: `run-0235-spec_writer` finished, `run-0237-critic` started), not this run.

## Tests added/changed

- Added `tests/factory/test_live_store_guard.py`, a new file with 11 tests. Each covers one rule of design A.3 or one requirement of the spec.
- Changed `tests/factory/test_instance.py`, both items listed under the spec's Tests to change:
  - `STRIP` gains `"FACTORY_DISPATCH"`. Without it, a runner shell with the marker exported would hide the in-flight rule from every own-store case in the file.
  - `test_composed_input_opens_with_the_instance_context` passes `FACTORY_DISPATCH="1"` to `run compose`. That call stands in for the dispatcher's command on a live store with a triage run in flight, so the in-flight rule would otherwise refuse it.

## Known gaps and uncertainties

- **Status date.** The README status header already said "as of 2026-10-04", which is today, so the bump in "Maintaining this page" left it unchanged.
- **Rejected fixture block.** The classifier refused the GIVEN block when I extracted it from `input.md` and ran it with `sh`, so I wrote the same three files with the Write tool and verified them line by line. A reviewer who wants the literal block run should run it themselves.
- **`_in_flight` and empty ticket files.** `_in_flight` reads every `tickets/*.yaml` on each fenced write. An empty or non-mapping ticket file would make `.get` raise, giving exit 1 instead of a refusal. Every ticket file the harness writes is a mapping, so I added no handling.
- **Unreachable `paths` entry.** `READ_ONLY` includes `("paths", None)` as design A.1 lists it. `main()` handles `paths` before the fence, so that entry is never reached; it does no harm.
- **Sentences other docs could still contradict.** I did not search `docs/design.md` beyond the new paragraph for older sentences that the fence now contradicts. For example, a sentence saying any role may run store commands could now be stale. I found none in the paragraphs next to the new one.
- `factory:` markers added: none.

## Out-of-scope observations

- `test_init_refused_outside_a_git_work_tree` still assumes its temporary directory lies outside every repository. The spec leaves it out of scope. After this change, with `TMPDIR` inside a run's scratch directory, that test would fail because the fence refuses `init`. It would no longer write the live store.
- Several other test files have their own `STRIP` tuple and `cli` helper without `FACTORY_DISPATCH`: `test_store_setup.py`, `test_harness_lock.py`, `test_writing_standard.py` and `test_coding_standard.py`. With the marker exported, the suite still passed in full, so none of them depends on it today. A later own-store test in those files with a run in flight could pass for the wrong reason in a shell that exported the marker.
- In both workflow scripts, `ENV ? ENV + ' ' : ''` is now always true. I left it alone, because removing it would be a drive-by edit.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 18 scenarios printed the expected output before and after, and the gate suite passed 265 of 265 with and without the marker exported. The one uncertainty is that the fixture files were written with the Write tool rather than by the spec's `cat >` block; they were verified line by line.
ESCALATIONS:
- The permission classifier refused the spec's GIVEN fixture block when I extracted it from `input.md` with `sed` and ran it with `sh`. To get past that I wrote the three fixture files with the Write tool, using the spec's exact text, and confirmed with `grep -xF` that every line matches `input.md`. The fixtures used are therefore identical to the spec's. If the auditor wants the GIVEN block itself run, they need to run it or allow it.
