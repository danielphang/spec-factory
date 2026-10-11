Round 1 review of T-0043 spec v1 (`factory stats` and the once-per-message-id cost count).

What I checked, from `~/dev/spec-factory` at `main` `5215c5f`:
- Cited paths and lines: `factory/cli.py` `READ_ONLY` at 1939-1940, `main()` at 1969-1985 with the `init`/`paths` exemption at 1972; `factory/cost.py` `tally()` at 47-71 adding every record's usage with no id check; `factory/prompts/reviewer.md:62` ("REQUEST-CHANGES requires at least one BLOCKING finding"); `docs/principles.md:59-60` ("1 BLOCKING finding in total") and line 68 ("Implemented by:"); `dev/build-harness.spec.md:295` (the `factory drive` paragraph); `tests/factory/test_harness_lock.py:48` (`("init", "paths")` chooses how the helper runs the CLI); `factory/stats.py` absent; `docs/changelog.md`'s last entry is 69. Every README and design.md heading the documents scenario greps for exists (`README.md:97, 118, 532, 549, 829, 871, 886, 982`; `docs/design.md:64, 68, 70`, each paragraph one line, as the greps need).
- Log event names in `.factory/store/log/`: `ticket.parked` 53, `approval.recorded` 44, `human.resolved` 66 (kinds: close, answer, redispatch, request-changes, ruling, to-spec-gate), `merge.refused` 8, `spec.added` 85, `spec.amended` 1, `store.migrated` 1. Non-run `spec.added` sources: 9 `gate edit ...` and 1 `amend ...` (see NIT below). Nanobot store, read only: 14 `claude:` cost records, 1 `UNKNOWN` status, 17 `BLOCKED`, 7 `KILLED`.
- Tests pinning old behaviour: `grep -rn 'cost\|tally\|READ_ONLY\|choices\|_subparsers\|invalid choice' tests/factory/*.py` finds only `test_drive*.py`'s `total_cost_usd` fixtures (the run record, not `factory.cost`) and the lock helper's `("init", "paths")`. "Tests to change: none" holds.
- Acceptance commands run on `main` through the wrapper, with the t0043 fixture sourced from my scratch directory: `.venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |'` prints `| critic | fable-5 | 1 | 5 | 725 | 33 |`, as the spec states (and `_role()` skips the relay message because it lacks the task prefix, so the role is `critic` today and after the change). The first section-A scenario prints `exit=2` only, as stated.
- Fixture arithmetic, by hand against the Decisions: every expected row of sections A, B, C and D, the window scenario's reviewer row, and the park ordering (count descending, then code point: `BLOCKED...` before `archive` before `archive: no spec store...`) follow from the fixture. The critic transcript's two ids give 105+205=310 context and 7+10=17 output tokens; the s2 triage transcript is ruled out for s1's run of the same id by the other-store rule; the gate rule gives `1 in 1 read, 1 not recorded` for the implementer.
- Approved changes not yet archived: none, so rubric 5 raises nothing.

What I could not check: the live-store figures (the prototype is not in a path I could find, and I run no suite), and the two guard-side NEW scenarios, which need the change.

Findings:

[BLOCKING] 6 proposal.md, Decisions (first bullet) and Evidence (first paragraph)
Problem: the first item of Decisions says the command honours `FACTORY_STATE` "as other commands do", and the first paragraph of Evidence says the figures were made "through the briefing's wrapper"; neither term is glossed anywhere in Problem, Evidence or Decisions, and an operator new to this system cannot judge the default-store rule without knowing what `FACTORY_STATE` is.
Evidence: `grep -n FACTORY_STATE` on the spec: first use is the Decisions sub-bullet; Problem and Evidence never define it. "wrapper" appears only in Evidence's first paragraph and the gate-command rule.
Suggested fix: one clause each, for example "honouring `FACTORY_STATE`, the environment variable that points a command at another store" and "through the fresh-HOME wrapper every role runs its commands in".

[SHOULD-FIX] 4 proposal.md, Decisions (park reasons) and the section B rows
Problem: the store has a `park.corrected` event (a human rewriting a park's reason after the fact) and the spec counts only `ticket.parked`, so a corrected park is reported under the reason the human replaced, and the spec does not say so.
Evidence: `.factory/store/log/`: one `park.corrected` on T-0040.3 (2026-10-10), with `previous` holding the old `harness-bug: run start implementer: ...` reason. The Decisions name `ticket.parked` only; "park.corrected" appears nowhere in the spec.
Suggested fix: decide in one line, either "a park counts under its latest `park.corrected` reason" or "corrections are ignored; the original reason counts", and state it under Decisions.

[SHOULD-FIX] 2 specs/factory-stats/spec.md, scenario "Stats reproduces the hand count on the two live stores"
Problem: this THEN is a snapshot of two live stores outside the checkout under test, so a later edit to a record dated before the cut (a `park.corrected`, a hand-fixed `meta.yaml`, a store move) fails the scenario with no defect in the change, and the verifier has no way to tell the two apart.
Evidence: the WHEN reads `/Users/dphang/dev/spec-factory/.factory/store` and `/Users/dphang/dev/nanobot-upstream/.factory/store` by absolute path; the store already carries one record correction (`park.corrected`), though after the cut.
Suggested fix: keep the scenario, and add one sentence under it saying the lines are the two stores' records as of 2026-10-11 and that a mismatch is first checked against the stores' log for a correction dated after that; or move the check to Operator steps as the gate's confirmation.

[NIT] 1 proposal.md, Evidence, "Ten `spec.added` events in this store name a gate edit"
Problem: nine name a gate edit and the tenth names an amendment (`"source": "amend /private/tmp/..."`, T-0040 v4).
Evidence: the log scan above.
Suggested fix: "nine name a gate edit and one an amendment".

[NIT] 6 proposal.md, Decisions, section C "Written by"
Problem: the rule names `human` for "a gate edit or a `spec.amended` version" but the amended version's `spec.added` source reads `amend <path>`, so an implementer matching on the words `gate edit` would print `unknown` for it.
Evidence: the T-0040 v4 `spec.added` event above.
Suggested fix: "`human` when the source is anything but a run id; `unknown` when there is no event".

Out-of-scope observations:
- The writer's own observation on live-store-guard's second requirement (its "read-only list above" wording now also covers `drive`) stands; nothing more from me.

STATUS: REVISE
CONFIDENCE: high. Every cited line and heading checked in the repo, two acceptance commands run on main with the stated output, the fixture tables reproduced by hand; the live figures and the guard scenarios remain unverified by me and need the build.
ESCALATIONS: none
