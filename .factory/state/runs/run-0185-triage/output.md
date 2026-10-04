Type: bug
Title: Roles running in parallel share the session scratchpad and overwrite each other's files
Summary: A role is one agent the factory starts for a single step of a ticket, such as a spec writer or a verifier, and each start is a run. Runs launched from the same session all inherit that session's scratchpad directory, and nothing tells them to keep their files apart. When intakes run in parallel, as the README recommends, one run can overwrite another's files, or run and cite a prototype another run made. Checkers are the roles that check a built change: the reviewer and the verifier. They also leave files in the dev checkout, `~/dev/spec-factory`, where the operator works. The requester needs each run's scratch files kept apart from every other run's and out of the dev checkout, and cleared after the run. A parked run is one stopped for a human, and its scratch files stay so a human can inspect them.

Evidence:
- Nanobot v3.5 store, run-0068 (spec writer, Nanobot ticket T-0022), `~/dev/nanobot-upstream/.factory/state/runs/run-0068-spec_writer/output.md:576`. The writer reported: "My session scratchpad was overwritten during this run by files from other work: a WhatsApp chat-log check and a `/summarize` check. I moved my prototype to a unique subdirectory and did not touch the foreign files." The request names T-0009's spec writer as the other run. I did not confirm that.
- Retro trial 2026-10-04, item H8, `.factory/answers/retro-trial-2026-10-04/retro_with_efficiency.md:159`. It says checkers need a scratch directory the harness owns and clears. The three runs it cites:

  | Run | What it left or found | Source |
  |---|---|---|
  | run-0062-verifier | created `/Users/dphang/dev/spec-factory/.venv`: its worktree had no `pyproject.toml`, so `uv` walked up to the dev checkout's project | `.factory/state/runs/run-0062-verifier/output.md:28`; run-0063-implementer `output.md:81` says the directory was left in place |
  | run-0103-verifier | left an untracked throwaway store under the dev checkout | retro text only; not checked in the run's output |
  | run-0134-verifier | found a stale `scratchpad/base` directory from another run and extracted its base checkout over it, so pytest printed `23 failed, 103 passed`; it discarded those results and redid the checks in fresh clones | `.factory/state/runs/run-0134-verifier/output.md:38` |

- What the harness does today, on this checkout:
  - The preamble, the shared opening of every role's prompt (`factory/prompts/preamble.md`), has a RUNNING CODE section that sets HOME. It says nothing about where scratch files go.
  - `run_start` in `factory/cli.py:198` creates `runs/<run id>/` with `meta.yaml` and `system-prompt.txt`, and no scratch directory.
  - `store.ensure_gitignore` in `factory/store.py:53` ignores `worktrees/`, `runs/*/wt/` and `runs/*/tripwire.yaml`, and nothing else.
  - `run_cleanup` in `factory/cli.py:266` removes only a checker's worktree.
- The interim operating rule is already in `README.md:298-300`: "One caveat until #35 lands: agents of parallel runs share the launching session's scratchpad … so don't run parallel intakes on tickets whose roles may prototype in the same part of the code."
- Duplicate search: this request is GitHub issue #35 (open) and store ticket T-0021, whose triage this run is. No other open or closed ticket covers it. Issue #39's own row "H8" is a different finding: tests that need a clean checkout. It shares only the label with the retro's H8. T-0022 is issue #40, about planner labels, and does not overlap.

Assumptions:
- (inference) The fix applies to every role, not only checkers. Both of the request's examples of shared-scratchpad collisions involve a spec writer and a verifier.
- (inference) The session scratchpad comes from the host's own system prompt, which tells the agent to always use it for temporary files. The preamble rule must say that it takes precedence over that instruction. Otherwise agents will follow the host's instruction.
- (inference) Run-0062's `.venv` was not a file the role chose to write. `uv` created it when it walked up from a worktree under the dev checkout. A preamble rule about where to write scratch files may not stop that. The spec writer should show the proposed change covers this case, or split it out and say so.
- The requester's A, B and C are proposals, not requirements. The requirements are: no two runs share a scratch location, no run leaves files in the dev checkout, and scratch is cleared after the run unless the run parked.
- Per the briefing, the ticket also updates `docs/design.md` §Shared preamble, its changelog entry in `docs/changelog.md`, the re-copied `docs/prompts/` file and `dev/build-harness.spec.md`. It also updates the README: when the fix lands, the caveat at `README.md:298-300` is removed or changed.
- The request names no Nanobot-side commit with an existing fix. Nanobot's checkout now holds only `.factory/`, so there is no reference fix to check against.
- Suggested priority (a suggestion only; the operator sets priority): p1. Until it lands, parallel intake carries the README caveat.

Reason: ACCEPT. The intent is clear and backed by four cited runs, three of which I checked in their output files. No product decision is needed to write the spec. The operator's queue policy (`.factory/answers/queue-preapproval-policy.md`) applies at the spec gate, not here.

STATUS: ACCEPT
CONFIDENCE: high, because I checked three of the four cited runs in their output files and the current harness code shows no scratch handling; run-0103's claim rests on the retro text alone.
ESCALATIONS: none
