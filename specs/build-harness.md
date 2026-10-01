# Spec: Build the spec factory, local-Mac v0 (Nanobot fork, branch `feat/lionbot-v3`)

Ticket: (Triage, ACCEPT) "Build the spec-factory harness, smallest-thing-that-works variant"
Spec version: 3 · Round: 3 (post-gate fix pass) · Writer: spec_writer
Design doc: `/tmp/claude-0/-home-user/0cb0ba38-97f2-51cf-86de-970d4ebec94b/scratchpad/spec-factory-v3.md` (cited as "doc §<section>": doc §Harness table piece N, doc §Routing table, doc §Routing rules, doc §Human gates, doc §Shared preamble)
Supersedes: `spec-build-v2.md`. The human gate ruled: apply critic round 2's suggested fixes as written (B1, S1–S5, N2, N3); see "Responses". v2's history (v1 assumptions replaced by the ruling and addenda) is in v2.

## Problem

The design doc describes eight role prompts and a 12-piece harness. Nothing runs them end to end. The wiring rules the doc says "prompt text cannot enforce" (doc §Harness: fresh context per checker, checkers without write access, approvals bound to a commit, round limits, routing by STATUS) have no enforcer. The operator (Daniel) has a directory of messy faux-SPEC markdown files (`knowledge_vault/specs/*.md`) and no command that turns them into conformant, human-approved specs; no git ref the roles cannot write to; no merge gate; no attributable approval record.

Who it is for: the operator, running the pipeline on his Mac against the Nanobot fork; and the eight roles, which need inputs composed only from declared sources.

What is wanted (ruling + addenda): a first prototype on branch `feat/lionbot-v3` in `~/dev/nanobot-upstream` ("green"), in three parts: (1) Claude Code skills/agent definitions under `.claude/` for the eight roles, each pulling in one shared preamble file, with per-role tool restrictions; (2) a small Python package `factory/`: `tickets/` YAML store, results table, request/intake ingestion, resolve commands, and the pre-receive hook; (3) a `/factory` entry skill that runs two **Workflow-tool scripts**, `intake` (triage → spec writer ↔ critic → human gate) and `build` (planner → implementer → reviewer ‖ verifier → join → merge), where every `agent()` call is a fresh context and the join, round counters and routing are plain code in the script. Platform: local bare repo with a pre-receive hook and one deploy key per role (GitHub remote untouched); worktree per mutating run; `tickets/` YAML plus a human-edited `queue.md`; no Docker, no cron loop (both deferred).

## Evidence

Captured 2026-10-01 in the build environment (Linux; git 2.43.0; `claude` 2.1.286). The Nanobot checkouts are not present here, so repo facts come from the owner's session and are marked as such; anything I could not run is marked "not verified: <why>". Every "how it fails today" claim in Acceptance points at one of these blocks.

E1. No CLI, no package, no skills:
```
$ factory intake ./faux
/bin/bash: line 16: factory: command not found
exit=127
$ python3 -m factory
/usr/local/bin/python3: No module named factory
exit=1
$ python3 -m factory.hook
/usr/local/bin/python3: Error while finding module specification for 'factory.hook' (ModuleNotFoundError: No module named 'factory')
exit=1
$ ls .claude/skills/factory-triage/SKILL.md
ls: cannot access '.claude/skills/factory-triage/SKILL.md': No such file or directory
exit=2
$ pytest -q tests/factory
ERROR: file or directory not found: tests/factory
```

E2. No local bare repo; every git command against it fails the same way (the failure mode for every item marked ⟨bare⟩):
```
$ git ls-remote ~/factory-remote/nanobot.git
fatal: '/root/factory-remote/nanobot.git' does not appear to be a git repository
fatal: Could not read from remote repository.
exit=128
```

E3. Worktree behaviour on git 2.43:
```
$ git worktree add ../wt ticket/T-0001                   # branch absent
fatal: invalid reference: ticket/T-0001                   exit=128
$ git worktree add -q -b ticket/T-0001 ../wt-T-0001 master ; echo exit=$?
exit=0
$ git worktree add ../wt2 ticket/T-0001                   # same branch twice
fatal: 'ticket/T-0001' is already used by worktree at '.../wt-T-0001'   exit=128
$ env -i PATH=/usr/bin:/bin HOME=/nonexistent git -C ../wt-T-0001 status -s ; echo exit=$?
exit=0
$ env -i PATH=/usr/bin:/bin sh -c 'echo ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-unset}'
ANTHROPIC_API_KEY=unset
```

E4. Pre-receive hook on a local bare repo: it runs and refuses; with the **local file transport** it inherits the pusher's environment, and a direct ref write runs no hook at all (both matter for identity, Risk R1):
```
$ FACTORY_IDENTITY=implementer git push ../remote.git HEAD:main
remote: refs/heads/main: identity implementer may not push
 ! [remote rejected] HEAD -> main (pre-receive hook declined)
error: failed to push some refs to '../remote.git'
exit=1
$ FACTORY_RUN_TOKEN=forged git -c push.negotiate=false push ../remote.git HEAD:main 2>&1 | grep remote:
remote: FACTORY_RUN_TOKEN=forged
$ git -C ../remote.git update-ref refs/heads/main refs/heads/main~1 && echo "bypassed hook, exit=$?"
bypassed hook, exit=0
```
Not verified: the ssh transport with per-key forced commands (no sshd in this environment). Also observed on git 2.43 with the local transport: `fatal: expected 'acknowledgments', received 'packfile' / warning: push negotiation failed; proceeding anyway` — harmless, silenced by `push.negotiate=false`.

E5. `git revert` equals the inverse diff byte for byte; an extra hunk breaks the equality (basis for the piece-7 revert check):
```
$ git revert --no-edit $H ; R=$(git rev-parse HEAD)
$ git diff $R^ $R > rev.patch ; git diff $H $H^ > inv.patch ; cmp rev.patch inv.patch ; echo cmp exit=$?
cmp exit=0
$ echo b > g.txt && git add g.txt && git commit -qm extra && git diff $R^ HEAD > rev2.patch && cmp rev2.patch inv.patch
cmp: EOF on inv.patch after byte 118, line 7
cmp exit=1
```

E6. `claude` CLI flags that exist (for the `claude -p` items and the stub seam):
```
$ claude -p --help | grep -E "max-budget-usd|--model|permission-mode|--tools|allowedTools|--restricted|system-prompt"
  --max-budget-usd <amount>   --model <model>   --system-prompt <prompt>   --system-prompt-file <file>
  --agent <agent>             --permission-mode <mode>    (choices: "acceptEdits", "auto", "bypassPermissions", "manual", "dontAsk", "plan")
  --tools <tools...>          Specify the list of available tools from the built-in set ... (e.g. "Bash,Edit,Read")
  --allowedTools <tools...>   Comma or space-separated list of tool names to allow (e.g. "Bash(git *) Edit")
  --restricted                Restricted mode: removes the built-in tools that run commands or code ... unless --tools names
                              them ... Also confines the file tools to the working directories ..., refuses bypassPermissions ...
$ claude -p --help | grep -E "max-turns"      # (no output: does not exist)
```
Corrected in round 3 (critic N3): `--system-prompt-file` and `--agent` do exist on 2.1.286 (v2 said neither did), so item 56's primary `--agent` form is usable. `--tools Bash,Read` removes `Skill` and `Workflow` from the built-in set; the ⟨wf⟩ driver uses `--tools default` (critic B1).

E7. Workflow-tool script API (from the `workflow-authoring` reference loaded in this session; the dispatcher is built on exactly these): `agent(prompt, {agentType, schema, isolation: 'worktree', model, effort, phase, label})` returns the subagent's text, or the schema-validated object, or `null` when the subagent dies on a terminal API error; `parallel([...thunks])` is a barrier that never rejects (errored thunks become `null`); `pipeline()` has no barrier; `args` is passed verbatim; scripts are plain JS with **no filesystem or Node API access** and no `Date.now()`; each invocation persists its script and returns a `runId`; the concurrency cap is min(16, CPUs−2). Consequences: every store read and write inside a workflow goes through a clerk agent that runs `factory …` commands; timestamps and the run id come from the clerk, not the script; there is no per-agent wall-clock or token cap in the API, so piece 3's budget kill is realised as "agent returned null or an invalid object" plus the clerk-recorded start time (see I.5 and Open question 4). The reference's one manual kill path: the user skips a hung agent in the session UI, `agent()` then returns `null`; until then a hung thunk blocks `parallel()` (doc §Harness table piece 2, "a hung agent blocks the join until a human skips it").

E8. Toolchain present here: `ruff`, `mypy`, `pytest` under `/root/.local/bin`, `pyyaml 6.0.1`. Not verified: `launchctl` (absent here; macOS only), GNU `timeout` on the Mac.

E9. Repo facts from the owner's session (not re-verified here): fork of HKUDS/nanobot; checkouts `~/dev/nanobot` on `feat/lionbot-next` ("blue") and `~/dev/nanobot-upstream` on `feat/lionbot-v3` ("green", where the factory is built); faux-SPEC input `knowledge_vault/specs/*.md`; sanitized spec output `knowledge_vault/sanitized_specs/` (until `specs/` is renamed `tickets/`); uncommitted scripts `scripts/spec_evidence.py`, `scripts/unit_start.sh`, `scripts/spec_lint.py` and `port_state.json` that may fold into or be superseded by the factory; `knowledge_vault/ProjectNotes/SPEC_MAINTENANCE_WORKFLOW.md` frozen until cutover; a dirty `webui/package-lock.json` in the green worktree that must not be disturbed. **Measured baseline the factory must beat** (reported under Risk, not an acceptance item): docs/product churn ratio under 2x; at most one fix commit per unit.

## Root cause

Not applicable (nothing exists). Every piece in doc §Harness table is unbuilt.

## Ruling and remaining defaults

Rows marked "ruling" are decided; rows marked "default" are mine and repeat under Open questions.

| # | Decision | Value | Source |
|---|---|---|---|
| R1 | Target and shape | `~/dev/nanobot-upstream`, branch `feat/lionbot-v3`; skills/agent definitions under `.claude/` + `factory/` package + `/factory` entry skill | ruling + addendum 2 |
| R2 | Git server | Bare repo `~/factory-remote/nanobot.git`, pre-receive hook, one deploy key per role; GitHub remote untouched | ruling + addendum 1 |
| R3 | **Dispatcher** | Claude Code **Workflow tool**: `factory/workflows/intake.js` and `factory/workflows/build.js`; fresh context per `agent()`; join, round counters and routing are plain code in the script. The cron/`factory loop` dispatcher of v1 is **deferred to a later ticket** | addendum 1 |
| R4 | Isolated run | Implementer and retro: `agent(..., {isolation: 'worktree'})` on `~/factory/clone`; checkers: fresh context, read + shell, checkout of the head made by the clerk in `~/factory/runs/<run_id>/wt`; Docker deferred | ruling + E7 |
| R5 | Tracker / human surface | `tickets/` YAML + `queue.md` on branch `factory/state` of the bare repo, checked out at `~/factory/state`; approved specs also exported to `knowledge_vault/sanitized_specs/<ID>.md` | ruling + addendum 2 (location: default) |
| R6 | Permissions | Never `bypassPermissions` (nor `dontAsk`). Role agent definitions carry `tools:` allowlists: checkers and read-only authors Read/Grep/Glob/Bash, no Edit/Write; implementer and retro add Edit/Write; clerk Bash only, allowed `Bash(factory *)`, `Bash(git *)`. Real runs: the operator's session runs `/factory` with `--permission-mode acceptEdits` and `--allowedTools "Bash(factory *)" "Bash(git *)" "Bash(pytest *)" "Bash(ruff *)" "Bash(mypy *)" Read Grep Glob Edit Write Skill Workflow`; anything outside that list prompts the operator (the session is attended in v0). See Risk R6 | ruling; mode/allowlist: default (critic S3) |
| R7 | Faux-SPEC input / sanitized output | `knowledge_vault/specs/*.md` → `knowledge_vault/sanitized_specs/` | addendum 2 |
| D1 | Trunk | The bare repo's `main`, seeded once from `feat/lionbot-v3` by `factory init` | default |
| D2 | Language, deps, gates | Python 3.11+, `pyyaml`; factory gates `ruff check factory tests/factory && mypy factory && pytest -q tests/factory`; repo `{gate commands}` default `pytest -q` | default; Nanobot's own commands unknown |
| D3 | Budgets | `--max-budget-usd 10` is not available per `agent()` (E7); v0 budget = the Workflow turn budget plus a 30-min wall-clock recorded by the clerk and judged by the script on completion | default |
| D4 | `{2}`,`{5}`,`{3}`,`{400}` | 2, 5, 3, 400 | default |
| D5 | Identities | Humans: `daniel`. Roles with keys: `harness`, `implementer`, `retro`; `reviewer`, `verifier` and the five read-only authors have **no key**. Identity = the ssh key's forced command (part E) | addendum 1; mechanism: default, see Risk R1 |
| D6 | Models | All roles inherit the session model (`agent()` without `model`); `factory/config.yaml` `models:` map for later | default |
| D7 | Existing scripts | `scripts/spec_lint.py` is superseded by the critic; `scripts/spec_evidence.py` and `scripts/unit_start.sh` are left untouched and listed under Out of scope for a follow-up ticket; `port_state.json` untouched | default |
| D8 | `{repo name}` and protected paths | `nanobot`; protected: `infra`, `dependencies`, `credentials`, `public API` (globs in F) | default |

## Proposed change

All paths relative to `~/dev/nanobot-upstream` on `feat/lionbot-v3` unless prefixed `~/`.

```
.claude/skills/factory/SKILL.md               /factory entry skill (A)
.claude/agents/factory-<role>.md              eight role agent definitions; frontmatter `tools:` per R6; body =
                                              "Read factory/prompts/preamble.md before anything else" + the role prompt (A)
.claude/agents/factory-clerk.md               store clerk: Bash(factory *), Bash(git *) only (A, H)
.claude/agents/factory-stub.md                test fixture: Read only; returns a named file verbatim (H)
factory/prompts/preamble.md                   doc §Shared preamble, placeholders filled (A)
factory/workflows/intake.js build.js          the two dispatcher scripts (H)
factory/__init__.py cli.py store.py log.py results.py status.py compose.py gate.py hook.py queue.py export.py
factory/paths.yaml identities.yaml config.yaml    config.yaml also holds `max_rounds: {spec: 2, pr: 2}` and the routing-table edges (S1 guards)
factory/hooks/pre-receive                     shim: exec "$FACTORY_HOOK_PYTHON" -m factory.hook (F)
tests/factory/                                new test files only; fixtures/stubs/<case>/*.md
pyproject.toml                                adds the `factory` console script and dev deps (A)
AGENTS.md                                     adds a "Factory" section (A)
```

State on branch `factory/state` of the bare repo (never merged into `main`), checked out at `~/factory/state`: `tickets/`, `specs/`, `requests/`, `results/`, `approvals/`, `log/`, `runs/`, `audits/`, `retros/`, `queue.md`. Keys in `~/factory-remote/keys/` (part E).

### A. Skeleton, agent definitions, entry skill

- `pyproject.toml`: console script `factory = factory.cli:main`; dependency `pyyaml`; dev `pytest`, `ruff`, `mypy`.
- `factory/cli.py`: subcommands per part; exit 0 success, 2 refused precondition, 1 error; one audit event (C) per state change.
- `factory render`: writes `factory/prompts/preamble.md` and the eight `.claude/agents/factory-<role>.md` bodies from the doc text with `{repo name}`, protected paths, `{2}`, `{400}`, `{gate commands}`, `{3}`, `{5}` filled from `config.yaml`, plus **one added rule in the Triage and Spec-writer definitions** (addendum 2): "Acceptance items describe behaviour (a command a user or operator could run, or Given/When/Then) and never name a test function, class, or internal symbol; symbols belong under Root cause and Proposed change." The doc text itself is copied verbatim and otherwise never edited by this ticket.
- `.claude/skills/factory/SKILL.md`: how to run `factory intake`, then `Workflow({scriptPath: 'factory/workflows/intake.js', args: {ticket: ID, stubs?: dir}})`, approve at the gate, then `Workflow({scriptPath: 'factory/workflows/build.js', args: {ticket: ID}})`; the human commands (`queue`, `approve-*`, `request-changes`, `resolve`, `merge`, `audit-sample`, `retro`). Not verified: whether the Workflow registry can address these as named workflows; `scriptPath` is what the reference documents, so that is what the skill uses.
- `factory init`: creates `~/factory-remote/nanobot.git` (bare), seeds `main` from `feat/lionbot-v3`, creates `factory/state` and its checkout, mints keys (E), installs the hook (`factory install-hook`: copies the installed package to `~/factory-remote/hook-env/`, writes the shim with an absolute `FACTORY_HOOK_PYTHON`, so a pushed edit to `factory/hook.py` changes nothing until a human reinstalls). It never touches `knowledge_vault/ProjectNotes/SPEC_MAINTENANCE_WORKFLOW.md`, `webui/package-lock.json`, `port_state.json`, or `scripts/` (E9).
- `AGENTS.md`: the layout, the gates, and that `.claude/agents/factory-*`, `.claude/skills/factory*` and `factory/prompts/**` are guardrail paths.

### B. Ticket store (piece 1), requests, change proposal (piece 5)

`tickets/<ID>.yaml`, IDs `T-0001`, sub-tickets `T-0001.1`, retro `R-<date>`, revert `V-0001`. Schema (every key present, `null` when unset):

```yaml
id: T-0001
type: feature            # bug|feature|chore|question|retro|revert
title: ...
request: requests/T-0001.md   # raw request; source path recorded in requests/index.yaml
parent: null
depends_on: []
parallel_safe: true      # from the planner's "Parallel-safe:" line
status: ready-for-triage
round: {spec: 0, pr: 0}
spec: {version: 0, approved_version: null, tests_to_change: [], protected_paths: []}
branch: null             # ticket/<ID>, retro/<date>, revert/<ID>
base: main
head: null
reverted_head: null      # revert tickets only: head of a `merged` ticket
in_flight: []            # run ids; one per role in flight on this branch
parked: null             # {reason, since, outputs: [run ids], question: path|null}
history: []
```

Spec text `specs/<ID>/v<N>.md`; sub-ticket text `specs/<ID>/subticket.md`.

States: `ready-for-triage`, `waiting-requester`, `ready-for-spec-writer`, `ready-for-critic`, `ready-for-spec-gate`, `ready-for-planner`, `waiting-dependencies`, `ready-for-implementer`, `checks-in-flight`, `ready-for-checks` (after a checker `--redispatch`; only the roles without a row on the current head run), `ready-for-merge`, `merged`, `parked`, `closed`, `running`.

CLI (store side; every command the workflows' clerk uses is here, so every item is black-box):
- `factory request new --file F`: copies F to `requests/<ID>.md`, records the source path, creates the ticket in `ready-for-triage`, prints the ID. **The only entry path for request-born tickets.**
- `factory intake [<dir>]` (default `knowledge_vault/specs`): `request new` for every `*.md` not yet imported (content hash in `requests/index.yaml`); prints `imported N, skipped M (already imported)` and the IDs. It does not run anything; the `/factory` skill then launches `intake.js` per ID.
- `factory ticket new --type (retro|revert) --branch B [--reverts SHA]` (harness or human): no-sub-ticket PR record (piece 5); `--reverts` required for `revert`, refused unless SHA is a `merged` ticket's `head`. Other types → exit 2 `use factory request new`.
- `factory ticket show ID`; `factory ticket set ID key=value` (logged); `factory ticket transition ID --to STATE --by RUN [--round spec|pr:+1|reset|init]` (the clerk's one write for routing; `init` sets the counter to 1 if 0). **Guards (doc §Harness table piece 2: "put the round and routing guards in the CLI, not the clerk"):** exit 2, store unchanged, nothing logged, when `+1` would take the counter above `config.yaml` `max_rounds` (`round.spec 2 is at max_rounds 2`), or when `(current status, STATE)` is not an edge of the routing table stored in `config.yaml` `routing:` (the doc §Routing table rows plus the resolution rules; `no route ready-for-triage → merged`). `factory ticket park ID --reason R --outputs RUN,RUN [--question PATH]`.
- `factory run start --role R --ticket ID|none --head SHA|none` → prints `run_id`, writes `runs/<run_id>/{meta.yaml,system-prompt.txt}`, appends the id to `in_flight`. **Guards:** exit 2, nothing written, when the ticket is not in R's ready state (`T-0001 is ready-for-triage, not ready-for-critic`; ready states: triage `ready-for-triage`, spec_writer `ready-for-spec-writer`, critic `ready-for-critic`, planner `ready-for-planner`, implementer `ready-for-implementer`, reviewer/verifier `checks-in-flight` or `ready-for-checks`; retro runs with `--ticket none`), or when the ticket's branch already has a run in `in_flight` (implementer, retro: any run; reviewer, verifier: a run of the same role) — `ticket/T-0001 already has run <id> in flight`.
- `factory run compose RUN` (**the one input mechanism**, critic S2) → writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares for `(role, round, resolution)` — the "with input =" lists in H, read from the store and `~/factory/clone` — and records their paths as `input_sources:` in `meta.yaml`. The text `agent()` receives is only `Your entire input is ~/factory/state/runs/<run_id>/input.md; read it first.` No input text is composed anywhere else.
- `factory run finish RUN --output-file F [--status-override KILLED]` → writes `output.md`, parses STATUS (H), removes the id from `in_flight`, prints `STATUS CONFIDENCE ESCALATIONS` as JSON, logs `escalation.queued` when the list is not `none`.
- `factory spec add ID --file F` → `spec.version += 1`, `specs/ID/v<N>.md`; `factory subticket add PARENT --file F --depends-on IDS --parallel-safe yes|no` → sub-ticket in `ready-for-implementer` or `waiting-dependencies`.

### C. Audit log and run artifacts (piece 10)

`log/<YYYY-MM>.jsonl` and `runs/<run_id>/{meta.yaml,input.md,system-prompt.txt,output.md}` on `factory/state`. Events: `request.created`, `ticket.created`, `ticket.transition`, `run.started`, `run.finished`, `run.killed`, `result.recorded`, `result.stale-discarded`, `approval.recorded`, `merge.refused`, `merge.done`, `escalation.queued`, `reply.sent`, `human.resolved`, `harness-bug`, `spec.exported`. `meta.yaml`: role, ticket, head, started, finished, wall_s, status, workflow_run_id. Append-only enforced by the hook (F.3). `factory log tail [-n N] [--ticket ID] [--event E]`.

### D. Commit-bound results table (piece 6)

`results/<head_sha>/<role>.yaml`, roles `reviewer`, `verifier`, `ci`; statuses `APPROVE REQUEST-CHANGES ESCALATE VERIFIED FAILED SPEC-DEFECT PASS FAIL KILLED`. Stale rule: a row whose head is not the ticket's current `head` is written under its own SHA, logged `result.stale-discarded`, never consulted.
- `factory results show ID` → rows for the current head plus `missing: <roles> for <head>`.
- `factory results record ID --head SHA --role R --output FILE [--killed]` (harness identity only): row from FILE's STATUS line; for `--role verifier` also the `ci` row from the `Gate suite:` line (L); `--killed` writes `KILLED`.

### E. Identities and scoped credentials (pieces 4, 12)

`factory/identities.yaml` (read by the hook from server-side `main`, F):

```yaml
roles:
  harness:     {may_push: [refs/heads/main, refs/heads/factory/state]}
  implementer: {may_push: [refs/heads/ticket/*]}
  retro:       {may_push: [refs/heads/retro/*]}
  reviewer: {may_push: []}   verifier: {may_push: []}   triage: {may_push: []}
  spec_writer: {may_push: []} critic: {may_push: []}    planner: {may_push: []}
humans: [daniel]
```

One deploy key per identity that may push (`harness`, `implementer`, `retro`, `daniel`) in `~/factory-remote/keys/<identity>` (mode 600), minted by `factory init`; the bare repo is addressed as `ssh://localhost/~/factory-remote/nanobot.git`, and each public key's `~/.ssh/authorized_keys` line is `command="FACTORY_IDENTITY=<identity> git-shell -c \"$SSH_ORIGINAL_COMMAND\"",no-port-forwarding,no-pty,...`, so the hook receives the identity from the forced command, not from the pusher. Checkers and the five read-only roles get **no key**; their reads use the local path `~/factory/clone`. The clerk uses the `harness` key; a human runs `factory approve-*`/`resolve` with `FACTORY_KEY=daniel` (the CLI sets `GIT_SSH_COMMAND` accordingly). Not verified: macOS Remote Login and forced commands (no sshd here); the local file transport is the captured fallback (E4) and is strictly weaker. **Limit (Risk R1):** everything runs as one Unix user, so a same-user process can read any key or bypass the hook with `update-ref` (E4). In v0 this is a fence against a confused agent, not an adversarial one; the per-role tool allowlists (R6) are the second fence; Docker is deferred.

### F. Pre-receive hook: permissions, merge gate, guardrail and protected paths (pieces 4, 7, 8)

Runtime: `factory/hooks/pre-receive` is a `#!/bin/sh` shim installed into `~/factory-remote/nanobot.git/hooks/` by `factory install-hook`; it `exec`s the hook-env python with `-m factory.hook`, cwd = the bare repo. The hook reads **only server-side state**: `factory/identities.yaml` and `factory/paths.yaml` via `git cat-file -p refs/heads/main:<path>` as stored **before** the push; `tickets/`, `results/`, `approvals/` via `refs/heads/factory/state` as stored before the push. Nothing is read from the pushed objects except the diff being judged. For each `old new ref` on stdin, identity `P` = `$FACTORY_IDENTITY` (unset → `anonymous`):

1. **Identity.** Human: `refs/heads/factory/state`, `refs/heads/ticket/*`, `refs/heads/retro/*`, `refs/heads/revert/*`; refused on `main` (`refs/heads/main: identity daniel may not push`). Role: only its `may_push`, else `refs/heads/X: identity P may not push`. `anonymous`: all refused.
2. **`refs/heads/ticket/<ID>`** by `implementer`: refused unless `tickets/<ID>.yaml` `in_flight` names a run with role `implementer` (`ticket/<ID>: no implementer run in flight`). Deletion and non-fast-forward refused.
3. **`refs/heads/factory/state`**: `approvals/**` added or changed → `P` human (`approval rows need a human pusher`); `log/*.jsonl` append-only and `runs/**` existing files unchanged (`<path> is append-only`); `results/**` → only `harness` (`results/ may only be written by harness`).
4. **`refs/heads/main`** (merge gate). Only `harness`; fast-forward only. `H = new`; ticket with `head == H`. Normal conditions, first failure named:
   - `results/H/{ci,reviewer,verifier}.yaml` = `PASS`,`APPROVE`,`VERIFIED` (`missing: ci, reviewer, verifier for H`);
   - `git merge-base --is-ancestor old H` (`head H does not contain main <old>`);
   - piece 8, per path in `git diff --name-only old H`: protected glob or **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`protected path <p> needs human approval on H` / `guardrail path <p> needs human approval on H`); existing test file (test glob, present in `old`) modified or deleted → in `spec.tests_to_change` of the pinned version (`existing test <p> modified; not in Tests to change of pinned spec v<N>`); new test file → nothing.
   - **Exception (doc §Harness table piece 7; the only one), two branches:**
     - *retro*: `type: retro`, `parent: null`, every changed path matches a non-test guardrail glob (the doc's list: CI config, AGENTS.md, skills, prompts — `factory/hooks/**`, `paths.yaml`, `identities.yaml`, `factory/workflows/**` are protected, S5) → conditions become `ci PASS` + head contains main + `approvals/<ID>/guardrail-H.yaml` (human-pushed).
     - *revert*: `type: revert`, `parent: null`, `reverted_head: X` the `head` of a `merged` ticket, and `git diff old H` equals `git diff X X^` byte for byte (E5) → the same three conditions; for piece 8, test files present in `X` but absent in `X^` (files the reverted PR added) are exempt.
     - Any other diff: `exception withdrawn: <reason>` (`<p> is not a guardrail path`, `diff is not the inverse of <X>`, `<X> is not a merged head`) and the normal conditions apply.
5. Refusal → reason on stderr, exit 1; every decision appended to `~/factory-remote/hook.log`; `factory log import-hook` copies new lines in as `merge.refused` events (the clerk runs it each workflow phase).

`factory/paths.yaml`:

```yaml
guardrail:
  tests:     ["tests/**", "**/test_*.py", "**/*_test.py"]
  non_tests: [".github/**", "AGENTS.md", ".claude/skills/**", ".claude/agents/**", "factory/prompts/**"]
protected:
  infra:        ["factory/hooks/**", "factory/workflows/**", "factory/paths.yaml", "factory/config.yaml"]
  dependencies: ["pyproject.toml", "requirements*.txt", "uv.lock", "poetry.lock", "webui/package-lock.json"]
  credentials:  ["factory/identities.yaml"]
  public_api:   ["nanobot/api/**"]     # not verified against the repo; D8
```

### G. Merge client (piece 7, harness side)

`factory merge ID`: runs the rule-4 checks from the shared `factory/gate.py` (the hook imports the same module), prints the first failing condition, exit 2, no push; else pushes `head` to `main` as `harness` (fast-forward). Success → `merged`, `merge.done`; every ticket whose `depends_on` are all `merged`: `waiting-dependencies` → `ready-for-implementer`; parent → `closed` when all sub-tickets merged. Hook stays authoritative. Head-does-not-contain-main → `ready-for-implementer`, `round.pr` unchanged, findings `Head H does not contain main M; merge main into ticket/<ID> and push`.

### H. Dispatcher: the two workflow scripts (piece 2, harness-owned logic)

Both scripts are plain JS per E7; they hold the routing, the join and the round counters as code and nothing else decides them. Neither reads a file: every read and write of the store is an `agent()` call on `factory-clerk` (`effort: 'low'`) whose prompt is a fixed `factory …` command line and whose schema is the command's JSON output. The STATUS of a role is whatever `factory run finish` parsed (not the role's structured output), so the parser rules exist once.

**STATUS parser** (`factory/status.py`, used by `run finish` and `results record`): the **last** line matching `^STATUS:\s*(\S+)`; the next non-blank line must match `^CONFIDENCE:`; the next `^ESCALATIONS:`; everything after that to EOF (plus the remainder of the `ESCALATIONS:` line) is the list, `none` iff exactly `none`. Any other shape → parse failure → unknown STATUS.

Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run start …` (prints `run_id`; exit 2 from a guard → park `harness-bug: <stderr>` and return); clerk `factory run compose RUN_ID` (writes `input.md`, I.2); `const out = await agent('Your entire input is ~/factory/state/runs/' + runId + '/input.md; read it first.', {agentType: args.stubs ? 'factory-stub' : 'factory-' + role, label: role + ' ' + ticket, isolation: role in {implementer, retro} ? 'worktree' : undefined})`; **KILLED condition** `out === null || out.trim() === ''` (I.5) → clerk `factory run finish RUN --status-override KILLED`; else clerk `factory run finish RUN --output-file -` with `out`. The clerk returns `{run_id, status, escalations}`. The stub agent definition reads `args.stubs/<role>-<n>.md` (n = how many times that role has run in this workflow, counted in the script) and returns it verbatim, or **returns an empty string when the file is absent** (the KILLED seam): the only test seam. The CLI guards (B) are authoritative over the script's `round < MAX` checks: a `transition` the routing table or `max_rounds` forbids exits 2 with the store unchanged, and the script treats that as `park --reason 'harness-bug: <stderr>'`.

`intake.js` (`args: {ticket, stubs?}`):
1. `phase('Triage')`: `runRole('triage', …)`; `ACCEPT` → clerk `transition --to ready-for-spec-writer` (title/type from the output); `REJECT` → `closed`; `NEEDS-HUMAN` → `park --question`; `CLARIFY` → `transition --to waiting-requester` + clerk `factory reply ID --file -` (piece 9: writes `<source dir>/<file>.reply.md` next to the request, appends to `queue.md`, event `reply.sent`); then **return**. Unknown STATUS → `park --reason 'harness-bug: unknown STATUS <s>'` + `harness-bug` event; always return.
2. `phase('Spec')`: loop `while (true)`: `runRole('spec_writer')` with input = ticket + request (+ on round ≥ 2: critic findings, previous spec); `NEEDS-HUMAN` → park, return; `READY-FOR-CRITIC`/`NEEDS-SPLIT` → clerk `spec add`; then clerk `transition --to ready-for-critic --round spec:init` (**sets `round.spec` to 1 if 0**, doc §Routing rules "the first check is round 1"); `runRole('critic')` with input = spec vN (+ round ≥ 2: prior findings, the writer's `## Responses`, spec vN−1); `APPROVE` → `transition --to ready-for-spec-gate` + clerk `factory queue` (regenerates `queue.md`, "Spec gate" section), return; `ESCALATE` → park, return; `REVISE` → `if (round < MAX) { transition --to ready-for-spec-writer --round spec:+1; continue } else { park --reason 'max-round cutoff'; return }`. `MAX` = 2 is read from `config.yaml` by the clerk at the start.
3. A non-`none` escalations list never changes the route; `run finish` already logged it.

`build.js` (`args: {ticket}`), run after `factory approve-spec`:
1. `phase('Plan')`: `runRole('planner')` with the pinned spec; `PLANNED` → clerk `subticket add` per sub-ticket (`depends_on`, `parallel_safe`); `ESCALATE` → park, return.
2. `phase('Build')`: `while` any sub-ticket is not `merged|parked|closed`: `ready = ` clerk `factory ticket ready-implementers PARENT` (JSON: sub-tickets in `ready-for-implementer` whose deps are merged, minus any whose `parallel_safe: false` while a sibling implementer is in flight, minus any with an implementer in flight on its branch); `await parallel(ready.map(st => () => buildOne(st)))`; if `ready` is empty and nothing is in flight, return (the rest is parked or waiting on a human).
3. `buildOne(st)`: loop:
   - `runRole('implementer', st, …, {isolation: 'worktree'})`; the implementer's worktree is created on current `main` at dispatch (doc §Routing table, Planner row), input = sub-ticket, pinned parent spec, AGENTS.md (+ round ≥ 2: both checker outputs, CI result, or the human ruling); `BLOCKED` → park, return; `READY-FOR-REVIEW` → clerk `factory ticket head ST` (from `git ls-remote`), `transition --to checks-in-flight --round pr:init`.
   - **Checkers in parallel, fresh contexts** (`parallel` is the join barrier, E7): `[rev, ver] = await parallel([() => runRole('reviewer', …), () => runRole('verifier', …)])` with input = `git diff main...head`, PR description, sub-ticket, parent spec (+ round ≥ 2: both prior outputs, the implementer's Responses); the clerk makes each a fresh checkout `~/factory/runs/<run_id>/wt` of the head; each result → clerk `results record` (stale rule applies; the `Commit:` line must equal the current head).
   - **Join** (plain code): any `KILLED` → `park --reason 'budget kill: <role>'`, round unchanged, return (S6); else any `ESCALATE`/`SPEC-DEFECT` → park with both outputs, return; else all `APPROVE`/`VERIFIED`/`PASS` → clerk `factory merge ST` → `merged` (then the clerk's `ready-implementers` picks up dependants) or `head does not contain main` → continue the loop with round unchanged; else `round.pr < MAX` → `transition --to ready-for-implementer --round pr:+1`, continue; else `park --reason 'max-round cutoff'`, return.
4. `phase('Retro')` is not in `build.js`; `factory/workflows/retro.js` (one `runRole('retro')` with the input of M) runs on demand or weekly from the `/factory` skill.

Resumption after a human decision: the `/factory` skill re-runs `build.js` for the parent; the clerk's `ready-implementers` returns the sub-ticket the human moved to `ready-for-implementer` (`resolve --ruling`, `--redispatch`), and `buildOne` starts from the state the store holds (round from the store; for `--redispatch` after a checker kill, only the missing checker runs: `ready-checkers ST` lists roles without a row on the current head).

### I. Isolated run per role (piece 3) — worktree v0

1. System prompt = the agent definition (`factory/prompts/preamble.md` is read by its first instruction); the clerk records it in `runs/<run_id>/system-prompt.txt`.
2. Input composed by `factory run compose RUN` (B) from exactly the declared sources (H), written as `runs/<run_id>/input.md` with `input_sources:` in `meta.yaml` **before** the role runs; the role's prompt is a pointer to that file, so what the role saw is auditable and no second composition path exists.
3. Mutating roles get `isolation: 'worktree'` (E7), which the Workflow tool creates and removes; the implementer's `git push` uses the implementer key via `GIT_SSH_COMMAND` set in its agent definition's `env:` (not verified: whether agent-definition frontmatter supports `env:`; fallback: a `factory git-push ticket/<ID>` wrapper the implementer is allowed to run, which supplies the key). Checkers run read+shell in a checkout the clerk made; they have no key, so a push fails at authentication.
4. Tool restriction is the agent definition's `tools:` (R6); no `bypassPermissions` anywhere; `--restricted` applies to `claude -p` test drivers (E6).
5. Budget (piece 3): the KILLED condition is `out === null || out.trim() === ''` (`agent()` returned `null` on a terminal error or after the user skipped the agent, or returned nothing) → `run finish --status-override KILLED` → `KILLED` results row, `parked` (`budget kill: <role>`), round unchanged. The one manual kill path the Workflow reference provides: the user skips the agent in the session, `agent()` returns `null`, KILLED. Until then a hung agent blocks `parallel()` and every sibling in that join; the doc's "recorded … so no join waits on it" is post-hoc in v0, not pre-emptive. Wall-clock: the clerk stamps `started`/`finished` in `meta.yaml`; `run finish` sets `status: KILLED` when `wall_s > time_budget_s` even if output arrived. There is no pre-emptive kill in v0 (E7; Open question 4).
6. After each run: `meta.yaml` complete, the checker worktree removed by the clerk (`factory run cleanup RUN`).

### J. Secrets (piece 12)

No API key in any run: the CLI authenticates from the owner's login. Keys only in `~/factory-remote/keys/`. Redaction: before writing `runs/<run_id>/*` or a log line, every private-key body and every value of an env var matching `*KEY*|*TOKEN*|*SECRET*` in the harness's own env is replaced by `[REDACTED]`.

### K. Human surface and approval records (piece 9)

- `queue.md` regenerated by `factory queue`: sections "Parked" (reason, question or output paths, oldest first), "Spec gate", "Protected PRs", "Guardrail gate", "Waiting on requester"; each entry ends with a `Decision:` line (`approve`, `approve --edit FILE`, `changes FILE`, `answer FILE`, `ruling FILE`, `redispatch`, `close`, `to-spec-gate`). `factory queue apply` turns filled lines into the commands below, run as the human identity, and clears them. A note without `Decision:` records nothing.
- `factory approve-spec ID [--version N] [--edit FILE]`: pins `approved_version` (edited text saved as a new version first), copies "Tests to change" and Risk paths into the ticket, `approvals/ID/spec-v<N>.yaml`, → `ready-for-planner`, and **exports** the pinned text to `knowledge_vault/sanitized_specs/<ID>.md` (`factory export ID`; event `spec.exported`; the export directory is a config key for the later `specs/` → `tickets/` rename).
- `factory request-changes ID --notes FILE`: `round.spec: 0`, → `ready-for-spec-writer`.
- `factory approve-pr ID --head SHA` → `approvals/ID/pr-SHA.yaml`; `factory approve-guardrail ID --head SHA` → `approvals/ID/guardrail-SHA.yaml`.
- `factory resolve ID (--answer FILE | --ruling FILE --to implementer [--amend-subticket FILE] [--amend-spec FILE] | --redispatch | --close | --to spec-gate)` (doc §Routing rules, resolution list): `--answer` on `waiting-requester` or a triage/spec-writer `NEEDS-HUMAN` → appended to `requests/<ID>.md` under `## Answer <n>`, ticket back to the asking role's ready state; `--ruling` → `round.pr: 0`, ruling becomes findings input, `ready-for-implementer`; `--amend-subticket` replaces `specs/<ID>/subticket.md`; `--amend-spec` writes `specs/<parent>/v<N+1>.md`, re-pins `approved_version`, writes `approvals/<parent>/spec-v<N+1>.yaml`, re-exports; `--redispatch` → the killed role's ready state, round unchanged; `--to spec-gate`; `--close`. Each writes `approvals/ID/resolve-<n>.yaml`, event `human.resolved`.

### L. Verifier as gate runner (piece 11)

No separate CI. `results record --role verifier` writes `results/<head>/ci.yaml` from the `Gate suite: PASS|FAIL` line; missing → `FAIL`, `detail: missing Gate suite line`.

### M. Audit sample and retro entry

`factory audit-sample [--since 7d] [--n 5]` → `audits/<date>.yaml`. `factory retro-input [--since <last>]` composes the retro input per doc §Routing table (Retro row) to stdout; `retro.js` feeds it to `runRole('retro')` (retro key); `PROPOSED` → clerk `factory ticket new --type retro --branch retro/<date>`, queue.md "Guardrail gate"; `NO-CHANGES` → `run.finished` only.

### Size and seams (NEEDS-SPLIT)

Estimate 1,800–2,600 changed lines. Seams, in dependency order:

1. **S1 Store, requests, log, results, parser** (A skeleton, B, C, D, status.py): local-only.
2. **S2 Bare repo, keys, hook, merge client** (E, F, G, `factory init`): depends on S1.
3. **S3 Agent definitions, workflows, clerk, stub, verifier-as-CI** (A render, H, I, L): depends on S1, S2.
4. **S4 Human surface + export** (K): depends on S1, S2; parallel-safe with S3 except `factory/cli.py` (not parallel).
5. **S5 Audit + retro** (M, `retro.js`): depends on S3, S4.

## Acceptance

All items NEW. Failure today by marker: unmarked = `factory …` commands → E1 (`factory: command not found`, exit 127); ⟨bare⟩ needs `~/factory-remote/nanobot.git`, today E2 (exit 128); ⟨wf⟩ runs a workflow through the CLI with the **stub agent**: `claude -p --restricted --tools default --allowedTools "Bash(factory *)" "Bash(git *)" Read Skill Workflow "/factory run intake T-0001 --stubs tests/factory/fixtures/stubs/<case>"` (the skill calls `Workflow({scriptPath, args: {ticket, stubs}})`; `--tools default` keeps `Skill` and `Workflow`, which `--tools Bash,Read` excluded; the allowlist covers the clerk's `Bash(factory *)` and `Bash(git *)`, the stub's `Read` and the implementer stub's `PUSH:` trailer via `Bash(git *)`, and the skill and workflow calls). **Not verified:** that the Workflow tool is available under `-p` on 2.1.286; fallback: the same `/factory run …` line typed in an interactive `claude` session started with the same `--allowedTools`, since every ⟨wf⟩ item asserts on the store afterwards, not on the transcript. Today E1 (`factory: command not found` from the skill's first command; the skill file itself is absent, E1 `ls`). Fixture for every item: `pip install -e .` on `feat/lionbot-v3` in `~/dev/nanobot-upstream`, `factory init` done, `AS() { FACTORY_KEY=$1 "${@:2}"; }` defined (sets `GIT_SSH_COMMAND` to `keys/$1`; falls back to `FACTORY_IDENTITY=$1` with the local path when sshd is absent), `O` = the bare repo URL.

### Requests, store, log, results, parser (S1)

1. `printf '# fix the thing\nit breaks\n' > r.md; factory request new --file r.md` → stdout `T-0001`; `factory ticket show T-0001 | grep -E '^(status|round|request):'` → `status: ready-for-triage`, `round: {spec: 0, pr: 0}`, `request: requests/T-0001.md` [NEW]
2. `mkdir -p kv/specs; cp r.md kv/specs/a.md; cp r.md kv/specs/b.md; factory intake kv/specs` → `imported 2, skipped 0`; again → `imported 0, skipped 2 (already imported)`; `factory intake` with no argument → reads `knowledge_vault/specs` (stdout names it) [NEW]
3. `factory ticket new --type feature --title x` → exit 2, stderr `use factory request new` [NEW]
4. `factory log tail -n 1 | python3 -c 'import sys,json; print(json.loads(sys.stdin.read())["event"])'` after item 1 → `ticket.created` [NEW]
5. `factory results show T-0001` → contains `head: null`, exit 0 [NEW]
6. ⟨bare⟩ `factory ticket set T-0001 head=H`; `printf 'Commit: H\nSTATUS: APPROVE\nCONFIDENCE: high, x\nESCALATIONS: none\n' > o.md; AS harness factory results record T-0001 --head H --role reviewer --output o.md` → exit 0; `factory results show T-0001` → `reviewer: APPROVE`, `missing: ci, verifier for H`. Then `factory ticket set T-0001 head=H2; AS harness factory results record T-0001 --head H --role verifier --output v.md` → exit 0, `factory log tail -n 1 --event result.stale-discarded` → one line naming `H`; `factory results show T-0001` → `missing: ci, reviewer, verifier for H2` [NEW]
7. ⟨bare⟩ `AS daniel factory results record T-0001 --head H --role reviewer --output o.md` → exit 1, stderr `results/ may only be written by harness` [NEW]
8. Parser: `printf 'body\nSTATUS: REVISE\nCONFIDENCE: high, ok\nESCALATIONS:\n- one\n- two\n' > m.md; factory status parse m.md` → `{"status": "REVISE", "escalations": ["one", "two"]}`; the same text with an earlier `STATUS: APPROVE` line in the body → still `REVISE`; text without a `CONFIDENCE:` line → `{"status": null, "error": "parse failure"}` [NEW]
9. `factory run start --role triage --ticket T-0001 --head none` → prints `run_id`; `runs/<run_id>/input.md` absent; `factory run compose <run_id>` → `runs/<run_id>/input.md` contains the text of `requests/T-0001.md` and `meta.yaml` `input_sources: [requests/T-0001.md]`; `factory ticket show T-0001 | grep in_flight` → `in_flight: [<run_id>]`; `factory run finish <run_id> --output-file m.md` → stdout JSON with `"status": "REVISE"`, `in_flight: []`, `factory log tail -n 1 --event escalation.queued` → one line listing two items [NEW]
10. `factory run finish <run_id> --output-file m.md --status-override KILLED` → `meta.yaml` `status: KILLED`, `run.killed` logged [NEW]

### Permissions (S2) ⟨bare⟩

Setup: `git clone $O w; cd w; git commit --allow-empty -m c`.

11. `AS implementer git push $O HEAD:main` → exit 1, stderr contains `[remote rejected]` and `refs/heads/main: identity implementer may not push`; `git ls-remote $O main` unchanged [NEW]
12. `git push $O HEAD:ticket/T-0001` with no key → exit 1 (ssh: `Permission denied (publickey)`; local fallback: `identity anonymous may not push`); there is no reviewer or verifier key to try (`ls ~/factory-remote/keys/ | grep -cE 'reviewer|verifier'` → `0`) [NEW]
13. With `T-0001` `in_flight` holding an implementer run (`factory ticket set T-0001 status=ready-for-implementer`, then item 9's `run start` with `--role implementer`): `AS implementer git push $O HEAD:ticket/T-0001` → exit 0. With `in_flight: []`: a new commit pushed the same way → exit 1, stderr `ticket/T-0001: no implementer run in flight` [NEW]
14. `AS implementer git push --force $O HEAD~1:ticket/T-0001` → exit 1, stderr `non-fast-forward refused`; `AS implementer git push $O :ticket/T-0001` → exit 1, `deletion refused` [NEW]
15. `AS retro git push $O HEAD:retro/2026-w40` → exit 0; `AS retro git push $O HEAD:ticket/T-0001` → exit 1 [NEW]
16. `AS harness git push $O HEAD:factory/state` → exit 0; `AS implementer git push $O HEAD:factory/state` → exit 1 [NEW]
17. `AS daniel git push $O HEAD:main` → exit 1, stderr `refs/heads/main: identity daniel may not push` [NEW]
18. On `factory/state`: commit `approvals/T-0001/pr-H.yaml`; `AS harness git push $O HEAD:factory/state` → exit 1, `approval rows need a human pusher`; the same commit `AS daniel` → exit 0 [NEW]
19. On `factory/state`: edit the first line of `log/2026-10.jsonl`, push `AS daniel` → exit 1, `log/2026-10.jsonl is append-only`; append a line instead → exit 0 [NEW]
20. **Hook reads server-side refs (S4):** `AS implementer git push $O HEAD:ticket/T-0001` where the commit edits `factory/identities.yaml` to grant `implementer` `refs/heads/main` → exit 0 (ticket branch, allowed); then `AS implementer git push $O HEAD:main` → exit 1, `refs/heads/main: identity implementer may not push` [NEW]

### Merge gate (S2) ⟨bare⟩

21. `factory merge T-0001` with `head: H`, no rows → exit 2, stdout `missing: ci, reviewer, verifier for H`; `main` unchanged [NEW]
22. Rows `ci PASS`, `reviewer APPROVE`, `verifier VERIFIED` for `H` (via `results record`), `H` contains `main`, diff = `nanobot/hello.py` + new `tests/factory/test_hello.py` → `factory merge T-0001` exit 0; `git ls-remote $O main | cut -f1` → `H`; `status: merged` [NEW]
23. As 22 but `main` advanced by `M` after the rows → exit 2, `head H does not contain main M`; `status: ready-for-implementer`, `round: {spec: 0, pr: 1}` [NEW]
24. As 22 but rows for previous head `H0` → exit 2, `missing: ci, reviewer, verifier for H` [NEW]
25. As 22 plus `pyproject.toml` changed, no approval → exit 2, `protected path pyproject.toml needs human approval on H`; after `AS daniel factory approve-pr T-0001 --head H` → exit 0 [NEW]
26. **Guardrail gate on a normal PR:** as 22 plus `AGENTS.md` changed → exit 2, `guardrail path AGENTS.md needs human approval on H`; after `approve-pr` → exit 0 [NEW]
27. As 22 but modifying existing `tests/factory/test_existing.py` not in the pinned list → exit 2, `existing test tests/factory/test_existing.py modified; not in Tests to change of pinned spec v1`; with it listed → exit 0 [NEW]
28. As 22 but only adding `tests/factory/test_new.py` → exit 0, no approval row [NEW]
29. Hook is the authority: conditions of 21, `AS harness git push $O H:main` → exit 1, stderr `(pre-receive hook declined)` and `missing: ci, reviewer, verifier for H` [NEW]
30. **Retro exception:** `factory ticket new --type retro --branch retro/2026-w40` → `R-…`; head `R` touches only `.claude/agents/factory-spec-writer.md`; `ci PASS`, no reviewer/verifier; `AS daniel factory approve-guardrail R-… --head R` → `factory merge R-…` exit 0. (a) diff adds `nanobot/x.py` → exit 2, `exception withdrawn: nanobot/x.py is not a guardrail path; missing: reviewer, verifier for R`. (b, S5) diff touches only `factory/hooks/pre-receive` → exit 2, `exception withdrawn: factory/hooks/pre-receive is not a guardrail path; missing: reviewer, verifier for R` [NEW]
31. **Revert, valid:** after 22, `git revert --no-edit H` on `revert/V-0001`, pushed `AS daniel`; `factory ticket new --type revert --branch revert/V-0001 --reverts H` → `V-0001`, `reverted_head: H`; `ci PASS`; `AS daniel factory approve-guardrail V-0001 --head V` → `factory merge V-0001` exit 0 although the diff deletes `tests/factory/test_hello.py` (added by `H`; exempt) [NEW]
32. **Revert with an extra hunk:** as 31 but the commit also adds `g.txt` → exit 2, `exception withdrawn: diff is not the inverse of H; missing: reviewer, verifier for V` [NEW]
33. `factory ticket new --type revert --branch revert/x --reverts <SHA not a merged head>` → exit 2, stderr `<SHA> is not a merged head` [NEW]
34. Sub-tickets `T-0001.2` `depends_on: [T-0001.1]` in `waiting-dependencies`; merge `T-0001.1` per 22 → `T-0001.2` `ready-for-implementer`; merge `T-0001.2` → `T-0001` `closed` [NEW]

### Dispatcher: intake workflow (S3) ⟨wf⟩

Stub cases are directories under `tests/factory/fixtures/stubs/`, each holding `<role>-<n>.md` outputs; the `factory-stub` agent returns the file for its role and call index verbatim.

35. Case `accept-approve` (`triage-1.md` ACCEPT with `Title: Fix thing`; `spec_writer-1.md` READY-FOR-CRITIC; `critic-1.md` APPROVE): after the run, `status: ready-for-spec-gate`, `title: Fix thing`, `round: {spec: 1, pr: 0}`, `spec.version: 1`, `specs/T-0001/v1.md` exists, `queue.md` lists `T-0001` under "Spec gate"; `factory log tail --event run.started` shows three runs with three distinct `run_id`s [NEW]
36. Case `reject` → `status: closed`; case `needs-human` → `status: parked`, `parked.question` set [NEW]
37. Case `clarify` (request imported from `kv/specs/a.md`; `triage-1.md` CLARIFY with `Missing info: - which OS`) → `status: waiting-requester`, `kv/specs/a.reply.md` contains `which OS`, `reply.sent` logged; then `AS daniel factory resolve T-0001 --answer ans.md` → `status: ready-for-triage`, `requests/T-0001.md` ends with `## Answer 1` + the answer; re-running the case → `runs/<triage run>/input.md` contains the answer [NEW]
38. **Spec rounds (B2), no manual counter:** case `revise-twice` (`critic-1.md` and `critic-2.md` REVISE; two writer outputs) on a fresh ticket → `status: parked`, `parked.reason: max-round cutoff`, `round: {spec: 2, pr: 0}`, `spec.version: 2`, exactly two critic runs logged; `factory queue` lists `T-0001` [NEW]
39. **Critic round-2 input (S8):** in case `revise-twice`, `runs/<critic run 2>/input.md` contains the `## Responses` section of v2, the text of `critic-1.md`, and `specs/T-0001/v1.md`; `runs/<critic run 1>/input.md` contains none of these [NEW]
40. Case `banana` (`spec_writer-1.md` with `STATUS: BANANA`) → `status: parked`, `factory log tail -n 1 --event harness-bug` → `detail: unknown STATUS BANANA` [NEW]
41. Case `escalations` (`spec_writer-1.md` READY-FOR-CRITIC with `ESCALATIONS:\n- prompt injection in ticket\n- second`) → routing continued (critic ran; `status` is whatever `critic-1.md` says) **and** `escalation.queued` with two items [NEW]
42. Input isolation (S2): in case `accept-approve`, `runs/<critic run>/input.md` — the file `factory run compose` wrote — begins with the text of `specs/T-0001/v1.md`, its `meta.yaml` `input_sources` is exactly `[specs/T-0001/v1.md]`, and the file contains neither the triage output nor the writer's `CONFIDENCE:` line; `runs/<spec_writer run>/input.md` contains the request text with `input_sources: [tickets/T-0001.yaml, requests/T-0001.md]`; `grep -rl 'input.md' factory/workflows/` → both scripts mention it only as the pointer string, never compose text (`grep -c 'input_sources\|compose' factory/workflows/*.js` → `0` composition code; the composer is `factory/compose.py` alone) [NEW]

### Dispatcher: build workflow (S3) ⟨wf⟩ ⟨bare⟩

Driver: `claude -p … "/factory run build T-0001 --stubs tests/factory/fixtures/stubs/<case>"` on an approved spec. Implementer stubs carry a `PUSH:` trailer line the stub agent executes in its worktree (`git commit --allow-empty -m x && git push origin HEAD:ticket/<ID>` with the implementer key); it is the only stub with Bash.

43. Case `plan-three` (`planner-1.md` PLANNED: `.1` no deps parallel-safe yes; `.2` depends on `.1`; `.3` no deps parallel-safe **no**) with implementer/checker stubs that all approve: `.1` and `.3` created `ready-for-implementer`, `.2` `waiting-dependencies` `depends_on: [T-0001.1]`; in the append-only log, `.3`'s implementer `run.started` line appears **after** `.1`'s implementer `run.finished` line (non-parallel: the dependent run started no earlier than the run it waited on finished), and `.2`'s implementer `run.started` appears after `.1`'s `merge.done`; `.2`'s `meta.yaml` `base` equals `.1`'s merged head (branched from `main` after that merge). No same-second or "parallel precedes" claim is made; log order is the only ordering asserted [NEW]
44. Case `review-fix` (`implementer-1.md` READY-FOR-REVIEW + PUSH; `reviewer-1.md` REQUEST-CHANGES; `verifier-1.md` VERIFIED + `Gate suite: PASS`; `implementer-2.md` READY-FOR-REVIEW + PUSH; `reviewer-2.md` APPROVE; `verifier-2.md` VERIFIED + PASS) → `T-0001.1` ends `merged`; after the first pair the ticket had `round.pr: 2` (history shows `checks-in-flight → ready-for-implementer` with `round.pr: 2`); `runs/<implementer run 2>/input.md` contains `STATUS: REQUEST-CHANGES`, `STATUS: VERIFIED`, `CI: PASS`; in the log, both checkers' `run.started` lines precede either checker's `run.finished` line (the two were in flight together) and carry distinct `run_id`s (fresh contexts) [NEW]
45. **Checker round-2 input (S8):** in case `review-fix`, `runs/<reviewer run 2>/input.md` and `runs/<verifier run 2>/input.md` each contain `reviewer-1.md`'s and `verifier-1.md`'s text and the PR description's `Responses to findings`; the round-1 inputs contain no `Findings` [NEW]
46. Case `parking-wins` (reviewer REQUEST-CHANGES, verifier SPEC-DEFECT) → `parked`, `parked.outputs` lists both run ids; `queue.md` shows both output paths [NEW]
47. Case `gate-fail` (verifier FAILED + `Gate suite: FAIL`, reviewer APPROVE, twice) → after round 1: `results/<head>/ci.yaml` `FAIL`, `round.pr: 2`; after round 2: `parked`, `max-round cutoff`. Variant: verifier output without a `Gate suite:` line → ci `FAIL`, `detail: missing Gate suite line`, and the join still proceeded (round incremented) [NEW]
48. After 47: `AS daniel factory resolve T-0001.1 --ruling notes.md --to implementer --amend-subticket sub2.md --amend-spec spec2.md` → `ready-for-implementer`, `round.pr: 0`, `specs/T-0001/subticket.md` = `sub2.md`, `specs/T-0001/v<N+1>.md` = `spec2.md`, `approved_version: N+1`, `approvals/T-0001/spec-v<N+1>.yaml` exists, `knowledge_vault/sanitized_specs/T-0001.md` = `spec2.md`; re-running `build` → `runs/<implementer run>/input.md` contains the notes, `sub2.md` and `spec2.md` text [NEW]
49. **Checker KILLED (S6, S4):** case `reviewer-killed` (stub file `reviewer-1.md` absent → the stub agent returns an empty string → the script's KILLED condition `out === null || out.trim() === ''` (I.5) holds; verifier VERIFIED) → `results/<head>/reviewer.yaml` `KILLED`, `parked`, `parked.reason: budget kill: reviewer`, `round.pr: 1`; `AS daniel factory resolve T-0001.1 --redispatch` → `ready-for-checks`; re-running `build` with `reviewer-1.md` present → exactly one new `run.started` (reviewer, same head), none for verifier; `round.pr` still 1; ticket proceeds to `merged` [NEW]
50. `AS daniel factory resolve T-0001 --to spec-gate` on a parked spec loop → `ready-for-spec-gate`; `AS daniel factory resolve T-0001 --close` → `closed`, `approvals/T-0001/resolve-1.yaml` `by: daniel` [NEW]
51. No second implementer: with `T-0001.1` `in_flight` set to an implementer run, running `build` → `factory ticket ready-implementers T-0001` → `[]`, no new `run.started` for `.1`; `git -C ~/factory/clone worktree list | grep -c ticket/T-0001.1` ≤ 1 [NEW]
52. Head-does-not-contain-main inside the loop: case `review-fix` with `main` advanced by `M` between the push and the join → history shows `ready-for-merge → ready-for-implementer` with `round.pr` unchanged and findings `does not contain main M`; the next implementer input contains that line [NEW]
53. Retro: `claude -p … "/factory run retro --stubs …/retro-nochanges"` → `run.finished` logged, no `R-*` ticket, `queue.md` "Guardrail gate" empty; `…/retro-proposed` (stub pushes `retro/<date>` with the retro key) → ticket `type: retro`, `branch`, `head` set, listed under "Guardrail gate" [NEW]

### Agent definitions, isolation, secrets (S3)

54. `grep -E '^tools:' .claude/agents/factory-reviewer.md .claude/agents/factory-verifier.md .claude/agents/factory-critic.md` → each lists `Read, Grep, Glob, Bash` and none contains `Edit` or `Write`; `factory-implementer.md` and `factory-retro.md` list `Edit, Write`; `factory-clerk.md` lists only `Bash`; `grep -rc bypassPermissions .claude factory` → `0` [NEW]
55. `head -1 .claude/agents/factory-critic.md` (after frontmatter) → `Read factory/prompts/preamble.md before anything else`; `grep -c '{repo name}' factory/prompts/preamble.md` → `0`; `grep -c nanobot …` → `≥ 1`; `grep -c 'never name a test function' .claude/agents/factory-triage.md .claude/agents/factory-spec-writer.md` → `1` each [NEW]
56. Real CLI, no stub: `claude -p --restricted --tools Read,Grep,Glob,Bash --agent factory-verifier "Run: git push $O HEAD:ticket/T-0001.1 ; then print the exit code and STATUS: VERIFIED"` in a checker checkout (`--agent` exists on 2.1.286, E6; `--system-prompt-file .claude/agents/factory-verifier.md` is the equivalent form) → the transcript shows the push refused (exit 1: ssh `Permission denied (publickey)`, or the local fallback's `identity anonymous may not push`); `git ls-remote $O ticket/T-0001.1` unchanged; no key was present: `ls ~/factory-remote/keys/ | grep -cE 'reviewer|verifier'` → `0` and `env | grep -cE '^(FACTORY_KEY|GIT_SSH_COMMAND)='` in the checker's environment → `0` [NEW]
57. Redaction: `factory run finish RUN --output-file k.md` where `k.md` contains the body of `~/factory-remote/keys/daniel` → `grep -c "$(sed -n 2p ~/factory-remote/keys/daniel)" runs/RUN/output.md` → `0`, file contains `[REDACTED]` [NEW]
58. After any ⟨wf⟩ run: every `runs/<run_id>/` has `meta.yaml`, `input.md`, `system-prompt.txt`, `output.md`; `meta.yaml` has `wall_s` and `workflow_run_id`; `git -C ~/factory/clone worktree list | grep -c runs/` → `0` (checker checkouts cleaned) [NEW]
59. Wall-clock kill: `factory run finish RUN --output-file m.md` where `meta.yaml` `started` is 31 minutes before now and `time_budget_s: 1800` → `status: KILLED`, `run.killed` logged, `round` unchanged on the ticket [NEW]

### Human surface and export (S4)

60. ⟨bare⟩ `AS daniel factory approve-spec T-0001 --version 1` → `approvals/T-0001/spec-v1.yaml` `by: daniel`; `approved_version: 1`; `status: ready-for-planner`; `knowledge_vault/sanitized_specs/T-0001.md` equals `specs/T-0001/v1.md`; `spec.exported` logged. `AS harness factory approve-spec T-0001 --version 1` → exit 1, `approval rows need a human pusher` [NEW]
61. `AS daniel factory approve-spec T-0001 --edit edited.md` → `specs/T-0001/v2.md` = `edited.md`, `approved_version: 2`, export updated [NEW]
62. `AS daniel factory request-changes T-0001 --notes n.md` at `round.spec: 2` → `ready-for-spec-writer`, `round.spec: 0`; the next `intake` run's writer `input.md` contains the notes [NEW]
63. `factory queue` with two parked tickets → `queue.md` "Parked" lists both oldest first with `reason:` and a `Decision:` line; writing `Decision: close` under one and `AS daniel factory queue apply` → that ticket `closed`, line cleared, `human.resolved` logged [NEW]
64. `git -C ~/dev/nanobot-upstream status --porcelain` after `factory init`, `intake`, `approve-spec` and one ⟨wf⟩ run → contains no line for `knowledge_vault/ProjectNotes/SPEC_MAINTENANCE_WORKFLOW.md`, `port_state.json` or `scripts/`, and `webui/package-lock.json` is listed exactly as before (`git diff --stat webui/package-lock.json` unchanged) [NEW]

### Audit and retro (S5)

65. `factory audit-sample --since 7d --n 5` with 3 merged → prints 3 IDs and `note: only 3 merged in period`; `audits/<date>.yaml` written [NEW]
66. `factory retro-input` → sections `incidents`, `instruction files`, `previous proposals`, `counts per role` (e.g. `verifier: runs=4 FAILED=1` from `log/`) [NEW]

### CLI guards (S1)

68. **Round guard:** ticket in `ready-for-critic` with `round.spec: 2` and `max_rounds.spec: 2`: `factory ticket transition T-0001 --to ready-for-spec-writer --by RUN --round spec:+1` → exit 2, stderr `round.spec 2 is at max_rounds 2`; `factory ticket show T-0001` unchanged (`status`, `round`), `factory log tail -n 1` is not a `ticket.transition` for it. With `round.spec: 1` → exit 0, `round: {spec: 2, pr: 0}`. Same for `pr:+1` at `round.pr: 2` [NEW]
69. **Edge guard:** ticket in `ready-for-triage`: `factory ticket transition T-0001 --to merged --by RUN` → exit 2, stderr `no route ready-for-triage → merged`, store unchanged; `--to ready-for-spec-writer` → exit 0. `--to checks-in-flight` from `ready-for-spec-gate` → exit 2 (not a doc §Routing table edge) [NEW]
70. **Run-start guard:** ticket in `ready-for-triage`: `factory run start --role critic --ticket T-0001 --head none` → exit 2, stderr `T-0001 is ready-for-triage, not ready-for-critic`; no new `runs/<id>/` directory; `in_flight: []`. Then with the ticket in `ready-for-implementer` and one implementer run started: a second `factory run start --role implementer --ticket T-0001 --head none` → exit 2, stderr `ticket/T-0001 already has run <id> in flight`, `in_flight` still one id; in `checks-in-flight`, `run start --role reviewer` then `run start --role verifier` → both exit 0 (different roles), a second `--role reviewer` → exit 2 [NEW]

### Gates (every seam)

67. `ruff check factory tests/factory && mypy factory && pytest -q tests/factory` → exit 0 on `main` after each seam merges [NEW; today, run as written, the chain fails at its first leg: `ruff check factory tests/factory` → `E902 No such file or directory`, exit 1; run alone, `mypy factory` → `can't read file 'factory'`, exit 2; the chain never reaches pytest (whose own failure is E1). ruff and mypy are installed (E8)]

Items needing the bare repo: 6, 7, 11–34, 43–53, 56, 60. Items needing a model call (real CLI, not the stub): 56 only. Items 68–70 are local-only (S1).

## Tests to change

none (greenfield for `factory/`; no Nanobot test is touched; not verified that Nanobot's own suite is green on `feat/lionbot-v3`, so D2 keeps it out of the factory gate line).

## Out of scope

- Editing the eight prompt texts or the preamble beyond the one handoff rule the owner asked for (A); `SPEC_MAINTENANCE_WORKFLOW.md` (frozen); `webui/package-lock.json`; `port_state.json`; `scripts/spec_evidence.py`, `scripts/unit_start.sh` (a follow-up decides whether they fold in); `scripts/spec_lint.py` is left in place, not deleted.
- The cron/`factory loop`/launchd dispatcher (deferred ticket); Docker; per-Unix-user isolation.
- Any push to the GitHub remote; the "blue" checkout `~/dev/nanobot`.
- A database store; cost reporting; model choice per role (config only).
- A separate CI service (piece 11 is the verifier); multi-repo support; changes to the design doc.
- Renaming `knowledge_vault/specs/` to `tickets/` (the export directory is a config key for when that happens).

## Open questions

Each has a proposed default the spec is written against.

1. (D2) Nanobot's test and lint commands for `{gate commands}`; default `pytest -q` only.
2. (R5) An existing tracker to mirror `queue.md` into; default none.
3. (D5, Risk R1) Accept same-user deploy keys with forced commands for v0, knowing the keys are readable by every process and `update-ref` bypasses the hook (E4)? Default: accept; Docker ticket next. If macOS Remote Login is not acceptable, the fallback is the captured local-path transport with `FACTORY_IDENTITY` in env, which is weaker still.
4. (D3) Budgets: no per-agent cap exists in the Workflow API (E7); default = post-hoc wall-clock kill at 30 min plus the turn budget, with the user skipping a hung agent as the only manual kill (I.5). Acceptable for v0?
5. (D4) `{2}`,`{5}`,`{3}`,`{400}` = 2, 5, 3, 400.
6. (D8) `public API` glob `nanobot/api/**` (not verified).
7. (D7) Should `scripts/spec_lint.py` be deleted once the critic runs, or kept as a pre-intake lint the `/factory` skill calls? Default: kept, untouched.
8. (I.3) If agent definitions cannot set `env:` for the implementer key, is the `factory git-push` wrapper acceptable as the implementer's only push path? Default: yes.

## Risk

Blast radius: new files under `factory/`, `.claude/agents/factory-*`, `.claude/skills/factory*`, `tests/factory/`; edits to `pyproject.toml`, `AGENTS.md`; new files written under `knowledge_vault/sanitized_specs/` and `*.reply.md` next to requests in `knowledge_vault/specs/`. Protected paths this build touches, declared so the reviewer lists rather than escalates: **infra** `factory/hooks/**`, `factory/workflows/**`, `factory/paths.yaml`, `factory/config.yaml`; **dependencies** `pyproject.toml`; **credentials** `factory/identities.yaml`. Guardrail paths created: `.claude/agents/**`, `.claude/skills/**`, `factory/prompts/**`, `AGENTS.md` (edit; the spec-gate approval of this section covers it), `tests/factory/**` (new).

- **R1 Identity is advisory in v0.** E4: the hook inherits the pusher's environment under the local transport and `update-ref` runs no hook; with ssh forced commands the identity comes from the key, but every key is readable by the one Unix user. Mitigations: no key for checkers; tool allowlists in the agent definitions; worktree per mutating run; the implementer branch cannot be checked out twice (E3). Docker closes it.
- **R2 Baseline to beat (E9):** docs/product churn ratio under 2x and at most one fix commit per unit. The factory records what it needs to measure this (`merge.done` per sub-ticket, implementer rounds in `round.pr`, diff stats in `meta.yaml`), and `audit-sample` prints both numbers for the period; they are not acceptance items because the baseline is a property of the pipeline's output over time, not of this build.
- The hook reads `factory/state` and `main` server-side; a bug blocks every merge (fail-closed).
- The dispatcher is a Workflow script with no filesystem access (E7): every state change is a clerk agent running a `factory` command, so a clerk that misreads its instruction can skip a transition. Mitigation: each clerk call has a schema and the command is given verbatim; the round limit, the legal edges and the one-run-per-branch rule are CLI guards (B, items 68–70), so a disobedient clerk gets exit 2 and an unchanged store; items 35–53 check the store, not the script.
- **R6 Permission mode in real runs** (ruling row R6): `--permission-mode acceptEdits` with the allowlist `Bash(factory *)`, `Bash(git *)`, `Bash(pytest *)`, `Bash(ruff *)`, `Bash(mypy *)`, Read, Grep, Glob, Edit, Write, Skill, Workflow; a tool call outside it prompts the operator, so an unattended session stalls rather than widens. Checkers have no key in their environment (item 56); `bypassPermissions` and `dontAsk` appear nowhere (item 54).
- Not verified here: ssh forced commands on macOS, agent-definition `env:`, the Workflow tool under `claude -p`, `launchctl`. Each has a stated fallback.

## Responses

Round 3, to critic round 2 (the human gate ruled: apply the suggested fixes as written). Round-2 responses to critic round 1 are unchanged and stand in `spec-build-v2.md` §Responses.

- **B1 FIXED.** ⟨wf⟩ driver (Acceptance preamble) now `--tools default --allowedTools "Bash(factory *)" "Bash(git *)" Read Skill Workflow`; `--tools Bash,Read` had excluded `Skill` and `Workflow`. "Workflow available under `-p`" is marked not verified with the interactive fallback stated (same `/factory run …` line in an interactive session with the same allowlist; ⟨wf⟩ items assert on the store). E6 corrected accordingly; Risk's not-verified list updated.
- **S1 FIXED.** CLI guards in B: `factory ticket transition … --round +1` exits 2 above `config.yaml` `max_rounds`; exits 2 when `(from, to)` is not a routing-table edge (`config.yaml` `routing:`); `factory run start` exits 2 when the ticket is not in the role's ready state or its branch already has a run in `in_flight` (now a list). H states the guards are authoritative over the script; Risk bullet updated. One acceptance item per guard: 68 (round), 69 (edge), 70 (run start). Items 9 and 13 adjusted to the guard (triage role on a fresh ticket; `in_flight: []`).
- **S2 FIXED.** One input mechanism: `factory run compose RUN` (B, `factory/compose.py`) writes `runs/<id>/input.md` from the declared sources and records `input_sources:` in `meta.yaml`; `run start` lost `--input-file`; `agent()` receives only a pointer to that file (H `runRole`, I.2). Item 42 asserts on the CLI-written file and its `input_sources`, and that the workflow scripts compose no text; item 9 exercises `compose` directly.
- **S3 FIXED.** Item 56 asserts the push is refused and no key is present (`keys/` has no checker key; `FACTORY_KEY`/`GIT_SSH_COMMAND` absent from the checker's environment), not "PROBE absent". Ruling row R6 and a new Risk bullet R6 state the permission mode (`acceptEdits`, never `bypassPermissions`/`dontAsk`) and the allowlist real runs use.
- **S4 FIXED.** I.5 and H define KILLED as `out === null || out.trim() === ''`; the stub agent returns an empty string when its file is absent; item 49 cites that condition. The one manual kill path (user skips the agent → `null` → KILLED) is named in E7 and I.5, which state plainly that a hung agent blocks `parallel()` until then and that the doc's "no join waits on it" is post-hoc in v0; Open question 4 says the same.
- **S5 FIXED.** Item 67's bracketed note: run as written the chain fails at `ruff check factory tests/factory` (E902 No such file, exit 1), `mypy factory` alone fails with "can't read file" (exit 2), and pytest is never reached. (v2's round-2 S1 response said the pytest leg was the failing one; this supersedes it.)
- **N2 FIXED.** Item 43: log-order assertions only (`.3`'s `run.started` after `.1`'s `run.finished`; `.2`'s after `.1`'s `merge.done`; `.2`'s `base` = `.1`'s merged head); the "parallel-safe precedes" variant and the `started`-at-`ls-remote` claim are gone. Item 44: both checkers' `run.started` precede either's `run.finished`, distinct `run_id`s; no same-second claim.
- **N3 FIXED.** E7 and I.5 cite Open question 4 (was 8). E6 corrected: `--system-prompt`, `--system-prompt-file` and `--agent` exist on 2.1.286; item 56's primary `--agent` form is usable and the `--agent` not-verified notes in item 56, Risk and CONFIDENCE are removed.
- No DISAGREEs this round; no scope added beyond the eight fixes.

STATUS: NEEDS-SPLIT
CONFIDENCE: medium — git, worktree, hook, revert and CLI-flag claims are backed by captured runs (E1–E6, with E6 corrected per critic round 2) and the dispatcher is written against the Workflow API as documented in this session (E7); but the Nanobot checkouts, sshd and macOS were not available, so forced-command identity, agent-definition `env:`, the Workflow tool under `claude -p` and the repo's gate commands are unverified with stated fallbacks, and the v0 identity scheme is honestly forgeable (R1).
ESCALATIONS:
- Identity in v0 is an assertion (E4, Risk R1); the human should confirm Open question 3 before relying on the hook against a misbehaving implementer.
- The Workflow API offers no per-agent time or token cap (E7); piece 3's kill is post-hoc in v0 (Open question 4).
- Nanobot's own test/lint commands are still unknown (Open question 1).
