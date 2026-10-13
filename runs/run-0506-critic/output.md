## Critic review, round 2: T-0051 v2

Reviewed per the convergence rule: whether the four round-1 findings were resolved, and the text the v1-to-v2 diff changed (Problem's last paragraphs, three Evidence paragraphs, Tests to change's last paragraph, the stand-in script and its WHEN/THEN, the matching verification.md item, and the new Responses section).

What I checked on `main` at `88c65e1` (`~/dev/spec-factory`, clean tree):

- Changed cited lines still hold: `factory/drive.py:241` guards the `run last-message` call with `and said`; `factory/drive.py:182`, `factory/workflows/intake.js:83` and `factory/workflows/build.js:74` write `EMPTY-OUTPUT from <role>`; `factory/cli.py:298-305` is `run_last_message`, 884 lines in the file. `grep -rn "EMPTY-OUTPUT from" tests/` lists `test_drive_build.py:60` and `test_drive.py:57`, so the spec's "these three sites" counts the `last-message` assertion at `test_empty_output.py:63` as the third; the set the change breaks is still the two listed.
- The revised stand-in script, written from the spec's block to my scratch directory and run as the WHEN gives it (`.venv/bin/python -B`, through the running-code wrapper, 8 s): `STANDIN: 200 rounds, 16 with a copy that did not reply, counter 768` and `BUILD_STANDIN: 200 rounds, 14 with a copy that did not reply, counter 773`. Non-zero and below 800 on `main`, so the item fails today for the stated reason, and the counter now sees a lost call even when every copy replies. The counter path the script reads, `claude.log.n-verifier`, is what the stand-ins write (`tests/factory/_fixtures.py:230`, `log.with_name(log.name + ".n-" + role)`). No `__pycache__` appeared under `tests/` and the tree stayed clean.
- Evidence arithmetic in the new sentences: 800 - 769 = 31 and 800 - 763 = 37, as written.
- "Approved changes not yet archived" is still `none`.

## Findings

none

## Prior findings

- [BLOCKING] 6, part letters unglossed → RESOLVED. The Problem now ends with the five lettered parts, one line each, before Evidence's table or Decisions names one; Part B's line also glosses gate commands.
- [SHOULD-FIX] 6, sub-ticket / current truth / play unglossed → RESOLVED. Sub-ticket is glossed before T-0047.2 (Problem paragraph 2), checker in Problem bullet 3, current truth and plays at their first use in Evidence, and the Workflow scripts where the three park sites are introduced.
- [NIT] 2, stand-in check blind to a swallow-and-restart fix → RESOLVED. The script prints the stand-in's final verifier count and the THEN expects `counter 800`; on `main` it prints a count below 800 (confirmed above).
- [NIT] 1, `test_drive_build.py:60` left off Tests to change → RESOLVED. It is named, with the reason it stays green (`drive.py:241`, `and said`), which I confirmed.

STATUS: APPROVE
CONFIDENCE: high, every round-1 finding is fixed in the text and the one changed acceptance command reproduced its "fails today" output on the checkout; the timings and lock delta remain for the verifier, as in round 1.
ESCALATIONS: none
