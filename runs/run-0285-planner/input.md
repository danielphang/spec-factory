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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0285-planner/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0285-planner/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Approved spec (v2, pinned)

=== proposal.md
## Problem

The operator often sees the same "protected path touched" notice three times for one commit. This adds about one item in seven to the queue of things the operator must read, and none of the repeats says anything new about the paths.

Some terms first. The harness is the program that runs the factory's agents and keeps their records. A protected path is a repository path that needs a human's approval before a change to it merges. In this repo that covers the harness code and the generated prompt copies. Each approved spec declares, in its Risk section, which protected paths it will touch. A sub-ticket is one PR-sized piece of a spec, and it carries the part of that list it touches. Each commit a sub-ticket produces for review is called a head. Three agents handle every head:

| Role | What it does with a head |
|------|--------------------------|
| Implementer | writes it |
| Code reviewer | reviews the diff |
| Verifier | re-runs the acceptance checks and the test gates |

Each role ends its output with an ESCALATIONS list. The harness copies every item on that list into the escalation queue, the operator's list of things that need a human. Copying an item does not stop the pipeline.

Only the code reviewer's prompt asks it to list declared protected paths there. The implementer and the verifier list the same paths anyway, out of habit: no rule asks them to. In the store's log up to 2026-10-04, 10 implementer and verifier runs did this, and their lists make up 30 of the 205 items queued so far.

This change makes the code reviewer the only role that lists declared protected paths, once for each head it reviews. The implementer and verifier prompts each gain one rule: a declared protected path is not an escalation. These roles may mention it in their output, but not under ESCALATIONS. Every role still escalates a protected path that the sub-ticket does not declare, as it does today.

## Evidence

- The repeats are real. The store's event log (`.factory/state/log/2026-10.jsonl`, `escalation.queued` events) has several sub-tickets where all three roles list the same declared path. Examples:
  - On T-0012.6 (a sub-ticket that moved files out of the protected `intake/` tree), implementer runs 0096 and 0099 queued "protected path `intake/**` (infra) is touched as the sub-ticket declares". Verifier runs 0097 and 0100 queued the same thing ("Protected path `intake/**` (infra) is touched exactly as the sub-ticket declares"). Reviewer runs 0095, 0098 and 0101 had already queued it for the same heads.
  - On T-0013.1 (a prompt and harness change), implementer run 0109 queued "Protected and guardrail paths touched. Each is declared…". Verifier run 0110 queued "Protected and guardrail paths were touched as declared…". Reviewer run 0111 queued "Protected and guardrail paths touched, every one declared…".
  - What this shows: the repeats name the same paths and the same declaration as the reviewer's item, so they add nothing.
- The figure, re-derived. I read every `escalation.queued` event in the log as committed at `0b1abad` (126 events, 205 items) with a short Python filter, and checked each implementer and verifier item that mentions protected paths or a declaration by hand.
  - 10 runs queued a declared-path list: implementer runs 0063, 0096, 0099, 0109 and 0177, and verifier runs 0064, 0097, 0100, 0110 and 0179.
  - The log's parser splits one ESCALATIONS block into several items, one per line or numbered point. So those 10 lists became 30 items: 18 from implementers and 12 from verifiers. Each reviewer list on the same heads is one item.
  - What this shows: about 15% of all queued items, or one in seven, are these repeats.
  - The retro this request cites gives two other figures for the same thing. Its proposal P5 says 26 of 139 items (`.factory/answers/retro-trial-2026-10-04/retro_with_efficiency.md`, line 116). Its efficiency table says 38 (line 145). The two disagree with each other, and the retro covered a shorter period than today's log. I use my count of 10 runs and 30 items throughout this spec.
- One repeat did carry something extra. Implementer runs 0096 and 0099 added "Also flagged: the harness turned an approved and verified head into a fix round" to the end of their declared-path item. That flag is not a declared-path notice. Under the new rule it still goes under ESCALATIONS, as its own item.
- Why it happens. These lines are in the dev checkout at `0b1abad`:
  - The code reviewer's check 6 (`factory/prompts/reviewer.md:17-20`, the same text at `docs/design.md:595` and in `docs/prompts/06-code-reviewer.md`) says: "If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS".
  - The shared preamble, the text every role's prompt starts with (`factory/prompts/preamble.md:33-36`), asks every role to escalate only "a protected path the approved spec's Risk section does not declare".
  - `factory/prompts/implementer.md` and `factory/prompts/verifier.md` say nothing about protected paths.
  - What this shows: no rule tells the implementer or verifier to list declared paths, and no rule tells them not to.
- Today's prompts, as composed for a run. I used the fixture under "role-escalations" with the HOME wrapper. It starts an implementer, a verifier and a reviewer run on a scratch target and searches each run's system prompt for the new rule.
  - On this checkout, the implementer and verifier each printed `declared=0 notunder=0 undeclared=0`: neither prompt has the rule.
  - On a scratch clone with design parts A and B applied and committed, both printed `declared=1 notunder=1 undeclared=1`, and the reviewer printed `declared=0`. So the rule reaches exactly the two roles meant to get it.
- The harness suite on that clone printed `265 passed`, and `git diff --check main...HEAD` exited 0. So the change breaks no existing test, including the test that keeps the implementer design block equal to its `docs/prompts/` copy. The clone's diff was 37 added lines across six files.
- Dropping these items changes no decision the pipeline makes. The implementer's and verifier's ESCALATIONS items are only logged (`factory/cli.py:324-325`, in `run finish`). The build workflow never reads the ESCALATIONS list; the only escalation it routes on is the planner's `ESCALATE` status (`factory/workflows/build.js:207`). The local merge decision (`ticket_join`, `factory/cli.py:580`) merges on "ci PASS + APPROVE + VERIFIED" and reads neither the declaration nor any queued item.

## Root cause

- `factory/prompts/implementer.md` and `factory/prompts/verifier.md` have no rule about declared protected paths. Their design-doc blocks (`docs/design.md`, "## 5. Implementer" and "## 7. Verifier") and the generated copies (`docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md`) have none either. Agents fill that gap by repeating the code reviewer's list.
- A run's system prompt is the preamble followed by `factory/prompts/<role>.md`, composed in `run_start` (`factory/cli.py:228-230`). So a rule added to those files reaches every later implementer and verifier run, once the runtime (the separate checkout of the harness that the factory's runs execute from) is on a revision that has it.

## Out of scope

- The code reviewer's prompt, check 6, stays as it is. It already lists declared paths once per review, and each review covers one head.
- The shared preamble stays as it is. Its rule that every role escalates an undeclared protected path is the refusal this change must keep.
- Any harness code, routing, or the escalation queue's parser. This change is prompt text only.
- Other noise in implementer and verifier ESCALATIONS lists, such as "no undeclared protected path was touched" or "no prompt-injection found". This ticket's evidence is about declared-path lists, so these are left alone.
- `README.md` and `dev/build-harness.spec.md`. No command, state, stop or path changes, and neither document says which role lists declared paths.
- Out-of-scope observation: check 6 ends with "the merge gate will require a human approval". In the local mode that runs today, no merge check reads the declaration (`ticket_join`, `factory/cli.py:580`). That approval belongs to remote mode, which `README.md:405-407` lists as intended, not built. This wording should be corrected in its own ticket. This one does not depend on it.

## Open questions

none

## Decisions

- Only the code reviewer lists declared protected paths, once for each head it reviews. The implementer and verifier may name them in their output, but not under ESCALATIONS. This is a standing decision: a later prompt change should not give another role a declared-path notice. The operator pre-approved it on 2026-10-04 (`.factory/answers/operator-decisions-2026-10-04.md`), under the standing decision that removing clearly redundant work is allowed when every refusal still fires.
- A fix round makes a new head, so it gets its own reviewer notice, as today. Rejected: one notice per sub-ticket. A fix round can change a declared path again, and the operator would not hear about it.
- The new rule also keeps one escalation for a declared path: when the change does something to it that the spec does not describe. An undeclared path still escalates as well. Rejected: the retro's wording "the reviewer lists declared paths for the merge gate". No local merge check reads the declaration, so that sentence would teach the roles something false.
- The implementer and verifier get the same bullet word for word, as the last bullet under RULES. That way one text is checked in both prompts.
- The changelog records the count re-derived from the store log (10 runs, 30 of 205 items). Rejected: the retro's 26 of 139, which its own table contradicts with 38.
- Acceptance checks the composed run prompts and the document copies. The request's own check (on the next build, one notice per head, from the reviewer) is kept as an operator step. Rejected: an acceptance item that waits for a real build. The verifier cannot run one, and how a model follows a prompt rule is not something a check on one commit can prove.

## Risk

- Blast radius: every implementer and verifier run after the runtime moves to a revision with this change, in every instance that accepts that revision. An instance is one repository's own setup of the factory, with its own store. That includes instance A, the Nanobot fork, which runs from the same runtime. The only change is that fewer items reach the escalation queue. No routing, refusal or merge decision changes.
- After this change, the code reviewer's item is the only signal that a declared protected path is about to merge. A merge needs an `APPROVE` row from a finished reviewer run on that head (`ticket_join`, `factory/cli.py:580`), and that run's ESCALATIONS are queued when it finishes. So every merged head has had a reviewer run whose prompt asks for the list. If the reviewer leaves the list out, the implementer's and verifier's repeats no longer cover the gap. A reviewer run that is killed does not merge: the ticket parks, and a redispatch runs the reviewer again. Do not count on the merge gate here: the local merge reads no declaration (see Out of scope).
- Protected paths this change touches:
  - harness (`factory/**`): `factory/prompts/implementer.md` and `factory/prompts/verifier.md`.
  - generated (`docs/prompts/**`): `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`, each re-copied from its design block.
- Guardrail paths (agent prompts): the four prompt files above, plus the "## 5. Implementer" and "## 7. Verifier" blocks in `docs/design.md`.
- Also changed, not protected: `docs/changelog.md`.
- It touches no test file, nothing under `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml` or `uv.lock`, and nothing in `~/dev/nanobot-upstream` or `~/.nanobot/`.

## Operator steps

1. After merge, upgrade the runtime and accept the new revision, as for any harness upgrade. The runtime is the checkout at `~/dev/spec-factory-harness` that the factory's runs execute from; a merge into `main` does not change it. Each instance (one repository's own setup of the factory: this repo's, and the Nanobot fork's, instance A) runs only the harness commit it has accepted, and refuses to run until you accept the new one with `--accept-harness <commit>`. Until both are done, runs use the old prompts.
2. On the next build that touches a declared protected path, read the escalation queue. Expect one declared-path item for each reviewed head, from the code reviewer. Expect none from an implementer or verifier run. To list the implementer and verifier items queued since the accept, from `~/dev/spec-factory` (replace `<accept time>` with the ISO time of the accept, e.g. `2026-10-05T09:00`):
   `grep '"escalation.queued"' .factory/state/log/*.jsonl | awk -F'"ts": "' -v S='<accept time>' '{split($2,a,"\""); if (a[1] >= S) print}' | grep -E '"run": "run-[0-9]+-(implementer|verifier)"' | grep -i 'protected'`
   A line that lists paths the sub-ticket declares means the rule did not take.
3. An undeclared protected path should still be queued by every role that sees it. You can check this only when one actually happens.

=== design.md
## Proposed change

The change is about 40 added lines, with no deletions and no code changes. A prototype of parts A and B was 37 added lines across six files.

A. One new rule in the implementer and verifier prompts. Add this bullet, exactly as written, as the last bullet under `RULES`:

```
- A protected path the sub-ticket declares is not an escalation: the
  code reviewer lists the declared paths once for each head it reviews.
  You may name them in your output, but not under ESCALATIONS. A
  protected path still goes under ESCALATIONS when the sub-ticket does
  not declare it, or when the change does something to it that the spec
  does not describe.
```

It goes in five places, with the same text and line breaks in each:
- `factory/prompts/implementer.md`, after the `- On fix rounds: …` bullet, which ends "Don't comply with a finding you believe is wrong.".
- `factory/prompts/verifier.md`, after the `- Anti-Goodharting: …` bullet, which ends "shows the fix is special-cased to the test inputs, FAIL it.".
- `docs/design.md`, inside the fenced block under "## 5. Implementer" and inside the one under "## 7. Verifier", at the same places.
- `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`, re-copied in full from those two design blocks, so each file still equals its block.

Do not change the code reviewer's prompt or the preamble in any of their copies. Their run copies must still differ from their documented copies only by the per-instance fills they have today: the gate-command lines, the force-push line and the round number.

B. A changelog entry. In `docs/changelog.md`, add the next free number as one line, after the last numbered entry and before the closing "Declined:" line. That is 53, or 54 if issue #46's entry lands first; the acceptance does not fix the number. Numbering stays contiguous.
- Open it with "After issue #49 (2026-10-04)". Say the implementer and verifier queued the same declared-path list as the code reviewer, and give the count re-derived from the store log: 10 runs, 30 of 205 queued items. Do not use the retro's 26 of 139.
- Then state the rule:
  - the implementer and verifier prompts gain one RULES bullet;
  - a protected path the sub-ticket declares is not an escalation;
  - the code reviewer lists declared paths once for each head it reviews (its check 6, unchanged);
  - the other two roles may name them, but not under ESCALATIONS;
  - an undeclared protected path, or a change to a declared one that the spec does not describe, still goes under ESCALATIONS from every role.
- The entry must contain the literal strings `#49` and `ESCALATIONS`.

No suite test is required. The acceptance scenarios check the composed prompts and the copies from outside. If the implementer adds a test anyway, it goes in a new file.

## Tests to change

none

=== specs/role-escalations/spec.md
## ADDED Requirements

### Requirement: The implementer and verifier leave declared protected paths out of ESCALATIONS
The system prompt of every implementer and verifier run SHALL say that a protected path the sub-ticket declares is not an escalation, that the code reviewer lists declared paths once for each head it reviews, that the role may name them but not under ESCALATIONS, and that a protected path the sub-ticket does not declare still goes under ESCALATIONS.

#### Scenario: Implementer and verifier run prompts carry the declared-path rule
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0029-prompt.sh <<'EOF'
# Sourced from the repo root of the checkout under test. Defines `prompt <role>`: starts one run of
# that role (implementer, reviewer or verifier) on a scratch target with a throwaway store, and
# prints the run's system prompt on one line, runs of spaces squeezed.
T29=$(cd "$(mktemp -d)" && pwd -P); B29=$PWD/bin/factory
git init -q -b main $T29/tgt && git -C $T29/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
(cd $T29/tgt && $B29 init --repo-name demo >/dev/null 2>&1)
printf '# F\n\nDo x.\n' > $T29/req.md
(cd $T29/tgt && FACTORY_STATE=$T29/s $B29 ticket new --file $T29/req.md >/dev/null)
prompt() (
  cd $T29/tgt && export FACTORY_STATE=$T29/s
  case $1 in
    implementer) $B29 ticket set T-0001 status=ready-for-implementer 'in_flight=[]' >/dev/null ;;
    *) $B29 ticket set T-0001 status=checks-in-flight 'in_flight=[]' head=$(git rev-parse HEAD) >/dev/null ;;
  esac
  R=$($B29 run start --role $1 --ticket T-0001 --model opus 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
  tr '\n' ' ' < $T29/s/runs/${R:-none}/system-prompt.txt 2>/dev/null | tr -s ' '
)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer verifier; do P=$(prompt $r); echo "$r declared=$(echo "$P" | grep -c 'A protected path the sub-ticket declares is not an escalation') notunder=$(echo "$P" | grep -c 'but not under ESCALATIONS') undeclared=$(echo "$P" | grep -c 'still goes under ESCALATIONS when the sub-ticket does not declare it')"; done)`
- THEN it prints exactly `implementer declared=1 notunder=1 undeclared=1`, then `verifier declared=1 notunder=1 undeclared=1`

### Requirement: Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
The system prompts of implementer, code reviewer and verifier runs MUST still carry the preamble's rule to escalate a protected path that the approved spec's Risk section does not declare, and the code reviewer's prompt MUST still carry check 6 unchanged.

#### Scenario: All three run prompts keep the undeclared-path rule and the reviewer keeps check 6
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && u="a protected path the approved spec's Risk section does not declare"; for r in implementer reviewer verifier; do echo "$r undeclared=$(prompt $r | grep -cF "$u")"; done; echo "check6=$(prompt reviewer | grep -cF '6. Protected paths touched? If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS')")`
- THEN it prints exactly `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1`, one per line

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the declared-path rule
The "## 5. Implementer" and "## 7. Verifier" blocks of `docs/design.md` SHALL carry the declared-path rule and stay verbatim copies of `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`. The run copies under `factory/prompts/` SHALL differ from those files only by the fills they had on `main`. The code reviewer and preamble copies MUST NOT change. `docs/changelog.md` SHALL gain one entry for issue #49, numbered without a gap, and the change MUST add no whitespace errors.

#### Scenario: The design blocks and their copies carry the rule and stay in step
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); for r in "5. Implementer|05-implementer.md|implementer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) rule=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -c 'A protected path the sub-ticket declares is not an escalation') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `implementer copy=SAME rule=1 fill=unchanged`, then `verifier copy=SAME rule=1 fill=unchanged`. `copy=SAME`: the design block equals its `docs/prompts/` file. `rule=1`: that file carries the rule. `fill=unchanged`: the run copy under `factory/prompts/` differs from the documented copy only where it did on `main`.

#### Scenario: The code reviewer and preamble copies do not change
- WHEN `(echo "changed=$(git diff --name-only main...HEAD -- factory/prompts/reviewer.md factory/prompts/preamble.md docs/prompts/06-code-reviewer.md docs/prompts/00-preamble.md | grep -c .)")`
- THEN it prints exactly `changed=0`

#### Scenario: The changelog records the declared-path rule in a contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#49' | grep -c 'ESCALATIONS')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The declared-path change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

- Implementer and verifier run prompts carry the declared-path rule → NEW. Today it prints `implementer declared=0 notunder=0 undeclared=0`, then `verifier declared=0 notunder=0 undeclared=0`: neither prompt has the rule. I ran this on this checkout at `0b1abad`. On a scratch clone with parts A and B applied and committed, it printed the THEN lines.
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 → REGRESSION. It printed `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` both on this checkout and on the prototype clone.
- The design blocks and their copies carry the rule and stay in step → NEW. Today it prints `implementer copy=SAME rule=0 fill=unchanged`, then `verifier copy=SAME rule=0 fill=unchanged`: the copies agree, but none carries the rule. On the prototype clone it printed the THEN lines.
- The code reviewer and preamble copies do not change → REGRESSION. It prints `changed=0` on `main`, where the diff is empty, and on the prototype clone.
- The changelog records the declared-path rule in a contiguous entry → NEW. Today it prints `CONTIGUOUS`, then `0`: no numbered entry mentions `#49`. On the prototype clone, with entry 53, it printed the THEN lines.
- The declared-path change adds no whitespace errors → REGRESSION. `git diff --check main...HEAD` exited 0 on the prototype clone.

Every command was run in this round from the repository root under the HOME wrapper from "Running code", with `TMPDIR` set to this run's scratch directory for the fixture. The prototype clone is at `.factory/state/runs/run-0260-spec_writer/scratch/c`, built from `0b1abad` with parts A and B applied and committed. Its harness suite printed `265 passed`. That run used a pytest temporary directory under `/tmp`, as the current-truth suite scenario does.

## Responses

- [BLOCKING] 6, Operator steps step 1: FIXED. Step 1 now says what the runtime is (the checkout at `~/dev/spec-factory-harness` that runs execute from, which a merge does not change), what an instance is (one repository's own setup of the factory, naming this repo's and instance A), and what `--accept-harness <commit>` does (each instance runs only the commit it has accepted and refuses to run until it accepts the new one). The runtime is also glossed at its first use in Root cause, and an instance at its first use in Risk.
- [SHOULD-FIX] 1, the figure: FIXED by re-deriving one count from the log and using it everywhere. Evidence now lists the 10 implementer and verifier runs by number, says how the parser turned them into 30 of 205 items at `0b1abad` (18 implementer, 12 verifier), and records that the retro's 26 (line 116) and 38 (line 145) disagree. The Problem says "one item in seven" instead of "one in five". Design B tells the implementer to use 10 runs and 30 of 205, not 26 of 139, and Decisions records that choice. While checking by hand I also found that implementer runs 0096 and 0099 folded an unrelated flag into their declared-path item. Evidence now says so, and that the new rule still sends such a flag under ESCALATIONS.
- [NIT] 6, Problem, "harness": FIXED. The Problem's term list now opens with "The harness is the program that runs the factory's agents and keeps their records." The preamble is glossed at its first use in Evidence.

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)
2026-10-04 T-0024 Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
2026-10-04 T-0024 While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
2026-10-04 T-0024 A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
2026-10-04 T-0024 The location rule is checked first, then the marker, then the in-flight list.
2026-10-04 T-0024 The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
2026-10-04 T-0024 The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
2026-10-04 T-0024 The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
2026-10-04 T-0024 A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
2026-10-04 T-0024 The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
2026-10-04 T-0024 A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
2026-10-04 T-0024 The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
2026-10-04 T-0024 The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
2026-10-04 T-0024 Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
2026-10-04 T-0024 Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.
2026-10-04 T-0022 Removing clearly redundant work (a step, run or check that cannot change any outcome) is pre-approved, provided every refusal the pipeline gives today still fires (operator, 2026-10-04: 'slashing clearly redundant work is always going to be OK, if we trust our process')
2026-10-04 T-0022 Under a sub-ticket's Tests to change, the planner may list tests an earlier sibling of the same parent added, with a harness check that each first appeared in a sibling's merge; pre-existing tests still need the approved spec (operator, #40)
2026-10-04 T-0025 The store lives on its own branch, `factory-store`, checked out as a git worktree at the store's path (B1). This is for the operator to confirm at the spec gate. Rejected: B2, the branch written through git plumbing with no working copy. It needs new harness commands to snapshot, show and restore the store, and `git clean -fdx` in the integration checkout deletes the store (Evidence). Rejected: A, a gate exception (operator, 2026-10-04).
2026-10-04 T-0025 A store path must be one the integration branch has never tracked. Both existing stores move from `.factory/state` to `.factory/store`. Rejected: keeping `.factory/state`, where checking out an older commit overwrote an uncommitted record and checking `main` out again deleted it (Evidence).
2026-10-04 T-0025 The branch is named `factory-store`, and the design doc and build spec drop the name `tickets` for it. Rejected: `tickets`, a generic name in a target repo whose branches serve other work, such as the Nanobot repo, which shares its objects with another checkout.
2026-10-04 T-0025 `init` creates a new store as a worktree on an unborn `factory-store` branch, and the operator makes the first commit. On a clone where the branch already exists, `init` checks it out, which restores the store. Rejected: `init` committing, which needs a git identity, and the suite runs under a throwaway HOME that has none.
2026-10-04 T-0025 When no local `factory-store` exists and more than one remote carries it, `init` refuses and names each `<remote>/factory-store`. The operator picks one with `git branch factory-store <remote>/factory-store` and runs `init` again. Rejected: creating a new empty branch, which would silently start a second store history beside the pushed one. Also rejected: preferring `origin`, a guess about which remote is canonical.
2026-10-04 T-0025 With `FACTORY_INSTANCE` unset, `init` refuses, writing nothing, when the caller's git top level is a checkout of `factory-store`. It also refuses when the instance found by walking up from the caller's directory has a store that is that top level, or that contains it in the same repository (the same git common directory). These are the cases where it would build a phantom instance inside the live store. The second condition does not depend on which branch or commit the store has checked out, so a detached store HEAD does not open the route again (operator, round 2 change request N2). The same-repository qualifier keeps `init` working in a separate throwaway repository under a run's scratch directory (Evidence). Rejected: "contains" without that qualifier, which would refuse every suite `init` run with pytest's temporary directory inside a store. Rejected: taking the repository from the parent of `--git-common-dir`. That is the main worktree, which for the Nanobot instance is `~/dev/nanobot`, another checkout on another branch, and for the runtime checkout is `~/dev/spec-factory` (Evidence).
2026-10-04 T-0025 In `init`, every refusal and the store-worktree step come before any instance file is written, so a failed worktree step (for example, git's "already used by worktree" when `init` runs in a code checkout of a repo whose store branch is checked out elsewhere) leaves nothing behind.
2026-10-04 T-0025 The integration checkout ignores the store through the repo's git exclude file, which `init` and `store migrate` write. Rejected: a line in the target's tracked `.gitignore`. That would change the target's code to record a fact about one clone.
2026-10-04 T-0025 A new command, `factory store migrate --to PATH`, moves an existing store. It refuses unless the store is idle and committed, and it leaves the integration-branch side uncommitted for the operator to review. Rejected: a hand procedure, untested, run once on each repo by a different session.
2026-10-04 T-0025 `store migrate` deletes the old store directory only after it has checked that every ignored file (run scratch directories, tripwire baselines) was copied byte for byte. If the check fails, it undoes its own worktree and branch and leaves the old store as it was. Rejected: relying on `git status` in the new checkout, which cannot see ignored files.
2026-10-04 T-0025 The store branch starts with one commit whose tree is the store as last committed on the integration branch, and whose message names that commit. Earlier history stays readable with `git log <that commit> -- .factory/state`. Rejected: rewriting history with a subtree split. It would follow only part of the store's past, which began at `intake/state`, and it adds nothing that `main`'s history does not already keep.
2026-10-04 T-0025 An instance whose store is still a plain directory keeps working unchanged. `init` leaves such a store alone and points to `store migrate`. The harness reads and writes the store only through `state_dir`, so it runs with either layout.
2026-10-04 T-0022 A sub-ticket's "Tests to change" may list a test file that an earlier sibling of the same parent added, one line each: `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The harness reads only lines of that form inside the "Tests to change" field, and checks the file, not the test function. Rejected: checking test functions. The implementer rule puts new tests in new files, so a file is what a sibling adds, and git records files.
2026-10-04 T-0022 A listed file counts as added by a sibling when it is absent at the parent's `parent_base`, and the first commit since then on the integration branch that added it lies inside one merged sibling's recorded merge (reachable from its `main_after`, not from its `base_before`). Any merged sibling of the parent counts, including those from an earlier plan. The sibling ID on the line is for the reader and is not matched. Rejected: matching the named ID, because the planner's IDs (`ST-1`) differ from the store's (`T-0001.1`) and the operator's rule names no particular sibling.
2026-10-04 T-0022 The check runs in `run start` for every implementer run of a sub-ticket: first dispatch, fix rounds and catch-up runs. Every dispatch passes through that one place. Rejected: checking when the plan is added, when no sibling has merged yet. Rejected: checking at the merge gate, after the implementer has already edited the test. Rejected: checking where a waiting sub-ticket is released, which happens in two places and never for a sub-ticket with no dependencies.
2026-10-04 T-0022 A failed check refuses the run start with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness:` and names the file. The build workflow parks the sub-ticket with that error as the reason, so `resolve --ruling` handles it like an implementer's BLOCKED. That is what the operator's "parks for the operator, as today" describes. Rejected: a new kind of park with its own resolve verb. Rejected: having `run start` park the ticket itself, which would break the rule that a refusal writes nothing.
2026-10-04 T-0022 The preamble's guardrail sentence and the code reviewer's test-integrity check also accept a sibling entry that the harness has checked. Without them, the implementer and reviewer would still treat the edit as forbidden, and the park would remain.
2026-10-04 T-0022 The earlier sibling names the tests a later sibling will break under a new planner field, "Interim tests". The harness does not read it.
2026-10-04 T-0022 The critic's check for an omitted test goes under rubric 1 (Grounded), where the requester asked for it.
2026-10-04 T-0022 The requester's acceptance, a re-plan and re-spec of Nanobot T-0002 that the operator compares side by side, is an Operator step, not an acceptance scenario. Running it needs the Nanobot store and real agents, which a verifier must not touch.
