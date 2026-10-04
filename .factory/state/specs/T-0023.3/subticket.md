## T-0023-S2 / Dispatcher park reasons and a redispatch that keeps passing rows (parts B and D)
Depends on: T-0023-S1
Parallel-safe: no (edits `factory/cli.py` `resolve` and `docs/changelog.md`, which siblings also edit)

Parent: T-0023 approved spec v2 (issue #39). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B (H2), B1 to B3; part D (H4), D1 to D3; part J1's S2 clause; the `test_shepherd.py` edit under Tests to change.

Notes for the implementer, checked on `main` at `1ab9540`:
- B. `clerk()` is at `factory/workflows/build.js:41-56` and at `factory/workflows/intake.js:50-64`. The two copies are identical today. Make the same edit to both, and change no reason template (B3).
- D1. The `--redispatch` branch is at `factory/cli.py:761-779`, and its comment is at `:762-764`. Create `superseded-<n>/` only when a row moves.
- D2. `buildOne` is at `factory/workflows/build.js:122`. The implementer runs at `:126-131`, and both checkers run in parallel at `:149-155`. `results show` prints `rows` and `missing` (`factory/cli.py:523-524`).
- D3. `tests/factory/test_redispatch_rows.py` is a new file. Use scratch stores.
- The workflow scripts have no suite test (parent Decisions). The four `build-dispatch` scenarios, run under node with the stub clerk, are their only check.

Acceptance (each WHEN verbatim from the parent, run through the wrapper from the worktree root):
- A redispatch after a killed reviewer keeps the verifier's passing rows. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
  THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `
- A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
  THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `
- A refused archive or sub-ticket add parks with the refusal text. NEW.
  WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
  THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`
- A refused run start during intake parks with the refusal text. NEW.
  WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
  THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`
- A command that prints no JSON parks with its exit code. NEW.
  WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
  THEN it prints exactly `park: archive: exit 1, no JSON on stdout`
- A redispatched sub-ticket runs only the checker whose row was set aside. NEW.
  WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
  THEN it prints exactly `start: reviewer`, then `park: stub stop`
- After an implementer run both checkers run. REGRESSION.
  WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
  THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line
- Intermediate check, the changelog entry carries this seam's clause. NEW.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
  THEN it prints `51 CONTIGUOUS`, then `6` (the four words so far, plus `error text` and `redispatch`).
- Intermediate check, the new test file and the edited shepherd test pass, and the shepherd edit stays inside its test. NEW.
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_redispatch_rows.py "tests/factory/test_shepherd.py::test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix"; git diff -U0 main...HEAD -- tests/factory/test_shepherd.py | grep '^@@'`
  THEN pytest exits 0, and every hunk header names lines between 570 and 590 of the old file, the docstring and lines 585 and 587.
- The harness suite passes with an uncommitted harness edit. REGRESSION.
  WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
  THEN it prints one line reporting a number of passed tests and no `failed` or `error`
- The change adds no whitespace errors. REGRESSION.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`

Tests to change: `tests/factory/test_shepherd.py` `test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix`: line 585's expectation, line 587 removed and the docstring wording, as the parent lists them.
Protected paths: harness: `factory/cli.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`.
Out of scope: the `--ruling` and `--replan` branches (T-0023-S1); a `--roles` flag on redispatch; forcing a re-run of a checker whose row passed; the merge rule and `ticket join`; adding node to the suite.

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: the approved spec v2 of T-0023 (issue #39), in this run's input and at `.factory/state/specs/T-0023.md` with its directory `.factory/state/specs/T-0023/`.

Four sub-tickets, one per seam in the parent's design.md table ("Size and seams"). The parent sizes the change at about 665 lines, half of them tests, and names the seams itself. Each seam holds whole items that touch the same code, so each is one reviewable PR that can be rolled back alone. I did not split further: a sub-ticket per lettered part would add three more merges, and every merge makes the next sibling re-verify.

Order. None of the seams needs another seam's code (parent design.md). But every seam edits `docs/changelog.md` entry 51, three of them edit `factory/cli.py` (S1, S2, S3), two edit `factory/compose.py` (S1, S3) and two edit `README.md` (S1, S3). So none is parallel-safe, and I chain them in one fixed order: S4, then S1, then S2, then S3. The `Depends on:` lines express that order, not a code dependency. A fixed order gives each sub-ticket's changelog check one exact expected count. S4 goes first for two reasons:
- After it merges, an implementer can run the harness suite in a worktree that has uncommitted edits. Today 23 tests fail there (parent Evidence, H8).
- The parent's scenario "The harness suite passes with an uncommitted harness edit" then becomes a REGRESSION check for S1, S2 and S3. That catches any new test file of theirs that would break the suite mid-edit, so S4 does not have to repair siblings' tests later.
The cost: if one seam parks, the seams after it wait.

The store numbers sub-tickets in plan order, so `T-0023-S4` becomes `T-0023.1`, `T-0023-S1` becomes `.2`, `T-0023-S2` becomes `.3` and `T-0023-S3` becomes `.4`. The labels keep the parent's seam names.

I checked the parent's anchors on `main` at `1ab9540`. `git diff --stat 67447b1 HEAD -- factory bin tests docs dev README.md agents` prints nothing, so the parent's evidence, taken at `67447b1`, still holds. A few line numbers have moved by one or two; each sub-ticket's notes give the current ones.

Rules for every sub-ticket:
- Run every command from the root of your worktree, after `uv sync --frozen`, through the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`, with `node` on `PATH`.
- Scenarios that name `t0023-parent.sh`, `t0023-closed.sh` or `t0023-wf.mjs` need the GIVEN block of the parent's first scenario, "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (`specs/human-resolution/spec.md`), run once, verbatim, at column 0. It writes the three files under `${TMPDIR:-/tmp}`. Setting `TMPDIR` to your scratch directory is fine (parent verification.md, round 2).
- The suite scenario "The harness suite passes with an uncommitted harness edit" sets its own `TMPDIR` under `/tmp` and removes it. Run it exactly as written.
- Changelog entry 51 is a single line, like entry 50 (`docs/changelog.md:54`). The parent's changelog scenario reads only the line that starts with `51. `, so each seam appends its clause to that same line. Use the clause wording of parent step J1. The first seam to merge (S4) creates the line after entry 50 and before the blank line above `Declined:` (`:56`). It starts with `51. After issue #39 (2026-10-04), a batch of harness defects found in real runs:`.
- New tests go in new files. Edit an existing test only where your "Tests to change" line names it.
