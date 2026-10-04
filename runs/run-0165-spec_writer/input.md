## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0165-spec_writer/output.md`

## Ticket (Triage output)

Type: bug

Title: Role test runs can write the operator's real home directory, and planner field lines written as `- ` bullets lose their dependencies without a word

Summary:
Two harness faults, both found during one build on the Nanobot instance (the factory's other target repository) on 2026-10-04. First, a safety fault: the agents the factory runs for each step (its roles) run tests with the operator's real `HOME`, so a test that resolves a path from `HOME` before a fixture redirects it can overwrite live production state. One implementer run did exactly that to the live bot's `~/.nanobot/policies.json` and its `.bak`. The requester needs every command a role runs to be kept away from the real home and the instance's declared credentials paths, and the safe command to be the one a role is handed. Second, the parser that turns the planner's plan into sub-tickets (the store's ticket records, one per unit of work) ignores field lines that start with `- `, so all eight sub-tickets of one plan were dispatched with no dependencies and no parallel-safety flag; the requester needs bullet field lines read, and a sub-ticket with no `Depends on:` line refused by name rather than treated as having no dependencies.

Evidence:
- The live-state write is recorded by the run that caused it. `~/dev/nanobot-upstream/.factory/state/runs/run-0080-implementer/output.md` line 1: "this run overwrote the live policy store in `~/.nanobot/`." Line 92: the first run of `uv run pytest tests/policy` "with the real `HOME`" wrote `/Users/dphang/.nanobot/policies.json` and `policies.json.bak`. Line 93 gives the cause: the test module imported the path function by name at collection, before the conftest fixture patched it, and the run's own error was `FileExistsError: [Errno 17] File exists: '/Users/dphang/.nanobot/policies.json'`. This confirms the request's account.
- Protected paths are a sentence in the prompt, not a control. `.factory/instance.yaml` line 19 declares `credentials: ["~/.nanobot/**"]`. The only harness reader of `protected_paths` is `factory/instance.py` line 175, which fills the preamble's protected-path line. The preamble is the rules text every role reads first. `grep -rn HOME factory/ bin/` prints nothing, so the harness sets no `HOME` for anything it runs.
- The request quotes Claude Code's permissions page (code.claude.com/docs/en/permissions.md): `permissions.deny` does not cover "arbitrary subprocesses that read or write files indirectly, like a Python or Node script". I did not re-fetch that page.
- The bullet fault reproduces on the runtime, the pinned checkout of the harness that runs tickets (`~/dev/spec-factory-harness` at `61ccf8d`). `factory/subtickets.py` line 17 is `FIELD_RE = re.compile(r"^\s*\**\s*([A-Z][A-Za-z -]+?)\s*:\s*\**\s*(.*)$")`. I fed `parse()` a three-sub-ticket plan. The output was `T-0002.1 [] False`, `T-0002.2 [] False`, `T-0002.3 ['T-0002.2'] True`. The two sub-tickets written with `- ` field lines lost `Depends on: T-0002.1` and `Parallel-safe: yes`. The one written with `* ` lines kept both, because the regex's leading `\**` consumes a `*` bullet. So `* ` bullets already parse, and only `- ` bullets are lost.
- The real plan's field lines are bullets: `~/dev/nanobot-upstream/.factory/state/plans/T-0002.md` lines 53, 79, 120, 164, 204, 233, 269 and 300 each start `- Depends on:`. Every sub-ticket record `T-0002.1` through `T-0002.8` in that store holds `depends_on: []` and `parallel_safe: false` at lines 30 and 31.
- The missing-line default is silent by design. `factory/subtickets.py` line 62 starts every sub-ticket with `"depends_on": [], "parallel_safe": False`, and a block with no matching field line keeps those defaults with no error.
- The request reports the downstream cost: sub-tickets 2 to 8 BLOCKED, about 3M tokens. I did not verify that figure.
- The request reports earlier faults of the same kind, where a planner line was formatted in a way the parser did not expect. The first is GitHub issue #13 (open, folded into #20 and #21). The second is spec-factory T-0014, whose plan was normalised by hand (`.factory/answers/T-0014-plan-normalised.md`).

Duplicate search: none. This request is GitHub issue #36 and is ticket T-0019. Open issues #27 to #35 cover other faults. T-0018 (issue #33, in flight, sub-ticket `T-0018.1` at `ready-for-implementer`) also fixes a parser that misreads a formatted line, but that parser reads the gate line, not plan fields. Its plan does not touch `FIELD_RE` or the `Depends on:` default (`.factory/state/plans/T-0018.md`).

Assumptions:
- (Inference) One fact in the request does not hold on every instance. The request says "Gate commands run under a throwaway `HOME`". That is true only on the Nanobot instance, and only because its own `instance.yaml` (lines 29 and 30) writes `HOME="$(cd "$(mktemp -d)" && pwd -P)"` into its gate command strings. This instance's gate commands (`.factory/instance.yaml`, `gate_commands`) set no `HOME`, and the harness adds none. The proposed change B says the wrapped command is "taken from the gate's environment", but the harness has no gate environment to take it from. The spec writer has to choose where the throwaway `HOME` comes from: the harness wraps it, or each instance declares it. The intent is clear either way, so I took this as a design choice for the spec rather than a missing fact.
- (Inference) "The instance's plain test command" means the test command in the target's briefing, the instance file every role reads. On Nanobot that is `~/dev/nanobot-upstream/.factory/context.md` line 14, which has no `HOME`. There is no test-command key in `instance.yaml`. Implementers and checkers already receive the gate commands verbatim (`factory/compose.py` lines 128 to 132). On Nanobot those are HOME-wrapped, but the briefing's shorter command was the one run. Triage, the spec writer and the planner get no gate commands at all, and they run commands too.
- (Inference) "State paths unreachable" in proposed change A can only be a rule the role is told to follow, because the request puts OS-enforced denial outside this ticket. A throwaway `HOME` does not protect against code that uses an absolute path such as `/Users/dphang/.nanobot`.
- (Inference) Proposed changes A and D edit prompt text that the design doc holds. Under this repo's conventions they bring a changelog entry, a consistent `dev/build-harness.spec.md` and re-copied `docs/prompts/` files. Proposed changes B and C edit harness code under `factory/**`. All of these are protected paths, and the spec's Risk section must declare them.
- (Inference) The two problems are independent and can be planned as separate sub-tickets. The requester filed them together, and I have not split the ticket.
- (Suggestion, priority is a human call) p0, as labelled. The live-state write has already happened once, and the parser fault silently reorders any plan whose author uses `- ` bullets.

Out-of-scope observations:
- The T-0002 plan writes pairwise parallel-safety, for example line 80 "yes with T-0002.3, T-0002.4 and T-0002.7 … Not with T-0002.8". The parser reads only a leading `yes`, so a line like that would make the sub-ticket parallel-safe with every sibling, including the ones it excludes. Fixing the bullet would make this live on the next such plan. The planner prompt (`factory/prompts/planner.md` line 25, `Parallel-safe: yes | no (reason)`) does not ask for pairwise answers, so the spec writer may want to state which form is allowed.
- The request leaves OS-enforced write denial through Claude Code's sandbox to the operator, and so does this ticket.

STATUS: ACCEPT
CONFIDENCE: medium. Both faults are reproduced from records and the runtime parser. Where the throwaway `HOME` comes from is left to the spec, because the request's "gate's environment" does not exist in the harness.
ESCALATIONS: none

## Request (raw)

---
title: "P0: role test runs can write live state outside the worktree; planner field bullets silently drop dependencies"
labels: "harness, p0"
---
**Problem 1 (safety):** an agent's test run overwrote live production state. On 2026-10-04, during the Nanobot v3.5 build of T-0002 (SPEC-20, the policy store), T-0002.1's implementer (run-0080) ran its new tests before they were isolated. The new store module defaulted to the real `~/.nanobot/policies.json`, so the tests overwrote the live bot's `policies.json` and its `.bak`. The live per-chat permissions were lost until the operator restored them. Two causes:
- **Only the gate isolates HOME.** Gate commands run under a throwaway `HOME`, but the roles' own test runs use the instance's plain test command, so a test that resolves a path from `HOME` before a fixture redirects it writes the real home.
- **Protected paths are not enforced.** `credentials: ~/.nanobot/**` is declared, but nothing enforces it while a role runs. Claude Code's `permissions.deny` cannot catch this either: it does not apply to "arbitrary subprocesses that read or write files indirectly, like a Python or Node script" (code.claude.com/docs/en/permissions.md).

**Problem 2 (planner parse):** a planner that writes its fields as Markdown bullets loses them silently. The T-0002 plan wrote `- Depends on: T-0002.1` and `- Parallel-safe: …`. `subtickets.FIELD_RE` does not match a line starting with `- `, so all eight sub-tickets came out with `depends_on: []` and `parallel_safe: false`. They were dispatched without their order, and 2 to 8 BLOCKED, about 3M tokens. Reproduced with the runtime's parser on `plans/T-0002.md`. The same class of fault as #13 and spec-factory T-0014 (`ID / Title:` head line).

**Proposed change:**
- A. **Preamble, a hard rule:** every test, script or prototype a role runs, runs with `HOME` set to a fresh temporary directory, and with the target's state paths (the instance's `credentials` class) unreachable. Never run anything that may write outside your worktree or run scratch directory without it.
- B. **Compose:** the role's input names the instance's test command already wrapped with a throwaway `HOME`, taken from the gate's environment, so the easiest command to copy is the safe one. A target whose test command cannot run under a throwaway `HOME` declares so in `instance.yaml`, and the role is told.
- C. **Parser:** field lines may start with a list bullet (`- `, `* `). Every sub-ticket must carry a `Depends on:` line, `none` included. A plan with a sub-ticket that has no `Depends on:` line is refused with the sub-ticket named, never defaulted to "no dependencies".
- D. **Planner prompt:** the OUTPUT example shows the field lines exactly as the parser reads them.

**Outside this ticket, the operator's decision:** OS-enforced write denial through Claude Code's sandbox (`sandbox.enabled`, `sandbox.filesystem.denyWrite: ["~/.nanobot"]`, code.claude.com/docs/en/sandboxing.md) in each runner session's project settings. Whether agents launched by a workflow inherit the session's sandbox is undocumented and must be tested with a canary write before relying on it.

## Critic findings on your previous version

## Critic review of T-0019 (v1)

Spot-checks performed on `main` at `17efb50`:
- Paths: `factory/subtickets.py` line 17 is the quoted `FIELD_RE`, line 62 the `"depends_on": [], "parallel_safe": False` default, line 88 the `startswith("yes")` read; `factory/compose.py` lines 128-132 render the gate commands verbatim in "Where you work" for build roles only; `factory/instance.py` lines 168-179 (`fill_preamble`) are the only `protected_paths` reader; `.factory/instance.yaml` line 19 is `credentials: ["~/.nanobot/**"]`; `grep -rn HOME factory bin` prints nothing; `factory/workflows/build.js` line 200 parks with `harness-bug: subticket add:`; `factory/cli.py` lines 395-397 map `ValueError` to `Refused`; `.factory/answers/T-0014-plan-normalised.md` and issue rows #13, #36, #37 in `dev/issues.md` exist. The Nanobot `run-0080-implementer/output.md` lines 92-93 carry the quoted `FileExistsError` and cause (read only).
- Acceptance commands run with the GIVEN fixtures on a scratch store: "Dash-bulleted field lines" printed all three sub-tickets `ready-for-implementer`, `depends_on: []`, `parallel_safe: false`; "A sub-ticket with no Depends on line" printed the success JSON, `exit=0`, three ticket files; "A triage input's wrapper" printed `fresh_home=no real_home_untouched=yes cache=` and the input has three `## ` sections; "run_env cannot set HOME" printed `exit=0 input=written`; both `SAME` checks print `SAME`; the planner-prompt greps print `0`. Every "today" result in verification.md that I ran matches.
- Tests to change: `test_instance.py` lines 265-271 (`startswith` on context then `## Output file`), 274-288 (compares every preamble line except 0, i, w, so added lines are compared), 303 (byte-identical copy); every plan fixture I found (`test_shepherd.py` 295/350/408, `test_parent_close_reuse.py` 15-18, both stub `planner-1.md`) has a `Depends on:` line per sub-ticket. "none" is right.

Findings:

[BLOCKING] 6 Operator steps, first paragraph
Problem: "the runtime" is a term specific to this system and is glossed only in Risk, which is not one of the sections the gate operator is assumed to read, so the operator cannot tell from Problem, Evidence, Decisions or Operator steps what has to "move" before step 1 applies.
Evidence: the gloss "the runtime, the pinned checkout of the harness that runs tickets" appears once, in Risk (line 122 of proposal.md); Operator steps line 136 uses "runtime" bare. The rubric makes an unglossed system term in the first paragraph of a human-facing section BLOCKING even when inferable. The fix is one phrase.
Suggested fix: in Operator steps, write "once the runtime (the pinned checkout of the harness that runs tickets) has moved to a revision with this change", and leave the Risk sentence as is or shorten it.

[SHOULD-FIX] 4 Decisions / Operator steps
Problem: this repository's own instance gets no `run_env`, so every implementer and verifier worktree here resolves `uv`'s cache under the throwaway `HOME` and re-downloads its packages on each fresh worktree, and the spec neither decides that this cost is acceptable nor gives the operator a step to add `run_env` here as it does for Nanobot.
Evidence: Evidence paragraph 6 reports "uv installed 6 packages" in a fresh worktree under a throwaway `HOME`; `.factory/instance.yaml` is out of scope (line 102), so only an Operator step can set it; Operator steps cover Nanobot only.
Suggested fix: either add an Operator step 3 for this repo's `instance.yaml` (`UV_CACHE_DIR`, and `UV_PYTHON_INSTALL_DIR` if a managed Python is in use), or add a Decision that this repo runs without `run_env` because the re-download is six small packages per worktree.

[SHOULD-FIX] 3 Proposed change (whole)
Problem: the ticket bundles two independent faults (role test isolation: A, B, E2, E3, F-isolation; plan parsing: C, D, F-plan-fields) in one PR of about a dozen files without marking NEEDS-SPLIT or naming the seam, so a reviewer of either half reads the other's diff and a defect in one blocks the other.
Evidence: Problem names them as two faults with no shared code; Root cause lists disjoint files for each; only E1's changelog entry joins them.
Suggested fix: mark NEEDS-SPLIT with the seam above, and say which half carries the changelog entry (or that each adds its own clause to one entry number, written by whichever merges first).

[NIT] 6 Problem, paragraph 3
Problem: "every one of them parked" uses the ticket state `parked` without saying what it is.
Evidence: no gloss anywhere in the human-facing sections; Risk later says "parks the parent with the refusal text".
Suggested fix: "were set aside as `parked`, the state for a ticket the build has stopped on".

[NIT] 2 Acceptance: "This repo's gate suite passes under a throwaway HOME" and "The harness suite passes"
Problem: the two scenarios run the same two-minute suite twice, once wrapped and once bare, and after part A the preamble tells the role to run the bare one through the wrapper anyway, so the second adds no evidence.
Evidence: role-run-isolation spec lines 291-293 and harness-docs spec lines 367-369; `factory/prompts/implementer.md` line 15 counts an acceptance command that ran a gate command "exactly as written" as that gate's run, and after B4 the handed form is the wrapped one.
Suggested fix: drop the bare scenario, or keep only it and note that the wrapped form is the gate command as handed.

[NIT] 4 Part A rule text
Problem: "That includes every command your briefing, ticket or spec gives you" invites a role to run `git commit` through the wrapper, where a fresh `HOME` hides `~/.gitconfig` and the commit fails for want of an identity; the failure is loud, not silent, so this is wording, not a defect.
Evidence: the rule's first bullet scopes itself to "test, script or prototype" and then widens to "every command"; nothing in the harness sets `user.name` in a worktree (`grep -rn "user.name" factory` was not run; I did not verify).
Suggested fix: "every test or check command your briefing, ticket or spec gives you".

Out-of-scope observations:
- Neither target runs the `agents/` role definitions today (`README.md` line 272: `inlineRoles: true` on every target), so the stale planner OUTPUT block in `agents/factory-planner.md` is inactive; the spec's observation stands and is correctly out of scope.
- Each wrapper invocation leaves one temporary directory behind; nothing removes it. Harmless on a workstation; worth a line in the design doc paragraph if anyone runs this on a long-lived host.

STATUS: REVISE
CONFIDENCE: high; every cited path and all seven acceptance commands I ran match the spec's claims, and the one BLOCKING finding is a rubric-6 gloss with a one-phrase fix.
ESCALATIONS: none

## Your previous spec (v1)

=== proposal.md
## Problem

Two faults in the spec factory's harness put the operator's live data and build budget at risk. Both were hit on 2026-10-04 while the factory built a change for the Nanobot chat bot. The spec factory runs each requested change through a chain of AI agents called roles: triage, spec writer, critic, planner, implementer, reviewer and verifier. The harness is the code that composes each role's input and records what it returns.

**A role's test run can overwrite live production data.** Roles run tests and scripts with the operator's real home directory as `HOME`. On the Nanobot instance (the factory's other target repository), an implementer's new tests computed a file path from `HOME` before the test fixture redirected it. They overwrote the live bot's per-chat permission file and its backup in `~/.nanobot/`, and the operator restored them by hand. Each instance lists sensitive locations, such as live credentials, as protected paths in its config. The harness only prints that list into the rules every role reads, and nothing points a role's commands away from those locations. A role is handed ready-made commands in one case only: the gate commands, the instance's lint and test commands that the implementer and verifier must run. Those run under a throwaway `HOME` only where an instance wrote that into its own config. Nanobot did; this repository did not. Triage, the spec writer, the critic and the planner are handed no command at all, so they copy the plain test command from the instance's briefing, the text every role reads first.

**The planner's dependency order can vanish without a word.** The planner splits an approved spec into sub-tickets, units of work that each become one branch and one merge. For each, it writes a `Depends on:` line naming the sub-tickets that must merge first. It also writes a `Parallel-safe:` line saying whether the sub-ticket may be built while its siblings are. The harness reads those lines with a pattern that skips a line starting with a `- ` list bullet. A sub-ticket whose lines are written that way is recorded as having no dependencies and as not parallel-safe, and nothing reports it. All eight sub-tickets of one Nanobot plan were written that way, were dispatched out of order, and every one of them parked. A sub-ticket with no `Depends on:` line at all gets the same silent default.

The fix hands every role a wrapper that runs a command under a throwaway `HOME`, with the gate commands already wrapped. It adds a rule to the shared preamble, the rules text at the top of every role's prompt: run code only through that wrapper, and never run anything that could write a protected path outside the repository. It also makes the harness read bulleted field lines and refuse a sub-ticket that has no `Depends on:` line. The wrapper is guidance the role follows, not an operating-system control: a command can still write an absolute path.

## Evidence

Checked on `main` at `17efb50`. No harness code changed between `9b73efe`, where the last harness change merged, and that commit.

- The live-data write is recorded by the run that caused it. The Nanobot store's `runs/run-0080-implementer/output.md` says the first run of `uv run pytest tests/policy` "with the real `HOME`" wrote `/Users/dphang/.nanobot/policies.json` and `policies.json.bak`. It quotes the run's own error, `FileExistsError: [Errno 17] File exists: '/Users/dphang/.nanobot/policies.json'`. It names the cause: the test module imported the path function by name at collection, before the conftest fixture replaced it. A test that resolves a path from `HOME` early reaches the real home whenever the real `HOME` is set.
- The harness sets no `HOME` for anything a role runs. `grep -rn HOME factory bin` prints nothing. Roles are started by the workflow scripts' `agent()` calls (`factory/workflows/build.js` lines 75-86), which take no environment option. So the harness cannot change a role's own environment. It can only hand the role a command form to use.
- Protected paths are text, not a control. The only reader of `protected_paths` is `fill_preamble` (`factory/instance.py` lines 168-179). It writes the list into the preamble's "Protected paths for this repo" line. This repo's `.factory/instance.yaml` line 19 declares `credentials: ["~/.nanobot/**"]`.
- Only implementers and verifiers are handed commands, and this repo's are not isolated. `factory/compose.py` lines 128-132 put the gate commands verbatim in the "Where you work" section of build-role inputs only. Composing an implementer input on a scratch store printed ``Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` ``. Neither command sets `HOME`. A composed triage input had only three sections: `## Context for this run`, `## Output file` and `## Request (raw, with any answers appended)`. No section tells the role how to run code.
- The Nanobot instance worked around the gap by hand, in its own files. Its gate commands set `HOME="$(cd "$(mktemp -d)" && pwd -P)"`, a fresh temporary directory per run. They also pin `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` to the real home, and the config comment says why: "so the temp HOME does not re-download them". After the incident its briefing's test command was rewritten the same way, with a sentence telling every role to run repo code that way. A throwaway `HOME` therefore needs a per-instance way to keep tool caches reachable, or roles pay a cold download on every test run.
- This repo's own gate passes under a throwaway `HOME`. `(HOME="$(cd "$(mktemp -d)" && pwd -P)" uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `157 passed in 120.88s`. In a fresh detached worktree with no `.venv`, the same wrapping ran `tests/factory/test_subtickets.py` to `6 passed` after uv installed 6 packages. `git diff --check main...HEAD` under a throwaway `HOME` exits 0. Wrapping this repo's gate commands breaks nothing.
- The bullet fault reproduces through the command line. A plan whose three sub-tickets use `- Depends on:` and `- **Depends on:**` lines, added with `bin/factory subticket add T-0001 --file plan.md` on a scratch store, printed `"depends_on": []`, `"parallel_safe": false` and `"state": "ready-for-implementer"` for all three. So `ST-2`, which depends on `ST-1`, was ready to build at once. The same plan written with `* `, `**…**`, indented or plain lines keeps its dependencies: `ST-2` comes out `"depends_on": ["T-0001.1"]`, `"state": "waiting-dependencies"`.
- The cause is the field pattern and a silent default. `factory/subtickets.py` line 17 is `FIELD_RE = re.compile(r"^\s*\**\s*([A-Z][A-Za-z -]+?)\s*:\s*\**\s*(.*)$")`. Its leading `\**` consumes a `*` bullet as if it were emphasis, but nothing consumes `-`. Line 62 starts every sub-ticket at `"depends_on": [], "parallel_safe": False`, and nothing checks that a `Depends on:` line was read. A plan with `ST-2` missing its `Depends on:` line printed `exit=0` and created `T-0001.2` with `"depends_on": []`.
- The real plan used `- ` bullets. Every sub-ticket in the Nanobot store's `plans/T-0002.md` writes `- Depends on:` and `- Parallel-safe:`. All eight sub-tickets `T-0002.1` to `T-0002.8` are `parked`. Each has one implementer run, seven of them `BLOCKED`. The store log shows their `depends_on` and `parallel_safe` were later set by hand with `ticket set` at `2026-10-04T07:59:58Z`. The request puts the cost at about 3M tokens; I did not verify that figure.
- The planner prompt shows a form the harness cannot read. `factory/prompts/planner.md` lines 22-25 show `  ID / Title`, `  Depends on: none | IDs` and `  Parallel-safe: yes | no (reason)`, all indented. The head-line pattern (`HEAD_RE`, `factory/subtickets.py` line 16) accepts a sub-ticket's ID line only at column 0 or after a heading mark. So the example, copied literally, gives no sub-tickets at all. The prompt does not say that these lines are machine-read or that `Depends on:` is required.
- A pairwise answer reads as unconditional. The Nanobot plan writes lines like `- Parallel-safe: yes with T-0002.3, T-0002.4 and T-0002.7 … Not with T-0002.8`. Line 88 of `factory/subtickets.py` reads only a leading `yes`, so once bullets are read, that sub-ticket would be parallel-safe with every sibling, including the one it excludes.
- The three copies of each prompt block are identical today. The preamble block in `docs/design.md`, `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md` printed `SAME` under the awk-and-diff check in this spec's verification. So did the planner block and its two copies. The changelog's numbered entries run 1 to 47 with no gap.
- Earlier faults of the same class: an earlier planner head line in a form the parser did not expect (issue #13), and a plan normalised by hand before its sub-tickets could be created (`.factory/answers/T-0014-plan-normalised.md`).

## Root cause

- `factory/subtickets.py` line 17, `FIELD_RE`: no optional `- ` list bullet before the field name.
- `factory/subtickets.py` `parse`, lines 57-93: `depends_on` defaults to `[]`, and a block with no `Depends on:` line is accepted.
- `factory/compose.py` `compose`, lines 52-178: no role input says how to run code. `gate_commands` (lines 42-49) hands the instance's strings over unchanged, and only build roles receive them.
- `factory/prompts/preamble.md`, a byte-identical copy of the design doc's preamble block: no rule about `HOME` or about writes outside the repository.
- `factory/prompts/planner.md` lines 21-35, the design doc's planner block: the OUTPUT example indents the lines the harness parses and does not say that they are parsed.

## Out of scope

- OS-enforced write denial, such as Claude Code's sandbox settings, macOS `sandbox-exec` or a separate user account for roles. The operator decides this, and a separate investigation (issue #37) tracks it.
- Changing the environment a role process starts with. `agent()` has no environment option.
- Reading pairwise parallel-safety (`yes with A, not with B`). The parser keeps reading only a leading `yes`, and the planner prompt says how to write the line instead.
- Field lines in a numbered list or with a `+ ` bullet.
- Either instance's own files: `.factory/**` here and everything in `~/dev/nanobot-upstream`. The Nanobot `T-0002` sub-ticket records were already corrected by hand.
- `agents/factory-planner.md`, which holds an older copy of the planner OUTPUT block (see Out-of-scope observations).
- The retro role's input, which `run compose` does not build.
- The `harness-bug:` label that `build.js` line 200 puts on a refused `subticket add`.

## Open questions

none

## Decisions

- Every role runs tests, scripts and prototypes through a wrapper the harness hands it, which sets `HOME` to a fresh temporary directory; the instance's gate commands reach a role already wrapped. Rejected: each instance writes `HOME` into its own commands and briefing, as Nanobot did by hand, because this repository's gate has none and nothing checks briefing prose.
- The wrapper is `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`, a subshell, so the export covers every part of a compound command. Rejected: a `HOME=… <command>` prefix, which covers only the first command of `a && b`.
- An instance keeps a tool's cache reachable by listing it in a new `run_env` key, whose variables the wrapper exports after `HOME`; `run_env` may not set `HOME`. Rejected: the request's per-instance "cannot run under a throwaway HOME" opt-out, because it would silently reopen the hole for every role on that instance.
- A planner's field line may start with a `- ` or `* ` list bullet, and every sub-ticket must have a `Depends on:` line (`none` included); a plan with a sub-ticket that lacks one is refused with that sub-ticket named.
- A sub-ticket with no `Parallel-safe:` line still runs alone, as today.
- `Parallel-safe: yes` means safe alongside every sibling; a sub-ticket that is safe with only some siblings is written `no`.

## Risk

Blast radius: every role's composed input on every instance gains one section, and every gate command a role is handed changes form. A gate command that ends in a shell comment (`# …`) would comment out the wrapper's closing parenthesis. A `~/` in a gate command would expand to the throwaway home. Neither instance's gate commands contains `#` or `~` (checked: this repo's two, Nanobot's three). Nanobot's gate commands set their own `HOME` inside the wrapper; the inner setting wins and is another fresh directory, so the gate behaves as before. A plan that leaves out a `Depends on:` line, which used to be accepted, is now refused. The build then parks the parent with the refusal text (`factory/workflows/build.js` line 200), so no sub-ticket is built in the wrong order. Nothing changes for running tickets until the runtime, the pinned checkout of the harness that runs tickets, is moved to a revision with this change and each instance accepts it.

Protected paths this change touches:
- harness: `factory/compose.py`, `factory/subtickets.py`, `factory/instance.template.yaml`, `factory/prompts/preamble.md`, `factory/prompts/planner.md`;
- generated: `docs/prompts/00-preamble.md`, `docs/prompts/04-planner.md`.

Guardrail paths: the preamble and the planner prompt are agent prompts; parts A and D of this ticket ask for those edits. New tests go in new files. No existing test changes.

Not touched: `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Gate policy: this is more than the operator's small-blast-radius pre-approval covers. It changes every role's preamble and input, across about a dozen files. It waits for the operator at the spec gate. As a prompt change, it also gets the operator's acceptance test before the runtime moves.

## Operator steps

These come after the merge, once the runtime has moved to a revision with this change and the Nanobot instance has accepted it. Each instance refuses to run under a new harness revision until its operator accepts it with `--accept-harness <revision>`.

1. In the Nanobot instance's `.factory/instance.yaml`, add `run_env: {UV_CACHE_DIR: /Users/dphang/.cache/uv, UV_PYTHON_INSTALL_DIR: /Users/dphang/.local/share/uv/python}`. These are the two variables its gate commands already pin. Without them, every role test run there downloads every package again into a fresh home.
2. Check: compose any role run on that instance and confirm that the `## Running code` wrapper in its `input.md` names both variables.

=== design.md
## Proposed change

Size estimate: about 300 changed lines, about half of them new tests.

**A. A running-code rule in the shared preamble.** In the design doc's preamble block (`## Shared preamble (every agent)` in `docs/design.md`), insert this section after the "Protected paths for this repo" placeholder line and before the blank line that precedes `GUARDRAIL PATHS`, with one blank line before it:

```
RUNNING CODE
- Run every test, script or prototype with HOME set to a fresh
  temporary directory, never the real one: use the wrapper in the
  "Running code" section of your input. That includes every command
  your briefing, ticket or spec gives you.
- A throwaway HOME does not stop a write to an absolute path. Never
  run anything that could write a protected path outside the
  repository, such as live credentials or production state.
- If something you must run cannot work this way, stop and escalate.
```

Re-copy the block verbatim into `docs/prompts/00-preamble.md`, and make `factory/prompts/preamble.md` byte-identical to it (an existing test checks that).

**B. Every role is handed the wrapper** (`factory/compose.py`, `factory/instance.template.yaml`, `docs/design.md`)
- B1. Add a reader for the instance key `run_env`. Absent or null means an empty mapping. Refuse with `store.Refused` (exit 2, no `input.md` written) in three cases: the value is not a mapping; a name does not match `[A-Za-z_][A-Za-z0-9_]*`; or a name is `HOME`. The message names `run_env` and the offending name.
- B2. The wrapper is the string `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"<vars>; <command>)`. `<vars>` is, for each `run_env` entry in file order, a space, `NAME=` and `shlex.quote(str(value))`. Example with `{T0019_CACHE: /tmp/t0019 cache}`: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)" T0019_CACHE='/tmp/t0019 cache'; <command>)`. To wrap a command, replace `<command>` with it.
- B3. In `compose`, for every role, add this section directly after the `## Output file` part, with the wrapper in place of `WRAPPER`:
  ```
  ## Running code
  Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `WRAPPER`. Put your command in place of <command>. This includes every command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.
  ```
  The backticked wrapper is the only backticked text in the section that contains `<command>`. The section is not a store source, so `input_sources` does not change.
- B4. In the "Where you work" section of build-role inputs (lines 128-132), render each gate command through the wrapper, after `{integration}` is replaced. Example: `` `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)` ``. Change "exactly as written" to "exactly as written; each is already wrapped".
- B5. In `factory/instance.template.yaml`, after `environment_files`, add `run_env: {}` with this comment: variables the running-code wrapper exports after the throwaway `HOME`, for tools that keep a cache under `HOME` (for example `UV_CACHE_DIR`); `HOME` itself is refused.
- B6. In `docs/design.md`, in the **Role-context block** paragraph of the Harness section (line 54):
  - add "the variables kept for code runs (`run_env`)" to the parenthesised list of what `instance.yaml` holds;
  - at the end of the paragraph, add: "The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell with `HOME` set to a fresh temporary directory, exporting any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository."

**C. Bulleted field lines, and a required `Depends on:` line** (`factory/subtickets.py`)
- C1. `FIELD_RE` accepts an optional `- ` or `* ` list bullet before the optional emphasis marks: `^\s*(?:[-*]\s+)?\**\s*([A-Z][A-Za-z -]+?)\s*:\s*\**\s*(.*)$`. `HEAD_RE` does not change, so a bullet still never starts a sub-ticket.
- C2. In `parse`, note whether each block had a `depends on` field line. After the block is read, if it had none, raise `ValueError` naming the planner's label: `<label>: no "Depends on:" line; write "Depends on: none" when it depends on nothing`. `subticket_add` already turns a `ValueError` into exit 2, before it writes anything (`factory/cli.py` lines 395-397).
- C3. Update the module docstring: field lines may carry a list bullet, and every sub-ticket needs a `Depends on:` line.

**D. The planner prompt shows the lines the harness reads.** In the design doc's `## 4. Planner / decomposer` block, replace the four lines from `For each sub-ticket:` through `  Parallel-safe: yes | no (reason)` with these nine lines:

```
For each sub-ticket, first these three lines, exactly as shown and each
at the start of its own line; the ID line may follow a heading mark.
The harness reads them. A sub-ticket with no "Depends on:" line is refused.
Parallel-safe "yes" means safe alongside every sibling; else write "no".
ID / Title
Depends on: none | IDs
Parallel-safe: yes | no (reason)
Then:
```

The indented `Scope:` line and everything after it stay as they are. Re-copy the block verbatim into `docs/prompts/04-planner.md` and `factory/prompts/planner.md`. All three are identical today.

**E. Documents**
- E1. `docs/changelog.md`: after the last numbered entry (47 today) and before `Declined:`, add the next number: `<n>. After issue #36 (2026-10-04), where a role's test run overwrote the Nanobot bot's live permission file and a plan's bulleted field lines lost every sub-ticket's dependencies: ...`. It says four things:
  - every role runs tests, scripts and prototypes through a wrapper the composer hands it, which sets a throwaway `HOME`, with gate commands already wrapped and `run_env` for tool caches;
  - the preamble forbids running anything that could write a protected path outside the repository;
  - the harness reads `Depends on:` and `Parallel-safe:` lines that start with a list bullet, and refuses a sub-ticket with no `Depends on:` line;
  - the planner prompt shows the three parsed lines at the start of a line and says `yes` means alongside every sibling.
- E2. `README.md`, in "Roles, harness, workflows", in the **Roles.** paragraph after its first two sentences: add this sentence on one line, `Every role's input carries a wrapper that runs a command with a fresh temporary HOME, and the repo's check commands come already wrapped.`, followed by `It does not stop a write to an absolute path.`
- E3. `README.md`, "Adopting the factory in a repo", step 3: after the sentence that names `gate_commands` and `protected_paths`, add this sentence, with `run_env` in code format: "Set run_env for any tool whose cache lives under HOME, so it still finds that cache from inside the fresh temporary HOME." Keep everything from "so it still finds" to the end on one line. Bump the status-header date to the merge date.
- E4. `dev/build-harness.spec.md`: no change. I read the lines that describe what this change touches, and none is contradicted:
  - line 174 (`parallel_safe` comes from the planner's `Parallel-safe:` line);
  - line 204 (`run compose` opens the input with the role-context block, ahead of the declared sources; the new section is not a source);
  - lines 206 and 284 (`subticket add`).

**F. New tests**, in new files, driven through `bin/factory` on scratch stores:
- `tests/factory/test_run_isolation.py`:
  - the `## Running code` section in triage, planner and implementer inputs;
  - wrapped gate commands;
  - `run_env` export order and quoting;
  - the `HOME` and bad-name refusals;
  - a probe run through the wrapper sees a fresh `HOME`.
- `tests/factory/test_plan_fields.py`: `- ` and `* ` bullet field lines, with and without bold; a missing `Depends on:` line refused with the label named and no ticket written; `Depends on: none` still meaning no dependencies.

## Tests to change

none. Each existing test was checked against the change:
- Composed-input tests assert containment, the input's opening lines (`tests/factory/test_instance.py` line 271: context, then `## Output file`, which still comes second) or `input_sources`, which the new section does not join.
- The preamble test (`tests/factory/test_instance.py` lines 274-288) compares a run's system prompt with whatever `docs/prompts/00-preamble.md` holds, line by line around the filled lines, so the added lines are compared rather than rejected.
- `tests/factory/test_instance.py` line 303 requires `factory/prompts/preamble.md` to be byte-identical to `docs/prompts/00-preamble.md`, which part A keeps.
- Every plan in the suite gives each sub-ticket a `Depends on:` line: `test_subtickets.py`, `test_shepherd.py` (lines 295, 350, 408-409, 504), `test_parent_close_reuse.py` (lines 15-19), `test_build_startup.py` (which reuses `PLAN_LETTERS`), and the stub plans `accept-approve/planner-1.md` and `two-siblings/planner-1.md`.
- The template tests compare named keys only, so a new `run_env` key passes.
- No test reads the planner prompt's text.

=== specs/role-run-isolation/spec.md
## ADDED Requirements

### Requirement: Every role's input carries the throwaway-HOME wrapper
Every role input that `run compose` writes SHALL contain a `## Running code` section whose backticked wrapper runs a command with `HOME` set to a fresh temporary directory.

#### Scenario: A triage input's wrapper runs a command under a fresh HOME
Run every command in this file from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the four fixture scripts written by the block below, run once at column 0 as shown (every later scenario of this change reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0019-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T19=$(mktemp -d); export FACTORY_STATE=$T19/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T19/req.md && printf '## Problem\nx\n' > $T19/spec.md
bin/factory ticket new --file $T19/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T19/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0019-triage.sh <<'EOF'
# Sourced from the repo root: a scratch store with one triage run composed; IN is its input file.
# Set T19 before sourcing to reuse a directory (one holding an instance copy, for example).
T19=${T19:-$(mktemp -d)}; export FACTORY_STATE=$T19/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T19/req.md && bin/factory ticket new --file $T19/req.md >/dev/null
R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/')
bin/factory run compose $R >/dev/null; IN=$FACTORY_STATE/runs/$R/input.md
EOF
cat > ${TMPDIR:-/tmp}/t0019-impl.sh <<'EOF'
# Sourced after t0019-parent.sh: a scratch target repo, one sub-ticket, its implementer run composed; IN is its input file.
git init -q -b main $T19/t && git -C $T19/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T19/t FACTORY_INTEGRATION_BRANCH=main
printf 'T-0001.1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md >/dev/null
R=$(bin/factory run start --role implementer --ticket T-0001.1 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/')
bin/factory run compose $R >/dev/null; IN=$FACTORY_STATE/runs/$R/input.md
EOF
cat > ${TMPDIR:-/tmp}/t0019-probe.sh <<'EOF'
# Sourced after a script that set IN and T19: runs the wrapper from IN's "Running code" section
# around a probe that writes $HOME/t0019-probe and prints $HOME and $T0019_CACHE.
awk '/^## Running code$/{f=1;next} /^## /{f=0} f' $IN | grep -o '`[^`]*<command>[^`]*`' | head -1 | tr -d '`' > $T19/wrap
echo 'touch "$HOME/t0019-probe"; echo "$HOME|$T0019_CACHE"' > $T19/inner.sh
sed "s|<command>|sh $T19/inner.sh|" $T19/wrap > $T19/run.sh; O=$(sh $T19/run.sh); H=${O%%|*}
echo "fresh_home=$([ -n "$H" ] && [ "$H" != "$HOME" ] && [ -f "$H/t0019-probe" ] && echo yes || echo no) real_home_untouched=$([ -e "$HOME/t0019-probe" ] && echo no || echo yes) cache=${O#*|}"
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0019-triage.sh && . ${TMPDIR:-/tmp}/t0019-probe.sh)`
- THEN it prints exactly `fresh_home=yes real_home_untouched=yes cache=`

#### Scenario: Planner and implementer inputs carry the wrapper
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && R=$(bin/factory run start --role planner --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && bin/factory run compose $R >/dev/null && echo "planner $(grep -c '^## Running code$' $FACTORY_STATE/runs/$R/input.md)"); (. ${TMPDIR:-/tmp}/t0019-parent.sh && . ${TMPDIR:-/tmp}/t0019-impl.sh && echo "implementer $(grep -c '^## Running code$' $IN)")`
- THEN it prints `planner 1` then `implementer 1`

### Requirement: Gate commands reach a role already wrapped
The gate commands in a build role's input SHALL each be rendered inside the throwaway-HOME wrapper.

#### Scenario: The implementer's gate commands come wrapped
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && . ${TMPDIR:-/tmp}/t0019-impl.sh && grep -oF '(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)' $IN; grep -oF '(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)' $IN; echo end)`
- THEN it prints `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`, then `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`, then `end`

#### Scenario: This repo's gate suite passes under a throwaway HOME
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`
- THEN it exits 0 with no failures

### Requirement: An instance's run_env reaches the wrapped command, and cannot set HOME
The wrapper SHALL export each variable the instance lists in `run_env` after the throwaway `HOME`, and `run compose` MUST refuse, with exit 2 and no input written, a `run_env` that names `HOME`.

#### Scenario: Variables listed in run_env reach the command
- WHEN `(T19=$(mktemp -d); mkdir $T19/inst && cp .factory/instance.yaml .factory/context.md $T19/inst/ && printf "run_env: {T0019_CACHE: '/tmp/t0019 cache'}\n" >> $T19/inst/instance.yaml && export FACTORY_INSTANCE=$T19/inst && . ${TMPDIR:-/tmp}/t0019-triage.sh && . ${TMPDIR:-/tmp}/t0019-probe.sh)`
- THEN it prints exactly `fresh_home=yes real_home_untouched=yes cache=/tmp/t0019 cache`

#### Scenario: run_env cannot set HOME
- WHEN `(T19=$(mktemp -d); mkdir $T19/inst && cp .factory/instance.yaml .factory/context.md $T19/inst/ && printf 'run_env: {HOME: /tmp/t0019-home}\n' >> $T19/inst/instance.yaml && export FACTORY_INSTANCE=$T19/inst FACTORY_STATE=$T19/store && printf '# Fixture\n\nThe bot should do the thing.\n' > $T19/req.md && bin/factory ticket new --file $T19/req.md >/dev/null && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && bin/factory run compose $R >/dev/null; echo "exit=$? input=$([ -f $FACTORY_STATE/runs/$R/input.md ] && echo written || echo absent)")`
- THEN stderr contains `run_env` and `HOME`, and the last line is `exit=2 input=absent`

### Requirement: The preamble tells every role how to run code
The shared preamble SHALL tell every role to run tests, scripts and prototypes under a throwaway `HOME` through its input's wrapper, and never to run anything that could write a protected path outside the repository, identically in the design doc block, its prompt copy and the harness's preamble.

#### Scenario: The running-code rule is in every copy and in a run's system prompt
- WHEN `(. ${TMPDIR:-/tmp}/t0019-triage.sh && for f in docs/design.md docs/prompts/00-preamble.md factory/prompts/preamble.md $(dirname $IN)/system-prompt.txt; do echo "$(basename $f) $(grep -cxF 'RUNNING CODE' $f) $(grep -cxF -e '- Run every test, script or prototype with HOME set to a fresh' $f) $(grep -cxF -e '  run anything that could write a protected path outside the' $f)"; done)`
- THEN it prints `design.md 1 1 1`, `00-preamble.md 1 1 1`, `preamble.md 1 1 1` and `system-prompt.txt 1 1 1`

#### Scenario: The preamble block and its copies stay identical
- WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## Shared preamble \(every agent\)$/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/00-preamble.md && diff docs/prompts/00-preamble.md factory/prompts/preamble.md && echo SAME`
- THEN it prints `SAME`

=== specs/plan-parsing/spec.md
## ADDED Requirements

### Requirement: Bulleted field lines are read
A planner field line that starts with a `- ` or `* ` list bullet, with or without emphasis marks, SHALL be read as that field.

#### Scenario: Dash-bulleted field lines keep their dependencies
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\n- Depends on: none\n- Parallel-safe: no (alone)\n\n## ST-2 / Second\n- Depends on: ST-1\n- Parallel-safe: yes\n\n## ST-3 / Third\n- **Depends on:** ST-2\n- **Parallel-safe:** yes\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md | tail -1)`
- THEN the printed JSON's `subtickets` list is exactly `{"id": "T-0001.1", "label": "ST-1", "state": "ready-for-implementer", "depends_on": [], "parallel_safe": false}`, `{"id": "T-0001.2", "label": "ST-2", "state": "waiting-dependencies", "depends_on": ["T-0001.1"], "parallel_safe": true}`, `{"id": "T-0001.3", "label": "ST-3", "state": "waiting-dependencies", "depends_on": ["T-0001.2"], "parallel_safe": true}`

#### Scenario: Star-bulleted, bold, indented and plain field lines read as before
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\n* Depends on: none\n* Parallel-safe: yes\n\n## ST-2 / Second\n**Depends on:** ST-1\n**Parallel-safe:** yes\n\nT-0001-C / Third\n  Depends on: ST-2\n  Parallel-safe: no (same file)\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md | tail -1)`
- THEN the printed JSON's `subtickets` list is exactly `{"id": "T-0001.1", "label": "ST-1", "state": "ready-for-implementer", "depends_on": [], "parallel_safe": true}`, `{"id": "T-0001.2", "label": "ST-2", "state": "waiting-dependencies", "depends_on": ["T-0001.1"], "parallel_safe": true}`, `{"id": "T-0001.3", "label": "T-0001-C", "state": "waiting-dependencies", "depends_on": ["T-0001.2"], "parallel_safe": false}`

### Requirement: A sub-ticket with no Depends on line is refused by name
`subticket add` MUST refuse, with exit 2 and no ticket written, a plan in which any sub-ticket has no `Depends on:` line, and the refusal SHALL name that sub-ticket's label.

#### Scenario: A sub-ticket with no Depends on line is refused
- WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\nDepends on: none\nParallel-safe: yes\n\n## ST-2 / Second\nParallel-safe: yes\nScope: B\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md; echo "exit=$?"; ls $FACTORY_STATE/tickets)`
- THEN stderr contains `ST-2` and `Depends on:`, it prints `exit=2`, and the listing is `T-0001.yaml` alone

### Requirement: The planner prompt shows the lines the harness reads
The planner prompt's OUTPUT SHALL show the ID, `Depends on:` and `Parallel-safe:` lines each at the start of a line, SHALL say that a sub-ticket with no `Depends on:` line is refused, and SHALL say that `yes` means safe alongside every sibling, identically in the design doc block and its two copies.

#### Scenario: The planner prompt shows the parsed lines in every copy
- WHEN `for f in docs/design.md docs/prompts/04-planner.md factory/prompts/planner.md; do echo "$f $(grep -cxF 'ID / Title' $f) $(grep -cxF 'Depends on: none | IDs' $f) $(grep -cxF 'Parallel-safe: yes | no (reason)' $f) $(grep -cF 'A sub-ticket with no "Depends on:" line is refused.' $f) $(grep -cF 'Parallel-safe "yes" means safe alongside every sibling' $f)"; done`
- THEN it prints `docs/design.md 1 1 1 1 1`, `docs/prompts/04-planner.md 1 1 1 1 1` and `factory/prompts/planner.md 1 1 1 1 1`

#### Scenario: The planner block and its copies stay identical
- WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## 4\. Planner/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/04-planner.md && diff docs/prompts/04-planner.md factory/prompts/planner.md && echo SAME`
- THEN it prints `SAME`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the running-code wrapper and the plan rules
The changelog SHALL record this change as its next numbered entry with no gap, the README SHALL say every role's input carries the wrapper and how an instance sets `run_env`, and the design doc and the instance template SHALL name `run_env`.

#### Scenario: The changelog records the change in order
- WHEN `grep -cE '^[0-9]+\. After issue #36 \(2026-10-04\)' docs/changelog.md; awk '/^[0-9]+\. /{n++; if ($1+0 != n) bad=1} END{print (bad?"GAP":"CONTIGUOUS")}' docs/changelog.md`
- THEN it prints `1` then `CONTIGUOUS`

#### Scenario: The README describes the wrapper and run_env
- WHEN `grep -cF "Every role's input carries a wrapper that runs a command with a fresh temporary HOME, and the repo's check commands come already wrapped." README.md; grep -cF 'so it still finds that cache from inside the fresh temporary HOME.' README.md; grep -c 'run_env' README.md`
- THEN it prints `1`, then `1`, then a number of 1 or more

#### Scenario: The design doc and the instance template name run_env
- WHEN `grep -c 'run_env' docs/design.md factory/instance.template.yaml`
- THEN both counts are 1 or more

#### Scenario: The harness suite passes
- WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
- THEN it exits 0 with no failures

#### Scenario: The change adds no whitespace errors
- WHEN `git diff --check main...HEAD; echo "exit=$?"`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Every scenario after the first needs the first scenario's GIVEN block run once. It writes `${TMPDIR:-/tmp}/t0019-parent.sh`, `t0019-triage.sh`, `t0019-impl.sh` and `t0019-probe.sh`. Every command runs from the repository root of the checkout under test, after `uv sync --frozen`. Each "today" result below was produced by running the GIVEN block and then the WHEN verbatim on `main` at `17efb50`.

- A triage input's wrapper runs a command under a fresh HOME → NEW. Today it prints `fresh_home=no real_home_untouched=yes cache=`. The input has no `## Running code` section, so there is no wrapper to run.
- Planner and implementer inputs carry the wrapper → NEW. Today it prints `planner 0` then `implementer 0`.
- The implementer's gate commands come wrapped → NEW. Today it prints only `end`: the input lists the bare `git diff --check main...HEAD` and `uv run --frozen pytest …` commands.
- This repo's gate suite passes under a throwaway HOME → REGRESSION. Today: `157 passed in 120.88s`.
- Variables listed in run_env reach the command → NEW. Today it prints `fresh_home=no real_home_untouched=yes cache=`: no wrapper, and `run_env` is ignored.
- run_env cannot set HOME → NEW. Today it prints `exit=0 input=written`: compose ignores `run_env` and writes the input.
- The running-code rule is in every copy and in a run's system prompt → NEW. Today all four lines end `0 0 0`.
- The preamble block and its copies stay identical → REGRESSION. Today it prints `SAME`.
- Dash-bulleted field lines keep their dependencies → NEW. Today all three sub-tickets print `"state": "ready-for-implementer", "depends_on": [], "parallel_safe": false`.
- Star-bulleted, bold, indented and plain field lines read as before → REGRESSION. Today it prints exactly the expected list.
- A sub-ticket with no Depends on line is refused → NEW. Today it prints the success JSON with `T-0001.2` at `"depends_on": []`, then `exit=0`, then `T-0001.1.yaml`, `T-0001.2.yaml`, `T-0001.yaml`.
- The planner prompt shows the parsed lines in every copy → NEW. Today each file prints `0 0 0 0 0`: the three lines are indented, and neither sentence exists.
- The planner block and its copies stay identical → REGRESSION. Today it prints `SAME`.
- The changelog records the change in order → NEW. Today it prints `0` then `CONTIGUOUS`.
- The README describes the wrapper and run_env → NEW. Today it prints `0`, `0`, `0`.
- The design doc and the instance template name run_env → NEW. Today it prints `docs/design.md:0` and `factory/instance.template.yaml:0`.
- The harness suite passes → REGRESSION.
- The change adds no whitespace errors → REGRESSION.

Out-of-scope observations:
- `agents/factory-planner.md` holds an older copy of the planner role text, whose OUTPUT block already differs from the design doc's (its Acceptance line is the earlier wording). A planner agent reads that copy and then `system-prompt.txt`, so after this change it holds two different OUTPUT blocks. `agents/**` is a protected path, and the request does not cover it.
- `build.js` line 200 parks a refused `subticket add` as `harness-bug: subticket add: …`, though after this change a refusal usually means a malformed plan, not a harness bug.
