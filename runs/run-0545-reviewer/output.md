Commit: 17fba148d8ecf5475b7aa7ddef46193437886317

## Review of T-0049.1, round 1

What I checked, by reading the diff and by narrow commands in the worktree:

- **Test integrity.** `git diff --stat 81482fe..HEAD` lists one file, `README.md` (67 insertions, 2 deletions). No test, CI config, agent prompt or skill changed. The spec's "Tests to change" is none and that holds.
- **Correctness against the spec's parts A to E.**
  - A: the new subsection sits between the first diagram's caption and `### Ticket states`, with one blank line before the heading (README:284-286). I extracted the Mermaid block from README and from the spec's part A with the same awk the acceptance uses and ran `diff`: IDENTICAL. The edges, the three `classDef` lines and the `"a later ticket"` subgraph title are therefore exactly as the spec requires.
  - A prose: two sentences differ from the spec's text. "a human approves a version, the newest by default" is true: `factory/human.py:135` uses `a.version or t["spec"]["version"]` and `factory/cli.py:787` defines `--version`. "its planner receives the decision log but no current truth" is true: `factory/compose.py:324-325` adds the approved spec and the decisions with the comment "no current truth for the planner". Both rewordings are more accurate than the spec's wording, and the spec allowed rewording so long as claims stay true.
  - B: README:209 is the exact line the spec gives, and no other line of the first diagram changed (the diff's first hunk is that one line).
  - C: the `| How a ticket moves |` row is the exact text of part C.
  - D: the Status row (README:9) already reads 2026-10-19, today's date. No edit was needed.
  - E: the edge-to-code table is in the PR description with three line-range corrections, each explained. I spot-checked `factory/compose.py:324-325` and `factory/human.py:130-150`; they match the table's claims.
- **Line count.** `wc -l README.md` prints 1174, under the 1,185 bound.
- **Scope.** Nothing outside the sub-ticket's lettered parts. The sequence diagram's `participant C as clerk agent` at README:325 is outside the first diagram and the spec did not ask for it; correctly left alone.
- **Silent behaviour changes.** None possible: documentation only.
- **Security and data safety.** Nothing applies.
- **Protected paths.** None touched; the parent's Risk list declares none.
- **Coding standard.** No code changed.
- **PR description.** "What changed" says in words what changed, glosses the clerk and the launch copy at first use, and names each deviation from the spec's text with its code reason. "Known gaps" states plainly that no real Mermaid render was done and lists the simplifications the diagram keeps from the spec. Both sections meet the writing standard.

Findings: none.

Prior findings: not applicable, round 1.

Out-of-scope observations:
- The parent spec already notes that the first diagram's subgraph labels "(agents, driven by the script)" still describe only the Workflow-script path. Still true; not for this ticket.

STATUS: APPROVE
CONFIDENCE: high. The diff is one documentation file, the diagram text is byte-identical to the approved spec's, and the two prose deviations are verified against the cited code.
ESCALATIONS: none
