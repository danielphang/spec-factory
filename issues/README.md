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
| [11](https://github.com/danielphang/spec-factory/issues/11) | Spec writer: the Problem section must be readable by the operator at the gate (p0) | T-0011 | in intake | — |
| [13](https://github.com/danielphang/spec-factory/issues/13) | Planner: sub-ticket id form, cross-ticket dependencies and shared plan sections are unspecified | not in intake yet | — | — |

Issues 1–10 are applied and can be closed against their merge; 11 stays open until T-0011 lands; 13 is open (harness side fixed on green `70de00d45`). #12 was a duplicate of #11.
New findings go straight to GitHub issues; this file is the index.
