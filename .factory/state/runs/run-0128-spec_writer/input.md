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
  `harness.lock`, and closed records (`answers/`, `green-pilot/`). Its live store is still
  `intake/state/` until an operator step moves it.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3`), is instance A: it
still runs its own in-tree copy of the harness, from which this repo's harness was imported. Read
it only to observe what a fix does there today; never write there, and never copy its test names,
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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0128-spec_writer/output.md`

## Ticket (Triage output)

Type: feature

Title: Coding standard: add `docs/coding.md`, the coding twin of `docs/writing.md`, point the implementer and code reviewer prompts to it, and name the `factory:` marker ledger in the retro's input

Summary:
The factory's coding roles have no rule against over-building. The implementer (the role that writes the code for one sub-ticket) is told to make "the smallest change that makes them pass for the right reason" and nothing about how to find it. The code reviewer's last check, "Maintainability, only where it will cause real problems", names no kind of finding. The requester wants one new page, `docs/coding.md`, in the format of the writing standard `docs/writing.md`. Every rule there can be checked in your own output, has a before/after, and names its code-design principle. The page opens with a precedence rule (a target repo's own instructions win where they disagree), and its rules are:
- reuse before writing, with a check order (DRY);
- grep every caller and fix the shared function once (single responsibility, root cause over symptom);
- a `factory:` comment on every deliberate shortcut, naming its limit and when to upgrade it (technical-debt bookkeeping);
- the reviewer's finding tags `reuse:`, `stdlib:`, `native:`, `yagni:` and `delete:`;
- one name per concept, from spec to code (ubiquitous language).
The implementer and code reviewer prompts each get one line pointing to the page. The spec-stage rule (cut any part the ticket does not need) stays in the spec writer's prompt. Per the operator's answer, part E ships as text only. The retro is the role that proposes prompt changes from pipeline outcomes. The design doc's retro INPUT, its Routing table Retro row and the build spec name the `factory:` marker ledger as part of the retro's input. The ledger is a harness-made list of every `factory:` comment. The code that produces it waits for the ticket that builds the retro.

Evidence:
- The governing text is the operator's rescope comment on #20 (`gh issue view 20 --comments`), 2026-10-03: "the deliverable is `docs/coding.md`, the coding twin of `docs/writing.md`, not five edits scattered through the role prompts"; "the implementer and reviewer prompts get one pointer line to `docs/coding.md`, as the writing standard did. The retro's marker ledger (E) is unchanged."
- Answer 1 (operator default, 2026-10-03), option (b): "Ship E's text and defer its code. The design doc's retro INPUT and Retro row, and the build spec, name the `factory:` marker ledger as intended design. Building the ledger producer waits for the ticket that builds the retro." The same answer says to use the post-#19 paths, `docs/design.md` and `docs/prompts/0N-….md`.
- `docs/coding.md` does not exist (`ls docs/coding.md`: No such file or directory). `docs/writing.md` has 131 lines (`wc -l`). Its intro says each rule is checkable in your own output, with an example and its rewrite, and a `Code counterpart:` line where a principle fits. That is the format the request names.
- The text the old proposal targeted is still present:
  - implementer step 4: `docs/design.md:493` and `docs/prompts/05-implementer.md:10`, "Make the smallest change that makes them pass for the right reason."
  - reviewer check 7: `docs/design.md:555` and `docs/prompts/06-code-reviewer.md:21`, "Maintainability, only where it will cause real problems. Not style."
- Here is how the writing standard is wired, the model for "as the writing standard did". The preamble, the text that opens every role's prompt, names it through a `{writing standard}` placeholder (`docs/prompts/00-preamble.md:53`). The harness fills that placeholder with the absolute path of the runtime checkout's `docs/writing.md` (`factory/instance.py:163-166`). The build spec documents this (`dev/build-harness.spec.md:158`).
- Where E's text goes:
  - the retro prompt's INPUT block: `docs/design.md:640`, copied in `docs/prompts/08-retro.md`;
  - the Routing table's Retro row: `docs/design.md:127`, "Full outputs behind every outcome signal since the last retro (piece 10), …";
  - the build spec's retro input composer, `factory retro-input`: `dev/build-harness.spec.md:323`, and its acceptance item 66 at line 435.
- No retro is built in this harness: `factory/workflows/` holds only `build.js` and `intake.js`. So the ledger producer has nothing to feed yet, which is the reason the operator deferred it.
- Sequencing is met. #19 is closed. #26's writing rules 9–12 are on `main` (`fcc8756 Merge factory/T-0014.1: Add rules 9–12 and code counterpart lines to the writing standard`). Writing rule 9 already cites ubiquitous language (Evans, DDD), so the new name rule can cite the same principle.
- The precedence example is real: `~/dev/nanobot/.agent/design.md:15` is the heading "Prefer duplication over premature abstraction".
- No harness fix exists on the Nanobot side, as the request says ("none"). Checked in the previous pass: green's `factory/` contains no `coding.md`, `grep every caller` or `reuse:` text.
- No duplicate exists. `dev/issues.md:27` maps #20 to intake ticket T-0015 and no other ticket. #15 (the simplifier role) is closed and superseded by #20 (`dev/issues.md:22`).

Assumptions (the triage agent's inferences; the request does not state them):
- The pointer line takes the writing standard's form: a new placeholder, filled by the harness with the runtime checkout's `docs/coding.md`. That needs a small change in `factory/instance.py`, under `factory/**`, a protected harness path. The edited prompt blocks are re-copied into `docs/prompts/`, a protected generated path. The spec's Risk section must declare both, and the build spec line that lists the placeholders (`dev/build-harness.spec.md:158`) changes with them.
- Part C's reviewer rules move into `docs/coding.md`: the tags, their severities (`reuse:` blocks the merge; the others ride with an approval as should-fix) and the closing `net: -N lines possible` or `Lean already.` line. The reviewer prompt gets only the pointer line. Whether check 7's "Maintainability, only where…" wording is replaced or kept beside the pointer is a decision the spec writer should state under Decisions. The rescope's "not five edits scattered through the role prompts" suggests the pointer replaces the check's body.
- Part D's spec critic probe ("a part no acceptance item needs is a finding", rubric 3 at `docs/design.md:379`) is not mentioned in the rescope, so it stands with the spec writer rule. The spec writer may cut it, but should then say so under Decisions.
- `README.md` is the current-state page and lists `docs/writing.md` in its files table (`README.md:349`). Adding `docs/coding.md` adds a path, so by the briefing's rule the README gains a row in the same ticket.
- The design doc change carries its own changelog entry in `docs/changelog.md`, which credits ponytail (MIT) for the check order and the tag vocabulary, as the original body's "Source read" line says.
- Suggested priority (a suggestion; priority is the human's call): p1. The operator wants it landed before the Nanobot v3.5 driver, the session running the Nanobot re-port, starts intake.

Reason: n/a (ACCEPT). The one open decision, what to do with part E, is answered: option (b).

Out-of-scope observations:
- #26 still shows as OPEN on GitHub, though its change is merged (`fcc8756`). `b33e593` notes it as "merged and awaiting acceptance", which explains the open state.

STATUS: ACCEPT
CONFIDENCE: high. The deliverable, the wiring and part E's scope are all set by the operator's rescope and Answer 1, and every path cited was checked on this checkout.
ESCALATIONS: none

## Request (raw)

---
title: "Coding standard: docs/coding.md, the coding twin of docs/writing.md (rescoped #20)"
labels: "design-doc"
---
**Rescope (operator, 2026-10-03; the newest comment on #20 below governs where it differs from the original body):**

Rescoped (operator, 2026-10-03): **the deliverable is `docs/coding.md`, the coding twin of `docs/writing.md`**, not five edits scattered through the role prompts. #19, the dependency this issue waited on, is closed.

- **Content:** parts A–E become rules in `docs/coding.md`, in `docs/writing.md`'s format: each rule checkable in your own output, each with a before/after, each naming its code-design principle. Mapping to start from: reuse before writing (A's check order) → DRY; grep every caller and fix the shared function once (B) → single responsibility, root cause over symptom; the `factory:` marker (B) → explicit technical-debt bookkeeping; reviewer tags (C) → `reuse:` DRY, `stdlib:`/`native:` don't reinvent, `yagni:` YAGNI, `delete:` dead-code removal; spec-stage YAGNI (D) stays in the spec writer's rules.
- **Add: one name per concept, spec to code.** The names a spec defines (its Problem section, and the README's terms table for the factory itself) are the identifiers the code uses. Ubiquitous language (Evans, DDD), the same principle as #26's writing rule; the two documents cite the same principles.
- **Precedence, stated first in the file:** a target repo's own instructions win where they disagree. Example: nanobot's `.agent/design.md` says "Prefer duplication over premature abstraction", which overrides DRY there.
- **Wiring:** the implementer and reviewer prompts get one pointer line to `docs/coding.md`, as the writing standard did. The retro's marker ledger (E) is unchanged.
- **Sequencing:** after #26, so both files land with one shared principle vocabulary. Both land before the nanobot v3.5 driver proceeds with intake.

---

**Original issue body (#20):**

**Depends on:** #19 (repo layout). This ticket edits the prompt blocks in the design doc, and #19 decides where those blocks live and how `prompts/` is rendered from them; writing this spec against the pre-#19 tree would land it on paths that move.

**Where:** `docs/spec-factory.md` §5 Implementer (PROCESS step 4, RULES, PR DESCRIPTION), §6 Code reviewer (CHECK item 7, OUTPUT Findings line), §2 Spec writer (RULES), §3 Spec critic (rubric 3), §8 Retro (INPUT), and the Routing table's Retro row ("Receives"); the rendered copies under `prompts/` (today `prompts/02-…`, `03-…`, `05-…`, `06-…`, `08-…`; green `factory/prompts/{spec_writer,critic,implementer,reviewer}.md`).

**Problem, for the gate:** the factory's roles have no instruction about over-building. The implementer is told to make "the smallest change that makes the tests pass for the right reason" and nothing about how to find it; the reviewer's last check is "maintainability, only where it will cause real problems", which names no shape of finding, so a reviewer either pads or says nothing. Both are where a coding agent's known bias (building more than the ticket needs: a new helper beside an existing one, a dependency for a stdlib call, an interface with one implementation) goes unchecked. Who it hurts: the operator, who reads bigger diffs at the gate and later owns the duplicate code; and the retro, which has no record of the shortcuts an implementer took deliberately.

**What happened (2026-10-03, review of DietrichGebert/ponytail, MIT, 152k stars):** ponytail is a ~1,100-word system prompt that gives a coding agent a seven-rung check order before writing code (does it need to exist → already in this codebase → stdlib → native platform → installed dependency → one line → minimum code), a set of guardrails it may never cut (trust-boundary validation, data-loss handling, security, accessibility, one runnable check per non-trivial change), and an output discipline. Three of its measured findings transfer to the factory:

1. **Wording that moves behaviour is operational, not prose.** Their comprehension benchmark (`benchmarks/results/2026-06-22-issue-245-217-comprehension.md`, a seeded `bank.py` where `transfer()` and `withdraw()` share `_debit()` and the bug report names only transfers): "trace the flow end to end" scored 0/3 on Opus; *"grep every caller of the function you touch; fix the shared function once"* scored 6/6 on Sonnet 4.6 and Opus 4.8, baseline 1/6. Haiku 4.5 fails both arms (0/6): the multi-step instruction is a model ceiling.
2. **The win is on open-ended work, near zero on surgical work.** Their agentic run (`2026-06-18-agentic.md`: headless Claude Code on a pinned real repo, `git diff` added lines, n=4, Haiku 4.5, a terse-prose control arm and a seven-word "YAGNI + one-liners" arm): −54% LOC mean across 12 feature tickets, 94% where the agent reaches for a component instead of a native input, ~0 where the code is already minimal; the bare one-liner prompt dropped a safety guard (95%), ponytail did not (100%).
3. **A deferral marker makes shortcuts greppable.** Every deliberate simplification with a known ceiling carries a `ponytail:` comment naming the ceiling and the upgrade trigger; a one-shot skill greps them into a ledger and flags markers with no trigger (`skills/ponytail-debt/SKILL.md`).

The factory already holds what ponytail spent four months adding (anti-Goodharting rules, "understand before you cut", the guardrail list in the preamble), so the borrowings are five narrow edits. Finding 2 is why none of them adds a role: factory sub-tickets are surgical by construction (lettered parts, runnable acceptance), the open-ended decision sits at the spec stage.

**Why it matters:** a reviewer with a named finding shape catches duplication and dead abstraction on every PR for the cost of one prompt line; an implementer told how to find the smallest diff (callers first) ships root-cause fixes instead of symptom patches; a marker convention gives the retro the deferral record the Decisions log does not carry at code level.

**Proposed change (one spec, one PR after #19):**

A. **Implementer, PROCESS step 4.** After "Make the smallest change that makes them pass for the right reason", one check order: *before writing, in this order, take the first rung that holds: a helper, util, type or pattern already in this repo → the standard library → a native platform feature (a DB constraint over app code) → a dependency already installed → one line → the minimum code that works.* Rung 1 of ponytail's ladder ("does this need to exist") is deliberately not here; it belongs to the spec stage (D).
B. **Implementer, RULES.** Add: *A ticket names a symptom. Before you edit, grep every caller of the function you are about to touch; one guard in the shared function is a smaller diff than one per caller, and patching only the named path leaves a sibling caller broken.* Add: *A deliberate simplification with a known ceiling (a global lock, an O(n²) scan, a naive heuristic) carries a `factory:` comment naming the ceiling and the upgrade trigger (`# factory: global lock; per-account locks if throughput matters`).* PR DESCRIPTION gains a line under "Known gaps and uncertainties": *`factory:` markers added: list, or none.*
C. **Code reviewer, CHECK item 7.** Replace "Maintainability, only where it will cause real problems. Not style." with: *Over-building. Tag each finding: `reuse:` an equivalent helper, util, type or pattern already in this repo (name the path); `stdlib:` a hand-rolled thing the standard library ships (name the function); `native:` a dependency or code doing what the platform already does (name the feature); `yagni:` an abstraction with one implementation, config nobody sets, a layer with one caller; `delete:` dead code, unused flexibility, a speculative feature (nothing replaces it). `reuse:` is BLOCKING; the others ride with APPROVE as SHOULD-FIX. End the pass with `net: -N lines possible` or `Lean already.`* OUTPUT Findings line gains the optional tag: `[BLOCKING | SHOULD-FIX | NIT] <tag:> file:line: problem → consequence`. Severity and shape of checks 1–6 are unchanged. Ponytail's sixth tag, `shrink:` (same logic, fewer lines), is not adopted: it names no replacement and invites the padding the ANTI-GOODHARTING block forbids.
D. **Spec writer RULES and Spec critic rubric 3.** Writer: *Before Proposed change, the first question is whether each part needs to exist for the ticket's intent at all; a speculative part is cut and named in one line under Out of scope.* Critic rubric 3 (Scoped) gains a probe: *a part no acceptance item needs is a finding.*
E. **Retro INPUT and Routing table Retro row.** The retro receives the marker ledger: every `factory:` comment in the integration branch (`grep -rnE '(#|//|/\*) ?factory:'`, excluding vendored and build directories), one row per marker with file:line, ceiling and trigger, and a `no-trigger` flag where the comment names no upgrade trigger. The ledger is a piece-10 input (append-only log), produced by the harness, not by a role.

**Decisions:**
- No simplifier seat in the PR loop. The over-building lens runs as a reviewer check (C) on every PR; a repo-wide, ranked, report-only pass (ponytail-audit's shape) is what #15's simplifier should produce for the retro. A second author per sub-ticket would cost a round, a merge and a checker pass where the measured win is near zero.
- Marker word is `factory:`, not `ponytail:`; the convention is borrowed, the name is this system's.
- The persona ("lazy senior dev"), intensity modes, persistence hooks and the "at most three lines" output rule are not adopted: the preamble's "write for a skeptical human auditor" is the frame, the composer rebuilds each role's input so nothing needs re-injecting, and the PR description is the checkers' evidence.

**Verification the spec writer can make runnable:** `render --check` (post-#19) passes on the edited blocks; the four rendered prompt files contain the new text (grep for `grep every caller`, `factory:`, `reuse:`, `net: -`); the reviewer prompt no longer contains "Maintainability, only where"; a behaviour check in ponytail's shape, if the operator wants one: a seeded repo with a shared `_debit()` and a ticket naming one caller, run through `build.js` with and without B, scored on whether the shared function is guarded (their `benchmarks/agentic/` harness is the template; Opus or Sonnet, not Haiku).

**Out of scope:** the verifier prompt; the routing table beyond the Retro row; the preamble; any new role; #15's audit pass itself (this ticket gives it its tag vocabulary).

**Risk, protected and guardrail paths:** the role prompts are guardrail paths (preamble GUARDRAIL PATHS: "agent prompts") and `prompts/**` is `generated` on instance B; this ticket changes prompt wording on purpose and declares it. No protected path on green until the paired #19 ticket moves the prompts; after it, the rendered copies move with the blocks.

**Sequencing:** after #19 lands on instance B (the blocks' home and the render path are #19's). Independent of the #16/#18 pilot.

**Source read:** DietrichGebert/ponytail at `c982cd4` (2026-10-03): `skills/ponytail/SKILL.md` (120 lines, 1,079 words), `skills/ponytail-review/SKILL.md`, `skills/ponytail-debt/SKILL.md`, `AGENTS.md`, `hooks/*.js`, `benchmarks/README.md`, `benchmarks/results/2026-06-18-agentic.md`, `benchmarks/results/2026-06-22-issue-245-217-comprehension.md`. MIT; the borrowed lines are reworded, and the ladder and tag vocabulary are credited in the design doc's changelog entry.

**Fix as implemented on the Nanobot side:** none.



## Answer 1

Operator default (taken by the Green session under the operator's standing rule: a recommended, reversible option is taken and reported), 2026-10-03: option (b).

Ship E's text and defer its code. The design doc's retro INPUT and Retro row, and the build spec, name the `factory:` marker ledger as intended design. Building the ledger producer waits for the ticket that builds the retro. `docs/coding.md` keeps the `factory:` marker rule so markers are greppable. The deliverable remains `docs/coding.md` plus the implementer and reviewer pointer lines, per the rescope. Use the post-#19 paths (`docs/design.md`, `docs/prompts/0N-….md`), not the original body's.
