## Problem

The operator reads two documents at every spec gate, the human review where a spec is approved before any code is written: `README.md`, the page that says what the factory does today, and `docs/design.md`, the design it is built from. Both have grown, and parts of README are wrong. README explains several mechanisms two or three times. It says six features have "not yet run" on a real ticket when the stores' logs show they have. It keeps project history that belongs in `docs/changelog.md`, the numbered record of design changes. Three finished working documents under `dev/` describe a design the code never had, yet the briefing that every agent reads first asks each change to keep one of them, the build spec, in step with the design. So every ticket pays to edit a document nobody uses, and the operator reads more than the system needs, some of it false.

A second cost follows from the first. The factory keeps "current truth", one spec per capability holding the checks the system must keep passing; each check is a shell command with its expected output. The capability for the documents, `harness-docs`, has 37 requirements, and many of them check README, the design doc, the changelog and the build spec with `grep`. Some of those checks can only pass on the change that wrote them. A check that the changelog's last entry is a given issue's entry fails as soon as another entry follows it. On `main` today, 12 of its checks fail because a later change moved on: a newer changelog entry, a later prompt edit, a revised principle. Others check "this change touched no prompt file" against `main`, which fails on the first later change that does. A de-bloat of README has to edit those checks too, or it breaks them.

This change shrinks what the operator reads and makes what remains true. It freezes the three `dev/` build documents as history. It corrects README's false claims from the logs. It gives each mechanism one home in README, with a short pointer everywhere else. It moves history to the changelog. It rewrites the `harness-docs` checks so that each one keeps passing after later changes and still checks what it was written to check.

## Evidence

All counts are on `main` at `7231670`, run from `~/dev/spec-factory`.

- Sizes (`wc -l`): `README.md` 1191, `docs/design.md` 923, `dev/build-harness.spec.md` 556, `dev/build-harness.plan.md` 298, `dev/P0-intake-skeleton.md` 118, and the current truth `.factory/store/openspec/specs/harness-docs/spec.md` 450.
- The build spec describes another design. Its header (lines 1-5) names the retired branch `feat/lionbot-v3` and a design doc under `/tmp/...`. The triage counted `bare repo` 15 times, `pre-receive` 9, `FACTORY_KEY` 13, `gate-run` 15 and `retro-input` 8 in it, and none of the five in `factory/*.py`.
- The duty to keep it in step: `.factory/context.md:34-36` says "A change to the design doc keeps its own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md` consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it." `git grep -e build-harness -e P0-intake` outside `.factory/answers/`, `.factory/green-pilot/` and `dev/` finds only `.factory/context.md:9,35` and the docstring at `factory/cli.py:1`. No test reads `README.md`, `dev/` or the changelog: `git grep` over `tests/factory/` finds `design.md` read only for its prompt blocks and the SCRATCH FILES rule.
- I ran every `harness-docs` scenario on `main` with a script that runs each WHEN under bash (fresh HOME, from the repo root). Twelve fail today:
  - Seven check that the changelog's last entry belongs to an issue, but entry 71 now follows them. Each prints `0` where it expects 3 to 7 term hits. They are the guard (#45), the small-change lane (#48), the critic revert (#74), the five-role reading rules (#76), the environment sync (#51), the sibling-merge exception (#85) and `factory stats` (#70).
  - Two pin the entry count: `51 CONTIGUOUS` and `64 CONTIGUOUS` print `71 CONTIGUOUS`.
  - One checks #86's entry is last and prints `last=no`.
  - One is "The writer prompt is as #73 left it": it compares the spec writer prompt with commit `05cf8f9` and prints `writer=2`, because later tickets changed that prompt.
  - One is principle 2's status clause in `docs/principles.md` ("done by #41 ... and by #73"). It prints `status=0`, because commit `4a34e40` (2026-10-08) removed the status line once the principle was implemented.
  - Three more cannot run on their own because they need setup scripts that other capabilities' scenarios write (`t0029-prompt.sh`, `t0023-parent.sh`). They are unaffected here.
- Checks that break on a later change. I simulated one in a scratch clone: one more changelog entry, and one identical line added to the verifier prompt in all three copies. The current `harness-docs` then also prints `prompts=2` in three scenarios, `untouched=2` in one and `others=2` in one, and `73 CONTIGUOUS` where it pins 51. The rewritten scenarios below print the same on that later change as on this one.
- Stale claims in README, checked against the two stores' logs (`.factory/store/log/*.jsonl` here and `~/dev/nanobot-upstream/.factory/store/log/*.jsonl`, read only):
  - README:157-158, the one-sub-ticket path "has not yet run on a real ticket": 15 `plan.skipped` events here (T-0032 to T-0051) and 5 on the Nanobot store. A `plan.skipped` event means the harness made the whole spec one sub-ticket with no planner run.
  - README:728-729 and 1025-1026, the driver "has not yet run a real ticket": the Nanobot store has 15 `reply.json` files, one per role process `factory drive` started. They belong to T-0035 (triage through critic, then the implementer and both checkers) and T-0036 (the same), and both tickets are `closed`.
  - README:948, a gate command's path skip, "no repo's configuration uses it yet": the Nanobot `instance.yaml:47-51` declares `paths:`, and `results/ee4849e9.../ci.yaml` there records `status: SKIPPED` for T-0036.1.
  - README:1000, re-plan after a re-spec, "has not yet fired": this store logged `subtickets.superseded` for T-0031 at 2026-10-09T18:11.
  - README:822-823, the per-run scratch directory, "has not yet run on a real ticket": every run since #35 gets one. This run's input names its own, `runs/run-0511-spec_writer/scratch`.
  - README:1016, the protected-path refusal at merge, "has not yet fired". The request lists this one as still true, but it is not. This store logged `merge.refused` with `protected paths not declared` for T-0044.1 at 2026-10-12T02:14, then a park, then `human.resolved` with `kind: accept-paths` at 04:37.
  - README:94, "A run that returns no output is recorded as killed". `docs/design.md:106` says such a run "is never recorded as a budget kill" and is re-dispatched once.
  - Still true, so kept:
    - The tripwire, the check that files outside the repo did not change during a run, has no park in either log.
    - The sibling-tests check's refusal text, "Tests to change lists ... as added by a sibling" (`factory/drift.py:33`), appears in neither log.
    - Neither `instance.yaml` sets `effort:`.
    - The drift check's sibling-merge exception leaves no event of its own, so I could not check it, and its "not yet run" stays.
  - `docs/design.md:3` reads `2026-09-30 · Daniel`.
- Mechanisms told more than once in README:
  - The live-store fence, the refusal of store writes while an agent run is in flight: lines 755-764, 836-860 and 963-972.
  - The final check's skip: 165-169 and 329-331.
  - "never moves the integration branch": 377, 619 and 955. Joined into one line, the page carries it 3 times.
  - "Not built" (1039-1052) repeats 4 of the 5 items in "Where this can go" (1054-1070).
  - "Running on another agent host" (1072-1095, 24 lines) restates `docs/design.md:868-888`, table included.
  - The Built entries 939-1037 restate how-to sections.
  - Terms rows 138-141 restate "Where it runs".
  - The merge gate row (127) also defines "protected path".
  - The Record row (868) restates the decision-log row (131).
- History in README: "On 2026-10-04 the two stores had 41 and 11 overlapping runs" (819-821), "`factory/cost.py` ... used to count most calls about twice" (1035-1036), "Both stores were made before the store branch existed and were moved onto it" (377-379), the narrative at 1120-1139, and "(today this caught two: ...)" at 1185-1186. `docs/design.md:70` repeats the `factory stats` figures that changelog entry 70 and principle 4 give.
- Prototype. I made every edit below in a scratch clone of `main` and checked the result:
  - README went from 1,191 to 1,101 lines. The diff is 124 insertions and 207 deletions across 7 files, 331 changed lines.
  - Every scenario in the delta below passes on it, apart from the one that needs another capability's setup script.
  - Every current-truth `harness-docs` scenario that the delta leaves alone prints the same on the prototype as on `main`.
  - The delta's 46 restated scenarios print the same on `main` as on the prototype. Its 8 new scenarios fail on `main` with the outputs under Acceptance.
  - The request asked README to fall by at least 150 lines. The cuts it names give about 90. Its estimate of about 75 lines of history (part D) counted text that is not in README.

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

