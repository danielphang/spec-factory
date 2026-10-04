## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0150-reviewer/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0150-reviewer/wt` (branch `factory/T-0017.1`, base `0d1cef4a8b6b534e177f16f779a1c6161f69c853`, head `6db43bf1ea50df49b0e56476f66a4ff7be6b69fc`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Sub-ticket T-0017.1

T-0017.1 / Log a standing decision at any ticket state, give the decision log to the spec writer, critic and planner, and ask whether a NEEDS-HUMAN answer is standing
  Parent: T-0017, approved spec v2 (`.factory/state/specs/T-0017/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.
  Depends on: none
  Parallel-safe: yes (it is the only sub-ticket)
  Scope: parts A, B, C, D and E of the parent, all of them.
    - A: `specstore.record_decision(root, tid, text, today=None)` in `factory/specstore.py`, with `archive()` appending its Decisions lines through it and the module docstring (line 6) updated; the `decision add ID TEXT` command in `factory/cli.py` `build_parser()`; `resolve --decision TEXT`, refused before any write unless given with `--answer` or `--close`, logged only after that branch's own refusals pass, and carried in `move()`'s `extra`; event `decision.recorded` with `ticket`, `by`, `line`, `via`.
    - B: `add_decisions()` beside `add_truth()` in `factory/compose.py`, called right after `add_truth()` in the `spec_writer` and `critic` branches and right after the approved spec in the `planner` branch, before its rulings loop. Absent or whitespace-only `decisions.md` adds nothing. Triage and the build roles unchanged.
    - C: the NEEDS-HUMAN item of `## 1. Triage` and the "Open questions stay open" rule of `## 2. Spec writer` in `docs/design.md`, with the exact wording the parent gives; `docs/prompts/01-triage.md` and `docs/prompts/02-spec-writer.md` re-copied verbatim from those blocks; the same edit in `factory/prompts/triage.md` and `factory/prompts/spec_writer.md`, keeping their existing differences (the "Acceptance items describe behaviour" rule and `400` for `{400}`).
    - D: `docs/design.md` line 82 (three writers of `decisions.md`; the planner also receives it), line 97 (closed as applied), the "A question returns to the role that asked" resolution item, and the routing table's "Receives" column for the three rows the parent names; `dev/build-harness.spec.md` lines 193, 211, 314 and 315; `docs/changelog.md` entry `46.` before `Declined:`; `README.md` "Where a human decides" (Unstick row gains `--decision`, new **Record** row), the "Maintaining this page" source-of-truth row for that section, and the status-header date.
    - E: one new file, `tests/factory/test_decision_log.py`, black-box through `bin/factory` on a throwaway `FACTORY_STATE` store, covering the scenarios of parts A and B and the design-block-equals-copy check for §1 and §2.
  Acceptance (all from the parent's `verification.md`; run each WHEN with bash from the root of the checkout under test, exactly as written; `TODAY` is the UTC date at run time):
    - Decision logged against a closed ticket (NEW)
      WHEN `` ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f resolve T-0001 --close >/dev/null; f decision add T-0001 "Lionbot code lives under lionbot/" >/dev/null 2>&1; echo "first=$? state=$(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml)"; f decision add T-0001 "  Second rule  " >/dev/null 2>&1; echo "second=$?"; sed "s/^$(date -u +%F) /TODAY /" $FACTORY_STATE/decisions.md 2>/dev/null; echo "events=$(f log tail -n 50 --event decision.recorded | wc -l | tr -d ' ')"; rm -rf $T ) ``
      THEN exactly `first=0 state=closed`, `second=0`, `TODAY T-0001 Lionbot code lives under lionbot/`, `TODAY T-0001 Second rule`, `events=2`, one per line
    - Unknown ticket, blank text and multi-line text are refused (NEW)
      WHEN `` ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f decision add T-0009 "x" >/dev/null 2>&1; a=$?; f decision add T-0001 "  " >/dev/null 2>&1; b=$?; f decision add T-0001 "$(printf 'one\ntwo')" >/dev/null 2>&1; c=$?; echo "unknown=$a blank=$b multiline=$c lines=$(cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' ')"; f decision add T-0001 "one" >/dev/null 2>&1; echo "valid=$? lines=$(cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' ')"; rm -rf $T ) ``
      THEN exactly `unknown=2 blank=2 multiline=2 lines=0` then `valid=0 lines=1`
    - Answer and close each log a decision (NEW)
      WHEN `` ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; st() { sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml; }; printf '# demo\n\nDo it.\n' > $T/r.md; printf 'Use option B.\n' > $T/a.md; f ticket new --file $T/r.md >/dev/null; f ticket park T-0001 --reason "NEEDS-HUMAN from triage" >/dev/null; f resolve T-0001 --answer $T/a.md --decision "Option B is the standing rule" >/dev/null 2>&1; echo "answer=$? state=$(st) answers=$(grep -c '^## Answer ' $FACTORY_STATE/requests/T-0001.md)"; f resolve T-0001 --close --decision "Closed as a recorded decision" >/dev/null 2>&1; echo "close=$? state=$(st)"; sed "s/^$(date -u +%F) /TODAY /" $FACTORY_STATE/decisions.md 2>/dev/null; rm -rf $T ) ``
      THEN exactly `answer=0 state=ready-for-triage answers=1`, `close=0 state=closed`, `TODAY T-0001 Option B is the standing rule`, `TODAY T-0001 Closed as a recorded decision`, one per line
    - Decision refused alone, with a ruling, and on a second close (NEW)
      WHEN `` ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; st() { sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml; }; n() { cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' '; }; printf '# demo\n\nDo it.\n' > $T/r.md; printf 'Ruling.\n' > $T/r2.md; f ticket new --file $T/r.md >/dev/null; f ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; f resolve T-0001 --decision "x" >/dev/null 2>&1; a=$?; f resolve T-0001 --ruling $T/r2.md --decision "x" >/dev/null 2>&1; echo "alone=$a ruling=$? state=$(st) rulings=$(ls $FACTORY_STATE/approvals/T-0001 2>/dev/null | grep -c ruling) lines=$(n)"; f resolve T-0001 --close --decision "Closed with a rule" >/dev/null 2>&1; echo "close=$? state=$(st) lines=$(n)"; f resolve T-0001 --close --decision "Again" >/dev/null 2>&1; echo "again=$? lines=$(n)"; rm -rf $T ) ``
      THEN exactly `alone=2 ruling=2 state=parked rulings=0 lines=0`, `close=0 state=closed lines=1`, `again=2 lines=1`, one per line
    - Documents describe the new writers (NEW)
      WHEN `` y() { grep -qF "$1" "$2" && echo yes || echo no; }; echo "old_design=$(y 'Only the archive step writes current truth and `decisions.md`' docs/design.md) old_build=$(y 'only `factory archive` (K) writes `openspec/specs/` and `decisions.md`' dev/build-harness.spec.md) design=$(y 'factory decision add' docs/design.md) build=$(y 'factory decision add' dev/build-harness.spec.md) readme=$(y 'factory decision add' README.md) changelog=$(grep -qE '^46\. .*decisions\.md' docs/changelog.md && echo yes || echo no)" ``
      THEN exactly `old_design=no old_build=no design=yes build=yes readme=yes changelog=yes`
    - Spec writer, critic and planner receive the decision log (NEW)
      WHEN `` ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; S=$FACTORY_STATE; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f init >/dev/null 2>&1; mkdir -p $S/openspec/specs/thing $S/specs/T-0001; printf '# thing\n\n## Requirements\n' > $S/openspec/specs/thing/spec.md; printf 'spec\n' > $S/specs/T-0001/v1.md; printf '2026-10-01 T-0009 SENTINEL keep the old format\n' > $S/decisions.md; f ticket set T-0001 spec.version=1 spec.approved_version=1 >/dev/null; go() { f ticket set T-0001 status=$2 'in_flight=[]' >/dev/null; i=$(f run start --role $1 --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); f run compose $i | python3 -c 'import json,sys; print("'$1'", json.load(sys.stdin)["sources"])'; echo "  in_input=$(grep -c SENTINEL $S/runs/$i/input.md)"; }; go triage ready-for-triage; go spec_writer ready-for-spec-writer; go critic ready-for-critic; go planner ready-for-planner; rm -rf $T ) ``
      THEN exactly these eight lines: `triage ['requests/T-0001.md']`, `  in_input=0`, `spec_writer ['requests/T-0001.md', 'openspec/specs/thing/spec.md', 'decisions.md']`, `  in_input=1`, `critic ['specs/T-0001/v1.md', 'openspec/specs/thing/spec.md', 'decisions.md']`, `  in_input=1`, `planner ['specs/T-0001/v1.md', 'decisions.md']`, `  in_input=1`
    - Empty and absent decision logs add no input source (REGRESSION)
      WHEN `` ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; S=$FACTORY_STATE; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f init >/dev/null 2>&1; mkdir -p $S/specs/T-0001; printf 'spec\n' > $S/specs/T-0001/v1.md; f ticket set T-0001 spec.version=1 spec.approved_version=1 >/dev/null; go() { f ticket set T-0001 status=$2 'in_flight=[]' >/dev/null; i=$(f run start --role $1 --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); f run compose $i | python3 -c 'import json,sys; print("'$3' '$1'", json.load(sys.stdin)["sources"])'; }; printf '\n' > $S/decisions.md; go spec_writer ready-for-spec-writer empty; go critic ready-for-critic empty; go planner ready-for-planner empty; rm $S/decisions.md; go spec_writer ready-for-spec-writer absent; go planner ready-for-planner absent; rm -rf $T ) ``
      THEN exactly `empty spec_writer ['requests/T-0001.md']`, `empty critic ['specs/T-0001/v1.md']`, `empty planner ['specs/T-0001/v1.md']`, `absent spec_writer ['requests/T-0001.md']`, `absent planner ['specs/T-0001/v1.md']`, one per line
    - Triage and spec-writer prompts ask about standing decisions (NEW)
      WHEN `` ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; y() { grep -q 'standing decision' "$1" && echo yes || echo no; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; for r in triage:ready-for-triage spec_writer:ready-for-spec-writer; do f ticket set T-0001 status=${r#*:} 'in_flight=[]' >/dev/null; i=$(f run start --role ${r%%:*} --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); echo "${r%%:*} prompt=$(y $FACTORY_STATE/runs/$i/system-prompt.txt)"; done; for c in 01-triage 02-spec-writer; do echo "$c copy=$(y docs/prompts/$c.md)"; done; rm -rf $T ) ``
      THEN exactly `triage prompt=yes`, `spec_writer prompt=yes`, `01-triage copy=yes`, `02-spec-writer copy=yes`, one per line
    - Triage and spec-writer design blocks equal their copies (REGRESSION)
      WHEN `` python3 -c 'import re; d=open("docs/design.md").read(); F="`"*3; [print(h, "SAME" if re.search(r"^## "+re.escape(h)+r"\n.*?^"+F+r"text\n(.*?)^"+F+"$", d, re.M|re.S).group(1)==open("docs/prompts/"+c).read() else "DIFFERENT") for h, c in (("1. Triage","01-triage.md"),("2. Spec writer","02-spec-writer.md"))]' ``
      THEN exactly `1. Triage SAME` then `2. Spec writer SAME`
    - Intermediate checks: none. The gate commands (`git diff --check main...HEAD` and `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, `136 passed` on base) run in every verifier run, and the suite gate covers the new test file. Two parts have no runnable scenario and are left to the reviewer against the parent's text: `archive()` writing through `record_decision` with unchanged output (the existing archive tests in `tests/factory/test_spec_store.py` are the regression guard), and the `decision.recorded` event and `decision` key written by `resolve --decision` into the `resolve-<n>.yaml` record and the ticket history.
  Tests to change: none. The parent's design names the existing exact-source assertions (`tests/factory/test_shepherd.py` lines 48, 54, 69; `tests/factory/test_spec_store.py` lines 60, 66, 71; `tests/factory/test_p0_cli.py` lines 108, 153, 172) and why they stay green: their stores have no `decisions.md` or only the empty one `factory init` creates.
  Protected paths: harness: `factory/cli.py`, `factory/compose.py`, `factory/specstore.py`, `factory/prompts/triage.md`, `factory/prompts/spec_writer.md`; generated: `docs/prompts/01-triage.md`, `docs/prompts/02-spec-writer.md` (re-copied from the changed `docs/design.md` blocks only, never hand-edited). All are declared in the parent's Risk section.
  Out of scope: backfilling past answers (operator step 2, per store); a new triage status; giving the log to triage, implementer, reviewer or verifier; logging a decision from `--ruling`, `--to spec-gate` or `--redispatch` (these refuse `--decision`); any change to what archive writes or when; inferring a decision from an answer file; adding `decision add` to the `FACTORY_KEY` command list in `dev/build-harness.spec.md` line 207; the harness lock, routing rules, merge gate and gate commands; `.factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`; moving the runtime checkout (operator step 1).

## Parent spec (v2, pinned)

=== proposal.md
## Problem

The factory forgets a standing rule that a human sets when answering one of its questions, so later tickets that depend on the rule are written without it. This hurts the AI agents that write, review and plan specs for those later tickets, and the operator, who today copies each such rule by hand into every request it affects.

Some background. The factory is a pipeline of AI agents, each with one fixed role, that turns a written request (a ticket) into merged code. The harness is the code that runs the pipeline and keeps its records. The harness keeps a decision log, `decisions.md`: one file per target repository, holding one dated line per decision, each tagged with the ticket that made it. The log has two gaps.

1. Only one step writes it. That step is archive, which runs when a finished ticket closes. Archive folds the ticket's approved spec into the repository's record of how the system behaves now, and copies the spec's Decisions section into the log. A decision made in any other way is never logged. The common case is a ticket that exists only to get a decision. An agent parks the ticket with a question for a human (the NEEDS-HUMAN status), the human answers, and the ticket closes without building anything. Archive never runs, so the answer stays in that one ticket's request file.
2. No agent receives the log. The harness builds each agent's input from a fixed list of files, and `decisions.md` is not on that list. Three agents need it: the spec writer (writes the spec), the critic (reviews the spec) and the planner (splits an approved spec into pieces that merge separately). Today they see a logged decision only if one of them happens to open the file.

This change does three things. It lets the human log a decision at any point in a ticket's life. It gives the log to those three agents. And it makes the agents' questions to a human ask whether the answer is a standing decision.

The pieces it adds have these names. `factory` is the harness's command line. `resolve` is the existing `factory` command a human runs to unstick a parked ticket: `--answer` answers its question, and `--close` closes it. The change adds a new command, `factory decision add <ticket> "<line>"`, and a new `--decision "<line>"` flag on `resolve --answer` and `resolve --close`; each appends one line to `decisions.md`. Each target keeps its records in a store, a directory of tickets, requests, run inputs and logs. `factory init` is the command that adds the spec tree to a store: the directory of current-truth specs that archive updates, plus an empty `decisions.md`. The new command and flag do not need `factory init` to have run.

## Evidence

Every command below ran from `~/dev/spec-factory` on `main` at `9a48194` (round 1); `main` is now at `98b9b31`, which differs only in `dev/issues.md` (`git diff --stat 9a48194 98b9b31`), so every observation holds. Commands ran against a throwaway store (`FACTORY_STATE` under `mktemp -d`). The live store was not touched.

- No command logs a decision. `bin/factory decision add T-0001 "…"` printed `factory: error: argument cmd: invalid choice: 'decision'` and exited 2. `bin/factory resolve T-0001 --close --decision "…"` printed `factory: error: unrecognized arguments: --decision …` and exited 2. Answering or closing a ticket cannot log what was decided.
- Archive is the only writer. `grep -rn decisions factory/` matches only `factory/specstore.py`. `init` creates an empty file at lines 67-70. `archive` appends at lines 328-333. The docstring at line 6 says "Only `archive` writes current truth and `decisions.md`."
- No agent receives the log. The scenario "Spec writer, critic and planner receive the decision log" (fixture: a store holding one current-truth spec and a `decisions.md` with one line containing `SENTINEL`) printed these input sources today:
  - triage `['requests/T-0001.md']`
  - spec_writer `['requests/T-0001.md', 'openspec/specs/thing/spec.md']`
  - critic `['specs/T-0001/v1.md', 'openspec/specs/thing/spec.md']`
  - planner `['specs/T-0001/v1.md']`

  Each role's input printed `in_input=0`: the logged line reaches none of them.
- The agents' questions do not ask whether an answer is standing. `grep 'standing decision'` finds nothing in the triage or spec-writer system prompt of a started run, or in `docs/prompts/01-triage.md` or `docs/prompts/02-spec-writer.md`. The triage prompt says only "Write the decision as one question with 2-3 concrete options."
- The design states the current rule. `docs/design.md` line 82 says "Only the archive step writes current truth and `decisions.md`." Line 97 says that a parent closed as applied leaves "Current truth and `decisions.md` … not updated". `dev/build-harness.spec.md` line 193 says "only `factory archive` (K) writes `openspec/specs/` and `decisions.md`", and line 315 repeats the closed-as-applied rule.
- The real case, in the Nanobot target's store (read only, `~/dev/nanobot-upstream/.factory/state`). Ticket T-0003 asked only for a decision about where the port's code lives. Its history shows: parked, then `to: ready-for-triage`, `by: dphang`, `resolve: answer`, then `to: closed`, `by: workflow`. Its request file `requests/T-0003.md` says, in Answer 1, "Close it as a recorded decision so that T-0011 (SPEC-06) and T-0013 (BUG-03) build on it." When this request was triaged, after T-0003 had closed, that store's `decisions.md` was 0 bytes (triage's `wc -c`). It has grown since: today `wc -l` prints `4`, all four lines dated `2026-10-04` and tagged `T-0012`, appended by archive when T-0012 closed; `grep -c T-0003` on it prints `0`, so T-0003's decision is still not logged. `requests/T-0011.md` and `requests/T-0013.md` each carry one hand-added paragraph headed "Port decision that binds this ticket (added by the v3.5 driver, 2026-10-04)" (`grep -c` prints `1` for each).
- Who runs `resolve`. No workflow script calls it: `grep -n resolve factory/workflows/*.js` matches nothing. T-0003's history records `by: dphang`. So the human, or the operator's session acting for them, runs `resolve`. The clerk (the small agent a workflow uses to run one store command) never does.
- The suite is green on base: `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `136 passed` (re-run on `98b9b31`: `136 passed in 212.52s`).

## Root cause

- `factory/specstore.py` `archive()` (lines 310-336) is the only code that appends to `decisions.md`. `init()` (lines 55-71) creates the file empty.
- `factory/compose.py` `compose()` (lines 52-169) has no source for `decisions.md`. The spec writer and critic get current truth through `add_truth()` (lines 68-70, called at 81 and 98). The planner gets the approved spec and any ruling (lines 106-112).
- `factory/cli.py` `resolve()` (lines 675-742) and its parser (lines 1075-1082) have no decision argument. No `decision` command exists in `build_parser()`.
- The triage and spec-writer prompt blocks in `docs/design.md` (§1 Triage, §2 Spec writer), their copies in `docs/prompts/01-triage.md` and `02-spec-writer.md`, and the harness prompts `factory/prompts/triage.md` and `spec_writer.md` never ask whether an answer is standing.

## Out of scope

- Backfilling past answers. Each store's operator does that by hand with the new command, if they choose (Operator steps).
- A new triage status.
- Giving the log to triage, implementer, reviewer or verifier. The request names three roles. Triage not seeing standing decisions is noted under Out-of-scope observations.
- Recording a decision from `resolve --ruling`, `--to spec-gate` or `--redispatch`. These refuse `--decision` instead of ignoring it.
- What archive writes and when. Its line format, refusals and current-truth behaviour do not change.
- The harness lock, the routing rules, the merge gate, the gate commands.

## Open questions

none

## Decisions

- When `decisions.md` does not exist, `factory decision add` and `resolve --decision` create it. The decision log does not depend on the spec tree. Rejected: refusing with "no spec store" as archive does. Archive refuses there only because it must apply the spec's changes to the spec tree, and a refusal would leave every store that never ran `factory init` (this repo's among them) with no way to log a decision.
- A logged line has archive's shape, `<YYYY-MM-DD> <ticket id> <text>`, with the UTC date and the text stripped of surrounding whitespace. There is one log format, whichever step writes it.
- The text must be one non-blank line, and the ticket must exist; otherwise the command exits 2 and writes nothing. A line break would break one line per decision.
- A decision may be logged against a ticket in any state, closed included. Closed is where T-0003's decision ended up.
- `--decision` is accepted only with `--answer` or `--close`. With any other `resolve` mode (`--ruling`, which answers an escalation; `--to spec-gate`, which sends the ticket back to the human's spec approval; `--redispatch`, which re-runs the checks), or alone, it exits 2 and writes nothing, so a decision is never silently dropped. It is logged only after that mode's own checks pass: a refused `resolve` writes no decision.
- The human who runs `resolve` decides whether an answer is standing, and passes `--decision`. The harness never infers a decision from the answer file. Rejected: parsing a marker line out of the answer file, which ties a free-text file to the store and silently misses a mistyped marker.
- An empty or whitespace-only `decisions.md` is not given to any role. It carries nothing, and the empty file `factory init` creates would otherwise add an empty section to every input.
- The spec writer and critic get the log right after current truth. The planner gets it right after the approved spec, before any ruling.
- Each logged decision also writes the event `decision.recorded` (ticket, who, the text, and which command logged it) to the harness's append-only event log. When `resolve` logs it, the decision is also kept in the record `resolve` writes for each call and in the ticket's history. The log file itself does not say who decided.

## Risk

Blast radius: every spec writer, critic and planner run in every target whose `decisions.md` is non-empty gets one more input section. In the Nanobot target that is immediate: its log holds four lines (from T-0012's archive), so from the first run after the runtime moves, its spec writer, critic and planner each receive those four lines. This repo has no `decisions.md`, so its runs change only once a decision is logged here. Each decision costs one line of input tokens per run, for those three roles. `resolve` gains an optional flag, and its existing modes behave as before without it. Archive's behaviour does not change.

Protected and guardrail paths this touches:
- harness (`factory/**`): `factory/cli.py`, `factory/compose.py`, `factory/specstore.py`, and the agent prompts `factory/prompts/triage.md` and `factory/prompts/spec_writer.md`. The ticket's part C asks for the prompt change.
- generated (`docs/prompts/**`): `docs/prompts/01-triage.md` and `docs/prompts/02-spec-writer.md`, each re-copied from its changed `docs/design.md` block, never edited by hand.

Also changed (not protected): `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md`, `README.md`, and one new test file under `tests/factory/`. Not touched: `.factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Rollback: move the runtime back to the previous harness revision. Lines already logged stay in `decisions.md`, in the same format archive writes.

## Operator steps

1. The runtime is the separate checkout, `~/dev/spec-factory-harness`, pinned to the harness revision that actually runs tickets; merging this change does not move it. The pre-approval policy (`.factory/answers/queue-preapproval-policy.md`) lets small changes pass the spec gate without you, but keeps your acceptance test for any prompt change before the runtime moves. So, before the runtime moves to this revision, run that test on the prompt change (part C): read the new NEEDS-HUMAN wording in `factory/prompts/triage.md` and `factory/prompts/spec_writer.md`.
2. Optional, per store, after the runtime moves: backfill decisions you want later tickets to see. For the Nanobot store that means running `factory decision add T-0003 "<the decision as one line>"` from `~/dev/nanobot-upstream`, and then deciding whether to remove the hand-added paragraphs in T-0011's and T-0013's requests.

## Out-of-scope observations

- Triage does not receive the log. A triage run can therefore re-ask a question that a standing decision already settled. The request does not ask for this.
- Two other queued requests also change what each role receives from the same function, `compose()` in `factory/compose.py`: #24 (role-specific inputs) and #27 (roles never see a request's attachments). If they are built close together, they will conflict there.
- `dev/build-harness.spec.md` line 207 lists the operator commands that need `FACTORY_KEY`, and this tree does not implement that check. This spec does not add `decision add` to that list.

=== design.md
## Proposed change

**A. Log a decision at any ticket state** (`factory/specstore.py`, `factory/cli.py`).
1. Add `specstore.record_decision(root, tid, text, today=None) -> str`. It strips `text`, raises `store.Refused` when the result is empty or contains a line break, and builds `f"{date} {tid} {text}"` with the UTC date archive uses. It appends that line plus a newline to `root / "decisions.md"`, creating the file and its parent if absent, and returns the line. Make `archive()` append each Decisions line through it (same date, same format), so that one function writes the log. Update the module docstring (line 6): archive is the only writer of current truth, and archive, `decision add` and `resolve --decision` write `decisions.md`.
2. New command `factory decision add ID TEXT` (a `decision` subparser with `add`, positional `id` and `text`). It loads the ticket (an unknown id refuses with `no ticket ID`), with no check on its state, then calls `record_decision`. It logs event `decision.recorded` with `ticket`, `by=_by()`, `line`, `via="decision add"`, and prints `{"ok": true, "id": ..., "decision": <line>}`.
3. `resolve` gets `--decision TEXT`. At the top of `resolve()`, before anything is written: if `--decision` is given without `--answer` or `--close`, refuse with `--decision applies only with --answer or --close`. Also validate the text, by calling the same strip and one-line check before any write, so that a bad text refuses before the answer is appended. In the `--answer` and `--close` branches, once that branch's own refusals have passed, call `record_decision`, log `decision.recorded` with `via="resolve --answer"` or `"resolve --close"`, and pass `{"decision": <line>}` in the `extra` given to `move()`. The line then lands in the ticket history, the `resolve-<n>.yaml` record and the printed result. Without `--decision`, every branch behaves exactly as today.

**B. Give the log to the spec writer, critic and planner** (`factory/compose.py`).
Add an `add_decisions()` beside `add_truth()`. When `root / "decisions.md"` exists and holds non-whitespace text, it adds that file under the heading `Decision log (decisions.md): standing decisions, read-only`, with source `decisions.md`. It adds nothing otherwise. Call it right after `add_truth()` in the `spec_writer` and `critic` branches, and right after the approved spec in the `planner` branch, before the rulings loop. Triage and the build roles are unchanged.

**C. Questions to a human ask whether the answer is standing** (`docs/design.md` §1 and §2 blocks, then copies).
1. `docs/design.md` §1 Triage, step 3, the NEEDS-HUMAN item becomes:
   ```
      - NEEDS-HUMAN: it needs a product, priority, or design call. Write the
        decision as one question with 2-3 concrete options, and ask whether
        the answer is a standing decision that later tickets must follow.
   ```
2. `docs/design.md` §2 Spec writer, the "Open questions stay open" rule becomes:
   ```
   - Open questions stay open. Don't resolve product or design ambiguity
     yourself; list it, and the spec goes to NEEDS-HUMAN. For each open
     question, ask whether the answer is a standing decision that later
     tickets must follow.
   ```
3. Re-copy each changed block verbatim to `docs/prompts/01-triage.md` and `docs/prompts/02-spec-writer.md`. Make the same edit in `factory/prompts/triage.md` and `factory/prompts/spec_writer.md`, keeping their existing differences from the copies: the "Acceptance items describe behaviour" rule, and `400` in place of `{400}`.

**D. Documents** (`docs/design.md`, `dev/build-harness.spec.md`, `docs/changelog.md`, `README.md`).
1. `docs/design.md` line 82: replace "Only the archive step writes current truth and `decisions.md`." with text saying that only archive writes current truth, and that `decisions.md` has three writers: archive, `factory decision add <ticket id> "<line>"` at any ticket state, and `resolve --answer` or `--close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`. Extend the sentence on what the spec writer and critic receive: they and the planner also receive a non-empty `decisions.md`. Line 97: archive appends nothing to `decisions.md` for a parent closed as applied, and the human logs any decision with `factory decision add`. Resolution list, the "A question returns to the role that asked" item: when the answer is a standing decision, the human passes `--decision`. Routing table "Receives": add "the decision log" to the Triage ACCEPT → Spec writer row, the Spec writer READY-FOR-CRITIC → Critic row and the Human spec gate Approved → Planner row.
2. `dev/build-harness.spec.md`: at line 193, replace "only `factory archive` (K) writes `openspec/specs/` and `decisions.md`" with the same three-writer rule, naming `factory decision add`. At line 314, add `--decision TEXT` to the `resolve` synopsis, with its one-line effect and refusals. At line 315, apply line 97's change. Add `decision.recorded` to the event list at line 211.
3. `docs/changelog.md`: entry `46.` before "Declined:", in the existing style. It says why (a decision answered at a park and then closed without archive was lost, from the Nanobot T-0003 case), and what changed: the second writer of `decisions.md`, the three roles that receive it, and the question wording.
4. `README.md`, "Where a human decides": add `--decision "<line>"` to the Unstick row, valid with `--answer` or `--close`. Add a row **Record**: `factory decision add T-n "<line>"`, deciding "that a decision binds later tickets". In "Maintaining this page", the "Where a human decides" source-of-truth row: add "the `decision` subparser" to the arguments it lists, and `… decision add --help` to its re-derive column. Bump the status-header date, per "Maintaining this page".

**E. Tests** (new file `tests/factory/test_decision_log.py`, black-box through `bin/factory` on a `FACTORY_STATE` throwaway store, as `tests/factory/test_spec_store.py` does). Cover the scenarios of parts A and B, and the design-block-equals-copy check for §1 and §2. No existing test changes.

## Tests to change

none. Existing tests that assert exact input sources (`tests/factory/test_shepherd.py` lines 48, 54 and 69; `tests/factory/test_spec_store.py` lines 60, 66 and 71; `tests/factory/test_p0_cli.py` lines 108, 153 and 172) run on stores with no `decisions.md`, or with the empty one `factory init` creates. Decision B adds no source for either.

=== specs/decision-log/spec.md
## ADDED Requirements

### Requirement: A decision can be logged against a ticket in any state
`factory decision add <ticket id> "<text>"` SHALL append one line `<UTC YYYY-MM-DD> <ticket id> <text, stripped>` to the store's `decisions.md`, creating the file when absent, for a ticket in any state, and SHALL log one `decision.recorded` event per line.

#### Scenario: Decision logged against a closed ticket
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f resolve T-0001 --close >/dev/null; f decision add T-0001 "Lionbot code lives under lionbot/" >/dev/null 2>&1; echo "first=$? state=$(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml)"; f decision add T-0001 "  Second rule  " >/dev/null 2>&1; echo "second=$?"; sed "s/^$(date -u +%F) /TODAY /" $FACTORY_STATE/decisions.md 2>/dev/null; echo "events=$(f log tail -n 50 --event decision.recorded | wc -l | tr -d ' ')"; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  first=0 state=closed
  second=0
  TODAY T-0001 Lionbot code lives under lionbot/
  TODAY T-0001 Second rule
  events=2
  ```

### Requirement: A bad decision is refused and writes nothing
`factory decision add` MUST exit 2 and leave `decisions.md` unchanged when the ticket does not exist or the text is blank or spans more than one line.

#### Scenario: Unknown ticket, blank text and multi-line text are refused
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f decision add T-0009 "x" >/dev/null 2>&1; a=$?; f decision add T-0001 "  " >/dev/null 2>&1; b=$?; f decision add T-0001 "$(printf 'one\ntwo')" >/dev/null 2>&1; c=$?; echo "unknown=$a blank=$b multiline=$c lines=$(cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' ')"; f decision add T-0001 "one" >/dev/null 2>&1; echo "valid=$? lines=$(cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' ')"; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  unknown=2 blank=2 multiline=2 lines=0
  valid=0 lines=1
  ```

### Requirement: Answering or closing a ticket can log a decision
`factory resolve <id> --answer F --decision "<text>"` and `factory resolve <id> --close --decision "<text>"` SHALL do what they do without `--decision`, and SHALL also append the decision line in the same format.

#### Scenario: Answer and close each log a decision
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; st() { sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml; }; printf '# demo\n\nDo it.\n' > $T/r.md; printf 'Use option B.\n' > $T/a.md; f ticket new --file $T/r.md >/dev/null; f ticket park T-0001 --reason "NEEDS-HUMAN from triage" >/dev/null; f resolve T-0001 --answer $T/a.md --decision "Option B is the standing rule" >/dev/null 2>&1; echo "answer=$? state=$(st) answers=$(grep -c '^## Answer ' $FACTORY_STATE/requests/T-0001.md)"; f resolve T-0001 --close --decision "Closed as a recorded decision" >/dev/null 2>&1; echo "close=$? state=$(st)"; sed "s/^$(date -u +%F) /TODAY /" $FACTORY_STATE/decisions.md 2>/dev/null; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  answer=0 state=ready-for-triage answers=1
  close=0 state=closed
  TODAY T-0001 Option B is the standing rule
  TODAY T-0001 Closed as a recorded decision
  ```

### Requirement: A decision on a resolve that cannot carry one is refused
`factory resolve` MUST exit 2, write no decision and leave the ticket unchanged when `--decision` is given alone, with `--ruling`, `--to` or `--redispatch`, or with a `--close` or `--answer` that is itself refused.

#### Scenario: Decision refused alone, with a ruling, and on a second close
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; st() { sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml; }; n() { cat $FACTORY_STATE/decisions.md 2>/dev/null | wc -l | tr -d ' '; }; printf '# demo\n\nDo it.\n' > $T/r.md; printf 'Ruling.\n' > $T/r2.md; f ticket new --file $T/r.md >/dev/null; f ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; f resolve T-0001 --decision "x" >/dev/null 2>&1; a=$?; f resolve T-0001 --ruling $T/r2.md --decision "x" >/dev/null 2>&1; echo "alone=$a ruling=$? state=$(st) rulings=$(ls $FACTORY_STATE/approvals/T-0001 2>/dev/null | grep -c ruling) lines=$(n)"; f resolve T-0001 --close --decision "Closed with a rule" >/dev/null 2>&1; echo "close=$? state=$(st) lines=$(n)"; f resolve T-0001 --close --decision "Again" >/dev/null 2>&1; echo "again=$? lines=$(n)"; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  alone=2 ruling=2 state=parked rulings=0 lines=0
  close=0 state=closed lines=1
  again=2 lines=1
  ```

### Requirement: The design documents name every writer of the decision log
`docs/design.md`, `dev/build-harness.spec.md` and `README.md` SHALL name `factory decision add` as a writer of `decisions.md`; the two design documents SHALL no longer say that only archive writes it; and `docs/changelog.md` SHALL carry entry 46 about `decisions.md`.

#### Scenario: Documents describe the new writers
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  y() { grep -qF "$1" "$2" && echo yes || echo no; }; echo "old_design=$(y 'Only the archive step writes current truth and `decisions.md`' docs/design.md) old_build=$(y 'only `factory archive` (K) writes `openspec/specs/` and `decisions.md`' dev/build-harness.spec.md) design=$(y 'factory decision add' docs/design.md) build=$(y 'factory decision add' dev/build-harness.spec.md) readme=$(y 'factory decision add' README.md) changelog=$(grep -qE '^46\. .*decisions\.md' docs/changelog.md && echo yes || echo no)"
  ```
- THEN it prints exactly `old_design=no old_build=no design=yes build=yes readme=yes changelog=yes`

=== specs/role-input/spec.md
## ADDED Requirements

### Requirement: Spec writer, critic and planner receive the decision log
`run compose` SHALL add a non-empty `decisions.md` to the input of the spec writer and the critic right after current truth, and to the planner's right after the approved spec, and SHALL NOT add it to triage's input.

#### Scenario: Spec writer, critic and planner receive the decision log
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; S=$FACTORY_STATE; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f init >/dev/null 2>&1; mkdir -p $S/openspec/specs/thing $S/specs/T-0001; printf '# thing\n\n## Requirements\n' > $S/openspec/specs/thing/spec.md; printf 'spec\n' > $S/specs/T-0001/v1.md; printf '2026-10-01 T-0009 SENTINEL keep the old format\n' > $S/decisions.md; f ticket set T-0001 spec.version=1 spec.approved_version=1 >/dev/null; go() { f ticket set T-0001 status=$2 'in_flight=[]' >/dev/null; i=$(f run start --role $1 --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); f run compose $i | python3 -c 'import json,sys; print("'$1'", json.load(sys.stdin)["sources"])'; echo "  in_input=$(grep -c SENTINEL $S/runs/$i/input.md)"; }; go triage ready-for-triage; go spec_writer ready-for-spec-writer; go critic ready-for-critic; go planner ready-for-planner; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  triage ['requests/T-0001.md']
    in_input=0
  spec_writer ['requests/T-0001.md', 'openspec/specs/thing/spec.md', 'decisions.md']
    in_input=1
  critic ['specs/T-0001/v1.md', 'openspec/specs/thing/spec.md', 'decisions.md']
    in_input=1
  planner ['specs/T-0001/v1.md', 'decisions.md']
    in_input=1
  ```

### Requirement: An empty or absent decision log adds nothing to role input
`run compose` MUST NOT add `decisions.md` to any role's input when the file is absent or holds only whitespace.

#### Scenario: Empty and absent decision logs add no input source
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; S=$FACTORY_STATE; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; f init >/dev/null 2>&1; mkdir -p $S/specs/T-0001; printf 'spec\n' > $S/specs/T-0001/v1.md; f ticket set T-0001 spec.version=1 spec.approved_version=1 >/dev/null; go() { f ticket set T-0001 status=$2 'in_flight=[]' >/dev/null; i=$(f run start --role $1 --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); f run compose $i | python3 -c 'import json,sys; print("'$3' '$1'", json.load(sys.stdin)["sources"])'; }; printf '\n' > $S/decisions.md; go spec_writer ready-for-spec-writer empty; go critic ready-for-critic empty; go planner ready-for-planner empty; rm $S/decisions.md; go spec_writer ready-for-spec-writer absent; go planner ready-for-planner absent; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  empty spec_writer ['requests/T-0001.md']
  empty critic ['specs/T-0001/v1.md']
  empty planner ['specs/T-0001/v1.md']
  absent spec_writer ['requests/T-0001.md']
  absent planner ['specs/T-0001/v1.md']
  ```

=== specs/needs-human-questions/spec.md
## ADDED Requirements

### Requirement: A question to a human asks whether its answer is a standing decision
The triage and spec-writer prompts, as a run receives them and in their `docs/prompts/` copies, SHALL tell the role to ask, with each NEEDS-HUMAN question, whether the answer is a standing decision.

#### Scenario: Triage and spec-writer prompts ask about standing decisions
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  ( H=$PWD; T=$(mktemp -d); export FACTORY_STATE=$T/s PYTHONDONTWRITEBYTECODE=1; f() { "$H/bin/factory" "$@"; }; y() { grep -q 'standing decision' "$1" && echo yes || echo no; }; printf '# demo\n\nDo it.\n' > $T/r.md; f ticket new --file $T/r.md >/dev/null; for r in triage:ready-for-triage spec_writer:ready-for-spec-writer; do f ticket set T-0001 status=${r#*:} 'in_flight=[]' >/dev/null; i=$(f run start --role ${r%%:*} --ticket T-0001 | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_id"])'); echo "${r%%:*} prompt=$(y $FACTORY_STATE/runs/$i/system-prompt.txt)"; done; for c in 01-triage 02-spec-writer; do echo "$c copy=$(y docs/prompts/$c.md)"; done; rm -rf $T )
  ```
- THEN it prints exactly:
  ```
  triage prompt=yes
  spec_writer prompt=yes
  01-triage copy=yes
  02-spec-writer copy=yes
  ```

### Requirement: The triage and spec-writer prompt copies stay verbatim
`docs/prompts/01-triage.md` and `docs/prompts/02-spec-writer.md` MUST each equal the fenced `text` block under its heading in `docs/design.md`.

#### Scenario: Triage and spec-writer design blocks equal their copies
- WHEN this is run with bash from `~/dev/spec-factory`:
  ```
  python3 -c 'import re; d=open("docs/design.md").read(); F="`"*3; [print(h, "SAME" if re.search(r"^## "+re.escape(h)+r"\n.*?^"+F+r"text\n(.*?)^"+F+"$", d, re.M|re.S).group(1)==open("docs/prompts/"+c).read() else "DIFFERENT") for h, c in (("1. Triage","01-triage.md"),("2. Spec writer","02-spec-writer.md"))]'
  ```
- THEN it prints exactly:
  ```
  1. Triage SAME
  2. Spec writer SAME
  ```

=== verification.md
## Acceptance

Run every command with bash from the root of the `~/dev/spec-factory` checkout under test. The fixtures need `python3` and write only under `mktemp -d`; each runs in a subshell, so its `FACTORY_STATE` does not leak. "Today" means `main` at `9a48194`, where every today output below was observed in round 1; `main` has since moved to `98b9b31`, which changes only `dev/issues.md`, and the "Spec writer, critic and planner receive the decision log" and "Documents describe the new writers" commands were re-run there with the same today output. `TODAY` stands for the UTC date when the scenario runs. A run that straddles UTC midnight can print the raw date instead; re-run it. No scenario repeats the gate commands (`git diff --check main...HEAD` and the harness suite, `136 passed` today), because the verifier runs them.

- Decision logged against a closed ticket → NEW. Today it prints `first=2 state=closed`, `second=2`, no decision lines, and `events=0`: `decision` is not a command (`invalid choice: 'decision'`).
- Unknown ticket, blank text and multi-line text are refused → NEW. Today it prints `unknown=2 blank=2 multiline=2 lines=0` then `valid=2 lines=0`: the refusals are argparse's, and the valid add also fails, so no line is ever written.
- Answer and close each log a decision → NEW. Today it prints `answer=2 state=parked answers=0` then `close=2 state=parked`, and no decision lines: `--decision` is an unrecognized argument, so neither the answer nor the close happens.
- Decision refused alone, with a ruling, and on a second close → NEW. Today it prints `alone=2 ruling=2 state=parked rulings=0 lines=0`, `close=2 state=parked lines=0`, `again=2 lines=0`. The first line already matches, only because the flag does not exist. The valid close fails, so the second and third lines differ.
- Documents describe the new writers → NEW. Today it prints `old_design=yes old_build=yes design=no build=no readme=no changelog=no`.
- Spec writer, critic and planner receive the decision log → NEW. Today the triage line matches, but spec_writer, critic and planner lack `'decisions.md'` in their sources, and each prints `in_input=0`.
- Empty and absent decision logs add no input source → REGRESSION. Today it prints exactly the expected five lines, and it must still do so after the change (decision: an empty log is not input).
- Triage and spec-writer prompts ask about standing decisions → NEW. Today all four lines print `no`.
- Triage and spec-writer design blocks equal their copies → REGRESSION. Today both lines print `SAME`. It must still pass after part C edits the blocks and re-copies them.

## Responses

- [BLOCKING] unglossed names in Decisions and Operator steps: FIXED. The Problem now ends with a paragraph that names and glosses `factory`, `resolve` (with `--answer` and `--close`), the new `factory decision add` command and `--decision` flag, the store, the spec tree and `factory init`. Decisions now spell the command and flag in full and gloss `--ruling`, `--to spec-gate`, `--redispatch`, the event log and the `resolve` record. Operator step 1 now opens by saying what the runtime is (the pinned `~/dev/spec-factory-harness` checkout that runs tickets, which a merge does not move) and what the pre-approval policy requires (the operator's acceptance test of any prompt change before the runtime moves), with its path.
- [SHOULD-FIX] Nanobot `decisions.md` no longer 0 bytes: FIXED. Confirmed today: `wc -l` prints `4`, all `2026-10-04 T-0012` lines, and `grep -c T-0003` prints `0`. Evidence now dates the 0-byte reading to triage of this request and states the current contents; Risk now says the Nanobot target's spec writer, critic and planner receive those four lines from the first run after the runtime moves, and this repo's runs change only once a decision is logged here. While editing that bullet I also removed the Nanobot request line numbers, which the briefing says never to copy into a spec; the quoted text and a `grep -c` count replace them.
- [NIT] README "Maintaining this page" derivation row: FIXED. D.4 now adds "the `decision` subparser" to the "Where a human decides" source-of-truth row (README line 446) and `… decision add --help` to its re-derive column.

## PR description (the implementer's output)

Sub-ticket: T-0017.1 (parent T-0017, approved spec v2, `.factory/state/specs/T-0017/v2.md`). Branch `factory/T-0017.1`, commit `6db43bf` on base `0d1cef4`, worktree `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0017.1`.

## What changed

Before this change, the factory lost a standing decision when a human answered a parked ticket's question and then closed the ticket without a build. The decision log, `decisions.md`, is one file per target repository with one dated line per decision. Only archive wrote it, and archive runs only when a built ticket closes. No agent received the log in its input either. Now a human can log a decision at any point in a ticket's life. The spec writer, critic and planner receive the log. Questions to a human ask whether the answer is a standing decision.

**A. Logging a decision** (`factory/specstore.py`, `factory/cli.py`)
- `specstore.decision_text(text)` strips the text. It refuses (exit 2) when the result is blank or spans more than one line. It uses `str.splitlines`, so `\r` and other line breaks count too.
- `specstore.record_decision(root, tid, text, today=None)` appends `<UTC YYYY-MM-DD> <tid> <text>` to `decisions.md` and returns the line. It creates the file and its parent when they are absent, so a store where `factory init` never ran can still log decisions.
- `archive()` now writes each Decisions line through `record_decision`, with the same date and format. A small helper, `_utc_date()`, holds the date expression that `archive` and `record_decision` share. The module docstring (line 6) now names the three writers.
- New command `factory decision add ID TEXT`. It loads the ticket, so an unknown id refuses with `no ticket ID`. It does not check the ticket's state. It logs the event `decision.recorded` with `ticket`, `by`, `line` and `via: "decision add"`, and prints `{"ok": true, "id", "decision": <line>}`.
- `resolve --decision TEXT`. Both checks below run at the top of `resolve()`, before the ticket loads and before any write, including the empty `approvals/<id>/` directory that `resolve` creates:
  - the flag must go with a mode that carries it. Otherwise `resolve` refuses with `--decision applies only with --answer or --close`.
  - the text must be one non-blank line.

  The `--answer` and `--close` branches log the decision only after their own refusals pass. They then log `decision.recorded` (`via: "resolve --answer"` or `"resolve --close"`) and pass `{"decision": <line>}` to `move()`. That puts the line in the ticket history, in the `resolve-<n>.yaml` record and in the printed result. Without `--decision`, every branch behaves as before.

  One case the spec did not spell out: `resolve` runs `--ruling`, `--to` and `--redispatch` ahead of `--close`. So `--ruling F --close --decision x` would have run the ruling and silently dropped the decision. The check refuses that combination too. This follows the spec's rule that a decision is never silently dropped.

**B. The log as input** (`factory/compose.py`)
- `add_decisions()` sits beside `add_truth()`. When `decisions.md` holds any non-whitespace text, it adds the file under the heading `Decision log (decisions.md): standing decisions, read-only`, with source `decisions.md`. Otherwise it adds nothing.
- The spec writer and critic branches call it right after `add_truth()`. The planner branch calls it right after the approved spec, before the rulings loop.
- Triage and the build roles are unchanged.

**C. Prompts**
- In `docs/design.md`, the NEEDS-HUMAN item of §1 Triage and the "Open questions stay open" rule of §2 Spec writer now use the exact wording the parent spec gives.
- `docs/prompts/01-triage.md` and `02-spec-writer.md` were re-copied by a script that extracts each fenced `text` block, not edited by hand.
- `factory/prompts/triage.md` and `spec_writer.md` got the same edit. A `diff` against the copies shows only the two differences they had before: the "Acceptance items describe behaviour" rule, and `400` in place of `{400}`.

**D. Documents**
- `docs/design.md`:
  - line 82 now says only archive writes current truth. It names the three writers of `decisions.md` and their line format. It adds that the spec writer, critic and planner receive a non-empty log.
  - line 97: archive appends nothing for a parent closed as applied. The human logs any decision with `factory decision add`.
  - the resolution item "A question returns to the role that asked" now says the human passes `--decision` when the answer is a standing decision.
  - the routing table's "Receives" column gains the decision log in three rows: Triage ACCEPT, Spec writer READY-FOR-CRITIC, and Human spec gate Approved.
- `dev/build-harness.spec.md`:
  - line 193 states the three-writer rule and what `run compose` gives.
  - line 211 adds `decision.recorded` to the event list.
  - line 314 adds `[--decision TEXT]` to the `resolve` synopsis, with its effect and refusals.
  - a new bullet follows it for `factory decision add ID TEXT`. Line 193 names this command, so its section needs a definition there; the parent did not name the bullet explicitly.
  - the archive bullet (old line 315, now 316) takes the same closed-as-applied change as design.md line 97.
- `docs/changelog.md` gains entry `46.` before `Declined:`.
- `README.md`, "Where a human decides": the Unstick row gains `--decision "<line>"`, valid with `--answer` or `--close`, and there is a new **Record** row. The source-of-truth row for that section names the `decision` subparser and `… decision add --help`. The status-header date stays `2026-10-04`, because that is already today's UTC date (`date -u` printed `Sun Oct  4 06:55:05 UTC 2026`).

**E. Tests**: one new file, `tests/factory/test_decision_log.py`, with 21 tests (described below).

Callers of the changed functions, found by `grep -rn` over `factory/` and `tests/`:
- `specstore.archive` has one caller, `cli.archive_cmd`, at `factory/cli.py:948`.
- `compose.compose` has one caller, `cli.run_compose`, at line 274.
- `resolve` is reached only through its parser, at line 1103.
- `record_decision` is called from `archive` and from the two CLI paths. `decision_text` is called from `record_decision` and from the up-front check in `resolve`.

## Acceptance results

Each WHEN command ran with bash from the worktree root, exactly as written. Before = base `0d1cef4`; after = `6db43bf`.

| Scenario | Label | Before (base) | After |
|---|---|---|---|
| Decision logged against a closed ticket | NEW | `first=2 state=closed` / `second=2` / `events=0` | `first=0 state=closed` / `second=0` / `TODAY T-0001 Lionbot code lives under lionbot/` / `TODAY T-0001 Second rule` / `events=2` |
| Unknown ticket, blank text and multi-line text are refused | NEW | `unknown=2 blank=2 multiline=2 lines=0` / `valid=2 lines=0` | `unknown=2 blank=2 multiline=2 lines=0` / `valid=0 lines=1` |
| Answer and close each log a decision | NEW | `answer=2 state=parked answers=0` / `close=2 state=parked` | `answer=0 state=ready-for-triage answers=1` / `close=0 state=closed` / `TODAY T-0001 Option B is the standing rule` / `TODAY T-0001 Closed as a recorded decision` |
| Decision refused alone, with a ruling, and on a second close | NEW | `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=2 state=parked lines=0` / `again=2 lines=0` | `alone=2 ruling=2 state=parked rulings=0 lines=0` / `close=0 state=closed lines=1` / `again=2 lines=1` |
| Documents describe the new writers | NEW | `old_design=yes old_build=yes design=no build=no readme=no changelog=no` | `old_design=no old_build=no design=yes build=yes readme=yes changelog=yes` |
| Spec writer, critic and planner receive the decision log | NEW | triage `['requests/T-0001.md']`, spec_writer `[…, 'openspec/specs/thing/spec.md']`, critic `[…, 'openspec/specs/thing/spec.md']`, planner `['specs/T-0001/v1.md']`, each `in_input=0` | the expected eight lines exactly: triage unchanged with `in_input=0`; spec_writer, critic and planner each end with `'decisions.md'` and print `in_input=1` |
| Empty and absent decision logs add no input source | REGRESSION | the expected five lines | the expected five lines (unchanged) |
| Triage and spec-writer prompts ask about standing decisions | NEW | all four lines `no` | `triage prompt=yes` / `spec_writer prompt=yes` / `01-triage copy=yes` / `02-spec-writer copy=yes` |
| Triage and spec-writer design blocks equal their copies | REGRESSION | `1. Triage SAME` / `2. Spec writer SAME` | `1. Triage SAME` / `2. Spec writer SAME` |

Every "before" output matches the "today" column of the parent's `verification.md`. Every "after" output matches its THEN exactly.

In the refusal scenario, the first line already matched on base, only because the flag did not exist. The parent spec says so, and the second and third lines still differ on base.

Gates, run from the worktree on `6db43bf`:
- `git diff --check main...HEAD` printed nothing and exited 0 (`main` = `0d1cef4`).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `157 passed in 133.79s`. That is the 136 on base plus the 21 new tests.
- Not a gate: `uv run --frozen ruff check factory tests/factory/test_decision_log.py` printed `All checks passed!`.

## Tests added/changed

Added: `tests/factory/test_decision_log.py`, 21 tests. Like `test_spec_store.py`, they run black-box through `bin/factory` on a throwaway `FACTORY_STATE` store.
- `decision add`:
  - logs against a closed ticket, prints the line and logs two `decision.recorded` events with `via` and a non-empty `by`.
  - appends to an existing log without a spec store.
  - refuses an unknown ticket, and text that is blank, empty, or has `\n` or `\r` (five cases), writing no file and no event.
- `resolve --decision`:
  - `--answer` and `--close` each log a decision. The line appears in `resolve-1.yaml` and `resolve-2.yaml`, in the ticket history and in the events.
  - without the flag, `resolve` writes no `decision` key and no log.
  - the flag is refused alone, and with `--ruling`, `--to spec-gate`, `--redispatch`, or `--ruling` plus `--close`. The ticket file stays byte-for-byte the same, and no ruling or log is written.
  - no decision is logged when the answer or close is itself refused.
  - blank or multi-line text refuses before the answer is appended.
- compose:
  - the spec writer, critic and planner get the log as a source and in their input, under the new heading; triage gets neither.
  - the planner gets the log before a ruling.
  - an absent, empty, `\n`-only or whitespace-only log adds no source for any of the three roles.
- prompts:
  - the triage and spec-writer system prompts of a started run contain "standing decision".
  - the §1 and §2 design blocks contain the phrase and equal their `docs/prompts/` copies.

Before the code for parts A and B, 12 of these failed for the expected reason: `decision` was an invalid argparse choice, `--decision` was not recognised, or `decisions.md` was missing from the sources. Part C was already applied when the tests first ran, so its tests passed on that first run.

Changed: none. The exact-source assertions the parent names stay green because their stores have no `decisions.md`, or only the empty one `factory init` creates. The full suite passes unchanged.

## Known gaps and uncertainties

- **Archive no longer creates an empty log.** Before, archive opened `decisions.md` in append mode even when the proposal had no Decisions lines, which created an empty file. Through `record_decision` it now writes nothing in that case. This shows only in a store where `factory init` ran and `decisions.md` was then deleted. Line format, refusals and current truth are unchanged, and the existing archive tests pass.
- **Archive's "nothing here refuses" still holds, but by argument, not by a test.** `record_decision` can refuse. Archive feeds it lines from `decisions_of()`, which are already stripped, non-blank and single-line: they come out of `splitlines()`, and wrapped lines are joined with a space. So the refusal cannot fire from archive, but no test covers that path.
- **The README describes a command no real ticket has run yet.** Its "Ground truth only" rule says a thing appears only after it has run on a real ticket. The parent spec's part D.4 and its acceptance (`readme=yes`) require the new rows anyway, so I followed the spec.
- **The README Record row is written to the spec, not to its own source-of-truth rule.** The "Where a human decides" row now names `… decision add --help` as the way to re-derive it. That help text exists only in this dev checkout until the runtime moves.
- **The changelog date is the UTC date of this change.** Entry 46 is dated 2026-10-04, the UTC date of this change. The Nanobot ticket it cites closed earlier.
- **The prompt edit still needs your acceptance test.** Before the runtime checkout moves to this revision, read the new NEEDS-HUMAN wording in `factory/prompts/triage.md` and `spec_writer.md`. This is parent Operator step 1, and this ticket cannot do it.
- factory: markers added: none.

## Out-of-scope observations

- Combining `resolve` modes is otherwise unguarded. For example, `--answer F --ruling R` runs only the answer and ignores the ruling, with no refusal. This change guards that only where `--decision` is involved.
- `resolve` creates `approvals/<id>/` before its own refusals run, so a refused `resolve` leaves an empty directory behind. Many refusals predate this ticket. The new `--decision` refusals run before that point and do not add to it.
- The parent's Out-of-scope observations still apply. Triage does not receive the log. Queued requests #24 and #27 also change `compose()`, so building them close to this one may conflict there.

## Responses to findings

None (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command prints its THEN exactly and both gates pass (157 passed); the only behaviour beyond the spec's text is refusing `--ruling … --close --decision`, which its never-drop rule implies.
ESCALATIONS: none

## Diff `0d1cef4a8b6b534e177f16f779a1c6161f69c853...6db43bf1ea50df49b0e56476f66a4ff7be6b69fc`

diff --git a/README.md b/README.md
index 4370608..60a7968 100644
--- a/README.md
+++ b/README.md
@@ -310,7 +310,8 @@ runs from the same runtime. Each target's runner then accepts the new revision b
 |---|---|---|
 | **File** | `factory ticket new --file <abs path>` | that this request is worth a ticket |
 | **Gate** | `factory approve-spec T-n [--edit F]` · `factory request-changes T-n F` · close | the spec's intent, risk declarations, operator steps, "tests to change"; a gate edit becomes a new spec version and is what gets pinned |
-| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated) · `--redispatch` (re-run the checks on the same commit after an outside fix) · `--to spec-gate` · `--close` | an answer, a ruling, a re-check, a re-scope, or closing |
+| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated) · `--redispatch` (re-run the checks on the same commit after an outside fix) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, a re-check, a re-scope, or closing |
+| **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included. It appends one dated line to the target's decision log, `decisions.md`, which the spec writer, critic and planner receive with their input | that a decision binds later tickets |
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
 Gap, as of today: an implementer that reports itself blocked has no `resolve` verb. A plain
@@ -443,7 +444,7 @@ each section comes from:
 | Terms, routing, states | `instance.yaml` (`routing`, `ready_state`); `factory/cli.py` (`ticket transition` guards) | read the files |
 | How a ticket moves | `factory/workflows/intake.js`, `build.js` (the `phase(...)` blocks and the `STATUS` routes); `factory/cli.py` `ticket_join`, `merge_cmd`, `archive_cmd` | read the code; confirm against the last closed ticket's run log in `.factory/state/log/` |
 | Where it runs, lock | `factory/instance.py` (`find`, `guard`), `instance.yaml` (`harness`, `state_dir`) | `~/dev/spec-factory-harness/bin/factory paths` (its `harness_revision` is the last commit touching harness code, not the runtime's HEAD); `cat .factory/harness.lock`, which must equal it |
-| Where a human decides | `factory/cli.py` `build_parser()`: the `approve-spec`, `request-changes`, `resolve`, `--accept-harness` arguments | `~/dev/spec-factory-harness/bin/factory --help`; `… resolve --help` (the runtime, not the dev checkout) |
+| Where a human decides | `factory/cli.py` `build_parser()`: the `approve-spec`, `request-changes`, `resolve`, `--accept-harness` arguments and the `decision` subparser | `~/dev/spec-factory-harness/bin/factory --help`; `… resolve --help`; `… decision add --help` (the runtime, not the dev checkout) |
 | Built / not built | `tests/factory/` (what has a test is built); `dev/issues.md` (what is named and open) | `uv run --frozen pytest -q -p no:cacheprovider tests/factory`; `gh issue list --state open` |
 | Where this can go | `docs/design.md` §Harness, §Routing table | read the design; nothing here comes from the code |
 | Related work and history | `.factory/state/tickets/`, `dev/issues.md`, `docs/changelog.md` | `ls .factory/state/tickets | wc -l`; `git log --oneline -20` |
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index d811724..ec64614 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -190,7 +190,7 @@ history: []
 
 Spec text `specs/<ID>/v<N>.md` (every version the writer returns, with its STATUS/CONFIDENCE/ESCALATIONS trailer removed: the text above its last `STATUS:` line, as item 42 requires); sub-ticket text `specs/<ID>/subticket.md`.
 
-**Spec store** (doc §Harness, Spec store). `factory init` creates `openspec/config.yaml` (`schema: spec-factory`), `openspec/schemas/spec-factory/schema.yaml` (the artifacts of OpenSpec's `spec-driven`, `proposal`, `specs` with `generates: specs/**/*.md`, `design` and `tasks`, plus `verification` with `generates: verification.md` and `requires: [specs]`), an empty `openspec/specs/` and an empty `decisions.md`. Pinning a version (K) splits it on its `=== <path>` lines (the path is the first token after `=== `; text before the first such line is dropped) into `openspec/changes/<ID>/<path>`. A version pinned before `factory init` created `openspec/` has no change folder; its parent's archive refuses (K). A version is **well-formed** when every path is `proposal.md`, `design.md`, `verification.md` or `specs/<capability>/spec.md` with a kebab-case capability, each at most once, with at least one delta part; every delta part has at least one `## ADDED Requirements`, `## MODIFIED Requirements` or `## REMOVED Requirements` heading, and every `### Requirement:` line sits under one of them and has a name unique within its part; and the `## Acceptance` of `verification.md` labels every `#### Scenario:` name of the delta parts exactly once, `NEW` or `REGRESSION`, and labels no other name. Any other version is malformed. Every spec that `approve-spec` or `--amend-spec` pins must be well-formed, so every build case that approves a spec (items 43–53, 60, 61, 64, 77, 83, 84) needs a well-formed four-part `spec_writer-1.md` stub. `verification.md` is the writer's part plus `## Critic rounds`: per critic run of the ticket, oldest first, `round <n> · spec v<N> · <run_id> · <STATUS>` and its findings verbatim. `tasks.md` comes from `factory spec tasks`. No role writes `openspec/` or `decisions.md`, and only `factory archive` (K) writes `openspec/specs/` and `decisions.md`.
+**Spec store** (doc §Harness, Spec store). `factory init` creates `openspec/config.yaml` (`schema: spec-factory`), `openspec/schemas/spec-factory/schema.yaml` (the artifacts of OpenSpec's `spec-driven`, `proposal`, `specs` with `generates: specs/**/*.md`, `design` and `tasks`, plus `verification` with `generates: verification.md` and `requires: [specs]`), an empty `openspec/specs/` and an empty `decisions.md`. Pinning a version (K) splits it on its `=== <path>` lines (the path is the first token after `=== `; text before the first such line is dropped) into `openspec/changes/<ID>/<path>`. A version pinned before `factory init` created `openspec/` has no change folder; its parent's archive refuses (K). A version is **well-formed** when every path is `proposal.md`, `design.md`, `verification.md` or `specs/<capability>/spec.md` with a kebab-case capability, each at most once, with at least one delta part; every delta part has at least one `## ADDED Requirements`, `## MODIFIED Requirements` or `## REMOVED Requirements` heading, and every `### Requirement:` line sits under one of them and has a name unique within its part; and the `## Acceptance` of `verification.md` labels every `#### Scenario:` name of the delta parts exactly once, `NEW` or `REGRESSION`, and labels no other name. Any other version is malformed. Every spec that `approve-spec` or `--amend-spec` pins must be well-formed, so every build case that approves a spec (items 43–53, 60, 61, 64, 77, 83, 84) needs a well-formed four-part `spec_writer-1.md` stub. `verification.md` is the writer's part plus `## Critic rounds`: per critic run of the ticket, oldest first, `round <n> · spec v<N> · <run_id> · <STATUS>` and its findings verbatim. `tasks.md` comes from `factory spec tasks`. No role writes `openspec/` or `decisions.md`. Only `factory archive` (K) writes `openspec/specs/`. `decisions.md` has three writers, each appending `<YYYY-MM-DD> <ID> <line>` (UTC date): `factory archive` (K); `factory decision add ID TEXT` (K), at any ticket state; and `factory resolve ID --answer FILE` or `--close` with `--decision TEXT` (K). `run compose` gives a `decisions.md` that holds any text to the spec writer and critic after current truth, and to the planner after the approved spec.
 
 States: `ready-for-triage`, `waiting-requester`, `ready-for-spec-writer`, `ready-for-critic`, `ready-for-spec-gate`, `ready-for-planner`, `waiting-dependencies`, `ready-for-implementer`, `checks-in-flight`, `ready-for-checks` (after a checker `--redispatch`; only the roles without a row on the current head run), `ready-for-merge`, `merged`, `ready-for-parent-verify` (parent only: every sub-ticket merged, one verifier run on `main` pending), `parked`, `closed`, `running`.
 
@@ -208,7 +208,7 @@ CLI (the **store CLI** of doc §Harness table piece 1 — read, transition, reco
 
 ### C. Audit log and run artifacts (piece 10)
 
-`log/<YYYY-MM>.jsonl` and `runs/<run_id>/{meta.yaml,input.md,system-prompt.txt,output.md}` on `tickets`. Events: `request.created`, `ticket.created`, `ticket.transition`, `run.started`, `run.finished`, `run.killed`, `result.recorded`, `result.stale-discarded`, `approval.recorded`, `merge.refused`, `merge.done`, `escalation.queued`, `reply.sent`, `human.resolved`, `harness-bug`, `spec.exported`, `change.pinned`, `change.archived`. `meta.yaml`: role, ticket, head, base, model, spec_version, budget_usd, resolution, started, finished, wall_s, status, escalations_note, workflow_run_id. Append-only enforced by the hook (F.3). `factory log tail [-n N] [--ticket ID] [--event E]`.
+`log/<YYYY-MM>.jsonl` and `runs/<run_id>/{meta.yaml,input.md,system-prompt.txt,output.md}` on `tickets`. Events: `request.created`, `ticket.created`, `ticket.transition`, `run.started`, `run.finished`, `run.killed`, `result.recorded`, `result.stale-discarded`, `approval.recorded`, `merge.refused`, `merge.done`, `escalation.queued`, `reply.sent`, `human.resolved`, `harness-bug`, `spec.exported`, `change.pinned`, `change.archived`, `decision.recorded`. `meta.yaml`: role, ticket, head, base, model, spec_version, budget_usd, resolution, started, finished, wall_s, status, escalations_note, workflow_run_id. Append-only enforced by the hook (F.3). `factory log tail [-n N] [--ticket ID] [--event E]`.
 
 ### D. Commit-bound results table (piece 6)
 
@@ -311,8 +311,9 @@ No API key in any run: the CLI authenticates from the owner's login. Keys only i
 - `factory approve-spec ID [--version N] [--edit FILE]`: pins `approved_version` (edited text saved as a new version first), copies "Tests to change" and Risk paths into the ticket, `approvals/ID/spec-v<N>.yaml`, writes the pinned version as the change folder (B; event `change.pinned`; exit 2 with nothing written when the version is malformed (B) or a delta does not apply to current truth: an ADDED requirement name already in `openspec/specs/<capability>/spec.md`, or a MODIFIED or REMOVED name not in it), → `ready-for-planner`, and **exports** the pinned text to `knowledge_vault/sanitized_specs/<ID>.md` (`factory export ID`; event `spec.exported`; the export directory is a config key for the later `specs/` → `tickets/` rename).
 - `factory request-changes ID --notes FILE`: `round.spec: 0`, → `ready-for-spec-writer`.
 - `factory approve-pr ID --head SHA` → `approvals/ID/pr-SHA.yaml`; `factory approve-guardrail ID --head SHA` → `approvals/ID/guardrail-SHA.yaml`.
-- `factory resolve ID (--answer FILE | --ruling FILE [--to implementer] [--amend-subticket FILE] [--amend-spec FILE] | --redispatch [--budget USD] | --close | --to spec-gate)` (doc §Routing rules, resolution list): `--answer` on `waiting-requester` or a triage/spec-writer `NEEDS-HUMAN` → appended to `requests/<ID>.md` under `## Answer <n>`, ticket back to the asking role's ready state, with the asking role's previous output (the `output.md` of its most recent finished run on the ticket) added to that role's next input (doc §Routing rules) (CLARIFY and NEEDS-HUMAN are questions: `--ruling` on them → exit 2 `use --answer`); `--ruling` on a park from BLOCKED, a critic ESCALATE or a planner ESCALATE → the emitting role's ready state, **same round**, the ruling in that role's next input; `--ruling` on a PR loop at max rounds, a SPEC-DEFECT or a reviewer ESCALATE (`--to implementer`, the default there) → `round.pr: 0`, ruling becomes findings input, `ready-for-implementer`; `--amend-subticket` replaces `specs/<ID>/subticket.md`; `--amend-spec` writes `specs/<parent>/v<N+1>.md`, re-pins `approved_version` and rewrites the change folder as `approve-spec` does (`## Critic rounds` kept; the same well-formed and applies-to-current-truth checks, exit 2 with nothing re-pinned when FILE fails them), writes `approvals/<parent>/spec-v<N+1>.yaml`, re-exports; in-flight siblings keep the version their `meta.yaml` `spec_version` names (their `input.md` is already written, I.2) and the human decides whether to re-plan; `--redispatch` → the killed role's ready state, round unchanged, and `--budget USD` sets the ticket's `budget_usd`, copied into the redispatched run's `meta.yaml` (recorded, not enforced per agent in v0, E7); `--to spec-gate`; `--close`. `--close` on a sub-ticket also parks its parent (`parked.reason: sub-ticket <ID> closed`), as a parent-close FAILED or SPEC-DEFECT does (H); on a parked parent, `--amend-spec FILE` re-pins the spec and moves the parent to `ready-for-planner` (re-plan: the planner's new sub-tickets take the next free ids under the same parent, merged ones stay `merged`), or `--close` closes the parent and its unmerged sub-tickets (doc §Routing rules). Each writes `approvals/ID/resolve-<n>.yaml`, event `human.resolved`.
-- `factory archive ID` (harness identity; `build.js` runs it on the parent-close VERIFIED, H): (1) appends `## Verifier results` to `openspec/changes/<ID>/verification.md`, one line per verifier row in `results/` for the parent's and its sub-tickets' heads, oldest first, `<head> · <ticket> · <STATUS> · <run_id>`; (2) applies every delta to `openspec/specs/<capability>/spec.md` (created with `# <capability>` and `## Requirements` when absent): ADDED appends the requirement block, MODIFIED replaces the block whose `### Requirement:` name matches, REMOVED deletes it; (3) moves `openspec/changes/<ID>` to `openspec/changes/archive/<YYYY-MM-DD>-<ID>` (UTC date); (4) appends `<YYYY-MM-DD> <ID> <line>` to `decisions.md` per line of `proposal.md`'s `## Decisions` other than `none`. One commit, event `change.archived`. Refusals, each exit 2 with nothing written, checked in this order before (1): no `openspec/` → `no spec store (factory init not run)`; no `openspec/changes/<ID>/` (its spec was pinned before `factory init`) → `<ID> has no change folder to archive`; a delta that does not apply. H parks the parent on each. A park for no spec store or no change folder is resolved by `factory resolve ID --close`, which closes the parent as applied: `openspec/specs/` and `decisions.md` stay unchanged, and if current truth should carry the spec, it is re-intaken as a new ticket (doc §Routing rules, resolution list).
+- `factory resolve ID (--answer FILE | --ruling FILE [--to implementer] [--amend-subticket FILE] [--amend-spec FILE] | --redispatch [--budget USD] | --close | --to spec-gate) [--decision TEXT]` (doc §Routing rules, resolution list): `--answer` on `waiting-requester` or a triage/spec-writer `NEEDS-HUMAN` → appended to `requests/<ID>.md` under `## Answer <n>`, ticket back to the asking role's ready state, with the asking role's previous output (the `output.md` of its most recent finished run on the ticket) added to that role's next input (doc §Routing rules) (CLARIFY and NEEDS-HUMAN are questions: `--ruling` on them → exit 2 `use --answer`); `--ruling` on a park from BLOCKED, a critic ESCALATE or a planner ESCALATE → the emitting role's ready state, **same round**, the ruling in that role's next input; `--ruling` on a PR loop at max rounds, a SPEC-DEFECT or a reviewer ESCALATE (`--to implementer`, the default there) → `round.pr: 0`, ruling becomes findings input, `ready-for-implementer`; `--amend-subticket` replaces `specs/<ID>/subticket.md`; `--amend-spec` writes `specs/<parent>/v<N+1>.md`, re-pins `approved_version` and rewrites the change folder as `approve-spec` does (`## Critic rounds` kept; the same well-formed and applies-to-current-truth checks, exit 2 with nothing re-pinned when FILE fails them), writes `approvals/<parent>/spec-v<N+1>.yaml`, re-exports; in-flight siblings keep the version their `meta.yaml` `spec_version` names (their `input.md` is already written, I.2) and the human decides whether to re-plan; `--redispatch` → the killed role's ready state, round unchanged, and `--budget USD` sets the ticket's `budget_usd`, copied into the redispatched run's `meta.yaml` (recorded, not enforced per agent in v0, E7); `--to spec-gate`; `--close`. `--close` on a sub-ticket also parks its parent (`parked.reason: sub-ticket <ID> closed`), as a parent-close FAILED or SPEC-DEFECT does (H); on a parked parent, `--amend-spec FILE` re-pins the spec and moves the parent to `ready-for-planner` (re-plan: the planner's new sub-tickets take the next free ids under the same parent, merged ones stay `merged`), or `--close` closes the parent and its unmerged sub-tickets (doc §Routing rules). Each writes `approvals/ID/resolve-<n>.yaml`, event `human.resolved`. `--decision TEXT`, valid only with `--answer` or `--close`, also appends `<YYYY-MM-DD> <ID> <TEXT>` to `decisions.md` once that mode's own checks pass, keeps the line as `decision` in the `resolve-<n>.yaml` record and the ticket history, and logs `decision.recorded` (`ticket`, `by`, `line`, `via`); alone, with any other mode, or with blank or multi-line TEXT → exit 2, nothing written.
+- `factory decision add ID TEXT`: appends `<YYYY-MM-DD> <ID> <TEXT>` (UTC date, TEXT stripped) to `decisions.md`, creating it when absent (no `factory init` needed), for a ticket in any state, closed included; event `decision.recorded` with `via: decision add`. An unknown ID, or blank or multi-line TEXT → exit 2, nothing written.
+- `factory archive ID` (harness identity; `build.js` runs it on the parent-close VERIFIED, H): (1) appends `## Verifier results` to `openspec/changes/<ID>/verification.md`, one line per verifier row in `results/` for the parent's and its sub-tickets' heads, oldest first, `<head> · <ticket> · <STATUS> · <run_id>`; (2) applies every delta to `openspec/specs/<capability>/spec.md` (created with `# <capability>` and `## Requirements` when absent): ADDED appends the requirement block, MODIFIED replaces the block whose `### Requirement:` name matches, REMOVED deletes it; (3) moves `openspec/changes/<ID>` to `openspec/changes/archive/<YYYY-MM-DD>-<ID>` (UTC date); (4) appends `<YYYY-MM-DD> <ID> <line>` to `decisions.md` per line of `proposal.md`'s `## Decisions` other than `none`. One commit, event `change.archived`. Refusals, each exit 2 with nothing written, checked in this order before (1): no `openspec/` → `no spec store (factory init not run)`; no `openspec/changes/<ID>/` (its spec was pinned before `factory init`) → `<ID> has no change folder to archive`; a delta that does not apply. H parks the parent on each. A park for no spec store or no change folder is resolved by `factory resolve ID --close`, which closes the parent as applied: `openspec/specs/` stays unchanged and archive appends nothing to `decisions.md` (the human logs any decision with `factory decision add`), and if current truth should carry the spec, it is re-intaken as a new ticket (doc §Routing rules, resolution list).
 
 ### L. Verifier as gate runner (piece 11)
 
diff --git a/docs/changelog.md b/docs/changelog.md
index b07d351..83aba0a 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -47,5 +47,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 43. After issue #23 (2026-10-03), where the operator's review of the overview draft found the same three failures the factory's own outputs show (an unglossed term, a parenthetical holding a second idea, a page that assumed its reader knew the project): a one-page writing standard, `docs/writing.md`, holds eight rules an agent can check in its own output, each with a before-and-after example from the factory's own writing. The shared preamble's OUTPUT block gains one line: every section a person reads follows the standard at `{writing standard}`, a placeholder the harness fills when a run starts with the path of `docs/writing.md` in the harness checkout that runs it; the role-context block also names who reads what the roles write. Critic rubric 6 widens from the Problem section to every human-facing section of a spec (Problem, Evidence, Open questions, Decisions, Operator steps), still BLOCKING on a Problem that does not say what is wrong and for whom or a first paragraph with an unglossed term specific to this system; other departures from the standard are SHOULD-FIX or NIT. The code reviewer gains check 8, whether the operator could read the PR description's What changed and Known gaps, which is SHOULD-FIX, never BLOCKING. The briefing template gains a line naming the reader of the repo's documents.
 44. After issue #20 (2026-10-03), because nothing stopped a coding agent from building more than its ticket needs: a coding standard, `docs/coding.md`, the twin of the writing standard. It opens with a precedence rule (a target repository's own instructions win where they disagree with it) and holds five rules an agent can check in its own output, each with a `Check:` line, the code-design principle it applies and a before-and-after example: reuse before writing, taking the first rung of a check order that holds; grep every caller and fix a shared function once; mark each deliberate shortcut with a `factory:` comment naming its limit and upgrade trigger; tag each over-building review finding; and one name per concept from spec to code. The review tags are `reuse:` (BLOCKING) and `stdlib:`, `native:`, `yagni:` and `delete:` (SHOULD-FIX), and a review pass ends with `net: -N lines possible` or `Lean already.` The implementer's step 4 gains a line pointing to the standard at `{coding standard}`, and the code reviewer's check 7 is replaced by one: its old "Maintainability, only where it will cause real problems" text is gone. The harness fills `{coding standard}` when a run starts, with the path of `docs/coding.md` in the harness checkout that runs it, through the same helper that fills `{writing standard}`, now applied to the role prompt as well as the preamble. The spec writer gains a rule to cut any part the ticket's intent does not need, naming it under Out of scope, and critic rubric 3 makes such a part a finding. The retro's input names the marker ledger, one row per `factory:` comment in the code on the integration branch; this is design only, and the harness code that builds the ledger waits for the ticket that builds the retro. The check order and the tag vocabulary are adapted from ponytail (DietrichGebert/ponytail, MIT).
 45. After issue #31 (2026-10-03), from the T-0013 to T-0015 build timings, where a parent-close run took 13 to 23% of each build and only two of about six test-suite runs per build could change a verdict: a REGRESSION acceptance check runs once, after the change. The implementer runs only the NEW checks before editing, and runs a REGRESSION check on its base only when it fails after the change; the verifier runs a REGRESSION check on base only when it fails on the PR. One gate run per commit: an acceptance check that already ran a gate command exactly as written on the same commit is that gate's run, for the implementer and the verifier. A parent with one sub-ticket closes on that sub-ticket's VERIFIED run when `main` has not moved since it merged, the run checked the merged head against the parent's recorded base, and the sub-ticket's text names every scenario of the parent's pinned spec; the run stands for the parent-close run, `ticket parent-check` reports it as `reuse`, and the close records it as `verified_by`. Every other parent still gets its own parent-close run, and every refusal is kept: a NEW check that does not fail first is a SPEC-DEFECT, a failing REGRESSION check fails the branch, and a gate failure is FAILED. The requested path-scoped gate skip was cut: a correct path list for this repository covers `docs/**`, which would have skipped no suite run in those builds.
+46. After the Nanobot target's T-0003 (2026-10-04), a ticket that existed only to get a decision: the human answered its question about where the port's code lives and closed it, archive never ran, and the decision stayed in that ticket's request, so the operator copied it by hand into the two later requests that depend on it. `decisions.md` gains writers besides archive: `factory decision add <ticket id> "<line>"`, at any ticket state, closed included, and `--decision "<line>"` on `resolve --answer` or `resolve --close`, refused with any other `resolve` mode. Each appends the line in archive's format, `<YYYY-MM-DD> <ticket id> <line>`, creates the file when absent, and logs `decision.recorded`. The spec writer and the critic receive a non-empty `decisions.md` after current truth, and the planner after the approved spec; triage and the build roles do not. Triage's NEEDS-HUMAN question and the spec writer's open questions now ask whether the answer is a standing decision that later tickets must follow. Archive's own output is unchanged.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index ac7d892..76ad2f6 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -79,7 +79,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | `tasks.md` | The sub-tickets and coverage map | Planner |
 | `verification.md` (the artifact the fork adds) | The NEW or REGRESSION label of each scenario and the writer's Responses; every critic round's output; at archive, every verifier result recorded per head for the parent and its sub-tickets | Spec writer (labels, Responses), critic, verifier |
 
-`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth and `decisions.md`. The spec writer and the critic receive every current-truth spec with their input (routing table).
+`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. The spec writer and the critic receive every current-truth spec with their input (routing table). They and the planner also receive `decisions.md` when it holds any text.
 
 **Routing table.** The dispatcher (piece 2) is this table and nothing else. Each row: a STATUS a role emits, what runs next, and what it receives. "Receives" adds to the INPUT the role prompt already declares. Both follow the role-context block (above).
 
@@ -90,28 +90,28 @@ Rules the table relies on:
 - The dispatcher reads a role's trailer by its labels, not by line position. The last `STATUS:` line wins; CONFIDENCE is the next line labelled `CONFIDENCE:` after it, and ESCALATIONS the next line labelled `ESCALATIONS:` after that. Lines between labelled lines are continuation (a wrapped reason, a remark), so a verbose but well-formed verdict routes on its STATUS. A trailer with no CONFIDENCE or no ESCALATIONS line after its last STATUS is a parse failure, which routes as a STATUS not in this table.
 - A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route. An ESCALATIONS line that starts with the word `none` followed by end of line or punctuation (so not `None of …`), with prose after it on that line and nothing below it, is empty for routing, and the prose is kept with the run for audit. A `none` line with further lines below it is a real list, copied verbatim from that line on. Only NEEDS-HUMAN, CLARIFY, BLOCKED, ESCALATE, SPEC-DEFECT, a max-round cutoff, a budget kill (piece 3), a parent-close FAILED, and an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) park the ticket. A parking STATUS from one checker wins over the other's REQUEST-CHANGES or FAILED; both outputs go to the queue.
 - When a human resolves a parked ticket:
-  - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way.
+  - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way. When the answer is a standing decision, the human passes `--decision "<line>"` with the answer, or with the close, so that it lands in `decisions.md`.
   - BLOCKED, a critic ESCALATE, and a planner ESCALATE return to the role that emitted them with the ruling, same round, or the human re-scopes (spec gate or writer round reset) or closes.
   - A spec loop at max rounds goes to the spec gate.
   - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (new sub-tickets under the same parent) or closes the parent.
-  - An archive refused for no change folder or no spec store parks the parent the same way, but its spec never entered the spec store: the human closes the parent as applied. Current truth and `decisions.md` are not updated; if current truth should carry the spec, it is re-intaken as a new ticket.
+  - An archive refused for no change folder or no spec store parks the parent the same way, but its spec never entered the spec store: the human closes the parent as applied. Current truth is not updated, and archive appends nothing to `decisions.md`; the human logs any decision with `factory decision add`. If current truth should carry the spec, it is re-intaken as a new ticket.
   - A PR loop at max rounds, a SPEC-DEFECT, or a reviewer ESCALATE returns to the implementer with the round reset and the human's ruling as findings, or the ticket closes. The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive. There is no merge-gate override. A budget-killed run re-dispatches the same role on the same inputs, same round (the human may raise that run's budget or amend the sub-ticket first), or the ticket closes. In-flight siblings keep the spec version they received; the human decides whether to re-plan.
 
 | From | STATUS | Next | Receives |
 |---|---|---|---|
 | New request | — | Triage | The request, ticket search |
-| Triage | ACCEPT | Spec writer | The ticket; current truth (Spec store), read-only |
+| Triage | ACCEPT | Spec writer | The ticket; current truth (Spec store) and the decision log, read-only |
 | Triage | NEEDS-HUMAN | Human queue | The question |
 | Triage | CLARIFY | Requester, via piece 9; ticket parks until answered | The missing-info list |
 | Triage | REJECT | Closed | — |
-| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic | Spec, repo and current truth read-only; round 2+: prior findings, the writer's responses, previous spec version |
+| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic | Spec, repo, current truth and the decision log read-only; round 2+: prior findings, the writer's responses, previous spec version |
 | Spec writer | NEEDS-HUMAN | Human queue | Open questions |
 | Critic | APPROVE | Human spec gate | Spec + critic output |
 | Critic | REVISE | Spec writer (round +1) if round < {2}, else Human queue | Findings, the spec version they apply to |
 | Critic | ESCALATE | Human queue | Findings |
 | Human queue, or requester (CLARIFY) | Answered (Triage asked) | Triage | The request with the answer, Triage's previous output (the question or missing-info list the answer is for) |
 | Human queue | Answered (Spec writer asked) | Spec writer | The ticket, the answer, the writer's previous output (the spec whose open questions the answer is for) |
-| Human spec gate | Approved | Planner | Approved spec, version pinned |
+| Human spec gate | Approved | Planner | Approved spec, version pinned; the decision log |
 | Human spec gate | Changes requested | Spec writer (round reset) | Human's notes |
 | Planner | PLANNED | Implementer, one run per sub-ticket. Each branches from main at dispatch; a sub-ticket dispatches only after its dependencies merge; parallel-safe ones run concurrently; one marked not parallel-safe dispatches only when no sibling of the same parent is in flight, and no sibling dispatches while it is in flight | Sub-ticket, parent spec, AGENTS.md; push to its own branch only |
 | Planner | ESCALATE | Human queue | Planner output |
@@ -241,7 +241,8 @@ FOR EACH REQUEST
 3. Decide:
    - ACCEPT: the intent is clear and no product decision is needed.
    - NEEDS-HUMAN: it needs a product, priority, or design call. Write the
-     decision as one question with 2-3 concrete options.
+     decision as one question with 2-3 concrete options, and ask whether
+     the answer is a standing decision that later tickets must follow.
    - CLARIFY: key facts are missing. List exactly what's missing.
    - REJECT: duplicate, out of scope, or not actionable. One-line reason.
 4. For ACCEPT: write a title and a 2-5 sentence summary of what the
@@ -303,7 +304,9 @@ RULES
   would pass with a stub. Acceptance never names a test function or an
   internal symbol: those go stale and the verifier can't run them.
 - Open questions stay open. Don't resolve product or design ambiguity
-  yourself; list it, and the spec goes to NEEDS-HUMAN.
+  yourself; list it, and the spec goes to NEEDS-HUMAN. For each open
+  question, ask whether the answer is a standing decision that later
+  tickets must follow.
 - Write the Problem section for the operator who approves the spec at
   the gate, not for the harness builder or the next role. Write it the
   way a design doc is written: for a deeply technical reader who does
diff --git a/docs/prompts/01-triage.md b/docs/prompts/01-triage.md
index 06b73d3..cccd415 100644
--- a/docs/prompts/01-triage.md
+++ b/docs/prompts/01-triage.md
@@ -10,7 +10,8 @@ FOR EACH REQUEST
 3. Decide:
    - ACCEPT: the intent is clear and no product decision is needed.
    - NEEDS-HUMAN: it needs a product, priority, or design call. Write the
-     decision as one question with 2-3 concrete options.
+     decision as one question with 2-3 concrete options, and ask whether
+     the answer is a standing decision that later tickets must follow.
    - CLARIFY: key facts are missing. List exactly what's missing.
    - REJECT: duplicate, out of scope, or not actionable. One-line reason.
 4. For ACCEPT: write a title and a 2-5 sentence summary of what the
diff --git a/docs/prompts/02-spec-writer.md b/docs/prompts/02-spec-writer.md
index 080e7ea..f2a9b2d 100644
--- a/docs/prompts/02-spec-writer.md
+++ b/docs/prompts/02-spec-writer.md
@@ -32,7 +32,9 @@ RULES
   would pass with a stub. Acceptance never names a test function or an
   internal symbol: those go stale and the verifier can't run them.
 - Open questions stay open. Don't resolve product or design ambiguity
-  yourself; list it, and the spec goes to NEEDS-HUMAN.
+  yourself; list it, and the spec goes to NEEDS-HUMAN. For each open
+  question, ask whether the answer is a standing decision that later
+  tickets must follow.
 - Write the Problem section for the operator who approves the spec at
   the gate, not for the harness builder or the next role. Write it the
   way a design doc is written: for a deeply technical reader who does
diff --git a/factory/cli.py b/factory/cli.py
index 2b2bae0..9807d32 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -673,11 +673,24 @@ def request_changes(a, root, cfg):
 
 
 def resolve(a, root, cfg):
+    if a.decision is not None:  # refuse before anything is written, so a decision is never dropped
+        # the branch below that will run: --answer wins, and --close runs only with no other mode
+        if not (a.answer or (a.close and not (a.ruling or a.to or a.redispatch))):
+            raise Refused("--decision applies only with --answer or --close")
+        specstore.decision_text(a.decision)
     t = store.load_ticket(root, a.id)
     st, parked = t["status"], t["parked"] or {}
     reason = parked.get("reason", "")
     d = _approval_dir(root, t["id"])
 
+    def decided(via: str) -> dict:
+        """Log `--decision`, once this mode's own refusals have passed; the `extra` for move()."""
+        if a.decision is None:
+            return {}
+        line = specstore.record_decision(root, t["id"], a.decision)
+        store.log_event(root, "decision.recorded", ticket=t["id"], by=_by(), line=line, via=via)
+        return {"decision": line}
+
     def move(to: str, kind: str, extra: dict) -> None:
         t["status"] = to
         if to != "parked":
@@ -699,7 +712,7 @@ def resolve(a, root, cfg):
         n = req.read_text(encoding="utf-8").count("\n## Answer ") + 1
         with req.open("a", encoding="utf-8") as fh:
             fh.write(f"\n\n## Answer {n}\n\n{Path(a.answer).read_text(encoding='utf-8').rstrip()}\n")
-        move(to, "answer", {"answer": n})
+        move(to, "answer", {"answer": n, **decided("resolve --answer")})
     elif a.ruling:
         if st != "parked" or not reason.startswith("ESCALATE"):
             if st == "parked" and (reason.startswith("NEEDS-HUMAN") or "CLARIFY" in reason):
@@ -737,11 +750,18 @@ def resolve(a, root, cfg):
     elif a.close:
         if st == "closed":
             raise Refused(f"{t['id']} is already closed")
-        move("closed", "close", {})
+        move("closed", "close", decided("resolve --close"))
     else:
         raise Refused("resolve needs one of --answer F | --ruling F | --to spec-gate | --redispatch | --close")
 
 
+def decision_add(a, root, cfg):
+    t = store.load_ticket(root, a.id)  # any state, closed included
+    line = specstore.record_decision(root, t["id"], a.text)
+    store.log_event(root, "decision.recorded", ticket=t["id"], by=_by(), line=line, via="decision add")
+    out({"ok": True, "id": t["id"], "decision": line})
+
+
 # ----- spec store (doc §Harness, Spec store; part K) ----------------------------------
 
 def _git_toplevel(cwd: Path) -> Path:
@@ -1079,7 +1099,13 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("--to")
     p.add_argument("--redispatch", action="store_true")
     p.add_argument("--close", action="store_true")
+    p.add_argument("--decision", metavar="TEXT", help="with --answer or --close: also log TEXT to decisions.md")
     p.set_defaults(fn=resolve)
+    dc = sp.add_parser("decision").add_subparsers(dest="sub", required=True)
+    p = dc.add_parser("add", help="log one standing decision against a ticket in any state")
+    p.add_argument("id")
+    p.add_argument("text")
+    p.set_defaults(fn=decision_add)
 
     p = sp.add_parser("config")
     p.set_defaults(fn=config_cmd)
diff --git a/factory/compose.py b/factory/compose.py
index 29c8cff..f85c0da 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -68,6 +68,12 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
     def add_truth() -> None:
         for p in current_truth(root):
             add(str(p.relative_to(root)), f"Current truth: {p.parent.name}")
+
+    def add_decisions() -> None:
+        # an empty log (the one `factory init` creates) carries nothing, so it is no input
+        p = root / "decisions.md"
+        if p.exists() and p.read_text(encoding="utf-8").strip():
+            add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")
     if role == "triage":
         add(t["request"], "Request (raw, with any answers appended)")
         prior = _runs_for(root, tid, "triage", run_id)
@@ -79,6 +85,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
             add(f"runs/{tri[-1]}/output.md", "Ticket (Triage output)")
         add(t["request"], "Request (raw)")
         add_truth()
+        add_decisions()
         if rnd >= 1 and version >= 1:
             crit = _runs_for(root, tid, "critic", run_id)
             if crit:
@@ -96,6 +103,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
     elif role == "critic":
         add(f"specs/{tid}/v{version}.md", f"Spec under review (v{version})")
         add_truth()
+        add_decisions()
         if rnd >= 2 and version >= 2:
             crit = _runs_for(root, tid, "critic", run_id)
             if crit:
@@ -108,6 +116,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         if av is None:
             raise store.Refused(f"{tid} has no approved spec version")
         add(f"specs/{tid}/v{av}.md", f"Approved spec (v{av}, pinned)")
+        add_decisions()
         for p in _approvals(root, tid, "ruling"):
             add(str(p.relative_to(root)), "Human ruling")
     elif role in ("implementer", "reviewer", "verifier"):
diff --git a/factory/prompts/spec_writer.md b/factory/prompts/spec_writer.md
index a3b0dec..d84cadd 100644
--- a/factory/prompts/spec_writer.md
+++ b/factory/prompts/spec_writer.md
@@ -32,7 +32,9 @@ RULES
   would pass with a stub. Acceptance never names a test function or an
   internal symbol: those go stale and the verifier can't run them.
 - Open questions stay open. Don't resolve product or design ambiguity
-  yourself; list it, and the spec goes to NEEDS-HUMAN.
+  yourself; list it, and the spec goes to NEEDS-HUMAN. For each open
+  question, ask whether the answer is a standing decision that later
+  tickets must follow.
 - Write the Problem section for the operator who approves the spec at
   the gate, not for the harness builder or the next role. Write it the
   way a design doc is written: for a deeply technical reader who does
diff --git a/factory/prompts/triage.md b/factory/prompts/triage.md
index bef1ec6..dfe55f6 100644
--- a/factory/prompts/triage.md
+++ b/factory/prompts/triage.md
@@ -10,7 +10,8 @@ FOR EACH REQUEST
 3. Decide:
    - ACCEPT: the intent is clear and no product decision is needed.
    - NEEDS-HUMAN: it needs a product, priority, or design call. Write the
-     decision as one question with 2-3 concrete options.
+     decision as one question with 2-3 concrete options, and ask whether
+     the answer is a standing decision that later tickets must follow.
    - CLARIFY: key facts are missing. List exactly what's missing.
    - REJECT: duplicate, out of scope, or not actionable. One-line reason.
 4. For ACCEPT: write a title and a 2-5 sentence summary of what the
diff --git a/factory/specstore.py b/factory/specstore.py
index 2492f82..6c457d1 100644
--- a/factory/specstore.py
+++ b/factory/specstore.py
@@ -3,7 +3,8 @@ build spec part B "Spec store", part K `approve-spec` / `archive`).
 
 Current truth is `openspec/specs/<capability>/spec.md`. A ticket's change is the folder
 `openspec/changes/<ID>/`, written by the harness when the human gate pins a version: the pinned
-text is split on its `=== <path>` lines. Only `archive` writes current truth and `decisions.md`.
+text is split on its `=== <path>` lines. Only `archive` writes current truth. `decisions.md` has
+three writers, all through `record_decision`: `archive`, `decision add` and `resolve --decision`.
 The store is active once `init` has created `openspec/`; a store without it keeps the P0
 behaviour (specs pinned as one text), so the live pilot store is unaffected.
 """
@@ -235,6 +236,31 @@ def applies(root: Path, deltas: dict[str, dict[str, dict[str, str]]]) -> list[st
     return errors
 
 
+# ----- the decision log -------------------------------------------------------------------
+
+def _utc_date() -> str:
+    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
+
+
+def decision_text(text: str) -> str:
+    """A decision's text, stripped. Refused unless it is one non-blank line."""
+    s = text.strip()
+    if not s or len(s.splitlines()) > 1:
+        raise store.Refused("a decision is one non-blank line of text")
+    return s
+
+
+def record_decision(root: Path, tid: str, text: str, today: str | None = None) -> str:
+    """Append `<UTC date> <tid> <text>` to `decisions.md`, creating it if absent; return the line.
+    Needs no spec store: the log does not depend on `openspec/`."""
+    line = f"{today or _utc_date()} {tid} {decision_text(text)}"
+    p = root / "decisions.md"
+    p.parent.mkdir(parents=True, exist_ok=True)
+    with p.open("a", encoding="utf-8") as fh:
+        fh.write(line + "\n")
+    return line
+
+
 # ----- pin and archive ----------------------------------------------------------------------
 
 def change_dir(root: Path, tid: str) -> Path:
@@ -311,7 +337,7 @@ def archive(root: Path, tid: str, verifier_rows: list[str], today: str | None =
     """Part K `factory archive`: verifier results, apply deltas, move the folder, append the
     decisions. Caller has checked `applies`; nothing here refuses."""
     d = change_dir(root, tid)
-    date = today or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
+    date = today or _utc_date()
     ver = d / "verification.md"
     vtext = ver.read_text(encoding="utf-8") if ver.exists() else ""
     store.write_text(ver, vtext.rstrip() + "\n\n## Verifier results\n\n" + ("\n".join(verifier_rows) + "\n" if verifier_rows else "none\n"))
@@ -326,10 +352,8 @@ def archive(root: Path, tid: str, verifier_rows: list[str], today: str | None =
         store.write_text(tp, apply_delta(cur, cap, ops))
         applied.append(cap)
     lines = decisions_of((d / "proposal.md").read_text(encoding="utf-8")) if (d / "proposal.md").exists() else []
-    dec = root / "decisions.md"
-    with dec.open("a", encoding="utf-8") as fh:
-        for ln in lines:
-            fh.write(f"{date} {tid} {ln}\n")
+    for ln in lines:
+        record_decision(root, tid, ln, date)
     dest = root_dir(root) / "changes" / "archive" / f"{date}-{tid}"
     dest.parent.mkdir(parents=True, exist_ok=True)
     shutil.move(str(d), str(dest))
diff --git a/tests/factory/test_decision_log.py b/tests/factory/test_decision_log.py
new file mode 100644
index 0000000..87b541b
--- /dev/null
+++ b/tests/factory/test_decision_log.py
@@ -0,0 +1,255 @@
+"""The decision log (spec-factory T-0017): `decision add` and `resolve --decision` write
+`decisions.md` at any ticket state; the spec writer, critic and planner receive a non-empty log;
+the triage and spec-writer prompts ask whether an answer is a standing decision.
+
+Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_spec_store.py does.
+"""
+from __future__ import annotations
+
+import datetime as dt
+import json
+import os
+import re
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+FENCE = "`" * 3
+
+
+def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
+    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+
+def js(cp):
+    return json.loads(cp.stdout.strip().splitlines()[-1])
+
+
+def today() -> str:
+    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
+
+
+def log_lines(store: Path) -> list[str]:
+    """The decision log's lines with the UTC date replaced by TODAY."""
+    p = store / "decisions.md"
+    if not p.exists():
+        return []
+    d = today() + " "
+    return ["TODAY " + ln[len(d):] if ln.startswith(d) else ln for ln in p.read_text(encoding="utf-8").splitlines()]
+
+
+def events(store: Path, name: str) -> list[dict]:
+    return [json.loads(ln) for ln in run(store, "log", "tail", "-n", "200", "--event", name).stdout.splitlines()]
+
+
+def ticket(store: Path) -> dict:
+    return yaml.safe_load((store / "tickets" / "T-0001.yaml").read_text())
+
+
+@pytest.fixture
+def store(tmp_path: Path) -> Path:
+    s = tmp_path / "state"
+    req = tmp_path / "r.md"
+    req.write_text("# demo\n\nDo it.\n")
+    assert run(s, "ticket", "new", "--file", str(req)).returncode == 0
+    return s
+
+
+def park(store: Path, reason: str) -> None:
+    assert run(store, "ticket", "park", "T-0001", "--reason", reason).returncode == 0
+
+
+# ----- part A: decision add -----------------------------------------------------------------
+
+def test_decision_add_logs_against_a_closed_ticket_in_archives_format(store):
+    assert run(store, "resolve", "T-0001", "--close").returncode == 0
+    cp = run(store, "decision", "add", "T-0001", "Lionbot code lives under lionbot/")
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp) == {"ok": True, "id": "T-0001", "decision": f"{today()} T-0001 Lionbot code lives under lionbot/"}
+    assert ticket(store)["status"] == "closed"
+    assert run(store, "decision", "add", "T-0001", "  Second rule  ").returncode == 0
+    assert log_lines(store) == ["TODAY T-0001 Lionbot code lives under lionbot/", "TODAY T-0001 Second rule"]
+    ev = events(store, "decision.recorded")
+    assert [(e["ticket"], e["via"], e["line"]) for e in ev] == [
+        ("T-0001", "decision add", f"{today()} T-0001 Lionbot code lives under lionbot/"),
+        ("T-0001", "decision add", f"{today()} T-0001 Second rule")]
+    assert all(e["by"] for e in ev)
+
+
+def test_decision_add_needs_no_spec_store_and_appends_to_an_existing_log(store):
+    assert not (store / "openspec").exists()
+    (store / "decisions.md").write_text("2026-01-01 T-0009 kept\n")
+    assert run(store, "decision", "add", "T-0001", "new").returncode == 0
+    assert (store / "decisions.md").read_text() == f"2026-01-01 T-0009 kept\n{today()} T-0001 new\n"
+    assert not (store / "openspec").exists()
+
+
+@pytest.mark.parametrize("tid, text", [("T-0009", "x"), ("T-0001", "  "), ("T-0001", ""),
+                                       ("T-0001", "one\ntwo"), ("T-0001", "one\rtwo")])
+def test_decision_add_refuses_an_unknown_ticket_and_blank_or_multi_line_text(store, tid, text):
+    cp = run(store, "decision", "add", tid, text)
+    assert cp.returncode == 2, cp.stderr
+    assert js(cp)["ok"] is False
+    assert not (store / "decisions.md").exists()
+    assert events(store, "decision.recorded") == []
+
+
+# ----- part A: resolve --decision ----------------------------------------------------------
+
+def test_resolve_answer_and_close_each_log_a_decision_and_keep_it_in_the_record(store, tmp_path):
+    ans = tmp_path / "a.md"
+    ans.write_text("Use option B.\n")
+    park(store, "NEEDS-HUMAN from triage")
+    cp = run(store, "resolve", "T-0001", "--answer", str(ans), "--decision", "Option B is the standing rule")
+    assert cp.returncode == 0, cp.stderr
+    line1 = f"{today()} T-0001 Option B is the standing rule"
+    assert js(cp)["decision"] == line1 and js(cp)["state"] == "ready-for-triage"
+    assert (store / "requests" / "T-0001.md").read_text().count("## Answer ") == 1
+    cp = run(store, "resolve", "T-0001", "--close", "--decision", "Closed as a recorded decision")
+    assert cp.returncode == 0, cp.stderr
+    line2 = f"{today()} T-0001 Closed as a recorded decision"
+    assert ticket(store)["status"] == "closed"
+    assert log_lines(store) == ["TODAY T-0001 Option B is the standing rule", "TODAY T-0001 Closed as a recorded decision"]
+    recs = [yaml.safe_load((store / "approvals" / "T-0001" / f"resolve-{n}.yaml").read_text()) for n in (1, 2)]
+    assert [(r["kind"], r["decision"]) for r in recs] == [("answer", line1), ("close", line2)]
+    hist = [h for h in ticket(store)["history"] if "resolve" in h]
+    assert [(h["resolve"], h["decision"]) for h in hist] == [("answer", line1), ("close", line2)]
+    ev = events(store, "decision.recorded")
+    assert [(e["via"], e["line"]) for e in ev] == [("resolve --answer", line1), ("resolve --close", line2)]
+
+
+def test_resolve_without_decision_writes_no_decision_key(store):
+    assert run(store, "resolve", "T-0001", "--close").returncode == 0
+    rec = yaml.safe_load((store / "approvals" / "T-0001" / "resolve-1.yaml").read_text())
+    assert "decision" not in rec
+    assert not (store / "decisions.md").exists()
+
+
+def test_resolve_decision_alone_or_with_a_mode_that_cannot_carry_one_is_refused(store, tmp_path):
+    ruling = tmp_path / "r2.md"
+    ruling.write_text("Ruling.\n")
+    park(store, "ESCALATE from critic")
+    before = ticket(store)
+    for argv in (["--decision", "x"],
+                 ["--ruling", str(ruling), "--decision", "x"],
+                 ["--to", "spec-gate", "--decision", "x"],
+                 ["--redispatch", "--decision", "x"],
+                 # --ruling runs ahead of --close, so the close (and its decision) would not happen
+                 ["--ruling", str(ruling), "--close", "--decision", "x"]):
+        cp = run(store, "resolve", "T-0001", *argv)
+        assert cp.returncode == 2, (argv, cp.stderr)
+        assert "--decision applies only with --answer or --close" in cp.stderr
+    assert ticket(store) == before
+    assert not list((store / "approvals" / "T-0001").glob("ruling-*"))
+    assert not (store / "decisions.md").exists()
+
+
+def test_resolve_decision_is_not_logged_when_the_close_or_answer_is_refused(store, tmp_path):
+    ans = tmp_path / "a.md"
+    ans.write_text("B.\n")
+    # --answer on a ticket that is not parked NEEDS-HUMAN: refused, no answer, no decision
+    cp = run(store, "resolve", "T-0001", "--answer", str(ans), "--decision", "x")
+    assert cp.returncode == 2
+    assert "## Answer" not in (store / "requests" / "T-0001.md").read_text()
+    assert run(store, "resolve", "T-0001", "--close", "--decision", "Closed with a rule").returncode == 0
+    cp = run(store, "resolve", "T-0001", "--close", "--decision", "Again")
+    assert cp.returncode == 2
+    assert log_lines(store) == ["TODAY T-0001 Closed with a rule"]
+    assert len(events(store, "decision.recorded")) == 1
+
+
+def test_resolve_bad_decision_text_refuses_before_the_answer_is_appended(store, tmp_path):
+    ans = tmp_path / "a.md"
+    ans.write_text("B.\n")
+    park(store, "NEEDS-HUMAN from triage")
+    req_before = (store / "requests" / "T-0001.md").read_text()
+    for text in ("   ", "one\ntwo"):
+        cp = run(store, "resolve", "T-0001", "--answer", str(ans), "--decision", text)
+        assert cp.returncode == 2, cp.stderr
+    assert (store / "requests" / "T-0001.md").read_text() == req_before
+    assert ticket(store)["status"] == "parked"
+    assert not (store / "approvals" / "T-0001").exists() or not list((store / "approvals" / "T-0001").glob("resolve-*"))
+    assert not (store / "decisions.md").exists()
+
+
+# ----- part B: the decision log as role input --------------------------------------------------
+
+def start_and_compose(store: Path, role: str, status: str) -> tuple[list[str], str]:
+    assert run(store, "ticket", "set", "T-0001", f"status={status}", "in_flight=[]").returncode == 0
+    rid = js(run(store, "run", "start", "--role", role, "--ticket", "T-0001"))["run_id"]
+    cp = run(store, "run", "compose", rid)
+    assert cp.returncode == 0, cp.stderr
+    return js(cp)["sources"], (store / "runs" / rid / "input.md").read_text()
+
+
+@pytest.fixture
+def spec_store(store: Path) -> Path:
+    assert run(store, "init").returncode == 0
+    (store / "openspec" / "specs" / "thing").mkdir(parents=True)
+    (store / "openspec" / "specs" / "thing" / "spec.md").write_text("# thing\n\n## Requirements\n")
+    (store / "specs" / "T-0001").mkdir(parents=True)
+    (store / "specs" / "T-0001" / "v1.md").write_text("spec\n")
+    assert run(store, "ticket", "set", "T-0001", "spec.version=1", "spec.approved_version=1").returncode == 0
+    return store
+
+
+def test_spec_writer_critic_and_planner_receive_a_non_empty_log_and_triage_does_not(spec_store):
+    s = spec_store
+    (s / "decisions.md").write_text("2026-10-01 T-0009 SENTINEL keep the old format\n")
+    got = {r: start_and_compose(s, r, st) for r, st in (
+        ("triage", "ready-for-triage"), ("spec_writer", "ready-for-spec-writer"),
+        ("critic", "ready-for-critic"), ("planner", "ready-for-planner"))}
+    assert got["triage"][0] == ["requests/T-0001.md"]
+    assert got["spec_writer"][0] == ["requests/T-0001.md", "openspec/specs/thing/spec.md", "decisions.md"]
+    assert got["critic"][0] == ["specs/T-0001/v1.md", "openspec/specs/thing/spec.md", "decisions.md"]
+    assert got["planner"][0] == ["specs/T-0001/v1.md", "decisions.md"]
+    assert "SENTINEL" not in got["triage"][1]
+    for r in ("spec_writer", "critic", "planner"):
+        text = got[r][1]
+        assert text.count("SENTINEL") == 1
+        assert "## Decision log (decisions.md): standing decisions, read-only\n\n2026-10-01 T-0009 SENTINEL" in text
+
+
+def test_planner_gets_the_log_before_a_ruling(spec_store):
+    s = spec_store
+    (s / "decisions.md").write_text("2026-10-01 T-0009 SENTINEL\n")
+    (s / "approvals" / "T-0001").mkdir(parents=True)
+    (s / "approvals" / "T-0001" / "ruling-1.md").write_text("Ruling.\n")
+    sources, _ = start_and_compose(s, "planner", "ready-for-planner")
+    assert sources == ["specs/T-0001/v1.md", "decisions.md", "approvals/T-0001/ruling-1.md"]
+
+
+@pytest.mark.parametrize("content", [None, "", "\n", "  \n\t\n"])
+def test_an_absent_or_whitespace_only_log_adds_no_source(spec_store, content):
+    s = spec_store
+    if content is None:
+        (s / "decisions.md").unlink()
+    else:
+        (s / "decisions.md").write_text(content)
+    assert start_and_compose(s, "spec_writer", "ready-for-spec-writer")[0] == ["requests/T-0001.md", "openspec/specs/thing/spec.md"]
+    assert start_and_compose(s, "critic", "ready-for-critic")[0] == ["specs/T-0001/v1.md", "openspec/specs/thing/spec.md"]
+    assert start_and_compose(s, "planner", "ready-for-planner")[0] == ["specs/T-0001/v1.md"]
+
+
+# ----- part C: the questions ask whether an answer is standing ------------------------------------
+
+def test_triage_and_spec_writer_system_prompts_ask_about_standing_decisions(store):
+    for role, status in (("triage", "ready-for-triage"), ("spec_writer", "ready-for-spec-writer")):
+        assert run(store, "ticket", "set", "T-0001", f"status={status}", "in_flight=[]").returncode == 0
+        rid = js(run(store, "run", "start", "--role", role, "--ticket", "T-0001"))["run_id"]
+        assert "standing decision" in (store / "runs" / rid / "system-prompt.txt").read_text(), role
+
+
+@pytest.mark.parametrize("heading, copy", [("1. Triage", "01-triage.md"), ("2. Spec writer", "02-spec-writer.md")])
+def test_triage_and_spec_writer_design_blocks_equal_their_copies(heading, copy):
+    design = (REPO / "docs" / "design.md").read_text(encoding="utf-8")
+    m = re.search(r"^## " + re.escape(heading) + r"\n.*?^" + FENCE + r"text\n(.*?)^" + FENCE + "$", design, re.M | re.S)
+    assert m is not None
+    block = m.group(1)
+    assert "standing decision" in block
+    assert block == (REPO / "docs" / "prompts" / copy).read_text(encoding="utf-8")
