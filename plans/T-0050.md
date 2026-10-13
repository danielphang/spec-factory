T-0050.1 / `run start` takes each role's model from the instance and refuses a `--model` that differs, so a Workflow run cannot start on a model the instance never named
Depends on: none
Parallel-safe: yes

Parent: T-0050, approved spec v1. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model
- A run start given the instance's own model is accepted and records it
- An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it
- A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model
- The harness suite passes with only the two fixtures that passed a wrong model changed
- The build spec and the README describe the model check
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
