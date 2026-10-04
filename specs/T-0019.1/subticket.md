## T-0019-S1 / Role runs under a throwaway HOME: the running-code wrapper, run_env and the preamble rule
Depends on: none
Parallel-safe: no (S2 also edits docs/design.md and docs/changelog.md)

Parent: T-0019 approved spec v2 (issue #36). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: parts A, B (B1 to B6), E1's S1 clause only, E2, E3, F1. Part E4 says `dev/build-harness.spec.md` does not change, so leave it alone.

Placement note: part B names `factory/compose.py` as the home of the `run_env` reader (B1). The parent's Risk list does not declare `factory/instance.py`. If the reader cannot live in `compose.py` without editing `instance.py`, stop and escalate. Do not edit an undeclared protected path.

Acceptance (each WHEN verbatim from the parent; run the fixture GIVEN block first):
- A triage input's wrapper runs a command under a fresh HOME. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0019-triage.sh && . ${TMPDIR:-/tmp}/t0019-probe.sh)`
  THEN it prints exactly `fresh_home=yes real_home_untouched=yes cache=`
- Planner and implementer inputs carry the wrapper. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && R=$(bin/factory run start --role planner --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && bin/factory run compose $R >/dev/null && echo "planner $(grep -c '^## Running code$' $FACTORY_STATE/runs/$R/input.md)"); (. ${TMPDIR:-/tmp}/t0019-parent.sh && . ${TMPDIR:-/tmp}/t0019-impl.sh && echo "implementer $(grep -c '^## Running code$' $IN)")`
  THEN it prints `planner 1` then `implementer 1`
- The implementer's gate commands come wrapped. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && . ${TMPDIR:-/tmp}/t0019-impl.sh && grep -oF '(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)' $IN; grep -oF '(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)' $IN; echo end)`
  THEN it prints `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`, then `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`, then `end`
- This repo's gate suite passes under a throwaway HOME. REGRESSION.
  WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`
  THEN it exits 0 with no failures, including the new `tests/factory/test_run_isolation.py`
- Variables listed in run_env reach the command. NEW.
  WHEN `(T19=$(mktemp -d); mkdir $T19/inst && cp .factory/instance.yaml .factory/context.md $T19/inst/ && printf "run_env: {T0019_CACHE: '/tmp/t0019 cache'}\n" >> $T19/inst/instance.yaml && export FACTORY_INSTANCE=$T19/inst && . ${TMPDIR:-/tmp}/t0019-triage.sh && . ${TMPDIR:-/tmp}/t0019-probe.sh)`
  THEN it prints exactly `fresh_home=yes real_home_untouched=yes cache=/tmp/t0019 cache`
- run_env cannot set HOME. NEW.
  WHEN `(T19=$(mktemp -d); mkdir $T19/inst && cp .factory/instance.yaml .factory/context.md $T19/inst/ && printf 'run_env: {HOME: /tmp/t0019-home}\n' >> $T19/inst/instance.yaml && export FACTORY_INSTANCE=$T19/inst FACTORY_STATE=$T19/store && printf '# Fixture\n\nThe bot should do the thing.\n' > $T19/req.md && bin/factory ticket new --file $T19/req.md >/dev/null && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && bin/factory run compose $R >/dev/null; echo "exit=$? input=$([ -f $FACTORY_STATE/runs/$R/input.md ] && echo written || echo absent)")`
  THEN stderr contains `run_env` and `HOME`, and the last line is `exit=2 input=absent`
- The running-code rule is in every copy and in a run's system prompt. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0019-triage.sh && for f in docs/design.md docs/prompts/00-preamble.md factory/prompts/preamble.md $(dirname $IN)/system-prompt.txt; do echo "$(basename $f) $(grep -cxF 'RUNNING CODE' $f) $(grep -cxF -e '- Run every test, script or prototype with HOME set to a fresh' $f) $(grep -cxF -e '  run anything that could write a protected path outside the' $f)"; done)`
  THEN it prints `design.md 1 1 1`, `00-preamble.md 1 1 1`, `preamble.md 1 1 1` and `system-prompt.txt 1 1 1`
- The preamble block and its copies stay identical. REGRESSION.
  WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## Shared preamble \(every agent\)$/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/00-preamble.md && diff docs/prompts/00-preamble.md factory/prompts/preamble.md && echo SAME`
  THEN it prints `SAME`
- The README describes the wrapper and run_env. NEW.
  WHEN `grep -cF "Every role's input carries a wrapper that runs a command with a fresh temporary HOME, and the repo's check commands come already wrapped." README.md; grep -cF 'so it still finds that cache from inside the fresh temporary HOME.' README.md; grep -c 'run_env' README.md`
  THEN it prints `1`, then `1`, then a number of 1 or more
- The design doc and the instance template name run_env. NEW.
  WHEN `grep -c 'run_env' docs/design.md factory/instance.template.yaml`
  THEN both counts are 1 or more
- The changelog records the change in order. NEW.
  WHEN `grep -cE '^[0-9]+\. After issue #36 \(2026-10-04\)' docs/changelog.md; awk '/^[0-9]+\. /{n++; if ($1+0 != n) bad=1} END{print (bad?"GAP":"CONTIGUOUS")}' docs/changelog.md`
  THEN it prints `1` then `CONTIGUOUS`, and the entry carries the S1 clause from parent E1
- The change adds no whitespace errors. REGRESSION.
  WHEN `git diff --check main...HEAD; echo "exit=$?"`
  THEN it prints only `exit=0`
- Intermediate check: only declared files change, and no existing test changes. NEW.
  WHEN `git diff --name-only main...HEAD | sort`
  THEN it prints exactly these files: `README.md`, `docs/changelog.md`, `docs/design.md`, `docs/prompts/00-preamble.md`, `factory/compose.py`, `factory/instance.template.yaml`, `factory/prompts/preamble.md`, `tests/factory/test_run_isolation.py`

Tests to change: none. The new file is `tests/factory/test_run_isolation.py`.
Protected paths: harness `factory/compose.py`, `factory/instance.template.yaml`, `factory/prompts/preamble.md`; generated `docs/prompts/00-preamble.md`. The preamble is an agent prompt, and part A asks for that edit.
Out of scope:
- Parts C, D and F2, and E1's S2 clause: they belong to T-0019-S2.
- `factory/subtickets.py`, `factory/prompts/planner.md`, `docs/prompts/04-planner.md`.
- `factory/instance.py`, `.factory/**` (including `run_env` for either instance, which is an Operator step), `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `dev/build-harness.spec.md`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.
- Removing the temporary directories the wrapper leaves behind.

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: the approved spec v2 of T-0019 (issue #36), in this run's input and the T-0019 spec store.

The parent marks itself NEEDS-SPLIT and names two seams (design.md, "Size and seams"). This plan keeps those two seams as they are: S1 for the throwaway-HOME wrapper, S2 for the plan field lines. The faults share no code, so neither sub-ticket depends on the other. A defect in one does not hold the other back, which is what the parent asks for. Both edit `docs/design.md` and `docs/changelog.md`, so neither is parallel-safe and the harness builds them one at a time. S1 is listed first, but nothing makes it merge first.

Shared notes for both sub-tickets:
- Fixtures. Most scenarios below need the four fixture scripts written by the GIVEN block of the first scenario in the parent's `specs/role-run-isolation/spec.md` ("A triage input's wrapper runs a command under a fresh HOME"). Run that block once, verbatim, at column 0, before running any scenario. S2 needs it too: its plan-parsing scenarios source `t0019-parent.sh`. Run every command from the root of your worktree, after `uv sync --frozen`.
- Changelog (parent E1). One entry for both sub-tickets, numbered after the last entry (47 on `main` at `1c5f6a7`), opening `<n>. After issue #36 (2026-10-04):`, placed after the last numbered entry and before `Declined:`. When you start, check `docs/changelog.md` on `main`. If no `After issue #36` entry is there, add it with your own clause only. If the other sub-ticket has already merged it, add your clause to that same entry and do not add a number.
- Running tests. Run the suite and any probe the way this change will require: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Never run tests with the real `HOME`.
