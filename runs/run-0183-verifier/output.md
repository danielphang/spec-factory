Commit: b45462df5b0c9570634b4d6d2074b3054ac296b6 (branch `factory/T-0020.1`, worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0183-verifier/wt`, clean `git status`; `main` = base = `02465fa0356b30d72ce6211ea874e230d5113236`)

How it ran: `uv sync --frozen` in the worktree. The base was a `git archive 02465fa` export into a scratch directory with its own `uv sync --frozen`. The fixture GIVEN block was copied verbatim from the input (lines 322-349) and run once at column 0. Every WHEN was copied verbatim from the sub-ticket into a file, and each ran under bash from the checkout root, inside `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <WHEN>)`. Outputs below are as printed. `$T20` is printed literally because the commands' own `sed` rewrites it.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
1. NEW | park-listed file changed | `state=ready-for-triage reason=None` / `secrets=0` | `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` / `secrets=0` | PASS
2. NEW | deleted or created counts as changed | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live/policies.json, $T20/live/new.json changed during run-0001-triage` | PASS
3. NEW | killed run still compared | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` | PASS
4. NEW | escalate-listed file queued, ticket moves | `state=ready-for-triage reason=None` / `items=None` / `moved=yes` / `secrets=0` | `state=ready-for-triage reason=None` / `items=['tripwire (escalate): $T20/live/pairing.json changed during run-0001-triage']` / `moved=yes` / `secrets=0` | PASS
5. REGRESSION | unchanged files neither park nor escalate | `status=ACCEPT` / `state=ready-for-triage reason=None` / `escalations=0` (run anyway) | same three lines | PASS
6. NEW | `ticket set` dropping the run compares it; an unrelated set does not | `state=ready-for-triage reason=None` twice | `state=ready-for-triage reason=None` / `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` | PASS
7. NEW | substitute HOME not watched | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live.json changed during run-0001-triage`. Afterwards `ls -la ~/.t0020-probe` printed "No such file or directory". | PASS
8. NEW | directory refuses run start | `exit=0 named=no runs=1` | `exit=2 named=yes runs=0` | PASS
9. NEW | baseline kept but not committable | `held=0` / `committed=0` | `held=1` / `committed=0` | PASS
10. REGRESSION | no tripwire key, no new output or file | same as PR (run anyway) | `['confidence', 'escalations', 'ok', 'run_id', 'status']` / `meta.yaml output.md system-prompt.txt ` (trailing space confirmed with `cat -e`) | PASS
11. REGRESSION | suite under a throwaway HOME | not run | `203 passed in 110.55s (0:01:50)`, exit 0. `tests/factory/test_tripwire.py` holds 13 `def test_` functions, all inside that run. | PASS (base: not run)
12. NEW | both scripts check run finish for a park (structural) | `factory/workflows/intake.js 0` / `factory/workflows/build.js 0` | `factory/workflows/intake.js 1` / `factory/workflows/build.js 1`. Each counted line is `if (fin.parked) { log(...); return null }`, right after the `if (!fin.ok) …` line in `runRole` (intake.js uses `TICKET`, build.js uses `ticket`; in build.js it sits after the checker `run cleanup`). Every `await runRole` caller returns on a falsy result without routing (`grep -n -A2 "await runRole"`: intake.js 132/146/160, build.js 127/150/193/250). The checker pair in build.js returns via `checked.some(r => !r)`. `node --check` exits 0 on both files. | PASS
13. NEW | rule 6 format, rule 4 names it | no `heading=yes` / all `no` / `0` / `The check order (rule 1) and` | `heading=yes` / `check=yes principle=yes before=yes after=yes tmp_path=yes module_attr=yes` / `1` / `The check order (rule 1) and` | PASS
14. NEW | design doc, template, README name the tripwire | `design=0 template=0 built=0 resume=0` | `design=1 template=1 built=2 resume=1` | PASS
15. NEW | changelog in order | `contiguous=yes last_names_tripwire=no` | `contiguous=yes last_names_tripwire=yes` (entry 49) | PASS
16. REGRESSION | `git diff --check main...HEAD` | not run | no output, exit 0 | PASS (base: not run)
17. NEW | only declared files change | empty (base = main, so the diff is empty) | exactly the 11 listed paths, sorted, in the listed order | PASS

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0 (criterion 16).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `203 passed`, exit 0. This is criterion 11, which wraps the gate command exactly as written in a throwaway HOME. Per step 4 it counts as that gate's run. I did not repeat it under the real HOME.

Probes (each on scratch instances and stores under a throwaway HOME; every existing listed file is under a `mktemp -d` directory):
- Same bytes rewritten with a new mtime (cp, mv, touch) → `"tripwire": {"park": [], "escalate": []}`, ticket not parked → OK. Detection is by content, not mtime.
- One byte changed at the end of a 30 MB escalate-listed file → `"escalate": ["$T20/live/big"]`, ticket state unchanged → OK.
- Park-listed file `chmod 000` during the run → counted as changed, ticket parked with the tripwire reason → OK (A4).
- Park-listed file unreadable at `run start` → `{"ok": false, "error": "tripwire.park entry '$T20/live/a' ($T20/live/a) cannot be read: Permission denied"}`, exit 2, runs=0 → OK (A1).
- Malformed lists → each refused with exit 2, no run recorded, and a message naming the entry or key: relative `live/a.json`, bare `~`, `park: /x/y` (not a list), `tripwire: [/x/y]` (not a mapping), an extra key `other` → OK.
- `{park: [], escalate: []}`, `tripwire:` (null) and `{}` → finish JSON keys exactly `['confidence', 'escalations', 'ok', 'run_id', 'status']`; run directory holds `meta.yaml output.md system-prompt.txt` only → OK (feature off).
- Ticket parked by hand ("manual hold") during the run, then a park-listed change and a KILLED finish → ticket keeps `reason=manual hold`. An `escalation.queued` event with run `run-0001-triage` and items `["tripwire: $T20/live/a changed during run-0001-triage"]` is logged. No re-park → OK (A4, second bullet).
- Same path in both lists, plus a `~/` entry for a nonexistent file in the account's home (`/Users/dphang/.t0183-nonexistent-probe`, recorded as `absent`, never created) → the path is reported under both lists. It parks once, and `tripwire.changed` lists the path under `park` and `escalate`. The absent→absent `~/` entry is not reported. Store `.gitignore` gains `runs/*/tripwire.yaml` → OK.
- `ticket set T-0001 'in_flight=[]'` after an escalate-listed change, then `run finish` on the same run → the second finish JSON has no `tripwire` field, and the log has exactly 1 `escalation.queued` event. Compared once → OK, as the PR's Known gaps state.
- Store `.gitignore` that already holds the old two lines → the whole block is appended again, so the old lines are duplicated and `runs/*/tripwire.yaml` is added. That is the harmless duplication the plan note allows → OK.

None of the probes shows the fix special-cased to the tested inputs. I read `factory/tripwire.py`. It hashes with `hashlib.file_digest` and expands `~/` through `pwd.getpwuid(os.getuid()).pw_dir`. It writes `compared` before acting. Only paths go into reasons and events.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command ran verbatim on the PR head and on base: each NEW criterion fails on base and passes on the PR, as the spec's verification section predicts. Both gates pass, and ten probes behave as the design says. The workflow-script stop is checked structurally only, because the scripts need the Workflow runtime.
ESCALATIONS: none
