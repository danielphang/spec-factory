Commit: 2588b553013712729323c916c8e9063633b47e29

## Review of T-0059.1, round 1

I read the diff `db28eb1...2588b55` in full: `factory/truth.py` (new, 297 lines), the `factory/cli.py` edits, `.factory/instance.yaml`, README, `docs/design.md`, `docs/changelog.md` and the new `tests/factory/test_truth.py`. I checked the code against the parent spec's design part A line by line, and against the `specstore` helpers it reuses (`scenario_blocks`, `requirement_blocks`, `parse_delta`, `apply_delta`, `applies`), which I read at `factory/specstore.py:76-120`, `:223-239`, `:317-338` and `:385-397`.

**Test integrity.** No existing test file changed. `git diff --name-only --diff-filter=DMR db28eb1..HEAD -- tests` printed nothing. The only test change is the new file `tests/factory/test_truth.py`; it has no skip or xfail marker (grep over the file found none). The spec's "Tests to change" is none, and the branch honours it.

**Correctness.** The replay matches the spec's design in every part I could check by reading:
- The exact-print rule (`factory/truth.py:42-63`) strips the trailing `.`, the exit clause and `, one per line` in the reverse of the grammar's order, reads the three BODY forms, and returns None on anything it cannot read in full. `_items` (`:28-39`) requires the whole LIST to be consumed, so a THEN with trailing prose is skipped rather than half-read, as Decisions require.
- Skip reasons (`:161-181`) are checked in the spec's order 1 to 5, with the spec's texts. The one extra reason, more than one THEN line, is documented in Known gaps and matches nothing in current truth today.
- Folding (`:118-158`): the ticket under test is found by the store layout at `:107-115` exactly as design A says; the folded set is the ticket's change plus every unarchived change with a merged sub-ticket and a ticket not closed; deltas fold in id order and each part is checked against the text folded so far with the same error texts as `specstore.applies`, then applied with `apply_delta`. A failing part refuses with exit 2 naming the change id, and nothing runs, because `fold` raises before any thread starts (`:247` before `:259`).
- Running (`:188-211`): one thread per shown capability, fresh `HOME` and `TMPDIR` per capability, every `FACTORY_*` name dropped, `bash -c` from the checkout with stdin closed, GIVEN blocks resolved through references (same capability first, then capability order at `:253-255`), recursively and never twice on one path, each block at most once per capability.
- Output (`:264-284`) prints the first line, one line per scenario in capability and file order, the failure detail with the 40-line cap and the last five stderr lines, and the counts line; exit 1 only on a failure.
- `cli.py`: `truth` joins both tuples in `main()`, the refusal message names `factory truth check` and `config`, `("truth", "check")` joins `READ_ONLY`, and the branch now returns `a.fn(a) or 0`. I confirmed `init_cmd`, `paths_cmd` and `stats_cmd` contain no `return` statement, so their exit code is unchanged. `cli.py` is 899 lines, under the 910 limit.
- The gate entry in `.factory/instance.yaml` is the design's text verbatim, after the suite line.
- README grows by exactly 11 lines (19 added, 8 removed); the reworded "Accepting a harness revision" sentence still contains `init`, `paths`, `stats`, `--accept-harness` and `refuse` in one sentence, which is what harness-docs' current-truth check at `openspec/specs/harness-docs/spec.md:514` counts.

**Scope and silent changes.** Every change falls under parts A to E. The one caller-visible change outside the new command is the `main()` return for `init`, `paths` and `stats`, which stays 0 as shown above.

**Security and data safety.** The command runs shell text from the store's specs by design; it writes nothing to the store, and each capability's temporary directory is removed in a `finally`. Nothing new reaches a protected path outside the repository.

**Protected paths.** `factory/truth.py`, `factory/cli.py` and `.factory/instance.yaml` are touched. All three are declared in the approved spec's Risk section, so they are listed under ESCALATIONS for the record only.

Findings:
- [NIT] README.md:1027: the new subsection says a scenario the check cannot run "is listed SKIPPED with its reason" but not that it is counted, which design part D asks the subsection to say → a reader does not learn from README that the last line's count includes skips. One word, "and counted", would close it if the line budget allows.
- [NIT] .factory/instance.yaml:23: the header comment above `gate_commands` still describes two commands (whitespace, then the suite) while the list now holds three → the next reader of the file gets a stale summary. The implementer already lists this under Known gaps.
- [NIT] factory/truth.py:198-208: an exception raised inside a capability thread, such as `bash` missing from `PATH`, surfaces through `f.result()` as a traceback rather than a `truth check:` refusal → an operator sees a stack trace instead of a one-line reason. The spec assumes `bash` on `PATH`, so this is outside its letter.

Prior findings: none (round 1).

PR description: What changed reads well for the operator. It glosses current truth, capability, scenario, WHEN and THEN on first use, says in words what each part does, and Known gaps names every departure from the spec's letter (size, the keyed owner map, the extra THEN skip reason, the reworded README sentence, the stale comment) with its effect today. No finding.

STATUS: APPROVE
CONFIDENCE: high. I read every changed line against design part A and the specstore helpers it relies on, confirmed no existing test changed and the three read-only commands' exit code is unchanged; the verifier runs the scenarios and gate on the same head.
ESCALATIONS: protected paths touched, all declared in the spec's Risk section: `factory/truth.py`, `factory/cli.py`, `.factory/instance.yaml` (for the record; no action needed).
