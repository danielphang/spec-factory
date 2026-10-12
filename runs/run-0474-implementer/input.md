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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0474-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0474-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0046.1` (branch `factory/T-0046.1`, base `34de412fd5fa7f410654e6f6c496877e9608cad1`, head `34de412fd5fa7f410654e6f6c496877e9608cad1`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0046.1

T-0046.1 / De-bloat C: give each operation the harness writes out several times one shared helper, with no change in behaviour
Depends on: none
Parallel-safe: yes

Parent: T-0046, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Only the store module lists a ticket's runs
- The CLI and the stats report read the event log through a shared reader
- One function records a status transition outside spec approval
- Neither spec amend nor the dispatcher builds the in-flight list itself
- One function reads the integration-branch tip
- Record copies, row set-asides, planner-run checks and spec apply checks each have one definition
- One line formats a failed-command park and one call cleans up a checker
- Status transitions write the same events and history entries
- Spec pinning and planner-run refusals keep their text
- The dispatcher parks a refused store command with the same reason
- The spec parser gives the same result as the base on every spec in the store
- The refactored harness has no unused imports or variables
- The harness suite passes and no existing test file changes
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v3, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0046/v3.md`

=== proposal.md
## Problem

The harness is the Python code under `factory/` that runs the factory: it records tickets, starts role runs and parks tickets for a human. In that code, seven small operations are written out by hand in two to eighteen places each. Each copy is a place a later fix can miss: a fix to one copy leaves the others with the old behaviour, and nobody notices until a run takes the unfixed path. The cost falls on whoever next changes one of these operations, usually an implementer agent working from a spec, and on the operator who reviews that change.

The seven operations are:
- listing the runs of one ticket, a run being one agent's attempt at one role;
- reading the store's event log, an append-only record of everything the harness did;
- recording a status change on a ticket;
- listing the runs still in flight on a ticket and its sub-tickets;
- reading the newest commit of the integration branch, the branch that finished work merges into;
- four smaller repeats in the command-line module;
- the reason the dispatcher writes when a store command fails and it parks the ticket. The dispatcher is the code in `factory/drive.py` that runs each role and calls the store's commands; a store command is one `bin/factory` call that reads or changes the store, the directory of tickets, runs and logs; a park is a stop that waits for a human, with a reason;

This change gives each operation one definition and points every copy at it. An eighth repeat the request named, the walks over spec Markdown in `specstore.py`, is left as it is (operator, at the spec gate; see Out of scope). Nothing a user or operator sees changes. Every refusal message, park reason, logged event and parse result stays as it is, and the existing tests pass without edits.

## Root cause

Each copy was written when its caller was written, and a later copy did not reuse the earlier one. For example, `cli._parent_close_verified` re-implements `compose._runs_for` with a different filter. The definitions this change adds and the callers each one replaces are listed in design.md.

## Out of scope

- Splitting `cli.py` into modules (T-0047, De-bloat D), which follows this ticket.
- The walks over spec Markdown in `specstore.py`: the section walks in `acceptance_labels`, `decisions_of` and `intent_of`, and the block walks in `requirement_blocks` and `scenario_blocks`. The operator cut this part at the spec gate (2026-10-12). These functions feed the archive step, which writes approved requirements into current truth by exact text, so a one-character slip would corrupt that record silently; sharing them saves about 20 lines. They stay as they are.
- The STATUS-trailer search shared by `status.py` and `subtickets.py` (issue #68).
- The Workflow scripts `factory/workflows/intake.js` and `factory/workflows/build.js` (issue #89). Their park reasons stay byte-identical because `drive.py`'s reasons stay byte-identical.
- `approve_spec`'s transition record (`cli.py:1115-1122`). `test_shepherd.py:79` checks that `approval.recorded` comes before `change.pinned`, and the transition event comes after both.
- The run listing in `stats._load` (`stats.py:66`). It reads every run of a store given by path, in flight or not, and adds fields of its own, so it is not a copy of operation 1.
- The other history appends (`cli.py:988` merge, `:1137` request-changes, `:1166` resolve, `store.py:139` park). They log a different event or none.
- Any change to a refusal message, park reason, event field, verdict, command or document.
- Edits to existing test files. New test files are allowed but not required.

## Open questions

none

## Decisions

- The shared run lister skips a run whose record file is empty, as the scratch clean-up does today. (The record file is `meta.yaml`, which each run's directory holds; the clean-up is `clear_scratch`, the function that deletes finished runs' scratch directories.) The other three callers would otherwise crash with `AttributeError` if they read the record while a run started in parallel is still writing it. This is the one difference from today's behaviour, and it can happen only during that write. Rejected: an iterator that hands back an empty meta for each caller to handle, which would leave the ticket, role and finished filters copied at every caller.
- The event log gets two readers. `store.log_lines` yields raw lines and leaves malformed-line handling to the caller, so `factory log tail` still prints raw text and the command-line readers still raise on a line that is not JSON. A new `cost._log_records` keeps the cost report's skip-malformed behaviour and is shared with the stats report (`stats.py`). `cost.py` stays free of imports from the `factory` package, as the request allows, because a test (`test_cost_once.py`) loads it by file path. Rejected: one strict reader for all four callers, which would change what `factory stats` does with a malformed line.
- The dispatcher's shared piece is a function that formats the park reason, not one that parks. Three of the 18 sites pick their reason inside a conditional expression (`drive.py:192`, `453`, `517`), and a helper cannot `return` from its caller. It is named `_harness_bug` so that it is not confused with `drive.py`'s existing `_fail` (`drive.py:664`), which prints a failure and exits.
- Part H of v2, one walker for spec sections and heading blocks, is cut (operator, spec gate, 2026-10-12): the most risk for the least saving. The spec-parser comparison stays as a REGRESSION check, because part A changes `specstore.critic_rounds`.
- The helpers' names and modules follow the request where it gave them (`store.record_transition`, `store.in_flight_runs`, a gitops helper, `section(text, heading)`). Where it did not, design.md names them.

## Risk

The change refactors eight harness modules: `cli.py`, `compose.py`, `cost.py`, `drive.py`, `gitops.py`, `specstore.py`, `stats.py` and `store.py`. Every ticket, run and archive passes through this code, so a slip changes live behaviour on both instances once the runtime is upgraded.

The archive path's spec parser is not refactored (part H cut). The spec-parser comparison under Acceptance still checks `specstore.py` against the base over every spec in this repo's store, since part A edits `critic_rounds` in that file.

The highest-risk part is G. `resolve --ruling` matches the park prefix `harness-bug: run start implementer:` (`cli.py:1187`), so that reason's text must not change.

Estimated size: about 200 to 300 changed lines, with a net fall of about 70.

Protected paths: `factory/**`

=== design.md
## Proposed change

Every part keeps each caller's refusal text, park reason, event fields, field order and result exactly. The parts are listed in the order to build them. Every function this change makes unused is deleted: `compose._runs_for`, and `stats.py`'s import of `_records`. The harness-code requirement that the harness keeps no unused definition applies.

**A. One run iterator (`factory/store.py`).**
Add `ticket_runs(root: Path, ticket: str, role: str | None = None, finished: bool = False)`.
- It yields `(run_id, meta)` for each `runs/<run_id>/meta.yaml`, in run-id (directory name) order.
- It skips a directory with no `meta.yaml`, or with an empty one (see Decisions).
- It yields only runs whose meta has `ticket == ticket`. When `role` is given, it also requires `role == role`. When `finished` is true, it also requires a truthy `finished`.
- A missing `runs/` yields nothing.

Its callers:
- `compose.py`: delete `_runs_for`. Its two uses become `[r for r, _ in store.ticket_runs(root, tid, role, finished=True) if r != run_id]`. The round filter at `compose.py:413` reads `round` from the yielded meta and does not re-read the file.
- `specstore.critic_rounds`: `ticket_runs(root, tid, "critic", finished=True)`. It reads `output.md` from `root / "runs" / run_id`.
- `cli._parent_close_verified`: `ticket_runs(root, t["id"], "verifier")`, with no finished filter, keeping its own `status == "VERIFIED"` and `head` checks. It returns the run id.
- `store.clear_scratch`: `ticket_runs(root, tid, finished=True)`. For each run, `runs/<id>/scratch` is unlinked when it is a symlink, removed with `shutil.rmtree` when it is a directory, and otherwise left alone. The comment about read-only directories stays.

`next_run_id` (`store.py:163`) lists run names, not a ticket's runs, and stays as it is.

**B. Event-log readers (`factory/store.py`, `factory/cost.py`, `factory/stats.py`).**
- Add `store.log_lines(root: Path)`. It yields each line (`str.splitlines()`) of each `log/*.jsonl` file, files in sorted name order. A missing `log/` yields nothing.
- `cli._recorded_plan_run` loops over `store.log_lines(root)` with `json.loads`. `cli.log_tail` builds its list from it. Both keep their own parsing, filtering and printing.
- Add `cost._log_records(store: str)`. It yields `_records(lf)` for each `log/*.jsonl` file of `store`, in sorted name order.
- `cost._store_paths` and `stats._load` loop over `_log_records`. `stats._load` keeps its `isinstance(e, dict) and e.get("ts")` filter and its sort.
- `stats.py` imports `_log_records` in place of `_records`.

**C. One transition record (`factory/store.py`).**
Add `record_transition(root, t, to, by, history=None, event=None) -> str`. It does the following, in order, and returns `frm`:
1. Set `frm = t["status"]` and `t["status"] = to`.
2. Append `{"ts": now(), "from": frm, "to": to, "by": by, **(history or {})}` to `t["history"]`.
3. `save_ticket(root, t)`.
4. `log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": to, "by": by, **(event or {})})`.

Its callers:
- `cli.ticket_transition`. It sets `t["parked"] = None` when `a.to != "parked"` before the call. It passes `history={"round": dict(t["round"]), **({"verified_by": verified_by} if verified_by else {})}` and `event={"round": t["round"]}`.
- `ticket_ready_implementers` (`cli.py:818-821`), with by `"ready-implementers"`.
- the dependant release in `merge` (`cli.py:1000-1003`), with by `"merge"`.
- `parent_check` (`cli.py:1063-1067`), with by `"parent-check"`.

`approve_spec` is not changed.

**D. In-flight runs (`factory/store.py`).**
Add `in_flight_runs(root, t) -> list[str]`, which returns `[r for x in (t, *subtickets_of(root, t["id"])) for r in x.get("in_flight") or []]`. `cli.spec_amend` (`cli.py:602-605`) and `drive._same_ticket_guard` (`drive.py:626`) use it. `spec_amend` keeps its own `subs` for its later lines. Both refusal texts are unchanged.

**E. Integration-branch tip (`factory/gitops.py`).**
Add `integration_tip(cfg, repo) -> str`, which returns `rev(repo, integration_branch(cfg, repo))`. The four `cli.py` sites (`254`, `328`, `545`, `1693`) call it.

**F. Smaller `cli.py` repeats (`factory/cli.py`).** Four helpers:
- `_copy_record(d: Path, kind: str, src) -> Path` sets `dest = d / f"{kind}-{_next_n(d, kind)}.md"`, runs `shutil.copyfile(src, dest)` and returns `dest`. It is used for the changes notes (`request_changes`) and the four ruling copies in `resolve`.
- `_supersede(root, t) -> tuple` reads `head = t.get("head")` and `moved = _set_aside_failed_rows(root, t)`, logs `results.superseded` with `ticket`, `head` and `roles=moved`, and returns `(head, moved)`. It is used by the reviewer-ESCALATE ruling and by `--redispatch`, at the same point in each branch as today.
- `_planner_run(root, run: str, tid: str) -> Path` returns `_run_dir(root, run)`. When that run's meta is not a PLANNED planner run of `tid`, it raises `Refused(f"{run} is not a PLANNED planner run of {tid}")`. `subticket_add` and `spec_tasks` use it, each at the point where it checks today.
- `_refuse_unless_applies(root, text, refusal: str)` runs `specstore.validate` and then, when that is clean, `specstore.applies`. On any error it raises `Refused(f"{refusal}: " + "; ".join(errors))`. `approve_spec` passes `"spec not pinned"` and `spec_amend` passes `"spec not amended"`, each inside its existing `is_active` block.

**G. Dispatcher parks (`factory/drive.py`).** Two module-level helpers:
- `_harness_bug(what: str, res: dict) -> str` returns `f"harness-bug: {what}: {res.get('stderr') or ''}"`, written on one line. All 18 reasons of that form use it, including the three inside conditional expressions (`192`, `453`, `517`) and the loop at `353`, which passes its `what`. Each `what` is the text between `harness-bug: ` and `: {` today, so `run start {role}`, `run compose {role}`, `run finish {role}`, `results record {role}`, `spec add`, `transition to critic`, `round increment refused`, `plan whole-spec`, `ready-implementers`, `ticket head`, `join`, `transition to checks`, `no head for the checkers`, `results show` and `merge` keep their current text.
- `_cleanup_checker(role: str, rid: str)` calls `call("run", "cleanup", rid)` when `role in CHECKERS`. It is used at `drive.py:225-226`, `233-234` and `574-575`.

The five "unknown STATUS" parks and the `wait` park (`drive.py:529`) do not carry a command's error text and stay as they are.

**PR description.** It reports `git diff --stat main...HEAD -- factory` (the line change per file), as the request asks.

## Tests to change

none

=== specs/harness-code/spec.md
## ADDED Requirements

### Requirement: Each operation the harness repeated has one definition
The harness SHALL define once each of the following: listing a ticket's runs, reading the event log (one reader for the CLI, one inside the standalone cost script), recording a status transition outside spec approval, listing the runs in flight on a ticket and its sub-tickets, reading the integration-branch tip, copying a resolution record, setting aside failed result rows, checking for a PLANNED planner run, refusing a spec that does not validate and apply, formatting a dispatcher park for a failed store command, and cleaning up a checker run. Every caller MUST use that definition.

#### Scenario: Only the store module lists a ticket's runs
- WHEN `cat factory/cli.py factory/compose.py factory/specstore.py | grep -cE 'runs\.(iterdir|glob)\(|"runs"\)\.(iterdir|glob)\('`
- THEN it prints `0`

#### Scenario: The CLI and the stats report read the event log through a shared reader
- WHEN `echo "$(cat factory/cli.py factory/stats.py | grep -c '"\*\.jsonl"') $(grep -c '"\*\.jsonl"' factory/store.py)"`
- THEN it prints `0 1`

#### Scenario: One function records a status transition outside spec approval
- WHEN `echo "$(grep -c '"ticket\.transition"' factory/cli.py) $(grep -c '"ticket\.transition"' factory/store.py)"`
- THEN it prints `1 1`

#### Scenario: Neither spec amend nor the dispatcher builds the in-flight list itself
- WHEN `cat factory/cli.py factory/drive.py | grep -cE 'for \w+ in \(t, \*'`
- THEN it prints `0`

#### Scenario: One function reads the integration-branch tip
- WHEN `echo "$(cat factory/*.py | grep -cE 'rev\(repo, (gitops\.)?integration_branch\(') $(grep -c '^def integration_tip(' factory/gitops.py)"`
- THEN it prints `1 1`

#### Scenario: Record copies, row set-asides, planner-run checks and spec apply checks each have one definition
- WHEN `echo "$(grep -c 'shutil\.copyfile(a\.' factory/cli.py) $(grep -c '"results\.superseded"' factory/cli.py) $(grep -c 'is not a PLANNED planner run' factory/cli.py) $(grep -c 'specstore\.applies(root, deltas)' factory/cli.py)"`
- THEN it prints `0 1 1 1`

#### Scenario: One line formats a failed-command park and one call cleans up a checker
- WHEN `echo "$(grep -cE "harness-bug: .*stderr" factory/drive.py) $(grep -c 'call("run", "cleanup"' factory/drive.py) $(grep -cE '^def _(harness_bug|cleanup_checker)\(' factory/drive.py)"`
- THEN it prints `1 1 2`

### Requirement: Sharing an operation changes no refusal, park reason, event or parse result
After the operations above are shared, every command MUST print the same refusals, write the same events, history entries and park reasons, and parse every spec the same way as before, and the existing harness tests SHALL pass with no existing test file changed.

#### Scenario: Status transitions write the same events and history entries
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0046-store.sh <<'EOF'
# Sourced from the repo root: a throwaway store (the suite's fixture instance) whose T-0001 is
# awaiting the spec gate with a one-line spec, and a stand-in `claude` that fails if ever called.
# Leaves T set. Every command's output is discarded.
T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/s FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance
export FACTORY_REPO=$T/none FACTORY_INTEGRATION_BRANCH=main PYTHONDONTWRITEBYTECODE=1 LOGNAME=op; unset FACTORY_DISPATCH
mkdir $T/bin && printf '#!/bin/sh\necho "{}"; exit 1\n' > $T/bin/claude && chmod +x $T/bin/claude && export PATH=$T/bin:$PATH
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && printf '## Problem\nx\n' > $T/spec.md
bin/factory ticket new --file $T/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0046-reason.py <<'EOF'
# uv run --frozen python t0046-reason.py <store> <ticket>: the ticket's park reason, as a Python
# literal, with the store's scratch directory written as <T>.
import os, sys, yaml
t = yaml.safe_load(open(os.path.join(sys.argv[1], "tickets", sys.argv[2] + ".yaml")))
print(sys.argv[2], repr((t.get("parked") or {}).get("reason")).replace(os.path.dirname(sys.argv[1]), "<T>"))
EOF
cat > ${TMPDIR:-/tmp}/t0046-specstore.py <<'EOF'
# uv run --frozen python t0046-specstore.py, from the repo root: runs the spec parser of the merge
# base of HEAD and main and the checkout's own over every spec version, change part and
# current-truth file in this repo's store, and counts the calls whose result (or raised exception
# type) differs. Prints `files=<n> checks=<m> differ=<k>`, then up to five differing calls.
import glob, importlib.util, os, subprocess, sys, tempfile
sys.path.insert(0, os.getcwd())
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
def load(name, src):
    p = os.path.join(tempfile.mkdtemp(), name + ".py"); open(p, "w").write(src)
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old = load("t0046_old", git("show", git("merge-base", "HEAD", "main").strip() + ":factory/specstore.py"))
new = load("t0046_new", open("factory/specstore.py", encoding="utf-8").read())
S = os.path.join(os.path.dirname(git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()), ".factory", "store")
files = sorted(glob.glob(S + "/specs/*/v*.md") + glob.glob(S + "/openspec/**/*.md", recursive=True))
truths = sorted(glob.glob(S + "/openspec/specs/*/spec.md"))
def res(m, fn, a):
    try: return repr(getattr(m, fn)(*a))
    except Exception as e: return "raised " + type(e).__name__
checks, differ = 0, []
for path in files:
    t = open(path, encoding="utf-8").read(); parts = dict(old.split_parts(t)); ops = old.parse_delta(t)[0]
    calls = [("validate", (t,)), ("intent_of", (t,)), ("scenario_blocks", (t,)), ("requirement_blocks", (t,)),
             ("parse_delta", (t,)), ("decisions_of", (parts.get("proposal.md", t),)),
             ("acceptance_labels", (parts.get("verification.md", t),))]
    if any(ops.values()):
        calls += [("apply_delta", (open(c, encoding="utf-8").read(), os.path.basename(os.path.dirname(c)), ops)) for c in truths]
    for fn, a in calls:
        checks += 1
        if res(old, fn, a) != res(new, fn, a):
            differ.append(f"{fn} {os.path.relpath(path, S)}")
print(f"files={len(files)} checks={checks} differ={len(differ)}")
for d in differ[:5]: print(d)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && bin/factory approve-spec T-0001 >/dev/null && printf 'ST-1 / A\nDepends on: none\nParallel-safe: yes\n\nST-2 / B\nDepends on: ST-1\nParallel-safe: yes\n' > $T/plan.md && bin/factory subticket add T-0001 --file $T/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket ready-implementers T-0001 >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null && bin/factory ticket parent-check T-0001 >/dev/null && bin/factory log tail --event ticket.transition -n 50 | sed 's/^{"ts": "[^"]*", /{/' && uv run --frozen python -c "import glob, sys, yaml; [print(p.rsplit('/', 1)[1][:-5], {k: v for k, v in h.items() if k != 'ts'}) for p in sorted(glob.glob(sys.argv[1] + '/tickets/*.yaml')) for h in yaml.safe_load(open(p))['history']]" $FACTORY_STATE)`
- THEN it prints exactly these 14 lines:

```
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-triage", "to": "ready-for-spec-writer", "by": "t", "round": {"spec": 0, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-spec-writer", "to": "ready-for-critic", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-critic", "to": "awaiting-spec-gate", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "awaiting-spec-gate", "to": "ready-for-planner", "by": "op"}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-planner", "to": "planned", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001.2", "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"}
{"event": "ticket.transition", "ticket": "T-0001", "from": "planned", "to": "ready-for-parent-verify", "by": "parent-check"}
T-0001.2 {'from': 'waiting-dependencies', 'to': 'ready-for-implementer', 'by': 'ready-implementers'}
T-0001 {'from': 'ready-for-triage', 'to': 'ready-for-spec-writer', 'by': 't', 'round': {'spec': 0, 'pr': 0}}
T-0001 {'from': 'ready-for-spec-writer', 'to': 'ready-for-critic', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'ready-for-critic', 'to': 'awaiting-spec-gate', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'awaiting-spec-gate', 'to': 'ready-for-planner', 'by': 'op', 'approved_version': 1}
T-0001 {'from': 'ready-for-planner', 'to': 'planned', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'planned', 'to': 'ready-for-parent-verify', 'by': 'parent-check'}
```

#### Scenario: Spec pinning and planner-run refusals keep their text
Needs the GIVEN block of "Status transitions write the same events and history entries" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && mkdir $T/s/openspec && bin/factory approve-spec T-0001 2>/dev/null | tail -1; rmdir $T/s/openspec && bin/factory approve-spec T-0001 >/dev/null && bin/factory ticket new --file $T/req2.md >/dev/null && R=$(bin/factory run start --role triage --ticket T-0002 --model m | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p') && bin/factory subticket add T-0001 2>/dev/null | tail -1; bin/factory subticket add T-0001 --run $R 2>/dev/null | tail -1; bin/factory spec tasks T-0001 --run $R 2>/dev/null | tail -1)`
- THEN it prints exactly these 4 lines:

```
{"ok": false, "error": "spec not pinned: no `=== <path>` part lines"}
{"ok": false, "error": "no recorded planner run found for T-0001 (latest plan.added source: none); pass --run RUN or --file F"}
{"ok": false, "error": "run-0001-triage is not a PLANNED planner run of T-0001"}
{"ok": false, "error": "run-0001-triage is not a PLANNED planner run of T-0001"}
```

#### Scenario: The dispatcher parks a refused store command with the same reason
Needs the GIVEN block of "Status transitions write the same events and history entries" run once. `factory drive` runs for real on the throwaway store. T-0001.1's implementer run start is refused because the target repository does not exist. T-0001.2 sits at its checks with no branch. T-0002 is at its planner with no approved spec.
- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && bin/factory approve-spec T-0001 >/dev/null && printf 'ST-1 / A\nDepends on: none\nParallel-safe: yes\n\nST-2 / B\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && bin/factory subticket add T-0001 --file $T/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.2 status=checks-in-flight >/dev/null && bin/factory ticket new --file $T/req2.md >/dev/null && bin/factory ticket set T-0002 status=ready-for-planner >/dev/null && bin/factory drive T-0001 --phase build >/dev/null 2>&1; bin/factory drive T-0002 --phase build >/dev/null 2>&1; for x in T-0001.1 T-0001.2 T-0002; do uv run --frozen python ${TMPDIR:-/tmp}/t0046-reason.py $FACTORY_STATE $x; done)`
- THEN it prints exactly these 3 lines:

```
T-0001.1 "harness-bug: run start implementer: factory: FileNotFoundError: [Errno 2] No such file or directory: PosixPath('<T>/none')\n"
T-0001.2 'harness-bug: no head for the checkers: T-0001.2 has no branch yet\n'
T-0002 'harness-bug: plan whole-spec: T-0002 has no approved spec\n'
```

#### Scenario: The spec parser gives the same result as the base on every spec in the store
Needs the GIVEN block of "Status transitions write the same events and history entries" run once.
- WHEN `(uv run --frozen python ${TMPDIR:-/tmp}/t0046-specstore.py)`
- THEN it prints one line, `files=<n> checks=<m> differ=0`, with n and m above 0, and nothing after it

#### Scenario: The refactored harness has no unused imports or variables
- WHEN `uvx ruff check --select F401,F841 factory tests`
- THEN it prints `All checks passed!` and exits 0

#### Scenario: The harness suite passes and no existing test file changes
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0046-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=DMR main...HEAD -- tests)`
- THEN it prints one line, which reports a number of passed tests and no `failed` or `error`, and nothing after it

=== verification.md
## Acceptance

- Only the store module lists a ticket's runs → NEW; on `2b9baf5` it prints `3` (`compose.py:20`, `specstore.py:276`, `cli.py:1722`).
- The CLI and the stats report read the event log through a shared reader → NEW; prints `3 0` today (`cli.py:674`, `cli.py:1761` and `stats.py:72` glob the log, and `store.py` has no reader).
- One function records a status transition outside spec approval → NEW; prints `5 0` today.
- Neither spec amend nor the dispatcher builds the in-flight list itself → NEW; prints `2` today (`cli.py:603`, `drive.py:626`).
- One function reads the integration-branch tip → NEW; prints `4 0` today (four call sites in `cli.py`, no helper in `gitops.py`).
- Record copies, row set-asides, planner-run checks and spec apply checks each have one definition → NEW; prints `5 2 2 2` today.
- One line formats a failed-command park and one call cleans up a checker → NEW; prints `18 3 0` today (18 park reasons, three cleanup calls, neither helper defined).
- Status transitions write the same events and history entries → REGRESSION
- Spec pinning and planner-run refusals keep their text → REGRESSION
- The dispatcher parks a refused store command with the same reason → REGRESSION
- The spec parser gives the same result as the base on every spec in the store → REGRESSION
- The refactored harness has no unused imports or variables → REGRESSION
- The harness suite passes and no existing test file changes → REGRESSION
