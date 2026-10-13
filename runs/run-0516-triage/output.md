Type: bug

Title: Fix the YAML frontmatter in four role agent templates, test every template's frontmatter, and have `factory init` report a target copy that differs from its template

Summary:
A role agent template is a Claude Code agent definition in `agents/`; `factory init` copies each one into a target repo's `.claude/agents/`. In four of the six templates (planner, spec-critic, spec-writer, triage), the frontmatter is not valid YAML. Each `description:` is an unquoted value that contains `: `, which YAML reads as a second key, so Claude Code cannot load these definitions. The operator saw this reported for `factory-spec-writer.md` on 2026-10-13. The requester wants three things: the four descriptions fixed with nothing else in the files changed; a suite test that parses every template's frontmatter and checks that it has `name`, `description`, `model` and `tools`; and `factory init` reporting any target copy that differs from its template, still without overwriting it, so stale copies show up.

Evidence:
- I checked this on the checkout. I parsed each template's frontmatter with `yaml.safe_load` (run in the fresh-HOME wrapper through `uv run --frozen python`):
  - `factory-clerk.md` and `factory-stub.md` parsed with keys `description, model, name, omitClaudeMd, tools`.
  - `factory-planner.md`, `factory-spec-critic.md`, `factory-spec-writer.md` and `factory-triage.md` failed with `mapping values are not allowed here`, at the `: ` after `Planner role` / `Spec critic role` / `Spec writer role` / `Triage role` on the `description:` line.
- I also checked how init copies the templates, in `factory/setup.py:180-184`. It globs `instance.AGENTS` for `factory-*.md` and copies a file only `if not (dest / src.name).exists()`. An existing copy is never compared or refreshed, as the request says.
- I compared the Nanobot copies with `cmp`. All six files in `~/dev/nanobot-upstream/.claude/agents/` are byte-identical to `agents/`, so the four broken ones are broken there too. The commit `4d548d574` ("factory: nanobot is a spec-factory target (lionbot-v3.5 instance)") exists. I only read that repo.
- The template history (`git log -- agents/`) is `9b45041` (2026-10-01) and `f5d8203` (2026-10-03), as the request says.
- The request says no run has failed because the Workflow runs pass `inlineRoles: true` and `factory drive` runs `claude -p`. `factory/workflows/intake.js:29-32` reads `inlineRoles`. README line 706 tells operators to pass `inlineRoles: true` on every target.
- README line 463 describes `.claude/agents/factory-*.md` as written by "`factory init`, when they are missing". Part C changes what init reports, so this row and the init section near README line 581 may need updating in the same ticket.
- Duplicates: none found. Issue #108 in `dev/issues.md:111` maps to this ticket (T-0052). I grepped tickets and requests for `frontmatter`, `factory-spec-writer` and `stale cop`. That found only T-0012, T-0028 and T-0045. All three are closed and none is about agent frontmatter.

Capabilities: store-setup, harness-docs

Assumptions:
- (Inference) "Reports" in part C means a field or line in init's existing output, naming each differing copy. The request does not say which form. The spec writer should pick one that matches how init already reports created files (`setup.py` collects them in an `agents` list).
- (Inference) "Differs from its template" means any byte difference, which matches the request's own byte-identical check. A target the operator has edited on purpose would also be reported. That is a report, not a refusal, so it does not seem to need a product call.
- (Inference) Refreshing Nanobot's four copies is not part of this ticket. The request gives it to the Driver once part A is live, and `~/dev/nanobot-upstream/**` is a protected path here.
- (Inference) Parts A and C touch the protected paths `agents/**` and `factory/**`. The spec's Risk section has to declare both.
- I could not check Claude Code's own frontmatter parser. The failure is confirmed with PyYAML `safe_load`. That Claude Code rejects these files rests on the operator's report.
- Priority, as a suggestion only: small. The request asks for it right after T-0048 (#101), which is closed, and before #104 (T-0049).

Reason: Accepted. The defect is reproduced, the intent is clear, and the request makes the one behaviour choice itself: init reports a stale copy and never overwrites it.

STATUS: ACCEPT
CONFIDENCE: high, because I reproduced the parse failures, the copy-only-when-missing logic and the byte-identical Nanobot copies on the current checkout.
ESCALATIONS: none
