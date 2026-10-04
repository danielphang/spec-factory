Commit: 2630f7559958db1d1f398839c6c227a0aa35caec

This is the parent-close check for T-0023: every scenario of the pinned v2 spec was run on `main` after all four sub-tickets merged.
Base is 1ab9540c9f5f53b505d2d7d8d8942438a71bc5e9. That is the last `main` commit before the first merge, 2e61b85 (T-0023.1).

How I ran it:
- PR: the given worktree `run-0218-verifier/wt`, detached at 2630f75, after `uv sync --frozen`. `git status` was clean before and after.
- Base: a clone in `scratch/base`, checked out at 1ab9540, after `uv sync --frozen`.
- The GIVEN block was extracted from input.md, and `diff` against the spec text printed nothing, so it is byte-identical. It was run once per checkout.
- Each WHEN was extracted verbatim into `scratch/when/w01..w25.sh` and run with `bash -c` from the checkout root. Each run used the fresh-HOME wrapper.
- TMPDIR stayed at the system default under `/var/folders`, which is outside every repository and instance.
- node v24.14.0.
- Raw outputs are in `scratch/pr.out`, `scratch/base.out`, `scratch/pr-w20.out`, `scratch/gate.out` and `scratch/gate2.out`.

Per criterion (NEW/REGRESSION | scenario | base | PR | result):
- NEW | A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling | `exit=2 parked pr=0` / `ruling=missing` / `in_input=0` | `exit=0 ready-for-implementer pr=0` / `ruling=kept` / `in_input=1` | PASS
- REGRESSION | A ruling on a critic ESCALATE still returns the ticket to the critic | `exit=0 ready-for-critic` (run in the batch) | `exit=0 ready-for-critic` | PASS
- NEW | A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list | `exit=2 parked` / `in_input=0 listed=0` | `exit=0 ready-for-planner` / `in_input=1 listed=2` | PASS
- NEW | A re-plan is refused while a sub-ticket is not merged | `names=0` / `parked spec-v1.yaml ` | `names=1` / `parked spec-v1.yaml ` | PASS
- NEW | A redispatch after a killed reviewer keeps the verifier's passing rows | `kept: ` / `set aside: ci.yaml reviewer.yaml verifier.yaml ` | `kept: ci.yaml verifier.yaml ` / `set aside: reviewer.yaml ` | PASS
- NEW | A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval | `kept: ` / `set aside: ci.yaml reviewer.yaml verifier.yaml ` | `kept: reviewer.yaml ` / `set aside: ci.yaml verifier.yaml ` | PASS
- NEW | A later plan's sub-tickets take the next free ids and may depend on a merged sibling | `"ready": []` only | `"id": "T-0001.3"` / `"depends_on": ["T-0001.2"]` / `"ready": ["T-0001.3"]` | PASS
- REGRESSION | A plan that reuses an existing sub-ticket id is refused and writes nothing | `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml ` (run in the batch) | same | PASS
- NEW | A refused archive or sub-ticket add parks with the refusal text | `park: archive: ` / `start: planner` / `park: harness-bug: subticket add: ` | `park: archive: no spec store (factory init not run)` / `start: planner` / `park: harness-bug: subticket add: ST-2: no Depends on line` | PASS
- NEW | A refused run start during intake parks with the refusal text | `start: triage` / `park: harness-bug: run start triage: ` | `start: triage` / `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage` | PASS
- NEW | A command that prints no JSON parks with its exit code | `park: archive: ` | `park: archive: exit 1, no JSON on stdout` | PASS
- NEW | A redispatched sub-ticket runs only the checker whose row was set aside | `start: reviewer` / `start: verifier` / `park: stub stop` | `start: reviewer` / `park: stub stop` | PASS
- REGRESSION | After an implementer run both checkers run | `start: implementer` / `start: reviewer` / `start: verifier` / `park: stub stop` (run in the batch) | same | PASS
- NEW | Run records in a store pass whitespace checks and other store files do not | `runs=2` / `other=2` | `runs=0` / `other=2` | PASS
- NEW | A run start adds the whitespace rule to an existing store | `rule=0` | `rule=1` | PASS
- NEW | init refuses to create an instance on a throwaway store and writes nothing | `exit=0 instance=written store=written names_state=0` | `exit=2 instance=none store=none names_state=1` | PASS
- NEW | A missing briefing refuses the compose with exit 2 | `exit=1 input=none names_context=1` | `exit=2 input=none names_context=1` | PASS
- NEW | Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory | `state=0 instance=0 repo=0` | `state=1 instance=1 repo=1` | PASS
- REGRESSION | An absolute FACTORY_STATE is used as given | `absolute=1` (run in the batch) | `absolute=1` | PASS
- NEW | The harness suite passes with an uncommitted harness edit | `23 failed, 192 passed in 229.59s (0:03:49)` | `254 passed in 248.12s (0:04:08)` | PASS
- REGRESSION | The uncommitted-edit refusal still holds on an instance's own store | `exit=2` / `has uncommitted changes:` (run in the batch) | `exit=2` / `has uncommitted changes:` | PASS
- NEW | The changelog records the change in order | `50 CONTIGUOUS` / `0` | `51 CONTIGUOUS` / `9` | PASS
- NEW | The README describes the new resolve verbs | `replan=0 gap=1` | `replan=1 gap=0` | PASS
- NEW | The README says relative paths resolve from the caller's directory | `0` | `1` | PASS
- REGRESSION | The change adds no whitespace errors | `exit=0` (empty range; run in the batch) | `exit=0` | PASS

Every NEW scenario fails on base with the exact output that verification.md predicts for "today", and passes on the PR. No NEW scenario passes on both checkouts. No scenario fails for a reason other than the one the spec states.

The suite scenario's `/tmp/t0023-suite.*` directory was removed both times. The one `/tmp/t0023-suite.g5G5PW` left on disk dates from 08:28, before this run.

Gate suite: PASS
- `git diff --check main...HEAD` exited 0. On a parent close HEAD is `main`, so this range is empty (see ESCALATIONS).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `254 passed in 189.89s (0:03:09)` and exited `rc=0`. It ran on the clean worktree. An earlier run printed `254 passed in 215.62s`, but my capture lost its exit code, so I ran it again.

Probes (all run on the PR worktree, through the wrapper):
- `resolve T-0001 --replan` on a parked parent with no sub-tickets → `--replan applies to a parent with sub-tickets; T-0001 has none`, exit 2. Only `spec-v1.yaml` is in approvals, so no ruling was written → OK
- `--replan` on a parent that is not parked (`ready-for-parent-verify`) → `--replan applies to a parked parent; T-0001 is ready-for-parent-verify` → OK
- `--ruling` on a `NEEDS-HUMAN from implementer` park → `use --answer` refusal, and the ticket stays parked → OK
- Two BLOCKED park and ruling cycles on one sub-ticket → `ruling-1.md` and `ruling-2.md`, the round stays `pr: 0`, and both resolves exit 0 → OK. I did not probe a round that was not 0.
- A third plan after T-0001.3 exists and has merged. It has two items, with `Depends on: T-0001.1, T-0001.3` and an internal ST-1 reference → ids `T-0001.4` and `T-0001.5`, with dependencies `["T-0001.1","T-0001.3"]` and `["T-0001.4"]`. A `Depends on: T-0001.9`, which does not exist, is still refused as "not a sub-ticket of this plan". Numbering follows the store, not the two ids in the scenario → OK
- An existing store `.gitattributes` holding `# mine` and `*.bin binary`, then two `run start`s → both own lines are kept and `runs/** -whitespace` is added once → OK
- A redispatch with all three rows passing → `"superseded": []`, no `superseded-*` directory, and `results show` reports `missing: []` → OK. With `VERIFIED` plus a gate `FAIL` → `ci.yaml` and `verifier.yaml` are set aside together → OK
- build.js with `results show` reporting missing `["ci"]` → only `start: verifier`. Missing `[]` → straight to join with no checker. All three missing → both checkers. A refused `results show` → `park: harness-bug: results show: no head` → OK
- Clerk results with `{"ok": false}`, no `error` field and exit 3 → `park: archive: exit 3, no error text`. intake.js with non-JSON stdout `Traceback boom` and exit 1 → `exit 1, no JSON on stdout` → OK
- Relative paths: `FACTORY_STATE=../st` from `$T/a/b` → `$T/a/st`. `FACTORY_STATE='~/hs'` → `$HOME/hs`. An empty `FACTORY_STATE` falls back to the instance's own store → OK
- `init` with `FACTORY_STATE` naming the target's own `.factory/state` → exit 0 and the full instance is written. Only a different store is refused → OK

STATUS: VERIFIED
CONFIDENCE: high, every scenario ran verbatim on both base and main, each NEW one moved from its documented base output to its expected output, and the probes show behaviour that generalises past the tested inputs.
ESCALATIONS:
- The whitespace gate checks nothing on a parent-close run. The gate `git diff --check main...HEAD` compares `main` with itself here, so its range is empty. Run over the whole parent, `git diff --check 1ab9540 2630f75` exits 2. Every path it reports is a store run record, such as `.factory/state/runs/run-0202-verifier/diff.patch` and `input.md` through `run-0208`. The same range with `.factory/state` excluded exits 0, so the harness code adds no whitespace errors. This is the defect that H3 fixes. The store's `.gitattributes` does not exist yet on `main`, because operator step 1 runs only after the runtime moves to this change. The runtime is the pinned harness checkout that runs tickets. Until the operator does that step and commits the file, whole-range whitespace checks will keep reporting run records. This is not a failure of any criterion here.
