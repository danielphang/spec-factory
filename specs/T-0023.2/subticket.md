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
