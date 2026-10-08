=== proposal.md
## Problem

Two of the factory's agent roles cost more than they need to, and the operator pays for it on every ticket. The factory turns a request into a spec through a chain of three agents called the **intake workflow**. **Triage** checks the request and decides whether it is a real ticket. The **spec writer** investigates the repository and writes the spec. The **critic** reviews that spec before a human approves it. Each agent works in **turns**: one turn is one model call, which reads files or runs commands and then decides what to do next. Every turn re-sends the agent's fixed start-up context (its role prompt and briefing, about 45k tokens) plus everything it has read so far in the run. A run's cost therefore grows with how many turns it takes and how much output it prints.

The spec writer is the most expensive role. It accounts for about a third of all the context tokens the factory's agents use: a median of 29 turns and 5.3M tokens per run. Its prompt says nothing about economy. It reads whole files where a few lines would do. It prints long command output, such as a full test-suite run, into its context, where that output is re-sent on every later turn. It spreads independent reads across separate turns. The critic is cheaper, but it does work its role should not do. It runs the whole test suite and builds **prototype clones** (disposable copies of the repository with the proposed change applied) to settle questions that are the implementer's job. The project's own principles say the critic only reads and spot-checks, with at most two paths and one command per claim. The critic's prompt sets that as a floor ("at least 2 … and 1"), never as a ceiling.

This change adds rules to the two role prompts only. The spec writer is told to batch independent reads into one turn, read line ranges instead of whole files, keep long output in a scratch file and search it, and write the spec in as few writes as it can. The critic is told the same reading rules, plus three more: run no test suite, build nothing, and spend at most two paths and one command on any one claim. A claim that it could settle only by building becomes a finding or a question. No rubric item, round limit or required spec section changes.

A merge does not change what runs. The **harness** is the code that starts each agent with its prompt and records what it produced. The **runtime** is the pinned checkout of the harness that runs tickets, and only an explicit upgrade moves it. Before that upgrade, the operator replays the intake workflow on a few tickets whose specs were already approved, once with the old prompts and once with the new. The operator then judges whether the writer's turns roughly halved and whether the specs stayed as good.

## Evidence

**Cost by role.** These figures come from request #73 (2026-10-07). Triage re-derived them from this session's workflow transcripts, the saved record of every model call each workflow run made. It used `factory/cost.py`'s role detection and counted each message once. I did not re-derive them. Triage's script printed:

```
spec_writer runs 58 median_calls 29.0 p90 71 ctxM 309 share 33 perrunM 5.3
critic runs 54 median_calls 8.5 p90 11 ctxM 42 share 5 perrunM 0.8
```

Read the first line as: 58 spec writer runs took a median of 29 turns each, and the slowest tenth took 71 or more. Their context tokens, summed over every turn, came to 309M, which is 33% of all the agents' context tokens, or 5.3M per run. The critic's 54 runs took a median of 8.5 turns and 42M tokens in all, 5% of the total and 0.8M per run.

The request breaks down the tool output the writer carries into later turns. 53% is output of `grep`, `sed`, `cat` and `git`. 37% comes from reading whole files, at 6.4k tokens per read on average. 8% comes from suite runs. Triage's counts of suite runs and clones depend on how a suite run is counted: 121 or 76 suite runs for the writer and 59 or 15 for the critic, with 53 and 15 clones. By every method, the critic runs suites and builds clones today.

**The critic's prompt sets a floor, not a cap.** The same line appears in all three copies of the critic prompt and nowhere else in its process:

```
$ grep -rn 'Spot-check' docs/design.md docs/prompts factory/prompts
docs/design.md:461:Spot-check at least 2 cited paths and 1 acceptance command yourself.
docs/prompts/03-spec-critic.md:42:Spot-check at least 2 cited paths and 1 acceptance command yourself.
factory/prompts/critic.md:42:Spot-check at least 2 cited paths and 1 acceptance command yourself.
```

The three copies are the design doc's block, its documented copy and the copy the harness actually sends. Each sets a minimum and no maximum.

`docs/principles.md` already describes the bound the prompt lacks. Principle 2 (lines 31–46) says "a role that only reads does not run suites". The Spiking section (lines 167–176) says the critic's grounding is bounded at "two paths, one command" and ends "The critic reads and spot-checks; it does not build." Principle 2's status line (lines 45–46) marks "reader roles run no suites" done by #41, though #41 changed only the code reviewer.

**Neither prompt has an economy rule today.** The first scenario below, run on `main` at `2e73dbb`, prints:

```
spec_writer copy=SAME doc=0/4 run=0/4 fill=unchanged
critic copy=SAME doc=0/6 run=0/6 fill=unchanged
```

`copy=SAME` means the design doc's prompt block equals its `docs/prompts/` copy. `doc=0/4` means none of the four writer rules is present. The rule about the scratch directory exists only in the shared preamble, the text every role receives first (`factory/prompts/preamble.md:54-60`). That rule says where files go, not to keep long output there.

**Prototype.** In this run I applied parts A–D to a clone of `main` at `2e73dbb` in this run's scratch directory, with the exact text given in design.md, and committed it on a branch. Every scenario below printed its THEN line there. The harness suite printed `364 passed in 221.77s`: nothing the change touches is pinned by a test. I ran it under a fresh HOME with `TMPDIR` under `/tmp`. On `main`, the NEW scenarios print the failures recorded in verification.md, and the REGRESSION scenarios print their THEN lines.

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

## Responses

- [BLOCKING] 6, unglossed terms in Evidence ¶1, Operator steps ¶1 and Problem ¶3 → FIXED. Problem ¶1 now names the intake workflow and glosses triage, the spec writer and the critic as its three agents. A new Problem ¶4 glosses the harness and the runtime, and says the replay runs before the runtime moves. Evidence ¶1 glosses the workflow transcripts. Operator steps 1 glosses the store and a throwaway store. Under rule 5, the quoted cost lines are now followed by a reading of every field (runs, median and p90 turns, total context tokens, share of the total, tokens per run). The Problem and Operator steps now say "turns" throughout, the name the Problem gives a model call, where v1 also said "agent calls".
- [SHOULD-FIX] 1, D.1 numbered the last entry 58 → FIXED. D.1 now says the last entry on `main` is 57 and the new entry is 58 (`grep -n '^[0-9]*\. ' docs/changelog.md | tail -1` prints line 61, `57. After issue #41 …`).
- [NIT] 2, the entry on one line → FIXED. D.1 now says to write the entry on one line, as every existing entry is. The prototype's entry is one line, and the changelog scenario printed `5` on it.

No scenario, part or decision changed in this round. I rebuilt the prototype in this run's scratch directory and re-ran all five scenarios on it and on `main`. Each printed what verification.md states. The suite printed `364 passed`.

## Out-of-scope observations

- `agents/factory-spec-critic.md` and `agents/factory-spec-writer.md` repeat old copies of their prompts, including the critic's `Spot-check at least 2 …` line (`agents/factory-spec-critic.md:28`). Inline runs never see them. T-0030 part A.3 replaces those bodies with a pointer to the run's `system-prompt.txt`, which removes the drift.
- The briefing every role receives (`.factory/context.md`, line 14) tells the reader how to run the harness suite, and the composed "Running code" section says to wrap "every test or check command the briefing above gives". A critic could read both as an invitation to run the suite. The new PROCESS lines override that for the critic. If the replay shows critics still running the suite, the briefing is the next place to look. It is infra (`.factory/**`), outside this ticket.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high, every scenario was re-run this round on a rebuilt prototype and on `main` at `2e73dbb` and printed what is stated, and the suite passed on the prototype; the turn savings themselves are judged only by the operator's replay
ESCALATIONS: none
