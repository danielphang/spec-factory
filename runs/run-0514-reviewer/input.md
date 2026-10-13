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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0514-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0514-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0514-reviewer/wt` (branch `factory/T-0048.1`, base `7231670f2303856db8c1ed709a402be43c251754`, head `08ad85edf30076259c47b7fc816976f45270e805`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0048.1

T-0048.1 / Shrink the maintained documents: freeze the three `dev/` build documents as history, fix README's stale "not yet run" claims, describe each mechanism once in README, move history to the changelog, and update the `harness-docs` current truth to match
Depends on: none
Parallel-safe: yes

Parent: T-0048, approved spec v1. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- The changelog records the change in order
- The README describes the new resolve verbs
- The README says relative paths resolve from the caller's directory
- The changelog records the guard in one entry
- The design doc names the marker and the run-directory rule
- README tells the operator how to write during a run, first thing under Where a human decides
- README says the final verifier run is listed as in flight
- README no longer says the factory's capabilities never entered the spec store
- The design doc names the store branch and the path rule
- The changelog records the store branch in one contiguous entry
- The README describes the store branch and the move
- The design doc describes the check
- The changelog records issue 40's change without a numbering gap
- README describes the sibling tests check and its ruling
- The design blocks and their copies carry the rule and stay in step
- The changelog records the declared-path rule in a contiguous entry
- The changelog records the small-change lane in one entry
- The design doc and README describe both skips
- Every reviewer copy carries the rule and the copies stay in step
- The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
- The design doc states the EMPTY-OUTPUT rule, its rows and its park
- README drops the budget park and describes the empty-output retry
- The changelog records issue 41 without a numbering gap
- Principle 2 names the critic's no-suite rule and no longer its build ban
- The changelog records the revert in one entry
- The Spiking section allows a small scratch check and records the replay
- The prompt copies, design, README and changelog name the capability index
- The design, README and changelog describe the whole decision log and no decision index
- The design doc, README and changelog record superseded plans
- The design doc drops the per-PR approval for protected paths
- The changelog records issue 57's change without a numbering gap
- README describes the protected-path check and the new resolve verb
- The changelog records the reading rules for the five roles in one entry
- The changelog records the change in one contiguous entry
- The design doc names the amend command, its intent flag, spec drift and the critic's new input
- README lists the amend command and the drift check
- The design doc, template and README name the sync and the dropped virtual environment
- The changelog records the environment sync in one entry
- The documents describe the driver
- The design doc, README and changelog record both changes
- The documents describe the driver's exemption and its same-ticket guard
- The documents record factory stats
- The README describes the model check
- The design doc names the waiting park reason
- The README names pytest-xdist and the waiting reason
- The changelog records issue 106 as entry 71, without a numbering gap
- The maintained documents pass git's whitespace check in full
- Each build document carries the header and is otherwise unchanged
- The briefing no longer asks a change to keep the build spec in step
- README no longer calls run features untried, and keeps the claims that are still true
- The Built rule asks for run status, and the design doc's date line points to the changelog
- Each Built entry is a short pointer, and each mechanism's detail has one home
- The glossary points to Where it runs and defines protected path once
- README keeps its issue references and drops the moved history, and the changelog records the move
- README is at most 1,110 lines
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v1, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0048/v1.md`

=== proposal.md
## Problem

The operator reads two documents at every spec gate, the human review where a spec is approved before any code is written: `README.md`, the page that says what the factory does today, and `docs/design.md`, the design it is built from. Both have grown, and parts of README are wrong. README explains several mechanisms two or three times. It says six features have "not yet run" on a real ticket when the stores' logs show they have. It keeps project history that belongs in `docs/changelog.md`, the numbered record of design changes. Three finished working documents under `dev/` describe a design the code never had, yet the briefing that every agent reads first asks each change to keep one of them, the build spec, in step with the design. So every ticket pays to edit a document nobody uses, and the operator reads more than the system needs, some of it false.

A second cost follows from the first. The factory keeps "current truth", one spec per capability holding the checks the system must keep passing; each check is a shell command with its expected output. The capability for the documents, `harness-docs`, has 37 requirements, and many of them check README, the design doc, the changelog and the build spec with `grep`. Some of those checks can only pass on the change that wrote them. A check that the changelog's last entry is a given issue's entry fails as soon as another entry follows it. On `main` today, 12 of its checks fail because a later change moved on: a newer changelog entry, a later prompt edit, a revised principle. Others check "this change touched no prompt file" against `main`, which fails on the first later change that does. A de-bloat of README has to edit those checks too, or it breaks them.

This change shrinks what the operator reads and makes what remains true. It freezes the three `dev/` build documents as history. It corrects README's false claims from the logs. It gives each mechanism one home in README, with a short pointer everywhere else. It moves history to the changelog. It rewrites the `harness-docs` checks so that each one keeps passing after later changes and still checks what it was written to check.

## Root cause

- README's "Update with the change" rule (README:1151-1154) has each ticket add a Built entry beside the how-to it updates. Nothing removes the older wording, so each mechanism collects a second and third description. Built entries also keep the "not yet run" status they had when they were written, and no later ticket re-reads it.
- `.factory/context.md:34-36` puts the build spec on every design change's checklist. That is why it had 16 commits after 2026-10-04 while describing a design the code left.
- `harness-docs` checks were written per ticket, as the acceptance of that ticket. Archive copies them into current truth unchanged (`docs/design.md:86-96`, the Spec store paragraph). Checks phrased "this change" therefore become checks on every later change: `tail -1` on the changelog, `git diff --name-only main...HEAD -- docs/prompts ...` counted as 0, `git diff --check main...HEAD`, and a fixed entry count.

## Out of scope

- The prompt blocks in `docs/design.md` (181-866) and its appendix (890-923), and the eight places that say a prompt change is hand-copied. Spec-factory issue #83 part C owns both. This change moves one of those sentences, from README's "Not built" list into its new "Not built" paragraph, without changing its words.
- README's `store migrate` runbook (640-698), which #83 part D owns. Its `factory store migrate`, `-ffdx` and "from before the move" stay, and current truth still checks them.
- `docs/north-star.md`, `docs/decided-against.md`, `docs/golden.md`, `docs/principles.md` and `docs/writing.md` are not edited. Only a `harness-docs` check about principle 2 changes.
- `dev/issues.md` stays the live issue index.
- The frozen documents' content: nothing in them is corrected to match the code.
- Harness code, tests, prompt files, workflow scripts and agent templates.
- README's diagrams, which #104 owns, and its section headings and order ("Headings are the contract", README:1163).
- `docs/design.md` beyond line 3 and the `factory stats` figures in line 70.
- The `harness-docs` requirements that check only prompt copies, role runs or `factory/gates.py` (12 of the 37). They read nothing this change edits, and the prototype run shows them unchanged.

## Open questions

none

## Decisions

- Part A freezes the three `dev/` build documents in place, with a header at line 3. Rejected: moving them to `dev/archive/`, which breaks the `Parent:` links in the plan and skeleton and every path cited in `decisions.md`, `dev/issues.md` and past answers.
- Standing: a frozen document is never edited again. Current truth checks that each one equals its text at `7231670` apart from the header.
- Part B keeps the tested-but-unfired features in the Built list and changes README's rule instead. The rule now says an entry appears once a feature is built and tested, and says whether it has run on a real ticket. Rejected: moving the three that are still unfired (tripwire, sibling-tests check, the drift check's sibling-merge exception) under "Where this can go". They are built, and that section is for intended work.
- The protected-path refusal is corrected to "has fired", against the request's "still true and kept". The log shows the refusal on T-0044.1 and the operator's `--accept-paths`.
- `docs/design.md:3` drops its date and points to the changelog, which dates every change. Rejected: bumping the date, which every later design change would also have to do.
- Part C homes:
  - The live-store fence lives under "Where a human decides".
  - The driver's own same-ticket guard lives in its how-to. The request asked to cut that paragraph to one line, but no other section describes the guard, so the paragraph keeps the guard and drops only the fence detail.
  - The final check's skip lives in "The build workflow, step by step".
  - The store branch lives in "How the factory uses git".
  - Other agent hosts live only in `docs/design.md`.
- "Not built" and "Where this can go":
  - "Where this can go" keeps the named intended work.
  - "Not built" becomes one paragraph of today's facts, with no bullet that repeats one there.
  - The bold name "Current truth for the factory itself" moves to "Where this can go", because current truth checks for that phrase.
- History moves to one new changelog entry, 72, for issue #101. "Related work and history" keeps every issue reference, as #23 asks. It also keeps its last sentence of current figures (tickets, sub-tickets, runtime commit), which the change re-derives.
- Standing, for the operator to confirm or strike at the gate: README gets a line budget of 1,110. A later change that needs more room raises it in its own spec. The request asked for a drop of at least 150 lines, but honest one-home cuts give about 90 (prototype: 1,101 lines). The budget is set at that result, with 9 lines of slack, rather than padding the cuts to reach 150.
- Part F rules, standing for later `harness-docs` scenarios:
  - A scenario finds a changelog entry by the words it opens with, "`<n>. After issue #<k> `", and checks that exactly one entry matches. It never uses the last line or an entry count.
  - A scenario does not check what one change left untouched against `main` or a fixed commit. The two requirements made only of such checks are removed.
  - Whitespace is checked once, over the maintained documents in full. The instance's gate command `git diff --check main...HEAD` (`.factory/instance.yaml:23`) still checks each change.
  - The `fill=` comparisons with `main` stay. They hold on every change that keeps the placeholders filled in the run copies, and a change to those is a change to the prompts.
  - Each check of the frozen build spec is dropped, with the clause that required it.
  - Principle 2's status clause is dropped, because the principle no longer has a status line.
- One sub-ticket. The prototype's diff is 331 lines, under the 400-line bound, and every part edits README, so parallel sub-tickets would collide. The spec names no seams, so the harness builds it whole. Rejected: the request's suggested split into A+F, B+E, C and D.

## Risk

Medium, from the number of string checks.

- A wrong README edit breaks a `harness-docs` check. The delta restates every requirement that reads README, the design doc, the changelog or `dev/`, so the verifier runs them all on the change. The remaining requirements read only prompt copies, role runs and `factory/gates.py`.
- `.factory/context.md` is the briefing every role reads first, so a bad edit there misdirects every later run at once. The edit is two sentences.

Protected paths: `.factory/context.md`

=== design.md
## Proposed change

Line numbers are on `main` at `7231670`. Where a check in the delta depends on exact words, the words are given here; elsewhere the wording is the implementer's, within the line targets. The prototype that met every check came to 1,101 README lines; the budget is 1,110.

**A. Freeze the three `dev/` build documents.**
1. In `dev/build-harness.spec.md`, `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md`, insert after line 2 (the blank line under the title) this line, then one blank line, and change nothing else in the files:
   `> **Frozen as history.** This document records how the harness was first specified and built, and parts of it describe a design the code never had. It is no longer kept in step with `docs/design.md` or the code, and no change updates it; `README.md` and `docs/design.md` describe the system.`
2. `.factory/context.md:9-11`: replace the `dev/` bullet with
   `` - `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the ``
   `  P0 walking skeleton, frozen as history from building the harness, which no change updates;`
   `.factory/context.md:34-36`: drop "`dev/build-harness.spec.md` consistent with the new text," so the sentence reads "A change to the design doc keeps its own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose block changed re-copied from it." After the edit the file names no `build-harness` path.
3. README:1111, the `dev/` row of "Where things live": `` | `dev/` | The issue index (`dev/issues.md`), kept live; and the build spec, its plan and the P0 walking skeleton, frozen as history from building the factory | ``

**B. Correct the stale claims.** Body text names no ticket ids ("Maintaining this page"); ids go in the changelog entry.
1. README:94-95: "A run that returns no output is run once more, then parks its ticket ("Empty output", under "What is built and what is not")." The retro sentence stays.
2. README:157-158: the one-sub-ticket path "has run on real tickets on both targets."
3. README:728-729: replace "The driver is tested, ... the tested route." with the file-tool limits sentence moved from the Built entry (C.2) and "It has taken real tickets through intake and the build on the chat-bot target."
4. README:821-823: drop "; this is tested but has not yet run on a real ticket" (the overlap figure goes in D).
5. README:948, 1000, 1016, 1025-1026: in the rewritten Built entries (C.5), the path skip "is recorded on a real sub-ticket", and the re-plan "has fired on a real ticket". The protected-path refusal "has fired on a real ticket, which the operator accepted with `--accept-paths`", and the driver "has taken real tickets through both on the chat-bot target". Keep "It is tested, and has not yet fired on a real ticket" in the tripwire and sibling-tests entries, the drift entry's "the sibling-merge exception is tested but has not yet run on a real ticket", and "Neither target sets it yet" in the effort entry.
6. README:1147-1150, the "Ground truth only above" rule: "A thing appears in the sections above only once it is built and tested, and its entry says whether it has yet run on a real ticket." The rest of the bullet stays.
7. `docs/design.md:3`: replace `2026-09-30 · Daniel` with `Daniel · first written 2026-09-30; every change since is in `docs/changelog.md``.
8. README:9: the status date becomes the day of the change.

**C. One home per mechanism in README.**
1. Live-store fence (home: "Where a human decides", 834-860, unchanged).
   - README:755-764, in the driver how-to, becomes at most 6 lines. It says the fence exempts the driver because it is the dispatcher, and that the driver marks its own store calls and never its role processes'. It keeps the same-ticket guard: it refuses with exit 2 and nothing written while the ticket or a sub-ticket has a run in flight, or while `drive/<ticket>.yaml` shows another live driver; delete that file if the pid is not a driver; after a SIGKILL, clear runs as "Where a human decides" says. It drops the location rule ("refused like any write") and "even while runs of other tickets are in flight".
   - The Built entry (963-972) becomes at most 3 lines and names "Where a human decides".
2. Driver (home: "Driving a ticket from a shell with `factory drive`").
   - The Built entry (1017-1026) becomes at most 4 lines and names that section. Its file-tool limits sentence moves to the how-to (B.3).
   - "Running on another agent host" (1072-1095) becomes at most 6 non-blank lines, with no table. Keep the heading. Say what a host must offer, that only the pieces in "What depends on Claude Code" need a counterpart, that `factory drive` is that counterpart on Claude Code, and that the comparison with OpenAI Codex and Google Antigravity, untried, is in `docs/design.md`, "Running on another agent host".
3. Final check's skip (home: "The build workflow, step by step").
   - README:329-331 takes the full condition and its reason from 166-169: one sub-ticket, its text names every acceptance scenario, the integration branch has not moved since it merged, so its verifier already checked the same code.
   - 165-170 keeps one sentence pointing there. The phrase "has not moved since" appears once in README.
4. Store branch (home: "How the factory uses git", 505-507).
   - 375-379 becomes "The store is the target's record of every ticket, a git worktree of its own branch, the store branch `factory-store` ("How the factory uses git"). Two targets run on the runtime today: this repo and a chat-bot repo."
   - Drop the first sentence of 619-620 and the sentence at 828.
   - The Built entry (954-956) becomes 2 lines with that pointer. Joined into one line, README says "never moves the integration branch" once.
5. Built entries. Each keeps its bold name exactly, and ends with its status from B:
   - Build, local-only (939-948): at most 6 lines; keep the word `SKIPPED`; point to "How the factory uses git" and "Adopting the factory in a repo".
   - Spec store (949-951): 2 lines.
   - Tripwire on live files (957-962): at most 4 lines, citing `docs/design.md`, "Tripwire on live files".
   - Sibling tests check (973-978): at most 4 lines, citing `docs/design.md`, "Tests a sibling added".
   - Spec amendment and drift (979-993): at most 6 lines, citing `docs/design.md`, "Spec drift"; keep "factory spec amend", "Where a human decides" and "is not drift".
   - Re-plan after a re-spec (994-1000): at most 4 lines.
   - Empty output (1001-1009): at most 6 lines, citing `docs/design.md`; keep `ended its turn waiting on a background command`.
   - Protected paths at merge (1010-1016): at most 4 lines, naming "How the factory uses git" and "Where a human decides".
   - Per-role effort (1027-1030): unchanged.
   - Counting catch and cost, `factory stats` (1031-1037): at most 3 lines, naming "Counting what each role catches and costs"; drop the `factory/cost.py` history (D).
6. "Not built" (1039-1052) becomes one paragraph with no bullets. It says the items under "Where this can go" are named work, not built, and gives today's facts:
   - one machine and one identity do everything, which suits one operator and not a team;
   - "the role prompts in `docs/prompts/` are copied from the design doc by hand", in those words (out of scope: #83 part C);
   - no retro has run;
   - this page stands in for the capabilities no ticket has changed since the spec store was created;
   - the status page `factory report TICKET` is not built, and today you read the store's YAML.
   In "Where this can go", the bullet "**The factory described by itself.**" is renamed "**Current truth for the factory itself.**".
7. README:711-714: drop the sentence repeating what `inlineRoles` does, and point to "What depends on Claude Code".

**D. History to the changelog.**
1. Drop README:819-821 "On 2026-10-04 ... planners)." and README:1035-1036 "`factory/cost.py` now counts the same way; it used to count most calls about twice." The second is already changelog entry 70.
2. Drop "Both stores were made before ... `factory store migrate`." (377-379, under C.4), and "Both targets' stores were moved there with `factory store migrate`." (956). Keep 461-462, which says where each store is.
3. "Related work and history" (1120-1139): replace the narrative with the issue references it carries, every one of #16-#24, #28, #35, #42, #46, #47, #53, #55, #61, #65 and #70, each beside what it names. Then name the two targets (instances A and B), point to `docs/changelog.md` for how this page and the design came to be and to `dev/issues.md`, and keep the final sentence of figures, re-derived. Drop "First written 2026-10-03" and the 2026-10-04 notes.
4. README:1185-1186: drop "(today this caught two: ... on the wrong case)".
5. `docs/design.md:70`: replace everything after "`factory stats` prints the evidence a change to this table needs" up to "counted apart." with "; its first figures, from 2026-10-11, are in `docs/principles.md`, principle 4, and changelog entry 70."
6. `docs/changelog.md`: add entry 72 after entry 71 and before the closing "Declined:" line.
   - It opens with `72. After issue #101 (2026-10-11), `.
   - It records parts A to E, and the `harness-docs` rewrite (F) with its rules.
   - Its words include `frozen`, `build-harness.spec.md`, `context.md`, the moved figure `41 and 11`, `harness-docs` and `not yet`.
   - It names the corrected claims and the tickets that showed them: T-0032 to T-0051 for the one-sub-ticket path, T-0035 and T-0036 for the driver, T-0036.1 for the path skip, T-0031 for the re-plan and T-0044.1 for the protected-path refusal.

**E. Glossary.**
1. Terms rows 138-141 (target, instance, store branch, runtime) become one row: `| target, instance, runtime, store branch | defined under "Where it runs" |`.
2. The merge gate row (127) drops "A protected path is one `instance.yaml` lists under `protected_paths` because a change to it is sensitive, such as the harness's own code." A new row follows it: `| protected path | a path `instance.yaml` lists under `protected_paths` because a change to it is sensitive, such as the harness's own code |`.
3. The **Record** row (868) drops its restatement of who reads the decision log: "`factory decision add T-n "<line>"`, at any ticket state, closed included: one dated line in the decision log".

**F. `harness-docs` current truth.** The delta below is the whole of this part; archive writes it, and no repository file changes for it. It restates 23 requirements and removes 2. Its rules are in Decisions: find a changelog entry by its opening words, drop per-change limits, check whitespace once in full, drop the frozen build spec's checks. It adds 7 requirements for parts A to E.

## Tests to change

none. No test reads `README.md`, `dev/`, `docs/changelog.md` or `.factory/context.md`. The tests that read `docs/design.md` read its prompt blocks and the SCRATCH FILES rule (`tests/factory/test_decision_log.py:235`, `test_coding_standard.py:69`, `test_run_scratch.py:85`), which this change does not touch.

=== specs/harness-docs/spec.md
## MODIFIED Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL hold entry 51 covering every part and stay numbered without a gap, and `README.md` SHALL describe the new `resolve` behaviour and relative environment paths.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL hold one entry for issue #45 recording the guard, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store.

#### Scenario: The changelog records the guard in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #45 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `design=1 dirs=1`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule. `docs/changelog.md` SHALL hold one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch, `factory store migrate`, the `git clean -ffdx` hazard and a checkout from before the move, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location.

#### Scenario: The design doc names the store branch and the path rule
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
- THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`

#### Scenario: The changelog records the store branch in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The README describes the store branch and the move
`old_cost` joins the page into one line first, because the retired clause is wrapped across two lines. `old_refs` counts only the places that give the live store's location, so a how-to may still name the path a store moves from.
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`

### Requirement: The documents record the sibling-tests check
`docs/design.md` SHALL describe the check in a paragraph that starts `**Tests a sibling added.**`, in piece 8 and in the spec approval gate row, and SHALL no longer call the gate's list the only authorization to alter an existing test; `docs/changelog.md` SHALL hold an entry for issue #40 and stay numbered without a gap; and `README.md` SHALL describe the check and the new `--ruling` case.

#### Scenario: The design doc describes the check
- WHEN `(echo "piece8=$(grep '^| 8 |' docs/design.md | grep -c 'added by that sibling') gate=$(grep '^| Spec approval |' docs/design.md | grep -c 'a test an earlier sibling added') stale=$(grep -c 'which is the only authorization to alter an existing test' docs/design.md) check=$(grep -c '^\*\*Tests a sibling added\.\*\*.*BLOCKED from harness:' docs/design.md)")`
- THEN it prints exactly `piece8=1 gate=1 stale=0 check=1`

#### Scenario: The changelog records issue 40's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #40 ' docs/changelog.md | grep -oF -e 'own base' -e 'added by' -e 'BLOCKED from harness' -e 'Decision' -e 'critic rubric 1' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the sibling tests check and its ruling
- WHEN `(echo "built=$(grep -c '^- \*\*Sibling tests check\.\*\*' README.md) ruling=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'a test no merged sibling added')")`
- THEN it prints exactly `built=1 ruling=1`

### Requirement: The documents record the declared-path rule
The "## 5. Implementer" and "## 7. Verifier" blocks of `docs/design.md` SHALL carry the declared-path rule and stay verbatim copies of `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`. The run copies under `factory/prompts/` SHALL differ from those files only by the fills they had on `main`. `docs/changelog.md` SHALL hold one entry for issue #49, numbered without a gap.

#### Scenario: The design blocks and their copies carry the rule and stay in step
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); for r in "5. Implementer|05-implementer.md|implementer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) rule=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -c 'A protected path the sub-ticket declares is not an escalation') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `implementer copy=SAME rule=1 fill=unchanged`, then `verifier copy=SAME rule=1 fill=unchanged`. `copy=SAME`: the design block equals its `docs/prompts/` file. `rule=1`: that file carries the rule. `fill=unchanged`: the run copy under `factory/prompts/` differs from the documented copy only where it did on `main`.

#### Scenario: The changelog records the declared-path rule in a contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#49' | grep -c 'ESCALATIONS')`
- THEN it prints `CONTIGUOUS`, then `1`

### Requirement: The documents record the small-change lane
`docs/changelog.md` SHALL hold one entry for issue #48 recording the lane, numbered without a gap. `docs/design.md` and `README.md` SHALL describe the whole-spec sub-ticket and gate-command paths.

#### Scenario: The changelog records the small-change lane in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #48 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e 'paths' -e SKIPPED -e 'plan whole-spec' -e NEEDS-SPLIT -e seams | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

#### Scenario: The design doc and README describe both skips
- WHEN `(echo "design=$(grep -c 'whole-spec' docs/design.md | awk '{print ($1 > 0)}') gate=$(grep '^| 11 | Gate runner' docs/design.md | grep -c 'SKIPPED') readme=$(grep -c 'plan whole-spec' README.md | awk '{print ($1 > 0)}') skipped=$(grep -c 'SKIPPED' README.md | awk '{print ($1 > 0)}') stale=$(grep -c 'The build workflow runs the planner, which' README.md)")`
- THEN it prints exactly `design=1 gate=1 readme=1 skipped=1 stale=0`

### Requirement: The code reviewer judges the diff and leaves the suite and the gate to the verifier
Every copy of the code reviewer prompt SHALL say `Do not run the test suite or the gate commands: the verifier runs them on the same head`, and SHALL allow a narrow command that confirms a specific finding. The design block SHALL stay a verbatim copy of `docs/prompts/06-code-reviewer.md`, and the run copy SHALL differ from it only by the fills it had on `main`. The reviewer's composed input MUST NOT list the gate commands, while the implementer's and the verifier's inputs still SHALL.

#### Scenario: Every reviewer copy carries the rule and the copies stay in step
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "judge=$(echo "$J" | grep -c 'Do not run the test suite or the gate commands: the verifier runs them on the same head') narrow=$(echo "$J" | grep -c 'You may run a narrow command to confirm a specific finding')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `judge=1 narrow=1`, then `copy=SAME fill=unchanged`

#### Scenario: The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && for r in reviewer verifier implementer; do [ $r = implementer ] && bin/factory ticket set T-0001.1 status=ready-for-implementer 'in_flight=[]' >/dev/null; R=$(bin/factory run start --role $r --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); bin/factory run compose ${R:-none} >/dev/null 2>&1; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "$r gates=$(grep -c 'Gate commands (run each from your worktree' $I 2>/dev/null) told=$(grep -c 'The verifier runs the gate commands on this head; you do not run them' $I 2>/dev/null)"; done)`
- THEN it prints exactly `reviewer gates=0 told=1`, `verifier gates=1 told=0`, `implementer gates=1 told=0`, one per line

### Requirement: The documents record the empty-output route
`docs/design.md` SHALL state the EMPTY-OUTPUT rule and its two routing-table rows, and SHALL list a second EMPTY-OUTPUT among the park reasons. `README.md` SHALL no longer say that a run is parked for exceeding a budget, and SHALL describe the empty-output retry. `docs/changelog.md` SHALL hold an entry for issue #41, numbered without a gap.

#### Scenario: The design doc states the EMPTY-OUTPUT rule, its rows and its park
- WHEN `(echo "rule=$(grep -c '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md) rows=$(grep -c '^| Any role | EMPTY-OUTPUT' docs/design.md) parks=$(grep '^- A non-empty ESCALATIONS line' docs/design.md | grep -c 'a second EMPTY-OUTPUT in a row') kill=$(grep -c 'never recorded as a budget kill' docs/design.md)")`
- THEN it prints exactly `rule=1 rows=2 parks=1 kill=1`

#### Scenario: README drops the budget park and describes the empty-output retry
- WHEN `(echo "budget=$(grep -c 'exceeding its budget\|over budget' README.md) built=$(grep -c '^- \*\*Empty output\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'ended without output twice')")`
- THEN it prints exactly `budget=0 built=1 unstick=1`

#### Scenario: The changelog records issue 41 without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #41 ' docs/changelog.md | grep -oF -e EMPTY-OUTPUT -e foreground -e 'last message' -e 're-dispatched once' -e 'gate commands' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

### Requirement: The documents record the turn-economy change
`docs/changelog.md` SHALL hold one entry for issue #73, numbered without a gap. `docs/principles.md` principle 2 SHALL name the critic's no-suite rule among its mechanisms and SHALL no longer say the critic builds nothing.

#### Scenario: Principle 2 names the critic's no-suite rule and no longer its build ban
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; P=$(sed -n '/^### 2\. /,/^### 3\. /p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "entries73=$(grep -c '^[0-9]*\. After issue #73 ' docs/changelog.md) implemented=$(printf '%s' "$P" | grep -c 'runs no test suite (#73') builds=$(printf '%s' "$P" | grep -c 'builds nothing')")`
- THEN it prints exactly `CONTIGUOUS`, then `entries73=1 implemented=1 builds=0`

### Requirement: The documents record the critic revert
`docs/changelog.md` SHALL hold one entry for issue #74, numbered without a gap, that records the replay result and the two removed rules. The Spiking section of `docs/principles.md` SHALL no longer bound the critic to two paths and one command or say it does not build, SHALL say the critic may run a small scratch check, SHALL say vetting a whole approach belongs to the spec writer or a spike, and SHALL record the replay.

#### Scenario: The changelog records the revert in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #74 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#74' -e replay -e 'per-claim cap' -e 'no-build rule' -e 'no test suite' -e UV_PYTHON_INSTALL_DIR -e brace-list | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `7`

#### Scenario: The Spiking section allows a small scratch check and records the replay
- WHEN `(X=$(sed -n '/^## Spiking/,$p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "bound=$(printf '%s' "$X" | grep -c 'two paths, one command') nobuild=$(printf '%s' "$X" | grep -c 'it does not build') scratch=$(printf '%s' "$X" | grep -c 'small scratch check') whole=$(printf '%s' "$X" | grep -c 'vetting a whole approach belongs to the spec writer') replay=$(printf '%s' "$X" | grep -c 'replay')")`
- THEN it prints exactly `bound=0 nobuild=0 scratch=1 whole=1 replay=1`

### Requirement: The documents record the capability index
The triage prompt's design block, its `docs/prompts/` copy and the runtime prompt SHALL each carry the `Capabilities:` output line. `docs/design.md` and the README's Triage, Spec writer and Spec critic rows MUST describe the capability index. `docs/changelog.md` MUST have an entry for issue #75.

#### Scenario: The prompt copies, design, README and changelog name the capability index
- WHEN `(echo "docs-copy=$(grep -c '^Capabilities:' docs/prompts/01-triage.md) runtime=$(grep -c '^Capabilities:' factory/prompts/triage.md) changelog=$(grep -c '^[0-9]*\. After issue #75 ' docs/changelog.md) design=$(grep -q 'capability index' docs/design.md && echo y || echo n) readme=$(grep -E '^\| (Triage|Spec writer|Spec critic) \(' README.md | grep -c 'capability index')")`
- THEN it prints exactly `docs-copy=1 runtime=1 changelog=1 design=y readme=3`

### Requirement: The documents describe the whole decision log for the spec writer, critic and planner
`docs/design.md` and the README's Spec writer, Spec critic and Planner rows MUST say that those roles receive the whole decision log, and neither MUST mention a decision index. `docs/changelog.md` SHALL have an entry for issue #78.

#### Scenario: The design, README and changelog describe the whole decision log and no decision index
- WHEN `(echo "design-index=$(grep -c 'decision index' docs/design.md) design-whole=$(grep -c 'They and the planner receive the whole decision log' docs/design.md) readme-index=$(grep -c 'decision index' README.md) readme-whole=$(grep -E '^\| (Spec writer|Spec critic|Planner) \(' README.md | grep -c 'the whole decision log') changelog=$(grep -c '^[0-9]*\. After issue #78 ' docs/changelog.md)")`
- THEN it prints exactly `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`

### Requirement: The documents record superseded plans
`docs/design.md` SHALL say, in its rule for a sub-ticket closed by the human, that a new plan from a later approved version supersedes the earlier plan's unmerged sub-tickets. `README.md` SHALL carry a "Re-plan after a re-spec" bullet. `docs/changelog.md` SHALL hold one entry for issue #77, numbered without a gap.

#### Scenario: The design doc, README and changelog record superseded plans
- WHEN `(echo "design=$(grep 'sub-ticket closed by the human' docs/design.md | grep -c supersede) readme=$(grep -c '^- \*\*Re-plan after a re-spec\.\*\*' README.md) changelog=$(grep '^[0-9]*\. After issue #77 ' docs/changelog.md | grep -oF -e superseded -e planned_from -e 'Depends on' | sort -u | grep -c .) $(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)")`
- THEN it prints exactly `design=1 readme=1 changelog=3 CONTIGUOUS`

### Requirement: The documents record the protected-path rule at merge
`docs/design.md` SHALL drop the per-PR approval for protected paths, describe the declared-path rule in piece 8 and the Protected paths gate row, and route a reviewer ESCALATE back to its checks; `docs/changelog.md` SHALL hold an entry for issue #57 and stay numbered without a gap; and `README.md` SHALL describe the check and `--accept-paths`.

#### Scenario: The design doc drops the per-PR approval for protected paths
- WHEN `(echo "gates=$(grep -c 'a PR touching a protected path, the daily escalation queue' docs/design.md) either=$(grep -c 'A change to either needs a human approval record before it merges' docs/design.md) onpr=$(grep -c 'any other guardrail or protected path needs a human approval on the PR itself' docs/design.md) piece8=$(grep '^| 8 |' docs/design.md | grep -c 'Protected paths:') piece9=$(grep -c 'review protected PRs' docs/design.md) gaterow=$(grep '^| Protected paths |' docs/design.md | grep -c -- '--accept-paths') stale=$(grep -c 'records the piece-8 approval; the merge gate does not merge without it' docs/design.md) reviewer_rule=$(grep -c '^  - A reviewer ESCALATE returns to its checks' docs/design.md) old_route=$(grep -c 'or a reviewer ESCALATE returns to the implementer' docs/design.md)")`
- THEN it prints exactly `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0`

#### Scenario: The changelog records issue 57's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #57 ' docs/changelog.md | grep -oF -e 'Risk' -e '--accept-paths' -e 'BLOCKED from merge gate' -e 'checks' -e 'Protected paths:' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the protected-path check and the new resolve verb
- WHEN `(echo "built=$(grep -c '^- \*\*Protected paths at merge\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--accept-paths') merges=$(sed -n '/^- \*\*Merges, one at a time\.\*\*/,/^- \*\*Setting up the store\.\*\*/p' README.md | grep -c 'Risk section' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `built=1 unstick=1 merges=1`

### Requirement: The documents record the reading rules for the five roles
`docs/changelog.md` SHALL hold one entry for issue #76, numbered without a gap, naming the five roles and the operator's replay, and the changelog SHALL end with its closing "Declined:" line.

#### Scenario: The changelog records the reading rules for the five roles in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #76 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oiF -e '#76' -e implementer -e verifier -e 'code reviewer' -e planner -e triage -e replay | tr A-Z a-z | sort -u | grep -c .) footer=$(tail -1 docs/changelog.md | grep -c '^Declined: a dedicated merge agent')")`
- THEN it prints `CONTIGUOUS`, then `entries=1 terms=7 footer=1`

### Requirement: The documents record spec amendment, spec drift and the cross-ticket check
`docs/changelog.md` SHALL hold one entry, numbered without a gap, covering the amend command with its intent flag, the drift check and the critic's cross-ticket check; `docs/design.md` SHALL name `factory spec amend` and `--intent unchanged`, carry a Spec drift paragraph and give the critic the approved changes not yet archived in its routing row; and README SHALL list the command under "Where a human decides" and the feature under Built.

#### Scenario: The changelog records the change in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. ' docs/changelog.md | grep -F 'factory spec amend'); echo "$E" | grep -c .; echo "$E" | grep -oF -e '--intent' -e 'in flight' -e tasks.md -e 'spec drift' -e 'not yet archived' -e whichever | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `6`

#### Scenario: The design doc names the amend command, its intent flag, spec drift and the critic's new input
- WHEN `(echo "amend=$(grep -c 'factory spec amend' docs/design.md | awk '{print ($1 > 0)}') intent=$(grep -c -- '--intent unchanged' docs/design.md | awk '{print ($1 > 0)}') drift=$(grep -c '^\*\*Spec drift\.\*\*' docs/design.md) row=$(grep '^| Spec writer | READY-FOR-CRITIC' docs/design.md | grep -c 'not yet archived')")`
- THEN it prints exactly `amend=1 intent=1 drift=1 row=1`

#### Scenario: README lists the amend command and the drift check
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' README.md); B=$(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' README.md); echo "amend=$(echo "$H" | grep -c 'factory spec amend' | awk '{print ($1 > 0)}') intent=$(echo "$H" | grep -c -- '--intent' | awk '{print ($1 > 0)}') built=$(echo "$B" | grep -c '^- \*\*Spec amendment and drift\.\*\*')")`
- THEN it prints exactly `amend=1 intent=1 built=1`

### Requirement: The documents record the environment sync and the dropped virtual environment
`docs/design.md` SHALL name `environment_sync` and say the wrapper drops `VIRTUAL_ENV`. `factory/instance.template.yaml` SHALL carry an `environment_sync` key. `README.md` SHALL name `environment_sync` and `VIRTUAL_ENV`. `docs/changelog.md` SHALL hold one entry for issue #51 recording the change, numbered without a gap.

#### Scenario: The design doc, template and README name the sync and the dropped virtual environment
- WHEN `(echo "design=$(grep -c environment_sync docs/design.md | awk '{print ($1 > 0)}') design_venv=$(grep -c VIRTUAL_ENV docs/design.md | awk '{print ($1 > 0)}') template=$(grep -c '^environment_sync:' factory/instance.template.yaml) readme=$(grep -c environment_sync README.md | awk '{print ($1 > 0)}') readme_venv=$(grep -c VIRTUAL_ENV README.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `design=1 design_venv=1 template=1 readme=1 readme_venv=1`

#### Scenario: The changelog records the environment sync in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #51 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e environment_sync -e VIRTUAL_ENV -e PYTHONHOME -e 'already synced' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `4`

### Requirement: The documents describe the driver
`README.md` MUST describe `factory drive` under "Starting a run", its `claude -p` role processes under "What depends on Claude Code", the driver among the built pieces and its status file in the store's file table, and SHALL no longer list per-role effort as not built; `docs/design.md` SHALL name the driver, and `docs/changelog.md` SHALL hold an entry for issue #65.

#### Scenario: The documents describe the driver
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; r=README.md; echo "starting=$(y $(sed -n '/^## Starting a run/,/^### Filing a request/p' $r | grep -c 'factory drive')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'claude -p')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory drive')) effort-gap=$(y $(grep -c 'none has an effort level' $r)) drive-row=$(y $(grep -cE '^\| `drive/' $r)) design=$(y $(grep -c 'factory drive' docs/design.md)) changelog=$(y $(grep -cE '^[0-9]+\. After issues? [^(]*#65' docs/changelog.md))")`
- THEN it prints exactly `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes`

### Requirement: The documents record the sibling-merge exception and the start-failure ruling
`docs/design.md`'s Spec drift paragraph SHALL name `main_after` as not drift and its routing rules SHALL name the `harness-bug: run start implementer` ruling; README's Unstick row SHALL name it, and its "Spec amendment and drift" bullet SHALL say a sibling's merge is not drift and SHALL no longer say the check has not yet fired; and `docs/changelog.md` SHALL hold one entry for issue #85, numbered without a gap.

#### Scenario: The design doc, README and changelog record both changes
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; B=$(sed -n '/^- \*\*Spec amendment and drift\.\*\*/,/^- \*\*Re-plan after a re-spec\.\*\*/p' README.md); echo "design-drift=$(y $(grep '^\*\*Spec drift\.\*\*' docs/design.md | grep -c main_after)) design-ruling=$(y $(grep -c 'harness-bug: run start implementer' docs/design.md)) unstick=$(y $(grep '^| \*\*Unstick\*\*' README.md | grep -c 'harness-bug: run start implementer')) bullet-sibling=$(y $(echo "$B" | grep -c 'not drift')) bullet-stale=$(y $(echo "$B" | grep -c 'has not yet fired'))"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #85 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#85' -e main_after -e 'harness-bug: run start implementer' | sort -u | grep -c .)`
- THEN it prints exactly `design-drift=yes design-ruling=yes unstick=yes bullet-sibling=yes bullet-stale=no`, then `CONTIGUOUS`, then `1`, then `3`

### Requirement: The documents record the driver's exemption and its same-ticket guard
`docs/changelog.md` SHALL hold one entry for issue #86, numbered without a gap. README's `factory drive` how-to SHALL no longer tell the operator to put the marker in front of the command, and SHALL say that the driver is exempt and what it refuses on the same ticket. The opening of README's "Where a human decides" SHALL say the driver is exempt. `docs/design.md`'s fence paragraph SHALL state the exemption and the same-ticket guard, and SHALL no longer say the driver meets the fence like any write.

#### Scenario: The documents describe the driver's exemption and its same-ticket guard
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; c() { tr '\n' ' ' | tr -s ' ' | grep -ci -- "$1"; }; r=README.md; D=$(sed -n '/^### Driving a ticket from a shell with `factory drive`/,/^Each role process/p' $r); H=$(sed -n '/^## Where a human decides/,/^```/p' $r); G=$(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md); echo "changelog=$(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md) entry=$(grep -c '^[0-9]*\. After issue #86 ' docs/changelog.md) step=$(echo "$D" | c 'put `FACTORY_DISPATCH=1` in front of the command') drive=$(y $(echo "$D" | c exempt)),$(y $(echo "$D" | c 'same ticket')) human=$(y $(echo "$H" | c exempt)) design=$(y $(echo "$G" | c exempt)),$(y $(echo "$G" | c 'same ticket')),$(echo "$G" | c 'like any write when it starts')")`
- THEN it prints exactly `changelog=CONTIGUOUS entry=1 step=0 drive=yes,yes human=yes design=yes,yes,0`

### Requirement: The documents record factory stats
README SHALL list `stats` among the commands that are not writes, say under "Accepting a harness revision" that it skips the lock, describe it in a how-to subsection "Counting what each role catches and costs", in "What depends on Claude Code" and under **Built**; `docs/design.md` SHALL list it in the fence paragraph's read-only list, name it in the lock clause, and cite it in the model-per-role paragraph; `docs/principles.md` §4 SHALL name it as implemented and no longer say "1 BLOCKING finding in total"; and `docs/changelog.md` SHALL hold one entry for issues #70 and #61, numbered without a gap.

#### Scenario: The documents record factory stats
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; j() { tr '\n' ' ' | tr -s ' '; }; r=README.md; H=$(sed -n '/^## Where a human decides/,/^```/p' $r | j); L=$(sed -n '/^### Accepting a harness revision/,/^### Upgrading the runtime/p' $r | j); echo "readonly=$(y $(echo "$H" | grep -c '`paths` and `stats`')) howto=$(y $(sed -n '/^### Counting what each role catches and costs/,/^##/p' $r | grep -c 'factory stats')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory stats')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'factory stats')) lock=$(y $(echo "$L" | grep -c '`stats`')) design-fence=$(y $(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md | grep -c '`paths` and `stats`')) design-lock=$(y $(grep '^\*\*Role-context block\.\*\*' docs/design.md | grep -c '`stats`')) design-model=$(y $(grep '^\*\*Model per role, starting point\.\*\*' docs/design.md | grep -c 'factory stats')) principles=$(y $(sed -n '/^### 4\. Measure catch beside cost\./,/^##/p' docs/principles.md | grep '^Implemented by:' | grep -c '`factory stats`')) principles-old=$(y $(grep -c '1 BLOCKING finding in total' docs/principles.md))"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #70 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#70' -e '#61' -e 'factory stats' -e 'message id' | sort -u | grep -c .)`
- THEN it prints exactly `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no`, then `CONTIGUOUS`, then `1`, then `4`

### Requirement: The documents record that run start owns each role's model
`README.md`'s role-call paragraph under "The intake workflow, step by step" SHALL say that `run start` refuses a `--model` the instance does not name.

#### Scenario: The README describes the model check
- WHEN `(echo "readme=$(sed -n '/^### The intake workflow, step by step/,/sequenceDiagram/p' README.md | grep -c -- '--model' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `readme=1`

### Requirement: The documents record the parallel suite and the waiting park reason
`docs/design.md`'s EMPTY-OUTPUT rule SHALL name the waiting park reason. `README.md` SHALL name pytest-xdist, and its Empty output entry SHALL give the waiting reason and no longer say it has not fired on a real ticket. `docs/changelog.md` SHALL hold entry 71 for issue #106, numbered without a gap.

#### Scenario: The design doc names the waiting park reason
- WHEN `(echo "design=$(grep '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md | grep -c 'ended its turn waiting on a background command')")`
- THEN it prints exactly `design=1`

#### Scenario: The README names pytest-xdist and the waiting reason
- WHEN `(B=$(awk '/^- \*\*Empty output\.\*\*/{f=1; print; next} f && /^(- \*\*|$|#)/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "bullet=$(grep -c '^- \*\*Empty output\.\*\*' README.md) waiting=$(echo "$B" | grep -c 'ended its turn waiting on a background command') unfired=$(echo "$B" | grep -c 'has not yet fired') xdist=$(grep -c 'pytest-xdist' README.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `bullet=1 waiting=1 unfired=0 xdist=1`

#### Scenario: The changelog records issue 106 as entry 71, without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #106 ' docs/changelog.md); printf '%s\n' "$E" | grep -c '^71\. '; printf '%s' "$E" | grep -oF -e 'pytest-xdist' -e 'ended its turn waiting on a background command' -e 'EMPTY-OUTPUT' -e 'stand-in' -e 'in-process' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

## REMOVED Requirements

### Requirement: Nothing else in the two prompts changes
Reason: it limited what issue #73's change touched, measured against `main` and the fixed commit `05cf8f9`, so any later change to the spec writer prompt breaks it; it fails on `main` today (`writer=2`).

### Requirement: The reading rules are the only change to the role prompts
Reason: it limited what issue #76's change added or removed, measured against `main`, so any later edit to those prompts or to `docs/design.md` breaks it.

## ADDED Requirements

### Requirement: The maintained documents carry no whitespace errors
`README.md`, every file under `docs/` and `dev/`, and `.factory/context.md` MUST carry no whitespace error, checked over each file in full rather than over one change's diff.

#### Scenario: The maintained documents pass git's whitespace check in full
- WHEN `(E=$(git hash-object -t tree /dev/null); git diff --check $E HEAD -- README.md docs dev .factory/context.md; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The build documents under dev/ are frozen as history
`dev/build-harness.spec.md`, `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md` SHALL each carry, as line 3, a header that starts `> **Frozen as history.**`, followed by a blank line, and SHALL otherwise stay byte for byte as they were at `7231670`. `.factory/context.md` MUST NOT ask a change to keep any of them consistent, and SHALL call them frozen; README's `dev/` row SHALL say they are frozen as history.

#### Scenario: Each build document carries the header and is otherwise unchanged
- WHEN `(for f in dev/build-harness.spec.md dev/build-harness.plan.md dev/P0-intake-skeleton.md; do echo "$f header=$(sed -n 3p $f | grep -c '^> \*\*Frozen as history\.\*\* ') rest=$(sed '3,4d' $f | cmp -s - <(git show 7231670:$f) && echo same || echo changed)"; done)`
- THEN it prints exactly `dev/build-harness.spec.md header=1 rest=same`, then `dev/build-harness.plan.md header=1 rest=same`, then `dev/P0-intake-skeleton.md header=1 rest=same`

#### Scenario: The briefing no longer asks a change to keep the build spec in step
- WHEN `(echo "buildspec=$(grep -c 'build-harness' .factory/context.md) frozen=$(grep -c 'frozen as history' .factory/context.md | awk '{print ($1 > 0)}') readme=$(grep '^| .dev/. |' README.md | grep -c 'frozen as history')")`
- THEN it prints exactly `buildspec=0 frozen=1 readme=1`

### Requirement: README's claims about what has run match the stores
README MUST NOT say that the one-sub-ticket path, the driver, the per-run scratch directory, a gate command's path skip, the re-plan after a re-spec or the protected-path refusal at merge has not yet run, and MUST NOT say that a run with no output is recorded as killed. Its tripwire and sibling-tests entries SHALL still say they have not yet fired, and its per-role effort entry that neither target sets it. Its "Ground truth only above" rule SHALL ask each entry to say whether it has yet run on a real ticket, and line 3 of `docs/design.md` SHALL point to `docs/changelog.md` instead of carrying a date of its own.

#### Scenario: README no longer calls run features untried, and keeps the claims that are still true
- WHEN `(b() { awk -v h="$1" 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(printf '%s' "$R" | grep -oF -e 'one-sub-ticket path is tested' -e 'has not yet run a real ticket' -e 'remains the tested route' -e 'parked; this is tested' -e 'configuration uses it yet' -e 'recorded as killed' | grep -c .) replan=$(b '- **Re-plan after a re-spec.**' | grep -c 'not yet') paths=$(b '- **Protected paths at merge.**' | grep -c 'not yet') drive=$(b '- **The driver, ' | grep -c 'not yet') tripwire=$(b '- **Tripwire on live files.**' | grep -c 'has not yet fired') sibling=$(b '- **Sibling tests check.**' | grep -c 'has not yet fired') effort=$(b '- **Per-role effort' | grep -c 'Neither target sets it yet')")`
- THEN it prints exactly `stale=0 replan=0 paths=0 drive=0 tripwire=1 sibling=1 effort=1`

#### Scenario: The Built rule asks for run status, and the design doc's date line points to the changelog
- WHEN `(echo "rule=$(sed -n '/^- \*\*Ground truth only above/,/^- \*\*Update with the change/p' README.md | tr '\n' ' ' | tr -s ' ' | grep -c 'its entry says whether it has yet run on a real ticket') date=$(sed -n 3p docs/design.md | grep -c 'docs/changelog.md') old=$(sed -n 3p docs/design.md | grep -c '^2026-09-30 · Daniel$')")`
- THEN it prints exactly `rule=1 date=1 old=0`

### Requirement: README describes each mechanism in one section
README SHALL describe the live-store fence under "Where a human decides", the driver under "Driving a ticket from a shell with `factory drive`", the final check's skip under "The build workflow, step by step", the store branch under "How the factory uses git", and other agent hosts only in `docs/design.md`. Elsewhere it SHALL give each a short entry with a pointer: the Built entries for the fence, the driver, the tripwire, the sibling-tests check, spec drift, empty output, protected paths at merge and `factory stats` SHALL each stay within a line budget and name the section or the `docs/design.md` paragraph that describes it, and "Not built" SHALL list nothing that "Where this can go" lists.

#### Scenario: Each Built entry is a short pointer, and each mechanism's detail has one home
`s` prints `pointer` when a Built entry is at most N lines and names its home, and `long` otherwise.
- WHEN `(b() { awk -v h="$1" 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' README.md; }; s() { b "$1" | awk -v n="$2" -v p="$3" '{t=t" "$0} END{gsub(/ +/," ",t); print ((NR>0 && NR<=n && index(t,p)) ? "pointer" : "long")}'; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "fence=$(s '- **Live-store fence.**' 3 'Where a human decides') driver=$(s '- **The driver, ' 4 'Driving a ticket from a shell') tripwire=$(s '- **Tripwire on live files.**' 4 'docs/design.md') sibling=$(s '- **Sibling tests check.**' 4 'docs/design.md') drift=$(s '- **Spec amendment and drift.**' 6 'docs/design.md') empty=$(s '- **Empty output.**' 6 'docs/design.md') paths=$(s '- **Protected paths at merge.**' 4 'Where a human decides') stats=$(s '- **Counting catch and cost' 3 'Counting what each role catches') host=$(sed -n '/^### Running on another agent host/,/^## /p' README.md | sed '1d;$d' | awk '{t=t" "$0} /./{n++} /^\|/{tab=1} END{print ((n<=6 && !tab && index(t,"docs/design.md")) ? "pointer" : "long")}') skip=$(printf '%s' "$R" | grep -o 'has not moved since' | grep -c .) store=$(printf '%s' "$R" | grep -o 'never moves the integration branch' | grep -c .) drivefence=$(sed -n '/^### Driving a ticket from a shell/,/^Each role process/p' README.md | tr '\n' ' ' | grep -c 'refused like any write') notbuilt=$(sed -n '/^\*\*Not built\*\*/,/^## Where this can go/p' README.md | grep -c '^- \*\*')")`
- THEN it prints exactly `fence=pointer driver=pointer tripwire=pointer sibling=pointer drift=pointer empty=pointer paths=pointer stats=pointer host=pointer skip=1 store=1 drivefence=0 notbuilt=0`

### Requirement: README defines each term once
README's "Terms used on this page" SHALL point to "Where it runs" for target, instance, runtime and store branch in one row instead of defining them again, and SHALL give protected path its own row; the merge gate row SHALL no longer define a protected path, and the **Record** row of "Where a human decides" SHALL no longer restate who reads the decision log.

#### Scenario: The glossary points to Where it runs and defines protected path once
- WHEN `(T=$(sed -n '/^## Terms used on this page/,/^## How a ticket moves/p' README.md); echo "rows=$(printf '%s\n' "$T" | grep -cE '^\| (target|instance|runtime|store branch) \|') pointer=$(printf '%s\n' "$T" | grep -c '^| target, instance, runtime, store branch |') protected=$(printf '%s\n' "$T" | grep -c '^| protected path |') merge=$(grep '^| merge gate |' README.md | grep -c 'protected_paths') record=$(grep '^| \*\*Record\*\*' README.md | grep -c 'receive')")`
- THEN it prints exactly `rows=0 pointer=1 protected=1 merge=0 record=0`

### Requirement: History lives in the changelog
README SHALL keep under "Related work and history" the issue references it carries today, and SHALL no longer carry the history this change moves: the 2026-10-04 overlap count, the double count `factory/cost.py` once made, the store moves, the page's own origin story and the regeneration pass's past catches. `docs/design.md`'s model-per-role paragraph SHALL point to changelog entry 70 for the first `factory stats` figures instead of repeating them. `docs/changelog.md` SHALL hold one entry for issue #101 recording the move, numbered without a gap.

#### Scenario: README keeps its issue references and drops the moved history, and the changelog records the move
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); X=$(sed -n '/^## Related work and history/,/^## Maintaining this page/p' README.md | tr '\n' ' ' | tr -s ' '); M=$(grep '^\*\*Model per role, starting point\.\*\*' docs/design.md); E=$(grep '^[0-9]*\. After issue #101 ' docs/changelog.md); echo "history=$(printf '%s' "$R" | grep -oF -e '41 and 11 overlapping' -e 'used to count most calls about twice' -e 'First written 2026-10-03' -e 'today this caught' -e 'were moved onto it' | grep -c .) refs=$(printf '%s' "$X" | grep -oE '#[0-9]+' | sort -u | grep -xcE '#(16|17|18|19|20|21|22|23|24|28|35|42|46|47|53|55|61|65|70)') figures=$(printf '%s' "$M" | grep -c '94,860,442') pointer=$(printf '%s' "$M" | grep -c 'changelog entry 70') entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e frozen -e build-harness.spec.md -e context.md -e '41 and 11' -e harness-docs -e 'not yet' | sort -u | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)`
- THEN it prints exactly `history=0 refs=19 figures=0 pointer=1 entries=1 terms=6`, then `CONTIGUOUS`

### Requirement: README stays within its line budget
`README.md` SHALL be at most 1,110 lines long; a later change that needs more room raises this bound in its own spec, where the operator approves it at the gate.

#### Scenario: README is at most 1,110 lines
- WHEN `(echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1110 ? "within" : "over")}')")`
- THEN it prints exactly `readme=within`

=== verification.md
## Acceptance

Every WHEN runs from the repository root under bash. The scenario "The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do" needs its two GIVEN blocks run first, as in current truth. The 46 restated scenarios print the same on `main` (`7231670`) as on the prototype, and on a simulated later change: one more changelog entry, and a line added to the verifier prompt in all three copies.

- The changelog records the change in order → REGRESSION
- The README describes the new resolve verbs → REGRESSION
- The README says relative paths resolve from the caller's directory → REGRESSION
- The changelog records the guard in one entry → REGRESSION
- The design doc names the marker and the run-directory rule → REGRESSION
- README tells the operator how to write during a run, first thing under Where a human decides → REGRESSION
- README says the final verifier run is listed as in flight → REGRESSION
- README no longer says the factory's capabilities never entered the spec store → REGRESSION
- The design doc names the store branch and the path rule → REGRESSION
- The changelog records the store branch in one contiguous entry → REGRESSION
- The README describes the store branch and the move → REGRESSION
- The design doc describes the check → REGRESSION
- The changelog records issue 40's change without a numbering gap → REGRESSION
- README describes the sibling tests check and its ruling → REGRESSION
- The design blocks and their copies carry the rule and stay in step → REGRESSION
- The changelog records the declared-path rule in a contiguous entry → REGRESSION
- The changelog records the small-change lane in one entry → REGRESSION
- The design doc and README describe both skips → REGRESSION
- Every reviewer copy carries the rule and the copies stay in step → REGRESSION
- The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do → REGRESSION
- The design doc states the EMPTY-OUTPUT rule, its rows and its park → REGRESSION
- README drops the budget park and describes the empty-output retry → REGRESSION
- The changelog records issue 41 without a numbering gap → REGRESSION
- Principle 2 names the critic's no-suite rule and no longer its build ban → REGRESSION
- The changelog records the revert in one entry → REGRESSION
- The Spiking section allows a small scratch check and records the replay → REGRESSION
- The prompt copies, design, README and changelog name the capability index → REGRESSION
- The design, README and changelog describe the whole decision log and no decision index → REGRESSION
- The design doc, README and changelog record superseded plans → REGRESSION
- The design doc drops the per-PR approval for protected paths → REGRESSION
- The changelog records issue 57's change without a numbering gap → REGRESSION
- README describes the protected-path check and the new resolve verb → REGRESSION
- The changelog records the reading rules for the five roles in one entry → REGRESSION
- The changelog records the change in one contiguous entry → REGRESSION
- The design doc names the amend command, its intent flag, spec drift and the critic's new input → REGRESSION
- README lists the amend command and the drift check → REGRESSION
- The design doc, template and README name the sync and the dropped virtual environment → REGRESSION
- The changelog records the environment sync in one entry → REGRESSION
- The documents describe the driver → REGRESSION
- The design doc, README and changelog record both changes → REGRESSION
- The documents describe the driver's exemption and its same-ticket guard → REGRESSION
- The documents record factory stats → REGRESSION
- The README describes the model check → REGRESSION
- The design doc names the waiting park reason → REGRESSION
- The README names pytest-xdist and the waiting reason → REGRESSION
- The changelog records issue 106 as entry 71, without a numbering gap → REGRESSION
- The maintained documents pass git's whitespace check in full → REGRESSION
- Each build document carries the header and is otherwise unchanged → NEW; today it prints `header=0 rest=changed` for each of the three files: no header, and deleting lines 3-4 of the original text changes it.
- The briefing no longer asks a change to keep the build spec in step → NEW; today it prints `buildspec=3 frozen=0 readme=0`.
- README no longer calls run features untried, and keeps the claims that are still true → NEW; today it prints `stale=7 replan=1 paths=1 drive=1 tripwire=1 sibling=1 effort=1`.
- The Built rule asks for run status, and the design doc's date line points to the changelog → NEW; today it prints `rule=0 date=0 old=1`.
- Each Built entry is a short pointer, and each mechanism's detail has one home → NEW. Today it prints `fence=long driver=long tripwire=long sibling=long drift=long empty=long paths=long stats=long host=long skip=2 store=3 drivefence=1 notbuilt=5`.
- The glossary points to Where it runs and defines protected path once → NEW; today it prints `rows=4 pointer=0 protected=0 merge=1 record=1`.
- README keeps its issue references and drops the moved history, and the changelog records the move → NEW; today it prints `history=5 refs=19 figures=1 pointer=0 entries=0 terms=0`, then `CONTIGUOUS`.
- README is at most 1,110 lines → NEW; today it prints `readme=over` (1,191 lines).

Out-of-scope observations:
- README:825-829 says parallel builds across tickets "have not been tried". I did not check that against the logs.
- `factory/cli.py:1`'s docstring cites "the build-harness spec". It is harness code, protected and out of scope.
- Three current-truth scenarios cannot run alone: they source setup scripts that other capabilities' scenarios write to `$TMPDIR`. One of them is restated here unchanged.

## PR description (the implementer's output)

Sub-ticket: T-0048.1 (parent T-0048, approved spec v1, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0048/v1.md`)
Branch: `factory/T-0048.1`, one commit `08ad85e` on base `7231670`. 7 files, 142 insertions, 220 deletions.

This change shortens the two documents the operator reads at every spec gate and makes them true.
The spec gate is the human review where a spec is approved before code is written. The documents are
`README.md`, the page saying what the factory does today, and `docs/design.md`.
- README goes from 1,191 to 1,106 lines.
- Its false "not yet run" claims are corrected from the stores' logs. The store is the factory's
  per-repo record of tickets, runs and verdicts.
- Each mechanism is described in one section, and other mentions point to that section.
- History moves to `docs/changelog.md`.
- The three finished build documents under `dev/` are frozen. The briefing every agent reads first
  no longer asks each change to keep them in step.

No code, test, or prompt file changes.

## What changed

**A. Freeze the `dev/` build documents.**
- `dev/build-harness.spec.md`, `dev/build-harness.plan.md`, `dev/P0-intake-skeleton.md`: the spec's
  "Frozen as history" header is inserted at line 3, followed by one blank line. Nothing else in these
  files changes, and scenario 48 checks this byte for byte against `7231670`.
- `.factory/context.md` (a protected path the spec declares): the `dev/` bullet now reads as the
  spec gives it. The design-change sentence no longer names `dev/build-harness.spec.md`, so the file
  names no `build-harness` path.
- README's `dev/` row in "Where things live" now says those three documents are frozen as history.

**B. Correct the stale claims.**
- README line 94: a run with no output is run once more and then parks its ticket. README no longer
  says such a run is "recorded as killed".
- These claims now say the feature has run:
  - the one-sub-ticket path, on both targets;
  - the driver, `factory drive`, which took real tickets through intake and the build on the
    chat-bot target;
  - the path skip, which is recorded on a real sub-ticket;
  - the re-plan after a re-spec, which has fired;
  - the protected-path refusal, which has fired and was accepted with `--accept-paths`.
- The per-run scratch directory sentence no longer says it is untried.
- These claims are kept, because they are still true:
  - the tripwire has not yet fired;
  - the sibling-tests check has not yet fired;
  - the drift check's sibling-merge exception has not yet run;
  - "Neither target sets it yet", in the effort entry.
- The "Ground truth only" rule now admits a thing once it is built and tested. It asks each entry to
  say whether the thing has yet run on a real ticket. The rest of that bullet stays.
- `docs/design.md` line 3 now reads ``Daniel · first written 2026-09-30; every change since is in `docs/changelog.md` ``.
- The README status date was already 2026-10-13, the day of this change, so it is unchanged.
- I checked each correction against the logs. The logs are read only; the Nanobot store is the
  other target's store.
  - `plan.skipped` events: 16 tickets here, from T-0031 to T-0051. There are 5 on the Nanobot store.
  - Driver replies: 15 `reply.json` files on the Nanobot store.
  - Path skip: `ci.yaml` with `SKIPPED` for `ticket: T-0036.1` on the Nanobot store.
  - Re-plan: `subtickets.superseded` for T-0031 at 2026-10-09T18:11:03.
  - Protected-path refusal: `merge.refused` "protected paths not declared" for T-0044.1 at
    2026-10-12T02:14:17, then `human.resolved` `kind: accept-paths` at 04:37:24.

**C. One home per mechanism in README.**
- The live-store fence blocks store writes while an agent run is in flight. Its home is "Where a
  human decides", which is unchanged.
  - The driver how-to paragraph about the fence is 6 lines. It keeps the exemption and the
    same-ticket guard: exit 2 and nothing written, the `drive/<ticket>.yaml` check, what to do about
    a pid that is not a driver, and the SIGKILL recovery.
  - It drops "refused like any write" and "even while runs of other tickets are in flight".
  - The fence's Built entry is 3 lines and points to "Where a human decides".
- The driver's home is its how-to section.
  - The file-tool limits sentence moved from the driver's Built entry into the how-to.
  - The Built entry is 4 lines.
  - "Running on another agent host" is 5 non-blank lines with no table. It points to
    `docs/design.md`, "Running on another agent host".
- The final check's skip has its full condition and reason in "The build workflow, step by step".
  "How a ticket moves" keeps one pointer sentence. "has not moved since" now appears once.
- The store branch's home is "How the factory uses git".
  - The target bullet in "Where it runs" now uses the spec's sentence.
  - The store-commit sentences at old lines 619-620 and 828 are dropped.
  - The Built entry is 2 lines.
  - "never moves the integration branch" now appears once. It is in "How the factory uses git",
    whose bullet also absorbs the catch-up consequence from old line 619.
- Built entries. Each keeps its bold name and is within its line target:
  - Build, local-only: 5 lines (target 6). It keeps `SKIPPED`.
  - Spec store: 2 lines.
  - Tripwire: 4 lines.
  - Sibling tests: 4 lines.
  - Spec amendment and drift: 5 lines (target 6). It keeps "factory spec amend", "Where a human
    decides" and "is not drift".
  - Re-plan: 4 lines.
  - Empty output: 5 lines (target 6). It keeps the waiting phrase.
  - Protected paths: 4 lines.
  - Per-role effort: unchanged.
  - `factory stats`: 3 lines. The `factory/cost.py` history is dropped.
- "Not built" is now one paragraph with no bullets. It gives the five facts from C.6 and keeps the
  hand-copy sentence word for word. The bullet in "Where this can go" is renamed "**Current truth for
  the factory itself.**".
- The `inlineRoles` how-to now points to "What depends on Claude Code" instead of repeating what the
  flag does.

**D. History to the changelog.**
- These sentences are dropped from README:
  - the 2026-10-04 overlap of 41 and 11 runs;
  - the `factory/cost.py` double count;
  - both store-move sentences;
  - the regeneration pass's "(today this caught two: ...)".
- "Related work and history" is now a list. It keeps every one of the 19 issue references, each
  beside what it names.
- After the list, it names instances A and B, points to `docs/changelog.md` and `dev/issues.md`,
  and gives re-derived figures:
  - 51 tickets and 64 sub-tickets: `ls .factory/store/tickets`.
  - Runtime commit `9dbd4f8`: `git -C ~/dev/spec-factory-harness rev-parse --short HEAD`.
  - Harness revision `5e00a1f`: `bin/factory paths` printed `"harness_revision": "5e00a1f5..."`,
    which equals `.factory/harness.lock`.
- `docs/design.md:70`: the text after "prints the evidence a change to this table needs" now reads
  "; its first figures, from 2026-10-11, are in `docs/principles.md`, principle 4, and changelog
  entry 70." This is the spec's wording.
- `docs/changelog.md`: new entry 72 for #101, after entry 71 and before the "Declined:" line. It
  records parts A to F and F's rules, the corrected claims with their tickets, and the rejected
  options. It also keeps the per-role `factory stats` figures that line 70 no longer carries (see
  Known gaps 1).

**E. Glossary.**
- The four rows for target, instance, store branch and runtime become one row pointing to "Where it
  runs". "Where it runs" defines all four.
- The merge-gate row no longer defines a protected path. A new `protected path` row follows it.
- The **Record** row no longer restates who reads the decision log.

**F. `harness-docs` current truth.**
- No repository file changes for this part. The pinned spec's delta is that change; archive applies
  it when the ticket closes. Archive is the step that folds an approved spec into current truth.

**Moves beyond the literal line targets.** I made three small moves so that detail the shorter
Built entries dropped keeps one home in README:
- "Adopting the factory in a repo" now says how a skipped gate command is reported. The checkers are
  told it is SKIPPED with the reason, the skip is recorded with the gate result, and the implementer
  still gets every command.
- The Code reviewer row in the roles table now says the reviewer leaves the test suite and the gate
  commands to the verifier.
- "How the factory uses git" took the catch-up consequence of a store commit, as described under C.

## Acceptance results

All 55 WHEN commands were extracted verbatim from the input. Each ran under bash from the worktree
root through the fresh-HOME wrapper. Logs are in the scratch directory: `base.txt` is on `7231670`,
before the change, and `final.txt` is on `08ad85e`.

NEW, before → after:
- Each build document carries the header and is otherwise unchanged:
  - before: `header=0 rest=changed`, for each of the three files;
  - after: `dev/build-harness.spec.md header=1 rest=same`, `dev/build-harness.plan.md header=1 rest=same`, `dev/P0-intake-skeleton.md header=1 rest=same`.
- The briefing no longer asks a change to keep the build spec in step:
  - before: `buildspec=3 frozen=0 readme=0`;
  - after: `buildspec=0 frozen=1 readme=1`.
- README no longer calls run features untried, and keeps the claims that are still true:
  - before: `stale=7 replan=1 paths=1 drive=1 tripwire=1 sibling=1 effort=1`;
  - after: `stale=0 replan=0 paths=0 drive=0 tripwire=1 sibling=1 effort=1`.
- The Built rule asks for run status, and the design doc's date line points to the changelog:
  - before: `rule=0 date=0 old=1`;
  - after: `rule=1 date=1 old=0`.
- Each Built entry is a short pointer, and each mechanism's detail has one home:
  - before: `fence=long driver=long tripwire=long sibling=long drift=long empty=long paths=long stats=long host=long skip=2 store=3 drivefence=1 notbuilt=5`;
  - after: `fence=pointer driver=pointer tripwire=pointer sibling=pointer drift=pointer empty=pointer paths=pointer stats=pointer host=pointer skip=1 store=1 drivefence=0 notbuilt=0`.
- The glossary points to Where it runs and defines protected path once:
  - before: `rows=4 pointer=0 protected=0 merge=1 record=1`;
  - after: `rows=0 pointer=1 protected=1 merge=0 record=0`.
- README keeps its issue references and drops the moved history, and the changelog records the move:
  - before: `history=5 refs=19 figures=1 pointer=0 entries=0 terms=0`, then `CONTIGUOUS`;
  - after: `history=0 refs=19 figures=0 pointer=1 entries=1 terms=6`, then `CONTIGUOUS`.
- README is at most 1,110 lines:
  - before: `readme=over`;
  - after: `readme=within`. `wc -l README.md` prints 1106.

All eight before-outputs match the spec's verification.md.

REGRESSION, after: all 47 print exactly their THEN on `08ad85e`.
- Their output is identical to the base run line for line. The one exception is "The reviewer's
  input no longer hands it the gate commands...", which cannot run without its setup.
- That scenario needs two setup blocks from current truth. I extracted the shell blocks of "A ruling
  on a BLOCKED park..." (human-resolution) and "A reviewer that ends its turn waiting..."
  (build-dispatch). I ran them once with `TMPDIR` set to the scratch `tmp/`.
- It then printed `reviewer gates=0 told=1`, `verifier gates=1 told=0`,
  `implementer gates=1 told=0`. This matches its THEN.
- Examples of the restated changelog checks:
  - "The changelog records the change in order" printed `CONTIGUOUS`, then `9`.
  - "The changelog records issue 106 as entry 71..." printed `CONTIGUOUS`, `1`, `5`.
  - "The maintained documents pass git's whitespace check in full" printed `exit=0`.
- No REGRESSION command failed, so none needed a run on base.

Gate commands, run exactly as written from the worktree on `08ad85e`:
- `git diff --check main...HEAD`: exit 0, with no output. `main` is `7231670`.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `584 passed in 139.56s`, exit 0.

## Tests added/changed

None. The spec's "Tests to change" is none. No test reads `README.md`, `dev/`, `docs/changelog.md`
or `.factory/context.md`, and this change edits no code. The checks for this change are the
acceptance scenarios above.

## Known gaps and uncertainties

1. **The new pointer on `docs/design.md:70` is only partly backed.** It says the first `factory stats`
   figures are in principle 4 and changelog entry 70. In fact both hold only the code reviewer's
   figure (4 of 94 runs, 3 BLOCKING findings).
   - Before this change, line 70 was the only place with the other roles' figures and the token
     counts.
   - So that this history is not lost, entry 72 records them word for word: the critic's 19 of 84,
     the verifier's 8 of 108 and 1 of 5, and the implementer's 18 of 111, with their tokens.
   - I used the spec's exact pointer wording and did not add "and entry 72". The operator may want
     the pointer to name entry 72 too.
2. **I wrote a different ticket range than the spec.** Spec D.6 names "T-0032 to T-0051" for the
   one-sub-ticket path. This store's log has `plan.skipped` for T-0031 too, and for T-0048, this
   ticket. Entry 72 says "16 tickets from T-0031 to T-0051 here, five on the Nanobot store". No check
   reads this phrase.
3. **README has 4 lines of slack.** It is 1,106 lines against the 1,110 budget; the prototype had
   1,101. Two things account for the difference: the Adopting sentence I added, and "Related work and
   history" written as a list.
4. **Some detail is now only in `docs/design.md`.** It left README with the shortened Built entries:
   - Re-plan: a new plan may not depend on a sub-ticket it supersedes, and old merged sub-tickets
     count as done.
   - Drift: the two kinds of drift. The critic's cross-ticket check is still in the Spec critic
     row.
   - Empty output: the sentence that no time or token budget is enforced.
   - Tripwire: that killed runs are included and that no file contents are printed.
   - The OpenSpec origin phrase.
   - The agent-host comparison table, which is at `docs/design.md:868`.
5. **The "Ground truth only" bullet is slightly at odds with the new "Not built" paragraph.** Spec B.6
   keeps the bullet's tail, which still says named work belongs under "Not built". The new "Not
   built" paragraph sends named work to "Where this can go".
6. **The live-store fence entry's status sentence is shorter.** It now reads "It has fired on a real
   target, when a stopped workflow left a run in flight". This fits the 3-line limit; the meaning is
   unchanged.
7. **The figures will go stale.** "51 tickets and 64 sub-tickets" was counted while this ticket was
   in flight, and the 64 includes T-0048.1. They stay true only until the next ticket is filed.
8. **The `dev/issues.md` row for #101 is not updated.** The spec does not ask for it. The row is
   normally updated when the ticket closes.

## Out-of-scope observations

- README "Parallel builds across tickets have not been tried": the spec noted this too, and I did
  not check it against the logs.
- `factory/cli.py:1`'s docstring cites "the build-harness spec". That file is harness code and
  protected.
- README "Where this can go" lists "**Many targets.**" as intended. Two targets already run on one
  runtime ("Where it runs"), so that bullet may describe something partly built. I did not change it,
  because that section changes only with the design.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 55 acceptance scenarios and both gate commands passed on the committed head, and every corrected claim was checked against the store logs.
ESCALATIONS: none

## Diff `7231670f2303856db8c1ed709a402be43c251754...08ad85edf30076259c47b7fc816976f45270e805`

diff --git a/.factory/context.md b/.factory/context.md
index 88c0e68..27f305a 100644
--- a/.factory/context.md
+++ b/.factory/context.md
@@ -6,9 +6,8 @@ design and the harness that runs it:
   `docs/changelog.md`;
 - `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
   by re-copying that block;
-- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
-  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
-  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
+- `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the
+  P0 walking skeleton, frozen as history from building the harness, which no change updates;
 - the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
   scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
   `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
@@ -32,8 +31,8 @@ line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live
 
 Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
 `git diff --check` against the documents, the harness suite). A change to the design doc keeps its
-own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
-consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.
+own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose
+block changed re-copied from it.
 
 The request is an issue draft, written from a real pipeline run: where in the documents,
 what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
diff --git a/README.md b/README.md
index 4eae6c9..8a81729 100644
--- a/README.md
+++ b/README.md
@@ -38,7 +38,7 @@ It does not stop a write to an absolute path.
 | Spec critic | judges the spec against a six-item rubric | Fable |
 | Planner | splits an approved spec into sub-tickets that can each be one merge | Opus |
 | Implementer | builds one sub-ticket on its own branch | Opus |
-| Code reviewer | judges the diff against the spec's intent | Fable |
+| Code reviewer | judges the diff against the spec's intent, and leaves the test suite and the gate commands to the verifier | Fable |
 | Verifier | runs the acceptance items and the gate commands on the result | Opus |
 | Retro | reads what went wrong and proposes rule changes (not yet built) | Fable |
 
@@ -91,8 +91,8 @@ directories and `models` entries use.
 | Verifier (`verifier`) | the same as the code reviewer; the final run on a parent gets the spec, where it works, and any ruling | VERIFIED · FAILED · SPEC-DEFECT | a verdict for that commit, `verifier.yaml`, and the gate result, `ci.yaml` |
 | Clerk (`clerk`) | one `bin/factory` command | none | nothing; it returns the command's output, exit code and errors to the script |
 
-A run that returns no output is recorded as killed, and its ticket parks. The retro has a model
-entry but no prompt and no way to run yet.
+A run that returns no output is run once more, then parks its ticket ("Empty output", under "What
+is built and what is not"). The retro has a model entry but no prompt and no way to run yet.
 
 ### What depends on Claude Code
 
@@ -124,7 +124,8 @@ agent hosts is under "Where this can go".
 | sub-ticket | one independently mergeable piece of a planned ticket; `T-0012.4` |
 | gate | a point where a human must decide before the pipeline continues; the spec gate is the main one |
 | gate commands | the target's own check commands, such as lint and tests (`gate_commands` in `instance.yaml`); the verifier runs them and records the gate result. No human is involved |
-| merge gate | the harness's check before a merge: both verdicts and the gate result on the same commit, which is the branch's tip and contains the integration branch, and every protected path the change touches declared in the approved spec. A protected path is one `instance.yaml` lists under `protected_paths` because a change to it is sensitive, such as the harness's own code. No human is involved, except that a refusal for an undeclared protected path parks the sub-ticket for a human |
+| merge gate | the harness's check before a merge: both verdicts and the gate result on the same commit, which is the branch's tip and contains the integration branch, and every protected path the change touches declared in the approved spec. No human is involved, except that a refusal for an undeclared protected path parks the sub-ticket for a human |
+| protected path | a path `instance.yaml` lists under `protected_paths` because a change to it is sensitive, such as the harness's own code |
 | checker | the code reviewer or the verifier: a role that judges a commit and cannot change it |
 | parent | a ticket that has sub-tickets; its final check verifies the whole spec |
 | PR description | the implementer's final report on what it changed; there is no pull request in local mode |
@@ -135,10 +136,7 @@ agent hosts is under "Where this can go".
 | round | one author-then-judge pass: the spec writer and the critic, or the implementer and both checkers; the spec and the code each get two before a human is asked |
 | integration branch | the branch finished sub-tickets are merged into; `integration_branch` in `instance.yaml`, `main` here |
 | current truth | one document per capability saying what the system does now; the pipeline keeps it |
-| target | a repo the factory works on |
-| instance | a target's `.factory/` directory: its config, its briefing for the roles, its store |
-| store branch | `factory-store`, the target's branch for its store; checked out as a git worktree at the store's path and never merged into the integration branch |
-| runtime | the pinned checkout of the harness that runs tickets; distinct from the dev checkout |
+| target, instance, runtime, store branch | defined under "Where it runs" |
 
 ## How a ticket moves
 
@@ -154,8 +152,8 @@ The build workflow first asks the harness whether the spec needs splitting, with
 from the whole spec, naming every scenario in it, and no planner runs. A spec needs only one when
 the spec writer did not mark it too large for one merge (`NEEDS-SPLIT`), no heading in it names
 seams (the places the writer says the work splits), and no planner has run on it before. Otherwise
-the planner runs, splitting the spec into sub-tickets with dependencies. The one-sub-ticket path is
-tested, and has not yet run on a real ticket.
+the planner runs, splitting the spec into sub-tickets with dependencies. The one-sub-ticket path
+has run on real tickets on both targets.
 When a sub-ticket's dependencies are merged, an implementer builds it on a branch in its own
 working copy. The reviewer and the verifier then judge the same commit, independently. The harness
 makes one decision from their verdicts: merge; send back for one revision; send back
@@ -163,14 +161,11 @@ to merge in a `main` that moved; or park for a human. A merge is a local `--no-f
 judged commit into the integration branch, one merge at a time.
 
 When every sub-ticket has merged, one more verifier run checks the whole spec against the
-integration branch. That final run is skipped when the spec had one sub-ticket, the text of that
-sub-ticket names every acceptance scenario of the spec (a command with its expected output), and
-the integration branch has not moved since it merged: the sub-ticket's verifier already checked
-the same code against the same starting point. On success the harness folds the spec into current truth and closes the
-ticket. If the target has no spec store yet (no `openspec/` tree), the fold is refused and the
-ticket parks; the human then closes it as applied with `resolve --close`, and current truth is
-not updated. While that final run is in progress, the ticket's record lists it as in flight, like
-any other run.
+integration branch. In one narrow case that run is skipped ("The build workflow, step by step").
+On success the harness folds the spec into current truth and closes the ticket. If the target has
+no spec store yet (no `openspec/` tree), the fold is refused and the ticket parks; the human then
+closes it as applied with `resolve --close`, and current truth is not updated. While that final
+run is in progress, the ticket's record lists it as in flight, like any other run.
 
 At any step a role can say it needs a human: a question, an escalation, a blocked build. The
 harness parks the ticket. So does running out of rounds, or a role that ended without output
@@ -327,8 +322,11 @@ checkers on the same commit. The harness's join turns their verdicts into one de
 - **park**: anything else.
 
 When every sub-ticket has merged, one more verifier run checks the whole spec on the integration
-branch. That run is skipped when the ticket had a single sub-ticket, its sub-ticket text names
-every scenario, and the branch has not moved since its merge. On VERIFIED, `archive` folds the spec into current truth and closes the ticket.
+branch. That run is skipped when the spec had one sub-ticket, the text of that sub-ticket names
+every acceptance scenario of the spec (a command with its expected output), and the integration
+branch has not moved since it merged. In that case the sub-ticket's verifier already checked the
+same code against the same starting point. On VERIFIED, `archive` folds the spec into current
+truth and closes the ticket.
 
 ```mermaid
 flowchart TD
@@ -372,11 +370,8 @@ Three places:
 - Each **target** holds only a `.factory/` directory, its instance: `instance.yaml` (config),
   `context.md` (the briefing every role reads first), the store, and `harness.lock`, the one
   harness commit this target has agreed to run with. The store is the target's record of every
-  ticket. A store that `factory init` creates is a git worktree of the store branch,
-  `factory-store`, at a path the integration branch has never tracked, so committing the store
-  never moves the integration branch. Two targets run on the runtime today: this repo and a
-  chat-bot repo. Both stores were made before the store branch existed and were moved onto it, at
-  `.factory/store`, with `factory store migrate`.
+  ticket, a git worktree of its own branch, the store branch `factory-store` ("How the factory
+  uses git"). Two targets run on the runtime today: this repo and a chat-bot repo.
 
 ```mermaid
 flowchart TB
@@ -503,8 +498,8 @@ The harness changes git in five ways, all local; it never pushes.
   path, creating the branch with no history when none exists, and adds the path to the repo's git
   exclude file. `factory store migrate` creates the branch from an existing store, with one commit.
 - **The store branch.** `factory-store` is a separate line of history that is never merged into
-  the integration branch, so committing a record never moves the branch that sub-tickets merge
-  into.
+  the integration branch, so committing a record never moves the integration branch or sends a
+  sub-ticket waiting to merge back for a catch-up run.
 
 ```mermaid
 gitGraph
@@ -595,13 +590,14 @@ From inside the target repo, with `R` the runtime (`~/dev/spec-factory-harness`)
    run its tests, what kind of request to expect. Set `gate_commands` and `protected_paths` in
    `.factory/instance.yaml`. A `gate_commands` entry may declare `paths`, the git pathspecs the
    command covers: `{command: "<command>", paths: [":(exclude)dev/"]}`. A sub-ticket whose changes
-   touch none of them skips that command. Prefer exclude pathspecs, so a new file still runs the
-   command. A command with no `paths` runs on every sub-ticket, so an instance that declares none gets
-   no skips. Set `run_env` for any tool whose cache lives under HOME,
-   so it still finds that cache from inside the fresh temporary HOME. Set `environment_sync` to the
-   command that installs the repo's environment (for example `uv sync --frozen`), so each build
-   checkout starts synced: `run start` runs it in the checkout before the role starts, and refuses
-   the run if it fails.
+   touch none of them skips that command: the checkers are told it is SKIPPED, with the reason,
+   and the skip is recorded with the gate result. The implementer still gets every command. Prefer
+   exclude pathspecs, so a new file still runs the command. A command with no `paths` runs on every
+   sub-ticket, so an instance that declares none gets no skips. Set `run_env` for any tool whose
+   cache lives under HOME, so it still finds that cache from inside the fresh temporary HOME. Set
+   `environment_sync` to the command that installs the repo's environment (for example
+   `uv sync --frozen`), so each build checkout starts synced: `run start` runs it in the checkout
+   before the role starts, and refuses the run if it fails.
 
 The repo is now a target. "Starting a run" is the rest.
 
@@ -616,8 +612,7 @@ git -C "$S" add -A && git -C "$S" commit -m "store: <what changed>"
 git push origin factory-store
 ```
 
-A store commit never moves the integration branch, so it never sends a sub-ticket that is waiting
-to merge back for a catch-up run. Commit when a workflow finishes and before moving the runtime.
+Commit when a workflow finishes and before moving the runtime.
 Records that are not committed exist only in that checkout.
 
 ### Backing up or cloning a target
@@ -709,9 +704,9 @@ $RUNTIME/bin/factory paths      # the harness, its entry point, both workflow sc
 It then calls the Workflow tool with `scriptPath` set to the intake script and args
 `{ticket, repo: <runtime>, instance: <.factory>}`. After the spec gate, the same call with the build
 script. Add `inlineRoles: true` on every target for now: `agents/` ships agent definitions only for
-the intake roles and the planner, so a build without it fails at the first implementer call. With it, roles
-read their prompt from the run's `system-prompt.txt`, and run without per-role tool limits. Start the
-build script after the spec gate; the intake script has nothing to do past it.
+the intake roles and the planner, so a build without it fails at the first implementer call. "What
+depends on Claude Code" says what it changes. Start the build script after the spec gate; the
+intake script has nothing to do past it.
 
 In practice you ask the runner session in plain words, for example "run the intake workflow for
 T-0032 with inlineRoles". The Workflow tool runs in the background; Claude Code's `/workflows` view
@@ -725,8 +720,10 @@ same state.
 It takes a ticket through the same routes as the scripts, with the same round limits and park
 reasons, and writes the same records. It calls the harness in its own process, so no clerk agent
 relays store commands. Each role runs as its own headless `claude -p` process, with that role's
-prompt, model and tool limits. The driver is tested, and has not yet run a real ticket. Until it
-has, the Workflow tool remains the tested route.
+prompt, model and tool limits. A role's file tools may edit only the run's output file, its scratch
+directory and the temporary directory; the implementer may also edit its own worktree. Shell
+commands are not limited. It has taken real tickets through intake and the build on the chat-bot
+target.
 
 1. From the target repo, start it on one ticket:
 
@@ -752,16 +749,12 @@ has, the Workflow tool remains the tested route.
    `KILLED`, parks nothing, and exits with 128 plus the signal number. Run the same command again to
    resume from the stored state.
 
-The driver needs no `FACTORY_DISPATCH=1`, even while runs of other tickets are in flight on the
-target. It is the dispatcher, the one process meant to write the store while runs work, so the
-live-store fence ("Where a human decides") exempts it from its in-flight check. Once started, it
-marks its own store calls. Its role processes never carry the marker. In place of that check, it
-guards the ticket it drives. It refuses to start on the same ticket, with exit 2 and nothing
-written, while that ticket or one of its sub-tickets has a run in flight. It also refuses while
-`drive/<ticket>.yaml` shows another driver of that ticket still running. From inside the store's
-`runs/` or `worktrees/` it is refused like any write, marker or not. A driver killed by SIGKILL has
-no chance to stop, so its runs stay in flight; clear them as "Where a human decides" says. If the
-refusal names a pid that is not a driver, delete that status file and drive again.
+The live-store fence ("Where a human decides") exempts the driver, because it is the dispatcher. It
+marks its own store calls, and never its role processes'. It guards the same ticket instead: it
+refuses with exit 2, writing nothing, while that ticket or a sub-ticket has a run in flight, or
+while `drive/<ticket>.yaml` shows another live driver. If the refusal names a pid that is not a
+driver, delete that file. A driver killed by SIGKILL leaves its runs in flight; clear them as
+"Where a human decides" says.
 
 Each role process's reply is kept as `reply.json` in its run directory. Its session id, cost in
 dollars, turn count and token usage are recorded under `claude:` in the run's `meta.yaml`. To give a
@@ -816,17 +809,14 @@ length on every one of those turns. The Nanobot port runs this way: its runner (
 reports harness problems to the session that owns this repo, which fixes them through tickets here.
 
 **Parallel intake works today.** Start one intake per ticket from a runner. Tickets share only the
-store, and every store write goes through `bin/factory`, which allocates run ids atomically. On
-2026-10-04 the two stores had 41 and 11 overlapping runs of different tickets (triage, spec writers,
-critics, planners). Each run has its own scratch directory in the store for its temporary files,
-cleared when its ticket moves on and kept while it is parked; this is tested but has not yet run on a
-real ticket.
+store, and every store write goes through `bin/factory`, which allocates run ids atomically. Each
+run has its own scratch directory in the store for its temporary files, cleared when its ticket
+moves on and kept while it is parked.
 
 **Parallel builds across tickets have not been tried.** Each sub-ticket builds in its own worktree,
 merges into the integration branch one at a time under a lock, and gets a catch-up run if the branch
 moved under it. Two builds at once also move the branch under each other, which costs catch-up runs.
-A store committed on its store branch no longer moves the integration branch. Until a real run
-shows the cost, run one build at a time per target.
+Until a real run shows the cost, run one build at a time per target.
 
 **Moving the runtime** happens only when no build is in flight on any target, because every target
 runs from the same runtime. Each target's runner then accepts the new revision between its builds.
@@ -865,7 +855,7 @@ FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLE
 | **Gate** | `factory approve-spec T-n [--edit F]` · `factory request-changes T-n F` · close | the spec's intent, risk declarations, operator steps, "tests to change"; a gate edit becomes a new spec version and is what gets pinned |
 | **Amend** | `factory spec amend T-n --file F --reason "<line>" --intent unchanged`, on an approved spec before archive, while no run is in flight on the ticket or its sub-tickets | that the approved spec must change after the gate, because another ticket merged first, a checker found a scenario that cannot pass as written, or you changed your mind. Amend only when the Problem, the Decisions and every requirement's statement stay as approved; otherwise restart, by re-spec and re-plan or by close and re-file. `--intent changed` prints what a restart keeps and discards. Later runs receive the amended version, but the amendment moves no ticket: resume it as usual, for example with `--ruling F` |
 | **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, the harness blocked an implementer whose sub-ticket lists a test no merged sibling added, the harness parked a sub-ticket for spec drift, or the harness failed to start an implementer run, a `harness-bug: run start implementer:` park; a ruling on the code reviewer's escalation re-runs the checks, with the ruling in their input) · `--accept-paths F` (the merge gate refused a protected path the approved spec does not declare: accept it under the approved design, and the sub-ticket returns to its checks; `--ruling F` sends the sub-ticket back to its implementer instead) · `--redispatch` (re-run the checks on the same commit after an outside fix, or after a checker ended without output twice) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, an accepted protected path, a re-check, a re-plan, a re-scope, or closing |
-| **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included. It appends one dated line to the target's decision log, `decisions.md`, which the spec writer, critic and planner receive with their input | that a decision binds later tickets |
+| **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included: one dated line in the decision log | that a decision binds later tickets |
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
 A ticket the tripwire parked returns with a plain `ticket transition` to the state its record
@@ -936,120 +926,65 @@ the column can undercount.
 - **Intake.** A request becomes a ticket. Triage accepts or routes it. The spec writer and critic
   alternate until the critic approves or two rounds are up. The ticket waits for the human at the
   gate. Every one of these runs has been real, with real models.
-- **Build, local-only.** There is no remote git server, no pull request and no CI service yet. In
-  their place: each sub-ticket is built on a branch in its own working copy. The verifier runs the
-  repo's own check commands (`gate_commands` in `instance.yaml`: lint, tests) and records the
-  result where a CI result would go. The reviewer and verifier judge the same commit. A sub-ticket
-  that passes is merged into the local integration branch, one merge at a time. If `main` moved
-  during the build, the implementer merges it in before the checks re-run; two catch-up runs that
-  fail to merge it in park the sub-ticket. A check command that declares the paths it covers is
-  skipped for a sub-ticket whose changes touch none of them: the reviewer and verifier are told it
-  is SKIPPED, with the reason, and the skip is recorded with the check result. The implementer
-  still gets every command. The skip is tested, and no repo's configuration uses it yet.
-- **Spec store.** Specs live in an OpenSpec tree, a folder-per-change layout borrowed from the
-  OpenSpec project. A ticket's spec is a set of deltas against current truth. When a ticket closes,
-  `archive` applies the deltas, so the description of the system is kept current by the pipeline.
+- **Build, local-only.** There is no remote git server, no pull request and no CI service yet. Each
+  sub-ticket is built on its own branch, judged on one commit by the reviewer and the verifier,
+  and merged into the local integration branch one at a time ("How the factory uses git"). A gate
+  command that declares `paths` is SKIPPED for a sub-ticket that touches none of them ("Adopting
+  the factory in a repo"). The skip is recorded on a real sub-ticket.
+- **Spec store.** Specs live in an OpenSpec tree, as deltas against current truth. When a ticket
+  closes, `archive` applies the deltas, so the pipeline keeps the description of the system current.
 - **Instances and the harness lock.** One runtime serves any number of targets. Each adopts a new
   harness revision only when its operator accepts it. See "Where it runs".
-- **Store branch.** Each target's records live on `factory-store`, checked out at
-  `.factory/store`, so committing a record never moves the integration branch. Both targets'
-  stores were moved there with `factory store migrate`.
-- **Tripwire on live files.** An instance can list files outside the repo that no role run should
-  change, such as a live bot's credentials, under `tripwire` in `instance.yaml`: a `park` list and
-  an `escalate` list. The harness hashes each file when a run starts and compares when the run ends,
-  killed runs included. A changed `park` file parks the ticket; a changed `escalate` file is queued
-  for the operator and the run goes on. Neither prints a file's contents. It is tested, and has not
-  yet fired on a real ticket.
-- **Live-store fence.** While a run is in flight on a target, a write to its store without the
-  `FACTORY_DISPATCH=1` marker is refused. The workflow scripts mark their own commands, and the
-  operator marks one command at a time ("Where a human decides"). `factory drive` is exempt from
-  this in-flight check, because it is the dispatcher. It guards its own ticket instead: it refuses
-  to start on a ticket that has a run in flight or another live driver. Once started, it marks its
-  own store calls, and its role processes are never marked. A write run from inside the
-  store's `runs/` or `worktrees/` is refused even with the marker. The fence stops a role's tools,
-  such as its test suite, from changing the live records by accident; it is not isolation. It has
-  fired on a real target: a run left in flight by a stopped workflow blocked writes until the
-  operator finished it.
-- **Sibling tests check.** The planner may let a sub-ticket change a test file that an earlier
-  sub-ticket of the same spec added, for example a test that pinned that earlier sub-ticket's
-  interim behaviour. Before each implementer run, the harness checks in git that a merged earlier
-  sub-ticket added the file. If none did, the sub-ticket parks as blocked, and the human rules on it
-  as on any blocked build ("Where a human decides"). Any other existing test still changes only if
-  the approved spec lists it. It is tested, and has not yet fired on a real ticket.
-- **Spec amendment and drift.** An approved spec can go stale while its sub-tickets are built:
-  another ticket merges first, or a scenario turns out unable to pass as written.
-  `factory spec amend` replaces the approved spec with a corrected version, when the correction
-  keeps what the ticket is for ("Where a human decides"). Later runs receive the corrected version,
-  and archive writes its scenarios into current truth. Spec drift is a change since the spec was
-  written that the spec did not plan for. Before a sub-ticket's first implementer run, the harness
-  checks for two kinds: the sub-ticket's acceptance checks name another sub-ticket of the same
-  spec that has not merged and is not one of its dependencies, or a test changed beside a file the
-  spec names, and no "Tests to change" list names it. A merge of another sub-ticket of the same
-  spec is not drift, because the plan expects its changes; any other commit or merge still counts.
-  On drift the sub-ticket parks as blocked, and the human amends the spec or rules on it. The
-  critic also receives every other approved spec not yet archived, and blocks a scenario whose
-  setup would not hold whichever of the two tickets merges first. The drift check has fired on
-  real sub-tickets, twice for a sibling's merge; that exception is tested but has not yet run on a
-  real ticket.
-- **Re-plan after a re-spec.** When the human sends a planned parent back to the spec gate and
-  approves a new spec version, the planner splits it again under the same parent. Each sub-ticket
-  records the approved version it was planned from. The new plan supersedes the old plan's
-  sub-tickets that have not merged: they keep their records and ids, but are no longer dispatched,
-  no longer park the parent, and no longer hold back its final check or close. Old sub-tickets that
-  merged stay merged and count as done work. A new plan may not depend on a sub-ticket it
-  supersedes. It is tested, and has not yet fired on a real ticket.
-- **Empty output.** A role run that ends without writing its output file is run once more on the
-  same inputs, and the harness keeps the agent's last message with the run. A second run in a row
-  that ends the same way parks the ticket. When either run's last message says it was still waiting
-  on a command it started, the park reason adds `ended its turn waiting on a background command`,
-  because a plain re-run is likely to end the same way. The harness enforces no time or token budget and cannot
-  tell why a run stopped, so it never labels such a run a budget kill. The code reviewer judges the
-  diff and leaves the test suite and the gate commands to the verifier. Every role is told to wait
-  for the commands it starts before it ends its turn. It has fired on a real ticket: both runs of
-  one verifier ended their turns waiting for the test suite.
-- **Protected paths at merge.** The merge gate refuses a change to a protected path that the
-  approved spec does not declare on the `Protected paths:` line of its Risk section, and names
-  each such path. The human approves that line at the spec gate, so a declared path merges with
-  no further approval. A refused sub-ticket parks as blocked. The human answers with
-  `resolve --accept-paths F`, which accepts the paths for that sub-ticket and returns it to its
-  checks, whose passing results stand, or with `resolve --ruling F`, which sends it back to its
-  implementer. It is tested, and has not yet fired on a real ticket.
-- **The driver, `factory drive`.** An ordinary command that takes a ticket through intake, or
-  through the build after the spec gate, on the same routes as the workflow scripts: the same round
-  limits, refusals and park reasons, and the same records. It calls the harness in its own process,
-  so no clerk agent relays store commands. Each role runs as one `claude -p` process with its
-  role's prompt and model, under Claude Code's `auto` permission mode. Its file tools may edit only
-  the run's output file, its scratch directory and the temporary directory; the implementer may
-  also edit its own worktree. Shell commands are not limited. Each process's reply and cost are
-  recorded with its run. A commit's two checkers run at once, and ready sub-tickets build at once
-  up to `--parallel N`. The workflow scripts are unchanged beside it. It is tested, and has not yet
-  run a real ticket.
+- **Store branch.** Each target's records live on their own branch, `factory-store`, checked out
+  as the store ("How the factory uses git").
+- **Tripwire on live files.** The harness hashes the files outside the repo that `tripwire` in
+  `instance.yaml` lists, such as a live bot's credentials, when a run starts and ends. A changed
+  file parks the ticket or is queued for the operator (`docs/design.md`, "Tripwire on live files").
+  It is tested, and has not yet fired on a real ticket.
+- **Live-store fence.** While a run is in flight, a store write without the `FACTORY_DISPATCH=1`
+  marker is refused ("Where a human decides"). It guards against accidents and is not isolation.
+  It has fired on a real target, when a stopped workflow left a run in flight.
+- **Sibling tests check.** Before each implementer run, the harness checks in git that a test the
+  sub-ticket may change as added by a sibling was added by a merged earlier sub-ticket of the same
+  spec. If not, the sub-ticket parks as blocked (`docs/design.md`, "Tests a sibling added"). It is
+  tested, and has not yet fired on a real ticket.
+- **Spec amendment and drift.** `factory spec amend` replaces an approved spec with a corrected
+  version that keeps what the ticket is for ("Where a human decides"). A change the spec did not
+  plan for parks a sub-ticket as spec drift before its first implementer run; a sibling's merge
+  is not drift (`docs/design.md`, "Spec drift"). The drift check has fired on real sub-tickets;
+  the sibling-merge exception is tested but has not yet run on a real ticket.
+- **Re-plan after a re-spec.** When a planned parent's spec goes back to the gate and a new version
+  is approved, the planner splits it again under the same parent. The new plan supersedes the old
+  plan's unmerged sub-tickets, which keep their records but are no longer dispatched or waited on.
+  It has fired on a real ticket.
+- **Empty output.** A role run that ends without writing its output is run once more on the same
+  inputs. A second in a row parks the ticket, and the reason adds `ended its turn waiting on a
+  background command` when either run's last message says it was waiting (`docs/design.md`,
+  "Routing table"). Every role is told to wait for its commands before it ends its turn. It has
+  fired on a real ticket: both runs of one verifier ended their turns waiting for the test suite.
+- **Protected paths at merge.** The merge gate refuses a protected path that the approved spec's
+  Risk section does not declare ("How the factory uses git"), and the sub-ticket parks for the
+  human ("Where a human decides"). It has fired on a real ticket, which the operator accepted with
+  `--accept-paths`.
+- **The driver, `factory drive`.** A command that takes a ticket through intake or the build on the
+  workflow scripts' routes, each role as one `claude -p` process ("Driving a ticket from a shell
+  with `factory drive`"). The workflow scripts are unchanged beside it. It has taken real tickets
+  through both on the chat-bot target.
 - **Per-role effort, for driver runs only.** An optional `effort:` map in `instance.yaml` gives a
   role an effort level, which `factory drive` passes to that role's process. A role not listed gets
   Claude Code's default. The workflow scripts ignore the map, so a role they run has a model and no
   effort level. Neither target sets it yet.
-- **Counting catch and cost, `factory stats`.** A command that reads one or more stores and
-  prints, per role and model, the runs, verdicts, outcome changes, BLOCKING findings and tokens;
-  where tickets park; and which runs wrote and critiqued each spec a later role found defective
-  ("Counting what each role catches and costs"). It takes a run's tokens from its cost record,
-  else from its Claude Code transcript, and counts each model call once. `factory/cost.py` now
-  counts the same way; it used to count most calls about twice. `factory stats` writes nothing,
-  and it skips the live-store fence and the harness lock. It has run over both targets' stores.
+- **Counting catch and cost, `factory stats`.** A read-only command that counts, per role and
+  model, how often each role's verdicts changed what happened next and what its runs cost
+  ("Counting what each role catches and costs"). It has run over both targets' stores.
 
 **Not built**
 
-- **Rendering the prompts.** The role prompts in `docs/prompts/` are copied from the design doc by
-  hand. The planned `factory render` command that would generate and check them does not exist.
-- **Remote mode.** Pull requests, a CI service running the checks, and a separate git identity per
-  role with server-side permissions. Today one machine and one identity do everything. That is fine
-  for one operator and not for a team.
-- **The retro role.** Reads the log and proposes changes to the prompts and rules from what went
-  wrong. No run has produced one yet.
-- **A status page.** `factory report TICKET` would render where a ticket is from the store alone.
-  Today you read the store's YAML or ask the session running it.
-- **Current truth for the factory itself.** The spec store holds only the capabilities that
-  tickets have changed since it was created, not the whole factory. This page is the hand-written
-  stand-in for the rest until they are written from the tests.
+Everything under "Where this can go" is named work, not built. Today one machine and one identity
+do everything, which suits one operator and not a team. The role prompts in `docs/prompts/` are
+copied from the design doc by hand. No retro has run. This page stands in for the capabilities no
+ticket has changed since the spec store was created. The status page, `factory report TICKET`, is
+not built; today you read the store's YAML.
 
 ## Where this can go
 
@@ -1064,7 +999,7 @@ from `docs/design.md` and changes only when the design does.*
   not move it are reverted.
 - **Generated prompts.** `factory render` produces `docs/prompts/` from the design doc and
   `render --check` refuses drift, so the design doc is the only place a prompt is edited.
-- **The factory described by itself.** Its own capabilities in current truth, kept there by
+- **Current truth for the factory itself.** Its own capabilities in current truth, kept there by
   `archive`, so a page like this one is written from the spec store instead of by hand.
 - **Many targets.** Any repo adopts the factory with `factory init`; one runtime serves them all,
   each on the revision it accepted.
@@ -1072,27 +1007,10 @@ from `docs/design.md` and changes only when the design does.*
 ### Running on another agent host
 
 The factory should run on any agent host that can start an agent with a given prompt, model and
-working directory, and return its answer in a fixed shape. The store CLI, the prompts, the spec
-format and the store carry over unchanged. Only the pieces in "What depends on Claude Code" need a
-counterpart. Neither OpenAI Codex nor Google Antigravity has a scripted orchestrator inside the
-agent session like Claude Code's Workflow tool. On either host, the workflow logic would move into
-an ordinary script that starts one headless agent run per role and reads its JSON reply. That
-script can call `bin/factory` itself, so the clerk role goes away. On Claude Code that script
-exists: `factory drive`, described under "Starting a run".
-
-| Need | Claude Code (today) | OpenAI Codex | Google Antigravity |
-|---|---|---|---|
-| Orchestrator | a Workflow tool script | an external script on the Codex SDK, or `codex exec` per role | an external script calling `agy -p` per role, or its Python SDK |
-| Reply in a fixed shape (the clerk's, today) | `agent(..., {schema})` | `--output-schema` | `--json-schema` |
-| Role definition | `.claude/agents/<role>.md`, or the prompt passed inline | `.codex/agents/<role>.toml` | `.agents/agents/<role>.md` |
-| Model per role | any Claude model | any OpenAI model, with a reasoning effort | Gemini tiers: `flash`, `pro`, `inherit` |
-| Tool limits for checkers | a tool list per agent | sandbox mode and MCP servers; no per-tool list found | a `tools` allowlist |
-| Project instructions | `CLAUDE.md` | `AGENTS.md` | `AGENTS.md`, `GEMINI.md` |
-
-On Antigravity, a tool call that needs approval is refused quietly and the run still exits 0. A port
-must therefore treat a missing reply as a failure. The table comes from each host's documentation,
-read on 2026-10-04, and has not been tried. The design is in `docs/design.md`, "Running on another
-agent host".
+working directory, and return its answer in a fixed shape. The store CLI, the prompts and the store
+carry over; only the pieces in "What depends on Claude Code" need a counterpart. On Claude Code
+that counterpart is `factory drive`. The comparison with OpenAI Codex and Google Antigravity, which
+has not been tried, is in `docs/design.md`, "Running on another agent host".
 
 ## Where things live
 
@@ -1108,7 +1026,7 @@ agent host".
 | `docs/golden.md` | The fixed golden set every prompt-change replay runs, with each entry's base and known catch, the baseline table, and the rule for changing the set |
 | `docs/writing.md` | The writing standard for every section a person reads; the preamble names the runtime's copy |
 | `docs/coding.md` | The coding standard for the implementer and code reviewer; their prompts name the runtime's copy |
-| `dev/` | Working documents from building the factory: the build spec, its plan, the P0 walking skeleton, the issue index (`dev/issues.md`) |
+| `dev/` | The issue index (`dev/issues.md`), kept live; and the build spec, its plan and the P0 walking skeleton, frozen as history from building the factory |
 | `factory/` | The harness package: the store CLI, its role prompts and its two workflow scripts (`factory/workflows/`) |
 | `bin/factory` | The harness entry point |
 | `agents/` | The role-agent templates `factory init` copies into a target's `.claude/agents/` |
@@ -1117,26 +1035,24 @@ agent host".
 
 ## Related work and history
 
-First written 2026-10-03, after the layout refactor (issue #19, ticket T-0012 on this repo: six
-sub-tickets merged, the whole spec verified 30/30 by the factory itself, then closed as applied
-because this repo had no spec store yet) and the first end-to-end builds on the chat-bot repo
-(issues #16 and #18). The two targets are this repo (instance B) and the nanobot fork at
-`~/dev/nanobot-upstream` (instance A); both run on the shared runtime, and both stores moved onto
-their store branch on 2026-10-04. The architecture subsections (what each role reads and writes,
-ticket states, both workflows step by step, what the factory keeps in a target, how it uses git,
-filing from an issue tracker, what you read at each stop, other agent hosts) were added on
-2026-10-04 at the operator's request; the target layout answers issue #55. Open work named above:
-`factory report` (#17); current-truth seeding (#21); registered agents for
-the build roles, which `inlineRoles` works around today (#24); a stopped run that stays in flight
-(#53). The driver, `factory drive`, answers #65 and absorbs per-role effort (#22), the operator's
-latest chat message reaching every role agent (#28), titles beside ticket ids in progress output
-(#47) and the checkers' tool limits (#24 part A); retiring the workflow scripts is a later ticket. `factory stats` answers #70 and absorbs the double count in `factory/cost.py` (#61);
-feeding its figures to the retro is #42. Earlier sources: prompt changes borrowed from the ponytail project (#20); the documentation
-standard this page follows (#23); each run's scratch directory (#35); the store branch (#46). The
-design document is `docs/design.md`, its changelog `docs/changelog.md`; the working documents from
-building the harness are under `dev/`; the issue index is `dev/issues.md`. The store holds 51
-tickets and 63 sub-tickets at `.factory/store/`; the runtime is at `~/dev/spec-factory-harness`,
-commit `9dbd4f8`, and its harness revision `5e00a1f` equals this repo's `harness.lock`.
+- Earlier work: the first end-to-end builds on the chat-bot repo (#16, #18); the layout refactor
+  (#19); prompt changes borrowed from the ponytail project (#20); the documentation standard this
+  page follows (#23); each run's scratch directory (#35); the store branch (#46); the target layout
+  (#55).
+- The driver, `factory drive` (#65). It absorbs per-role effort (#22), the operator's latest chat
+  message reaching every role agent (#28), titles beside ticket ids in progress output (#47) and
+  the checkers' tool limits (#24 part A). Retiring the workflow scripts is a later ticket.
+- `factory stats` (#70). It absorbs the double count in `factory/cost.py` (#61); feeding its
+  figures to the retro is #42.
+- Open work named above: `factory report` (#17); current-truth seeding (#21); registered agents
+  for the build roles, which `inlineRoles` works around today (#24); a stopped run that stays in
+  flight (#53).
+
+The two targets are this repo (instance B) and the nanobot fork at `~/dev/nanobot-upstream`
+(instance A); both run on the shared runtime. How this page and the design came to be is in
+`docs/changelog.md`; the issue index is `dev/issues.md`. The store holds 51 tickets and 64
+sub-tickets at `.factory/store/`; the runtime is at `~/dev/spec-factory-harness`, commit
+`9dbd4f8`, and its harness revision `5e00a1f` equals this repo's `harness.lock`.
 
 ## Maintaining this page
 
@@ -1145,9 +1061,9 @@ by whoever changes the system, in the same ticket, and the code reviewer checks
 document.
 
 - **Ground truth only above "Where this can go".** A thing appears in the sections above only
-  after it has run on a real ticket. Until then it belongs under "Where this can go" (if the design
-  intends it) or under "Not built" (if it is named work). Never describe an intended behaviour in
-  the present tense.
+  once it is built and tested, and its entry says whether it has yet run on a real ticket. Until it
+  is built, it belongs under "Where this can go" (if the design intends it) or under "Not built"
+  (if it is named work). Never describe an intended behaviour in the present tense.
 - **Update with the change, not after it.** A sub-ticket that changes a command, a state, a stop
   or a path updates the sentence that describes it, re-derives any figure it quotes (counts, dates,
   paths, commits), and bumps the date in the status header. The reviewer treats a stale sentence
@@ -1182,9 +1098,8 @@ each section comes from:
 | Related work and history | `.factory/store/tickets/`, `dev/issues.md`, `docs/changelog.md` | `ls .factory/store/tickets | wc -l`; `git log --oneline -20` |
 
 Then two checks before it lands, in this order. First, the session that owns the harness code
-reads the draft against the running revision and corrects every as-built fact (today this caught
-two: a target described as cut over that was not, and a bound stated on the wrong case). Second,
-an independent reader with no project context reads it against "Maintaining this page" and the
+reads the draft against the running revision and corrects every as-built fact. Second, an
+independent reader with no project context reads it against "Maintaining this page" and the
 writing standard; every term they stumble on is a finding. Both passes are the same ones the
 critic and reviewer run on a spec, applied to this document. When the factory's own capabilities
 are in current truth (#21), the first pass becomes a diff against the spec store and most of this
diff --git a/dev/P0-intake-skeleton.md b/dev/P0-intake-skeleton.md
index a284fbd..d8d7874 100644
--- a/dev/P0-intake-skeleton.md
+++ b/dev/P0-intake-skeleton.md
@@ -1,5 +1,7 @@
 # P0: intake walking skeleton
 
+> **Frozen as history.** This document records how the harness was first specified and built, and parts of it describe a design the code never had. It is no longer kept in step with `docs/design.md` or the code, and no change updates it; `README.md` and `docs/design.md` describe the system.
+
 Parent: `dev/build-harness.spec.md` (v4). This is not a sub-ticket of `dev/build-harness.plan.md`; it is a cut through it. It builds BH-1-lite, BH-4, and BH-5 and defers BH-2a, BH-2b, BH-3, BH-6, BH-7. Nothing built here is thrown away: the agent definitions, the `factory` CLI, and `intake.js` are the same files the full plan grows.
 
 ## Why first
diff --git a/dev/build-harness.plan.md b/dev/build-harness.plan.md
index 78ed91b..6aac12f 100644
--- a/dev/build-harness.plan.md
+++ b/dev/build-harness.plan.md
@@ -1,5 +1,7 @@
 # Plan: Build the spec factory, local-Mac v0 — sub-tickets (plan v2)
 
+> **Frozen as history.** This document records how the harness was first specified and built, and parts of it describe a design the code never had. It is no longer kept in step with `docs/design.md` or the code, and no change updates it; `README.md` and `docs/design.md` describe the system.
+
 Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory` (https://github.com/danielphang/spec-factory/blob/main/dev/build-harness.spec.md); approved text = `spec-build-v4.md` (STATUS NEEDS-SPLIT; 84 acceptance items, of which 71–84 are the gate's round-4 amendments A–N), pinned by the human gate. The v1 rulings stand (every Open question on its proposed default; same-user deploy keys for v0; post-hoc budget kill; standing allowlist for real runs, never `bypassPermissions`; first acceptance run interactive; Nanobot gate commands unknown and carried as BH-1's open question; split along seams S1–S5), plus the amendments and the doc-v5 deltas folded into them.
 Planner: planner · Plan version: 2 (re-plan after the gate amended the pinned spec; supersedes `plan-build-v1.md`) · Design doc: `spec-factory-v5.md`
 
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index f26c6cf..c6b5d9d 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -1,5 +1,7 @@
 # Spec: Build the spec factory, local-Mac v0 (Nanobot fork, branch `feat/lionbot-v3`)
 
+> **Frozen as history.** This document records how the harness was first specified and built, and parts of it describe a design the code never had. It is no longer kept in step with `docs/design.md` or the code, and no change updates it; `README.md` and `docs/design.md` describe the system.
+
 Ticket: (Triage, ACCEPT) "Build the spec-factory harness, smallest-thing-that-works variant"
 Spec version: 4 · Round: 4 (post-gate amend pass; round reset) · Writer: spec_writer
 Design doc: `/tmp/claude-0/-home-user/0cb0ba38-97f2-51cf-86de-970d4ebec94b/scratchpad/spec-factory-v5.md` (cited as "doc §<section>": doc §Harness table piece N, doc §Routing table, doc §Routing rules, doc §Human gates, doc §Shared preamble)
diff --git a/docs/changelog.md b/docs/changelog.md
index 59e1061..e686eb2 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -74,4 +74,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 70. After issue #70 (2026-10-11), where the operator could not tell which checks pay for themselves: the figures behind a model choice, such as the code reviewer changing an outcome in 4 of 94 runs, came from a hand-written count over both stores, and the one token report, `factory/cost.py`, counted most model calls about twice, because Claude Code writes one transcript record per streamed block of a reply and each record carries the whole call's usage (issue #61). `factory/cost.py` now counts each message id once, from its last record, and its `calls` column counts message ids. Measured over every transcript matched to a run when the change was specified, the old count was 1.89 times the new one for the Nanobot store and 1.94 times for this one; the new count of a driver run's transcript equals that run's cost record. A new command, `factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...` (`factory/stats.py`), reads one or more stores and prints four tables: runs and verdicts by role and model, with kills, changed outcomes, BLOCKING findings and the implementer's gate failures fixed before hand-off; parks by normalised reason, taking a park's corrected reason when the correction is dated before `--until`, with the spec gate, resolution and merge decisions; each spec defect a verifier or implementer caught, against the runs that wrote and critiqued that spec; and each role's wall time and tokens, from the run's cost record, else its transcript under `--transcripts`, else none. `--until` makes a past figure repeatable on a growing store. `stats` writes nothing and must read a live store during a run and from a checkout the instance has not accepted, so, like `paths`, it skips the instance lookup, the live-store fence and the harness lock and ignores `--accept-harness`; the fence's read-only list gains it. Its count corrects one figure in `docs/principles.md` §4: the reviewer's BLOCKING findings are 3, one in each REQUEST-CHANGES run, not 1. Rejected: JSON output, which no consumer needs yet; adding `stats` only to the fence's read-only list, since the lock would still refuse it outside the accepted runtime; searching `~/.claude/projects` by default, which ties the command to one machine's layout and costs about 12 seconds a call; counting every mention of BLOCKING, which counts "No BLOCKING findings", or the round-2 restatements marked RESOLVED; matching a transcript only by the store's current path, which loses every run from before an unrecorded store move; ignoring park corrections, which reports the error a human fixed, and applying corrections dated after `--until`, which moves a past figure; and reading gate failures from the implementer's output, which states only final results. Figures quoted from `factory/cost.py` before this change, such as those in entries 58 and 67, stay as history and are not restated.
 71. After issue #106 (2026-10-12), where both verifier runs of one sub-ticket started the harness suite in the background, ended their turns to wait for it and so wrote no output: one run of the suite took six to ten minutes, against the 10-minute limit of a single agent tool call. The ticket parked as `EMPTY-OUTPUT from verifier`, a reason that did not say why. The harness suite now runs across every CPU core with pytest-xdist, a new dev dependency, switched on once in `pyproject.toml` (`addopts = "-n auto"`), so the gate command and every scenario that runs the suite use it with no change to their text; one run measured 66.80 to 146.81 seconds when the change was specified, against 385.56 seconds one test at a time. A new test must not depend on test order, or share a file, port, environment variable or other process-wide state with another test outside its own `tmp_path`. Adding pytest-xdist is a deliberate exception to the 2026-10-04 decision not to add to what the gate needs. The suite's two stand-in `claude` programs now hold a file lock around their per-role call counter, so a copy of one role started beside another no longer reads the counter while the other rewrites it, which had now and then crashed a checker run under load. `factory run last-message` also prints `waiting`: true when the kept message contains, ignoring case, the word `wait` or `waiting`, or `still running`, `still in progress` or `in the background`. The driver and both workflow scripts park a second EMPTY-OUTPUT in a row as `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command` when either run was waiting, and as `EMPTY-OUTPUT from <role>` otherwise; the route itself is unchanged, and no role prompt changes. Rejected: calling the CLI in-process in the suite, which was faster but needs a module-table swap around every call and stops most CLI calls from crossing a real process boundary; adding `-n auto` to the gate command, which leaves every scenario that runs the suite running one test at a time; and deciding waiting in each caller or in a separate command, rather than once in `run last-message`.
 
+72. After issue #101 (2026-10-11), where the operator read two long maintained documents at every spec gate and parts of README were false: README explained several mechanisms two or three times, said six features had not yet run on a real ticket when the stores' logs showed they had, and kept project history; and the briefing asked every design change to keep `dev/build-harness.spec.md` in step though it describes a design the code never had. The three `dev/` build documents, `dev/build-harness.spec.md`, `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md`, are frozen as history: each gains a header at line 3 and is otherwise as it was at `7231670`, and no change updates them; `.factory/context.md` and README's `dev/` row say so, and the briefing no longer names them in a design change's conventions. `dev/issues.md` stays the live issue index. README's claims now match the logs: the one-sub-ticket path has run on real tickets on both targets (16 tickets from T-0031 to T-0051 here, five on the Nanobot store); the driver took T-0035 and T-0036 through intake and the build on the Nanobot target; a gate command's path skip is recorded for T-0036.1; the re-plan after a re-spec fired for T-0031; the protected-path refusal at merge fired for T-0044.1, which the operator accepted with `--accept-paths`; every run has its scratch directory; and a run with no output is run once more, not recorded as killed. The tripwire, the sibling-tests check and the drift check's sibling-merge exception still say they have not yet fired or run, and the effort entry that neither target sets it. README's rule for its Built list now admits a thing once it is built and tested and asks its entry to say whether it has yet run on a real ticket, and `docs/design.md` line 3 drops its own date and points here. Each mechanism has one home in README: the live-store fence under "Where a human decides", the driver and its same-ticket guard under its how-to, the final check's skip under "The build workflow, step by step", the store branch under "How the factory uses git", and other agent hosts only in `docs/design.md`; the Built entries become short pointers, "Not built" one paragraph that repeats nothing under "Where this can go", and the glossary points to "Where it runs" and defines a protected path in its own row. History moved out of README: the overlap of 41 and 11 runs of different tickets in the two stores on 2026-10-04, the double count `factory/cost.py` once made (entry 70), the two stores' moves onto their store branch with `factory store migrate`, the page's origin story and the regeneration pass's two past catches, a target described as cut over that was not and a bound stated on the wrong case; "Related work and history" keeps every issue reference beside what it names. `docs/design.md`'s model-per-role paragraph points to principle 4 and entry 70 for the first `factory stats` figures, which it no longer repeats; they were, up to 2026-10-07 12:00 UTC over both stores, the code reviewer (Fable) changing an outcome in 4 of 94 runs with 3 BLOCKING findings for 94,860,442 context tokens over 99 runs, the critic (Fable) in 19 of 84 for 66,027,675, the verifier in 8 of 108 on Opus for 232,945,610 and in 1 of 5 on Fable for 5,189,563, and the implementer (Opus) in 18 of 111 for 372,507,821 over 114 runs. README is held to at most 1,110 lines; a later change that needs more raises the bound in its own spec. The `harness-docs` current truth is rewritten so each check keeps passing after later changes: a check finds a changelog entry by its opening words, `<n>. After issue #<k> `, and never by the last line or an entry count; no check measures what one change left untouched against `main` or a fixed commit, and the two requirements made only of such checks are removed; whitespace is checked once over the maintained documents in full, while the instance's gate command still checks each change; the frozen build spec's checks, and principle 2's retired status clause, are dropped. Rejected: moving the build documents to `dev/archive/`, which breaks the `Parent:` links and every path cited to them; moving the built but unfired features under "Where this can go", which is for intended work; bumping `docs/design.md`'s date, which every later change would also have to do; padding the cuts to the requested 150 lines, against about 90 that one home per mechanism gives; and splitting the work into four sub-tickets, which would all edit README.
+
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 6efb79e..9b394bf 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -1,6 +1,6 @@
 # Spec Factory: Agent Role Prompts
 
-2026-09-30 · Daniel
+Daniel · first written 2026-09-30; every change since is in `docs/changelog.md`
 
 ## How to use this
 
@@ -67,7 +67,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), the command that installs each build checkout's environment (`environment_sync`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance; `paths` and `stats`, which only read, run under any revision) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell that first drops a Python virtual environment inherited from the launching shell (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset), then sets `HOME` to a fresh temporary directory and exports any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. When the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the command and its output in the run's `environment-sync.log`), and the role's input says the environment is already synced. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
 
-**Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception. `factory stats` prints the evidence a change to this table needs; run on 2026-10-11 over this repo's store and the Nanobot target's as `factory stats --store .factory/store --store ~/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 --transcripts ~/.claude/projects`, it shows that up to 2026-10-07 12:00 UTC the code reviewer (Fable) changed an outcome in 4 of 94 runs, with 3 BLOCKING findings, for 94,860,442 context tokens over its 99 runs including killed ones; the critic (Fable) in 19 of 84, for 66,027,675; the verifier in 8 of 108 on Opus, for 232,945,610, and in 1 of 5 on Fable, for 5,189,563; and the implementer (Opus) in 18 of 111, with no gate failure found fixed before hand-off, for 372,507,821 over 114 runs. These are the hand count's figures, except that the reviewer's BLOCKING findings are 3, not 1, and the verifier's two models are counted apart.
+**Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception. `factory stats` prints the evidence a change to this table needs; its first figures, from 2026-10-11, are in `docs/principles.md`, principle 4, and changelog entry 70.
 
 | Role | Default | Why |
 |---|---|---|
