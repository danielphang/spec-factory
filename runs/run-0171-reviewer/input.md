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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0171-reviewer/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0171-reviewer/wt` (branch `factory/T-0019.1`, base `1c5f6a7aa096c39b9a9f355b2dee286ccd3b4a84`, head `5f43cba12a208e095e48872471e4f6f2f9dc47f5`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Sub-ticket T-0019.1

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

## Parent spec (v2, pinned)

=== proposal.md
## Problem

Two faults in the spec factory's harness put the operator's live data and build budget at risk. Both were hit on 2026-10-04 while the factory built a change for the Nanobot chat bot. The spec factory runs each requested change through a chain of AI agents called roles: triage, spec writer, critic, planner, implementer, reviewer and verifier. The harness is the code that composes each role's input and records what it returns.

**A role's test run can overwrite live production data.** Roles run tests and scripts with the operator's real home directory as `HOME`. On the Nanobot instance (the factory's other target repository), an implementer's new tests computed a file path from `HOME` before the test fixture redirected it. They overwrote the live bot's per-chat permission file and its backup in `~/.nanobot/`, and the operator restored them by hand. Each instance lists sensitive locations, such as live credentials, as protected paths in its config. The harness only prints that list into the rules every role reads, and nothing points a role's commands away from those locations. A role is handed ready-made commands in one case only: the gate commands, the instance's lint and test commands that the implementer and verifier must run. Those run under a throwaway `HOME` only where an instance wrote that into its own config. Nanobot did; this repository did not. Triage, the spec writer, the critic and the planner are handed no command at all, so they copy the plain test command from the instance's briefing, the text every role reads first.

**The planner's dependency order can vanish without a word.** The planner splits an approved spec into sub-tickets, units of work that each become one branch and one merge. For each, it writes a `Depends on:` line naming the sub-tickets that must merge first. It also writes a `Parallel-safe:` line saying whether the sub-ticket may be built while its siblings are. The harness reads those lines with a pattern that skips a line starting with a `- ` list bullet. A sub-ticket whose lines are written that way is recorded as having no dependencies and as not parallel-safe, and nothing reports it. All eight sub-tickets of one Nanobot plan were written that way and were dispatched out of order. Every one of them ended `parked`, the state for a ticket the build has stopped on. A sub-ticket with no `Depends on:` line at all gets the same silent default.

The fix hands every role a wrapper that runs a command under a throwaway `HOME`, with the gate commands already wrapped. It adds a rule to the shared preamble, the rules text at the top of every role's prompt: run code only through that wrapper, and never run anything that could write a protected path outside the repository. It also makes the harness read bulleted field lines and refuse a sub-ticket that has no `Depends on:` line. The wrapper is guidance the role follows, not an operating-system control: a command can still write an absolute path. The two faults share no code, so they are built as two separate changes.

## Evidence

Checked on `main` at `17efb50`, the same commit as v1; no harness code changed between `9b73efe`, where the last harness change merged, and that commit. On this round I re-ran "Dash-bulleted field lines keep their dependencies" and the implementer's gate-command line on `17efb50`, with the same results as v1.

- The live-data write is recorded by the run that caused it. The Nanobot store's `runs/run-0080-implementer/output.md` says the first run of `uv run pytest tests/policy` "with the real `HOME`" wrote `/Users/dphang/.nanobot/policies.json` and `policies.json.bak`. It quotes the run's own error, `FileExistsError: [Errno 17] File exists: '/Users/dphang/.nanobot/policies.json'`. It names the cause: the test module imported the path function by name at collection, before the conftest fixture replaced it. A test that resolves a path from `HOME` early reaches the real home whenever the real `HOME` is set.
- The harness sets no `HOME` for anything a role runs. `grep -rn HOME factory bin` prints nothing. Roles are started by the workflow scripts' `agent()` calls (`factory/workflows/build.js` lines 75-86), which take no environment option. So the harness cannot change a role's own environment. It can only hand the role a command form to use.
- Protected paths are text, not a control. The only reader of `protected_paths` is `fill_preamble` (`factory/instance.py` lines 168-179). It writes the list into the preamble's "Protected paths for this repo" line. This repo's `.factory/instance.yaml` line 19 declares `credentials: ["~/.nanobot/**"]`.
- Only implementers and verifiers are handed commands, and this repo's are not isolated. `factory/compose.py` lines 128-132 put the gate commands verbatim in the "Where you work" section of build-role inputs only. Composing an implementer input on a scratch store printed ``Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` ``. Neither command sets `HOME`. A composed triage input had only three sections: `## Context for this run`, `## Output file` and `## Request (raw, with any answers appended)`. No section tells the role how to run code.
- The Nanobot instance worked around the gap by hand, in its own files. Its gate commands set `HOME="$(cd "$(mktemp -d)" && pwd -P)"`, a fresh temporary directory per run. They also pin `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` to the real home, and the config comment says why: "so the temp HOME does not re-download them". After the incident its briefing's test command was rewritten the same way, with a sentence telling every role to run repo code that way.
- A throwaway `HOME` changes which Python this repo's tests run on in a fresh checkout. The operator's `.venv/bin/python` here points into `/Users/dphang/.local/share/uv/python` (uv's managed Python 3.12; `uv python dir` prints that directory, and `uv cache dir` prints `/Users/dphang/.cache/uv`). In a fresh copy of `17efb50` with no `.venv`, `uv run --frozen -v` under a throwaway `HOME` searched the empty `$HOME/.local/share/uv/python`, then printed `Using CPython 3.14.5 interpreter at: /opt/homebrew/opt/python@3.14/bin/python3.14`, and downloaded the packages into an empty cache. `test_subtickets.py` and `test_instance.py` passed there (`28 passed in 11.26s`). So wrapping does not break this repo, but each new worktree builds a fresh `.venv` on whatever system Python is first on `PATH`, unless the instance keeps uv's two directories reachable. That is the job of `run_env` (Decisions).
- This repo's gate passes under a throwaway `HOME`. In v1, `(HOME="$(cd "$(mktemp -d)" && pwd -P)" uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `157 passed in 120.88s`. This round, the same command written with `export` printed `171 passed in 100.14s (0:01:40)` on the same commit (see verification.md). `git diff --check main...HEAD` under a throwaway `HOME` exits 0.
- The bullet fault reproduces through the command line. A plan whose three sub-tickets use `- Depends on:` and `- **Depends on:**` lines, added with `bin/factory subticket add T-0001 --file plan.md` on a scratch store, printed `"depends_on": []`, `"parallel_safe": false` and `"state": "ready-for-implementer"` for all three. So `ST-2`, which depends on `ST-1`, was ready to build at once. The same plan written with `* `, `**…**`, indented or plain lines keeps its dependencies: `ST-2` comes out `"depends_on": ["T-0001.1"]`, `"state": "waiting-dependencies"`.
- The cause is the field pattern and a silent default. `factory/subtickets.py` line 17 is `FIELD_RE = re.compile(r"^\s*\**\s*([A-Z][A-Za-z -]+?)\s*:\s*\**\s*(.*)$")`. Its leading `\**` consumes a `*` bullet as if it were emphasis, but nothing consumes `-`. Line 62 starts every sub-ticket at `"depends_on": [], "parallel_safe": False`, and nothing checks that a `Depends on:` line was read. A plan with `ST-2` missing its `Depends on:` line printed `exit=0` and created `T-0001.2` with `"depends_on": []`.
- The real plan used `- ` bullets. Every sub-ticket in the Nanobot store's `plans/T-0002.md` writes `- Depends on:` and `- Parallel-safe:`. All eight sub-tickets `T-0002.1` to `T-0002.8` are `parked`. Each has one implementer run, seven of them `BLOCKED`. The store log shows their `depends_on` and `parallel_safe` were later set by hand with `ticket set` at `2026-10-04T07:59:58Z`. The request puts the cost at about 3M tokens; I did not verify that figure.
- The planner prompt shows a form the harness cannot read. `factory/prompts/planner.md` lines 22-25 show `  ID / Title`, `  Depends on: none | IDs` and `  Parallel-safe: yes | no (reason)`, all indented. The head-line pattern (`HEAD_RE`, `factory/subtickets.py` line 16) accepts a sub-ticket's ID line only at column 0 or after a heading mark. So the example, copied literally, gives no sub-tickets at all. The prompt does not say that these lines are machine-read or that `Depends on:` is required.
- A pairwise answer reads as unconditional. The Nanobot plan writes lines like `- Parallel-safe: yes with T-0002.3, T-0002.4 and T-0002.7 … Not with T-0002.8`. Line 88 of `factory/subtickets.py` reads only a leading `yes`, so once bullets are read, that sub-ticket would be parallel-safe with every sibling, including the one it excludes.
- The three copies of each prompt block are identical today. The preamble block in `docs/design.md`, `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md` printed `SAME` under the awk-and-diff check in this spec's verification. So did the planner block and its two copies. The changelog's numbered entries run 1 to 47 with no gap.
- A spec writer's `NEEDS-SPLIT` goes to the critic exactly as `READY-FOR-CRITIC` does (`factory/workflows/intake.js` line 150), and the planner turns each named seam into sub-tickets. Marking this change `NEEDS-SPLIT` changes nothing but the planner's guidance.
- Earlier faults of the same class: an earlier planner head line in a form the parser did not expect (issue #13), and a plan normalised by hand before its sub-tickets could be created (`.factory/answers/T-0014-plan-normalised.md`).

## Root cause

- `factory/subtickets.py` line 17, `FIELD_RE`: no optional `- ` list bullet before the field name.
- `factory/subtickets.py` `parse`, lines 57-93: `depends_on` defaults to `[]`, and a block with no `Depends on:` line is accepted.
- `factory/compose.py` `compose`, lines 52-178: no role input says how to run code. `gate_commands` (lines 42-49) hands the instance's strings over unchanged, and only build roles receive them.
- `factory/prompts/preamble.md`, a byte-identical copy of the design doc's preamble block: no rule about `HOME` or about writes outside the repository.
- `factory/prompts/planner.md` lines 21-35, the design doc's planner block: the OUTPUT example indents the lines the harness parses and does not say that they are parsed.

## Out of scope

- OS-enforced write denial, such as Claude Code's sandbox settings, macOS `sandbox-exec` or a separate user account for roles. The operator decides this, and a separate investigation (issue #37) tracks it.
- Changing the environment a role process starts with. `agent()` has no environment option.
- Reading pairwise parallel-safety (`yes with A, not with B`). The parser keeps reading only a leading `yes`, and the planner prompt says how to write the line instead.
- Field lines in a numbered list or with a `+ ` bullet.
- Either instance's own files: `.factory/**` here and everything in `~/dev/nanobot-upstream`. Their `run_env` settings are Operator steps. The Nanobot `T-0002` sub-ticket records were already corrected by hand.
- Removing the temporary directories the wrapper leaves behind; the design doc says they are left.
- `agents/factory-planner.md`, which holds an older copy of the planner OUTPUT block (see Out-of-scope observations).
- The retro role's input, which `run compose` does not build.
- The `harness-bug:` label that `build.js` line 200 puts on a refused `subticket add`.

## Open questions

none

## Decisions

- Every role runs tests, scripts and prototypes through a wrapper the harness hands it, which sets `HOME` to a fresh temporary directory; the instance's gate commands reach a role already wrapped. Rejected: each instance writes `HOME` into its own commands and briefing, as Nanobot did by hand, because this repository's gate has none and nothing checks briefing prose.
- The wrapper is `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`, a subshell, so the export covers every part of a compound command. Rejected: a `HOME=… <command>` prefix, which covers only the first command of `a && b`.
- An instance keeps a tool's cache reachable by listing it in a new `run_env` key, whose variables the wrapper exports after `HOME`; `run_env` may not set `HOME`. Rejected: the request's per-instance "cannot run under a throwaway HOME" opt-out, because it would silently reopen the hole for every role on that instance.
- Both instances get `run_env` for uv's cache and its managed Pythons, set by the operator after the merge (Operator steps 1 and 3). This change does not write either instance's file, which is out of scope; until the operator sets it, a role's first test run in a new worktree here builds its `.venv` on the first system Python on `PATH`.
- A planner's field line may start with a `- ` or `* ` list bullet, and every sub-ticket must have a `Depends on:` line (`none` included); a plan with a sub-ticket that lacks one is refused with that sub-ticket named.
- A sub-ticket with no `Parallel-safe:` line still runs alone, as today.
- `Parallel-safe: yes` means safe alongside every sibling; a sub-ticket that is safe with only some siblings is written `no`.
- The change is built as two seams, one per fault (design.md, "Size and seams"). Both edit `docs/design.md` and `docs/changelog.md`, so they run one after the other, and they share one changelog entry.

## Risk

Blast radius: every role's composed input on every instance gains one section, and every gate command a role is handed changes form. A gate command that ends in a shell comment (`# …`) would comment out the wrapper's closing parenthesis. A `~/` in a gate command would expand to the throwaway home. Neither instance's gate commands contains `#` or `~` (checked: this repo's two, Nanobot's three). Nanobot's gate commands set their own `HOME` inside the wrapper; the inner setting wins and is another fresh directory, so the gate behaves as before. A plan that leaves out a `Depends on:` line, which used to be accepted, is now refused. The build then parks the parent with the refusal text (`factory/workflows/build.js` line 200), so no sub-ticket is built in the wrong order. Each wrapped run leaves one temporary directory behind. Nothing changes for running tickets until the runtime, the pinned checkout of the harness that runs tickets, is moved to a revision with this change and each instance accepts it.

Protected paths this change touches:
- harness: `factory/compose.py`, `factory/subtickets.py`, `factory/instance.template.yaml`, `factory/prompts/preamble.md`, `factory/prompts/planner.md`;
- generated: `docs/prompts/00-preamble.md`, `docs/prompts/04-planner.md`.

Guardrail paths: the preamble and the planner prompt are agent prompts; parts A and D of this ticket ask for those edits. New tests go in new files. No existing test changes.

Not touched: `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Gate policy: this is more than the operator's small-blast-radius pre-approval covers. It changes every role's preamble and input, across about a dozen files. It waits for the operator at the spec gate. As a prompt change, it also gets the operator's acceptance test before the runtime moves.

## Operator steps

These come after the merge, once the runtime (the pinned checkout of the harness that runs tickets) has moved to a revision with this change. Each instance refuses to run under a new harness revision until the operator accepts that revision for it with `--accept-harness <revision>`; do that for an instance before its steps below.

1. In the Nanobot instance's `.factory/instance.yaml`, add `run_env: {UV_CACHE_DIR: /Users/dphang/.cache/uv, UV_PYTHON_INSTALL_DIR: /Users/dphang/.local/share/uv/python}`. These are the two variables its gate commands already pin. Without them, every role's first test run in a new worktree downloads every package again into a fresh home.
2. Check: compose any role run on that instance and confirm that the `## Running code` wrapper in its `input.md` names both variables.
3. In this repo's `.factory/instance.yaml`, add the same `run_env` line, and commit it with the store. The two paths are what `uv cache dir` and `uv python dir` print here. Without them, a role's first test run in a new worktree builds its `.venv` on the first system Python on `PATH` (Homebrew 3.14 today) instead of uv's managed 3.12, and downloads the packages again. Check it as in step 2.

=== design.md
## Proposed change

### Size and seams (NEEDS-SPLIT)

About 300 changed lines in all, about half of them new tests. That fits one PR, but the two faults share no code, and a defect in one should not hold the other back. So the planner builds them as two seams:

- **S1, role runs under a throwaway HOME**: parts A, B, E2, E3, F1, and E1's first clause. About 200 lines. Scenarios: every scenario in `specs/role-run-isolation/spec.md`, plus "The README describes the wrapper and run_env", "The design doc and the instance template name run_env", "The changelog records the change in order" and "The change adds no whitespace errors".
- **S2, plan field lines**: parts C, D, F2, and E1's second clause. About 100 lines. Scenarios: every scenario in `specs/plan-parsing/spec.md`, plus "The changelog records the change in order", "The change adds no whitespace errors" and "This repo's gate suite passes under a throwaway HOME".

Both seams edit `docs/design.md` and `docs/changelog.md`, so they are not parallel-safe. Neither depends on the other's code. The seam that merges first writes the changelog entry with its own clause, and the second adds its clause to that same entry (E1).

**A. A running-code rule in the shared preamble.** (S1) In the design doc's preamble block (`## Shared preamble (every agent)` in `docs/design.md`), insert this section after the "Protected paths for this repo" placeholder line and before the blank line that precedes `GUARDRAIL PATHS`, with one blank line before it:

```
RUNNING CODE
- Run every test, script or prototype with HOME set to a fresh
  temporary directory, never the real one: use the wrapper in the
  "Running code" section of your input. That includes every test or
  check command your briefing, ticket or spec gives you.
- A throwaway HOME does not stop a write to an absolute path. Never
  run anything that could write a protected path outside the
  repository, such as live credentials or production state.
- If something you must run cannot work this way, stop and escalate.
```

Re-copy the block verbatim into `docs/prompts/00-preamble.md`, and make `factory/prompts/preamble.md` byte-identical to it (an existing test checks that).

**B. Every role is handed the wrapper** (S1; `factory/compose.py`, `factory/instance.template.yaml`, `docs/design.md`)
- B1. Add a reader for the instance key `run_env`. Absent or null means an empty mapping. Refuse with `store.Refused` (exit 2, no `input.md` written) in three cases: the value is not a mapping; a name does not match `[A-Za-z_][A-Za-z0-9_]*`; or a name is `HOME`. The message names `run_env` and the offending name.
- B2. The wrapper is the string `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"<vars>; <command>)`. `<vars>` is, for each `run_env` entry in file order, a space, `NAME=` and `shlex.quote(str(value))`. Example with `{T0019_CACHE: /tmp/t0019 cache}`: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)" T0019_CACHE='/tmp/t0019 cache'; <command>)`. To wrap a command, replace `<command>` with it.
- B3. In `compose`, for every role, add this section directly after the `## Output file` part, with the wrapper in place of `WRAPPER`:
  ```
  ## Running code
  Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `WRAPPER`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.
  ```
  The backticked wrapper is the only backticked text in the section that contains `<command>`. The section is not a store source, so `input_sources` does not change.
- B4. In the "Where you work" section of build-role inputs (lines 128-132), render each gate command through the wrapper, after `{integration}` is replaced. Example: `` `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)` ``. Change "exactly as written" to "exactly as written; each is already wrapped".
- B5. In `factory/instance.template.yaml`, after `environment_files`, add `run_env: {}` with this comment: variables the running-code wrapper exports after the throwaway `HOME`, for tools that keep a cache under `HOME` (for example `UV_CACHE_DIR`); `HOME` itself is refused.
- B6. In `docs/design.md`, in the **Role-context block** paragraph of the Harness section (line 54):
  - add "the variables kept for code runs (`run_env`)" to the parenthesised list of what `instance.yaml` holds;
  - at the end of the paragraph, add: "The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell with `HOME` set to a fresh temporary directory, exporting any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind."

**C. Bulleted field lines, and a required `Depends on:` line** (S2; `factory/subtickets.py`)
- C1. `FIELD_RE` accepts an optional `- ` or `* ` list bullet before the optional emphasis marks: `^\s*(?:[-*]\s+)?\**\s*([A-Z][A-Za-z -]+?)\s*:\s*\**\s*(.*)$`. `HEAD_RE` does not change, so a bullet still never starts a sub-ticket.
- C2. In `parse`, note whether each block had a `depends on` field line. After the block is read, if it had none, raise `ValueError` naming the planner's label: `<label>: no "Depends on:" line; write "Depends on: none" when it depends on nothing`. `subticket_add` already turns a `ValueError` into exit 2, before it writes anything (`factory/cli.py` lines 395-397).
- C3. Update the module docstring: field lines may carry a list bullet, and every sub-ticket needs a `Depends on:` line.

**D. The planner prompt shows the lines the harness reads.** (S2) In the design doc's `## 4. Planner / decomposer` block, replace the four lines from `For each sub-ticket:` through `  Parallel-safe: yes | no (reason)` with these eight lines:

```
For each sub-ticket, first these three lines, exactly as shown and each
at the start of its own line; the ID line may follow a heading mark.
The harness reads them. A sub-ticket with no "Depends on:" line is refused.
Parallel-safe "yes" means safe alongside every sibling; else write "no".
ID / Title
Depends on: none | IDs
Parallel-safe: yes | no (reason)
Then:
```

The indented `Scope:` line and everything after it stay as they are. Re-copy the block verbatim into `docs/prompts/04-planner.md` and `factory/prompts/planner.md`. All three are identical today.

**E. Documents**
- E1. `docs/changelog.md`: after the last numbered entry (47 today) and before `Declined:`, one entry with the next number, opening `<n>. After issue #36 (2026-10-04):`. It has two clauses, each written by its seam:
  - S1: a role's test run overwrote the Nanobot bot's live permission file, so every role now runs tests, scripts and prototypes through a wrapper the composer hands it, which sets a throwaway `HOME`, with gate commands already wrapped and `run_env` for tool caches; and the preamble forbids running anything that could write a protected path outside the repository.
  - S2: a plan's bulleted field lines lost every sub-ticket's dependencies, so the harness now reads `Depends on:` and `Parallel-safe:` lines that start with a list bullet and refuses a sub-ticket with no `Depends on:` line; and the planner prompt shows the three parsed lines at the start of a line and says `yes` means alongside every sibling.

  The seam that merges first writes the entry with its clause; the second adds its clause to the same entry and does not add a new number.
- E2. (S1) `README.md`, in "Roles, harness, workflows", in the **Roles.** paragraph after its first two sentences: add this sentence on one line, `Every role's input carries a wrapper that runs a command with a fresh temporary HOME, and the repo's check commands come already wrapped.`, followed by `It does not stop a write to an absolute path.`
- E3. (S1) `README.md`, "Adopting the factory in a repo", step 3: after the sentence that names `gate_commands` and `protected_paths`, add this sentence, with `run_env` in code format: "Set run_env for any tool whose cache lives under HOME, so it still finds that cache from inside the fresh temporary HOME." Keep everything from "so it still finds" to the end on one line. Bump the status-header date to the merge date.
- E4. `dev/build-harness.spec.md`: no change. I read the lines that describe what this change touches, and none is contradicted:
  - line 174 (`parallel_safe` comes from the planner's `Parallel-safe:` line);
  - line 204 (`run compose` opens the input with the role-context block, ahead of the declared sources; the new section is not a source);
  - lines 206 and 284 (`subticket add`).

**F. New tests**, in new files, driven through `bin/factory` on scratch stores:
- F1 (S1). `tests/factory/test_run_isolation.py`:
  - the `## Running code` section in triage, planner and implementer inputs;
  - wrapped gate commands;
  - `run_env` export order and quoting;
  - the `HOME` and bad-name refusals;
  - a probe run through the wrapper sees a fresh `HOME`.
- F2 (S2). `tests/factory/test_plan_fields.py`: `- ` and `* ` bullet field lines, with and without bold; a missing `Depends on:` line refused with the label named and no ticket written; `Depends on: none` still meaning no dependencies.

## Tests to change

none. Each existing test was checked against the change:
- Composed-input tests assert containment, the input's opening lines (`tests/factory/test_instance.py` line 271: context, then `## Output file`, which still comes second) or `input_sources`, which the new section does not join.
- The preamble test (`tests/factory/test_instance.py` lines 274-288) compares a run's system prompt with whatever `docs/prompts/00-preamble.md` holds, line by line around the filled lines, so the added lines are compared rather than rejected.
- `tests/factory/test_instance.py` line 303 requires `factory/prompts/preamble.md` to be byte-identical to `docs/prompts/00-preamble.md`, which part A keeps.
- Every plan in the suite gives each sub-ticket a `Depends on:` line: `test_subtickets.py`, `test_shepherd.py` (lines 295, 350, 408-409, 504), `test_parent_close_reuse.py` (lines 15-19), `test_build_startup.py` (which reuses `PLAN_LETTERS`), and the stub plans `accept-approve/planner-1.md` and `two-siblings/planner-1.md`.
- The template tests compare named keys only, so a new `run_env` key passes.
- No test reads the planner prompt's text.

=== specs/role-run-isolation/spec.md
## ADDED Requirements

### Requirement: Every role's input carries the throwaway-HOME wrapper
Every role input that `run compose` writes SHALL contain a `## Running code` section whose backticked wrapper runs a command with `HOME` set to a fresh temporary directory.

#### Scenario: A triage input's wrapper runs a command under a fresh HOME
Run every command in this file from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the four fixture scripts written by the block below, run once at column 0 as shown (every later scenario of this change reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0019-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T19=$(mktemp -d); export FACTORY_STATE=$T19/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T19/req.md && printf '## Problem\nx\n' > $T19/spec.md
bin/factory ticket new --file $T19/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T19/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0019-triage.sh <<'EOF'
# Sourced from the repo root: a scratch store with one triage run composed; IN is its input file.
# Set T19 before sourcing to reuse a directory (one holding an instance copy, for example).
T19=${T19:-$(mktemp -d)}; export FACTORY_STATE=$T19/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T19/req.md && bin/factory ticket new --file $T19/req.md >/dev/null
R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/')
bin/factory run compose $R >/dev/null; IN=$FACTORY_STATE/runs/$R/input.md
EOF
cat > ${TMPDIR:-/tmp}/t0019-impl.sh <<'EOF'
# Sourced after t0019-parent.sh: a scratch target repo, one sub-ticket, its implementer run composed; IN is its input file.
git init -q -b main $T19/t && git -C $T19/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T19/t FACTORY_INTEGRATION_BRANCH=main
printf 'T-0001.1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md >/dev/null
R=$(bin/factory run start --role implementer --ticket T-0001.1 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/')
bin/factory run compose $R >/dev/null; IN=$FACTORY_STATE/runs/$R/input.md
EOF
cat > ${TMPDIR:-/tmp}/t0019-probe.sh <<'EOF'
# Sourced after a script that set IN and T19: runs the wrapper from IN's "Running code" section
# around a probe that writes $HOME/t0019-probe and prints $HOME and $T0019_CACHE.
awk '/^## Running code$/{f=1;next} /^## /{f=0} f' $IN | grep -o '`[^`]*<command>[^`]*`' | head -1 | tr -d '`' > $T19/wrap
echo 'touch "$HOME/t0019-probe"; echo "$HOME|$T0019_CACHE"' > $T19/inner.sh
sed "s|<command>|sh $T19/inner.sh|" $T19/wrap > $T19/run.sh; O=$(sh $T19/run.sh); H=${O%%|*}
echo "fresh_home=$([ -n "$H" ] && [ "$H" != "$HOME" ] && [ -f "$H/t0019-probe" ] && echo yes || echo no) real_home_untouched=$([ -e "$HOME/t0019-probe" ] && echo no || echo yes) cache=${O#*|}"
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0019-triage.sh && . ${TMPDIR:-/tmp}/t0019-probe.sh)`
- THEN it prints exactly `fresh_home=yes real_home_untouched=yes cache=`

#### Scenario: Planner and implementer inputs carry the wrapper
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && R=$(bin/factory run start --role planner --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && bin/factory run compose $R >/dev/null && echo "planner $(grep -c '^## Running code$' $FACTORY_STATE/runs/$R/input.md)"); (. ${TMPDIR:-/tmp}/t0019-parent.sh && . ${TMPDIR:-/tmp}/t0019-impl.sh && echo "implementer $(grep -c '^## Running code$' $IN)")`
- THEN it prints `planner 1` then `implementer 1`

### Requirement: Gate commands reach a role already wrapped
The gate commands in a build role's input SHALL each be rendered inside the throwaway-HOME wrapper.

#### Scenario: The implementer's gate commands come wrapped
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && . ${TMPDIR:-/tmp}/t0019-impl.sh && grep -oF '(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)' $IN; grep -oF '(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)' $IN; echo end)`
- THEN it prints `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`, then `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`, then `end`

#### Scenario: This repo's gate suite passes under a throwaway HOME
This is the harness suite gate command in the wrapped form an implementer and verifier are handed after this change; it replaces a bare run of the suite.
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`
- THEN it exits 0 with no failures

### Requirement: An instance's run_env reaches the wrapped command, and cannot set HOME
The wrapper SHALL export each variable the instance lists in `run_env` after the throwaway `HOME`, and `run compose` MUST refuse, with exit 2 and no input written, a `run_env` that names `HOME`.

#### Scenario: Variables listed in run_env reach the command
- WHEN `(T19=$(mktemp -d); mkdir $T19/inst && cp .factory/instance.yaml .factory/context.md $T19/inst/ && printf "run_env: {T0019_CACHE: '/tmp/t0019 cache'}\n" >> $T19/inst/instance.yaml && export FACTORY_INSTANCE=$T19/inst && . ${TMPDIR:-/tmp}/t0019-triage.sh && . ${TMPDIR:-/tmp}/t0019-probe.sh)`
- THEN it prints exactly `fresh_home=yes real_home_untouched=yes cache=/tmp/t0019 cache`

#### Scenario: run_env cannot set HOME
- WHEN `(T19=$(mktemp -d); mkdir $T19/inst && cp .factory/instance.yaml .factory/context.md $T19/inst/ && printf 'run_env: {HOME: /tmp/t0019-home}\n' >> $T19/inst/instance.yaml && export FACTORY_INSTANCE=$T19/inst FACTORY_STATE=$T19/store && printf '# Fixture\n\nThe bot should do the thing.\n' > $T19/req.md && bin/factory ticket new --file $T19/req.md >/dev/null && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && bin/factory run compose $R >/dev/null; echo "exit=$? input=$([ -f $FACTORY_STATE/runs/$R/input.md ] && echo written || echo absent)")`
- THEN stderr contains `run_env` and `HOME`, and the last line is `exit=2 input=absent`

### Requirement: The preamble tells every role how to run code
The shared preamble SHALL tell every role to run tests, scripts and prototypes under a throwaway `HOME` through its input's wrapper, and never to run anything that could write a protected path outside the repository, identically in the design doc block, its prompt copy and the harness's preamble.

#### Scenario: The running-code rule is in every copy and in a run's system prompt
- WHEN `(. ${TMPDIR:-/tmp}/t0019-triage.sh && for f in docs/design.md docs/prompts/00-preamble.md factory/prompts/preamble.md $(dirname $IN)/system-prompt.txt; do echo "$(basename $f) $(grep -cxF 'RUNNING CODE' $f) $(grep -cxF -e '- Run every test, script or prototype with HOME set to a fresh' $f) $(grep -cxF -e '  run anything that could write a protected path outside the' $f)"; done)`
- THEN it prints `design.md 1 1 1`, `00-preamble.md 1 1 1`, `preamble.md 1 1 1` and `system-prompt.txt 1 1 1`

#### Scenario: The preamble block and its copies stay identical
- WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## Shared preamble \(every agent\)$/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/00-preamble.md && diff docs/prompts/00-preamble.md factory/prompts/preamble.md && echo SAME`
- THEN it prints `SAME`

=== specs/plan-parsing/spec.md
## ADDED Requirements

### Requirement: Bulleted field lines are read
A planner field line that starts with a `- ` or `* ` list bullet, with or without emphasis marks, SHALL be read as that field.

#### Scenario: Dash-bulleted field lines keep their dependencies
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\n- Depends on: none\n- Parallel-safe: no (alone)\n\n## ST-2 / Second\n- Depends on: ST-1\n- Parallel-safe: yes\n\n## ST-3 / Third\n- **Depends on:** ST-2\n- **Parallel-safe:** yes\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md | tail -1)`
- THEN the printed JSON's `subtickets` list is exactly `{"id": "T-0001.1", "label": "ST-1", "state": "ready-for-implementer", "depends_on": [], "parallel_safe": false}`, `{"id": "T-0001.2", "label": "ST-2", "state": "waiting-dependencies", "depends_on": ["T-0001.1"], "parallel_safe": true}`, `{"id": "T-0001.3", "label": "ST-3", "state": "waiting-dependencies", "depends_on": ["T-0001.2"], "parallel_safe": true}`

#### Scenario: Star-bulleted, bold, indented and plain field lines read as before
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\n* Depends on: none\n* Parallel-safe: yes\n\n## ST-2 / Second\n**Depends on:** ST-1\n**Parallel-safe:** yes\n\nT-0001-C / Third\n  Depends on: ST-2\n  Parallel-safe: no (same file)\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md | tail -1)`
- THEN the printed JSON's `subtickets` list is exactly `{"id": "T-0001.1", "label": "ST-1", "state": "ready-for-implementer", "depends_on": [], "parallel_safe": true}`, `{"id": "T-0001.2", "label": "ST-2", "state": "waiting-dependencies", "depends_on": ["T-0001.1"], "parallel_safe": true}`, `{"id": "T-0001.3", "label": "T-0001-C", "state": "waiting-dependencies", "depends_on": ["T-0001.2"], "parallel_safe": false}`

### Requirement: A sub-ticket with no Depends on line is refused by name
`subticket add` MUST refuse, with exit 2 and no ticket written, a plan in which any sub-ticket has no `Depends on:` line, and the refusal SHALL name that sub-ticket's label.

#### Scenario: A sub-ticket with no Depends on line is refused
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\nDepends on: none\nParallel-safe: yes\n\n## ST-2 / Second\nParallel-safe: yes\nScope: B\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md; echo "exit=$?"; ls $FACTORY_STATE/tickets)`
- THEN stderr contains `ST-2` and `Depends on:`, it prints `exit=2`, and the listing is `T-0001.yaml` alone

### Requirement: The planner prompt shows the lines the harness reads
The planner prompt's OUTPUT SHALL show the ID, `Depends on:` and `Parallel-safe:` lines each at the start of a line, SHALL say that a sub-ticket with no `Depends on:` line is refused, and SHALL say that `yes` means safe alongside every sibling, identically in the design doc block and its two copies.

#### Scenario: The planner prompt shows the parsed lines in every copy
- WHEN `for f in docs/design.md docs/prompts/04-planner.md factory/prompts/planner.md; do echo "$f $(grep -cxF 'ID / Title' $f) $(grep -cxF 'Depends on: none | IDs' $f) $(grep -cxF 'Parallel-safe: yes | no (reason)' $f) $(grep -cF 'A sub-ticket with no "Depends on:" line is refused.' $f) $(grep -cF 'Parallel-safe "yes" means safe alongside every sibling' $f)"; done`
- THEN it prints `docs/design.md 1 1 1 1 1`, `docs/prompts/04-planner.md 1 1 1 1 1` and `factory/prompts/planner.md 1 1 1 1 1`

#### Scenario: The planner block and its copies stay identical
- WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## 4\. Planner/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/04-planner.md && diff docs/prompts/04-planner.md factory/prompts/planner.md && echo SAME`
- THEN it prints `SAME`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the running-code wrapper and the plan rules
The changelog SHALL record this change as one next numbered entry with no gap, the README SHALL say every role's input carries the wrapper and how an instance sets `run_env`, and the design doc and the instance template SHALL name `run_env`.

#### Scenario: The changelog records the change in order
- WHEN `grep -cE '^[0-9]+\. After issue #36 \(2026-10-04\)' docs/changelog.md; awk '/^[0-9]+\. /{n++; if ($1+0 != n) bad=1} END{print (bad?"GAP":"CONTIGUOUS")}' docs/changelog.md`
- THEN it prints `1` then `CONTIGUOUS`

#### Scenario: The README describes the wrapper and run_env
- WHEN `grep -cF "Every role's input carries a wrapper that runs a command with a fresh temporary HOME, and the repo's check commands come already wrapped." README.md; grep -cF 'so it still finds that cache from inside the fresh temporary HOME.' README.md; grep -c 'run_env' README.md`
- THEN it prints `1`, then `1`, then a number of 1 or more

#### Scenario: The design doc and the instance template name run_env
- WHEN `grep -c 'run_env' docs/design.md factory/instance.template.yaml`
- THEN both counts are 1 or more

#### Scenario: The change adds no whitespace errors
- WHEN `git diff --check main...HEAD; echo "exit=$?"`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Every scenario after the first needs the first scenario's GIVEN block run once. It writes `${TMPDIR:-/tmp}/t0019-parent.sh`, `t0019-triage.sh`, `t0019-impl.sh` and `t0019-probe.sh`. Every command runs from the repository root of the checkout under test, after `uv sync --frozen`. Each "today" result below was produced by running the GIVEN block and then the WHEN verbatim on `main` at `17efb50` (v1; `main` has not moved since, and this round re-ran the two marked "re-run" and the gate suite).

- A triage input's wrapper runs a command under a fresh HOME → NEW. Today it prints `fresh_home=no real_home_untouched=yes cache=`. The input has no `## Running code` section, so there is no wrapper to run.
- Planner and implementer inputs carry the wrapper → NEW. Today it prints `planner 0` then `implementer 0`.
- The implementer's gate commands come wrapped → NEW. Today it prints only `end`: the input lists the bare `git diff --check main...HEAD` and `uv run --frozen pytest …` commands (re-run: the input's gate line still reads ``exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` ``).
- This repo's gate suite passes under a throwaway HOME → REGRESSION. Today: `157 passed in 120.88s` (v1); this round's re-run result is in the note below the list.
- Variables listed in run_env reach the command → NEW. Today it prints `fresh_home=no real_home_untouched=yes cache=`: no wrapper, and `run_env` is ignored.
- run_env cannot set HOME → NEW. Today it prints `exit=0 input=written`: compose ignores `run_env` and writes the input.
- The running-code rule is in every copy and in a run's system prompt → NEW. Today all four lines end `0 0 0`.
- The preamble block and its copies stay identical → REGRESSION. Today it prints `SAME`.
- Dash-bulleted field lines keep their dependencies → NEW. Today all three sub-tickets print `"state": "ready-for-implementer", "depends_on": [], "parallel_safe": false` (re-run: same).
- Star-bulleted, bold, indented and plain field lines read as before → REGRESSION. Today it prints exactly the expected list.
- A sub-ticket with no Depends on line is refused → NEW. Today it prints the success JSON with `T-0001.2` at `"depends_on": []`, then `exit=0`, then `T-0001.1.yaml`, `T-0001.2.yaml`, `T-0001.yaml`.
- The planner prompt shows the parsed lines in every copy → NEW. Today each file prints `0 0 0 0 0`: the three lines are indented, and neither sentence exists.
- The planner block and its copies stay identical → REGRESSION. Today it prints `SAME`.
- The changelog records the change in order → NEW. Today it prints `0` then `CONTIGUOUS`.
- The README describes the wrapper and run_env → NEW. Today it prints `0`, `0`, `0`.
- The design doc and the instance template name run_env → NEW. Today it prints `docs/design.md:0` and `factory/instance.template.yaml:0`.
- The change adds no whitespace errors → REGRESSION.

This round's re-run of "This repo's gate suite passes under a throwaway HOME", WHEN verbatim on `17efb50` in the dev checkout: `171 passed in 100.14s (0:01:40)`, exit 0. v1 reported 157 for what it recorded as the same commit; I did not find out why the counts differ, and both runs passed with no failures.

## Responses

- [BLOCKING] Operator steps gloss of "runtime": FIXED. Operator steps now open "once the runtime (the pinned checkout of the harness that runs tickets) has moved to a revision with this change", and `--accept-harness` is explained in the same paragraph.
- [SHOULD-FIX] No `run_env` for this repo: FIXED, with a stronger reason than re-downloads. Under a throwaway `HOME` in a fresh copy of `17efb50`, uv could not see its managed Pythons and built the `.venv` on Homebrew's CPython 3.14.5 instead of the managed 3.12 the operator's `.venv` uses (Evidence, paragraph 6). Added Operator step 3, which sets `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` here from what `uv cache dir` and `uv python dir` print, and a Decision saying both instances get `run_env` from the operator, not from this change.
- [SHOULD-FIX] Two faults in one PR: FIXED. The spec is marked NEEDS-SPLIT, with two seams under "Size and seams": S1 (A, B, E2, E3, F1) and S2 (C, D, F2), and each lettered part names its seam. The whole is about 300 lines and would fit one PR, so the split is for independent review and rollback, not size. `NEEDS-SPLIT` reaches the critic exactly as `READY-FOR-CRITIC` does (`factory/workflows/intake.js` line 150). Both seams edit `docs/design.md` and `docs/changelog.md`, so they are not parallel-safe. They share one changelog entry: the first to merge writes it with its clause, and the second adds its clause (E1).
- [NIT] "parked" unglossed: FIXED. Problem now says "Every one of them ended `parked`, the state for a ticket the build has stopped on."
- [NIT] Suite run twice: FIXED. Dropped the bare "The harness suite passes" scenario. The wrapped one stays, with a line saying it is the gate command as handed after this change.
- [NIT] "every command" in the rule: FIXED. Part A and B3 now say "every test or check command". The lines the preamble scenario greps for are unchanged. Checked: under a throwaway `HOME`, `git var GIT_COMMITTER_IDENT` in this repo still printed an auto-detected identity, so I did not show that a wrapped `git commit` fails. The narrower wording stands either way.
- Critic's out-of-scope observation on leftover temporary directories: the design doc text in B6 and Risk now say each run leaves its temporary directory behind. Removing them stays out of scope.

Out-of-scope observations:
- `agents/factory-planner.md` holds an older copy of the planner role text, whose OUTPUT block already differs from the design doc's (its Acceptance line is the earlier wording). A planner agent reads that copy and then `system-prompt.txt`, so after this change it holds two different OUTPUT blocks. `agents/**` is a protected path, and the request does not cover it. Neither target runs these definitions today (the critic notes `inlineRoles: true` on both).
- `build.js` line 200 parks a refused `subticket add` as `harness-bug: subticket add: …`, though after this change a refusal usually means a malformed plan, not a harness bug.
- Under a throwaway `HOME`, uv also ignores the operator's uv config under `~/.config/uv`, if any. I did not check whether one exists, and `run_env` can carry `UV_CONFIG_FILE` if it does.

## PR description (the implementer's output)

Sub-ticket: T-0019.1 (T-0019-S1, "Role runs under a throwaway HOME"), parent T-0019 approved spec v2 (issue #36)
Branch: `factory/T-0019.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0019.1`, base `1c5f6a7`, head `5f43cba` (one commit; 8 files, 252 insertions, 5 deletions).

## What changed

Before this change, roles ran tests with the operator's real home directory as `HOME`. On the Nanobot instance, that let a test overwrite the live bot's permission file. Now every role input the harness composes carries a ready-made wrapper. The wrapper runs a command with `HOME` set to a fresh temporary directory, and the gate commands come already wrapped. (Gate commands are the instance's check commands that the implementer and verifier must run.) The wrapper is guidance a role follows. It does not stop the operating system from writing anywhere.

- **A, the preamble rule.** The shared preamble is the rules text at the top of every role's prompt. In `docs/design.md` it gains a `RUNNING CODE` section, placed after the protected-paths placeholder line and before `GUARDRAIL PATHS`, with the parent's wording. `docs/prompts/00-preamble.md` is re-copied from that block, and `factory/prompts/preamble.md` is byte-identical to the copy.
- **B1, the run_env reader.** `factory/compose.py` gains `run_env(cfg)` (line 57). It reads the new instance key `run_env`, and an absent or null key counts as empty. It raises `store.Refused` (exit 2) if the value is not a mapping, if a name does not match `[A-Za-z_][A-Za-z0-9_]*`, or if a name is `HOME`. Each message names `run_env` and the offending name. The reader takes the `cfg` that `compose` already receives, so `factory/instance.py` is not edited.
- **B2, the wrapper.** `wrap(command, env)` (line 74) returns `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"<vars>; <command>)`. For each `run_env` entry, in file order, `<vars>` adds a space, `NAME=` and `shlex.quote(str(value))`.
- **B3, the section in every input.** `compose` adds a `## Running code` section, with the parent's text, directly after `## Output file`. Every role gets it. The section is not a store source, so `input_sources` is unchanged. `run_env` is read before anything is built, so a refused value means `cli.run_compose` never writes `input.md`.
- **B4, wrapped gate commands.** In "Where you work", each gate command goes through `wrap` after `{integration}` is replaced. The text now reads "exactly as written; each is already wrapped". Callers, found by grep: `compose.compose` is called only from `factory/cli.py:274` (`run_compose`). `gate_commands` is called only from `compose.py`, and I left it unchanged, so its output is still the bare commands.
- **B5.** `factory/instance.template.yaml` adds `run_env: {}` after `environment_files`, with the comment the parent asks for.
- **B6.** In the **Role-context block** paragraph of `docs/design.md` (line 54), the `instance.yaml` list now names "the variables kept for code runs (`run_env`)". The paragraph also ends with the parent's three sentences on the "Running code" section.
- **E1 (S1 clause only).** `docs/changelog.md` adds entry 48, "After issue #36 (2026-10-04): …", with the S1 clause. It sits after entry 47 and before `Declined:`. `main` had no `After issue #36` entry, so this sub-ticket adds the entry. When S2 merges, it adds its clause to entry 48.
- **E2, E3.** `README.md`: the **Roles.** paragraph gains the two sentences, the first on one line. In "Adopting the factory in a repo", step 3 gains "Set `run_env` for any tool whose cache lives under HOME, so it still finds that cache from inside the fresh temporary HOME.", with everything from "so it still finds" on one line. The status header already reads 2026-10-04, today's date, so it is unchanged.
- **E4.** `dev/build-harness.spec.md` is untouched, as the parent says.
- **F1.** New file `tests/factory/test_run_isolation.py`, described under "Tests added/changed".

## Acceptance results

All commands ran from the worktree root after `uv sync --frozen`, with the parent's fixture GIVEN block run verbatim first. I ran each block inside an outer `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`, so no probe ran with my real `HOME`.

| Scenario | Kind | Before (base `1c5f6a7`) | After (head `5f43cba`) |
|---|---|---|---|
| A triage input's wrapper runs a command under a fresh HOME | NEW | `fresh_home=no real_home_untouched=yes cache=` | `fresh_home=yes real_home_untouched=yes cache=` |
| Planner and implementer inputs carry the wrapper | NEW | `planner 0` / `implementer 0` | `planner 1` / `implementer 1` |
| The implementer's gate commands come wrapped | NEW | `end` only | `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`, `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`, `end` |
| This repo's gate suite passes under a throwaway HOME | REGRESSION | not run (runs once, after) | `182 passed in 100.01s (0:01:40)`, exit 0. The 11 new tests are included: 171 existing + 11 = 182. |
| Variables listed in run_env reach the command | NEW | `fresh_home=no real_home_untouched=yes cache=` | `fresh_home=yes real_home_untouched=yes cache=/tmp/t0019 cache` |
| run_env cannot set HOME | NEW | `exit=0 input=written` | stderr `run_env may not set HOME: the running-code wrapper sets it to a fresh temporary directory`, then `exit=2 input=absent` |
| The running-code rule is in every copy and in a run's system prompt | NEW | all four `0 0 0` | `design.md 1 1 1`, `00-preamble.md 1 1 1`, `preamble.md 1 1 1`, `system-prompt.txt 1 1 1` |
| The preamble block and its copies stay identical | REGRESSION | `SAME` | `SAME` |
| The README describes the wrapper and run_env | NEW | `0`, `0`, `0` | `1`, `1`, `1` |
| The design doc and the instance template name run_env | NEW | `docs/design.md:0`, `factory/instance.template.yaml:0` | `docs/design.md:1`, `factory/instance.template.yaml:1` |
| The changelog records the change in order | NEW | `0`, `CONTIGUOUS` | `1`, `CONTIGUOUS`; entry 48 carries the S1 clause |
| The change adds no whitespace errors | REGRESSION | `exit=0` (empty diff) | `exit=0` |
| Only declared files change, no existing test changes | NEW | (empty) | exactly the 8 declared files: `README.md`, `docs/changelog.md`, `docs/design.md`, `docs/prompts/00-preamble.md`, `factory/compose.py`, `factory/instance.template.yaml`, `factory/prompts/preamble.md`, `tests/factory/test_run_isolation.py` |

What the "after" results show:
- `fresh_home=yes` means the probe ran under a `HOME` other than the caller's, and wrote its file there.
- `real_home_untouched=yes` means nothing was written to the caller's `HOME`.
- `cache=/tmp/t0019 cache` means a `run_env` value containing a space reached the command intact.

Gate commands, each run once on head `5f43cba`, in the wrapped form the parent requires:
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)` exited 0.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `182 passed`, exit 0. This is the same run as the REGRESSION row above.

Also: `ruff check factory/compose.py tests/factory/test_run_isolation.py` printed `All checks passed!`. Ruff is not a gate here.

## Tests added/changed

Added `tests/factory/test_run_isolation.py`, with 11 cases. Each drives `bin/factory` on a throwaway store. The cases that change `instance.yaml` use a copy of the suite's fixture instance.
- The triage input has exactly one `## Running code` section, right after `## Output file`, with the exact B3 text. `sources` is still only `requests/T-0001.md`.
- The planner and implementer inputs each carry the section once, with the bare wrapper.
- The implementer's gate command is rendered wrapped, after "exactly as written; each is already wrapped", and never bare.
- `run_env: {ZED: '/tmp/a b', ALPHA: "it's", N_1: 3}` produces ` ZED='/tmp/a b' ALPHA='it'"'"'s' N_1=3`, in file order and shell-quoted. The same string appears in the wrapper and in the wrapped gate command.
- A null `run_env` and `run_env: {}` both export nothing.
- Four refusals: `HOME`, `1BAD`, `A-B` and a list value. Each exits 2, its stderr names `run_env` and the offending name or type, and no `input.md` is written.
- A compound command `touch "$HOME/probe" && echo …`, run twice through the wrapper with a fake real `HOME`:
  - both halves see the same fresh, symlink-resolved `HOME` and the `run_env` variable;
  - the two runs get different homes;
  - the fake real `HOME` stays empty.

I watched them fail before the change: 11 failed on base. I changed no existing test.

## Known gaps and uncertainties

- **This repo has no `run_env` until the operator sets it.** Until Operator step 3 adds `run_env` for uv here, a wrapped test run in a fresh worktree that has no `.venv` resolves Python from an empty temporary home. It then builds `.venv` on the first system Python on `PATH`, and downloads every package again. I created this worktree's `.venv` with `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` exported to the real uv paths, which is what step 3 would set. So the 182-test run used uv's managed CPython 3.12.13, not Homebrew's 3.14. Neither instance's `.factory/instance.yaml` was changed; that is out of scope.
- **Odd value types.** `run_env` values go through `str()`, as B2 specifies. A null value (`X: ~`) is therefore exported as the string `None`, and a YAML boolean as `True` or `False`. The parent does not ask for either case to be refused, so I did not refuse them.
- **The README runs ahead of its own rule.** "Maintaining this page" says a thing appears above "Where this can go" only after it has run on a real ticket. Parts E2 and E3 ask for present-tense README text now, before the runtime has moved to this revision. I followed the spec.
- **The wrapper is not a sandbox.** A command can still write an absolute path, and each run leaves its temporary directory behind. Both are stated in the parent and the design doc, and both are out of scope.
- **Gate commands that would break the wrapper.** A gate command with a shell comment (`#`) or a backtick would break the wrapped form or its rendering. The parent checked both instances' gate commands, and none has either character. Nothing here validates them.
- `factory:` markers added: none.

## Out-of-scope observations

- My shell had inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test`. uv warned that it does not match the project's `.venv` and ignored it, so the suite ran on the worktree's own `.venv`.
- `.factory/context.md`, this repo's briefing, still gives the bare test command. The new `## Running code` section and the preamble rule tell a role to wrap it. Changing the briefing is an instance-file change, out of scope here.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command ran before the change and after it, with the results above. The full suite passed under a throwaway HOME: 182 tests, 0 failures.
ESCALATIONS: none

## Diff `1c5f6a7aa096c39b9a9f355b2dee286ccd3b4a84...5f43cba12a208e095e48872471e4f6f2f9dc47f5`

diff --git a/README.md b/README.md
index d471629..e9cb379 100644
--- a/README.md
+++ b/README.md
@@ -27,6 +27,8 @@ built, who checked it against what, and why it was allowed through.
 **Roles.** Eight jobs, each a prompt. A role runs as a fresh agent every time and sees only its
 declared inputs: the critic never sees the writer's reasoning, the reviewer never sees the
 implementer's.
+Every role's input carries a wrapper that runs a command with a fresh temporary HOME, and the repo's check commands come already wrapped.
+It does not stop a write to an absolute path.
 
 | Role | Does | Model |
 |---|---|---|
@@ -254,7 +256,8 @@ From inside the target repo, with `R` the runtime (`~/dev/spec-factory-harness`)
 2. Restart the Claude Code session so the agents register.
 3. Fill in `.factory/context.md`, the briefing every role reads first: which repo this is, how to
    run its tests, what kind of request to expect. Set `gate_commands` and `protected_paths` in
-   `.factory/instance.yaml`.
+   `.factory/instance.yaml`. Set `run_env` for any tool whose cache lives under HOME,
+   so it still finds that cache from inside the fresh temporary HOME.
 
 The repo is now a target. "Starting a run" is the rest.
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 5cb18bd..efc3221 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -49,5 +49,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 45. After issue #31 (2026-10-03), from the T-0013 to T-0015 build timings, where a parent-close run took 13 to 23% of each build and only two of about six test-suite runs per build could change a verdict: a REGRESSION acceptance check runs once, after the change. The implementer runs only the NEW checks before editing, and runs a REGRESSION check on its base only when it fails after the change; the verifier runs a REGRESSION check on base only when it fails on the PR. One gate run per commit: an acceptance check that already ran a gate command exactly as written on the same commit is that gate's run, for the implementer and the verifier. A parent with one sub-ticket closes on that sub-ticket's VERIFIED run when `main` has not moved since it merged, the run checked the merged head against the parent's recorded base, and the sub-ticket's text names every scenario of the parent's pinned spec; the run stands for the parent-close run, `ticket parent-check` reports it as `reuse`, and the close records it as `verified_by`. Every other parent still gets its own parent-close run, and every refusal is kept: a NEW check that does not fail first is a SPEC-DEFECT, a failing REGRESSION check fails the branch, and a gate failure is FAILED. The requested path-scoped gate skip was cut: a correct path list for this repository covers `docs/**`, which would have skipped no suite run in those builds.
 46. After the Nanobot target's T-0003 (2026-10-04), a ticket that existed only to get a decision: the human answered its question about where the port's code lives and closed it, archive never ran, and the decision stayed in that ticket's request, so the operator copied it by hand into the two later requests that depend on it. `decisions.md` gains writers besides archive: `factory decision add <ticket id> "<line>"`, at any ticket state, closed included, and `--decision "<line>"` on `resolve --answer` or `resolve --close`, refused with any other `resolve` mode. Each appends the line in archive's format, `<YYYY-MM-DD> <ticket id> <line>`, creates the file when absent, and logs `decision.recorded`. The spec writer and the critic receive a non-empty `decisions.md` after current truth, and the planner after the approved spec; triage and the build roles do not. Triage's NEEDS-HUMAN question and the spec writer's open questions now ask whether the answer is a standing decision that later tickets must follow. Archive's own output is unchanged.
 47. After issue #33 (2026-10-04), where six approved tickets on the Nanobot target stalled with no record of why: intake ends at the spec gate, and the build owns planning. A build that finds a planned parent with no sub-tickets creates them from the planner run named by the parent's latest `plan.added` event (`subticket add PARENT` with no `--run`), or parks the parent with a reason containing `no sub-tickets`. No stop is silent any more: an `agent()` call that throws finishes its run KILLED and parks the ticket with `agent call failed: <role>: <error>`, and a refused `parent-check` parks the parent with its refusal. The verifier writes `Gate suite:` as a plain line, never a heading or bold, and the harness also reads that line in heading or bold form, so a verifier's PASS written as `## Gate suite: PASS` is no longer recorded as a missing gate line.
+48. After issue #36 (2026-10-04): a role's test run overwrote the Nanobot bot's live permission file, so every role now runs tests, scripts and prototypes through a wrapper the composer hands it, which sets a throwaway `HOME`, with gate commands already wrapped and `run_env` for tool caches; and the preamble forbids running anything that could write a protected path outside the repository.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 5b22403..57c4c39 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -51,7 +51,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **What the harness itself owns** (no platform provides these): the routing table, the round counter and the max-round cutoff, composing each role's input from *only* its declared sources, choosing the model per role, and the escalation queue view for the daily human pass.
 
-**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout.
+**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell with `HOME` set to a fresh temporary directory, exporting any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
 
 **Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception.
 
@@ -203,6 +203,16 @@ SCOPE AND ESCALATION
 - Protected paths for this repo:
   {auth, payments, migrations, infra, public API, dependencies}
 
+RUNNING CODE
+- Run every test, script or prototype with HOME set to a fresh
+  temporary directory, never the real one: use the wrapper in the
+  "Running code" section of your input. That includes every test or
+  check command your briefing, ticket or spec gives you.
+- A throwaway HOME does not stop a write to an absolute path. Never
+  run anything that could write a protected path outside the
+  repository, such as live credentials or production state.
+- If something you must run cannot work this way, stop and escalate.
+
 GUARDRAIL PATHS
 Never modify or delete existing tests, CI config, AGENTS.md, skills, or
 agent prompts unless your ticket explicitly says to (for existing tests:
diff --git a/docs/prompts/00-preamble.md b/docs/prompts/00-preamble.md
index 65073b5..eea6488 100644
--- a/docs/prompts/00-preamble.md
+++ b/docs/prompts/00-preamble.md
@@ -37,6 +37,16 @@ SCOPE AND ESCALATION
 - Protected paths for this repo:
   {auth, payments, migrations, infra, public API, dependencies}
 
+RUNNING CODE
+- Run every test, script or prototype with HOME set to a fresh
+  temporary directory, never the real one: use the wrapper in the
+  "Running code" section of your input. That includes every test or
+  check command your briefing, ticket or spec gives you.
+- A throwaway HOME does not stop a write to an absolute path. Never
+  run anything that could write a protected path outside the
+  repository, such as live credentials or production state.
+- If something you must run cannot work this way, stop and escalate.
+
 GUARDRAIL PATHS
 Never modify or delete existing tests, CI config, AGENTS.md, skills, or
 agent prompts unless your ticket explicitly says to (for existing tests:
diff --git a/factory/compose.py b/factory/compose.py
index f85c0da..02fc05d 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -4,6 +4,8 @@ Per (role, round, resolution). No other code path assembles role input.
 """
 from __future__ import annotations
 
+import re
+import shlex
 from pathlib import Path
 
 from factory import instance, store
@@ -49,11 +51,44 @@ def gate_commands(cfg: dict) -> list[str]:
     return [g.replace("{integration}", str(co)) for g in cfg.get("gate_commands", [])]
 
 
+_ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
+
+
+def run_env(cfg: dict) -> dict:
+    """The instance's `run_env`: variables the running-code wrapper exports after the throwaway HOME,
+    for tools that keep a cache under HOME. Absent or null is empty. Refused when it is not a mapping,
+    when a name is not a shell variable name, or when it names HOME, which the wrapper owns."""
+    env = cfg.get("run_env")
+    if env is None:
+        return {}
+    if not isinstance(env, dict):
+        raise store.Refused(f"run_env must be a mapping of variable name to value, not a {type(env).__name__}")
+    for name in env:
+        if not isinstance(name, str) or not _ENV_NAME.fullmatch(name):
+            raise store.Refused(f"run_env: {name!r} is not a variable name ([A-Za-z_][A-Za-z0-9_]*)")
+        if name == "HOME":
+            raise store.Refused("run_env may not set HOME: the running-code wrapper sets it to a fresh temporary directory")
+    return env
+
+
+def wrap(command: str, env: dict) -> str:
+    """`command` in a subshell with HOME set to a fresh temporary directory, then each `run_env`
+    variable exported in file order. A subshell, so the export covers every part of `a && b`."""
+    exports = "".join(f" {k}={shlex.quote(str(v))}" for k, v in env.items())
+    return f'(export HOME="$(cd "$(mktemp -d)" && pwd -P)"{exports}; {command})'
+
+
 def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]:
     role, run_id, tid = meta["role"], meta["run_id"], t["id"]
     out_path = root / "runs" / run_id / "output.md"
+    env = run_env(cfg)
     parts = [(instance.require() / "context.md").read_text(encoding="utf-8").rstrip(),
-             f"\n## Output file\n`{out_path}`\n"]
+             f"\n## Output file\n`{out_path}`\n",
+             "\n## Running code\nRun every test, script or prototype through this wrapper, which gives it a fresh "
+             "temporary HOME so it cannot write the operator's real home directory: "
+             f"`{wrap('<command>', env)}`. Put your command in place of <command>. This includes every test or "
+             "check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: "
+             "never run anything that could write a protected path outside the repository.\n"]
     sources: list[str] = []
 
     def add(rel: str, heading: str) -> None:
@@ -128,8 +163,8 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         where = (f"\n## Where you work\nWorktree: `{meta.get('worktree')}` (branch `{meta.get('branch')}`, "
                  f"base `{meta.get('base')}`, head `{meta.get('head')}`). There is no remote: commit on the "
                  f"branch; the PR is the branch plus the description you return. Gate commands (run each from "
-                 f"your worktree, exactly as written): "
-                 + "; ".join(f"`{g}`" for g in gate_commands(cfg)) + "\n")
+                 f"your worktree, exactly as written; each is already wrapped): "
+                 + "; ".join(f"`{wrap(g, env)}`" for g in gate_commands(cfg)) + "\n")
         parts.append(where)
         if role == "implementer":
             if t.get("merge_refused"):
diff --git a/factory/instance.template.yaml b/factory/instance.template.yaml
index 4452806..8674d5d 100644
--- a/factory/instance.template.yaml
+++ b/factory/instance.template.yaml
@@ -25,6 +25,9 @@ integration_branch: null
 # example a lockfile the target repo git-ignores). A tracked file does not belong here: copying it in
 # would mask the branch's own version.
 environment_files: []
+# Variables the running-code wrapper exports after the throwaway HOME, for tools that keep a cache
+# under HOME (for example UV_CACHE_DIR: /Users/me/.cache/uv). HOME itself is refused.
+run_env: {}
 force_push_allowed: false
 models:
   triage: opus
diff --git a/factory/prompts/preamble.md b/factory/prompts/preamble.md
index 65073b5..eea6488 100644
--- a/factory/prompts/preamble.md
+++ b/factory/prompts/preamble.md
@@ -37,6 +37,16 @@ SCOPE AND ESCALATION
 - Protected paths for this repo:
   {auth, payments, migrations, infra, public API, dependencies}
 
+RUNNING CODE
+- Run every test, script or prototype with HOME set to a fresh
+  temporary directory, never the real one: use the wrapper in the
+  "Running code" section of your input. That includes every test or
+  check command your briefing, ticket or spec gives you.
+- A throwaway HOME does not stop a write to an absolute path. Never
+  run anything that could write a protected path outside the
+  repository, such as live credentials or production state.
+- If something you must run cannot work this way, stop and escalate.
+
 GUARDRAIL PATHS
 Never modify or delete existing tests, CI config, AGENTS.md, skills, or
 agent prompts unless your ticket explicitly says to (for existing tests:
diff --git a/tests/factory/test_run_isolation.py b/tests/factory/test_run_isolation.py
new file mode 100644
index 0000000..164a927
--- /dev/null
+++ b/tests/factory/test_run_isolation.py
@@ -0,0 +1,175 @@
+"""Role runs under a throwaway HOME (issue #36, part B): every composed input carries a
+"Running code" section whose wrapper runs a command with HOME set to a fresh temporary directory,
+gate commands reach build roles already wrapped, and the instance's `run_env` is exported after
+HOME and may not set HOME itself.
+
+Black-box through `bin/factory`, each case on a throwaway store (FACTORY_STATE) and, where it
+changes `instance.yaml`, on a copy of the suite's fixture instance (FACTORY_INSTANCE).
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+from pathlib import Path
+
+import pytest
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
+WRAP = '(export HOME="$(cd "$(mktemp -d)" && pwd -P)"{vars}; {cmd})'
+SECTION = ("\n## Running code\nRun every test, script or prototype through this wrapper, which gives it a "
+           "fresh temporary HOME so it cannot write the operator's real home directory: `{wrapper}`. Put your "
+           "command in place of <command>. This includes every test or check command the briefing above gives. "
+           "A throwaway HOME does not stop a write to an absolute path: never run anything that could write a "
+           "protected path outside the repository.\n")
+
+
+class Store:
+    def __init__(self, tmp_path: Path, run_env: str | None = None):
+        self.tmp = tmp_path
+        self.root = tmp_path / "state"
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"}
+        if run_env is not None:
+            inst = tmp_path / "inst"
+            shutil.copytree(FIXTURE_INSTANCE, inst)
+            with (inst / "instance.yaml").open("a", encoding="utf-8") as f:
+                f.write(run_env)
+            self.env["FACTORY_INSTANCE"] = str(inst)
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def request(self) -> None:
+        p = self.tmp / "req.md"
+        p.write_text("# Fixture\n\nThe bot should do the thing.\n")
+        self.ok("ticket", "new", "--file", str(p))
+
+    def approved(self) -> None:
+        """T-0001 past the spec gate, as the spec's t0019-parent.sh fixture leaves it."""
+        self.request()
+        spec = self.tmp / "spec.md"
+        spec.write_text("## Problem\nx\n")
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+        self.ok("spec", "add", "T-0001", "--file", str(spec))
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
+        self.ok("approve-spec", "T-0001")
+
+    def implementer_ready(self) -> None:
+        """One sub-ticket of an approved T-0001, in a scratch target repo with a `main` branch."""
+        self.approved()
+        target = self.tmp / "target"
+        target.mkdir()
+        for argv in (["init", "-q", "-b", "main"],
+                     ["-c", "user.email=f@x", "-c", "user.name=f", "commit", "-q", "--allow-empty", "-m", "init"]):
+            subprocess.run(["git", "-C", str(target), *argv], check=True, capture_output=True)
+        self.env.update({"FACTORY_REPO": str(target), "FACTORY_INTEGRATION_BRANCH": "main"})
+        plan = self.tmp / "plan.md"
+        plan.write_text("T-0001.1 / Do it\nDepends on: none\nParallel-safe: yes\n")
+        self.ok("subticket", "add", "T-0001", "--file", str(plan))
+
+    def start(self, role: str, tid: str) -> str:
+        return self.ok("run", "start", "--role", role, "--ticket", tid)["run_id"]
+
+    def compose(self, role: str, tid: str) -> tuple[str, dict]:
+        run_id = self.start(role, tid)
+        out = self.ok("run", "compose", run_id)
+        return (self.root / "runs" / run_id / "input.md").read_text(encoding="utf-8"), out
+
+
+def wrapper_in(text: str) -> str:
+    """The backticked text holding `<command>` in the input's Running code section."""
+    section = text.split("\n## Running code\n", 1)[1].split("\n## ", 1)[0]
+    found = [s for s in section.split("`")[1::2] if "<command>" in s]
+    assert len(found) == 1, section
+    return found[0]
+
+
+def test_triage_input_carries_the_section_right_after_the_output_file(tmp_path):
+    s = Store(tmp_path)
+    s.request()
+    text, out = s.compose("triage", "T-0001")
+    _, rest = text.split("\n## Output file\n", 1)
+    assert rest.split("\n", 1)[1].startswith(SECTION.format(wrapper=WRAP.format(vars="", cmd="<command>")))
+    assert text.count("\n## Running code\n") == 1
+    assert out["sources"] == ["requests/T-0001.md"], "the section is not a store source"
+
+
+def test_planner_and_implementer_inputs_carry_the_section_once(tmp_path):
+    s = Store(tmp_path)
+    s.implementer_ready()
+    for role, tid in (("planner", "T-0001"), ("implementer", "T-0001.1")):
+        text, _ = s.compose(role, tid)
+        assert text.count("\n## Running code\n") == 1, role
+        assert wrapper_in(text) == WRAP.format(vars="", cmd="<command>"), role
+
+
+def test_implementer_gate_commands_come_wrapped(tmp_path):
+    s = Store(tmp_path)
+    s.implementer_ready()
+    text, _ = s.compose("implementer", "T-0001.1")
+    where = text.split("\n## Where you work\n", 1)[1].split("\n## ", 1)[0]
+    # the suite's fixture instance has one gate command
+    assert ("Gate commands (run each from your worktree, exactly as written; each is already wrapped): `"
+            + WRAP.format(vars="", cmd="git diff --check main...HEAD") + "`\n") in where + "\n"
+    assert "`git diff --check main...HEAD`" not in where
+
+
+def test_run_env_is_exported_after_home_in_file_order_and_quoted(tmp_path):
+    s = Store(tmp_path, run_env="run_env: {ZED: '/tmp/a b', ALPHA: \"it's\", N_1: 3}\n")
+    s.implementer_ready()
+    vars_ = " ZED='/tmp/a b' ALPHA='it'\"'\"'s' N_1=3"
+    text, _ = s.compose("implementer", "T-0001.1")
+    assert wrapper_in(text) == WRAP.format(vars=vars_, cmd="<command>")
+    assert "`" + WRAP.format(vars=vars_, cmd="git diff --check main...HEAD") + "`" in text
+
+
+@pytest.mark.parametrize("value", ["run_env:\n", "run_env: {}\n"])
+def test_empty_or_null_run_env_exports_nothing(tmp_path, value):
+    s = Store(tmp_path, run_env=value)
+    s.request()
+    text, _ = s.compose("triage", "T-0001")
+    assert wrapper_in(text) == WRAP.format(vars="", cmd="<command>")
+
+
+@pytest.mark.parametrize(("value", "named"), [
+    ("run_env: {HOME: /tmp/t0019-home}\n", "HOME"),
+    ("run_env: {OK: x, 1BAD: y}\n", "1BAD"),
+    ("run_env: {'A-B': y}\n", "A-B"),
+    ("run_env: [UV_CACHE_DIR]\n", "list"),
+])
+def test_bad_run_env_is_refused_and_no_input_is_written(tmp_path, value, named):
+    s = Store(tmp_path, run_env=value)
+    s.request()
+    run_id = s.start("triage", "T-0001")
+    cp = s.cli("run", "compose", run_id)
+    assert cp.returncode == 2
+    assert "run_env" in cp.stderr and named in cp.stderr, cp.stderr
+    assert not (s.root / "runs" / run_id / "input.md").exists()
+
+
+def test_a_command_run_through_the_wrapper_gets_a_fresh_home_and_run_env(tmp_path):
+    s = Store(tmp_path, run_env="run_env: {T0019_CACHE: '/tmp/t0019 cache'}\n")
+    s.request()
+    text, _ = s.compose("triage", "T-0001")
+    # A compound command: the export reaches both halves, and each run gets its own HOME.
+    probe = 'touch "$HOME/probe" && echo "$HOME|$T0019_CACHE|$(ls "$HOME")"'
+    script = wrapper_in(text).replace("<command>", probe)
+    fake_home = tmp_path / "real-home"
+    fake_home.mkdir()
+    env = {**os.environ, "HOME": str(fake_home)}
+    env.pop("T0019_CACHE", None)
+    first, second = (subprocess.run(["sh", "-c", script], capture_output=True, text=True, env=env, check=True)
+                     .stdout.strip().split("|") for _ in range(2))
+    assert first[1:] == ["/tmp/t0019 cache", "probe"]
+    assert first[0] != str(fake_home) and second[0] != first[0]
+    assert Path(first[0]).is_dir() and Path(first[0]) == Path(first[0]).resolve()
+    assert list(fake_home.iterdir()) == []
