Sub-ticket: T-0020.1 (parent T-0020, issue #38). Branch `factory/T-0020.1`, head `b45462df5b0c9570634b4d6d2074b3054ac296b6`, one commit on base `02465fa0356b30d72ce6211ea874e230d5113236`. 11 files, +429 / -18.

## What changed

Until now, nothing in the factory noticed when a role run changed one of the operator's live files outside the repository. A role run is one agent call that the harness starts and records. With this change, an instance can list such files under `tripwire` in its `instance.yaml` (the instance is a target repo's `.factory/` directory). A changed file on the `park` list stops the ticket and puts it in the human queue. A changed file on the `escalate` list queues a flagged item for the operator, and the ticket goes on. No event, reason or output names anything but the file's path.

**A. Baseline at run start, comparison when the run ends** (`factory/tripwire.py` new, `factory/cli.py`, `factory/store.py`)
- A1/A2: `tripwire.baseline(cfg)` reads `cfg["tripwire"]`. It returns None when the key is absent or null, or when both lists are empty. Otherwise the key must be a mapping whose only keys are `park` and `escalate`, each a list of strings. A `~/` entry expands with `pwd.getpwuid(os.getuid()).pw_dir`, never `HOME`. Some entries are refused with `store.Refused` (exit 2), and the message names the entry as written and as expanded: an entry that is not absolute, one that exists and is not a regular file, and one that exists and cannot be read. `run_start` calls it before `store.next_run_id`, so a refusal writes nothing. Each file's state is the hex SHA-256 of its bytes (`hashlib.file_digest`), or `absent`.
- A3: after `meta.yaml`, `run_start` calls `store.ensure_gitignore(root)` and writes `runs/<id>/tripwire.yaml` as `{park: {...}, escalate: {...}, compared: null}`. `STORE_GITIGNORE` gains a comment line and `runs/*/tripwire.yaml`. The tuple `ensure_gitignore` checks gains the same line. The two existing lines are unchanged.
- A4: `tripwire.compare(root, rid, tid)` re-hashes the baseline's paths, but only when `compared` is null. A file that cannot be read now counts as changed. The function sets `compared` and returns the changed paths in baseline order. Then:
  - a park-list change on a ticket that is neither parked nor closed parks it, with reason `tripwire: <paths> changed during <run>`, outputs `[<run>]` and history `by: tripwire`;
  - on a ticket already parked or closed, the same reason goes out as an `escalation.queued` event instead;
  - an escalate-list change logs `escalation.queued`, with item `tripwire (escalate): <paths> changed during <run>`;
  - any change also logs `tripwire.changed`.

  The park goes through the new helper `store.park_ticket`. That helper is `ticket_park`'s old body, moved. `ticket_park` now calls it and keeps its own refusal for a `closed` or `parked` ticket.
- A5: `run_finish` calls `compare` after the run is recorded and its events are logged, for both normal and `--status-override KILLED` finishes. When the run has a baseline, the printed JSON gains `tripwire: {park, escalate}`. When the comparison parked the ticket, it also gains `parked: <reason>`.

**B. A run dropped by hand** (`ticket_set`): `ticket_set` notes `in_flight` before applying the assignments. After saving, it compares each run that left the list. When one of them parked the ticket, the JSON gains `parked`.

**C. Workflow stop** (`intake.js`, `build.js`): `runRole` gains `if (fin.parked) { log(...); return null }`, right after the existing `if (!fin.ok) …` line. It uses `TICKET` in intake.js and `ticket` in build.js. In build.js the checker `run cleanup` still runs first. Every caller of `runRole` returns on `null` without routing. I checked this with `grep -n -A2 "await runRole"` over both scripts.

**D. Documents**
- D1: the template gets the commented `tripwire` example after `protected_paths`. `run_env: {}` is untouched.
- D2: a new `**Tripwire on live files.**` paragraph in `docs/design.md`, placed after **What the harness itself owns**. It is prose, so no `docs/prompts/` file changes.
- D3: README gets a **Built** bullet after "Instances and the harness lock", and the resume sentence after "returns it." in "Where a human decides". The status date is already 2026-10-04, today's date.
- D4: changelog entry 49, before `Declined:`, with the required opening text.

**E. `docs/coding.md`**: rule 6, in the page's format, goes before the closing "The check order…" paragraph. In rule 4, "rule 2, 3 or 5" becomes "rule 2, 3, 5 or 6", kept on one line. The two lines after it re-wrapped to stay within the page width.

**F.** `tests/factory/test_tripwire.py` (new, 13 tests).

Callers of the existing functions I changed (coding rule 2), from a grep of `factory/`:
- `ticket_park` is reached only through the CLI parser (`cli.py:1036`) and the workflow scripts' `park()`. Its output is unchanged.
- `ensure_gitignore` is called by `run_start` (new, only when a baseline exists), `_start_build_run` and `init`.
- `run_start`, `run_finish` and `ticket_set` are CLI entry points. Without a `tripwire` key their output is unchanged.

Reuse (coding rule 1): the store's own `read_yaml`, `write_yaml`, `log_event`, `now` and `Refused`, and the standard library's `hashlib.file_digest`. `store.content_hash` does not fit: it hashes text and truncates to 16 hex characters.

## Acceptance results

Every command ran exactly as written under bash, from the worktree root, after `uv sync --frozen` and the fixture GIVEN block. All of them ran under `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`. "Before" means base `02465fa` before any edit. "After" means head `b45462d`.

| Scenario | Kind | Before | After |
|---|---|---|---|
| A changed park-listed file parks the ticket | NEW | `state=ready-for-triage reason=None` / `secrets=0` | `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` / `secrets=0` |
| Deleted or created counts as changed | NEW | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live/policies.json, $T20/live/new.json changed during run-0001-triage` |
| A killed run is still compared | NEW | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` |
| Escalate-listed file queued, ticket moves | NEW | `state=ready-for-triage reason=None` / `items=None` / `moved=yes` / `secrets=0` | `state=ready-for-triage reason=None` / `items=['tripwire (escalate): $T20/live/pairing.json changed during run-0001-triage']` / `moved=yes` / `secrets=0` |
| Unchanged files neither park nor escalate | REGRESSION | (not required) `status=ACCEPT` / `state=ready-for-triage reason=None` / `escalations=0` | same three lines |
| Clearing an abandoned run compares it | NEW | `state=ready-for-triage reason=None` twice | `state=ready-for-triage reason=None` / `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` |
| Substitute HOME not watched | NEW | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live.json changed during run-0001-triage` |
| Directory refuses run start | NEW | `exit=0 named=no runs=1` | `exit=2 named=yes runs=0` |
| Baseline kept but not committable | NEW | `held=0` / `committed=0` | `held=1` / `committed=0` |
| No tripwire key, no new output or file | REGRESSION | (not required) same as after | `['confidence', 'escalations', 'ok', 'run_id', 'status']` / `meta.yaml output.md system-prompt.txt ` |
| Suite under a throwaway HOME | REGRESSION | not run | `203 passed in 103.70s`, exit 0 (171 on the spec's base, plus T-0019's tests, plus 13 new) |
| Both scripts check run finish for a park | NEW | `intake.js 0` / `build.js 0` | `factory/workflows/intake.js 1` / `factory/workflows/build.js 1`; each count is the `if (fin.parked) { log(...); return null }` line inside `runRole` |
| Rule 6 format, rule 4 names it | NEW | no `heading=yes`, all `no`, `0`, `The check order (rule 1) and` | `heading=yes` / `check=yes principle=yes before=yes after=yes tmp_path=yes module_attr=yes` / `1` / `The check order (rule 1) and` |
| Docs name the tripwire | NEW | `design=0 template=0 built=0 resume=0` | `design=1 template=1 built=2 resume=1` |
| Changelog in order | NEW | `contiguous=yes last_names_tripwire=no` | `contiguous=yes last_names_tripwire=yes` |
| No whitespace errors | REGRESSION | exit 0 | no output, exit 0 |
| Only declared files change | NEW | (empty) | exactly the 11 listed paths, sorted |

What the outputs mean:
- `secrets=0`: no store file and no captured command output holds the watched files' contents.
- `named=yes runs=0`: the refusal message names the bad entry, and no run directory was created.
- `held=1 committed=0`: the digest is in exactly one store file, and `git add -A` in the store does not stage it.
- The substitute-HOME probe path `~/.t0020-probe` resolves to the account's home. I confirmed with `ls` that it does not exist there, before and after.

Gate commands, each run from the worktree on `b45462d`:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: run once, as the suite REGRESSION command above, which wraps it exactly as written. Result: `203 passed`, exit 0.

## Tests added/changed

- Added `tests/factory/test_tripwire.py`, 13 tests through `bin/factory`. Each runs on a copy of the suite's fixture instance with a `tripwire` key appended, and on a throwaway store. The tests cover:
  - park; delete and create; killed;
  - escalate, with the ticket still able to transition;
  - unchanged;
  - a park-list change on a ticket that is already parked, which queues an escalation and does not park again;
  - `ticket set`: an unrelated set does not compare, dropping the run compares it, and a later `run finish` does not compare it again;
  - the account home and not `HOME`;
  - directory refusal; bad-list refusal (relative entry, unknown key, non-mapping, non-string);
  - a baseline held once and never staged;
  - no key: output and files unchanged, and no `.gitignore` written;
  - empty lists mean off.

  Every listed file that exists lives under `tmp_path`. The home test lists `~/.tripwire-probe-<uuid>` and asserts first that it does not exist. Before the change, 11 failed and 2 passed: the two backward-compatibility tests.
- Changed: none.

## Known gaps and uncertainties

- The store `.gitignore` gets duplicate lines on existing stores. When a store's `.gitignore` already has the two old lines, the next `ensure_gitignore` appends the whole block again: two old lines plus the new one. Every build-role `run start` calls it. On this repo's tracked store and on Nanobot's, that rewrites `.gitignore` once with the duplicated lines. The plan note calls this harmless, and I kept the whole-block append. Appending only the missing lines would also have been within A3.
- A run compared by `ticket set` is not compared again. If someone later runs `run finish` on that same run, the JSON has no `tripwire` field, because nothing was compared that time. The test covers this. A5 says "when the run had a baseline, add the field"; I read it as "when a comparison happened". I did not print `{"park": [], "escalate": []}`, because that would claim nothing changed.
- An agent call that throws can leave a stale "parked" line in the workflow log. In both scripts the `catch` path runs `run finish --status-override KILLED` and then calls `park(...)` without reading `fin`. If the tripwire parked the ticket in that `run finish`, the follow-up `ticket park` is refused, because the ticket is already parked. The ticket stays parked with the tripwire reason. The script still logs `parked: agent call failed…`. Part C names only the line after `if (!fin.ok)`, so I left this path alone.
- Parallel checker runs can see each other's changes. In build.js the reviewer and verifier run in parallel on one ticket. A change made during one shows up in both comparisons. The second comparison finds the ticket already parked and queues an escalation, as the "during" wording intends.
- The README's status date is already 2026-10-04, today. If the merge lands on a later day, D3 asks for that date.
- The new README **Built** bullet uses the spec's exact text, "It is tested, and has not yet fired on a real ticket." That sits against the README's "Ground truth only above 'Where this can go'" rule, under which a thing appears only after it has run on a real ticket. I followed the approved spec text.
- The workflow scripts were checked by reading them and by `node --check` on each (both exit 0) only. They cannot run here: they need the Claude Code Workflow runtime.
- `factory:` markers added: none.

## Out-of-scope observations

- The README paragraph at lines 105-107 ("At any step a role can say it needs a human … So does running out of rounds, or a run exceeding its budget.") lists what parks a ticket and does not name the tripwire. D3 did not ask for that edit, so I left it.
- Both of the parent's out-of-scope observations still hold:
  - Nothing guards a ticket leaving `parked`. Part C closes that gap only for tripwire parks.
  - Recovery of a run left in flight is undocumented.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command and both gates were run on `b45462d` and printed the required output; the workflow-script change is checked structurally only.
ESCALATIONS: none
