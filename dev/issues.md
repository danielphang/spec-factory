# Issues

Findings against the design doc, build spec or P0 plan, each from a real pipeline run. Filed on
GitHub 2026-10-02; the drafts that lived here were removed in the commit that recorded the numbers.
A fix closes its issue through a reviewed change on `main`; the merge column is that change.

| # | Issue | Intake ticket | Merge on `main` | Changelog |
|---|---|---|---|---|
| [1](https://github.com/danielphang/spec-factory/issues/1) | STATUS parser rejects a wrapped CONFIDENCE line | T-0001 | `fdefa22` + `3bd8641` | 34 |
| [2](https://github.com/danielphang/spec-factory/issues/2) | Clerk-via-schema re-encodes the CLI's JSON | T-0002 | `b83e883` | 35 |
| [3](https://github.com/danielphang/spec-factory/issues/3) | Re-asked role does not receive its own prior output | T-0003 | `32cf6f6` | 36 |
| [4](https://github.com/danielphang/spec-factory/issues/4) | `.claude/agents/` created mid-session is invisible to that session | T-0004 | `e321117` | plan only |
| [5](https://github.com/danielphang/spec-factory/issues/5) | Faux-spec live-state steps sit under a protected path | T-0005 | `ac66b2c` | 37 |
| [6](https://github.com/danielphang/spec-factory/issues/6) | P0-5 grep contradicts the inline-script allowance | T-0006 | `366d469` | plan only |
| [7](https://github.com/danielphang/spec-factory/issues/7) | Harness instance is single-target | T-0007 | `b9379ec` | 38 |
| [8](https://github.com/danielphang/spec-factory/issues/8) | Adopt OpenSpec's storage model as a forked schema | T-0008 | `03d8835` | 39 |
| [9](https://github.com/danielphang/spec-factory/issues/9) | `run start` must reserve the run id atomically | T-0009 | `f2576ca` | spec only |
| [10](https://github.com/danielphang/spec-factory/issues/10) | A spec pinned before `factory init` has no change folder | T-0010 | `3890a2f` | 40 |
| [11](https://github.com/danielphang/spec-factory/issues/11) | Spec writer: the Problem section must be readable by the operator at the gate (p0) | T-0011 | `9168ce1` | 41 |
| [13](https://github.com/danielphang/spec-factory/issues/13) | Planner: sub-ticket id form, cross-ticket dependencies and shared plan sections are unspecified | folds into #21 (doc residue) and #20 (planner id line); harness side green `70de00d45` | — | — |
| [14](https://github.com/danielphang/spec-factory/issues/14) | Build half as built: local-commit mode, the join in the store, bounded conflict runs, serialised merges, baseline-relative gate | folds into #21 (`build`, `gates` requirements); built on green through `baeb930d4` | — | — |
| [15](https://github.com/danielphang/spec-factory/issues/15) | A simplifier role: replay a task set against a simplified harness, measure, propose | closed 2026-10-03, superseded by #20 (reviewer tags, `factory:` marker) and #21 part D (dead-code list); reopen with a replay set | — | — |
| [16](https://github.com/danielphang/spec-factory/issues/16) | Harness: a checker result with no or a non-SHA Commit: line is recorded against the current commit (first end-to-end pilot) | green-pilot T-0001 | green `1f3a58e52` | harness |
| [17](https://github.com/danielphang/spec-factory/issues/17) | Harness: `factory report TICKET` status page | not in intake yet | — | — |
| [18](https://github.com/danielphang/spec-factory/issues/18) | Harness: a killed checker run parks as a harness bug instead of a budget kill (found by #16's writer) | green-pilot T-0002 | green `7c0a0353d` | harness |
| [19](https://github.com/danielphang/spec-factory/issues/19) | Repo layout: the harness moves home, each target carries a `.factory/` instance (p0; carries #7's harness side) | T-0012 (closed as applied 2026-10-03: VERIFIED, no spec store on this instance) | `70c32ab`; store move `95c1acf` | 42 |
| [20](https://github.com/danielphang/spec-factory/issues/20) | Prompts: ponytail's check order, callers-first root-cause rule, reviewer over-building tags, `factory:` deferral marker (after #19) | not in intake yet | — | — |
| [21](https://github.com/danielphang/spec-factory/issues/21) | Current-state spec for the factory itself: seed its own current truth, README as the overview (after #19; #13, #14 fold in) | not in intake yet | — | — |
| [22](https://github.com/danielphang/spec-factory/issues/22) | Per-role effort setting beside `models:` (p2; do not take until the operator confirms) | not in intake | — | — |
| [23](https://github.com/danielphang/spec-factory/issues/23) | Technical documentation standards for the factory's agents: `docs/writing.md`, preamble, critic and reviewer checks (p1; after #19, alongside #21) | not in intake | — | — |

Issues 1–10 are applied and can be closed against their merge; 11 applied (`9168ce1`); 13 and 14 fold into #21 (checklists until it archives); 15 closed as superseded. #12 was a duplicate of #11.
New findings go straight to GitHub issues; this file is the index.
