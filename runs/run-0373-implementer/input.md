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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0373-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0373-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0039.1` (branch `factory/T-0039.1`, base `b002c95b18b3cd1dad4329cdc4e13b6fe71b18af`, head `b002c95b18b3cd1dad4329cdc4e13b6fe71b18af`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0039.1

T-0039.1 / Give the implementer, verifier, code reviewer, planner and triage the reading rules the spec writer and critic already have (#76, prompt part)
Depends on: none
Parallel-safe: yes

Parent: T-0039, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- The five role prompts carry the critic's reading paragraph in every copy
- Only the paragraph is added, and no other prompt changes
- Implementer, reviewer and verifier runs receive the reading paragraph
- Triage and planner runs receive the reading paragraph
- The changelog records the reading rules for the five roles as its last entry
- The reading-rules change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0039/v2.md`

=== proposal.md
## Problem

Five of the factory's seven role prompts lack the reading rules that cut the spec writer's token use by about 37% at the same quality. The five are triage, planner, implementer, code reviewer and verifier. The operator pays for those tokens on every ticket. The implementer and the verifier pay the most, because they run test suites and other long commands. The factory runs each step of a ticket as a separate model agent, a "role": triage sorts a request, the spec writer drafts a spec, the critic checks it, the planner splits it into sub-tickets, the implementer writes the code, the code reviewer reads the diff and the verifier re-runs the checks. Each role is steered by its own written prompt.

An agent works in turns. A turn is one call to the model, and every call re-sends everything the agent has read so far in the run. A file read whole, or a test run printed in full, is paid for again on every later turn. Issue #73 gave the spec writer and the critic a short paragraph of reading rules: put independent reads and commands in one turn, read only the line range a search found, and send long command output to a file in the run's scratch directory (a per-run folder for temporary files), then search or tail that file. In the operator's replay of past runs, the spec writer's tokens fell by about 37% with the same spec quality. The same replay found no saving for the critic, whose prompt #73 had also given a cap on how much it could check. That cap made it check less, and it was removed. The reading rules stayed.

This change adds the same paragraph to the five other prompts and to nothing else.

Each prompt exists in three copies that must agree: a block in the design document, a verbatim copy of that block under `docs/prompts/`, and the copy the harness actually sends (`factory/prompts/`), which differs from the documented one only where the harness fills in values. All three copies change. The operator's replay of past build runs then decides whether the running harness moves to the new prompts.

## Root cause

The #73 change (T-0034) scoped the rules to the spec writer and critic, which were the two roles it measured. Its decision log records "No shared preamble line ... which would reach every role, including the implementer and verifier, which the request does not cover." No later ticket added them to the other roles.

## Out of scope

- The spec writer and critic prompts, the shared preamble, the retro and doc-reviewer prompts, and `agents/`.
- Any existing line of the five prompts: no rubric, routing, round limit, required section or output format changes.
- The enforcing hook that refuses whole-file reads and uncapped searches (#76 part B, with #65).
- The replay procedure itself (#80).
- `docs/principles.md` principle 13's "Implemented by" line, which still credits reading rules to #73 only. The operator keeps those status lines up to date (commit `4a34e40`, "statuses updated for #57, #75, #78").
- `README.md` and `dev/build-harness.spec.md`. This change adds no command, state, stop or path, and neither document describes the reading rules.

## Open questions

none

## Decisions

- All five roles get the critic's form of the paragraph, word for word, as one bullet starting `- Turn economy: `. It carries the three reading rules and the sentence saying why they matter. The spec writer's "as few writes as you can" stays out, as the request says. The writer's "such as a suite run" example also stays out, because the code reviewer must not run the suite. With one text, one check covers all five prompts.
- The paragraph goes into each role's own prompt, not into the shared preamble. A preamble line would also reach the spec writer and critic, which already carry the rules, and T-0034 rejected a preamble line for the same reason. The request names the five prompts.
- New lines only: no existing line of any prompt changes. Placement: in the implementer and verifier, a RULES bullet directly before the declared-path bullet, so that bullet stays last under RULES where T-0029 put it. In the code reviewer, the last bullet of WHAT YOU RUN, which is about the commands it runs. In the planner and triage, the last RULES bullet. In triage's run copy, that is before the instance-added "Acceptance items" block.
- Acceptance checks the text each role receives: all three prompt copies and the composed run prompt. The request's own acceptance, the operator replaying past implementer and verifier runs with old and new prompts, is an Operator step. It needs live model runs and a human judgement of verdict quality (as in T-0034 and T-0029).
- `docs/changelog.md` gains entry 64 after entry 63 and before the closing "Declined:" line. The entry cites the #74 replay result as entry 59.

## Risk

Every future run of the five roles reads this paragraph once the runtime moves. The behavioural risk is a role that reads too little. For example, a verifier might tail a suite log and miss a failure printed earlier. The paragraph does not lift the verifier's "Record the actual output" or the implementer's acceptance-result reporting. A role that greps a log still reports what it found. There is a precedent: the #74 replay (changelog entry 59) found that #73's critic rules saved no tokens and made the critic check less. #74 acted on it by removing the cap and the build ban and keeping the reading sentences, but the two were never tested apart. The operator's replay is the check on this risk. A merge into `main` does not change the running harness, so nothing reaches live runs until the operator moves the runtime.

Protected paths: `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `factory/prompts/reviewer.md`, `factory/prompts/planner.md`, `factory/prompts/triage.md`, `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md`, `docs/prompts/06-code-reviewer.md`, `docs/prompts/04-planner.md`, `docs/prompts/01-triage.md`

## Operator steps

1. After merge and before moving the runtime, replay two or three past build runs of the implementer and verifier with the old and the new prompts, on the same inputs and bases. Compare agent calls, tokens and verdict quality. (#80 tracks the replay procedure.)
2. Only if the replay holds quality, move the runtime checkout to the new harness revision and accept it (`--accept-harness`). If it does not, report the result on #76 and leave the runtime where it is.

=== design.md
## Proposed change

The paragraph, wrapped as a bullet at 72 columns, is exactly:

```
- Turn economy: every turn re-sends everything read so far, so a
  wasted turn or a long printout costs again on every later turn. Put
  independent reads and commands in one turn. Once grep has found the
  lines you need, read that line range, not the whole file. Send long
  output to a file in your scratch directory and grep or tail it,
  rather than printing it in full.
```

A. Implementer and verifier. In `factory/prompts/implementer.md`, `docs/prompts/05-implementer.md` and the "## 5. Implementer" block of `docs/design.md`, insert the paragraph as a RULES bullet directly before the bullet `- A protected path the sub-ticket declares is not an escalation: the`. Do the same in `factory/prompts/verifier.md`, `docs/prompts/07-verifier.md` and the "## 7. Verifier" block.

B. Code reviewer. In `factory/prompts/reviewer.md`, `docs/prompts/06-code-reviewer.md` and the "## 6. Code reviewer" block, insert the paragraph as the last bullet of WHAT YOU RUN, after the line `  one test or a grep, and cite its output with that finding.`

C. Planner and triage. In `factory/prompts/planner.md`, `docs/prompts/04-planner.md` and the "## 4. Planner / decomposer" block, insert it as the last RULES bullet, after `  siblings to re-verify, so parallel sub-tickets are not free.` In `factory/prompts/triage.md`, `docs/prompts/01-triage.md` and the "## 1. Triage" block, insert it as the last RULES bullet, after `  When unsure between ACCEPT and CLARIFY, choose CLARIFY.` In the run copy, that puts it before the blank line and the "Acceptance items describe behaviour" block.

D. Changelog. Add entry `64. After issue #76 (2026-10-09), ...` directly after entry 63 and before the closing "Declined:" line of `docs/changelog.md`. It says that the implementer, verifier, code reviewer, planner and triage prompts gain #73's three reading rules in the critic's form, without the spec writer's one-write sentence. It cites the #74 replay result (entry 59), says nothing else in the prompts changes and the hook stays with #65, says the runtime moves only after the operator's replay of implementer and verifier runs, and records the rejected preamble line.

The prototype touched 12 files with 91 added lines and none removed.

## Tests to change

none

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The implementer, verifier, code reviewer, planner and triage carry the reading rules
Every copy of the implementer, verifier, code reviewer, planner and triage prompts (the `docs/design.md` block, its `docs/prompts/` file and the `factory/prompts/` run copy) SHALL carry the Turn economy paragraph in the critic's words, and MUST NOT carry the spec writer's `as few writes as you can`. Each design block MUST stay byte-identical to its `docs/prompts/` file, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: The five role prompts carry the critic's reading paragraph in every copy
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for r in "1. Triage|01-triage.md|triage" "4. Planner / decomposer|04-planner.md|planner" "5. Implementer|05-implementer.md|implementer" "6. Code reviewer|06-code-reviewer.md|reviewer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF "$P" | grep -c .) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF "$P" | grep -c .) writes=$(cat docs/prompts/$c factory/prompts/$f.md | tr '\n' ' ' | tr -s ' ' | grep -c 'as few writes as you can') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly five lines: `triage copy=SAME doc=1 run=1 writes=0 fill=unchanged`, then the same for `planner`, `implementer`, `reviewer` and `verifier`. `copy=SAME`: the design block equals its `docs/prompts/` file. `doc` and `run`: the documented copy and the run copy each carry the whole paragraph once, joined into one line so it may wrap. `writes=0`: neither carries the spec writer's one-write sentence. `fill=unchanged`: the run copy differs from the documented copy only where it did on `main`.

### Requirement: The reading rules are the only change to the role prompts
In the ten `docs/prompts/` and `factory/prompts/` files of the five roles, the lines this change adds SHALL be the paragraph and nothing else, and no existing line SHALL be removed or changed, nor any line of `docs/design.md`. No other file under `docs/prompts/`, `factory/prompts/` or `agents/` SHALL change.

#### Scenario: Only the paragraph is added, and no other prompt changes
- WHEN `(P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; F="docs/prompts/01-triage.md docs/prompts/04-planner.md docs/prompts/05-implementer.md docs/prompts/06-code-reviewer.md docs/prompts/07-verifier.md factory/prompts/triage.md factory/prompts/planner.md factory/prompts/implementer.md factory/prompts/reviewer.md factory/prompts/verifier.md"; extra=0; for f in $F; do A=$(git diff -U0 main...HEAD -- $f | grep '^+' | grep -v '^+++' | cut -c2- | tr '\n' ' ' | tr -s ' ' | sed 's/^ //; s/^- //; s/ $//'); [ -z "$A" ] || [ "$A" = "$P" ] || extra=$((extra+1)); done; deleted=$(git diff -U0 main...HEAD -- $F docs/design.md | grep '^-' | grep -vc '^---'); others=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts agents | grep -vxF $(for f in $F; do printf -- '-e %s ' $f; done) | grep -c .); echo "extra=$extra deleted=$deleted others=$others")`
- THEN it prints exactly `extra=0 deleted=0 others=0`. `extra` counts the ten files whose added text is anything other than the paragraph. `deleted` counts removed lines in those files and the design doc. `others` counts changed prompt or agent files outside the ten.

### Requirement: Runs of the five roles receive the reading rules
The system prompt that `run start` writes for an implementer, code reviewer, verifier, triage and planner run SHALL contain the Turn economy paragraph once, and MUST NOT contain `as few writes as you can`.

#### Scenario: Implementer, reviewer and verifier runs receive the reading paragraph
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for r in implementer reviewer verifier; do X=$(prompt $r); echo "$r preamble=$(echo "$X" | grep -c "UNTRUSTED INPUT") economy=$(echo "$X" | grep -cF "$P") writes=$(echo "$X" | grep -c 'as few writes as you can')"; done)`
- THEN it prints exactly `implementer preamble=1 economy=1 writes=0`, `reviewer preamble=1 economy=1 writes=0`, `verifier preamble=1 economy=1 writes=0`, one per line. `preamble=1` shows the run started and its prompt was read.

#### Scenario: Triage and planner runs receive the reading paragraph
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-triage >/dev/null; bin/factory ticket set T-0002 status=ready-for-planner >/dev/null; bin/factory run start --role triage --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role planner --ticket T-0002 >/dev/null 2>&1; for r in triage planner; do X=$(tr '\n' ' ' < $(ls $FACTORY_STATE/runs/*-$r/system-prompt.txt) | tr -s ' '); echo "$r preamble=$(printf '%s' "$X" | grep -c 'UNTRUSTED INPUT') economy=$(printf '%s' "$X" | grep -cF "$P") writes=$(printf '%s' "$X" | grep -c 'as few writes as you can')"; done)`
- THEN it prints exactly `triage preamble=1 economy=1 writes=0`, then `planner preamble=1 economy=1 writes=0`

### Requirement: The documents record the reading rules for the five roles
`docs/changelog.md` SHALL gain one entry for issue #76 as its last numbered entry, numbered without a gap, placed before the closing "Declined:" line, naming the five roles and the operator's replay. The change MUST add no whitespace errors.

#### Scenario: The changelog records the reading rules for the five roles as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; echo "terms=$(grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oiF -e '#76' -e implementer -e verifier -e 'code reviewer' -e planner -e triage -e replay | tr A-Z a-z | sort -u | grep -c .) footer=$(tail -1 docs/changelog.md | grep -c '^Declined: a dedicated merge agent')")`
- THEN it prints `64 CONTIGUOUS`, then `terms=7 footer=1`

#### Scenario: The reading-rules change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

- The five role prompts carry the critic's reading paragraph in every copy → NEW; today each of the five lines prints `doc=0 run=0` (`copy=SAME writes=0 fill=unchanged` already hold), because no copy of these prompts carries the paragraph.
- Only the paragraph is added, and no other prompt changes → REGRESSION; prints `extra=0 deleted=0 others=0` on base and must still after the change. A mutated prototype printed `extra=2 deleted=1 others=1`.
- Implementer, reviewer and verifier runs receive the reading paragraph → NEW; today prints `preamble=1 economy=0 writes=0` for each role. The run starts, but its prompt lacks the paragraph.
- Triage and planner runs receive the reading paragraph → NEW; today prints `triage preamble=1 economy=0 writes=0`, then `planner preamble=1 economy=0 writes=0`.
- The changelog records the reading rules for the five roles as its last entry → NEW; today prints `63 CONTIGUOUS`, then `terms=2 footer=1`, because the last entry is #57's.
- The reading-rules change adds no whitespace errors → REGRESSION; prints `exit=0` on base.
