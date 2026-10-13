## Acceptance

Each item was run through the running-code wrapper on `main` at `88c65e1` and on a scratch prototype of Parts A to D, except where it says otherwise. The prototype had no document changes, so the four document items were run on `main` only. Two base runs were not made, because their result follows from a measured one; each says so.

- One suite run passes in under three minutes → NEW. Fails today: the suite runs one test at a time, 385.56 s on this machine, so the script stops it and prints `stopped | over 180 s`. The prototype printed `583 passed in 93.99s (0:01:33) | under 180 s`.
- Two suite runs at once each pass in under five minutes → NEW. Fails today: one run alone takes 385.56 s, so each of the two must print `stopped | over 300 s`. Not run on `main`; the script stops both at 300 s, so the verifier's base run fits in one tool call. The prototype printed two lines, `583 passed in 162.35s` and `583 passed in 162.48s`, each `| under 300 s`.
- Four stand-ins of one role started together all reply, 200 times over → NEW. Fails today: on this revision's script, `STANDIN: 200 rounds, 13 with a copy that did not reply, counter 769` and `BUILD_STANDIN: 200 rounds, 21 with a copy that did not reply, counter 763`. The counts vary run to run: the script exactly as written here, run again on `main`, printed `5 ... counter 777` and `16 ... counter 765`. A locked prototype of Part C printed `0` and `counter 800` for both. A fix that swallows the parse error and restarts the count would still print a counter below 800. This is the deterministic check of the cause of the intermittent failure of the test at `test_drive_build.py:123`.
- No test is removed and only the two listed assertions change → NEW. Fails today: with no change, HEAD equals its merge base, so it prints `pair: 0` and `missing: 0`. The prototype printed `pair: 1`, `removed: 0`, `added: 0`, `missing: 2` and the two expected lines. The new test of Part D.4 will add one `added` line.
- The gate's suite command, as the instance lists it, passes in under three minutes → NEW. Fails today: the first line is as expected, then `stopped | over 180 s`, because on `main` the gate command runs the suite one test at a time (385.56 s). Not run on `main`; the same command form printed `stopped | over 180 s` there in the item above. The prototype printed `gate: uv run --frozen pytest -q -p no:cacheprovider tests/factory`, then `583 passed in 97.65s (0:01:37) | under 180 s`.
The four scenarios of the MODIFIED requirement "A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT":
- A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows → NEW. Fails today: the first line is `park T-0001.1: EMPTY-OUTPUT from reviewer`, with no waiting phrase. The other three lines are the same before and after.
- One empty reviewer run followed by a real one routes on the real one → REGRESSION. Passed on `main` and on the prototype.
- An implementer that returns nothing twice parks as EMPTY-OUTPUT → REGRESSION. Passed on both.
- An intake role's second empty output in a row parks as EMPTY-OUTPUT → REGRESSION. Passed on both. The stub store's `run last-message` reply carries no `waiting`, so the reason stays plain.
- An intake role that ends waiting twice parks with the waiting reason, in the driver and the script → NEW. Fails today: `script EMPTY-OUTPUT from triage` and `drive EMPTY-OUTPUT from triage`.
- A build checker that ends waiting twice parks with the waiting reason, in the driver and the script → NEW. Fails today: `script EMPTY-OUTPUT from reviewer` and `drive EMPTY-OUTPUT from reviewer`.
- A role whose last message is not about waiting parks with the plain reason → REGRESSION. Prints the expected three lines on `main` and on the prototype.
- The design doc and build spec name the waiting park reason, and no prompt copy changes → NEW. Fails today: `design=0 spec=0 cli=0 prompts=0`.
- The README names pytest-xdist and the waiting reason → NEW. Fails today: `bullet=1 waiting=0 unfired=1 xdist=0`.
- The changelog records issue 106 as its last entry, without a numbering gap → NEW. Fails today: `CONTIGUOUS`, then `0`, then `0`; the last entry is 70.
- The parallel-suite change adds no whitespace errors → REGRESSION. On `main` there is no diff, and it prints `exit=0`.

These current-truth scenarios were run on the prototype and print their current-truth results unchanged:
- build-dispatch: "The driver takes the intake fixtures through the same routes as the intake script" and "The driver takes the build fixtures through the same routes as the build script".
- harness-suite: "A suite run in a fresh clone passes and adds nothing to the checkout" and "The harness suite passes with an uncommitted harness edit".
- harness-code: "factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines", which reads 890 lines.

## Responses

- [BLOCKING] Part letters unglossed in Decisions and Evidence → FIXED. The Problem's last paragraph now introduces the change as five lettered parts, A to E, with one line each, before Evidence or Decisions uses a letter. Part B also glosses gate commands there.
- [SHOULD-FIX] sub-ticket, current truth and play used unglossed → FIXED. Problem paragraph 2 says what a sub-ticket is before naming T-0047.2, and Problem bullet 3 says what a checker is. Evidence glosses current truth at its first use (the store's record of what the harness does today, grouped by capability) and plays at theirs (the scripted replies a test sets for each stand-in role). While there, I also glossed the Workflow scripts and replaced "driver-against-script fixture" with what that fixture does.
- [NIT] Stand-in check blind to a swallow-and-restart fix → FIXED. The script now also prints the stand-in's final verifier count, and the THEN expects `counter 800` for each stand-in. On `main` it printed `counter 769` / `763`, and again `777` / `765`. A locked prototype printed `800` for both. The WHEN gains `-B`, so importing the helper module writes no bytecode under `tests/`. Evidence and verification.md carry the new output.
- [NIT] Tests to change omitted `test_drive_build.py:60` → FIXED. Tests to change now names it, and says why it stays green: its reviewer says `""`, and `drive.py:241` sends only a non-blank message to `run last-message`.

## Critic rounds

round 1 · spec v1 · run-0504-critic · REVISE

## Critic review, round 1: T-0051 v1

What I checked on `main` at `88c65e1` (`~/dev/spec-factory`, clean tree):

- Cited paths and symbols, all present where the spec says: `factory/drive.py:182` (the park), `:220-228` (KILLED on a failed call), `:241-242` (the `run last-message` call); `factory/cli.py:298-305` (`run_last_message`, prints `ok`, `run_id`, `last_message`), 884 lines; `factory/workflows/intake.js:83`, `:126-127`; `factory/workflows/build.js:74`, `:130-131`; `tests/factory/_fixtures.py:230-231` and `:297-298` (unlocked `read_text` / `write_text` of `.n-<role>`), both stand-ins formatted with `.format(python=...)` and reading `STANDIN_LOG` / `STANDIN_PLAYS`; `factory/stats.py:50-55`; `factory/human.py:211-226`; `factory/drift.py:38`; `.factory/instance.yaml:22-24`; `factory/prompts/preamble.md:45-48`; `pyproject.toml` has no `[tool.pytest.ini_options]` and there is no `pytest.ini`, `setup.cfg` or `tox.ini`; `docs/design.md:106` bullet, `dev/build-harness.spec.md:206` and `:306`, README's `- **Empty output.**` bullet at `:999` with "has not yet fired" at `:1004`; changelog's last entry is 70.
- Tests that pin the changed behaviour: `grep -rn "EMPTY-OUTPUT from" tests/` and `grep -rn 'last.message' tests/factory/*.py`. The two listed (`test_drive.py:57`, `test_empty_output.py:63`) are the only ones the change breaks. `test_drive_build.py:60` also pins `EMPTY-OUTPUT from reviewer`, but its reviewer says `""`, and an empty message never reaches `run last-message` (`drive.py:241`), so it stays green (NIT below).
- Acceptance commands run as the spec gives them, through the running-code wrapper, none a test suite: the three document checks printed `bullet=1 waiting=0 unfired=1 xdist=0`, `design=0 spec=0 cli=0 prompts=0`, and `CONTIGUOUS` / `0` / `0`, exactly the "fails today" lines in verification.md. The stand-in race check (`t0051-standin.py`, written to and run from my scratch directory, 8 s) printed `STANDIN: 200 rounds, 9 with a copy that did not reply` and `BUILD_STANDIN: 200 rounds, 12 ...`: non-zero on `main`, as a race should be, so the item fails today for the stated reason.
- Cross-ticket: "Approved changes not yet archived" is `none`. T-0047, which the request orders this after, is `closed`; T-0048 and T-0049 are at `ready-for-triage` with no spec. The stub clerk `t0023-wf.mjs` answers an unlisted command with `{ok: true}`, so the regression scenario's "no `waiting`, reason stays plain" holds.
- Request vs spec: the request's A (parallel or in-process, measure and pick), B (gate and verifier use the faster form), C (the waiting park reason) and its later comment (make the flaky test independent of load) each map to a part; the preamble stays out as the request asks.

Not verified, because they need a build or the network: the `uv.lock` delta (two packages only), the timings, and the prototype's parity outputs. The spec states them as measured output with the commands that produced them, and the verifier will re-run them.

## Findings

[BLOCKING] 6 Decisions, first bullet ("Part A runs the suite with pytest-xdist alone ... That is Part B"); also Evidence table row 4 ("the Part D prototype")
Problem: The part letters are a term of this spec's design section, which the operator at the gate has not read, and no human-facing section says what a Part is before Decisions uses two of them in its first paragraph.
Evidence: Searched Problem, Evidence and Decisions for a gloss of "Part"; none. The writing standard (`docs/writing.md` §2) and the rubric both name section letters as terms needing a gloss at first use, and the rubric makes an unglossed one in a first paragraph blocking even when the reader could work it out. The rest of the spec is sound, so this is the only thing standing between it and approval.
Suggested fix: In the Problem's last paragraph, which already lists the pieces, label them once, e.g. "runs the suite's tests in parallel (Part A; the parts are the lettered pieces of the proposed change) ... the park reason now says so (Part D) ... the stand-in now takes a lock (Part C)", so every later "Part X" reads.

[SHOULD-FIX] 6 Problem paragraph 2 ("sub-ticket T-0047.2"); Evidence paragraphs 4 and 6 ("current-truth harness-suite requirement", "current-truth driver-against-script fixture", "stand-in plays")
Problem: Three more factory terms are used before anything says what they are, so the operator infers what a sub-ticket, current truth and a play are.
Evidence: Read the three sections as the gate reader; "driver", "park", "EMPTY-OUTPUT", "redispatch" and "gate commands" are glossed, these are not.
Suggested fix: One short gloss each at first use: a sub-ticket is one piece of a ticket's build; current truth is the store's record of what the harness does today; a play is the scripted reply a stand-in agent gives.

[NIT] 2 harness-suite, scenario "Four stand-ins of one role started together all reply, 200 times over"
Problem: A wrong fix that catches the `ValueError` and restarts the count at 1 would also print `0` for both stand-ins, since the check reads only exit codes and JSON.
Evidence: Ran the script on `main`; a copy that does not reply is the only failure it can see. The counter's value is never read.
Suggested fix: After the 200 rounds, also print the `.n-verifier` counter and expect `800` for each stand-in, which only a real serialisation passes.

[NIT] 1 Tests to change, last paragraph ("No other existing test pins the old reason")
Problem: `tests/factory/test_drive_build.py:60` does assert `== "EMPTY-OUTPUT from reviewer"`; it stays green only because its reviewer says `""` and an empty message is never sent to `run last-message`.
Evidence: `grep -rn "EMPTY-OUTPUT from" tests/` lists three sites, not two; `drive.py:241` guards the call with `and said`.
Suggested fix: Say that this third assertion pins the plain form with an empty message and is unaffected, so the implementer does not stop to decide whether to list it.

Prior findings: none (round 1).

round 2 · spec v2 · run-0506-critic · APPROVE

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

## Verifier results

5e00a1f5261b2576ae6243b46ac8895f71042ff9 · T-0051.1 · VERIFIED · run-0508-verifier
