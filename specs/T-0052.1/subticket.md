T-0052.1 / Fix the YAML frontmatter in four role agent templates, test every template's frontmatter, and have `factory init` report a target copy that differs from its template
Depends on: none
Parallel-safe: yes

Parent: T-0052, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Every role agent template's frontmatter parses and carries name, description, model and tools
- The four fixed templates keep their description's words and every other line
- The suite fails on a template with broken frontmatter and names it
- init reports an edited agent copy and leaves it as it is
- init still creates a missing agent copy and lists no matching copy
- README describes init's report of a differing agent copy
- The changelog records issue 108 in one entry without a numbering gap
- README stays within its line budget and both documents pass the whitespace check
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
