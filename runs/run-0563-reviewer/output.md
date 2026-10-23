Commit: 6f4d8658252556ed62bd19e130b09634f119f454 (branch `factory/T-0058.1`, base `788a201`)

## Review

Round 1. I read the full diff (8 files, 165 insertions, 16 deletions, per `git diff --stat`) against spec v3 and the sub-ticket, and read the surrounding code in `factory/cli.py` `main()` and the agent-copy loop in `factory/setup.py` `init_cmd`.

**1. Test integrity.** The only existing test file changed is `tests/factory/test_stats.py`, which the spec lists under "Tests to change". The change is the one the spec asks for: the `--accept-harness … stats` call now asserts exit 2 and the `config` hint, the comment is updated, and the surrounding `snapshot(target) == before` assertion is kept. No other test is weakened, skipped or deleted. The new file `tests/factory/test_small_defects.py` has no skip or xfail. I ran that file once as a narrow check: `12 passed in 1.69s`.

**2. Correctness.**
- Part A (`factory/status.py:19`, `:43`): the footer filter runs on `tail` after the list marker is stripped and before rule (b), as design A.2 says. `fullmatch` against `^🤖 Generated with \[Claude Code\]\(\S+\)$` keeps a line with text after the footer, a line with an empty link, and a line that only mentions Claude Code, which the new parametrised test covers. All four callers of `parse` go through this one function.
- Part B (`factory/setup.py:188-199`): `is_file()` and the read sit in one `try … except OSError`; on error the copy's path goes to `stale`, one stderr line names it with `could not be read (<strerror>)`, and `continue` moves to the next template. Nothing writes, chmods or deletes the copy. The `else` branch keeps the old condition's semantics for a readable copy. The implementer's Known gaps note the small departure from design B.1 (one `try`, not two branches); the observable behaviour matches the spec's requirement text, so I accept it.
- Part C (`factory/cli.py:851-853`): the refusal is the first statement inside the `try`, before the three commands run and before `instance.require()`, so a fresh repository gets no instance. `Refused` is caught at line 869, which prints the message to stderr, emits `{"ok": false, …}` and returns 2. The message names `factory <cmd>`, says it never checks the harness lock, and ends `factory --accept-harness <sha> config`.
- Parts E and F: the README, design and changelog edits match the lettered list. Entry 76 is the next number and names the four issues and the four phrases the scenario greps for. No `docs/prompts/` file changed, and no store file was touched.

**3. Scope.** All changes fall under parts A to E. Nothing outside them.

**4. Silent behaviour changes.** The `--accept-harness` refusal for three commands is the one visible change, and the spec decides it. Nothing else a caller would notice.

**5. Security and data safety.** None. The refusal writes nothing; the init change only reads.

**6. Protected paths.** `factory/status.py`, `factory/setup.py`, `factory/cli.py`, each declared in the spec's Risk section. Listed under ESCALATIONS for the record.

**7. Coding standard.** No over-building. The test helper `bare()` in the new test file repeats four lines that `test_stats.py` also has inline, but no shared helper exists in `tests/factory/_cli.py` that skips the lock stub for `stats`, and the docstring says why. Lean already.

**8. PR description.** What changed and Known gaps are in words, gloss the harness, the trailer, rule (b) and current truth at first use, and name the callers of each changed function. Known gaps lists the one `factory:` marker statement and the README "Upgrade" row it left alone. Readable at the gate.

## Findings

- [NIT] README.md:928: the "Where a human decides" table's **Upgrade** row still reads `factory --accept-harness <sha> <command>`. Three commands now refuse the flag, so a reader who picks `init`, `paths` or `stats` as `<command>` gets exit 2. The spec's part E does not list this row, and the implementer flagged it in Known gaps. A one-word follow-up to `config` would close it. Not a merge blocker.

net: Lean already.

## Prior findings

None (round 1).

## Out-of-scope observations

- `docs/changelog.md` entry 70 still says `stats` ignores `--accept-harness`. It is a dated history entry and entry 76 records the change, so this is correct as history.
- `src.read_bytes()` on an unreadable harness template would be reported as the copy "could not be read" (`factory/setup.py:190`). The template lives in the harness checkout, so an unreadable one breaks the harness anyway. Not worth a change here.

STATUS: APPROVE
CONFIDENCE: high, the diff does what each lettered part asks, the only existing test changed is the one the spec lists, and the new test file passes on this head
ESCALATIONS: protected paths changed and declared in the spec's Risk section: `factory/status.py`, `factory/setup.py`, `factory/cli.py`
