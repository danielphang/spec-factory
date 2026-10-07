Commit: 67b61a587546e8a45349e91c13c00c3daa8346fe (branch `factory/T-0030.3`, base d226a4d03ca94bab45bd4221972285a4d16ee0bb)

Setup. The PR head is the run worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0314-verifier/wt`, with a clean status and `uv sync --frozen` run. The base is a `git archive d226a4d` export in `scratch/base`, also with `uv sync --frozen`. I wrote the two fixtures this sub-ticket names, `t0030-spec.sh` and `t0030-critic.sh`, by running input.md lines 376–451 (the two heredocs from the spec's GIVEN block) with `TMPDIR` set to this run's scratch directory. Then I ran `diff` of each file against its heredoc body (input.md lines 377–427 and 430–450), and both printed nothing. Every command below ran inside the HOME wrapper with `TMPDIR=<scratch>`. `git diff --stat main...HEAD` shows only `factory/compose.py` (+45/−8) and a new `tests/factory/test_role_inputs.py` (197 lines).

Per criterion:
- NEW | "Downstream roles get every spec section but Evidence and Responses, and the full spec's path" (`. ${TMPDIR:-/tmp}/t0030-spec.sh && marks planner … && marks parent-close $(comp verifier T-0001)`, as written) | base: `evidence=1 responses=1 kept=9 full=0` on all five lines (planner, implementer, reviewer, verifier, parent-close), the spec's "today" line | PR: `planner: evidence=0 responses=0 kept=9 full=1`, `implementer: evidence=0 responses=0 kept=9 full=1`, `reviewer: evidence=0 responses=0 kept=9 full=1`, `verifier: evidence=0 responses=0 kept=9 full=1`, `parent-close: evidence=0 responses=0 kept=9 full=1` | PASS
- NEW | "A round-2 critic receives a small revision as a diff" (`I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh small) && echo …`, as written) | base: `removed=0 added=0 keep100=2 prior_findings=1`, the spec's "today" line | PR: `removed=1 added=1 keep100=1 prior_findings=1` | PASS
- REGRESSION | "A round-2 critic receives a rewritten spec's previous version whole" (`I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh rewrite) && echo …`, as written) | base: `removed=0 keep100=1 other100=1 prior_findings=1` (I ran it there although it passed on the PR) | PR: `removed=0 keep100=1 other100=1 prior_findings=1` | PASS
- REGRESSION | gate suite, including `test_p0_cli.py` and `test_shepherd.py` | base: not run | PR: see the gate suite line below | PASS

Gate suite: PASS
  `(export HOME=…; git diff --check main...HEAD)` printed nothing and exited 0. `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `364 passed in 219.27s (0:03:39)`.

Probes:
- The cut applied to every stored spec version in this repo's store, 61 files under `.factory/store/specs/*/v*.md`, read-only. For each file I compared the headings outside fences (`## `/`=== ` lines) before and after the cut. In all 61, the output's headings equal the input's minus exactly the `## Evidence` and `## Responses` headings (0 mismatches). On T-0030 v2, the size goes from 56,646 to 51,088 bytes. The Evidence text ("Token overhead") is gone. Root cause is kept, and so is the fenced GIVEN block (`t0030-critic.sh` is still present). → OK
- The diff-or-whole choice on all 28 consecutive version pairs in the store: 21 got the diff and 7 the whole previous version, and total previous-version input fell from 1,088.8 KB to 596.9 KB. So the rule is not fixed to the fixture's 200-line shape. Fidelity check: I built the diff for T-0030 v1→v2 exactly as `compose` does (2,157 bytes against a 56,262-byte v1). Then `patch -o v2.rebuilt v1.md p.diff` followed by `cmp` against the stored v2 gave identical files. → OK
- Edge inputs to `without_evidence`:
  - empty text → `''`;
  - Evidence as the last section with no final newline → cut to the end, `'## Problem\nP'`;
  - CRLF headings → cut correctly, but the output is normalised to LF;
  - `## Responses` followed by a `STATUS:` trailer → the trailer is cut too (as the PR's Known gaps says);
  - a `# Top` line inside Evidence → stays inside Evidence;
  - an unclosed ``` fence inside Evidence → every later section is hidden (`'## Problem\nP\n'`), as the PR's Known gaps says;
  - a `~~~` fence inside Evidence holding `## Risk` → the cut ends at that fenced line. `specstore.lines_outside_fences` treats only ``` as a fence.

  No stored spec has a `~~~` fence or a CR (both `grep` counts were 0), so none of these affects real inputs today. → CONCERN, minor, under ESCALATIONS. None of these shows special-casing, and none breaks a stated criterion.

Protected path declared by the sub-ticket and changed: harness, `factory/compose.py`. No other protected or guardrail path changed. No existing test changed.

STATUS: VERIFIED
CONFIDENCE: high. Both NEW criteria fail on base with the spec's "today" lines and pass on the head. The REGRESSION criterion and both gate commands pass. Probes on all 61 real spec versions and 28 real version pairs behave as the spec describes.
ESCALATIONS:
- Minor, outside the sub-ticket's criteria. `without_evidence` uses the store's fence rule (`specstore.lines_outside_fences`, factory/specstore.py:77–86), which recognises only ``` fences. So a `~~~` fenced block inside Evidence can end the cut early, and an unclosed ``` fence hides every later section from the planner, implementer and checkers. CRLF text comes back as LF. No stored spec version triggers any of these today (0 `~~~` fences, 0 CRs, 0 odd fence counts reported by the implementer). The question for the operator is whether the store's fence rule should also cover `~~~` and unclosed fences. That rule is shared with the spec-store splitter, so it belongs with the separately filed splitter issue, not this sub-ticket.
