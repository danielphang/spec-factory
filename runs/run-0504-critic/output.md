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

STATUS: REVISE
CONFIDENCE: high, every cited location was confirmed on the checkout and four acceptance commands reproduced the spec's "fails today" output; the one blocking finding is a gloss the writer can fix in one sentence.
ESCALATIONS: none
