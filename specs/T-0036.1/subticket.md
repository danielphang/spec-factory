T-0036.1 / Send the spec writer, critic and planner only the specs and decisions their ticket touches, with a complete index of the rest and a command to open any of it
Depends on: none
Parallel-safe: yes

Parent: T-0036, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A ticket naming one capability composes inputs with only that capability in full and an index line for each other one
- Decisions of other tickets and capabilities reach each role as one index line per ticket
- Without a Capabilities line every capability and every decision reach the writer, critic and planner
- The harness suite passes with the new inputs
- A triage input lists every capability by path and requirement, and its prompt asks for the Capabilities line
- The prompt copies, design, build spec, README and changelog name the capability index
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
