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

## Critic rounds

round 1 · spec v1 · run-0512-critic · APPROVE

Round 1 review of the v1 spec for T-0048 (shrink the maintained documents, rewrite `harness-docs`).

What I checked, on `main` at `7231670` from `~/dev/spec-factory`, each command under the fresh-HOME wrapper:
- Ran all 8 NEW scenarios as written. Each prints exactly what Acceptance says it prints today (`header=0 rest=changed` x3; `buildspec=3 frozen=0 readme=0`; `stale=7 replan=1 paths=1 drive=1 tripwire=1 sibling=1 effort=1`; `rule=0 date=0 old=1`; the pointer line with every `long`, `skip=2 store=3 drivefence=1 notbuilt=5`; `rows=4 pointer=0 protected=0 merge=1 record=1`; `history=5 refs=19 figures=1 pointer=0 entries=0 terms=0` then `CONTIGUOUS`; `readme=over`). The whitespace scenario prints `exit=0`, as its REGRESSION label says.
- Ran the 45 restated scenarios that need no setup script. All 45 print their THEN on `main`, so the restatements hold today, as Evidence claims. Two current-truth scenarios the spec says fail today do fail: "guard as its last entry" prints `0` where it wants 5, and "writer prompt as #73 left it" prints `writer=2`.
- Cited paths and lines: `.factory/context.md:9-11,34-36`, `README.md:9,127,138-141,868,1111`, every Built entry's line (939 through 1039), `## Where this can go` at 1054, `### Running on another agent host` at 1072 with `## Where things live` next at 1097, `docs/design.md:3` (`2026-09-30 · Daniel`) and `:70` (carries `94,860,442`), `docs/changelog.md` ending with entry 71 then the `Declined:` line. All as the spec gives them. `harness-docs` has 37 requirements; the delta restates 23 and removes 2.
- Evidence against the logs: 15 `plan.skipped` events here (T-0031..T-0051, matching the spec's range) and 5 on the Nanobot store; `merge.refused` with `protected paths not declared` for T-0044.1 at 2026-10-12T02:14 and two `accept-paths` events; `subtickets.superseded` for T-0031 at 2026-10-09T18:11; 15 `reply.json` files on the Nanobot store; Nanobot `instance.yaml` declares `paths:` on its gate commands and `results/ee4849e9.../ci.yaml` carries `SKIPPED`; commit `4a34e40` touched only `docs/principles.md`. The spec's correction of the request ("protected-path refusal has fired") is right.
- Tests: `git grep` over `tests/factory/` finds no test reading `README.md`, `docs/changelog.md`, `dev/` or this repo's `.factory/context.md` for content (the `context.md` hits are new-instance fixtures); the `docs/design.md` reads take prompt blocks and the SCRATCH FILES rule, which parts B.7 and D.5 do not touch. "Tests to change: none" is right.
- Protected paths: `.factory/instance.yaml:15` lists `.factory/**` as infra, so `.factory/context.md` is protected and is declared under Risk. `README.md`, `docs/*.md` (other than `docs/prompts/`) and `dev/` are not protected. Part F changes no repository file.
- Consistency: approved changes not yet archived: none. Open tickets touching README: T-0049 (#104, the diagram), which Out of scope names. Decision-log entries on README (T-0024 fence documentation, T-0042 driver step, T-0047 status date, T-0051 Empty output status) are each kept by parts B and C.

Findings

[SHOULD-FIX] 6 proposal.md, Decisions, first bullet
Problem: the first bullet names `decisions.md` and "past answers" with no gloss; the operator at the gate has not met either term in the Problem or Evidence.
Evidence: Problem glosses spec gate, current truth, `harness-docs` and the changelog; neither it nor Evidence names the decision log or `.factory/answers/`. The bullet's point (moving the files breaks links to them) is followable without knowing what the two files are, so I am not blocking on rubric 6's letter.
Suggested fix: "every path cited in the decision log (`decisions.md`), `dev/issues.md` and the closed answer records under `.factory/answers/`".

[NIT] 6 design.md, E.3
Problem: the sentence reads as if the quoted text is what is dropped, but the quote is the text that stays.
Evidence: README:868 today reads "`factory decision add T-n "<line>"`, at any ticket state, closed included. It appends one dated line to the target's decision log, `decisions.md`, which the spec writer, critic and planner receive with their input"; the scenario drops only `receive`.
Suggested fix: "drops the clause 'which the spec writer, critic and planner receive with their input', so the row reads: ...".

[NIT] 2 verification.md, Acceptance
Problem: "The maintained documents pass git's whitespace check in full" sits under ADDED Requirements yet is labeled REGRESSION, which is right (it passes today and replaces the eleven per-change whitespace scenarios) but a reader of ADDED expects a NEW line.
Evidence: ran it on `main`: `exit=0`.
Suggested fix: none needed; one clause in Acceptance saying why this added scenario is REGRESSION would spare the question.

Not findings, noted for the implementer: the restated scenarios bound the parts the Proposed change leaves to its wording. `**Not built**` must stay at a line start (two scenarios use it as a range end); the Built entries must keep their order (the #85 scenario ranges from "Spec amendment and drift" to "Re-plan after a re-spec"); "Current truth for the factory itself" must appear exactly once after the rename. The spec's checks cover each of these.

What I could not check: the "simulated later change" claim (restated scenarios hold after one more changelog entry and a verifier-prompt edit) and the prototype's 1,101-line result. The rules in Decisions (find an entry by its opening words, no `tail -1`, no entry count, no `main`-relative "untouched" checks) are visible in every restated WHEN I read, which is what the claim rests on.
