## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0010-critic/output.md`

## Spec under review (v1)

## Problem

`plans/P0-intake-skeleton.md` Part A has the operator write `.claude/agents/factory-*.md` for six roles (Triage, Spec writer, Spec critic, Planner, clerk, stub). P0-2..P0-8 then dispatch those roles by agent type. The plan does not say that Claude Code only picks up agent files under some conditions:
- It loads `.claude/agents/` at session start.
- After that, it watches the directory only if the directory existed when the session started.
- It never watches the `.claude/agents/` of a directory added with `--add-dir`.

An operator who follows the plan in one session writes the files, then runs P0-2. Every `factory-*` agent type is then "not found". The plan has no check that would catch this before P0-2. The only way forward on 2026-10-01 was a fallback that runs every role as `general-purpose`. That fallback keeps each role's model but drops the per-role `tools:` fences that spec R6 relies on.

This affects:
- every operator who runs P0 from the plan, including the Nanobot rerun;
- anyone who reads a P0 run as evidence about the role definitions.

## Evidence

Commands were run from `~/dev/spec-factory` on `main` at `b2674dd`, unless noted.

- **The plan today.**
  - `sed -n 27p plans/P0-intake-skeleton.md` → the Part A row: "`.claude/agents/factory-*.md` for Triage, Spec writer, Spec critic, Planner, clerk, stub; …".
  - The Risk section (lines 63–68) has four bullets. None mentions agent registration, session start, restart or `--add-dir`: `awk '/^## Risk/,/^## Tests to change/' plans/P0-intake-skeleton.md | grep -c 'existed when the session started'` → `0`.
  - Acceptance (lines 38–49) is P0-1..P0-8. None checks registration: `awk '/^## Acceptance/,/^## What you measure/' plans/P0-intake-skeleton.md | grep -oE '^- P0-[0-9]+' | tr '\n' ' '` → `- P0-1 - P0-2 - P0-3 - P0-4 - P0-5 - P0-6 - P0-7 - P0-8`.
- **The failure (from the request, 2026-10-01).** `Agent(subagent_type: "factory-clerk")` → "Agent type 'factory-clerk' not found". The Workflow `agentType` resolves from the same registry. I did not reproduce the in-session failure myself. The reference harness comment quoted below records the same cause.
- **Claude Code docs** (https://code.claude.com/docs/en/sub-agents, fetched in this run):
  - "The watcher covers only directories that existed when the session started, so after creating a scope's first agent file in a new `agents` directory, restart to load it."
  - "Claude Code doesn't watch `.claude/agents/` inside directories added with `--add-dir` or `/add-dir`, so after adding or editing a subagent there, restart to load the change."
  - With `--add-dir`, its `.claude/agents/` is still loaded at session start.

  So the requester's "create `.claude/agents/` (even empty) before starting the session" works for a session started in the checkout. It does not work for a session that attaches the checkout with `--add-dir`.
- **Reference harness (read only)**: `~/dev/nanobot-upstream`, `feat/lionbot-v3` at `053a7bd5e`.
  - `factory/workflows/intake.js:24-26` says: "inlineRoles: the .claude/agents/factory-* definitions are not registered in this session (the directory did not exist at session start), so every role runs as general-purpose … Model per role is unchanged; tool fences are not."
  - Lines 49, 83 and 89 set `agentType: INLINE ? 'general-purpose' : …`.
  - `ls .claude/agents/` → `factory-clerk.md factory-planner.md factory-spec-critic.md factory-spec-writer.md factory-stub.md factory-triage.md`.
  - The harness works around the problem and does not fix it. Nothing in it makes the agents register.
- **Why the fallback matters.** `specs/build-harness.md:118` (R6) makes "Role agent definitions carry `tools:` allowlists" the permission fence. `:296` (I.4) says: "Tool restriction is the agent definition's `tools:` (R6)." A `general-purpose` agent carries no role `tools:` list.
- **A fresh session's agent list can be read black-box.** I checked this on Claude Code `2.1.286` in a scratch directory with `.claude/agents/factory-probe.md`. Running `claude -p --model haiku --max-turns 1 --output-format stream-json --verbose "reply ok"` prints a `{"type":"system","subtype":"init",…}` event. That event has an `agents` array: `"agents":["claude","Explore","factory-probe","general-purpose","Plan","statusline-setup"]`. The same command in a directory with no `.claude/agents/` lists `0` `factory-*` agents. `claude agents --help` → "Manage background agents". It does not list subagent definitions, so it cannot be used for this check.
- **The proposed P0-9 command works on both sides.** I took it verbatim from the patched plan (Acceptance item 5 below):
  - With six fixture agents it exits 0 (`PASS`).
  - With a fixture file that has no `description:` (so it does not register) it prints `< factory-stub` and exits 1.
  - Without `</dev/null`, `claude -p` warns "no stdin data received in 3s", so the command includes the redirect.
- **The proposed change works.** I applied it in a scratch clone (`git clone ~/dev/spec-factory`, branch off `main`): `git diff --stat` → `1 file changed, 3 insertions(+), 1 deletion(-)`. I ran every Acceptance item below on that branch and on `main`. Results are quoted with each item.
- **Renumbering would break references.** `grep -rnoE "P0-[0-9]+" docs specs plans prompts issues README.md` finds P0-2 and P0-5 cited outside the plan's own list: `issues/04_p0_agents_dir.md` and `issues/06_p05_grep_vs_inline_scripts.md` (5× P0-5). Inside the plan, line 67 cites "P0-2's `meta.yaml` check" and the metrics table cites "(P0-5)". So the new item gets the next free number and is placed by its position in the list.

## Root cause

`plans/P0-intake-skeleton.md` treats Part A (writing the agent files) and P0-2..P0-8 (dispatching to them) as one continuous session. It does not state the Claude Code precondition that links the two: the session that dispatches must start after `.claude/agents/` exists, or after the files exist when the checkout is attached with `--add-dir`. Nothing in the Risk list or the Acceptance list states or checks that precondition. Since nothing checks it, the failure first shows up mid-run as "Agent type … not found". It can also go unnoticed when a run falls back to `general-purpose` agents.

## Proposed change

One file changes: `plans/P0-intake-skeleton.md`. The tested diff is 3 insertions and 1 deletion. `docs/spec-factory.md`, `specs/build-harness.md` and `prompts/` do not change. The plan has no Changelog, so none is added.

**A. Acceptance preamble** (line 40). Replace the whole line with:
```text
Black-box, numbered P0-1.. so they don't collide with the spec's 1–84. Each is NEW; today every one fails with `factory: command not found` or "no such workflow", and P0-9 because no `.claude/agents/factory-*.md` file exists yet (its count is `0`).
```

**B. New acceptance item P0-9.** Insert this line directly after the P0-1 line (line 42) and before the P0-2 line. Do not renumber any existing item. The Evidence section explains why.
```text
- P0-9 (after Part A, before P0-2; numbered last so P0-2..P0-8 keep their numbers) A fresh session in the green checkout registers every Part A agent: `ls .claude/agents/factory-*.md | wc -l` → `6`; `diff <(sed -n 's/^name: //p' .claude/agents/factory-*.md | sort) <(claude -p --model haiku --max-turns 1 --output-format stream-json --verbose ok </dev/null | grep '"subtype":"init"' | grep -o '"agents":\[[^]]*\]' | grep -oE '"factory-[^"]*"' | tr -d '"' | sort)` → no output, exit 0. Run P0-2..P0-8 in a session started after this check.
```
Notes on this item:
- It compares the files' own `name:` fields with what a fresh session registers. It does not hard-code six names. The documents disagree on the critic's file name: `specs/build-harness.md` says `factory-critic`, while the reference harness has `factory-spec-critic`. That choice is not this ticket's to make.
- The `ls … | wc -l` → `6` part stops the diff from passing on two empty lists before Part A exists.

**C. New Risk bullet.** Insert this line directly after the bullet ``- Workflow under `claude -p` unverified; fallback is an interactive session (same script).`` (line 66). Change no existing bullet.
```text
- Role agents may not register mid-session. Claude Code loads `.claude/agents/` when a session starts and afterwards watches it only if the directory existed then, and it never watches the one inside a directory added with `--add-dir`; a session started before Part A's files were written may not see them (2026-10-01: `Agent(subagent_type: "factory-clerk")` → "Agent type 'factory-clerk' not found"). Start the session that runs P0-2..P0-8 in the green checkout after Part A's agent files exist, or restart it after writing them; P0-9 checks this before P0-2. Running every role as `general-purpose` with its prompt read from a file keeps each role's model but drops the `tools:` fences of R6, so R6 is not in force on such a run.
```
The rule says "start after the files exist, or restart". It does not say "create the directory first", which was the requester's suggestion. The reason: the stronger rule also covers `--add-dir`, where the directory is never watched, and it is what P0-9 checks.

## Acceptance

Run every command as written from `~/dev/spec-factory`. On the base, `main...HEAD` is empty. Item 5 needs a logged-in `claude` on `PATH` (checked on `2.1.286`) and makes one Haiku call.

1. `awk '/^## Risk/,/^## Tests to change/' plans/P0-intake-skeleton.md | grep -F 'only if the directory existed then' | grep -F -- '--add-dir' | grep -F 'restart' | grep -c 'R6'` → `1` [NEW. Today `0`. No Risk bullet mentions registration, `--add-dir`, restart or R6.]
2. `awk '/^## Acceptance/,/^## What you measure/' plans/P0-intake-skeleton.md | grep -oE '^- P0-[0-9]+' | tr '\n' ' '` → `- P0-1 - P0-9 - P0-2 - P0-3 - P0-4 - P0-5 - P0-6 - P0-7 - P0-8 ` [NEW. Today `- P0-1 - P0-2 - P0-3 - P0-4 - P0-5 - P0-6 - P0-7 - P0-8 `. There is no P0-9, and nothing comes before P0-2.]
3. `` awk '/^## Acceptance/,/^## What you measure/' plans/P0-intake-skeleton.md | grep -E '^- P0-9 ' | grep -F '"subtype":"init"' | grep -F "sed -n 's/^name: //p' .claude/agents/factory-*.md" | grep -c '→ `6`' `` → `1` [NEW. Today `0`.]
4. `` grep -c 'and P0-9 because no `.claude/agents/factory-\*.md` file exists yet' plans/P0-intake-skeleton.md `` → `1` [NEW. Today `0`. Line 40 names only `factory: command not found` and "no such workflow".]
5. `c=$(awk -F'\140' '/^- P0-9 /{print $6}' plans/P0-intake-skeleton.md); d=$(mktemp -d); mkdir -p $d/.claude/agents; for r in triage spec-writer spec-critic planner clerk stub; do printf -- '---\nname: factory-%s\ndescription: fixture\nmodel: haiku\ntools: Read\n---\nfixture\n' $r > $d/.claude/agents/factory-$r.md; done; [ -n "$c" ] && (cd $d && bash -c "$c") && echo PASS || echo FAIL` → `PASS` [NEW. Today `FAIL`: there is no P0-9 line, so `$c` is empty. This runs the plan's own P0-9 command, verbatim, against six fixture agents in a fresh directory.]
6. `git diff main...HEAD -- plans/P0-intake-skeleton.md | grep -E '^-' | grep -v '^--- ' | grep -v '^-Black-box, numbered P0-1\.\.'` → no output, exit 1 [REGRESSION. The only line removed or edited is the line-40 preamble. P0-1..P0-8 and the four existing Risk bullets are unchanged. Today no output, exit 1.]
7. `git diff --name-only main...HEAD -- docs specs prompts plans issues README.md | grep -vx 'plans/P0-intake-skeleton.md'` → no output, exit 1 [REGRESSION. The design doc, the spec, `prompts/` and the issue drafts are untouched. Today no output, exit 1.]
8. `git diff --check main...HEAD` → no output, exit 0 [REGRESSION. Today exit 0.]

Observed: on the patched scratch clone, items 1–8 gave exactly the results above. On `main`, items 1–5 gave the "today" values, and 6–8 passed.

## Tests to change

none. This repo has no test suite, and P0-1..P0-8 are left as they are.

## Out of scope

- `specs/build-harness.md` and `plans/build-harness.md`. BH-4 creates `.claude/agents/` (spec layout `:136-139`) and has the same exposure. Extending this fix there was not asked for. See the observations below.
- `docs/spec-factory.md` and every `prompts/` file.
- Renumbering any P0 item, and the "spec's 1–84" count on line 40.
- Whether a P0 run that used the `general-purpose` fallback counts as passing P0-2..P0-8. That is a human call. The Risk bullet only states the consequence.
- The agents' `tools:` contents and the critic's file name (`factory-critic` vs `factory-spec-critic`).
- `issues/04_p0_agents_dir.md`. Under `issues/README.md` it is deleted when the issue is filed, not by this change.
- Anything under `~/dev/nanobot-upstream` or `~/.nanobot`.

## Open questions

none.

## Risk

The change touches one plan document, and the diff is 4 lines. The new P0-9 adds one paid Haiku call to a P0 run, and it requires `claude -p` with `--output-format stream-json --verbose`. Both were checked on `2.1.286`. If a later Claude Code version drops `agents` from the `init` event, P0-9 fails loudly: the diff shows every expected name as missing. It does not pass silently.

Protected paths touched:
- `intake/**`: only this run's own `output.md`, which the harness names as the output file.
- `prompts/**`, `~/dev/nanobot-upstream/**` (read only, via `git`/`ls`/`sed`), `~/.nanobot/**`: none.

Guardrail paths: none. `plans/` is not a guardrail path.

## Out-of-scope observations

- `specs/build-harness.md` (layout `:136-139`, part A/BH-4) and `plans/build-harness.md` BH-4 create `.claude/agents/` with no registration precondition. The full build has the same trap. A follow-up ticket could add the same Risk line and a P0-9-style item there.
- Naming disagreement:
  - `specs/build-harness.md` item 54 greps `.claude/agents/factory-critic.md`.
  - The reference harness has `factory-spec-critic.md`.
  - The reference gives Triage, Spec writer, Spec critic and Planner `tools: Read, Grep, Glob, Bash, Write`, but R6 says read-only authors and checkers get "no Edit/Write". Triage raised this too.
- My scratch probe also showed that the `init` event lists the built-in agent `claude`. That does not affect P0-9, which filters on `factory-`.
- On the Nanobot side, this needs no code fix. The `inlineRoles` comment in `factory/workflows/intake.js` already records the cause. The plan rule makes the fallback unnecessary when P0 is followed from a fresh session.
