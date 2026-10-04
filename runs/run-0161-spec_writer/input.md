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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0161-spec_writer/output.md`

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
