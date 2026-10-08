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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0326-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0326-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0326-reviewer/wt` (branch `factory/T-0034.1`, base `2e73dbb8c997a4284649dcc25f5e9fbba8b65fea`, head `f25dffed5f970142f9da01b0ed24f8e8deaac40a`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0034.1

T-0034.1 / Cut the spec writer's and critic's turn count: batch reads, read line ranges, keep long output in scratch; the critic runs no test suites and builds no prototypes
Depends on: none
Parallel-safe: yes

Parent: T-0034, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule
- Spec writer and critic run prompts carry the new rules
- Rubric, round limit, format and every other prompt are unchanged
- The changelog and the principles page record the change
- The turn-economy change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0034/v2.md`

=== proposal.md
## Problem

Two of the factory's agent roles cost more than they need to, and the operator pays for it on every ticket. The factory turns a request into a spec through a chain of three agents called the **intake workflow**. **Triage** checks the request and decides whether it is a real ticket. The **spec writer** investigates the repository and writes the spec. The **critic** reviews that spec before a human approves it. Each agent works in **turns**: one turn is one model call, which reads files or runs commands and then decides what to do next. Every turn re-sends the agent's fixed start-up context (its role prompt and briefing, about 45k tokens) plus everything it has read so far in the run. A run's cost therefore grows with how many turns it takes and how much output it prints.

The spec writer is the most expensive role. It accounts for about a third of all the context tokens the factory's agents use: a median of 29 turns and 5.3M tokens per run. Its prompt says nothing about economy. It reads whole files where a few lines would do. It prints long command output, such as a full test-suite run, into its context, where that output is re-sent on every later turn. It spreads independent reads across separate turns. The critic is cheaper, but it does work its role should not do. It runs the whole test suite and builds **prototype clones** (disposable copies of the repository with the proposed change applied) to settle questions that are the implementer's job. The project's own principles say the critic only reads and spot-checks, with at most two paths and one command per claim. The critic's prompt sets that as a floor ("at least 2 … and 1"), never as a ceiling.

This change adds rules to the two role prompts only. The spec writer is told to batch independent reads into one turn, read line ranges instead of whole files, keep long output in a scratch file and search it, and write the spec in as few writes as it can. The critic is told the same reading rules, plus three more: run no test suite, build nothing, and spend at most two paths and one command on any one claim. A claim that it could settle only by building becomes a finding or a question. No rubric item, round limit or required spec section changes.

A merge does not change what runs. The **harness** is the code that starts each agent with its prompt and records what it produced. The **runtime** is the pinned checkout of the harness that runs tickets, and only an explicit upgrade moves it. Before that upgrade, the operator replays the intake workflow on a few tickets whose specs were already approved, once with the old prompts and once with the new. The operator then judges whether the writer's turns roughly halved and whether the specs stayed as good.

## Root cause

The spec writer prompt (`factory/prompts/spec_writer.md`, with its documented copy `docs/prompts/02-spec-writer.md` and the "## 2. Spec writer" block of `docs/design.md`) tells the writer to investigate and reproduce before writing (PROCESS step 1). It says nothing about how to spend turns or output. The critic prompt (`factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`, the "## 3. Spec critic" block) has a one-line PROCESS section, line 42. That line sets a minimum amount of checking and no maximum. It does not say the critic should not run suites or build. The briefing every role receives tells it how to run the suite (`.factory/context.md` line 14), so a critic that wants certainty has an obvious command to run.

## Out of scope

- The fixed start-up context re-sent on each turn (#65, `--system-prompt-file`).
- Short specs on a bounded path (#64).
- The harness running acceptance commands on the base itself (#67, #68).
- What each role is given as input (T-0030, #24).
- The spec writer's own suite runs and clones. Its investigation may still need them; only how it reads and prints output changes.
- The shared preamble, and every other role's prompt.
- The agent definition templates under `agents/`. Their bodies are already stale copies of the prompts, and T-0030 replaces them with a pointer to the run's `system-prompt.txt`.
- Every rubric item, the round limit, the CONVERGENCE and OUTPUT sections of the critic prompt, and the writer's PROCESS and FORMAT.
- `README.md` and `dev/build-harness.spec.md`. No command, state, stop or path changes, and the build spec does not describe the critic's or writer's process.

## Open questions

none

## Decisions

- The critic keeps its minimum check, at least 2 cited paths and 1 acceptance command per review. It gains a cap of at most 2 paths and 1 command for any one claim. Rejected: replacing the minimum with the cap, which would let a critic approve having checked nothing. `docs/principles.md`'s Spiking section states the bound per claim ("Grounding a claim … two paths, one command").
- The critic runs no test suite and builds nothing (no clone, worktree or prototype of the change). It runs an acceptance command only as the spec gives it, and picks one that runs no test suite. Standing: a later change to the critic prompt keeps this rule, as principle 2 requires.
- A claim the critic could settle only by running a test suite or building the change is a finding for the writer, or a question, and the critic says what it could not check. The finding's severity follows the existing rubric. Rubric item 2 ("NEW items fail today") stays unchanged.
- The writer and the critic get the same three reading sentences: batch independent reads and commands, read a line range once grep has found it, and send long output to a scratch file and grep or tail it. Only the writer gets "write the spec in as few writes as you can". The critic writes one verdict and needs no such rule.
- No shared preamble line. The rules go only in the two role prompts. Rejected: a preamble line, which would reach every role, including the implementer and verifier, which the request does not cover.
- The rules are added as new lines only, so no existing line of either prompt changes. The writer's rule is the last RULES bullet of the documented copy. The critic's rules follow its existing PROCESS line.
- `docs/principles.md` records the critic's new rule under principle 2 and corrects principle 2's status line, which says "reader roles run no suites" was done by #41 alone.
- The request's acceptance, a replay of 2–3 approved intakes with old and new prompts, is an Operator step. Running it needs live model runs, and judging spec quality side by side is a human call. The scenarios check the text the roles receive.

## Risk

Blast radius: every spec writer and critic run in both instances (this repository and the Nanobot fork), once the runtime is upgraded to a revision with this change. Until then nothing running changes. Two failure modes are possible. A writer that reads too little could miss a cited line. A critic capped per claim could under-check a spec. Both are judged in the operator's replay before the runtime moves, and the human spec gate still reads every spec.

Protected paths this change touches:
- harness: `factory/prompts/spec_writer.md`, `factory/prompts/critic.md` (also agent prompts, a guardrail path, changed because this ticket asks for it);
- generated: `docs/prompts/02-spec-writer.md`, `docs/prompts/03-spec-critic.md`, each re-copied from its `docs/design.md` block.

Protected paths: `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/03-spec-critic.md`

Merge-order notes. T-0027 (approved) adds four lines under the critic's rubric item 5. T-0033 (approved) changes the writer's FORMAT `## Risk` line. Neither touches the lines this change adds, and this change's checks compare against whatever `main` holds when the branch is cut.

## Operator steps

1. **Replay before upgrading the runtime.** After merge, and before moving the runtime checkout (`~/dev/spec-factory-harness`) to a revision that includes this change, pick 2–3 tickets whose specs were approved. For each, run the intake workflow twice on a throwaway store. The store is the directory of ticket records, runs and results that the harness reads and writes. A throwaway store is a scratch one in a temporary directory, named by `FACTORY_STATE`, so the live tickets are untouched. Give both replays the same request and base. Run one from the current runtime (old prompts) and one from a checkout of the merged revision (new prompts). For each spec writer and critic run, record its turns and context tokens (`factory/cost.py`), its test-suite runs and its clones. Targets: the writer's median turns roughly halve, and the critic runs no test suite and builds no clone.
2. **Judge the specs side by side.** Read each pair of specs. Upgrade the runtime only if the new-prompt specs are as good as the old ones. If they are not, record what was lost as a new issue before upgrading.

=== design.md
## Proposed change

The four prompt files get added lines only. Each design doc block stays byte-identical to its `docs/prompts/` copy. Each run copy under `factory/prompts/` keeps the differences it has today from its documented copy: `400` and `2` filled in, and the writer's extra "Acceptance items describe behaviour" bullet.

**A. Spec writer: a turn-economy rule** (`docs/design.md` "## 2. Spec writer" block, `docs/prompts/02-spec-writer.md`, `factory/prompts/spec_writer.md`). Insert these seven lines directly after the line `  wrong just to get approved.` (the end of the "On revision" bullet; `docs/design.md:371`, line 58 of both other files). In the run copy they therefore come before the blank line and the "Acceptance items describe behaviour" bullet.

```
- Turn economy: every turn re-sends everything read so far, so a
  wasted turn or a long printout costs again on every later turn. Put
  independent reads and commands in one turn. Once grep has found the
  lines you need, read that line range, not the whole file. Send long
  output, such as a suite run or a scenario's output, to a file in your
  scratch directory and grep or tail it, rather than printing it in
  full. Write the spec in as few writes as you can, ideally one.
```

**B. Critic: a cap, no suites, no builds, and the same reading rules** (`docs/design.md` "## 3. Spec critic" block, `docs/prompts/03-spec-critic.md`, `factory/prompts/critic.md`). Keep the line `Spot-check at least 2 cited paths and 1 acceptance command yourself.` (`docs/design.md:461`, line 42 of both other files). Insert these twelve lines directly after it, before the blank line that precedes `ANTI-GOODHARTING (REVIEWER SIDE)`.

```
Ground any one claim with at most 2 paths and 1 command. Run no test
suite and build nothing: no clone, worktree or prototype of the change.
Pick an acceptance command that runs no test suite, and run it as the
spec gives it. A claim you could settle only by running a test suite or
building the change is a finding for the writer, or a question; say
what you could not check.
Turn economy: every turn re-sends everything read so far, so a wasted
turn or a long printout costs again on every later turn. Put
independent reads and commands in one turn. Once grep has found the
lines you need, read that line range, not the whole file. Send long
output to a file in your scratch directory and grep or tail it, rather
than printing it in full.
```

**C. Nothing else in the prompts.** No other line of the four files changes. The RUBRIC, CONVERGENCE (with its round limit) and OUTPUT sections of the critic, and the ROLE, INPUT, PROCESS and FORMAT sections of the writer, stay byte for byte. No other file under `docs/prompts/`, `factory/prompts/` or `agents/` changes.

**D. Documents.**
1. `docs/changelog.md`: one new numbered entry after the last one, before the closing `Declined:` line, continuing the numbering without a gap. The last entry on `main` today is 57, so the new entry is 58. Write it on one line, as every existing entry is. It must contain the phrases `#73`, `line range`, `scratch directory`, `no test suite` and `two paths and one command`. This text, used in the prototype, does:
   > 58. After issue #73 (2026-10-07), where the spec writer took a third of all workflow context tokens (309M of 866M; a median of 29 agent calls and 5.3M tokens per run), because every call re-sends the start-up context and everything read so far, and where the critic ran the test suite and built prototype clones of the change on its own initiative, though its grounding is meant to stay within two paths and one command per claim. The spec writer prompt gains a RULES bullet, Turn economy: put independent reads and commands in one turn, read a line range once grep has found it, send long output to a file in the run's scratch directory and grep or tail it, and write the spec in as few writes as possible. The critic's PROCESS keeps its minimum spot-check and caps any one claim at two paths and one command; it runs no test suite and builds nothing, and a claim it could settle only by building becomes a finding for the writer or a question. It gains the same reading rules. No rubric item, round limit or required spec section changes, and the shared preamble does not change. Rejected: a shared preamble line, which would reach every role.
2. `docs/principles.md`, principle 2:
   - The "Implemented by" sentence (lines 41–44) ends `` (#41, `factory/prompts/reviewer.md`, `factory/compose.py`). ``. Change that ending to `` (#41, `factory/prompts/reviewer.md`, `factory/compose.py`); the critic's PROCESS section, which runs no test suite and builds nothing (#73, `factory/prompts/critic.md`). ``.
   - Replace the status line (lines 45–46) with: `Status of #72 part B.2 (reader roles run no suites): done by #41 for the code reviewer and by #73 for the critic. The code reviewer is the only reader role that was given gate commands; the critic and triage never were, but the critic ran suites on its own initiative until #73.`
   - Wrap at the file's existing width (about 100 columns).

## Tests to change

none. No test pins the critic's PROCESS line or the absence of these rules. The tests that keep each design block equal to its `docs/prompts/` copy keep passing when parts A and B edit all three copies alike (prototype: `364 passed`).

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The spec writer and the critic carry the turn-economy rules
Every copy of the spec writer prompt SHALL tell it to batch independent reads and commands, read line ranges once grep has found them, keep long output in a scratch file, and write the spec in as few writes as it can. Every copy of the critic prompt SHALL carry the same reading rules, cap any one claim at 2 paths and 1 command, forbid test-suite runs and builds, and turn a claim that needs one into a finding or a question. Each design block MUST stay byte-identical to its `docs/prompts/` copy, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); printf '%s\n' 'Put independent reads and commands in one turn' 'read that line range, not the whole file' 'to a file in your scratch directory and grep or tail it' > $T/both; { cat $T/both; echo 'Write the spec in as few writes as you can'; } > $T/spec_writer; { cat $T/both; printf '%s\n' 'Ground any one claim with at most 2 paths and 1 command' 'Run no test suite and build nothing' 'is a finding for the writer, or a question'; } > $T/critic; for r in "2. Spec writer|02-spec-writer.md|spec_writer" "3. Spec critic|03-spec-critic.md|critic"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `spec_writer copy=SAME doc=4/4 run=4/4 fill=unchanged`, then `critic copy=SAME doc=6/6 run=6/6 fill=unchanged`. `doc` and `run` count the rule phrases found in the documented copy and the run copy, each joined into one line so a phrase may wrap.

### Requirement: Spec writer and critic runs receive the turn-economy rules
The system prompt that `run start` writes for a spec writer run SHALL contain the writer's turn-economy rule, and the one it writes for a critic run SHALL contain the critic's reading rules, its per-claim cap and its no-suite, no-build rule.

#### Scenario: Spec writer and critic run prompts carry the new rules
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0002 status=ready-for-critic >/dev/null; bin/factory run start --role spec_writer --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role critic --ticket T-0002 >/dev/null 2>&1; W=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0001-spec_writer/system-prompt.txt | tr -s ' '); C=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0002-critic/system-prompt.txt | tr -s ' '); echo "spec_writer batch=$(printf "%s" "$W" | grep -c 'Put independent reads and commands in one turn') writes=$(printf "%s" "$W" | grep -c 'Write the spec in as few writes as you can')"; echo "critic batch=$(printf "%s" "$C" | grep -c 'Put independent reads and commands in one turn') suite=$(printf "%s" "$C" | grep -c 'Run no test suite and build nothing') cap=$(printf "%s" "$C" | grep -c 'Ground any one claim with at most 2 paths and 1 command')")`
- THEN it prints exactly `spec_writer batch=1 writes=1`, then `critic batch=1 suite=1 cap=1`

### Requirement: Nothing else in the two prompts changes
The change MUST NOT remove or alter any existing line of the spec writer or critic prompt copies. The critic's RUBRIC, CONVERGENCE and OUTPUT sections and the writer's ROLE, INPUT, PROCESS and FORMAT sections SHALL stay byte for byte as on `main`, and no other file under `docs/prompts/`, `factory/prompts/` or `agents/` SHALL change.

#### Scenario: Rubric, round limit, format and every other prompt are unchanged
- WHEN `(T=$(mktemp -d); n=0; for x in "docs/prompts/02-spec-writer.md|1,/^RULES\$/p" "docs/prompts/02-spec-writer.md|/^FORMAT\$/,\$p" "factory/prompts/spec_writer.md|1,/^RULES\$/p" "factory/prompts/spec_writer.md|/^FORMAT\$/,\$p" "docs/prompts/03-spec-critic.md|1,/^PROCESS\$/p" "docs/prompts/03-spec-critic.md|/^ANTI-GOODHARTING/,\$p" "factory/prompts/critic.md|1,/^PROCESS\$/p" "factory/prompts/critic.md|/^ANTI-GOODHARTING/,\$p"; do f=${x%%|*}; s=${x#*|}; git show main:$f | sed -n "$s" > $T/a; sed -n "$s" $f > $T/b; [ -s $T/a ] || n=$((n+100)); cmp -s $T/a $T/b || { n=$((n+1)); echo "changed: $f $s"; }; done; echo "sections_changed=$n removed=$(git diff main...HEAD -- docs/prompts/02-spec-writer.md docs/prompts/03-spec-critic.md factory/prompts/spec_writer.md factory/prompts/critic.md | grep -v '^---' | grep -c '^-') others=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts agents | grep -vxF -e docs/prompts/02-spec-writer.md -e docs/prompts/03-spec-critic.md -e factory/prompts/spec_writer.md -e factory/prompts/critic.md | grep -c .)")`
- THEN it prints only `sections_changed=0 removed=0 others=0`

### Requirement: The documents record the turn-economy change
`docs/changelog.md` SHALL gain one entry for issue #73 as its last numbered entry, numbered without a gap. `docs/principles.md` principle 2 SHALL name the critic's new rule among its mechanisms and SHALL say part B.2 is done by #41 for the code reviewer and by #73 for the critic. The change MUST add no whitespace errors.

#### Scenario: The changelog and the principles page record the change
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e '#73' -e 'line range' -e 'scratch directory' -e 'no test suite' -e 'two paths and one command' | sort -u | grep -c .; P=$(sed -n '/^### 2\. /,/^### 3\. /p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "implemented=$(printf '%s' "$P" | grep -c 'runs no test suite and builds nothing (#73, .factory/prompts/critic.md.)') status=$(printf '%s' "$P" | grep -c 'done by #41 for the code reviewer and by #73 for the critic')")`
- THEN it prints exactly `CONTIGUOUS`, then `5`, then `implemented=1 status=1`

#### Scenario: The turn-economy change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

- Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule → NEW. On `main` at `2e73dbb` it prints `spec_writer copy=SAME doc=0/4 run=0/4 fill=unchanged`, then `critic copy=SAME doc=0/6 run=0/6 fill=unchanged`: no copy holds any of the rules.
- Spec writer and critic run prompts carry the new rules → NEW. On `main` at `2e73dbb` it prints `spec_writer batch=0 writes=0`, then `critic batch=0 suite=0 cap=0`, the same under `zsh` and `sh`.
- Rubric, round limit, format and every other prompt are unchanged → REGRESSION. On `main` it prints `sections_changed=0 removed=0 others=0`, and on the prototype as well.
- The changelog and the principles page record the change → NEW. On `main` at `2e73dbb` it prints `CONTIGUOUS`, then `0` (the last entry, 57 for #41, holds none of the five phrases), then `implemented=0 status=0`.
- The turn-economy change adds no whitespace errors → REGRESSION. It printed `exit=0` on the prototype.

## Out-of-scope observations

- `agents/factory-spec-critic.md` and `agents/factory-spec-writer.md` repeat old copies of their prompts, including the critic's `Spot-check at least 2 …` line (`agents/factory-spec-critic.md:28`). Inline runs never see them. T-0030 part A.3 replaces those bodies with a pointer to the run's `system-prompt.txt`, which removes the drift.
- The briefing every role receives (`.factory/context.md`, line 14) tells the reader how to run the harness suite, and the composed "Running code" section says to wrap "every test or check command the briefing above gives". A critic could read both as an invitation to run the suite. The new PROCESS lines override that for the critic. If the replay shows critics still running the suite, the briefing is the next place to look. It is infra (`.factory/**`), outside this ticket.

## PR description (the implementer's output)

Sub-ticket: T-0034.1 (parent T-0034, spec v2: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0034/v2.md`)
Branch: `factory/T-0034.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0034.1`, one commit `f25dffe` on base `2e73dbb`.

## What changed

The spec writer and the critic now carry rules that cut how many turns they take and how much they print. The critic is also told to run no test suite and build nothing. Two agent roles are involved. The spec writer is the agent that investigates a request and writes its spec. The critic is the agent that reviews that spec before a human approves it. Each role prompt exists in three copies: a block in the design document (`docs/design.md`), its documented copy under `docs/prompts/`, and the run copy under `factory/prompts/`, which the harness gives the agent. Every change is added lines only.

- **A. Spec writer.** A new `- Turn economy:` RULES bullet goes directly after `  wrong just to get approved.` in all three copies (`docs/design.md` after line 371; `docs/prompts/02-spec-writer.md` and `factory/prompts/spec_writer.md` after line 58). The text is the spec's seven lines verbatim. In the run copy it sits before the blank line and the run copy's extra "Acceptance items describe behaviour" bullet.
- **B. Critic.** The spec's twelve lines go directly after `Spot-check at least 2 cited paths and 1 acceptance command yourself.` in all three copies (`docs/design.md` after line 468 once A has shifted it; `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md` after line 42). They come before the blank line that precedes `ANTI-GOODHARTING (REVIEWER SIDE)`. The existing minimum spot-check line is kept.
- **C. Nothing else in the prompts.** No other file under `docs/prompts/`, `factory/prompts/` or `agents/` changed, and no existing prompt line changed. The REGRESSION check below confirms both.
- **D.1 `docs/changelog.md`.** Entry 58 is added on one line after entry 57 and before `Declined:`. It uses the spec's text verbatim.
- **D.2 `docs/principles.md`, principle 2.** The "Implemented by" sentence now ends `…(#41, `factory/prompts/reviewer.md`, `factory/compose.py`); the critic's PROCESS section, which runs no test suite and builds nothing (#73, `factory/prompts/critic.md`).` The status line is replaced with the spec's text. Both are rewrapped to the file's width.

The insertions in A and B were made by a script under the run's scratch directory (`scratch/edit.py`). The script asserts that each anchor line appears exactly once and at the expected line number. D was edited by hand.

## Acceptance results

All commands were run from the worktree under a fresh HOME, using `zsh`. The NEW items were run before the change (on `2e73dbb`) and after it (on `f25dffe`).

| Scenario | Kind | Before (`2e73dbb`) | After (`f25dffe`) |
|---|---|---|---|
| Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule | NEW | `spec_writer copy=SAME doc=0/4 run=0/4 fill=unchanged` / `critic copy=SAME doc=0/6 run=0/6 fill=unchanged` | `spec_writer copy=SAME doc=4/4 run=4/4 fill=unchanged` / `critic copy=SAME doc=6/6 run=6/6 fill=unchanged` |
| Spec writer and critic run prompts carry the new rules | NEW | `spec_writer batch=0 writes=0` / `critic batch=0 suite=0 cap=0` | `spec_writer batch=1 writes=1` / `critic batch=1 suite=1 cap=1` (the same under `sh`) |
| Rubric, round limit, format and every other prompt are unchanged | REGRESSION | not run | `sections_changed=0 removed=0 others=0` |
| The changelog and the principles page record the change | NEW | `CONTIGUOUS` / `0` / `implemented=0 status=0` | `CONTIGUOUS` / `5` / `implemented=1 status=1` |
| The turn-economy change adds no whitespace errors | REGRESSION | not run | `exit=0` |

Every "before" output matched what `verification.md` predicted, so the spec matched reality before the change.

What the "after" outputs show:
- `copy=SAME`: each design block is still byte-identical to its `docs/prompts/` copy.
- `doc=4/4` and `doc=6/6`, with the matching `run=` counts: every rule phrase is present in both the documented copy and the run copy.
- `fill=unchanged`: each run copy differs from its documented copy exactly as it did on `main`.
- `batch=1 writes=1` and `batch=1 suite=1 cap=1`: the system prompt that `run start` writes for a spec writer run, and for a critic run, contains the new rules.
- `sections_changed=0 removed=0 others=0`: the protected sections are byte for byte as on `main`, no line was removed, and no other prompt file changed.
- `CONTIGUOUS` and `5`: the changelog numbering has no gap, and its last entry holds all five required phrases.
- `implemented=1 status=1`: principle 2 names the critic's rule and the new status.

Gate commands, run exactly as written:
- `git diff --check main...HEAD` exited 0 with no output: the diff adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `364 passed in 225.80s`. The tests that keep each design block equal to its `docs/prompts/` copy are part of that run.

## Tests added/changed

None. The spec's "Tests to change" is none. The scenarios check the text of the prompts directly, and the existing block-equality tests already cover the three copies staying in step.

## Known gaps and uncertainties

- Whether the rules actually halve the writer's turns, and keep spec quality, is not checked here. That is the operator's replay in Operator steps 1–2 (run the intake on a few approved tickets with the old and the new prompts, then compare), which needs live model runs.
- In `docs/principles.md`, two rewrapped lines are 102 and 101 columns wide (lines 44 and 46). The file already has lines from 101 to 112 columns (for example lines 12 and 26), and the spec asks for "about 100".
- factory: markers added: none.
- Protected paths touched, all declared in the spec's Risk section: `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/03-spec-critic.md`.

## Out-of-scope observations

- The `agents/factory-spec-critic.md` and `agents/factory-spec-writer.md` templates still hold old prompt bodies, as `verification.md` already notes. They are left untouched; T-0030 replaces those bodies.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high — every acceptance scenario printed its expected output on `f25dffe`, every NEW one printed its predicted failure on `2e73dbb`, and both gates passed (`364 passed`).
ESCALATIONS: none

## Diff `2e73dbb8c997a4284649dcc25f5e9fbba8b65fea...f25dffed5f970142f9da01b0ed24f8e8deaac40a`

diff --git a/docs/changelog.md b/docs/changelog.md
index da2cefe..6c6a5b7 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -59,5 +59,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 55. After issue #49 (2026-10-04), where the implementer and verifier queued the same declared-path list as the code reviewer: in the store's log, 10 implementer and verifier runs did this, and their lists made up 30 of the 205 items queued so far. The implementer and verifier prompts gain one RULES bullet: a protected path the sub-ticket declares is not an escalation. The code reviewer lists declared paths once for each head it reviews, through its check 6, unchanged. The other two roles may name them in their output, but not under ESCALATIONS. An undeclared protected path, or a change to a declared one that the spec does not describe, still goes under ESCALATIONS from every role. Rejected: the retro's figure of 26 of 139 items, which its own table contradicts with 38.
 56. After issue #48 (2026-10-04), where every approved spec paid for a planner run and every sub-ticket for every gate command, though nine of the thirteen specs planned so far got exactly one sub-ticket, each after a 72 to 302 second planner run that restated it: the small-change lane. A spec that needs one sub-ticket skips the planner. At `ready-for-planner` the build first runs `factory plan whole-spec`, which creates `<parent>.1` from the whole spec, ready for its implementer, naming every scenario of the spec, and logs `plan.skipped`, when the parent has no sub-ticket and no earlier planner run, its latest spec-writer run did not end NEEDS-SPLIT, and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that names seams. Otherwise it reports that the planner is needed, writes nothing, and the planner runs as before; it refuses a parent that is not ready for its planner, has a run in flight or has no approved spec, and the build parks that refusal as a harness bug. To force the planner on such a spec, the operator adds a `### Size and seams` heading at the gate. A gate command may also declare `paths`, as git pathspecs. When a reviewer or verifier run starts on a sub-ticket, the harness marks SKIPPED, with the reason, each command whose paths the sub-ticket's diff touches none of, lists it apart from the commands to run, and records it in the run's `meta.yaml` and on the `ci` row, whose PASS or FAIL still comes from the commands that ran. The implementer and the parent-close verifier still get every command, and a malformed entry refuses every build role's run start. This overturns the cut of the path-scoped skip in T-0016's spec; no repository's gate configuration changes. Rejected: the request's trigger of exactly one lettered part, which would have skipped none of the nine.
 57. After issue #41 (2026-10-04), where a code reviewer started the full test suite in the background, ended its turn to wait for it, and so wrote no review, three times in one day, each time on a commit the verifier had already passed; the harness recorded each run as KILLED and parked the ticket as a budget kill, though it enforces no budget and the agent call reports no reason a run stopped. A role run that ends without writing its output is now EMPTY-OUTPUT in `run finish`, never a budget kill, and the workflow keeps the agent's last message with the run (`factory run last-message`). The same role is re-dispatched once, on the same inputs and in the same round; a second EMPTY-OUTPUT in a row parks the ticket as `EMPTY-OUTPUT from <role>` with both runs, and records no result row for that run, so `resolve --redispatch` re-runs only that checker. A thrown agent call keeps its KILLED record and its `agent call failed` park. The shared preamble gains one RUNNING CODE bullet: run every command in the foreground and never end the turn while one is still running. The code reviewer prompt gains a WHAT YOU RUN section: judge the diff by reading it and leave the test suite and the gate commands to the verifier, which runs them on the same head; a narrow command that confirms one finding is allowed. The reviewer's input no longer lists the gate commands; it says the verifier runs them. The routing table gains two EMPTY-OUTPUT rows. Rejected: keeping a budget-kill label for some empty outputs, and a retry counter in the store.
+58. After issue #73 (2026-10-07), where the spec writer took a third of all workflow context tokens (309M of 866M; a median of 29 agent calls and 5.3M tokens per run), because every call re-sends the start-up context and everything read so far, and where the critic ran the test suite and built prototype clones of the change on its own initiative, though its grounding is meant to stay within two paths and one command per claim. The spec writer prompt gains a RULES bullet, Turn economy: put independent reads and commands in one turn, read a line range once grep has found it, send long output to a file in the run's scratch directory and grep or tail it, and write the spec in as few writes as possible. The critic's PROCESS keeps its minimum spot-check and caps any one claim at two paths and one command; it runs no test suite and builds nothing, and a claim it could settle only by building becomes a finding for the writer or a question. It gains the same reading rules. No rubric item, round limit or required spec section changes, and the shared preamble does not change. Rejected: a shared preamble line, which would reach every role.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 0612cba..6e862ab 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -369,6 +369,13 @@ RULES
 - On revision: respond to each critic finding with FIXED (what changed)
   or DISAGREE (why, with evidence). Don't accept findings you think are
   wrong just to get approved.
+- Turn economy: every turn re-sends everything read so far, so a
+  wasted turn or a long printout costs again on every later turn. Put
+  independent reads and commands in one turn. Once grep has found the
+  lines you need, read that line range, not the whole file. Send long
+  output, such as a suite run or a scenario's output, to a file in your
+  scratch directory and grep or tail it, rather than printing it in
+  full. Write the spec in as few writes as you can, ideally one.
 
 FORMAT
 One document in four parts, each opened by a line `=== <file>`. At the
@@ -459,6 +466,18 @@ RUBRIC (judge intent, not wording)
 
 PROCESS
 Spot-check at least 2 cited paths and 1 acceptance command yourself.
+Ground any one claim with at most 2 paths and 1 command. Run no test
+suite and build nothing: no clone, worktree or prototype of the change.
+Pick an acceptance command that runs no test suite, and run it as the
+spec gives it. A claim you could settle only by running a test suite or
+building the change is a finding for the writer, or a question; say
+what you could not check.
+Turn economy: every turn re-sends everything read so far, so a wasted
+turn or a long printout costs again on every later turn. Put
+independent reads and commands in one turn. Once grep has found the
+lines you need, read that line range, not the whole file. Send long
+output to a file in your scratch directory and grep or tail it, rather
+than printing it in full.
 
 ANTI-GOODHARTING (REVIEWER SIDE)
 - The rubric is a tool for finding real problems. If a spec passes every
diff --git a/docs/principles.md b/docs/principles.md
index c8d4123..1a7f618 100644
--- a/docs/principles.md
+++ b/docs/principles.md
@@ -41,9 +41,11 @@ https://engineering.fb.com/2018/11/21/developer-tools/predictive-test-selection/
 Implemented by: regression checks and gates once per change (#31); `paths:` on a gate command, and
 the gate skips it when the diff touches none of them (#48, `gate_commands` in `instance.yaml`); the
 reviewer's WHAT YOU RUN section and its input, which says the verifier runs the gate commands (#41,
-`factory/prompts/reviewer.md`, `factory/compose.py`).
-Status of #72 part B.2 (reader roles run no suites): done by #41. The code reviewer is the only reader
-role that was given gate commands; the critic and triage never were.
+`factory/prompts/reviewer.md`, `factory/compose.py`); the critic's PROCESS section, which runs no test
+suite and builds nothing (#73, `factory/prompts/critic.md`).
+Status of #72 part B.2 (reader roles run no suites): done by #41 for the code reviewer and by #73 for
+the critic. The code reviewer is the only reader role that was given gate commands; the critic and
+triage never were, but the critic ran suites on its own initiative until #73.
 
 ### 3. Deterministic before judgment.
 
diff --git a/docs/prompts/02-spec-writer.md b/docs/prompts/02-spec-writer.md
index 2d18ff5..e2b097d 100644
--- a/docs/prompts/02-spec-writer.md
+++ b/docs/prompts/02-spec-writer.md
@@ -56,6 +56,13 @@ RULES
 - On revision: respond to each critic finding with FIXED (what changed)
   or DISAGREE (why, with evidence). Don't accept findings you think are
   wrong just to get approved.
+- Turn economy: every turn re-sends everything read so far, so a
+  wasted turn or a long printout costs again on every later turn. Put
+  independent reads and commands in one turn. Once grep has found the
+  lines you need, read that line range, not the whole file. Send long
+  output, such as a suite run or a scenario's output, to a file in your
+  scratch directory and grep or tail it, rather than printing it in
+  full. Write the spec in as few writes as you can, ideally one.
 
 FORMAT
 One document in four parts, each opened by a line `=== <file>`. At the
diff --git a/docs/prompts/03-spec-critic.md b/docs/prompts/03-spec-critic.md
index f9e2ded..d021dc8 100644
--- a/docs/prompts/03-spec-critic.md
+++ b/docs/prompts/03-spec-critic.md
@@ -40,6 +40,18 @@ RUBRIC (judge intent, not wording)
 
 PROCESS
 Spot-check at least 2 cited paths and 1 acceptance command yourself.
+Ground any one claim with at most 2 paths and 1 command. Run no test
+suite and build nothing: no clone, worktree or prototype of the change.
+Pick an acceptance command that runs no test suite, and run it as the
+spec gives it. A claim you could settle only by running a test suite or
+building the change is a finding for the writer, or a question; say
+what you could not check.
+Turn economy: every turn re-sends everything read so far, so a wasted
+turn or a long printout costs again on every later turn. Put
+independent reads and commands in one turn. Once grep has found the
+lines you need, read that line range, not the whole file. Send long
+output to a file in your scratch directory and grep or tail it, rather
+than printing it in full.
 
 ANTI-GOODHARTING (REVIEWER SIDE)
 - The rubric is a tool for finding real problems. If a spec passes every
diff --git a/factory/prompts/critic.md b/factory/prompts/critic.md
index 257d808..e3abc21 100644
--- a/factory/prompts/critic.md
+++ b/factory/prompts/critic.md
@@ -40,6 +40,18 @@ RUBRIC (judge intent, not wording)
 
 PROCESS
 Spot-check at least 2 cited paths and 1 acceptance command yourself.
+Ground any one claim with at most 2 paths and 1 command. Run no test
+suite and build nothing: no clone, worktree or prototype of the change.
+Pick an acceptance command that runs no test suite, and run it as the
+spec gives it. A claim you could settle only by running a test suite or
+building the change is a finding for the writer, or a question; say
+what you could not check.
+Turn economy: every turn re-sends everything read so far, so a wasted
+turn or a long printout costs again on every later turn. Put
+independent reads and commands in one turn. Once grep has found the
+lines you need, read that line range, not the whole file. Send long
+output to a file in your scratch directory and grep or tail it, rather
+than printing it in full.
 
 ANTI-GOODHARTING (REVIEWER SIDE)
 - The rubric is a tool for finding real problems. If a spec passes every
diff --git a/factory/prompts/spec_writer.md b/factory/prompts/spec_writer.md
index c5c26db..c60265a 100644
--- a/factory/prompts/spec_writer.md
+++ b/factory/prompts/spec_writer.md
@@ -56,6 +56,13 @@ RULES
 - On revision: respond to each critic finding with FIXED (what changed)
   or DISAGREE (why, with evidence). Don't accept findings you think are
   wrong just to get approved.
+- Turn economy: every turn re-sends everything read so far, so a
+  wasted turn or a long printout costs again on every later turn. Put
+  independent reads and commands in one turn. Once grep has found the
+  lines you need, read that line range, not the whole file. Send long
+  output, such as a suite run or a scenario's output, to a file in your
+  scratch directory and grep or tail it, rather than printing it in
+  full. Write the spec in as few writes as you can, ideally one.
 
 - Acceptance items describe behaviour (a command a user or operator could run, or
   Given/When/Then) and never name a test function, class, or internal symbol;
