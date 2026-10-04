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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0288-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0288-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0288-reviewer/wt` (branch `factory/T-0029.1`, base `7d57998169bf08563fe33fcd098729fae200c4b9`, head `090939d6428bff085890aa5d1b9d384bb8915c78`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0029.1

## ST-1 / Declared protected paths leave the implementer and verifier ESCALATIONS lists
Depends on: none
Parallel-safe: yes

Parent: T-0029, approved spec v2 (issue #49). Read it for context. Do NOT implement parts outside this sub-ticket.

One sub-ticket. The whole change is about 40 added lines of prompt text plus one changelog line, and the spec's prototype was 37 added lines across six files. Splitting it would gain nothing for review or rollback. It would also break things: the existing test that keeps each design block equal to its `docs/prompts/` copy fails if part A lands in `docs/design.md` without the copies, and part B's changelog entry describes part A.

Scope: parts A and B of the parent's design.
- A. Add the new RULES bullet, word for word and with the spec's line breaks, as the last bullet under `RULES` in five places:
  - `factory/prompts/implementer.md`, after the `- On fix rounds: …` bullet (it ends at line 43 on `main` at `7d57998`);
  - `factory/prompts/verifier.md`, after the `- Anti-Goodharting: …` bullet (it ends at line 33);
  - `docs/design.md`, in the fenced blocks under "## 5. Implementer" (anchor at line 585) and "## 7. Verifier" (anchor at line 693);
  - `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`, each re-copied in full from its design block.

  Do not change the code reviewer's prompt or the preamble in any copy.
- B. One numbered entry in `docs/changelog.md`, after the last numbered entry and before the "Declined:" line, with the content the design lists. It opens "After issue #49 (2026-10-04)", uses 10 runs and 30 of 205 items, and contains `#49` and `ESCALATIONS`.
  - Numbering note: the spec expected 53, or 54 if #46 landed first. On `main` at `7d57998`, entries 53 (#46) and 54 (#40) already exist (`docs/changelog.md` lines 57-58). So the next free number is 55. The spec's acceptance does not fix the number, only that numbering stays contiguous.

Acceptance (all from the parent; commands run from the repo root after `uv sync --frozen`, under the HOME wrapper, with `TMPDIR` set to the run's scratch directory for the fixture):
- Implementer and verifier run prompts carry the declared-path rule (NEW).
  - GIVEN: write the fixture with the spec's `cat > ${TMPDIR:-/tmp}/t0029-prompt.sh <<'EOF' … EOF` block, verbatim.
  - WHEN: `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer verifier; do P=$(prompt $r); echo "$r declared=$(echo "$P" | grep -c 'A protected path the sub-ticket declares is not an escalation') notunder=$(echo "$P" | grep -c 'but not under ESCALATIONS') undeclared=$(echo "$P" | grep -c 'still goes under ESCALATIONS when the sub-ticket does not declare it')"; done)`
  - THEN: it prints exactly `implementer declared=1 notunder=1 undeclared=1`, then `verifier declared=1 notunder=1 undeclared=1`.
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 (REGRESSION).
  - WHEN: `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && u="a protected path the approved spec's Risk section does not declare"; for r in implementer reviewer verifier; do echo "$r undeclared=$(prompt $r | grep -cF "$u")"; done; echo "check6=$(prompt reviewer | grep -cF '6. Protected paths touched? If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS')")`
  - THEN: it prints exactly `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1`, one per line.
- The design blocks and their copies carry the rule and stay in step (NEW).
  - WHEN: the spec's command beginning `(T=$(mktemp -d); Q=$(printf '\140\140\140'); for r in "5. Implementer|05-implementer.md|implementer" …`, verbatim from `specs/harness-docs/spec.md`.
  - THEN: it prints exactly `implementer copy=SAME rule=1 fill=unchanged`, then `verifier copy=SAME rule=1 fill=unchanged`.
- The code reviewer and preamble copies do not change (REGRESSION).
  - WHEN: `(echo "changed=$(git diff --name-only main...HEAD -- factory/prompts/reviewer.md factory/prompts/preamble.md docs/prompts/06-code-reviewer.md docs/prompts/00-preamble.md | grep -c .)")`
  - THEN: it prints exactly `changed=0`.
- The changelog records the declared-path rule in a contiguous entry (NEW).
  - WHEN: `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#49' | grep -c 'ESCALATIONS')`
  - THEN: it prints `CONTIGUOUS`, then `1`.
- The declared-path change adds no whitespace errors (REGRESSION).
  - WHEN: `(git diff --check main...HEAD; echo "exit=$?")`
  - THEN: it prints only `exit=0`.
- Intermediate check: the harness suite (REGRESSION). This is not a parent scenario. It guards the existing copy-equality test.
  - WHEN: `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, with pytest's temporary directory under `/tmp` as the current-truth suite scenario does.
  - THEN: all tests pass, none skipped or deselected beyond what `main` already does.

Tests to change: none

Protected paths:
- harness (`factory/**`): `factory/prompts/implementer.md` and `factory/prompts/verifier.md`.
- generated (`docs/prompts/**`): `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`.
- Guardrail paths (agent prompts) that the spec's Risk declares: the four files above, plus the "## 5. Implementer" and "## 7. Verifier" blocks in `docs/design.md`.

Out of scope:
- The code reviewer's prompt, including check 6 and its wording "the merge gate will require a human approval". That wording is a separate ticket.
- The shared preamble in every copy.
- Any harness code, routing, or the escalation queue's parser.
- Other noise in implementer and verifier ESCALATIONS lists.
- `README.md`, `dev/build-harness.spec.md`, and anything under `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream` or `~/.nanobot/`.
- The operator steps: the runtime upgrade, `--accept-harness`, and checking the queue on the next build.

## Parent spec (v2, pinned)

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

## PR description (the implementer's output)

Sub-ticket: T-0029.1 (ST-1, "Declared protected paths leave the implementer and verifier ESCALATIONS lists"), parent T-0029, approved spec v2 (issue #49). Branch `factory/T-0029.1`, head `090939d6428bff085890aa5d1b9d384bb8915c78`, base `7d57998169bf08563fe33fcd098729fae200c4b9`.

## What changed

After this change, the implementer and verifier prompts tell those roles not to list a declared protected path under ESCALATIONS. A protected path is a repository path that needs a human's approval before a change to it merges. A declared one is a path the sub-ticket says it will touch. ESCALATIONS is the list at the end of each role's output, and the harness copies every item on it into the operator's escalation queue. The code reviewer is now the only role told to list declared paths. It keeps doing so once for each head (each commit put up for review), through its check 6, which is unchanged. Every role still escalates an undeclared protected path. The change is prompt text and one changelog line: 37 added lines across six files, with no deletions and no code.

- A. The spec's RULES bullet, word for word and with its line breaks, is now the last bullet under `RULES` in five places:
  - `factory/prompts/implementer.md`, after the `- On fix rounds: …` bullet;
  - `factory/prompts/verifier.md`, after the `- Anti-Goodharting: …` bullet;
  - `docs/design.md`, inside the fenced blocks under "## 5. Implementer" and "## 7. Verifier", at the same two places;
  - `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`. I re-copied each in full from its design block, using the same awk extraction the acceptance command uses. Each copy's diff is only the six added lines.
  - The bullet went in through a script that matched the anchor line, and the script checked that each anchor occurs exactly once in its file. The code reviewer's prompt and the preamble are untouched in every copy.
- B. A new entry 55 in `docs/changelog.md`, after entry 54 (#40) and before the "Declined:" line.
  - It opens "After issue #49 (2026-10-04)" and gives the re-derived count: 10 runs, 30 of 205 queued items.
  - It then states the rule in the five points the design lists, and records that the retro's figure of 26 of 139 was rejected.
  - The number is 55, not the spec's 53, because entries 53 (#46) and 54 (#40) were already on `main` at `7d57998`. The ticket's numbering note says the same.

## Acceptance results

Every command ran from the worktree root under the HOME wrapper, after `uv sync --frozen`. `TMPDIR` was set to this run's scratch directory, and the fixture was written there with the spec's block, verbatim.

| Check | Label | Before (base `7d57998`) | After (`090939d`) |
|---|---|---|---|
| 1. Implementer and verifier run prompts carry the declared-path rule | NEW | `implementer declared=0 notunder=0 undeclared=0`, `verifier declared=0 notunder=0 undeclared=0` | `implementer declared=1 notunder=1 undeclared=1`, `verifier declared=1 notunder=1 undeclared=1` |
| 2. All three run prompts keep the undeclared-path rule; reviewer keeps check 6 | REGRESSION | not run | `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` |
| 3. Design blocks and copies carry the rule and stay in step | NEW | `implementer copy=SAME rule=0 fill=unchanged`, `verifier copy=SAME rule=0 fill=unchanged` | `implementer copy=SAME rule=1 fill=unchanged`, `verifier copy=SAME rule=1 fill=unchanged` |
| 4. Code reviewer and preamble copies do not change | REGRESSION | not run | `changed=0` |
| 5. Changelog records the rule in a contiguous entry | NEW | `CONTIGUOUS`, `0` | `CONTIGUOUS`, `1` |
| 6. No whitespace errors (`git diff --check main...HEAD; echo "exit=$?"`) | REGRESSION | not run | `exit=0` |

Each NEW command failed on the base exactly as the spec's verification section predicted. Each command printed its THEN lines after the change. Neither REGRESSION command failed, so neither needed a run on the base.

Gates, each run once on `090939d`, from the worktree, exactly as written:
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`: no output, exit 0.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `310 passed in 379.56s (0:06:19)`, with nothing skipped or deselected. This also covers the existing test that keeps each design block equal to its `docs/prompts/` copy.

## Tests added/changed

None. The design says no suite test is required: the acceptance commands check the composed run prompts and the document copies from outside, and the existing copy-equality test already guards the design blocks. "Tests to change" is none, and no existing test file was touched.

## Known gaps and uncertainties

- The checks prove only that the rule text reaches the composed implementer and verifier prompts. They cannot prove that a model will follow it. The spec keeps that check as operator step 2: on the next build, read the escalation queue.
- The ticket asks for the suite to run with pytest's temporary directory under `/tmp`. I ran the gate exactly as written, in a shell whose `TMPDIR` was the macOS default, `/var/folders/1t/.../T/`. That directory is not `/tmp`, but like `/tmp` it lies outside the repository and the store. I believe this is the condition the ticket means, but I have not verified that the suite behaves the same under `/tmp` itself.
- The ticket gave the design-doc anchors as lines 585 and 693. On `7d57998`, the two bullets end at lines 585 and 693, and the headings are at lines 541 and 659. The inserts are at the bullet ends, as the ticket intends.
- factory: markers added: none.

## Out-of-scope observations

- This change touches no harness code. The rule reaches runs only after the operator upgrades the runtime (the checkout at `~/dev/spec-factory-harness` that runs execute from) and accepts the new commit with `--accept-harness <commit>` in each instance, as the spec's Operator steps say.
- The spec's own out-of-scope note still stands. Check 6's wording "the merge gate will require a human approval" does not match local mode, where no merge check reads the declaration. That wording is for a separate ticket.

## Responses to findings

Not applicable: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates ran on the committed head and printed exactly the expected output, and the diff is the spec's 37 lines.
ESCALATIONS: none

## Diff `7d57998169bf08563fe33fcd098729fae200c4b9...090939d6428bff085890aa5d1b9d384bb8915c78`

diff --git a/docs/changelog.md b/docs/changelog.md
index 7e4a414..922bd88 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -56,5 +56,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 52. After issue #45 (2026-10-04), where a spec writer's test run executed `init` from inside its scratch directory and initialised this repository's live store, writing a spec store, `decisions.md` and six agent files: the store CLI fences an instance's own store. A write run from inside the store's `runs/` or `worktrees/` is refused, with or without the marker and with or without a run in flight. While any run is in flight on the store, a write without `FACTORY_DISPATCH=1` in its environment is refused. The read-only commands stay open, and any command given `--accept-harness` counts as a write. Both workflow scripts put `FACTORY_DISPATCH=1` in front of every clerk command; the operator puts it in front of one command at a time and never exports it. A refusal is exit 2, writes nothing, and advises a throwaway `FACTORY_STATE` without naming the marker. The fence is checked before the harness lock, so the marker cannot get past the lock. Declined from the request: a preamble line telling roles to use a throwaway store, because the incident came from the test suite rather than a command the role typed; and a tripwire on the store root, because role runs and other tickets' clerk commands legitimately write the store during a run, so a comparison could not tell whose write it saw.
 53. After issue #46 (2026-10-04), where each store commit on the integration branch sent every sub-ticket waiting to merge back for a catch-up merge and a second round of checks that could not change the verdict: the store moves to its own branch, `factory-store`, checked out as a git worktree at the store's path and never merged into the integration branch, so a store commit no longer moves that branch; the merge gate is unchanged. A store path must be one the integration branch has never tracked, because at a once-tracked path a checkout of an older commit overwrites live records and a checkout back deletes them. `init` creates a missing own store as a worktree of an unborn `factory-store` branch, which needs no commit, or checks out the branch where it exists locally or on exactly one remote, which restores the store on a clone, and adds the store to the repo's git exclude file. It refuses when more than one remote carries the branch, naming each, and at a once-tracked path. With `FACTORY_INSTANCE` unset it refuses from inside the store checkout, on its branch or on a detached HEAD, so it can no longer build a phantom instance inside the live store; a separate repository under a run's scratch directory still gets its own instance. Every refusal comes before the first write. An existing store that is a plain directory is left alone, and `init` reports `store_branch` in its JSON. A new command, `factory store migrate --to PATH`, moves such a store: it refuses, writing nothing, unless the store in use is the instance's own and not yet on its branch, no `factory-store` branch exists, the integration branch is checked out, no run is in flight, no git worktree lies under the store, every store file is committed, PATH does not exist, lies outside the old store and was never tracked, and `instance.yaml` has a `state_dir:` line; it then starts `factory-store` at one commit whose tree is the store as last committed and whose message names that commit, checks it out at PATH, copies the files git ignores there and verifies them byte for byte, undoing its own worktree and branch and exiting 1 on a mismatch, and only then untracks and deletes the old directory, adds PATH to the exclude file and rewrites only the value of `state_dir`; it commits and pushes nothing.
 54. After issue #40 (2026-10-04), where sub-tickets parked for three causes that were visible when the work was planned or specified: a NEW check copied from the whole spec already passed at the sub-ticket's own start; an implementer could not change a test an earlier sibling sub-ticket had added to pin its interim behaviour, because only the spec gate's "Tests to change" list authorized a test edit and that test did not exist at the gate; and a spec's Decision overturned an existing test that nobody listed. The planner labels each check NEW or REGRESSION against the sub-ticket's own base, the integration branch with its dependencies merged, not by the parent's label. An earlier sibling names the new test files a later sibling will break under "Interim tests", which the harness does not read. A sub-ticket's "Tests to change" may list a test file an earlier sibling added, as `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. Before each implementer run, `run start` checks in git that the file was absent at the parent's base and was first added inside a merged sibling's recorded merge; otherwise it refuses with exit 2, writing nothing, with an error that starts `BLOCKED from harness:`, and the build parks the sub-ticket with that error so `resolve --ruling` returns it to its implementer. The preamble and the code reviewer accept such a checked entry. The spec writer lists the tests each behaviour-changing Decision overturns, and critic rubric 1 makes a missing one a finding. A test that existed before the parent's first merge still needs the pinned spec's list. Rejected: letting the implementer edit a test on its own judgement.
+55. After issue #49 (2026-10-04), where the implementer and verifier queued the same declared-path list as the code reviewer: in the store's log, 10 implementer and verifier runs did this, and their lists made up 30 of the 205 items queued so far. The implementer and verifier prompts gain one RULES bullet: a protected path the sub-ticket declares is not an escalation. The code reviewer lists declared paths once for each head it reviews, through its check 6, unchanged. The other two roles may name them in their output, but not under ESCALATIONS. An undeclared protected path, or a change to a declared one that the spec does not describe, still goes under ESCALATIONS from every role. Rejected: the retro's figure of 26 of 139 items, which its own table contradicts with 38.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index f08bbcc..93c2a4b 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -583,6 +583,12 @@ RULES
   description, even if it might cause a rejection.
 - On fix rounds: respond to each finding with FIXED (commit) or DISAGREE
   (evidence). Don't comply with a finding you believe is wrong.
+- A protected path the sub-ticket declares is not an escalation: the
+  code reviewer lists the declared paths once for each head it reviews.
+  You may name them in your output, but not under ESCALATIONS. A
+  protected path still goes under ESCALATIONS when the sub-ticket does
+  not declare it, or when the change does something to it that the spec
+  does not describe.
 
 PR DESCRIPTION
 Sub-ticket: <link>
@@ -691,6 +697,12 @@ RULES
 - Anti-Goodharting: your job is to find out whether the thing works, not
   whether the checklist is green. If every command passes but a probe
   shows the fix is special-cased to the test inputs, FAIL it.
+- A protected path the sub-ticket declares is not an escalation: the
+  code reviewer lists the declared paths once for each head it reviews.
+  You may name them in your output, but not under ESCALATIONS. A
+  protected path still goes under ESCALATIONS when the sub-ticket does
+  not declare it, or when the change does something to it that the spec
+  does not describe.
 
 OUTPUT
 Commit: <head SHA you verified>
diff --git a/docs/prompts/05-implementer.md b/docs/prompts/05-implementer.md
index fcf1e89..20697da 100644
--- a/docs/prompts/05-implementer.md
+++ b/docs/prompts/05-implementer.md
@@ -40,6 +40,12 @@ RULES
   description, even if it might cause a rejection.
 - On fix rounds: respond to each finding with FIXED (commit) or DISAGREE
   (evidence). Don't comply with a finding you believe is wrong.
+- A protected path the sub-ticket declares is not an escalation: the
+  code reviewer lists the declared paths once for each head it reviews.
+  You may name them in your output, but not under ESCALATIONS. A
+  protected path still goes under ESCALATIONS when the sub-ticket does
+  not declare it, or when the change does something to it that the spec
+  does not describe.
 
 PR DESCRIPTION
 Sub-ticket: <link>
diff --git a/docs/prompts/07-verifier.md b/docs/prompts/07-verifier.md
index 1f95b6e..a54f138 100644
--- a/docs/prompts/07-verifier.md
+++ b/docs/prompts/07-verifier.md
@@ -30,6 +30,12 @@ RULES
 - Anti-Goodharting: your job is to find out whether the thing works, not
   whether the checklist is green. If every command passes but a probe
   shows the fix is special-cased to the test inputs, FAIL it.
+- A protected path the sub-ticket declares is not an escalation: the
+  code reviewer lists the declared paths once for each head it reviews.
+  You may name them in your output, but not under ESCALATIONS. A
+  protected path still goes under ESCALATIONS when the sub-ticket does
+  not declare it, or when the change does something to it that the spec
+  does not describe.
 
 OUTPUT
 Commit: <head SHA you verified>
diff --git a/factory/prompts/implementer.md b/factory/prompts/implementer.md
index 70d76e8..e8890a4 100644
--- a/factory/prompts/implementer.md
+++ b/factory/prompts/implementer.md
@@ -41,6 +41,12 @@ RULES
   description, even if it might cause a rejection.
 - On fix rounds: respond to each finding with FIXED (commit) or DISAGREE
   (evidence). Don't comply with a finding you believe is wrong.
+- A protected path the sub-ticket declares is not an escalation: the
+  code reviewer lists the declared paths once for each head it reviews.
+  You may name them in your output, but not under ESCALATIONS. A
+  protected path still goes under ESCALATIONS when the sub-ticket does
+  not declare it, or when the change does something to it that the spec
+  does not describe.
 
 PR DESCRIPTION
 Sub-ticket: <link>
diff --git a/factory/prompts/verifier.md b/factory/prompts/verifier.md
index b9f7855..b436283 100644
--- a/factory/prompts/verifier.md
+++ b/factory/prompts/verifier.md
@@ -31,6 +31,12 @@ RULES
 - Anti-Goodharting: your job is to find out whether the thing works, not
   whether the checklist is green. If every command passes but a probe
   shows the fix is special-cased to the test inputs, FAIL it.
+- A protected path the sub-ticket declares is not an escalation: the
+  code reviewer lists the declared paths once for each head it reviews.
+  You may name them in your output, but not under ESCALATIONS. A
+  protected path still goes under ESCALATIONS when the sub-ticket does
+  not declare it, or when the change does something to it that the spec
+  does not describe.
 
 OUTPUT
 Commit: <head SHA you verified>
