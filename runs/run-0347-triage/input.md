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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0347-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0347-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "#75 follow-up: decision lines that name no capability always reach the writer, critic and planner in full"
labels: "harness"
---
**Where:** `factory/compose.py`, the decision-log filter that #75 added (T-0036, merged `deedbb9`), and its current-truth requirement and docs.

**Problem:** #75 sends a decision line in full only when it was logged against this ticket, or when its text names a capability sent in full. A cross-cutting standing decision names no capability, so it reaches the spec writer, critic and planner only as a one-line entry in the per-ticket index. Examples: where code must live, or how a whole category of change is done. Writers and critics can then miss a rule every ticket must follow.

**Evidence:** the operator's replay acceptance of #75 (2026-10-09), on Nanobot T-0032 in a scratch store.
- The new writer put its new code in a new module, `nanobot/cron/session_sweep.py`.
- Standing decision T-0003 rules that module out: lionbot code goes through upstream's extension points first, and `nanobot/agent/lionbot.py` holds only plain helpers.
- The original writer, given the whole log, followed T-0003 (its D11), and the original critic confirmed it. The replay critic missed the conflict, because it did not get the decision in full either.
- Everything else held: writer input fell 518 KB → 162 KB on Nanobot and 187 KB → 100 KB on spec-factory, and the Nanobot writer's run fell from 18.4M to 8.6M tokens. Quality was the same on both tickets, and no capability conflict was missed.

**Proposed change:**
- A. A decision line whose text names no current-truth capability goes in full to every spec writer, critic and planner input, as before #75.
- B. A line that names one or more capabilities goes in full when one of them is sent in full, as #75 does. Otherwise it stays in the index.
- C. Lines logged against this ticket go in full, unchanged.
- D. Measure the decision part's size on both stores before and after, and record it.

**Then:** one runtime move ships #75 with this fix.

Operator decision 2026-10-09 ("Fix the filter first, then ship"); filed by the Green session.



Issue: https://github.com/danielphang/spec-factory/issues/78


## Answer 1

# T-0037 (#78): answer to triage's question

Option 2: drop #75's decision-log filter. The spec writer, critic and planner receive the whole decision log, `decisions.md`, in full, as before #75. The decision index and its `grep` instruction are removed. #75's capability half stays as built: the capabilities triage names in full, plus the capability index.

Why: no decision line in either store names a capability (0 of 254 on Nanobot, 0 of 108 here), so the filter kept nothing in full. A cross-cutting standing decision (T-0003, where lionbot code lives) reached the writer and critic only as an index line, and the replay's writer broke it. The whole log is the simplest correct behaviour. Estimated writer input after this change: Nanobot about 518 → 235 kB, spec-factory about 187 → 135 kB.

Standing: yes. Decisions reach these roles in full until a scoping scheme exists that cannot drop a cross-cutting rule. #54's product/implementation tagging is where that scheme belongs.

Operator's choice in the Green session, 2026-10-09.

## Your previous Triage output (the question you asked is answered above)

Type: bug

Title: Standing decisions that name no capability must reach the spec writer, critic and planner in full (#75 follow-up)

Summary:
Issue #75 cut what the spec writer, critic and planner receive each turn. A line in the decision log (`decisions.md`, one line per standing decision with its date and ticket id) now reaches them in full only if it was logged against their ticket or names a capability they get in full. A capability is one current-truth spec, `openspec/specs/<name>/spec.md`. Every other line is reduced to one entry per ticket in a "decision index". A cross-cutting decision names no capability, so the writer and critic can miss a rule that every ticket must follow. That happened in the operator's replay of #75. The requester wants decision lines that name no capability sent in full again (their A). Lines that name a capability keep #75's rule (B), and the ticket's own lines stay in full (C). They also want the size of the decision part measured on both stores, before and after, and recorded (D). #75 and this fix then ship together in one runtime move.

Evidence:
- Requester: in the replay of #75 on Nanobot ticket T-0032, the new writer put its code in a new module, `nanobot/cron/session_sweep.py`. Standing decision T-0003 rules that out. The original writer, given the whole log, followed T-0003, and the original critic confirmed it. The replay critic missed the conflict.
- `.factory/answers/T-0036-acceptance-2026-10-09.md` records the replay. Writer input fell from 518 to 162 kB on Nanobot and from 187 to 100 kB on spec-factory, and quality was the same on both tickets. It records one miss: T-0003 "names no capability and was filtered into the index". It records the operator's choice: "Fix the filter first, then ship". The follow-up "sends every decision line that names no capability in full".
- I confirmed T-0003 names no capability. It is line 5 of `~/dev/nanobot-upstream/.factory/store/decisions.md`: "Where lionbot code lives: lionbot behaviours attach through upstream's extension points first …; `nanobot/agent/lionbot.py` holds only plain helpers …". None of the 23 Nanobot capability names appears in it.
- The filter is `add_decisions` in `factory/compose.py` (lines 226–261). A line goes in full when `f[1] == tid` or when its text matches one of the selected capability names as a whole word. Otherwise it goes into the index (lines 239–244).
- New finding, measured with the same whole-word match against every current-truth capability (not only the selected ones), and checked again with a plain `grep -c <name>` for each capability:

  | Store | Decision lines | Lines that name any capability | Size of the log |
  |---|---|---|---|
  | Nanobot (`~/dev/nanobot-upstream/.factory/store`) | 254 | 0 | 76,342 bytes |
  | spec-factory (`~/dev/spec-factory/.factory/store`) | 108 | 0 | 35,747 bytes |

  No line in either log names a capability. Decisions cite tickets and code paths, not spec names. So, with today's logs, A as written sends every line in full to every writer, critic and planner. The decision index is then always empty, and B's capability rule picks out nothing. On the decision part, this is the same as removing #75's filter. It restores about 76 kB per input on Nanobot and about 36 kB on spec-factory. By a rough sum, Nanobot writer input rises from 162 kB to about 238 kB, still about 54% below the 518 kB before #75. That figure is my estimate, not a measurement; D measures the real one.
- Current truth already states #75's rule. The requirement "The spec writer, critic and planner receive in full only the decisions of their ticket and its capabilities, and a decision index for the rest" is in `.factory/store/openspec/specs/role-inputs/spec.md` (lines 53–59). Its scenario expects `other=0` for `OTHER-LINE logs rotate weekly.`, a line that names no capability. Under A, that line goes in full.

Assumptions:
- (Inference) The fix changes the existing role-inputs requirement and its scenario rather than adding a new one beside them. The `OTHER-LINE` expectation flips from `other=0` to `other=1`, and the requirement's title and SHALL text change with it.
- (Inference) The design doc paragraph (`docs/design.md` line 94) and the README's spec writer, critic and planner rows (`README.md` lines 85–87) describe #75's rule. They change in the same ticket, with a changelog entry, as the briefing requires.
- (Inference) "Record it" in D means a measurement in the spec's Evidence or the PR description, not a new file or a new harness command.
- (Inference) A line with no date and ticket id keeps its current treatment: it is always sent in full.
- Suggested priority: p1, because #75 is held from the runtime until this fix merges. This is a suggestion; priority is the operator's call.

Question for human:
No line in either store's decision log names a capability (0 of 254 on Nanobot, 0 of 108 on spec-factory). So the rule you chose ("send every decision line that names no capability in full") sends the whole log to the spec writer, critic and planner on every ticket today. That is about 76 kB per input on Nanobot and 36 kB on spec-factory, as before #75. Capability specs stay filtered as #75 built them. Which do you want?
1. Build A–D as written. Today's behaviour is the whole log in full. The capability rule (B) only starts to filter if later decisions name capabilities. This matches your recorded choice and fixes the T-0003 miss. (Suggested.)
2. Drop the decision filter and send the whole log, as before #75. The result is the same as option 1 today, with less code and no decision index. Only the capability-spec half of #75 ships.
3. Keep the filter and mark cross-cutting decisions explicitly. For example, a "standing for every ticket" flag on `factory decision add`, set on T-0003 and the others like it. Only marked lines, the ticket's own lines and lines naming its capabilities go in full. This keeps more of #75's savings, but it needs a new flag and someone to go back and mark the existing logs, so #75 ships later.
Is the answer a standing decision that later tickets must follow, for example on how decisions are scoped in any role input?

STATUS: NEEDS-HUMAN
CONFIDENCE: high. The duplicate search found only this ticket (T-0037 is #78). I measured the zero-match finding on both stores and checked it a second way.
ESCALATIONS: none
