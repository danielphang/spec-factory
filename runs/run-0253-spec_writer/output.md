=== proposal.md
## Problem

The operator often sees the same "protected path touched" notice three times for one commit. This adds about one item in five to the queue of things the operator must read, and none of the repeats says anything new.

Some terms first. A protected path is a repository path that needs a human's approval before a change to it merges. In this repo that covers the harness code and the generated prompt copies. Each approved spec declares, in its Risk section, which protected paths it will touch. A sub-ticket is one PR-sized piece of a spec, and it carries the part of that list it touches. Each commit a sub-ticket produces for review is called a head. Three agents handle every head:

| Role | What it does with a head |
|------|--------------------------|
| Implementer | writes it |
| Code reviewer | reviews the diff |
| Verifier | re-runs the acceptance checks and the test gates |

Each role ends its output with an ESCALATIONS list. The harness copies every item on that list into the escalation queue, the operator's list of things that need a human. Copying an item does not stop the pipeline.

Only the code reviewer's prompt asks it to list declared protected paths there. The implementer and the verifier list the same paths anyway, out of habit: no rule asks them to. A retro run on 2026-10-04 counted 26 such repeats among 139 queued items.

This change makes the code reviewer the only role that lists declared protected paths, once for each head it reviews. The implementer and verifier prompts each gain one rule: a declared protected path is not an escalation. These roles may mention it in their output, but not under ESCALATIONS. Every role still escalates a protected path that the sub-ticket does not declare, as it does today.

## Evidence

- The repeats are real. The store's event log (`.factory/state/log/2026-10.jsonl`, `escalation.queued` events) has several sub-tickets where all three roles list the same declared path. I extracted it with a short Python filter on the cited sub-tickets:
  - On T-0012.6 (a sub-ticket that moved files out of the protected `intake/` tree), implementer runs 0096 and 0099 queued "protected path `intake/**` (infra) is touched as the sub-ticket declares". Verifier runs 0097 and 0100 queued the same thing ("Protected path `intake/**` (infra) is touched exactly as the sub-ticket declares"). Reviewer runs 0095, 0098 and 0101 had already queued it for the same heads.
  - On T-0013.1 (a prompt and harness change), implementer run 0109 queued "Protected and guardrail paths touched. Each is declared…". Verifier run 0110 queued "Protected and guardrail paths were touched as declared…". Reviewer run 0111 queued "Protected and guardrail paths touched, every one declared…".
  - What this shows: the repeats name the same paths and the same declaration as the reviewer's item, so they add nothing.
- The figure. The retro proposal (`.factory/answers/retro-trial-2026-10-04/retro_with_efficiency.md`, proposal P5) gives "26 declared-path lists queued by the implementer (16) and the verifier (10) out of 139 queued items". I did not re-derive 26. The log's parser splits one ESCALATIONS block into several items, so an item count depends on how items are grouped. The triage count of items containing "protected" found implementer 7, verifier 5 and reviewer 27 across today's whole store.
- Why it happens. These lines are in the dev checkout at `0b1abad`:
  - The code reviewer's check 6 (`factory/prompts/reviewer.md:17-20`, the same text at `docs/design.md:595` and in `docs/prompts/06-code-reviewer.md`) says: "If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS".
  - The shared preamble (`factory/prompts/preamble.md:33-36`) asks every role to escalate only "a protected path the approved spec's Risk section does not declare".
  - `factory/prompts/implementer.md` and `factory/prompts/verifier.md` say nothing about protected paths.
  - What this shows: no rule tells the implementer or verifier to list declared paths, and no rule tells them not to.
- Today's prompts, as composed for a run. I used the fixture under "role-escalations" with the HOME wrapper. It started an implementer, a verifier and a reviewer run on a scratch target and searched each composed system prompt for the new rule.
  - On this checkout, every role printed `declared=0 notunder=0 undeclared=0`, which means no role's prompt has the rule.
  - On a scratch clone with the change in design part A applied and committed, the implementer and the verifier printed `declared=1 notunder=1 undeclared=1` and the reviewer still printed zeros. So the rule reaches exactly the two roles meant to get it.
- The harness suite on that prototype clone printed `265 passed`, and `git diff --check` exited 0. So the change breaks no existing test, including the test that keeps the implementer design block equal to its `docs/prompts/` copy.
- Dropping these items changes no decision the pipeline makes. The implementer's and verifier's ESCALATIONS items are only logged (`factory/cli.py:324-325`, in `run finish`). The build workflow never reads the ESCALATIONS list; the only escalation it routes on is the planner's `ESCALATE` status (`factory/workflows/build.js:207`). The local merge decision (`ticket_join`, `factory/cli.py:580`) merges on "ci PASS + APPROVE + VERIFIED" and reads neither the declaration nor any queued item.

## Root cause

- `factory/prompts/implementer.md` and `factory/prompts/verifier.md` have no rule about declared protected paths. Their design-doc blocks (`docs/design.md`, "## 5. Implementer" and "## 7. Verifier") and the generated copies (`docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md`) have none either. Agents fill that gap by repeating the code reviewer's list.
- A run's system prompt is the preamble followed by `factory/prompts/<role>.md`, composed in `run_start` (`factory/cli.py:228-230`). So a rule added to those files reaches every later implementer and verifier run, once the runtime is on a revision that has it.

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
- Acceptance checks the composed run prompts and the document copies. The request's own check (on the next build, one notice per head, from the reviewer) is kept as an operator step. Rejected: an acceptance item that waits for a real build. The verifier cannot run one, and how a model follows a prompt rule is not something a check on one commit can prove.

## Risk

- Blast radius: every implementer and verifier run after the runtime moves to a revision with this change, in every instance that accepts that revision. That includes instance A, the Nanobot fork, which runs from the same runtime. The only change is that fewer items reach the escalation queue. No routing, refusal or merge decision changes.
- After this change, the code reviewer's item is the only signal that a declared protected path is about to merge. A merge needs an `APPROVE` row from a finished reviewer run on that head (`ticket_join`, `factory/cli.py:580`), and that run's ESCALATIONS are queued when it finishes. So every merged head has had a reviewer run whose prompt asks for the list. If the reviewer leaves the list out, the implementer's and verifier's repeats no longer cover the gap. A reviewer run that is killed does not merge: the ticket parks, and a redispatch runs the reviewer again. Do not count on the merge gate here: the local merge reads no declaration (see Out of scope).
- Protected paths this change touches:
  - harness (`factory/**`): `factory/prompts/implementer.md` and `factory/prompts/verifier.md`.
  - generated (`docs/prompts/**`): `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`, each re-copied from its design block.
- Guardrail paths (agent prompts): the four prompt files above, plus the "## 5. Implementer" and "## 7. Verifier" blocks in `docs/design.md`.
- Also changed, not protected: `docs/changelog.md`.
- It touches no test file, nothing under `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml` or `uv.lock`, and nothing in `~/dev/nanobot-upstream` or `~/.nanobot/`.

## Operator steps

1. After merge, move the runtime to the merged revision and accept it in each instance (`--accept-harness <commit>`), as for any harness upgrade. Until then, runs use the old prompts.
2. On the next build that touches a declared protected path, read the escalation queue. Expect one declared-path item for each reviewed head, from the code reviewer. Expect none from an implementer or verifier run. To list the implementer and verifier items queued since the accept, from `~/dev/spec-factory` (replace `<accept time>` with the ISO time of the accept, e.g. `2026-10-05T09:00`):
   `grep '"escalation.queued"' .factory/state/log/*.jsonl | awk -F'"ts": "' -v S='<accept time>' '{split($2,a,"\""); if (a[1] >= S) print}' | grep -E '"run": "run-[0-9]+-(implementer|verifier)"' | grep -i 'protected'`
   A line that lists paths the sub-ticket declares means the rule did not take.
3. An undeclared protected path should still be queued by every role that sees it. You can check this only when one actually happens.

=== design.md
## Proposed change

The change is about 40 added lines, with no deletions and no code changes.

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
- Open it with "After issue #49 (2026-10-04)". Say the implementer and verifier received the same declared-path list as the code reviewer, and give the retro's count (26 of 139 queued items).
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

- Implementer and verifier run prompts carry the declared-path rule → NEW. Today it prints `implementer declared=0 notunder=0 undeclared=0`, then `verifier declared=0 notunder=0 undeclared=0`: neither prompt has the rule. I ran this on this checkout at `0b1abad`. On a scratch clone with part A applied and committed, it printed the THEN lines.
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 → REGRESSION. It printed `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` both on this checkout and on the prototype clone.
- The design blocks and their copies carry the rule and stay in step → NEW. Today it prints `implementer copy=SAME rule=0 fill=unchanged`, then `verifier copy=SAME rule=0 fill=unchanged`: the copies agree, but none carries the rule. On the prototype clone it printed the THEN lines.
- The code reviewer and preamble copies do not change → REGRESSION. It prints `changed=0` on `main`, where the diff is empty, and on the prototype clone.
- The changelog records the declared-path rule in a contiguous entry → NEW. Today it prints `CONTIGUOUS`, then `0`: no numbered entry mentions `#49`.
- The declared-path change adds no whitespace errors → REGRESSION. `git diff --check` exited 0 on the prototype clone.

Every command was run from the repository root under the HOME wrapper from "Running code". The fixture went in this run's scratch directory through `TMPDIR`. The prototype clone was at `.factory/state/runs/run-0253-spec_writer/scratch/c`. Its harness suite printed `265 passed`. That run used a pytest temporary directory under `/tmp`, as the current-truth suite scenario does.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high. Every scenario was run on this checkout and on a prototype of the change, with the outputs above. The duplicates are visible in the store log for the runs cited. The one figure not re-derived (26 of 139) is the retro's and is cited as such.
ESCALATIONS: none
