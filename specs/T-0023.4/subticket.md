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
