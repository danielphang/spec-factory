## Round 1 review of T-0044 spec v1 (harness de-bloat)

What I checked on `main` at `0ba4e4f`, from `~/dev/spec-factory`:
- Cited paths and lines: `factory/cli.py:199-240` (run_start), `:377`, `:778`, `:1469`, `:1960-1972`; `factory/gitops.py:18-19`, `:202-211` (last lines of a 211-line file); `factory/store.py:1-4`, `:15`, `:29`; `factory/specstore.py:8-9`, `:20`, `:202`; `factory/compose.py:110`, `:278-350`, `:420`; `factory/instance.py:88-90`; `tests/factory/test_instance.py:109,113,354`; `.factory/instance.yaml:34`; `~/dev/nanobot-upstream/.factory/instance.yaml:65` (read only). All match the spec's text and the `force_push_allowed` hit list.
- Ran the six grep/awk scenarios of `harness-code` as written, under the running-code wrapper: `4 0`, `2 3 3`, `1`, `13 0 0`, `3` (the stale-text count). Each equals the "today" value under Acceptance, so each NEW item fails today for the stated reason.
- Ran the build-dispatch scenario (throwaway target, no suite): printed `T-0001 already has run run-0001-triage in flight`, `exit=2`, `run-0001-triage`, as the spec says.
- Rubric 1 test search: the merged refusal text is pinned by `tests/factory/test_whole_spec_plan.py:200`, `test_p0_cli.py:97`, `test_shepherd.py:533`; the text does not change, so none belongs under Tests to change. No test names `run_gates`, `STATES`, `OPS`, `store.load_config`, `prompt_name`, `ensure_gitignore`, `repo_root(` or the `not supported yet` message. "Tests to change" is exactly the two files the key removal breaks.
- Design E's F841 claim: at every one of the 11 `cli.py` callers and `compose.py:110`, `cfg` is a parameter (or closure variable at `:1219`) with other uses in the same function; no local `cfg =` assignment. The claim holds.
- Rubric 5: "Approved changes not yet archived: none". T-0046/T-0047 are named under Risk with the overlap stated. The T-0023 temp-dir decision the suite scenario cites exists (decision log, 2026-10-04).
- Not run: the suite and `uvx ruff` (REGRESSION items; the verifier runs them).

Findings:

[BLOCKING] 6 Decisions, first bullet
Problem: The first bullet uses five names specific to this system with no gloss: "capability", "spec store", "delta part", "triage output" and "build-dispatch"; the operator new to the system cannot tell what is being added or why it must be added somewhere.
Evidence: Problem and Evidence gloss none of them. Evidence's last paragraph says "Current truth opened" and "current-truth requirement", also unglossed. `docs/writing.md` rule 2 and rubric 6 make an unglossed term in a human section's first paragraph blocking.
Suggested fix: Open the bullet with one sentence such as "The spec store is the folder of requirement files (`.factory/store/openspec/specs/<capability>/spec.md`, one folder per capability, a named area of behaviour) that each ticket must add to; a change with no such addition is refused", then name `harness-code` and `build-dispatch` as two such folders; gloss "current truth" (the archived requirement files) where Evidence first uses it.

[SHOULD-FIX] 1 Evidence, last paragraph
Problem: The paths `openspec/specs/harness-suite/spec.md` and `openspec/specs/*/spec.md` do not exist from `~/dev/spec-factory`, where the paragraph says the checks ran.
Evidence: `ls openspec/specs/` → "No such file or directory"; the store's tree is `.factory/store/openspec/specs/...` (the capability index in my input gives those absolute paths).
Suggested fix: Write both paths as `.factory/store/openspec/specs/...`.

[NIT] 1 Root cause item 12 and Design C, last bullet
Problem: The four blank lines are at `factory/cli.py:1967-1970`, not `:1966-1969`.
Evidence: `awk 'NR>=1966&&NR<=1971'` shows `1966: return ap`, `1967-1970` empty, `1971` the fence comment; the awk scenario reports the third blank at `:1969`, which agrees.
Suggested fix: Change both line ranges to `:1967-1970`.

Prior findings: none (round 1).

STATUS: REVISE
CONFIDENCE: high; every cited line and every runnable NEW scenario was checked on `0ba4e4f`, and the one blocking item is a wording gap with a one-sentence fix.
ESCALATIONS: none
