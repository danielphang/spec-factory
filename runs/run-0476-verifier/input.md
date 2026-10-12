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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0476-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0476-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0476-verifier/wt` (branch `factory/T-0046.1`, base `34de412fd5fa7f410654e6f6c496877e9608cad1`, head `b1123b0bb2430ff9d23d9302c34e133b522c5aa2`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

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

## PR description (the implementer's output)

Sub-ticket: T-0046.1 (parent T-0046, approved spec v3). Branch `factory/T-0046.1`, commit `b1123b0` on base `34de412`.

## What changed

The harness is the Python code under `factory/` that runs the factory. Before this change, seven small operations were written out by hand in several places each. Each one now has a single definition, and every copy calls it. Nothing a user or operator sees has changed. The REGRESSION scenarios print byte-identical refusals, events, history entries and park reasons, and the spec parser gives the same result on all 4034 calls checked. The changes, by lettered part of the design:

| Part | New definition | Callers that now use it |
|---|---|---|
| A. List a ticket's runs | `store.ticket_runs(root, ticket, role=None, finished=False)`, which yields `(run_id, meta)` in run-id order and skips a run whose `meta.yaml` is missing or empty | `compose.py` (every former `_runs_for` call, plus `_last_run_meta`); `specstore.critic_rounds`; `cli._parent_close_verified`; `store.clear_scratch`; **and three `cli.py` callers of `compose._runs_for` that the spec did not list** (see Known gaps). `compose._runs_for` is deleted. |
| B. Read the event log | `store.log_lines(root)` (raw lines); `cost._log_records(store)` (parsed records, malformed lines skipped) | `cli._recorded_plan_run` and `cli.log_tail` use `log_lines`. `cost._store_paths` and `stats._load` use `_log_records`. `stats.py` imports `_log_records` in place of `_records`. |
| C. Record a status transition | `store.record_transition(root, t, to, by, history=None, event=None)`, which returns the status the ticket left | `cli.ticket_transition`, `ticket_ready_implementers`, the dependant release in `merge`, `ticket_parent_check`. `approve_spec` is unchanged. |
| D. List runs in flight | `store.in_flight_runs(root, t)` | `cli.spec_amend` and `drive._same_ticket_guard` |
| E. Read the integration-branch tip | `gitops.integration_tip(cfg, repo)` | the four `cli.py` sites (`_check_sibling_tests`, `_test_drift`, `_integration_head`, `_reused_subticket_run`) |
| F. Four smaller `cli.py` repeats | `_copy_record`, `_supersede`, `_planner_run`, `_refuse_unless_applies` | `request_changes` and the four ruling copies in `resolve`; the reviewer-ESCALATE ruling and `--redispatch`; `subticket_add` and `spec_tasks`; `approve_spec` ("spec not pinned") and `spec_amend` ("spec not amended") |
| G. Dispatcher parks (the dispatcher is `factory/drive.py`, which runs each role and parks the ticket when a store command fails) | `drive._harness_bug(what, res)` formats the park reason; `drive._cleanup_checker(role, rid)` cleans up a checker run | all 18 `harness-bug: <what>: <stderr>` reasons, including the three inside conditional expressions and the loop over `what`; the three checker clean-ups |

`git diff --stat main...HEAD -- factory`, the line change per file, as the design asks:
```
 factory/cli.py       | 137 ++++++++++++++++++++++++---------------------------
 factory/compose.py   |  33 ++++---------
 factory/cost.py      |  23 +++++----
 factory/drive.py     |  58 ++++++++++++----------
 factory/gitops.py    |   5 ++
 factory/specstore.py |  17 ++-----
 factory/stats.py     |   9 ++--
 factory/store.py     |  46 ++++++++++++++---
 8 files changed, 175 insertions(+), 153 deletions(-)
```

Callers of each changed function were found with grep (coding rule 2). `grep -rn "_runs_for\|_last_run_meta" factory bin agents tests docs README.md` found the three extra `cli.py` callers. After the change, `_runs_for` appears nowhere. `README.md` is not updated: no command, state, stop or path changed.

## Acceptance results

Every command ran from the worktree inside the fresh-HOME wrapper. For the GIVEN fixtures, `TMPDIR` pointed at this run's scratch directory.

NEW, before (base `34de412`) and after (`b1123b0`):

| Scenario | Before | After | Expected after |
|---|---|---|---|
| Only the store module lists a ticket's runs | `3` | `0` | `0` |
| The CLI and the stats report read the event log through a shared reader | `3 0` | `0 1` | `0 1` |
| One function records a status transition outside spec approval | `5 0` | `1 1` | `1 1` |
| Neither spec amend nor the dispatcher builds the in-flight list itself | `2` | `0` | `0` |
| One function reads the integration-branch tip | `4 0` | `1 1` | `1 1` |
| Record copies, row set-asides, planner-run checks and spec apply checks each have one definition | `5 2 2 2` | `0 1 1 1` | `0 1 1 1` |
| One line formats a failed-command park and one call cleans up a checker | `18 3 0` | `1 1 2` | `1 1 2` |

Each "before" value matches what verification.md predicted for this base.

REGRESSION, after:
- **Status transitions write the same events and history entries.** The 14 lines are byte-identical to the spec's expected block. The comparison was a Python string equality against the block extracted from `specs/T-0046/v3.md`, and it printed `1 SAME 14`. This means the four rewritten transition sites write the same history entries and log events, with the same fields in the same order.
- **Spec pinning and planner-run refusals keep their text.** The 4 lines are byte-identical (`2 SAME 4`), so the refusals from `_refuse_unless_applies` and `_planner_run` keep their text.
- **The dispatcher parks a refused store command with the same reason.** The 3 lines are byte-identical (`3 SAME 3`), so `_harness_bug` keeps every park reason's text, including the `harness-bug: run start implementer:` prefix that `resolve --ruling` matches. The first run of this scenario failed and caught a real defect, covered in Known gaps.
- **The spec parser gives the same result as the base on every spec in the store.** It printed `files=272 checks=4034 differ=0` and nothing after it. This means the edit to `critic_rounds` (part A) leaves every parse result as it was on the base.
- **The refactored harness has no unused imports or variables.** `uvx ruff check --select F401,F841 factory tests` printed `All checks passed!` and exited 0. As an extra check, a full default `ruff check factory` reports the same findings as on the base. The two lists, with line numbers stripped, have an empty diff.
- **The harness suite passes and no existing test file changes.** It printed `576 passed in 464.24s (0:07:44)`. The `git diff --name-only --diff-filter=DMR main...HEAD -- tests` part printed nothing, so no existing test file changed.

Gate commands on `b1123b0`, each as written:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: the first run reported `1 failed, 575 passed`. The failure was `test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`. That test passes only if a 50 ms poll sees all four checker runs at once inside a 2-second window. I was running the spec-parser comparison and ruff alongside it during that run. Run alone, it passed 3 times out of 3. A second full gate run with nothing alongside it printed `576 passed in 468.06s`, and the REGRESSION suite command above passed too. I read this as a timing flake under CPU load, not a regression. I did not prove that, so it is also listed under Known gaps.

## Tests added/changed

None. Every behaviour is covered by the existing suite and the spec's scenarios. No existing test file was touched.

## Known gaps and uncertainties

- **The spec missed three callers of `compose._runs_for`.** Design.md says `_runs_for` has "two uses", all in `compose.py`, and tells me to delete it. In fact it had 8 call sites in `compose.py` and 3 more in `cli.py`: `_check_drift`, `_planner_needed` and the conflict-run counter in `ticket_head` (base lines 288, 754 and 845). Deleting the function as the spec says broke those `cli.py` callers. The first run of the dispatcher-park scenario caught it, printing `AttributeError: module 'factory.compose' has no attribute '_runs_for'` in T-0001.1's park reason. I pointed all three at `store.ticket_runs(..., finished=True)`, the same filter `_runs_for` applied. The spec's requirement says "Every caller MUST use that definition", so I treated this as within scope, not a new design. After this, all three REGRESSION command scenarios were byte-identical. `compose._last_run_meta` stays: it is still called from `compose.py` and `cli._planner_needed`, and it now reads its meta from `ticket_runs`.
- **The net line change is +22, not the spec's estimated fall of about 70.** `factory/` has 175 insertions and 153 deletions. The spec estimated a net fall of about 70. Three things account for most of the gap. Each new helper has a one-line docstring. Deleting `_runs_for` as the design says leaves 11 inline list comprehensions in its place. The estimate may also predate the cut of part H. I did not add anything outside the design to close the gap.
- **`clear_scratch` acts slightly differently on edge cases, as the design specifies.** It now unlinks a scratch entry that is a symlink, even a broken one. Before, `glob("*/scratch")` may not have matched a broken symlink. A scratch entry that is a regular file is now left alone, where `shutil.rmtree` would have raised before. Both changes follow design.md part A. Neither can happen to a scratch directory the harness creates itself.
- **An empty `meta.yaml` is now skipped.** This is the one behaviour change the spec's Decisions accept. The other run listers would have raised `AttributeError` on a run whose record is still being written.
- **`cost._store_paths` now reads the log files in sorted order.** Before, it used an unsorted glob. Its result is a set, so the order cannot change what it returns.
- **The flaky test is not proven flaky.** See the gate results above: one failure under load, then 3 of 3 passes alone and two clean full runs.
- `factory:` markers added: none. The existing marker in `clear_scratch` is kept.

## Out-of-scope observations

- The verification.md evidence for part A named only the run-directory listings in `compose.py`, `specstore.py` and `cli.py`. A later spec that deletes a helper might grep for qualified uses (`module._name`) too, since that is what the "two uses" count missed.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW and REGRESSION scenario was run on the head, and the three REGRESSION command outputs are byte-identical to the spec. The one open point is a timing test that failed once under load and then passed three times alone and in two full runs.
ESCALATIONS: none

## Diff `34de412fd5fa7f410654e6f6c496877e9608cad1...b1123b0bb2430ff9d23d9302c34e133b522c5aa2`

diff --git a/factory/cli.py b/factory/cli.py
index 8373b4b..091fc46 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -168,13 +168,11 @@ def ticket_transition(a, root, cfg):
         if specstore.is_active(root) and specstore.change_dir(root, t["id"]).exists():
             raise Refused(f"{t['id']} is verified but not archived: run `archive {t['id']}` first")
     _apply_round(t, a.round, cfg)
-    t["status"] = a.to
     if a.to != "parked":
         t["parked"] = None
-    t["history"].append({"ts": store.now(), "from": frm, "to": a.to, "by": a.by, "round": dict(t["round"]),
-                         **({"verified_by": verified_by} if verified_by else {})})
-    store.save_ticket(root, t)
-    store.log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": a.to, "by": a.by, "round": t["round"]})
+    store.record_transition(root, t, a.to, a.by,
+                            history={"round": dict(t["round"]), **({"verified_by": verified_by} if verified_by else {})},
+                            event={"round": t["round"]})
     out({"ok": True, "id": t["id"], "state": t["status"], "round": t["round"]})
 
 
@@ -196,6 +194,15 @@ def _run_dir(root: Path, rid: str) -> Path:
     return d
 
 
+def _planner_run(root: Path, run: str, tid: str) -> Path:
+    """Run `run`'s directory, refused unless it is a PLANNED planner run of ticket `tid`."""
+    d = _run_dir(root, run)
+    meta = store.read_yaml(d / "meta.yaml")
+    if meta.get("ticket") != tid or meta.get("role") != "planner" or meta.get("status") != "PLANNED":
+        raise Refused(f"{run} is not a PLANNED planner run of {tid}")
+    return d
+
+
 def run_start(a, root, cfg):
     if a.role not in ROLES:
         raise Refused(f"unknown role {a.role}; roles: {', '.join(ROLES)}")
@@ -251,7 +258,7 @@ def _check_sibling_tests(root: Path, cfg: dict, t: dict) -> None:
     parent = store.load_ticket(root, t["parent"])
     base = parent.get("parent_base")
     repo = gitops.repo_root()
-    tip = gitops.rev(repo, gitops.integration_branch(cfg, repo))
+    tip = gitops.integration_tip(cfg, repo)
     merges = [s["merge"] for s in store.subtickets_of(root, parent["id"])
               if s["id"] != t["id"] and s["status"] == "merged"
               and (s.get("merge") or {}).get("main_after") and s["merge"].get("base_before")]
@@ -278,7 +285,7 @@ def _check_drift(root: Path, cfg: dict, t: dict) -> None:
     design names, and no Tests to change list names it. A merged sibling's recorded merge is not
     drift: the plan expects its changes. The build parks the refusal as BLOCKED."""
     tid = t["id"]
-    if compose._runs_for(root, tid, "implementer", "") or list((root / "approvals" / tid).glob("ruling-*")):
+    if any(store.ticket_runs(root, tid, "implementer", finished=True)) or list((root / "approvals" / tid).glob("ruling-*")):
         return
     sub = root / "specs" / tid / "subticket.md"
     sub_text = sub.read_text(encoding="utf-8") if sub.exists() else ""
@@ -325,7 +332,7 @@ def _test_drift(root: Path, cfg: dict, parent: dict, sub_text: str) -> list[str]
     repo = gitops.repo_root()
     if not gitops.git(repo, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", check=False):
         return []
-    tip = gitops.rev(repo, gitops.integration_branch(cfg, repo))
+    tip = gitops.integration_tip(cfg, repo)
     design = dict(specstore.split_parts((root / "specs" / parent["id"] / f"v{n}.md").read_text(encoding="utf-8")))
     design_text = design.get("design.md", "")
     at_tip = set(gitops.git(repo, "ls-tree", "-r", "--name-only", tip).splitlines())
@@ -542,7 +549,7 @@ def _integration_head(cfg: dict) -> str | None:
     """The integration branch's head in the target repo, or None when the repo or branch does not resolve."""
     try:
         repo = gitops.repo_root()
-        return gitops.rev(repo, gitops.integration_branch(cfg, repo))
+        return gitops.integration_tip(cfg, repo)
     except (Refused, OSError):
         return None
 
@@ -600,7 +607,7 @@ def spec_amend(a, root, cfg):
     if not reason or len(reason.splitlines()) > 1:
         raise Refused("--reason is one non-blank line of text")
     subs = store.subtickets_of(root, tid)
-    runs = [r for x in (t, *subs) for r in x.get("in_flight") or []]
+    runs = store.in_flight_runs(root, t)
     if runs:
         raise Refused(f"{tid} has runs in flight on it or its sub-tickets: {', '.join(runs)}; amend once they finish")
     if a.intent == "changed":
@@ -617,10 +624,7 @@ def spec_amend(a, root, cfg):
         if not specstore.change_dir(root, tid).exists():
             raise Refused(f"{tid} has no change folder ({_rel(root, specstore.change_dir(root, tid))}): "
                           "it was archived, so its spec can no longer be amended")
-        _, deltas, errors = specstore.validate(text)
-        errors += specstore.applies(root, deltas) if not errors else []
-        if errors:
-            raise Refused("spec not amended: " + "; ".join(errors))
+        _refuse_unless_applies(root, text, "spec not amended")
     n = _add_spec_version(root, t, text, f"amend {a.file}", cfg)
     if specstore.is_active(root):
         tasks = specstore.change_dir(root, tid) / "tasks.md"
@@ -671,11 +675,10 @@ def plan_add(a, root, cfg):
 def _recorded_plan_run(root: Path, tid: str) -> str:
     """The run named by the ticket's latest `plan.added` event, when that is a run of this store."""
     source = None
-    for p in sorted((root / "log").glob("*.jsonl")):
-        for ln in p.read_text(encoding="utf-8").splitlines():
-            e = json.loads(ln)
-            if e.get("event") == "plan.added" and e.get("ticket") == tid:
-                source = e.get("source")
+    for ln in store.log_lines(root):
+        e = json.loads(ln)
+        if e.get("event") == "plan.added" and e.get("ticket") == tid:
+            source = e.get("source")
     if not source or "/" in source or not (root / "runs" / source / "meta.yaml").exists():
         raise Refused(f"no recorded planner run found for {tid} (latest plan.added source: {source or 'none'}); "
                       "pass --run RUN or --file F")
@@ -689,10 +692,7 @@ def subticket_add(a, root, cfg):
     if not a.run and not a.file:
         a.run = _recorded_plan_run(root, parent["id"])
     if a.run:
-        d = _run_dir(root, a.run)
-        meta = store.read_yaml(d / "meta.yaml")
-        if meta.get("ticket") != parent["id"] or meta.get("role") != "planner" or meta.get("status") != "PLANNED":
-            raise Refused(f"{a.run} is not a PLANNED planner run of {parent['id']}")
+        d = _planner_run(root, a.run, parent["id"])
         text = status.strip_trailer((d / "output.md").read_text(encoding="utf-8"))
     else:
         text = Path(a.file).read_text(encoding="utf-8")
@@ -751,7 +751,7 @@ def _planner_needed(root: Path, t: dict, spec_text: str) -> str | None:
     subs = store.subtickets_of(root, t["id"])
     if subs:
         return f"it already has sub-tickets: {', '.join(s['id'] for s in subs)}"
-    planned = compose._runs_for(root, t["id"], "planner", "")
+    planned = [r for r, _ in store.ticket_runs(root, t["id"], "planner", finished=True)]
     if planned:
         return f"a planner already ran on it: {planned[-1]}"
     writer = compose._last_run_meta(root, t["id"], "spec_writer", "")
@@ -815,10 +815,7 @@ def ticket_ready_implementers(a, root, cfg):
     ready = subtickets.ready_implementers(subs, status_of)
     for s in subs:  # a dependency that just became met releases its dependant (siblings at merge; other parents here)
         if s["id"] in ready and s["status"] == "waiting-dependencies":
-            s["status"] = "ready-for-implementer"
-            s["history"].append({"ts": store.now(), "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"})
-            store.save_ticket(root, s)
-            store.log_event(root, "ticket.transition", ticket=s["id"], **{"from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"})
+            store.record_transition(root, s, "ready-for-implementer", "ready-implementers")
     out({"ok": True, "parent": a.id, "ready": ready, "subtickets": [s["id"] for s in every],
          "remaining": [s["id"] for s in subs if s["status"] not in ("merged", "parked", "closed")],
          "in_flight": [s["id"] for s in subs if s["in_flight"] or s["status"] in subtickets.IN_FLIGHT_STATES],
@@ -845,7 +842,7 @@ def ticket_head(a, root, cfg):
         else:
             # A conflict run that did not merge the integration branch in. Counted once per
             # implementer run (this command may be called more than once), so the loop is bounded.
-            last = compose._runs_for(root, t["id"], "implementer", "")
+            last = [r for r, _ in store.ticket_runs(root, t["id"], "implementer", finished=True)]
             if last and last[-1] != t.get("conflict_counted_run"):
                 t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
                 t["conflict_counted_run"] = last[-1]
@@ -997,10 +994,7 @@ def merge_cmd(a, root, cfg):
         for s in store.subtickets_of(root, t["parent"]):
             if s["status"] == "waiting-dependencies" and all(
                     store.load_ticket(root, dep)["status"] in subtickets.SATISFIED for dep in s["depends_on"]):
-                s["status"] = "ready-for-implementer"
-                s["history"].append({"ts": store.now(), "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "merge"})
-                store.save_ticket(root, s)
-                store.log_event(root, "ticket.transition", ticket=s["id"], **{"from": "waiting-dependencies", "to": "ready-for-implementer", "by": "merge"})
+                store.record_transition(root, s, "ready-for-implementer", "merge")
                 released.append(s["id"])
     gitops.remove_worktree(repo, root / "worktrees" / t["id"])
     out({"ok": True, "id": t["id"], "state": "merged", "base_before": before, "main_after": after, "released": released})
@@ -1060,11 +1054,7 @@ def ticket_parent_check(a, root, cfg):
         raise Refused(f"{parent['id']} has no sub-tickets")
     subs, superseded = subtickets.split_plan(every)
     if all(s["status"] == "merged" for s in subs) and parent["status"] == "planned":
-        frm = parent["status"]
-        parent["status"] = "ready-for-parent-verify"
-        parent["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
-        store.save_ticket(root, parent)
-        store.log_event(root, "ticket.transition", ticket=parent["id"], **{"from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
+        store.record_transition(root, parent, "ready-for-parent-verify", "parent-check")
     reuse = _reused_subticket_run(root, cfg, parent) if parent["status"] == "ready-for-parent-verify" else None
     out({"ok": True, "id": parent["id"], "state": parent["status"],
          "subtickets": {s["id"]: s["status"] for s in subs}, "superseded": [s["id"] for s in superseded],
@@ -1087,6 +1077,21 @@ def _next_n(d: Path, kind: str) -> int:
     return len(list(d.glob(f"{kind}-*"))) + 1
 
 
+def _refuse_unless_applies(root: Path, text: str, refusal: str) -> None:
+    """Refuse spec `text` when it does not validate or its deltas do not apply to current truth."""
+    _, deltas, errors = specstore.validate(text)
+    errors += specstore.applies(root, deltas) if not errors else []
+    if errors:
+        raise Refused(f"{refusal}: " + "; ".join(errors))
+
+
+def _copy_record(d: Path, kind: str, src) -> Path:
+    """Copy `src` into approvals directory `d` as the next `<kind>-<n>.md`."""
+    dest = d / f"{kind}-{_next_n(d, kind)}.md"
+    shutil.copyfile(src, dest)
+    return dest
+
+
 def approve_spec(a, root, cfg):
     t = store.load_ticket(root, a.id)
     if a.edit:
@@ -1099,10 +1104,7 @@ def approve_spec(a, root, cfg):
     pinned: list[str] = []
     if specstore.is_active(root):
         # Part K: refuse a malformed version or a delta that does not apply; nothing is written.
-        _, deltas, errors = specstore.validate(text)
-        errors += specstore.applies(root, deltas) if not errors else []
-        if errors:
-            raise Refused("spec not pinned: " + "; ".join(errors))
+        _refuse_unless_applies(root, text, "spec not pinned")
     if t["status"] != "awaiting-spec-gate":
         raise Refused(f"{t['id']} is {t['status']}, not awaiting-spec-gate")
     if a.edit:
@@ -1129,8 +1131,7 @@ def request_changes(a, root, cfg):
     if t["status"] != "awaiting-spec-gate":
         raise Refused(f"{t['id']} is {t['status']}, not awaiting-spec-gate")
     d = _approval_dir(root, t["id"])
-    dest = d / f"changes-{_next_n(d, 'changes')}.md"
-    shutil.copyfile(a.notes, dest)
+    dest = _copy_record(d, "changes", a.notes)
     frm = t["status"]
     t["status"] = "ready-for-spec-writer"
     t["round"]["spec"] = 0
@@ -1193,18 +1194,15 @@ def resolve(a, root, cfg):
                           f"implementer's run start; {t['id']} is {st} ({reason or 'no park'})")
         if reason.startswith("ESCALATE from reviewer"):
             # Back to its checks, same round: the reviewer runs again with the ruling in its input.
-            head, moved = t.get("head"), _set_aside_failed_rows(root, t)
-            store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
-            dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
-            shutil.copyfile(a.ruling, dest)
+            head, moved = _supersede(root, t)
+            dest = _copy_record(d, "ruling", a.ruling)
             move("checks-in-flight", "ruling", {"ruling": _rel(root, dest), "head": head, "superseded": moved})
             return
         if reason.startswith("BLOCKED") or start_bug:  # an implementer's or the gate's BLOCKED: back to the implementer, same round
             to = "ready-for-implementer"
         else:
             to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
-        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
-        shutil.copyfile(a.ruling, dest)
+        dest = _copy_record(d, "ruling", a.ruling)
         move(to, "ruling", {"ruling": _rel(root, dest)})
     elif a.accept_paths:
         # The merge gate refused a protected path the pinned spec does not declare; the human accepts
@@ -1216,8 +1214,7 @@ def resolve(a, root, cfg):
         paths, _ = undeclared_protected(root, cfg, t, head)
         if not paths:
             raise Refused(f"nothing to accept: {t['id']} has no undeclared protected path at {head[:9]}")
-        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
-        shutil.copyfile(a.accept_paths, dest)
+        dest = _copy_record(d, "ruling", a.accept_paths)
         t["accepted_paths"] = sorted(set(t.get("accepted_paths") or []) | set(paths))
         move("checks-in-flight", "accept-paths", {"ruling": _rel(root, dest), "head": head, "accepted": paths})
     elif a.to:
@@ -1231,8 +1228,7 @@ def resolve(a, root, cfg):
         # (a harness or gate defect, a killed checker). Round unchanged.
         if st != "parked" or parked.get("from") not in ("checks-in-flight", "ready-for-merge"):
             raise Refused(f"--redispatch applies to a sub-ticket parked from its checks; {t['id']} is {st} (from {parked.get('from')})")
-        head, moved = t.get("head"), _set_aside_failed_rows(root, t)
-        store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
+        head, moved = _supersede(root, t)
         move("checks-in-flight", "redispatch", {"head": head, "superseded": moved})
     elif a.replan:
         # After a failed parent-close check: back to the planner with F as a ruling. Its new
@@ -1245,8 +1241,7 @@ def resolve(a, root, cfg):
         unmerged = [f"{s['id']} is {s['status']}" for s in subtickets.split_plan(subs)[0] if s["status"] != "merged"]
         if unmerged:
             raise Refused(f"--replan needs every sub-ticket merged: {', '.join(unmerged)}")
-        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
-        shutil.copyfile(a.replan, dest)
+        dest = _copy_record(d, "ruling", a.replan)
         move("ready-for-planner", "replan", {"ruling": _rel(root, dest)})
     elif a.close:
         if st == "closed":
@@ -1257,6 +1252,13 @@ def resolve(a, root, cfg):
                       "--replan F | --close")
 
 
+def _supersede(root: Path, t: dict) -> tuple:
+    """Set aside the head's failed result rows and log it; returns (head, roles moved)."""
+    head, moved = t.get("head"), _set_aside_failed_rows(root, t)
+    store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
+    return head, moved
+
+
 def _set_aside_failed_rows(root: Path, t: dict) -> list[str]:
     """Move the head's rows that did not pass under results/<head>/superseded-<n>/, so the join cannot
     read them as current and the build runs only the checkers with no row. The reviewer row stays
@@ -1648,10 +1650,7 @@ def stats_cmd(a):
 
 def spec_tasks(a, root, cfg):
     t = store.load_ticket(root, a.id)
-    d = _run_dir(root, a.run)
-    meta = store.read_yaml(d / "meta.yaml")
-    if meta.get("ticket") != t["id"] or meta.get("role") != "planner" or meta.get("status") != "PLANNED":
-        raise Refused(f"{a.run} is not a PLANNED planner run of {t['id']}")
+    d = _planner_run(root, a.run, t["id"])
     if not specstore.is_active(root):
         out({"ok": True, "id": t["id"], "skipped": "no spec store (factory init not run)"})
         return
@@ -1690,7 +1689,7 @@ def _reused_subticket_run(root: Path, cfg: dict, t: dict) -> str | None:
     if s["status"] != "merged" or not after or not s.get("head"):
         return None
     repo = gitops.repo_root()
-    if gitops.rev(repo, gitops.integration_branch(cfg, repo)) != after:
+    if gitops.integration_tip(cfg, repo) != after:
         return None
     row = store.results_for(root, s["head"]).get("verifier") or {}
     rid = row.get("run_id")
@@ -1718,16 +1717,11 @@ def _parent_close_verified(root: Path, cfg: dict, t: dict) -> str | None:
     if any(s["status"] != "merged" for s in subs):
         return None
     repo = gitops.repo_root()
-    runs = root / "runs"
-    for d in sorted(runs.iterdir()) if runs.exists() else []:
-        mp = d / "meta.yaml"
-        if not mp.exists():
-            continue
-        m = store.read_yaml(mp)
-        if m.get("ticket") != t["id"] or m.get("role") != "verifier" or m.get("status") != "VERIFIED" or not m.get("head"):
+    for rid, m in store.ticket_runs(root, t["id"], "verifier"):
+        if m.get("status") != "VERIFIED" or not m.get("head"):
             continue
         if all(gitops.head_contains(repo, m["head"], s["merge"]["main_after"]) for s in subs if s["merge"].get("main_after")):
-            return d.name
+            return rid
     return _reused_subticket_run(root, cfg, t)
 
 
@@ -1758,10 +1752,7 @@ def status_parse(a, root, cfg):
 
 
 def log_tail(a, root, cfg):
-    files = sorted((root / "log").glob("*.jsonl")) if (root / "log").exists() else []
-    lines: list[str] = []
-    for p in files:
-        lines.extend(p.read_text(encoding="utf-8").splitlines())
+    lines = list(store.log_lines(root))
     if a.event:
         lines = [ln for ln in lines if json.loads(ln).get("event") == a.event]
     if a.ticket:
diff --git a/factory/compose.py b/factory/compose.py
index 893a8f8..e5bd846 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -13,19 +13,6 @@ from pathlib import Path
 from factory import instance, specstore, store, subtickets
 
 
-def _runs_for(root: Path, ticket: str, role: str, exclude: str) -> list[str]:
-    runs = root / "runs"
-    out = []
-    if runs.exists():
-        for p in sorted(runs.iterdir()):
-            if p.name == exclude or not (p / "meta.yaml").exists():
-                continue
-            m = store.read_yaml(p / "meta.yaml")
-            if m.get("ticket") == ticket and m.get("role") == role and m.get("finished"):
-                out.append(p.name)
-    return out
-
-
 def _approvals(root: Path, ticket: str, kind: str) -> list[Path]:
     d = root / "approvals" / ticket
     return sorted(d.glob(f"{kind}-*.md")) if d.exists() else []
@@ -43,7 +30,7 @@ def triage_capabilities(root: Path, tid: str) -> list[str] | None:
     finished triage output, split on commas and whitespace, backticks and periods stripped, unknown
     names (`none`, `new`) dropped. None when there is no such run or no such line: the ticket then
     gets the whole of current truth and the decision log, as before the line existed."""
-    runs = _runs_for(root, tid, "triage", "")
+    runs = [r for r, _ in store.ticket_runs(root, tid, "triage", finished=True)]
     p = root / "runs" / runs[-1] / "output.md" if runs else None
     if p is None or not p.exists():
         return None
@@ -69,8 +56,8 @@ def capability_index(paths: list[Path]) -> str:
 
 
 def _last_run_meta(root: Path, ticket: str, role: str, exclude: str) -> dict | None:
-    runs = _runs_for(root, ticket, role, exclude)
-    return store.read_yaml(root / "runs" / runs[-1] / "meta.yaml") if runs else None
+    runs = [m for r, m in store.ticket_runs(root, ticket, role, finished=True) if r != exclude]
+    return runs[-1] if runs else None
 
 
 def gate_entries(cfg: dict) -> list[tuple[str, list[str] | None]]:
@@ -282,11 +269,11 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
             parts.append("\n## Capability index: every capability in current truth\n\nName the capabilities this "
                          "request touches on your `Capabilities:` line. The spec writer receives those in full and "
                          "this index for the rest.\n\n" + capability_index(every))
-        prior = _runs_for(root, tid, "triage", run_id)
+        prior = [r for r, _ in store.ticket_runs(root, tid, "triage", finished=True) if r != run_id]
         if prior:
             add(f"runs/{prior[-1]}/output.md", "Your previous Triage output (the question you asked is answered above)")
     elif role == "spec_writer":
-        tri = _runs_for(root, tid, "triage", run_id)
+        tri = [r for r, _ in store.ticket_runs(root, tid, "triage", finished=True) if r != run_id]
         if tri:
             add(f"runs/{tri[-1]}/output.md", "Ticket (Triage output)")
         add(t["request"], "Request (raw)")
@@ -294,7 +281,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         add_truth(sel)
         add_decisions()
         if rnd >= 1 and version >= 1:
-            crit = _runs_for(root, tid, "critic", run_id)
+            crit = [r for r, _ in store.ticket_runs(root, tid, "critic", finished=True) if r != run_id]
             if crit:
                 add(f"runs/{crit[-1]}/output.md", "Critic findings on your previous version")
             add(f"specs/{tid}/v{version}.md", f"Your previous spec (v{version})")
@@ -314,7 +301,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         add_decisions()
         add_approved_changes()
         if rnd >= 2 and version >= 2:
-            crit = _runs_for(root, tid, "critic", run_id)
+            crit = [r for r, _ in store.ticket_runs(root, tid, "critic", finished=True) if r != run_id]
             if crit:
                 add(f"runs/{crit[-1]}/output.md", "Your prior findings (round %d)" % (rnd - 1))
             # the smaller of the diff and the previous version: a rewrite's diff outgrows the version
@@ -400,7 +387,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
             else:
                 add(f"specs/{tid}/subticket.md", f"Sub-ticket {tid}")
                 add_spec(f"specs/{parent}/v{av}.md", f"Parent spec (v{av}, pinned)")
-                impl = _runs_for(root, tid, "implementer", run_id)
+                impl = [r for r, _ in store.ticket_runs(root, tid, "implementer", finished=True) if r != run_id]
                 if impl:
                     add(f"runs/{impl[-1]}/output.md", "PR description (the implementer's output)")
                 diff_rel = f"runs/{run_id}/diff.patch"
@@ -409,8 +396,8 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
                 prnd = t["round"]["pr"]
                 if prnd >= 2:  # both checkers' findings from the previous round (doc §Routing table, Implementer row)
                     for r in ("reviewer", "verifier"):
-                        prev = [x for x in _runs_for(root, tid, r, run_id)
-                                if store.read_yaml(root / "runs" / x / "meta.yaml").get("round") == prnd - 1]
+                        prev = [x for x, m in store.ticket_runs(root, tid, r, finished=True)
+                                if x != run_id and m.get("round") == prnd - 1]
                         if prev:
                             who = "Your" if r == role else f"The {r}'s"
                             add(f"runs/{prev[-1]}/output.md", f"{who} prior findings (round {prnd - 1})")
diff --git a/factory/cost.py b/factory/cost.py
index 77640fc..6037e08 100644
--- a/factory/cost.py
+++ b/factory/cost.py
@@ -39,6 +39,12 @@ def _records(path: str):
                 continue
 
 
+def _log_records(store: str):
+    """Each parseable record of a store's event log, `log/*.jsonl` in file-name order."""
+    for lf in sorted(glob.glob(os.path.join(store, "log", "*.jsonl"))):
+        yield from _records(lf)
+
+
 def _user_text(o: dict) -> str | None:
     """The text of a user record, or None for any other record."""
     if o.get("type") != "user":
@@ -126,15 +132,14 @@ def _store_paths(store: str) -> set[str]:
     """A store's path and its paths before each `store.migrated` event in its log."""
     here = os.path.realpath(store)
     paths = {here}
-    for lf in glob.glob(os.path.join(store, "log", "*.jsonl")):
-        for e in _records(lf):
-            if e.get("event") != "store.migrated" or not e.get("from") or not e.get("to"):
-                continue
-            src, dst = e["from"], e["to"].rstrip("/")
-            if os.path.isabs(src):
-                paths.add(os.path.realpath(src))
-            elif here.endswith(os.sep + os.path.normpath(dst)):
-                paths.add(os.path.realpath(os.path.join(here[:-len(os.path.normpath(dst))], src)))
+    for e in _log_records(store):
+        if e.get("event") != "store.migrated" or not e.get("from") or not e.get("to"):
+            continue
+        src, dst = e["from"], e["to"].rstrip("/")
+        if os.path.isabs(src):
+            paths.add(os.path.realpath(src))
+        elif here.endswith(os.sep + os.path.normpath(dst)):
+            paths.add(os.path.realpath(os.path.join(here[:-len(os.path.normpath(dst))], src)))
     return paths
 
 
diff --git a/factory/drive.py b/factory/drive.py
index 74392cc..0b2dee2 100644
--- a/factory/drive.py
+++ b/factory/drive.py
@@ -189,12 +189,12 @@ class Driver:
             # check): parked verbatim, so `resolve --ruling` treats it as an implementer's BLOCKED.
             err = start.get("error")
             blocked = isinstance(err, str) and err.startswith("BLOCKED ")
-            self.park(ticket, err if blocked else f"harness-bug: run start {role}: {start.get('stderr') or ''}", [])
+            self.park(ticket, err if blocked else _harness_bug(f"run start {role}", start), [])
             return None
         rid = start["run_id"]
         comp = call("run", "compose", rid)
         if not comp["ok"]:
-            self.park(ticket, f"harness-bug: run compose {role}: {comp.get('stderr') or ''}", [rid])
+            self.park(ticket, _harness_bug(f"run compose {role}", comp), [rid])
             return None
         run = os.path.realpath(self.root / "runs" / rid)
         wt = os.path.realpath(start["worktree"]) if start.get("worktree") else None
@@ -222,19 +222,17 @@ class Driver:
             # A failed call is treated as a thrown agent() call: the run is recorded KILLED and the
             # ticket parked with the error, so no run is left in flight. No retry.
             call("run", "finish", rid, "--status-override", "KILLED", "--reply", reply_path)
-            if role in CHECKERS:
-                call("run", "cleanup", rid)
+            _cleanup_checker(role, rid)
             self.running.pop(rid, None)
             self.step(f"{role} {rid}: KILLED", ticket)
             self.park(ticket, f"agent call failed: {role}: {_failure_message(reply, err, code)}", [rid])
             return None
         # run finish reads the output file for every run: a missing or blank one is EMPTY-OUTPUT.
         fin = call("run", "finish", rid, "--reply", reply_path)
-        if role in CHECKERS:
-            call("run", "cleanup", rid)
+        _cleanup_checker(role, rid)
         self.running.pop(rid, None)
         if not fin["ok"]:
-            self.park(ticket, f"harness-bug: run finish {role}: {fin.get('stderr') or ''}", [rid])
+            self.park(ticket, _harness_bug(f"run finish {role}", fin), [rid])
             return None
         if fin.get("parked"):  # the tripwire saw a listed live file change: do not route on STATUS
             self.step(f"parked: {fin['parked']}", ticket)
@@ -289,11 +287,11 @@ class Driver:
                     return parked
                 added = call("spec", "add", T, "--from-run", w["runId"])
                 if not added["ok"]:
-                    self.park(T, f"harness-bug: spec add: {added.get('stderr') or ''}", [w["runId"]])
+                    self.park(T, _harness_bug("spec add", added), [w["runId"]])
                     return parked
                 tr = self.transition("ready-for-critic", "spec:init")
                 if not tr["ok"]:
-                    self.park(T, f"harness-bug: transition to critic: {tr.get('stderr') or ''}", [w["runId"]])
+                    self.park(T, _harness_bug("transition to critic", tr), [w["runId"]])
                     return parked
                 rnd = _spec_round(tr, rnd)
                 state = "ready-for-critic"
@@ -314,7 +312,7 @@ class Driver:
             if rnd < self.max_spec:
                 tr = self.transition("ready-for-spec-writer", "spec:+1")
                 if not tr["ok"]:
-                    self.park(T, f"harness-bug: round increment refused: {tr.get('stderr') or ''}", [c["runId"]])
+                    self.park(T, _harness_bug("round increment refused", tr), [c["runId"]])
                     return parked
                 rnd = _spec_round(tr, rnd)
                 state = "ready-for-spec-writer"
@@ -331,7 +329,7 @@ class Driver:
             # A spec that needs one sub-ticket becomes it without a planner run; the harness decides which.
             whole = call("plan", "whole-spec", T)
             if not whole["ok"]:
-                self.park(T, f"harness-bug: plan whole-spec: {whole.get('stderr') or ''}", [])
+                self.park(T, _harness_bug("plan whole-spec", whole), [])
                 return parked
             if whole.get("planner") == "skipped":
                 self.step(f"planner skipped ({whole.get('reason')}); one sub-ticket from the whole spec")
@@ -350,7 +348,7 @@ class Driver:
                                    ("subticket add", ("subticket", "add", T, "--run", p["runId"]))):
                     res = call(*argv)
                     if not res["ok"]:
-                        self.park(T, f"harness-bug: {what}: {res.get('stderr') or ''}", [p["runId"]])
+                        self.park(T, _harness_bug(what, res), [p["runId"]])
                         return parked
             self.transition("planned")
             state = "planned"
@@ -365,7 +363,7 @@ class Driver:
             while True:
                 ready = call("ticket", "ready-implementers", T)
                 if not ready["ok"]:
-                    self.park(T, f"harness-bug: ready-implementers: {ready.get('stderr') or ''}", [])
+                    self.park(T, _harness_bug("ready-implementers", ready), [])
                     return parked
                 # A parent planned with no sub-tickets (e.g. by an older intake): create them once from
                 # the planner run its recorded plan names, or park the parent saying why.
@@ -443,19 +441,19 @@ class Driver:
                     return
                 moved = call("ticket", "head", st)
                 if not moved["ok"]:
-                    self.park(st, f"harness-bug: ticket head: {moved.get('stderr') or ''}", [impl["runId"]])
+                    self.park(st, _harness_bug("ticket head", moved), [impl["runId"]])
                     return
                 if moved.get("merge_refused"):
                     # A conflict run that did not merge the integration branch in: no point checking that head.
                     j = call("ticket", "join", st)
                     if j["ok"] and j.get("decision") == "conflict":
                         continue
-                    self.park(st, (j.get("reason") or "") if j["ok"] else f"harness-bug: join: {j.get('stderr') or ''}",
+                    self.park(st, (j.get("reason") or "") if j["ok"] else _harness_bug("join", j),
                               [impl["runId"]])
                     return
                 tr = self.transition("checks-in-flight", "pr:init", st)
                 if not tr["ok"]:
-                    self.park(st, f"harness-bug: transition to checks: {tr.get('stderr') or ''}", [impl["runId"]])
+                    self.park(st, _harness_bug("transition to checks", tr), [impl["runId"]])
                     return
             elif show["state"] != "checks-in-flight":
                 return  # parked, merged, closed or waiting: nothing for this loop to do
@@ -465,13 +463,13 @@ class Driver:
             head_now = call("ticket", "head", st)
             sha = head_now.get("head") if head_now["ok"] else None
             if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
-                self.park(st, f"harness-bug: no head for the checkers: {head_now.get('stderr') or ''}", [])
+                self.park(st, _harness_bug("no head for the checkers", head_now), [])
                 return
             roles = list(CHECKERS)
             if not implemented:
                 rows = call("results", "show", st)
                 if not rows["ok"]:
-                    self.park(st, f"harness-bug: results show: {rows.get('stderr') or ''}", [])
+                    self.park(st, _harness_bug("results show", rows), [])
                     return
                 missing = rows.get("missing") or []
                 roles = [r for r in roles if r in missing or (r == "verifier" and "ci" in missing)]
@@ -483,7 +481,7 @@ class Driver:
                 rec = call("results", "record", st, "--head", sha, "--role", role, "--output", r["outputPath"],
                            "--run", r["runId"], *(["--killed"] if r["status"] == "KILLED" else []))
                 if not rec["ok"]:
-                    self.park(st, f"harness-bug: results record {role}: {rec.get('stderr') or ''}", [r["runId"]])
+                    self.park(st, _harness_bug(f"results record {role}", rec), [r["runId"]])
                     return None
                 return r
 
@@ -493,7 +491,7 @@ class Driver:
             outs = [r["runId"] for r in checked]
             join = call("ticket", "join", st)
             if not join["ok"]:
-                self.park(st, f"harness-bug: join: {join.get('stderr') or ''}", outs)
+                self.park(st, _harness_bug("join", join), outs)
                 return
             decision, reason = join.get("decision"), join.get("reason") or ""
             self.step(f"join: {decision} ({reason})", st)
@@ -514,12 +512,12 @@ class Driver:
                     self.transition("ready-for-implementer", None, st)
                     continue
                 self.park(st, (again.get("reason") or "") if again["ok"] and again.get("decision") == "park"
-                          else f"harness-bug: merge: {m.get('stderr') or ''}", outs)
+                          else _harness_bug("merge", m), outs)
                 return
             if decision == "revise":
                 tr = self.transition("ready-for-implementer", join.get("round_op"), st)
                 if not tr["ok"]:
-                    self.park(st, f"harness-bug: round increment refused: {tr.get('stderr') or ''}", outs)
+                    self.park(st, _harness_bug("round increment refused", tr), outs)
                     return
                 continue
             if decision == "conflict":
@@ -571,8 +569,7 @@ class Driver:
             await asyncio.gather(*waits)
         for rid, r in list(self.running.items()):
             call("run", "finish", rid, "--status-override", "KILLED")
-            if r["role"] in CHECKERS:
-                call("run", "cleanup", rid)
+            _cleanup_checker(r["role"], rid)
             self.running.pop(rid)
             self.procs.pop(rid, None)
             self.step(f"{r['role']} {rid}: KILLED", r["ticket"])
@@ -599,6 +596,17 @@ async def _all(aws) -> list:
         raise
 
 
+def _harness_bug(what: str, res: dict) -> str:
+    """The park reason for a store command `what` that failed with result `res`."""
+    return f"harness-bug: {what}: {res.get('stderr') or ''}"
+
+
+def _cleanup_checker(role: str, rid: str) -> None:
+    """Remove a checker run's checkout; other roles have none."""
+    if role in CHECKERS:
+        call("run", "cleanup", rid)
+
+
 def _spec_round(tr: dict, rnd: int) -> int:
     spec = (tr.get("round") or {}).get("spec")
     return spec if isinstance(spec, int) and not isinstance(spec, bool) else rnd
@@ -623,7 +631,7 @@ def _same_ticket_guard(root: Path, tid: str) -> None:
     if not store.ticket_path(root, tid).exists():
         return
     t = store.load_ticket(root, tid)
-    runs = [r for x in (t, *store.subtickets_of(root, tid)) for r in x.get("in_flight") or []]
+    runs = store.in_flight_runs(root, t)
     if runs:
         raise store.Refused(f"{tid} has runs in flight on it or its sub-tickets: {', '.join(runs)}; "
                             "drive it again once they finish")
diff --git a/factory/gitops.py b/factory/gitops.py
index 253f6bd..c1484be 100644
--- a/factory/gitops.py
+++ b/factory/gitops.py
@@ -39,6 +39,11 @@ def rev(repo: Path, ref: str) -> str:
     return git(repo, "rev-parse", ref)
 
 
+def integration_tip(cfg: dict, repo: Path) -> str:
+    """The commit at the tip of the integration branch."""
+    return rev(repo, integration_branch(cfg, repo))
+
+
 def branch_of(tid: str) -> str:
     return f"factory/{tid}"
 
diff --git a/factory/specstore.py b/factory/specstore.py
index 2e31ea4..85c05b3 100644
--- a/factory/specstore.py
+++ b/factory/specstore.py
@@ -270,19 +270,12 @@ def critic_rounds(root: Path, tid: str) -> str:
     """`## Critic rounds`: per finished critic run of the ticket, oldest first."""
     from factory import status  # local import: status has no store dependency
 
-    runs = root / "runs"
     entries = []
-    if runs.exists():
-        for d in sorted(runs.iterdir()):
-            mp = d / "meta.yaml"
-            if not mp.exists():
-                continue
-            m = store.read_yaml(mp)
-            if m.get("ticket") != tid or m.get("role") != "critic" or not m.get("finished"):
-                continue
-            body = (d / "output.md").read_text(encoding="utf-8") if (d / "output.md").exists() else ""
-            entries.append(f"round {m.get('round')} · spec v{m.get('spec_version')} · {m['run_id']} · {m.get('status')}\n\n"
-                           + status.strip_trailer(body).rstrip() + "\n")
+    for run_id, m in store.ticket_runs(root, tid, "critic", finished=True):
+        out = root / "runs" / run_id / "output.md"
+        body = out.read_text(encoding="utf-8") if out.exists() else ""
+        entries.append(f"round {m.get('round')} · spec v{m.get('spec_version')} · {m['run_id']} · {m.get('status')}\n\n"
+                       + status.strip_trailer(body).rstrip() + "\n")
     return "## Critic rounds\n\n" + ("\n".join(entries) if entries else "none\n")
 
 
diff --git a/factory/stats.py b/factory/stats.py
index e56e6d1..a8c8040 100644
--- a/factory/stats.py
+++ b/factory/stats.py
@@ -21,7 +21,7 @@ from datetime import datetime
 from pathlib import Path
 
 from factory.cli import ROLES
-from factory.cost import _records, _when, gate_failures, match_transcripts, transcript_usage
+from factory.cost import _log_records, _when, gate_failures, match_transcripts, transcript_usage
 from factory.store import Refused, read_yaml
 
 # Verdicts that change what happens next, from any role.
@@ -69,10 +69,9 @@ def _load(store: str) -> tuple[list[dict], list[dict]]:
         m.update(_store=store, _id=os.path.basename(d), _dir=d, _started=_when(m.get("started")))
         runs.append(m)
     events = []
-    for lf in sorted(glob.glob(os.path.join(store, "log", "*.jsonl"))):
-        for e in _records(lf):
-            if isinstance(e, dict) and e.get("ts"):
-                events.append({**e, "_ts": _when(e["ts"])})
+    for e in _log_records(store):
+        if isinstance(e, dict) and e.get("ts"):
+            events.append({**e, "_ts": _when(e["ts"])})
     events.sort(key=lambda e: e["_ts"])
     return runs, events
 
diff --git a/factory/store.py b/factory/store.py
index 9e12804..7ef578b 100644
--- a/factory/store.py
+++ b/factory/store.py
@@ -92,6 +92,13 @@ def log_event(root: Path, event: str, **fields) -> dict:
     return line
 
 
+def log_lines(root: Path):
+    """Each line of the event log, `log/*.jsonl` in file-name order; the caller parses it."""
+    d = root / "log"
+    for p in sorted(d.glob("*.jsonl")) if d.exists() else []:
+        yield from p.read_text(encoding="utf-8").splitlines()
+
+
 def ticket_path(root: Path, tid: str) -> Path:
     return root / "tickets" / f"{tid}.yaml"
 
@@ -116,19 +123,46 @@ def save_ticket(root: Path, t: dict) -> None:
 def clear_scratch(root: Path, tid: str) -> None:
     """Remove runs/<id>/scratch of each finished run of ticket `tid`; runs in flight, other tickets'
     runs and every path outside runs/*/scratch are left alone."""
-    for d in (root / "runs").glob("*/scratch"):
-        meta = d.parent / "meta.yaml"
-        m = read_yaml(meta) if meta.exists() else None
-        if not m or m.get("ticket") != tid or not m.get("finished"):
-            continue
+    for rid, _ in ticket_runs(root, tid, finished=True):
+        d = root / "runs" / rid / "scratch"
         if d.is_symlink():
             d.unlink()
-        else:
+        elif d.is_dir():
             # factory: plain rmtree fails on a read-only directory inside scratch (a Go module cache,
             # say); add a chmod-and-retry handler if a run ever leaves one
             shutil.rmtree(d)
 
 
+def ticket_runs(root: Path, ticket: str, role: str | None = None, finished: bool = False):
+    """(run_id, meta) of each run of `ticket` in run-id order, only `role`'s when given and only
+    finished ones when `finished`. A run whose meta.yaml is missing or still empty is skipped."""
+    runs = root / "runs"
+    for d in sorted(runs.iterdir()) if runs.exists() else []:
+        mp = d / "meta.yaml"
+        m = read_yaml(mp) if mp.exists() else None
+        if (not m or m.get("ticket") != ticket or (role is not None and m.get("role") != role)
+                or (finished and not m.get("finished"))):
+            continue
+        yield d.name, m
+
+
+def in_flight_runs(root: Path, t: dict) -> list[str]:
+    """The runs in flight on ticket `t` and on its sub-tickets."""
+    return [r for x in (t, *subtickets_of(root, t["id"])) for r in x.get("in_flight") or []]
+
+
+def record_transition(root: Path, t: dict, to: str, by: str, history: dict | None = None,
+                      event: dict | None = None) -> str:
+    """Move ticket `t` to status `to`: append its history entry (plus `history`), save it and log
+    `ticket.transition` (plus `event`). Returns the status it left."""
+    frm = t["status"]
+    t["status"] = to
+    t["history"].append({"ts": now(), "from": frm, "to": to, "by": by, **(history or {})})
+    save_ticket(root, t)
+    log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": to, "by": by, **(event or {})})
+    return frm
+
+
 def park_ticket(root: Path, t: dict, reason: str, outputs: list[str], question: str | None = None,
                 by: str = "park") -> None:
     """Park ticket `t` (the caller has checked it is not parked or closed): record where it came
