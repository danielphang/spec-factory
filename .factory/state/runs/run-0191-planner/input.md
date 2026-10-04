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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0191-planner/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Approved spec (v2, pinned)

=== proposal.md
## Problem

Agents the factory runs at the same time can overwrite each other's temporary files, and some agents leave files in the operator's working copy. As a result the operator sees wrong or discarded results and cannot safely run intakes for several tickets at once, even though the README recommends doing that.

Some terms. A role is one of the factory's agents, such as the spec writer or the verifier. A run is one start of a role on one ticket. The harness gives each run a directory in the store, which is the factory's on-disk record of tickets and runs, and keeps the run's input, prompt and output there. A session scratchpad is a temporary directory that Claude Code gives to one session. Every agent that session launches inherits the same path, and the host tells each of them to put temporary files there. Checkers are the two roles that check a built change: the reviewer and the verifier. The dev checkout is `~/dev/spec-factory`, the working copy where the operator works and where tickets merge. A ticket is parked when the factory stops it so a human can answer a question or rule on a failure.

Nothing in the factory gives a run its own place for temporary files such as prototypes, clones of the code under test or throwaway stores. So runs that happen at the same time write into one shared directory. One run can then overwrite another's files, or run and cite a prototype that another run built. Other runs write inside the dev checkout instead. The requester needs each run's temporary files kept apart from every other run's and out of the dev checkout. The files should be cleared when the run is done, but kept while its ticket is parked, so a human can look at them.

## Evidence

Three runs hit the problem:

| Run | What happened | Source |
|---|---|---|
| Nanobot store, run-0068 (spec writer) | "My session scratchpad was overwritten during this run by files from other work: a WhatsApp chat-log check and a `/summarize` check. I moved my prototype to a unique subdirectory and did not touch the foreign files." | `~/dev/nanobot-upstream/.factory/state/runs/run-0068-spec_writer/output.md:576`, read for this spec |
| run-0134-verifier | It unpacked its base checkout over a stale `scratchpad/base` directory that another run had left. pytest there printed `23 failed, 103 passed`, a mix of two trees. It threw those results away and redid every base check in fresh clones. | `.factory/state/runs/run-0134-verifier/output.md:38` |
| run-0062-verifier | It created `/Users/dphang/dev/spec-factory/.venv` in the dev checkout. The head it checked had no `pyproject.toml`, so `uv` walked up from the checker's worktree to the dev checkout's project. | `.factory/state/runs/run-0062-verifier/output.md:28`; `ls -la .venv` shows the directory last modified on Oct 3 at 01:12 local time, a minute after the run started (08:11 UTC). This spec does not fix this case; see Out of scope. |

The retro of 2026-10-04 (item H8, `.factory/answers/retro-trial-2026-10-04/retro_with_efficiency.md:159`) also says that run-0103 left an untracked throwaway store under the dev checkout. I did not find that in the run's own output.

What the harness does today, on `main` at `d15d833`:

- The preamble is the shared opening of every role's prompt (`factory/prompts/preamble.md`). Its RUNNING CODE section sets `HOME` and says nothing about where temporary files go.
- `run start` (`factory/cli.py:198`) creates `runs/<run id>/` with `meta.yaml` and `system-prompt.txt`, and no directory for temporary files.
- The store's `.gitignore` covers `worktrees/`, `runs/*/wt/` and `runs/*/tripwire.yaml`, and nothing else (`factory/store.py:49-63`). `run start` writes that file only for build roles or when a tripwire baseline exists (`factory/cli.py:223`, `:242`).
- `run cleanup` (`factory/cli.py:266`) removes only a checker's worktree.

The acceptance scenarios below were run on a clone of `main` at `d15d833`, with the fixture instance and a throwaway store. They printed:

- scenario 1: `run-0001-triage dir=no heading=0 own=0 other=0`. No run gets a scratch directory, and no input names one.
- scenario 2: `0`. No role's system prompt holds the rule's precedence clause.
- scenario 4: `untracked_scratch=1`. A file under a run's directory would be picked up when the store is committed.
- scenario 5: `1 1 1 0`. An existing store `.gitignore` is not extended on `run start`.
- scenario 6: `after_move A=kept B=kept`. Nothing ever clears a run's temporary files.

I also ran the same harness scenarios on a prototype of the proposed change, and each printed its expected result. The harness suite printed `203 passed` on `main`, and `1 failed, 202 passed` on the prototype of parts A to D. The one failure is the test listed under Tests to change. In round 2 I re-ran scenario 2 with its new check and the reflowed preamble text of design part C. It printed `0` on `main` and `1` on a prototype that carries only that text in all three preamble copies, and the suite on that prototype printed `203 passed`.

## Root cause

- `factory/cli.py:198` `run_start` reserves `runs/<run id>/` but creates no directory for temporary files.
- `factory/compose.py:85-90` builds every role's input with an Output file section and a Running code section, and names no place for temporary files.
- `factory/prompts/preamble.md` RUNNING CODE says how to run code but not where its files go. So the host's own instruction to use the session scratchpad is the only one an agent receives.
- `factory/store.py:53` `ensure_gitignore` knows three ignore lines. When any of them is missing it appends its whole block again, so an older store's file would get duplicate lines.
- Nothing removes a run's leftovers except a checker's worktree (`factory/cli.py:266`).

## Out of scope

- The worktrees the build half already owns, `worktrees/<ticket>` and `runs/<run id>/wt/`, and where they live.
- The run-0062 `.venv` case. The gate command ran as instructed in the checker's worktree, which sits inside the store and so inside the dev checkout. `uv` walked up only because that head had no `pyproject.toml` of its own. A rule about where to put temporary files cannot stop this. Every head of this repo now has `pyproject.toml` at its root, so `uv` stays inside the worktree. The fix would be to move checker worktrees out of the dev checkout, or to tell `uv` which project to use. Both change the worktrees named above, so this needs its own ticket.
- Runs that never finish, which stay in flight. Their temporary files are not cleared; that belongs with the in-flight cleanup work.
- The workflow scripts (`factory/workflows/*.js`), the routing table, the gates and the merge rule do not change.
- Setting `TMPDIR` to the run's scratch directory in the running-code wrapper. Cut: the ticket's intent is met without it.

## Open questions

none

## Decisions

- Each run's temporary files go in its own scratch directory, `runs/<run id>/scratch/` in the store. `run start` creates it and the store's `.gitignore` excludes it. This is a standing decision that later tickets must follow. Rejected: the system temp directory, because the OS clears it on its own schedule, so a parked run's files could vanish, and the files would not sit beside the run's record.
- The scratch directory is inside the store, which in this repo sits inside the dev checkout. It still meets the requester's need: git ignores it and the harness clears it, so `git status` in the dev checkout never shows it.
- A finished run's scratch directory is removed when its ticket next changes state, unless the new state is `parked`. So it is kept while the ticket is parked, and removed once a human sends the ticket on or closes it. One consequence: a spec writer's prototype is gone before the critic or the operator at the spec gate reads the spec, because the ticket moves on to the critic as soon as the writer finishes. A prototype survives only while its ticket is parked, so a writer who wants the gate to see one must put what it showed in the spec itself. Rejected: removing it at `run finish`, because the workflow decides whether to park only after `run finish`, so a parked run's files would already be gone. Rejected: a cleanup call on each path in the workflow scripts where the ticket continues, because that adds many call sites and one missed path leaks.
- The preamble rule says it takes precedence over any other instruction to use a session scratchpad. Without that, an agent follows the host's own instruction, which arrives first.
- No command can check whether an agent obeys the rule. Acceptance checks what the harness controls: the directory, the input that names it, the prompt rule, the ignore line and the clearing.

## Risk

- Blast radius: every role's system prompt gains a 10-line section, and every run start gains one directory and a `.gitignore` check. Every ticket state change except a change to `parked` now deletes directories. The deletion is limited to the `runs/*/scratch` directories of finished runs of that one ticket. A bug there could delete another run's scratch files, but never anything outside `runs/*/scratch`.
- If a role makes a `git worktree` (instead of a clone) inside its scratch directory, removing the directory leaves a stale worktree entry in that repository's `.git`. `git worktree prune` clears it.
- Protected paths touched: harness (`factory/cli.py`, `factory/compose.py`, `factory/store.py`, `factory/prompts/preamble.md`); generated (`docs/prompts/00-preamble.md`, re-copied from the design doc block); the existing test `tests/factory/test_tripwire.py`, as listed under Tests to change.
- A merge changes nothing that runs. The factory runs from a separate copy of this repo, the runtime checkout `~/dev/spec-factory-harness`, which changes only when the operator moves it to a new revision (the upgrade step in the README). After that move, each instance has to accept the new revision with `--accept-harness`. An instance is one repo the factory runs against, with its own store. After it accepts, the harness itself rewrites that instance's store `.gitignore` at the first `run start`. These files are `.factory/state/.gitignore` here (infra) and `~/dev/nanobot-upstream/.factory/state/.gitignore` (reference_harness). The PR does not edit either file.
- No routing, gate or merge-rule change, and no check is loosened. Moving the runtime checkout back to the previous revision reverts the change.

## Operator steps

1. Before the upgrade step moves the runtime checkout (`~/dev/spec-factory-harness`, the copy the factory runs from) to this revision, run the operator's own acceptance test on the new preamble text. The operator's spec-gate policy, `.factory/answers/queue-preapproval-policy.md`, requires this test for any prompt change but does not set its steps.
2. After the runtime checkout has moved and this repo's instance has accepted the revision (`--accept-harness`), the first `run start` adds `runs/*/scratch/` to `.factory/state/.gitignore`, and also `runs/*/tripwire.yaml` if that line is missing. Commit that file with the store. The Nanobot instance's store gets the same lines when it accepts the revision.
3. On the first parallel intake after the runtime checkout has moved, check that each run's files are under its own `.factory/state/runs/<run id>/scratch/`. Then check that `git status --porcelain --untracked-files=all` in `~/dev/spec-factory` lists nothing under those directories.

=== design.md
## Proposed change

A. Scratch directory at run start (`factory/cli.py` `run_start`, `factory/store.py`).
- After `meta.yaml` is written, `run_start` creates `runs/<run id>/scratch/` for every role. It calls `store.ensure_gitignore(root)` for every role, not only for build roles or when a tripwire baseline exists. A refused start still writes nothing, because the directory is created only after every guard has passed.
- `store.STORE_GITIGNORE` gains a comment line and `runs/*/scratch/`. `ensure_gitignore` checks four lines: `worktrees/`, `runs/*/wt/`, `runs/*/tripwire.yaml`, `runs/*/scratch/`. It writes the full commented block when the file is absent or empty. Otherwise it appends only the missing lines, never a second copy of lines already there. Existing lines and comments stay as they are.

B. The input names the directory (`factory/compose.py` `compose`). Directly after the Running code section, before any declared source, every role's input gets this section:

```
## Scratch directory
Put every file you make for your own use in this run under `<absolute path of runs/<run id>/scratch>`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.
```

The path is `root / "runs" / run_id / "scratch"`, under the same resolved store root that the Output file section uses. It is not a store source, so `input_sources` does not change.

C. The preamble rule. Insert this block between RUNNING CODE and GUARDRAIL PATHS, identically in `docs/design.md` §Shared preamble (the source of truth), `docs/prompts/00-preamble.md` (re-copied from it) and `factory/prompts/preamble.md`. The precedence clause sits on one line so that scenario 2 can find it:

```
SCRATCH FILES
- Put every file you make for your own use (a prototype, a clone, a
  log, a throwaway store) under the directory named in the "Scratch
  directory" section of your input. No other run uses it.
- Never put such files in a session scratchpad, in a repository
  checkout or in another run's directory. On where files go, this rule
  takes precedence over any other instruction to use a session scratchpad.
- The harness clears the directory when the ticket moves on, and keeps
  it while the ticket is parked so a human can inspect it.
```

D. Clearing (`factory/store.py`). `save_ticket` is the only place a ticket record is written (`grep` finds no other writer of `tickets/<id>.yaml`). Before writing, it reads the stored status. After writing, if a stored status existed, the new status differs from it and the new status is not `parked`, it calls a new `clear_scratch(root, ticket_id)`. That function walks `runs/*/scratch`. For each directory whose run `meta.yaml` names that ticket and has `finished` set, it removes the directory tree. Runs still in flight, runs of other tickets and every other path are left alone. `run finish` does not change status, so it clears nothing. `ticket park` and a tripwire park set `parked`, so they keep everything. Every later change of state clears: `ticket transition`, `resolve`, `approve-spec`, `request-changes`, `merge`, `ticket parent-check`, `ticket ready-implementers` and `ticket set status=…`.

E. Documents.
- `docs/design.md` §Harness: after the "Tripwire on live files" paragraph, add a "Scratch directory per run" paragraph. It says what A, B and D do, and gives the reason for keeping files while a ticket is parked.
- `docs/changelog.md`: the next numbered entry, "After issue #35 (2026-10-04) …", giving the evidence in one sentence and the change in A to D.
- `dev/build-harness.spec.md`: the `factory run start` bullet (line 203) lists `runs/<run_id>/scratch/` among what it writes. After-run item 6 (line 301) says that scratch is cleared on the ticket's next state change other than `parked`.
- `README.md`: replace the caveat at lines 298-300 ("One caveat until #35 lands: …") with one sentence. It says that each run has its own scratch directory in the store, cleared when its ticket moves on and kept while it is parked. Following the page's own rule for untried features, it adds that this is tested but has not yet run on a real ticket. Bump the status-header date. The issue number moves to "Related work and history", if it is kept at all.

F. New tests in a new file, `tests/factory/test_run_scratch.py`, black-box through `bin/factory` on a throwaway store, like `test_run_isolation.py`. They cover scenarios 1 to 7 below, plus a refused `run start` that leaves no `runs/` entry.

Size: about 30 changed lines of harness code, 30 of prompt text across the three copies, 30 of documents and about 120 of new tests. That is well under 400.

## Tests to change

- `tests/factory/test_tripwire.py:230-231`, in `test_no_tripwire_key_writes_and_prints_what_it_did_before`. It asserts that, when no tripwire is configured, a run directory holds exactly `meta.yaml`, `output.md` and `system-prompt.txt`, and that the store has no `.gitignore`. Part A makes every `run start` create `scratch/` and the store `.gitignore`, so both assertions break by design. Change: the expected listing becomes `["meta.yaml", "output.md", "scratch", "system-prompt.txt"]`. Line 231 becomes an assertion that `runs/*/scratch/` is a line of the store's `.gitignore`. The test's point stays intact: with no tripwire key there is still no `tripwire.yaml`, and the JSON that `run finish` prints is unchanged. On the prototype this was the only failing test (`1 failed, 202 passed`).

=== specs/run-scratch/spec.md
## ADDED Requirements

### Requirement: each run has its own scratch directory, named in its input
`run start` MUST create `runs/<run id>/scratch/` for every role, and the composed input MUST name that absolute path under a `## Scratch directory` heading, never another run's.

#### Scenario: two runs get separate scratch directories, each named only in its own input
- GIVEN the repository root as the working directory, and the command run through the Running code wrapper
- WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; rid(){ sed -E 's/.*"run_id": "([^"]+)".*/\1/'; }; printf '# A\n\nx\n' >$S.a; printf '# B\n\ny\n' >$S.b; bin/factory ticket new --file $S.a >/dev/null; bin/factory ticket new --file $S.b >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | rid); B=$(bin/factory run start --role triage --ticket T-0002 | rid); c(){ bin/factory run compose $1 >/dev/null; echo "$1 dir=$(test -d $S/runs/$1/scratch && echo yes || echo no) heading=$(grep -c '^## Scratch directory$' $S/runs/$1/input.md) own=$(grep -c "$S/runs/$1/scratch" $S/runs/$1/input.md) other=$(grep -c "$S/runs/$2/scratch" $S/runs/$1/input.md)"; }; c $A $B; c $B $A`
- THEN it prints exactly two lines, `run-0001-triage dir=yes heading=1 own=1 other=0` and `run-0002-triage dir=yes heading=1 own=1 other=0`

### Requirement: the preamble directs temporary files to the run's scratch directory
Every role's system prompt MUST tell the agent to put its own temporary files only in its run's scratch directory, and MUST say that this takes precedence over any instruction to use a session scratchpad.

#### Scenario: a run's system prompt carries the scratch rule
- GIVEN the repository root as the working directory, and the command run through the Running code wrapper
- WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; printf '# A\n\nx\n' >$S.a; bin/factory ticket new --file $S.a >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | sed -E 's/.*"run_id": "([^"]+)".*/\1/'); grep -c 'takes precedence over any other instruction to use a session scratchpad' $S/runs/$A/system-prompt.txt`
- THEN it prints exactly `1`

#### Scenario: the three copies of the preamble stay identical
- GIVEN the repository root as the working directory
- WHEN `awk '/^## Shared preamble/{f=1} f&&/^.{3}text$/{p=1;next} p&&/^.{3}$/{exit} p' docs/design.md | diff - docs/prompts/00-preamble.md && diff docs/prompts/00-preamble.md factory/prompts/preamble.md && echo SAME`
- THEN it prints `SAME` and nothing else

### Requirement: the store never commits a scratch directory
The store's `.gitignore` MUST exclude `runs/*/scratch/` after any `run start`. An existing `.gitignore` MUST keep its own lines and gain only the lines it lacks, each once.

#### Scenario: a file in a run's scratch directory is ignored by git
- GIVEN the repository root as the working directory, and the command run through the Running code wrapper
- WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; printf '# A\n\nx\n' >$S.a; bin/factory ticket new --file $S.a >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | sed -E 's/.*"run_id": "([^"]+)".*/\1/'); mkdir -p $S/runs/$A/scratch; touch $S/runs/$A/scratch/f; git -C $S init -q; echo "untracked_scratch=$(git -C $S status --porcelain --untracked-files=all | grep -c /scratch/)"`
- THEN it prints `untracked_scratch=0`

#### Scenario: an existing store .gitignore gains only the missing line
- GIVEN the repository root as the working directory, and the command run through the Running code wrapper
- WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; printf '# A\n\nx\n' >$S.a; bin/factory ticket new --file $S.a >/dev/null; printf '# kept\nworktrees/\nruns/*/wt/\n' >$S/.gitignore; bin/factory run start --role triage --ticket T-0001 >/dev/null; echo "$(grep -c '^# kept$' $S/.gitignore) $(grep -cxF 'worktrees/' $S/.gitignore) $(grep -cxF 'runs/*/wt/' $S/.gitignore) $(grep -cxF 'runs/*/scratch/' $S/.gitignore)"`
- THEN it prints `1 1 1 1`

### Requirement: scratch is cleared when the ticket moves on, and kept while it is parked
When a ticket changes to any state other than `parked`, the harness MUST remove the scratch directory of each finished run of that ticket. It MUST NOT remove the scratch directory of a run still in flight, of another ticket's run, or of any run while its ticket is parked.

#### Scenario: moving a ticket on clears its finished run's scratch and no other ticket's
- GIVEN the repository root as the working directory, and the command run through the Running code wrapper
- WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; rid(){ sed -E 's/.*"run_id": "([^"]+)".*/\1/'; }; printf '# A\n\nx\n' >$S.a; printf '# B\n\ny\n' >$S.b; bin/factory ticket new --file $S.a >/dev/null; bin/factory ticket new --file $S.b >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | rid); B=$(bin/factory run start --role triage --ticket T-0002 | rid); for r in $A $B; do mkdir -p $S/runs/$r/scratch; touch $S/runs/$r/scratch/f; done; printf 'Type: bug\nTitle: A\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n' >$S.o; bin/factory run finish $A --output-file $S.o >/dev/null; k(){ test -e $S/runs/$1/scratch && echo kept || echo removed; }; echo "after_finish A=$(k $A)"; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; echo "after_move A=$(k $A) B=$(k $B)"`
- THEN it prints `after_finish A=kept` then `after_move A=removed B=kept`

#### Scenario: a parked ticket keeps its run's scratch until a human sends it on
- GIVEN the repository root as the working directory, and the command run through the Running code wrapper
- WHEN `S=$(cd "$(mktemp -d)" && pwd -P)/s; export FACTORY_STATE=$S FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance; printf '# A\n\nx\n' >$S.a; bin/factory ticket new --file $S.a >/dev/null; A=$(bin/factory run start --role triage --ticket T-0001 | sed -E 's/.*"run_id": "([^"]+)".*/\1/'); mkdir -p $S/runs/$A/scratch; touch $S/runs/$A/scratch/f; printf 'STATUS: NEEDS-HUMAN\nCONFIDENCE: low\nESCALATIONS: none\n' >$S.o; bin/factory run finish $A --output-file $S.o >/dev/null; bin/factory ticket park T-0001 --reason q --outputs $A >/dev/null; k(){ test -e $S/runs/$A/scratch && echo kept || echo removed; }; echo "parked=$(k)"; bin/factory ticket transition T-0001 --to ready-for-triage --by t >/dev/null; echo "resumed=$(k)"`
- THEN it prints `parked=kept` then `resumed=removed`

### Requirement: the documents describe the scratch directory
The changelog, the build spec and the README MUST describe the per-run scratch directory, and the README MUST drop its interim caveat against parallel intake.

#### Scenario: the documents carry the change
- GIVEN the repository root as the working directory
- WHEN `echo "$(grep -c 'One caveat until #35 lands' README.md) $(grep -c '#35' docs/changelog.md) $(grep -c 'runs/<run_id>/scratch/' dev/build-harness.spec.md)"`
- THEN it prints `0 N M` with N of 1 or more and M of 1 or more

### Requirement: the harness suite still passes
The harness's own test suite MUST pass after the change, with only the test listed under Tests to change edited.

#### Scenario: the harness suite passes
- GIVEN the repository root as the working directory, and the command run through the Running code wrapper
- WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
- THEN it exits 0 and its last line reports no failures

=== verification.md
## Acceptance

- two runs get separate scratch directories, each named only in its own input → NEW. Today it prints `run-0001-triage dir=no heading=0 own=0 other=0` and the same for run-0002: no directory is created and the input has no such section.
- a run's system prompt carries the scratch rule → NEW. Today it prints `0`: no system prompt holds the precedence clause. A stub that only mentions a session scratchpad somewhere also prints `0`.
- the three copies of the preamble stay identical → REGRESSION. It prints `SAME` today, with the 70-line block, and must still do so with the new section in all three.
- a file in a run's scratch directory is ignored by git → NEW. Today it prints `untracked_scratch=1`: a triage `run start` writes no `.gitignore`, and no rule covers `scratch/`.
- an existing store .gitignore gains only the missing line → NEW. Today it prints `1 1 1 0`: `run start` for a triage run leaves the file alone.
- moving a ticket on clears its finished run's scratch and no other ticket's → NEW. Today it prints `after_finish A=kept` then `after_move A=kept B=kept`: nothing clears scratch.
- a parked ticket keeps its run's scratch until a human sends it on → NEW. Today it prints `parked=kept` then `resumed=kept`. The second line is the failing half.
- the documents carry the change → NEW. Today it prints `1 0 0`.
- the harness suite passes → REGRESSION. On a clean clone of `main` at `d15d833` it printed `203 passed`. On the prototype of parts A to D, before the test listed under Tests to change was edited, it printed `1 failed, 202 passed`, and the failure was that test.

How these were checked. In round 1, every scenario command was run verbatim, through the Running code wrapper, on a clone of `main` at `d15d833` and on a clone carrying a prototype of parts A to D. The outputs on the clone of `main` are the "today" values above. The prototype printed the THEN line of every scenario except two. The documents scenario was not prototyped, because the prototype edited no documents besides the preamble copies. The suite scenario on the prototype failed only the test listed under Tests to change, which the prototype did not edit. Scenario 1 was run under both bash and zsh, because an early draft that relied on word splitting failed under zsh.

In round 2, only scenario 2's check and the line breaks of part C's text changed. I re-ran scenario 2 verbatim through the wrapper on a fresh clone of `d15d833`, where it printed `0`. I then ran it on a clone that carries part C's new text in all three preamble copies, committed, where it printed `1`. On that clone the preamble-identity scenario printed `SAME` and the suite printed `203 passed`. The text has a longest line of 79 characters, the same as the current preamble. The round-1 results for the other scenarios do not depend on the preamble text, so I did not re-run them.

## Responses

- [BLOCKING] 6, Operator steps item 1: FIXED. Item 1 now names the upgrade step and the runtime checkout (`~/dev/spec-factory-harness`, the copy the factory runs from), and gives the path of the policy that requires the acceptance test. It also says that the policy requires the test for a prompt change but does not set its steps, since `.factory/answers/queue-preapproval-policy.md:10` names the test and does not describe it. "The runtime moves" is now glossed at its first use in Risk, which also glosses "instance" and `--accept-harness`. Items 2 and 3 say "the runtime checkout has moved".
- [SHOULD-FIX] 2, scenario "a run's system prompt carries the scratch rule": FIXED. The check now greps for the precedence clause `takes precedence over any other instruction to use a session scratchpad`, and THEN is exactly `1`. Part C's block is reflowed so that the clause sits on one line; before, it was split across two lines and the new grep would never have matched. Results: `0` on `main`, `1` on a prototype carrying the new text (see How these were checked).
- [NIT] 4, Decisions third bullet: FIXED. Added that a spec writer's prototype is gone before the critic or the gate operator reads the spec, that a prototype survives only while its ticket is parked, and that a writer who wants the gate to see one must put what it showed in the spec itself.
