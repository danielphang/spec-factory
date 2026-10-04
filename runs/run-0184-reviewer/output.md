Commit: b45462df5b0c9570634b4d6d2074b3054ac296b6 (branch `factory/T-0020.1`, one commit on base `02465fa0356b30d72ce6211ea874e230d5113236`; 11 files, +429 / -18)

## What I checked, in the role's order

1. **Test integrity.** `git diff --name-only main...HEAD | sort` prints exactly the 11 paths the sub-ticket lists; the only test file is the new `tests/factory/test_tripwire.py`. No existing test is changed, skipped, weakened or rewritten. The new tests assert exact reasons, exact event lists, exact JSON key sets and the absence of the fixture secrets in store and output; none is loosened to match output.
2. **Correctness.** I read `factory/tripwire.py`, the `run_start`, `run_finish`, `ticket_set` and `ticket_park` changes in `factory/cli.py` (worktree lines 110-126, 182-190, 212-224, 286-331), `store.park_ticket` and `ensure_gitignore` in `factory/store.py`, and the `runRole` edits in both workflow scripts. Then I wrote the spec's two fixture scripts and ran every acceptance WHEN from the worktree under a throwaway `HOME`. Each printed the required output:
   - park: `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` / `secrets=0`; the `run finish` JSON also carried `"tripwire": {"park": [...], "escalate": []}` and `"parked": "<reason>"` (A5).
   - deleted or created: `... $T20/live/policies.json, $T20/live/new.json changed ...`: config order kept, because `write_yaml` uses `sort_keys=False` (`factory/store.py:71`).
   - escalate: `state=ready-for-triage reason=None` / `items=['tripwire (escalate): $T20/live/pairing.json changed during run-0001-triage']` / `moved=yes` / `secrets=0`.
   - `ticket set`: `state=ready-for-triage reason=None` then `state=parked reason=tripwire: ...` (an unrelated set does not compare; dropping the run does).
   - substitute HOME: `state=parked reason=tripwire: $T20/live.json changed during run-0001-triage` (the `~/` entry resolved to the account's home via `pwd.getpwuid`, `factory/tripwire.py:25`).
   - directory: `exit=2 named=yes runs=0`. Baseline: `held=1` / `committed=0`. No key: `['confidence', 'escalations', 'ok', 'run_id', 'status']` / `meta.yaml output.md system-prompt.txt `.
   - structural: `intake.js 1` / `build.js 1`; both lines are `if (fin.parked) { log(...); return null }` right after `if (!fin.ok)`, and every `runRole` caller already returns on `null`. `node --check` passes on both.
   - rule 6: `heading=yes`, all six `yes`, `1`, `The check order (rule 1) and`. Docs: `design=1 template=1 built=2 resume=1`. Changelog: `contiguous=yes last_names_tripwire=yes`.
   Edge cases the spec implies: a file that is unreadable at compare time counts as changed (`tripwire.py:92-94`); `compare` re-reads the ticket from disk after `run_finish` saved it, so the park sees the current record; a run that `run finish` refuses (missing output, already finished) stays in flight and is not compared early; a second comparison of the same run is a no-op because `compared` is set before any action.
3. **Scope.** Only the parent's declared files change. The rule-4 re-wrap in `docs/coding.md` (lines 67-69) is the consequence of the sentence edit part E asks for.
4. **Silent behavior changes.** One, already flagged by the PR's Known gaps: see the NIT below on `.gitignore` duplication.
5. **Security and data safety.** The baseline holds digests only; `secrets=0` on every scenario and the test's `store_text()` check confirm no bytes leak. Refusal messages name the entry as written and expanded, never contents. No destructive operation is added; `park_ticket` is a move of existing code with an added `by` argument.
6. **Protected paths.** Touched: `factory/tripwire.py` (new), `factory/cli.py`, `factory/store.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/instance.template.yaml`. All six are declared in the parent's Risk list and the sub-ticket. Guardrail path `docs/coding.md` is declared under part E. Listed under ESCALATIONS; the merge gate needs a human approval.
7. **Coding standard.** Rule 1: `hashlib.file_digest` is stdlib on the project's `requires-python = ">=3.11"`; the store's `read_yaml`/`write_yaml`/`log_event`/`now`/`Refused` are reused; `content_hash` was rightly not reused (16-hex text hash). Rule 2: the PR names every caller of `ticket_park`, `ensure_gitignore`, `run_start`, `run_finish`, `ticket_set`. Rule 3: no shortcut needing a marker. Rule 5: `parked`, `tripwire`, `park`/`escalate` match the spec's names. Over-building pass: Lean already.
8. **PR description.** What changed glosses "role run" and "instance" at first use and says what changed in words before the lettered detail. Known gaps are honest and I confirmed each (the `.gitignore` duplication, the compared-once JSON, the `catch` path where `park()` ignores a refused `ticket park` and only logs). No finding.

Gate commands, run from the worktree on `b45462d`: `git diff --check main...HEAD` exited 0 with no output; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `203 passed in 180.77s`.

## Findings

- [NIT] factory/store.py:56-58: `ensure_gitignore` still appends the whole `STORE_GITIGNORE` block when any checked line is missing → on this repo's tracked store `.gitignore` (`.factory/state/.gitignore`, which has the two old lines today) and on Nanobot's, the next build-role `run start` after the upgrade rewrites the file with `worktrees/` and `runs/*/wt/` twice. I reproduced it: an old-form `.gitignore` becomes 8 lines with both old lines duplicated. Git honours the duplicates, so nothing leaks; the operator sees one unexpected store-file change in their next commit. The plan note calls this harmless and allows either form, so this is not a request for change. Appending only `missing` would be a one-line fix if the operator prefers a clean diff.
- [NIT] factory/cli.py:323-324 (A5): the spec says the `run finish` JSON gains `tripwire` "when the run had a baseline"; the code adds it only when a comparison happened now. A run already compared by `ticket set in_flight=[]` and then finished prints no `tripwire` field. The implementer's reading (do not print `{"park": [], "escalate": []}` for a comparison that did not run, because that would claim nothing changed) is the safer one and is tested (`test_ticket_set_compares_a_dropped_run_and_not_one_still_in_flight`). Record only; no change requested.

No BLOCKING or SHOULD-FIX findings.

## Out-of-scope observations

- The README's "At any step a role can say it needs a human …" paragraph (worktree lines 105-107) lists what parks a ticket and does not name the tripwire; D3 did not ask for it. The implementer noted the same.
- The parent's two out-of-scope observations still stand: no store-level guard on leaving `parked`, and no page documents recovering a run left in flight.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high, every acceptance command and both gates ran on `b45462d` from the worktree and printed the required output; the workflow-script change is verified by reading and `node --check` only, as the spec's structural scenario allows.
ESCALATIONS:
- Protected paths touched, all declared in the parent's Risk list: harness `factory/tripwire.py` (new), `factory/cli.py`, `factory/store.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/instance.template.yaml`. Guardrail path `docs/coding.md`, declared under part E. The merge gate requires a human approval for these; the code earns APPROVE.
