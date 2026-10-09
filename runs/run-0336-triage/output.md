Type: feature

Title: Send the spec writer, critic and planner only the specs and decisions their ticket touches, with a complete index of the rest and a command to open any of it

Summary:
The spec writer (the agent that turns a ticket into a spec), the spec critic (the agent that reviews that spec) and the planner (the agent that splits an approved spec into sub-tickets) are each handed the whole spec store as input: every capability's current truth (the store's spec of how each capability behaves today, one `openspec/specs/<capability>/spec.md` per capability) and the whole decision log (`decisions.md`, the standing decisions). On the Nanobot store that makes the writer's input 102 KB on average and up to 416 KB, and that input is re-sent on each of a run's model calls, a median of 45. The requester wants these roles to receive in full only the capabilities the ticket touches and the decisions that name them, plus a complete one-line-per-item index of everything else, and a command to print any capability or decision on demand. Nothing is hidden, only deferred. The requester also wants writer input size measured on both stores before and after, with targets on the Nanobot store of a mean below 40 KB and a maximum below 100 KB.

Evidence:
- Request (issue #75, https://github.com/danielphang/spec-factory/issues/75): "On the nanobot store the writer's composed `input.md` averages 102 KB and the largest is 416 KB, about 104k tokens. In that largest input, 300 KB is "Requirements" ... and 51 KB is the whole decision log. The ticket touched one or two capabilities."
- Request: writer runs take a median of 45 API calls, p90 80 (105 transcripts). It cites SWE-agent (Yang et al., NeurIPS 2024, https://arxiv.org/html/2405.15793): a 100-line window scored 18.0%, the full file 12.7%.
- Checked on this checkout (`~/dev/spec-factory`, `main` at `9a25809`):
  - `factory/compose.py:33-37` `current_truth` returns every `openspec/specs/*/spec.md`.
  - `add_truth` (`:168-170`) adds each one, and `add_decisions` (`:172-176`) adds the whole `decisions.md`.
  - The `spec_writer` branch (`:182-188`) and the `critic` branch (`:203-206`) call both.
  - The `planner` branch (`:224-229`) calls only `add_decisions`. The planner gets the whole decision log but no current truth. This differs from the request, which says all three add every spec.
- Measured with `stat` over `runs/*-spec_writer/input.md`:
  - Nanobot store (`~/dev/nanobot-upstream/.factory/store`, read only): 38 writer inputs, mean 102 KB, max 416 KB.
  - This store: 60 writer inputs, mean 58 KB, max 217 KB. The request says 56 KB; the store has grown since.
  - The Nanobot store today has 22 capability specs totalling 410,318 bytes and a 71,430-byte `decisions.md`. The request says 20 capabilities, 404 KB of specs and 68 KB of decisions, so the store has grown since it was written.
  - `run-0276-spec_writer/input.md` on the Nanobot store: the largest sections are "Requirements" sections of 71, 43 ("ADDED Requirements"), 42, 26, 24 and 23 KB, and a 50.5 KB "Decision log". This matches the request.
- `factory spec` and `factory decision` already exist as command groups (`factory/cli.py:1462`, `:1538`), but neither has a `show` subcommand. `factory/cost.py` exists. #70 (`factory stats`) is "not in intake" (`dev/issues.md:76`).
- Duplicate search: there is no duplicate among `.factory/store/tickets/T-*.yaml` or `dev/issues.md`. T-0036 is this request's own ticket. The nearest ticket is T-0030 (#24 parts A and C, token cost), whose sub-ticket T-0030.3 ("Each role's input cut to the spec sections it uses", merged) lists "The triage and spec writer inputs, and the critic's current spec" as out of scope (`.factory/store/specs/T-0030.3/subticket.md:32-33`). So this request extends that work and does not repeat it.

Assumptions:
- Inference: for the planner, the change covers only the decision log, because the planner receives no current truth today. "Nothing changes for roles that do not receive current truth today" then means triage, implementer, reviewer and verifier are untouched.
- Inference: proposed change A changes the triage output format, so it changes the triage prompt in `docs/design.md`, its re-copy under `docs/prompts/` (a generated, protected path), the changelog, `dev/build-harness.spec.md` and the README. The spec must declare those paths and `factory/**` in its Risk section.
- Inference: the measurement in D can use `factory/cost.py` or a plain size count of `input.md` files if #70 has not landed. The request allows either.
- Proposed changes A to D, and the 40 KB / 100 KB targets, are the requester's suggestion. The evidence and the stated decisions ("no capability is hidden, only deferred"; the critic sees the writer's list plus whatever the writer opened) are the requirement.
- Suggested priority (a suggestion; priority is the operator's call): p1, as `dev/issues.md:80` already records. Sequence it after T-0030.3 and before #64.

Reason: The intent, the evidence, the design decisions, the sequencing, what is out of scope and a runnable acceptance are all stated. The figures re-measure as stated within a few percent. The one factual slip (the planner gets no current truth) narrows the change and does not block it. The spec gate covers the remaining design detail, such as how the index line and the decision filter are formed.

STATUS: ACCEPT
CONFIDENCE: high, the size figures and the compose wiring were re-measured on both stores and read in `factory/compose.py`, and no duplicate ticket exists
ESCALATIONS: none
