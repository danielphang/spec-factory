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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0335-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0335-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0335-reviewer/wt` (branch `factory/T-0035.1`, base `49ea4c7646475a00adee963e1e806302a3eed18c`, head `9a87c3e3983a8dd04c7e21f9dd6fdfe99dfe5a41`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0035.1

T-0035.1 / Revert #73's critic limits: drop the per-claim cap and the no-build rule; keep the no-suite line and the reading rules
Depends on: none
Parallel-safe: yes

Parent: T-0035, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules
- A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban
- The writer prompt is as #73 left it, and only the critic's PROCESS changes
- Principle 2 names the critic's no-suite rule and no longer its build ban
- The changelog records the revert as its last entry
- The Spiking section allows a small scratch check and records the replay
- The critic revert adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0035/v2.md`

=== proposal.md
## Problem

The factory runs each ticket through a chain of AI agents, each with its own prompt (its "role"). Two of them shape a spec before a human approves it: the **spec writer**, which turns an accepted ticket into a spec, and the **critic**, which reviews that spec against a rubric and either approves it, sends it back once, or escalates to the human.

Issue #73 (merged as `05cf8f9`) gave both roles rules meant to save tokens. The critic got four: a per-claim cap (settle any one claim with at most two file paths and one command), a no-build rule (no clone, worktree or prototype of the change), a no-test-suite rule, and three reading rules (batch independent reads, read only the line range grep found, send long output to a file). On 2026-10-08 the operator replayed three past intakes, tickets the factory had already taken from request to approved spec, with the old and new prompts. The writer's rules cut its tokens by about 37% at the same quality, and the operator accepted them. The critic's rules saved no tokens. They also made it check less, and it missed a real defect on two of the three tickets. One of those defects the old prompt had confirmed with a small experiment in a throwaway git repository, which the no-build rule now forbids.

So the critic as it stands on `main` is a worse reviewer at no saving. The operator decided to take out the per-claim cap and the no-build rule, keep the no-test-suite rule and the reading rules, and leave the writer's rules alone. The runtime, the pinned copy of the harness that actually runs tickets, has not yet picked up #73. It is meant to pick up #73's writer rules and this revert together, so that no live critic runs under the rules the operator rejected.

## Root cause

The critic's PROCESS section in `docs/design.md` (the "## 3. Spec critic" block, lines 467-474), `docs/prompts/03-spec-critic.md:42-47` and `factory/prompts/critic.md:42-47` carries the per-claim cap and the no-build sentence #73 added. `docs/principles.md` principle 2 (lines 44-45) and the Spiking section (heading at line 169, paragraph at lines 171-178) describe those rules as the critic's design. Per the replay, the critic's cost is mostly its fixed start-up context, so capping its checks did not lower its cost; it lowered what it found.

## Out of scope

- The spec writer prompt, in all three copies: it stays exactly as #73 left it.
- The critic's rubric, round limit, output format, its minimum spot-check (2 cited paths, 1 acceptance command), its no-test-suite rule, its acceptance-command rule and its three reading rules.
- Any other prompt, `agents/`, the shared preamble, `README.md` (it names none of the removed rules) and `dev/build-harness.spec.md` (likewise).
- `dev/issues.md`'s index row for #74: the operator's own `dev:` commits maintain it.
- Moving the runtime to the merged revision: an operator step after merge, not this change.
- Re-running the replay: an operator step, not acceptance.

## Open questions

none

## Decisions

- This change overturns part of a standing decision, one that later tickets must keep, recorded on 2026-10-08 for T-0034, the ticket that applied #73: "The critic runs no test suite and builds nothing ... Standing: a later change to the critic prompt keeps this rule". The no-test-suite half stands. The no-build half and the per-claim cap (T-0034's other 2026-10-08 decision) are removed. Authority: the operator's choice in `.factory/answers/T-0034-acceptance-2026-10-08.md`. Standing: later changes to the critic prompt keep the no-suite rule and do not re-add a per-claim cap or a no-build rule without new evidence.
- The critic prompt gains one sentence that allows a small experiment in its scratch directory to confirm a finding. Without it, the kept sentence "A claim you could settle only by ... building the change is a finding" reads as the old ban. The kept sentence still covers building or trying out the change itself, which the request's item C (its `docs/principles.md` change) leaves to the writer or to a spike, a ticket built only to test whether an approach works. Rejected: deleting the kept sentence. The triage role, which sorts a request before the spec writer sees it, asked to keep it, and it still tells the critic what to do with a claim it cannot check.
- The no-suite line gains its reason, "the implementer and the verifier run it", as the request's item B (its list of what the critic keeps) gives. `Pick an acceptance command that runs no test suite, and run it as the spec gives it.` and the Turn economy paragraph stay word for word.
- The Spiking section records the replay result, as the request's item C asks ("Record the replay result"). The changelog entry records it too.
- Of the current-truth requirements that #73 added, four are restated (MODIFIED), because each states the rule being removed or forbids removing a critic line. Other current-truth requirements that check the diff of their own change (for example "The documents record the live-store guard", which expects no prompt copy to change) are left as they are, as #73 left them. Their scenarios describe their own change, not standing behaviour.
- "Writer unchanged from #73" is checked as no difference from `05cf8f9` in either writer prompt file, plus the writer's design block equal to its `docs/prompts/` copy. Together these mean the design block is unchanged too.

## Risk

- Blast radius: every critic run after the operator moves the runtime. The critic may spend more turns per review, for example on a scratch experiment. The replay shows the version with no cap and no build ban at about the same token cost. No routing, store, CLI or workflow code changes.
- Protected paths this change touches:
  - `factory/prompts/critic.md` (harness)
  - `docs/prompts/03-spec-critic.md` (generated; re-copied from the design doc block, never edited apart from it)
- Not protected, also changed: `docs/design.md`, `docs/principles.md`, `docs/changelog.md`.

## Operator steps

1. After merge, move the runtime to a revision that holds both `05cf8f9` (#73) and this change, and accept it with `--accept-harness`, as the request's "Then" line says.
2. Optional: re-run the critic replay on #51 and #57 with the merged critic prompt, to confirm it finds the `UV_PYTHON_INSTALL_DIR` risk and the brace-list declaration bug again. The result belongs in the acceptance record, not in this ticket's checks.
3. Update `dev/issues.md`'s #74 row once merged.

=== design.md
## Proposed change

**A. Critic PROCESS, in all three copies.** In the "## 3. Spec critic" block of `docs/design.md`, then `docs/prompts/03-spec-critic.md` (re-copied from that block), then `factory/prompts/critic.md`, replace the seven lines from `Spot-check at least 2 cited paths ...` through `what you could not check.` with:

```
Spot-check at least 2 cited paths and 1 acceptance command yourself.
Run no test suite: the implementer and the verifier run it. Pick an
acceptance command that runs no test suite, and run it as the spec
gives it. To confirm a finding you may run a small experiment in your
scratch directory, such as a few git commands in a throwaway
repository. A claim you could settle only by running a test suite or
building the change is a finding for the writer, or a question; say
what you could not check.
```

The `Turn economy:` paragraph that follows stays byte for byte. Nothing else in the critic prompt changes. The run copy's one existing difference from the documented copy (`round 2` against `round {2}`) stays.

**B. `docs/principles.md`, principle 2.** Change "the critic's PROCESS section, which runs no test suite and builds nothing (#73, `factory/prompts/critic.md`)." to "the critic's PROCESS section, which runs no test suite (#73, kept by #74, `factory/prompts/critic.md`)." The status line ("done by #41 for the code reviewer and by #73 for the critic ...") stays.

**C. `docs/principles.md`, Spiking section.** Replace its paragraph with:

```
Grounding a claim the spec makes, for example that a path exists or that an acceptance command fails
on the base, is the critic's job. Its prompt sets a floor, two cited paths and one acceptance command,
and no ceiling. To confirm a finding, the critic may run a small scratch check, such as a few git
commands in a throwaway repository; it runs no test suite (principle 2). Vetting whether a whole
approach works is implementation. A critic that builds the change duplicates work the implementer
redoes, in a disposable checkout, and the result survives only as a sentence in a finding. Principle 1
is the reason: a critic's trial of an approach is self-repair's weak signal, and an implementer's is
execution feedback. So vetting a whole approach belongs to the spec writer during investigation, with
its output in Evidence, or to a spike ticket on #64's spike path, run by an implementer and recorded
as a decision. #73 capped the critic at two paths and one command for any one claim and forbade any
build. The replay that accepted #73, three past intakes (#49, #51, #57) with the same inputs, found
that the critic then used about the same tokens (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M),
checked less, and missed a real finding on two of the three, one of which the earlier prompt had
confirmed with a scratch git test. #74 removed the cap and the no-build rule and kept the no-suite
rule.
```

**D. `docs/changelog.md`.** Insert entry 59 directly after entry 58, so it is the last numbered entry (the `Declined:` line stays after it), one line:

```
59. After issue #74 (2026-10-08), where the operator's replay of three past intakes (#49, #51, #57), with the same inputs and bases, found that #73's spec writer rules cut its tokens by about 37% at the same quality, but that its critic rules saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less: it missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk on #51 and, on #57, the brace-list declaration bug that the earlier prompt had confirmed with a scratch git test. The critic's PROCESS drops the per-claim cap (at most two paths and one command for any one claim) and the no-build rule (no clone, worktree or prototype), and says the critic may run a small experiment in its scratch directory to confirm a finding. It keeps its minimum spot-check, the rule that it runs no test suite, the rule for picking an acceptance command, the rule that a claim needing a suite run or a build of the change is a finding or a question, and the three reading rules. `docs/principles.md` principle 2 keeps the critic's no-suite rule, and its Spiking section drops the two-path bound and says that vetting a whole approach is still the spec writer's or a spike's job. The spec writer prompt is unchanged from #73.
```

Size: 31 added and 20 removed lines across five files (prototype `git diff --stat main...HEAD`).

## Tests to change

none. No test under `tests/factory/` names the removed phrases (`git grep`, Evidence). The two tests that compare design blocks with their `docs/prompts/` copies pass on the prototype (`10 passed`), because the three copies change together.

=== specs/harness-docs/spec.md
## MODIFIED Requirements

### Requirement: The spec writer and the critic carry the turn-economy rules
Every copy of the spec writer prompt SHALL tell it to batch independent reads and commands, read line ranges once grep has found them, keep long output in a scratch file, and write the spec in as few writes as it can. Every copy of the critic prompt SHALL carry the same reading rules, its minimum spot-check, a rule that it runs no test suite, the rule for picking an acceptance command, a sentence allowing a small experiment in its scratch directory to confirm a finding, and the rule that turns a claim needing a suite run or a build of the change into a finding or a question; it MUST NOT cap a claim at a number of paths and commands or forbid a clone, worktree or prototype. Each design block MUST stay byte-identical to its `docs/prompts/` copy, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); printf '%s\n' 'Put independent reads and commands in one turn' 'read that line range, not the whole file' 'to a file in your scratch directory and grep or tail it' > $T/both; { cat $T/both; echo 'Write the spec in as few writes as you can'; } > $T/spec_writer; { cat $T/both; printf '%s\n' 'Spot-check at least 2 cited paths and 1 acceptance command yourself' 'Run no test suite' 'Pick an acceptance command that runs no test suite' 'small experiment in your scratch directory' 'is a finding for the writer, or a question'; } > $T/critic; printf '%s\n' 'Ground any one claim' 'build nothing' 'no clone, worktree or prototype' > $T/gone; for r in "2. Spec writer|02-spec-writer.md|spec_writer" "3. Spec critic|03-spec-critic.md|critic"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) gone=$(for g in docs/prompts/$c factory/prompts/$f.md; do tr '\n' ' ' < $g | tr -s ' ' | grep -oF -f $T/gone; done | grep -c .) fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged`, then `critic copy=SAME doc=8/8 run=8/8 gone=0 fill=unchanged`. `doc` and `run` count the kept or added phrases found in the documented copy and the run copy, each joined into one line so a phrase may wrap; `gone` counts the removed phrases found in either.

### Requirement: Spec writer and critic runs receive the turn-economy rules
The system prompt that `run start` writes for a spec writer run SHALL contain the writer's turn-economy rule. The one it writes for a critic run SHALL contain the critic's reading rules, its no-suite rule and the sentence allowing a small scratch experiment, and MUST NOT contain the per-claim cap or the no-build rule.

#### Scenario: A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0002 status=ready-for-critic >/dev/null; bin/factory run start --role spec_writer --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role critic --ticket T-0002 >/dev/null 2>&1; W=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0001-spec_writer/system-prompt.txt | tr -s ' '); C=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0002-critic/system-prompt.txt | tr -s ' '); echo "spec_writer batch=$(printf "%s" "$W" | grep -c 'Put independent reads and commands in one turn') writes=$(printf "%s" "$W" | grep -c 'Write the spec in as few writes as you can')"; echo "critic batch=$(printf "%s" "$C" | grep -c 'Put independent reads and commands in one turn') suite=$(printf "%s" "$C" | grep -c 'Run no test suite') scratch=$(printf "%s" "$C" | grep -c 'small experiment in your scratch directory') cap=$(printf "%s" "$C" | grep -c 'Ground any one claim') build=$(printf "%s" "$C" | grep -c 'build nothing')")`
- THEN it prints exactly `spec_writer batch=1 writes=1`, then `critic batch=1 suite=1 scratch=1 cap=0 build=0`

### Requirement: Nothing else in the two prompts changes
The spec writer prompt copies SHALL stay as #73 left them at `05cf8f9`. In the critic prompt copies, everything before the PROCESS section and everything from ANTI-GOODHARTING on SHALL stay byte for byte as on `main`. No other file under `docs/prompts/`, `factory/prompts/` or `agents/` SHALL change.

#### Scenario: The writer prompt is as #73 left it, and only the critic's PROCESS changes
- WHEN `(T=$(mktemp -d); n=0; for x in "docs/prompts/03-spec-critic.md|1,/^PROCESS\$/p" "docs/prompts/03-spec-critic.md|/^ANTI-GOODHARTING/,\$p" "factory/prompts/critic.md|1,/^PROCESS\$/p" "factory/prompts/critic.md|/^ANTI-GOODHARTING/,\$p"; do f=${x%%|*}; s=${x#*|}; git show main:$f | sed -n "$s" > $T/a; sed -n "$s" $f > $T/b; [ -s $T/a ] || n=$((n+100)); cmp -s $T/a $T/b || { n=$((n+1)); echo "changed: $f $s"; }; done; echo "sections_changed=$n writer=$(git diff --name-only 05cf8f9 HEAD -- docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md | grep -c .) others=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts agents | grep -vxF -e docs/prompts/03-spec-critic.md -e factory/prompts/critic.md | grep -c .)")`
- THEN it prints only `sections_changed=0 writer=0 others=0`

### Requirement: The documents record the turn-economy change
`docs/changelog.md` SHALL hold one entry for issue #73, numbered without a gap. `docs/principles.md` principle 2 SHALL name the critic's no-suite rule among its mechanisms, SHALL no longer say the critic builds nothing, and SHALL say part B.2 is done by #41 for the code reviewer and by #73 for the critic.

#### Scenario: Principle 2 names the critic's no-suite rule and no longer its build ban
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; P=$(sed -n '/^### 2\. /,/^### 3\. /p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "entries73=$(grep -c '^[0-9]*\. After issue #73 ' docs/changelog.md) implemented=$(printf '%s' "$P" | grep -c 'runs no test suite (#73') builds=$(printf '%s' "$P" | grep -c 'builds nothing') status=$(printf '%s' "$P" | grep -c 'done by #41 for the code reviewer and by #73 for the critic')")`
- THEN it prints exactly `CONTIGUOUS`, then `entries73=1 implemented=1 builds=0 status=1`

## ADDED Requirements

### Requirement: The documents record the critic revert
`docs/changelog.md` SHALL gain one entry for issue #74 as its last numbered entry, numbered without a gap, that records the replay result and the two removed rules. The Spiking section of `docs/principles.md` SHALL no longer bound the critic to two paths and one command or say it does not build, SHALL say the critic may run a small scratch check, SHALL say vetting a whole approach belongs to the spec writer or a spike, and SHALL record the replay. The change MUST add no whitespace errors.

#### Scenario: The changelog records the revert as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e '#74' -e replay -e 'per-claim cap' -e 'no-build rule' -e 'no test suite' -e UV_PYTHON_INSTALL_DIR -e brace-list | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `7`

#### Scenario: The Spiking section allows a small scratch check and records the replay
- WHEN `(X=$(sed -n '/^## Spiking/,$p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "bound=$(printf '%s' "$X" | grep -c 'two paths, one command') nobuild=$(printf '%s' "$X" | grep -c 'it does not build') scratch=$(printf '%s' "$X" | grep -c 'small scratch check') whole=$(printf '%s' "$X" | grep -c 'vetting a whole approach belongs to the spec writer') replay=$(printf '%s' "$X" | grep -c 'replay')")`
- THEN it prints exactly `bound=0 nobuild=0 scratch=1 whole=1 replay=1`

#### Scenario: The critic revert adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Base outputs below are from `~/dev/spec-factory` at `49ea4c7` (`main`), each command run under a throwaway HOME in this round. On the prototype (`scratch/proto` in this run's directory, built by `scratch/edit.py` from `49ea4c7`, with the round 2 wording) each scenario printed its THEN line exactly.

- Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules → NEW. Today the second line is `critic copy=SAME doc=7/8 run=7/8 gone=6 fill=unchanged`: the scratch-experiment phrase is missing, and the three removed phrases are found in both files. The writer line already matches; that half is a regression guard.
- A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban → NEW. Today the second line is `critic batch=1 suite=1 scratch=0 cap=1 build=1`.
- The writer prompt is as #73 left it, and only the critic's PROCESS changes → REGRESSION. Today it prints `sections_changed=0 writer=0 others=0`. It must still do so after the change.
- Principle 2 names the critic's no-suite rule and no longer its build ban → NEW. Today it prints `CONTIGUOUS`, then `entries73=1 implemented=0 builds=1 status=1`.
- The changelog records the revert as its last entry → NEW. Today it prints `CONTIGUOUS`, then `1`: entry 58 contains only `no test suite`.
- The Spiking section allows a small scratch check and records the replay → NEW. Today it prints `bound=1 nobuild=1 scratch=0 whole=0 replay=0`.
- The critic revert adds no whitespace errors → REGRESSION. Today it prints `exit=0`, because the diff is empty.

## PR description (the implementer's output)

Sub-ticket: T-0035.1 (parent T-0035, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0035/v2.md`). Branch `factory/T-0035.1`, head `9a87c3e`, base `49ea4c7`.

## What changed

This change takes two of issue #73's limits back out of the critic. The critic is the agent that reviews a spec against a rubric before a human approves it. The two limits are the per-claim cap (at most two file paths and one command to settle any one claim) and the no-build rule (no clone, worktree or prototype). The operator's replay of three past intakes found that these limits saved no tokens and caused the critic to miss real defects. The critic keeps its minimum spot-check, its no-test-suite rule and its reading rules. The spec writer prompt does not change.

- **A. Critic PROCESS, all three copies.** In `docs/design.md` (the "## 3. Spec critic" block), `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md`, I replaced the seven lines from `Spot-check at least 2 cited paths ...` through `what you could not check.` with the spec's eight lines, word for word. The `Turn economy:` paragraph after them did not change. The run copy's existing `round 2` / `round {2}` difference also stayed, as the s1 output `fill=unchanged` shows. I applied the same replacement to all three files with one script (`scratch/edit_a.py`), and the script asserted that each file held the old text exactly once.
- **B. `docs/principles.md` principle 2.** "which runs no test suite and builds nothing (#73, ..." is now "which runs no test suite (#73, kept by #74, ...". The status line did not change.
- **C. `docs/principles.md` Spiking section.** I replaced its paragraph, which ran to the end of the file, with the spec's text word for word.
- **D. `docs/changelog.md`.** Entry 59 now follows entry 58, word for word from the spec. The `Declined:` line still comes after it.

Size: `git diff --stat main...HEAD` prints `5 files changed, 31 insertions(+), 20 deletions(-)`. This matches the size the spec gives for its prototype.

## Acceptance results

I ran every command from the worktree with bash, under a throwaway HOME. Each scenario's WHEN text was copied out of the input file with sed.

| Scenario | Kind | Before (base `49ea4c7`) | After (`9a87c3e`) |
|---|---|---|---|
| Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules | NEW | `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged` / `critic copy=SAME doc=7/8 run=7/8 gone=6 fill=unchanged` | `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged` / `critic copy=SAME doc=8/8 run=8/8 gone=0 fill=unchanged` |
| A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban | NEW | `spec_writer batch=1 writes=1` / `critic batch=1 suite=1 scratch=0 cap=1 build=1` | `spec_writer batch=1 writes=1` / `critic batch=1 suite=1 scratch=1 cap=0 build=0` |
| The writer prompt is as #73 left it, and only the critic's PROCESS changes | REGRESSION | `sections_changed=0 writer=0 others=0` | `sections_changed=0 writer=0 others=0` |
| Principle 2 names the critic's no-suite rule and no longer its build ban | NEW | `CONTIGUOUS` / `entries73=1 implemented=0 builds=1 status=1` | `CONTIGUOUS` / `entries73=1 implemented=1 builds=0 status=1` |
| The changelog records the revert as its last entry | NEW | `CONTIGUOUS` / `1` | `CONTIGUOUS` / `7` |
| The Spiking section allows a small scratch check and records the replay | NEW | `bound=1 nobuild=1 scratch=0 whole=0 replay=0` | `bound=0 nobuild=0 scratch=1 whole=1 replay=1` |
| The critic revert adds no whitespace errors | REGRESSION | `exit=0` | `exit=0` |

What the results mean:

- Before the change, every NEW command failed exactly as `verification.md` says it would.
- After the change, every command prints its THEN line exactly.
- In the first scenario, `copy=SAME` means each design block is byte-identical to its `docs/prompts/` copy. `gone=0` means none of the removed phrases is left in either the documented copy or the run copy.
- In the second scenario, `run start` is the harness command that writes a run's prompt, and the critic prompt it writes now has the scratch allowance and neither removed rule.

Gate commands, run from the worktree exactly as written:
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `364 passed in 225.62s (0:03:45)` and exited 0.

I checked that the removed phrases are gone everywhere except the changelog. `git grep -nE "build nothing|Ground any one claim|no clone, worktree|two paths, one command|at most 2 paths" -- . ':!docs/changelog.md'` found no match (exit 1). This confirms the spec's claim that `README.md` and `dev/build-harness.spec.md` do not name the removed rules.

## Tests added/changed

None.
- The spec lists no tests to change, and I changed no existing test file.
- I added no new test file. The acceptance scenarios already check the changed behaviour, which is prompt and document text. The two existing tests that compare each design block with its `docs/prompts/` copy pass, inside the 364 above.

## Known gaps and uncertainties

- `factory:` markers added: none. This change touches no code.
- I did not re-run the operator's critic replay on #51 and #57. The spec makes that an optional operator step after merge, not an acceptance check, so whether the reverted critic finds those two defects again is unverified.
- The live runtime (the pinned checkout of the harness that actually runs tickets) is unchanged until the operator moves it. Until then, live critic runs use the runtime's own prompt. That prompt predates #73.

## Out-of-scope observations

- The worktree has no `AGENTS.md`. Step 1 of my process says to read it, so I worked from the briefing in the run input instead.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The change is a word-for-word text replacement from the spec. All seven acceptance commands print their THEN lines, both gates pass, and I ran each command myself on head `9a87c3e`.
ESCALATIONS: none. The change touches two protected paths, `factory/prompts/critic.md` (harness) and `docs/prompts/03-spec-critic.md` (generated; re-copied from the design block). The spec's Risk section declares both.

## Diff `49ea4c7646475a00adee963e1e806302a3eed18c...9a87c3e3983a8dd04c7e21f9dd6fdfe99dfe5a41`

diff --git a/docs/changelog.md b/docs/changelog.md
index 6c6a5b7..3d1474f 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -60,5 +60,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 56. After issue #48 (2026-10-04), where every approved spec paid for a planner run and every sub-ticket for every gate command, though nine of the thirteen specs planned so far got exactly one sub-ticket, each after a 72 to 302 second planner run that restated it: the small-change lane. A spec that needs one sub-ticket skips the planner. At `ready-for-planner` the build first runs `factory plan whole-spec`, which creates `<parent>.1` from the whole spec, ready for its implementer, naming every scenario of the spec, and logs `plan.skipped`, when the parent has no sub-ticket and no earlier planner run, its latest spec-writer run did not end NEEDS-SPLIT, and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that names seams. Otherwise it reports that the planner is needed, writes nothing, and the planner runs as before; it refuses a parent that is not ready for its planner, has a run in flight or has no approved spec, and the build parks that refusal as a harness bug. To force the planner on such a spec, the operator adds a `### Size and seams` heading at the gate. A gate command may also declare `paths`, as git pathspecs. When a reviewer or verifier run starts on a sub-ticket, the harness marks SKIPPED, with the reason, each command whose paths the sub-ticket's diff touches none of, lists it apart from the commands to run, and records it in the run's `meta.yaml` and on the `ci` row, whose PASS or FAIL still comes from the commands that ran. The implementer and the parent-close verifier still get every command, and a malformed entry refuses every build role's run start. This overturns the cut of the path-scoped skip in T-0016's spec; no repository's gate configuration changes. Rejected: the request's trigger of exactly one lettered part, which would have skipped none of the nine.
 57. After issue #41 (2026-10-04), where a code reviewer started the full test suite in the background, ended its turn to wait for it, and so wrote no review, three times in one day, each time on a commit the verifier had already passed; the harness recorded each run as KILLED and parked the ticket as a budget kill, though it enforces no budget and the agent call reports no reason a run stopped. A role run that ends without writing its output is now EMPTY-OUTPUT in `run finish`, never a budget kill, and the workflow keeps the agent's last message with the run (`factory run last-message`). The same role is re-dispatched once, on the same inputs and in the same round; a second EMPTY-OUTPUT in a row parks the ticket as `EMPTY-OUTPUT from <role>` with both runs, and records no result row for that run, so `resolve --redispatch` re-runs only that checker. A thrown agent call keeps its KILLED record and its `agent call failed` park. The shared preamble gains one RUNNING CODE bullet: run every command in the foreground and never end the turn while one is still running. The code reviewer prompt gains a WHAT YOU RUN section: judge the diff by reading it and leave the test suite and the gate commands to the verifier, which runs them on the same head; a narrow command that confirms one finding is allowed. The reviewer's input no longer lists the gate commands; it says the verifier runs them. The routing table gains two EMPTY-OUTPUT rows. Rejected: keeping a budget-kill label for some empty outputs, and a retry counter in the store.
 58. After issue #73 (2026-10-07), where the spec writer took a third of all workflow context tokens (309M of 866M; a median of 29 agent calls and 5.3M tokens per run), because every call re-sends the start-up context and everything read so far, and where the critic ran the test suite and built prototype clones of the change on its own initiative, though its grounding is meant to stay within two paths and one command per claim. The spec writer prompt gains a RULES bullet, Turn economy: put independent reads and commands in one turn, read a line range once grep has found it, send long output to a file in the run's scratch directory and grep or tail it, and write the spec in as few writes as possible. The critic's PROCESS keeps its minimum spot-check and caps any one claim at two paths and one command; it runs no test suite and builds nothing, and a claim it could settle only by building becomes a finding for the writer or a question. It gains the same reading rules. No rubric item, round limit or required spec section changes, and the shared preamble does not change. Rejected: a shared preamble line, which would reach every role.
+59. After issue #74 (2026-10-08), where the operator's replay of three past intakes (#49, #51, #57), with the same inputs and bases, found that #73's spec writer rules cut its tokens by about 37% at the same quality, but that its critic rules saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less: it missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk on #51 and, on #57, the brace-list declaration bug that the earlier prompt had confirmed with a scratch git test. The critic's PROCESS drops the per-claim cap (at most two paths and one command for any one claim) and the no-build rule (no clone, worktree or prototype), and says the critic may run a small experiment in its scratch directory to confirm a finding. It keeps its minimum spot-check, the rule that it runs no test suite, the rule for picking an acceptance command, the rule that a claim needing a suite run or a build of the change is a finding or a question, and the three reading rules. `docs/principles.md` principle 2 keeps the critic's no-suite rule, and its Spiking section drops the two-path bound and says that vetting a whole approach is still the spec writer's or a spike's job. The spec writer prompt is unchanged from #73.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 6e862ab..40c079c 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -466,10 +466,11 @@ RUBRIC (judge intent, not wording)
 
 PROCESS
 Spot-check at least 2 cited paths and 1 acceptance command yourself.
-Ground any one claim with at most 2 paths and 1 command. Run no test
-suite and build nothing: no clone, worktree or prototype of the change.
-Pick an acceptance command that runs no test suite, and run it as the
-spec gives it. A claim you could settle only by running a test suite or
+Run no test suite: the implementer and the verifier run it. Pick an
+acceptance command that runs no test suite, and run it as the spec
+gives it. To confirm a finding you may run a small experiment in your
+scratch directory, such as a few git commands in a throwaway
+repository. A claim you could settle only by running a test suite or
 building the change is a finding for the writer, or a question; say
 what you could not check.
 Turn economy: every turn re-sends everything read so far, so a wasted
diff --git a/docs/principles.md b/docs/principles.md
index 1a7f618..5fd43db 100644
--- a/docs/principles.md
+++ b/docs/principles.md
@@ -42,7 +42,7 @@ Implemented by: regression checks and gates once per change (#31); `paths:` on a
 the gate skips it when the diff touches none of them (#48, `gate_commands` in `instance.yaml`); the
 reviewer's WHAT YOU RUN section and its input, which says the verifier runs the gate commands (#41,
 `factory/prompts/reviewer.md`, `factory/compose.py`); the critic's PROCESS section, which runs no test
-suite and builds nothing (#73, `factory/prompts/critic.md`).
+suite (#73, kept by #74, `factory/prompts/critic.md`).
 Status of #72 part B.2 (reader roles run no suites): done by #41 for the code reviewer and by #73 for
 the critic. The code reviewer is the only reader role that was given gate commands; the critic and
 triage never were, but the critic ran suites on its own initiative until #73.
@@ -169,10 +169,17 @@ then parked, with the agent's last message kept (#41, `factory/cli.py`, both wor
 ## Spiking: who vets an approach
 
 Grounding a claim the spec makes, for example that a path exists or that an acceptance command fails
-on the base, is the critic's job, and its rubric bounds it: two paths, one command. Vetting whether an
-approach works is implementation. A critic that builds duplicates work the implementer redoes, in a
-disposable checkout, and the result survives only as a sentence in a finding. Principle 1 is the
-reason: a critic's trial is self-repair's weak signal, and an implementer's is execution feedback.
-So empirical vetting belongs to the spec writer during investigation, with its output in Evidence, or
-to a spike ticket on #64's spike path, run by an implementer and recorded as a decision. The critic
-reads and spot-checks; it does not build.
+on the base, is the critic's job. Its prompt sets a floor, two cited paths and one acceptance command,
+and no ceiling. To confirm a finding, the critic may run a small scratch check, such as a few git
+commands in a throwaway repository; it runs no test suite (principle 2). Vetting whether a whole
+approach works is implementation. A critic that builds the change duplicates work the implementer
+redoes, in a disposable checkout, and the result survives only as a sentence in a finding. Principle 1
+is the reason: a critic's trial of an approach is self-repair's weak signal, and an implementer's is
+execution feedback. So vetting a whole approach belongs to the spec writer during investigation, with
+its output in Evidence, or to a spike ticket on #64's spike path, run by an implementer and recorded
+as a decision. #73 capped the critic at two paths and one command for any one claim and forbade any
+build. The replay that accepted #73, three past intakes (#49, #51, #57) with the same inputs, found
+that the critic then used about the same tokens (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M),
+checked less, and missed a real finding on two of the three, one of which the earlier prompt had
+confirmed with a scratch git test. #74 removed the cap and the no-build rule and kept the no-suite
+rule.
diff --git a/docs/prompts/03-spec-critic.md b/docs/prompts/03-spec-critic.md
index d021dc8..6c3f745 100644
--- a/docs/prompts/03-spec-critic.md
+++ b/docs/prompts/03-spec-critic.md
@@ -40,10 +40,11 @@ RUBRIC (judge intent, not wording)
 
 PROCESS
 Spot-check at least 2 cited paths and 1 acceptance command yourself.
-Ground any one claim with at most 2 paths and 1 command. Run no test
-suite and build nothing: no clone, worktree or prototype of the change.
-Pick an acceptance command that runs no test suite, and run it as the
-spec gives it. A claim you could settle only by running a test suite or
+Run no test suite: the implementer and the verifier run it. Pick an
+acceptance command that runs no test suite, and run it as the spec
+gives it. To confirm a finding you may run a small experiment in your
+scratch directory, such as a few git commands in a throwaway
+repository. A claim you could settle only by running a test suite or
 building the change is a finding for the writer, or a question; say
 what you could not check.
 Turn economy: every turn re-sends everything read so far, so a wasted
diff --git a/factory/prompts/critic.md b/factory/prompts/critic.md
index e3abc21..c31f0d4 100644
--- a/factory/prompts/critic.md
+++ b/factory/prompts/critic.md
@@ -40,10 +40,11 @@ RUBRIC (judge intent, not wording)
 
 PROCESS
 Spot-check at least 2 cited paths and 1 acceptance command yourself.
-Ground any one claim with at most 2 paths and 1 command. Run no test
-suite and build nothing: no clone, worktree or prototype of the change.
-Pick an acceptance command that runs no test suite, and run it as the
-spec gives it. A claim you could settle only by running a test suite or
+Run no test suite: the implementer and the verifier run it. Pick an
+acceptance command that runs no test suite, and run it as the spec
+gives it. To confirm a finding you may run a small experiment in your
+scratch directory, such as a few git commands in a throwaway
+repository. A claim you could settle only by running a test suite or
 building the change is a finding for the writer, or a question; say
 what you could not check.
 Turn economy: every turn re-sends everything read so far, so a wasted
