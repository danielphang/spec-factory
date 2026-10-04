# Plan for T-0023 (issue #39): eight harness defects from real runs, in four seams

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

## T-0023-S4 / The harness suite runs with an uncommitted harness edit (part G)
Depends on: none
Parallel-safe: no (edits `docs/changelog.md`, which every sibling edits; first in the fixed order)

Parent: T-0023 approved spec v2 (issue #39). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part G (H8), steps G1 to G3, and part J1's S4 clause. Tests and the changelog only; no harness code changes.

Notes for the implementer, checked on `main` at `1ab9540`:
- G1. `tests/factory/clean_harness_cli.py` does not exist yet. The name must not start with `test_`, so pytest does not collect it. It replaces `factory.instance.harness_changes` and nothing else. The lock comparison (design items C.2 and C.3) must still run.
- G2. `tests/factory/test_harness_lock.py`: the `cli` helper is at `:31`. The module docstring lines to replace are `:8-10`. The uncommitted-edit refusal tests run a clone's `bin/factory` (for example the assertion at `:238`). They must keep doing so.
- G3. `tests/factory/test_instance.py`: the `cli` helper is at `:23-26`. Add `import sys`.
- Change no assertion in either file. The intermediate check below enforces this.

Acceptance (each WHEN verbatim from the parent, run through the wrapper from the worktree root):
- The harness suite passes with an uncommitted harness edit. NEW.
  WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
  THEN it prints one line reporting a number of passed tests and no `failed` or `error`
- The uncommitted-edit refusal still holds on an instance's own store. REGRESSION.
  WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
  THEN it prints `exit=2`, then `has uncommitted changes:`
- Intermediate check, the changelog entry exists with this seam's clause. NEW.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
  THEN it prints `51 CONTIGUOUS`, then `1` (the word `uncommitted`). This is the parent's changelog scenario at the count this seam reaches.
- Intermediate check, the two edited test files change no assertion. REGRESSION.
  WHEN `(git diff main...HEAD -- tests/factory/test_harness_lock.py tests/factory/test_instance.py | grep -cE '^[-+][[:space:]]*assert')`
  THEN it prints `0`
- The change adds no whitespace errors. REGRESSION.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`

Tests to change: `tests/factory/test_harness_lock.py` (the `cli` helper and module docstring lines 8-10) and `tests/factory/test_instance.py` (the `cli` helper and one import), as the parent lists them.
Protected paths: none. The parent's Risk list names only harness files, and this seam changes none of them.
Out of scope: the harness-lock refusal itself (`factory/instance.py` `guard`, no change); any switch the production CLI honours; the four `test_instance.py` tests that assume their temporary directory lies outside every repository (parent Out of scope); every other part.

## T-0023-S1 / Resolve verbs: a ruling on a BLOCKED park, and re-plan after a failed parent close (parts A and I)
Depends on: T-0023-S4
Parallel-safe: no (edits `factory/cli.py` `resolve`, `factory/compose.py`, `README.md` and `docs/changelog.md`, which siblings also edit)

Parent: T-0023 approved spec v2 (issue #39). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A (H1), A1 to A3; part I (H9), I1 to I5; part J1's S1 clause; J2; J4 for this merge.

Notes for the implementer, checked on `main` at `1ab9540`:
- A1. `resolve` starts at `factory/cli.py:705`. The `--ruling` branch is `:746-754`. Its refusal text is at `:750`, and the target is chosen at `:751`.
- I3. The `--decision` refusal is at `:709`. The "resolve needs one of" message is at `:785`. The resolve options are defined at `:1129-1133`. Add `--replan` after `--redispatch` and before `--close`, as I3 says.
- I1. `subtickets.parse` is at `factory/subtickets.py:33`. The numbering is the `enumerate(heads, 1)` at `:48`. The "not a sub-ticket of this plan" refusal is at `:84-85`. Update the module docstring.
- I2. `subticket_add` is at `factory/cli.py:392`, and it calls `subtickets.parse` at `:407`. `store.subtickets_of` is at `factory/store.py:214`.
- I4. The planner branch of `compose` is at `factory/compose.py:152`. Add nothing to the planner input when the parent has no sub-tickets. I5 tests that.
- J2. In `README.md`, the Unstick row is at `:317`, the "Gap, as of today" paragraph starts at `:321`, and the status-header date is at `:9`. Read "Maintaining this page" (`:421`) before you edit.
- A3 and I5 are new files, `tests/factory/test_resolve_rulings.py` and `tests/factory/test_replan.py`. Drive them through `bin/factory` on scratch stores (`FACTORY_STATE`), never on an instance's own store, so they pass mid-edit. The suite scenario below checks this.

Acceptance (each WHEN verbatim from the parent, run through the wrapper from the worktree root):
- A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
  THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`
- A ruling on a critic ESCALATE still returns the ticket to the critic. REGRESSION.
  WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
  THEN it prints `exit=0 ready-for-critic`
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
  THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`
- A re-plan is refused while a sub-ticket is not merged. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
  THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)
- A later plan's sub-tickets take the next free ids and may depend on a merged sibling. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
  THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`
- A plan that reuses an existing sub-ticket id is refused and writes nothing. REGRESSION.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
  THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `
- The README describes the new resolve verbs. NEW.
  WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
  THEN it prints `replan=1 gap=0`
- Intermediate check, the changelog entry carries this seam's clause. NEW.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
  THEN it prints `51 CONTIGUOUS`, then `4` (`uncommitted`, plus `BLOCKED`, `--replan` and `next free`).
- Intermediate check, the new test files pass. NEW.
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_resolve_rulings.py tests/factory/test_replan.py`
  THEN it exits 0. The files cover the cases listed in A3 and I5, including a first plan still numbered from `.1` and a first plan's planner input with no sub-ticket section.
- The harness suite passes with an uncommitted harness edit. REGRESSION.
  WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
  THEN it prints one line reporting a number of passed tests and no `failed` or `error`
- The change adds no whitespace errors. REGRESSION.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`

Tests to change: none.
Protected paths: harness: `factory/cli.py`, `factory/subtickets.py`, `factory/compose.py`.
Out of scope: the `--redispatch` branch (T-0023-S2); `init_cmd` and the `context.md` check in `compose` (T-0023-S3); `build.js` (I4: no change); a re-plan while any sub-ticket is not merged; `--amend-spec`; the requester's `parked → planned` edge; keeping the first plan's `plans/<id>.md` and `tasks.md`; the reviewer-ESCALATE route (parent Out-of-scope observations); `docs/design.md` and `dev/build-harness.spec.md` (J5: no change).

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

## T-0023-S3 / Store and instance setup: whitespace rule, no half instance, relative paths (parts C, E and F)
Depends on: T-0023-S2
Parallel-safe: no (edits `factory/cli.py`, `factory/compose.py`, `README.md` and `docs/changelog.md`, which siblings also edit; last in the fixed order)

Parent: T-0023 approved spec v2 (issue #39). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part C (H3), C1 to C3; part E (H6), E1 to E3; part F (H7), F1 to F3; part J1's S3 clause; J3; J4 for this merge.

Notes for the implementer, checked on `main` at `1ab9540`:
- C1. `ensure_gitignore` is at `factory/store.py:56`. Model `ensure_gitattributes` on it.
- C2. `init_cmd` calls `ensure_gitignore` at `factory/cli.py:857`. `run_start` (`:198`) calls it at `:222`, and the tripwire baseline calls it at `:243`. The parent asks for the call beside the one at `:222`, which runs on every start that passes its guards.
- E1. `init_cmd` is at `factory/cli.py:821`. `instance.yaml` is written at `:836`, and `context.md` is written from `:842`. The refusal must come before any write.
- E2. `compose` reads `context.md` at `factory/compose.py:85` with no check.
- F. `caller_cwd()` already exists (`factory/instance.py:38-39`). The raw environment reads to replace are `factory/instance.py:46`, `:72` and `:89`, `factory/store.py:41` and `factory/cli.py:829`.
- E1 refuses only when `instance.yaml` does not exist. `tests/factory/test_instance.py:166-176` runs `init` with `FACTORY_STATE` on a target that already has an instance, so it keeps passing.
- C3, E3 and F3 share the new file `tests/factory/test_store_setup.py`. Use scratch stores, or `init` and `paths`, which the lock exempts, so the file passes mid-edit.
- J3. In `README.md`, the "How the harness finds a target" paragraph is at `:202-204`. The status-header date is at `:9`.
- Do not commit any store's `.gitattributes`. The operator does that after the runtime moves (parent Operator steps).

Acceptance (each WHEN verbatim from the parent, run through the wrapper from the worktree root):
- Run records in a store pass whitespace checks and other store files do not. NEW.
  WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
  THEN it prints `runs=0`, then `other=2`
- A run start adds the whitespace rule to an existing store. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
  THEN it prints `rule=1`
- init refuses to create an instance on a throwaway store and writes nothing. NEW.
  WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
  THEN it prints `exit=2 instance=none store=none names_state=1`
- A missing briefing refuses the compose with exit 2. NEW.
  WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
  THEN it prints `exit=2 input=none names_context=1`
- Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory. NEW.
  WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
  THEN it prints `state=1 instance=1 repo=1`
- An absolute FACTORY_STATE is used as given. REGRESSION.
  WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
  THEN it prints `absolute=1`
- The README says relative paths resolve from the caller's directory. NEW.
  WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
  THEN it prints `1`
- The changelog records the change in order. NEW.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
  THEN it prints `51 CONTIGUOUS`, then `9`
- Intermediate check, the new test file passes. NEW.
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_store_setup.py`
  THEN it exits 0. The file covers the cases listed in C3, E3 and F3.
- The harness suite passes with an uncommitted harness edit. REGRESSION.
  WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
  THEN it prints one line reporting a number of passed tests and no `failed` or `error`
- The change adds no whitespace errors. REGRESSION.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`

Tests to change: none.
Protected paths: harness: `factory/cli.py`, `factory/store.py`, `factory/instance.py`, `factory/compose.py`.
Out of scope: `bin/factory` (no change: it already hands over `FACTORY_CWD`); `.factory/**` including `.factory/state/.gitattributes` (written by the next `run start` after the runtime moves); moving the store off `main`; rewriting committed run records; the four `test_instance.py` tests that assume a temporary directory outside every repository; every other part.

## Coverage map
- A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling → T-0023-S1
- A ruling on a critic ESCALATE still returns the ticket to the critic → T-0023-S1
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list → T-0023-S1
- A re-plan is refused while a sub-ticket is not merged → T-0023-S1
- A redispatch after a killed reviewer keeps the verifier's passing rows → T-0023-S2
- A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval → T-0023-S2
- A later plan's sub-tickets take the next free ids and may depend on a merged sibling → T-0023-S1
- A plan that reuses an existing sub-ticket id is refused and writes nothing → T-0023-S1
- A refused archive or sub-ticket add parks with the refusal text → T-0023-S2
- A refused run start during intake parks with the refusal text → T-0023-S2
- A command that prints no JSON parks with its exit code → T-0023-S2
- A redispatched sub-ticket runs only the checker whose row was set aside → T-0023-S2
- After an implementer run both checkers run → T-0023-S2
- Run records in a store pass whitespace checks and other store files do not → T-0023-S3
- A run start adds the whitespace rule to an existing store → T-0023-S3
- init refuses to create an instance on a throwaway store and writes nothing → T-0023-S3
- A missing briefing refuses the compose with exit 2 → T-0023-S3
- Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory → T-0023-S3
- An absolute FACTORY_STATE is used as given → T-0023-S3
- The harness suite passes with an uncommitted harness edit → T-0023-S4 (NEW); REGRESSION in T-0023-S1, T-0023-S2 and T-0023-S3
- The uncommitted-edit refusal still holds on an instance's own store → T-0023-S4
- The changelog records the change in order → T-0023-S3 (`9`); at partial counts in T-0023-S4 (`1`), T-0023-S1 (`4`) and T-0023-S2 (`6`)
- The README describes the new resolve verbs → T-0023-S1
- The README says relative paths resolve from the caller's directory → T-0023-S3
- The change adds no whitespace errors → every sub-ticket

Every lettered part is covered: A, I and J2 → T-0023-S1; B and D → T-0023-S2; C, E, F and J3 → T-0023-S3; G → T-0023-S4; J1 and J4 → each seam's own clause and README merge date; J5 needs no change.
