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

