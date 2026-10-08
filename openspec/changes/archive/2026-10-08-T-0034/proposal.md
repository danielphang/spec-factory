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

