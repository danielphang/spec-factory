## Acceptance

Run every command from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper. The fixture GIVEN block and live-store-guard's GIVEN block are each run once first. Every NEW item's output on `main` `5215c5f` below was captured by running it there.

- Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures → NEW. Today it prints only `exit=2`: `stats` is not a command (`invalid choice: 'stats'`).
- A window bounds the count and the command writes nothing → NEW. Today it prints `exit=2 store=unchanged since=0`.
- Parks are grouped by normalised reason, with gate and merge decisions → NEW. Today it prints only `exit=2`.
- Each downstream spec catch names the runs that wrote and critiqued its spec → NEW. Today it prints only `exit=2`.
- Cost comes from the run record, else the transcript of that store's run, counted once per call → NEW. Today it prints only `exit=2`.
- The transcript cost report counts each message once → NEW. Today it prints `| critic | fable-5 | 1 | 5 | 725 | 33 |`: five records counted as five calls, with 725 context and 33 output tokens in place of 310 and 17.
- Stats reproduces the hand count on the two live stores → NEW. Today it prints only `exit=2`.
- Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing → NEW. Today it prints `here=2 inside=2 store=unchanged own=0 locked=2`: `stats` is not a command, while the lock does refuse `ticket show` (`locked=2`), which shows the fixture's lock is in force.
- Unmarked writes from inside the target are refused while a run is in flight, init included → REGRESSION
- The refusal names the throwaway store and not the marker → REGRESSION
- A harness acceptance is refused while a run is in flight → REGRESSION
- The documents record factory stats → NEW. Today it prints `readonly=no howto=no built=no depends=no lock=no design-fence=no design-lock=no design-model=no principles=no principles-old=yes buildspec=no prompts=0`, then `CONTIGUOUS`, then `0`, then `clean`.

Round 1's prototype printed the expected THEN lines of the four fixture table scenarios, the window scenario's row and the live-store scenario's lines. This round, on the fixture with its two new corrections, `scratch/p.py` printed the section A rows and the window scenario's row unchanged and the new section B lines, and on the live stores the A and park lines of the live-store scenario. The two new log events touch no section C or D input (those read `spec.added`, `approval.recorded`, run records and transcripts). The parks scenario and the cost-report scenario were rerun on `main` `5215c5f` this round with the new fixture and print `exit=2` and `| critic | fable-5 | 1 | 5 | 725 | 33 |`, as stated. The cost-report and guard scenarios need the real change, and were run only on `main`.

## Responses

- [BLOCKING] 6, `FACTORY_STATE` and "wrapper" unglossed → FIXED. Decisions now gloss `FACTORY_STATE` as the environment variable that points a command at another store, and Evidence's first paragraph glosses the wrapper as the prefix that gives each command a fresh, empty home directory.
- [SHOULD-FIX] 4, `park.corrected` not handled → FIXED. Decisions gain a rule: a park counts under its latest correction dated before `--until`, matched by ticket and `previous`, with the rejected options. Evidence records the one correction on record and that only a human writes the event. The section B requirement states the rule, design part B applies it before normalising, part D tests it, and the fixture gains two corrections: one applied (the harness-bug park now counts as `BLOCKED from harness: spec drift`) and one dated after `--until` that does not apply (`budget kill: reviewer` stays). The parks scenario's THEN changes to match, still seventeen lines.
- [SHOULD-FIX] 2, the live-store scenario is a snapshot → FIXED by keeping it with a note. The scenario now says its lines are the stores' records as of 2026-10-11, that a correction dated after the cut cannot move them under the new rule, and that a mismatch is first checked against the stores for a hand edit dated before the cut or a moved store. I kept it as acceptance rather than an operator step because the request asks for the reproduction as acceptance, and on 2026-10-11 it still reproduced exactly.
- [NIT] 1, ten gate edits → FIXED: "nine name a gate edit, and one an amendment", with the amendment's source quoted.
- [NIT] 6, "Written by" for an amendment → FIXED: `human` when the source is anything but a run id, `unknown` when the version has no `spec.added` event.

## Out-of-scope observations

- live-store-guard's second requirement, "Writes from inside a store's run directories or code checkouts are refused, marked or not", exempts "the read-only list above". Since `drive` joined that list, the wording also exempts `drive` from the location rule, which `drive` still obeys. The code is right and the wording is loose. This change restates only the first requirement and does not touch that wording.
- `README.md:109` says `factory/cost.py` "reads the Workflow tool's transcript files". After part A it still does, so that row stays true, and part E adds a row for `factory stats` beside it.

## Critic rounds

round 1 · spec v1 · run-0432-critic · REVISE

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

round 2 · spec v2 · run-0434-critic · APPROVE

Round 2 review of T-0043 spec v2 (`factory stats` and the once-per-message-id cost count). Per the convergence rule I reviewed the resolution of my round-1 findings and the text the v1→v2 diff changed; unchanged text was not re-reviewed.

What I checked, from `~/dev/spec-factory` at `main` `5215c5f` (clean tree):
- The new Evidence claims about `park.corrected`: `grep -rIn park.corrected factory bin tests` prints nothing, as stated. The live log has exactly one such event, at `.factory/store/log/` line 2158, `ts 2026-10-10T17:18:37+00:00`, ticket T-0040.3, with `previous`, `reason` and `by`. The Nanobot store's log has zero (`grep -c`, read only). The one real correction's `previous` equals, character for character, the reason of the single earlier `ticket.parked` on T-0040.3 (2026-10-10T07:12:26), so the Decisions' exact-match rule would apply it; and both the park and the correction are dated after the live scenario's cut (2026-10-07T12:00), so the live-store lines do not move, as the scenario's new note says.
- The new fixture lines: sourced the GIVEN block from my scratch directory through the wrapper. The s1 log holds the two `park.corrected` events at 2026-10-02T15:00 and 2026-10-09T12:00 with the stated `previous` texts, and the 10-02 correction's `previous` equals the 10-02T14:00 park's reason.
- The changed parks THEN by hand against the Decisions: with `--until 2026-10-08` the 10-02 correction applies (its park becomes `BLOCKED from harness: spec drift: tests/test_a.py ... <sha> ... <sha>`, cut to `BLOCKED from harness: spec drift`), the 10-09 correction is dated after `--until` and does not (`budget kill: reviewer` stays), the T-0003 park of 10-09 is outside the window, and s2 adds one `NEEDS-HUMAN from triage`. That gives 9 parks and, by count descending then code point (`BLOCKED from harness` < `BLOCKED from implementer` < `archive` < `archive: no spec store...` < `budget...` < `operator...` < `sub-ticket...`), exactly the seventeen lines stated. The decision rows are untouched by the new events.
- Acceptance commands run on `main` through the wrapper with the fixture: the parks scenario prints `exit=2` only, and `.venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |'` prints `| critic | fable-5 | 1 | 5 | 725 | 33 |`, both as verification.md states.
- The glosses: `FACTORY_STATE` is now defined where first used in Decisions, and the wrapper where first used in Evidence. The new `park.corrected` term is introduced in Evidence ("A human can correct a park's reason after the fact") before Decisions relies on it.
- Approved changes not yet archived: none, so rubric 5 raises nothing new.

What I could not check: the writer's `scratch/p.py` and its live-store output (another run's scratch directory; I run no suite and build nothing), and the two guard-side NEW scenarios, which need the change. Section C and D are unchanged and, as the writer says, read none of the new events.

Findings: none.

Prior findings (round 1):
- [BLOCKING] 6, `FACTORY_STATE` and "wrapper" unglossed → RESOLVED. Both glossed at first use in Decisions and Evidence (diff lines 1892, 1922).
- [SHOULD-FIX] 4, `park.corrected` not handled → RESOLVED. A rule is decided (count under the latest correction dated before `--until`, matched by ticket and exact `previous`; rejected options stated), carried into the requirement text, design part B, part D's tests and the fixture, with one applied and one post-window correction. The real event on record satisfies the exact-match rule.
- [SHOULD-FIX] 2, the live-store scenario is a snapshot → RESOLVED. The scenario now dates its lines (2026-10-11) and tells the verifier how to separate a store edit from a defect. Keeping it as acceptance is a defensible reading of the request; the only correction on record is after the cut.
- [NIT] 1, ten gate edits → RESOLVED ("nine ... and one an amendment", source quoted).
- [NIT] 6, "Written by" for an amendment → RESOLVED (`human` for any non-run source, `unknown` for no `spec.added` event).

Out-of-scope observations:
- The writer's observation on live-store-guard's second requirement (its "read-only list above" wording now also covers `drive`, and after this change `stats`) still stands; nothing more from me.

## Verifier results

41417c1789d40b26370b10f2bdcae6a84f903a9d · T-0043.2 · VERIFIED · run-0440-verifier
608a62ced66a5f32cb0e3e090d43ef75dd2a6618 · T-0043.3 · VERIFIED · run-0443-verifier
e375b16232346cc46947937e750c4f3be25a7472 · T-0043.1 · VERIFIED · run-0438-verifier
