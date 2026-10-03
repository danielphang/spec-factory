## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0067-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/intake/state/runs/run-0067-verifier/wt` (branch `factory/T-0012.3`, base `51ea76c94740462b299941d40bf8a431d07ee9ba`, head `f5d820346e2ed3edd2b8d160f280dc02d74d57f1`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Sub-ticket T-0012.3

## T-0012.3 / Instances: resolver, `instance.yaml`, briefing, filled preamble, `init`, `paths`, agent pointer, workflows, test conftest

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: T-0012.1, T-0012.2

Parallel-safe: no, with T-0012.4 and T-0012.6, which depend on it and edit the same harness files or need them. It is parallel-safe with T-0012.5, which shares no files.

Scope: B.1–B.9, plus C.1 (the harness-revision function only, used by `init` and `paths`).
- The `<harness>` for C.1 is the running checkout.
- Delete A's interim `factory/config.yaml` and `factory/prompts/context.md`.
- `factory/prompts/preamble.md` becomes byte-identical to `docs/prompts/00-preamble.md`.
- New files: `factory/instance.template.yaml`, `factory/context.template.md`, `tests/factory/conftest.py`, `tests/factory/fixtures/instance/{instance.yaml,context.md}`, and new test files for B's behaviours.

Acceptance (first `uv sync --frozen`; then from the repo root):
- **harness-files-in-repo** → NEW [specs/harness-home]. THEN only `agents=6 green_only=0`.
- **role-prompt-text-unchanged** → NEW [specs/harness-home]. THEN `changed=0 of 14`.
- **init-creates-instance-in-throwaway-target** → NEW [specs/factory-instance]. THEN `init=0`, then `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1`.
- **store-command-from-subdirectory-uses-target-instance** → NEW [specs/factory-instance]. THEN `init=0`, then `new=0 tickets=[T-0001.yaml] harness_changes=0`.
- **command-outside-any-instance-refused** → NEW [specs/factory-instance]. THEN `exit=2 created=0 names_instance=1`.
- **factory-instance-override-from-elsewhere** → NEW [specs/factory-instance]. THEN `init=0`, then `found=1`.
- **composed-input-opens-with-instance-context** → NEW [specs/factory-instance]. THEN `init=0`, then `first=[CTX-MARKER for demo]`.
- **run-system-prompt-names-instance** → NEW [specs/factory-instance]. THEN `init=0`, then `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1`.
- **paths-name-harness-workflows-and-instance** → NEW [specs/factory-instance]. THEN `init=0`, then `True True True True`.
- **init-refusals-and-idempotence** → NEW (intermediate; B.5).
  - WHEN `H=$PWD; D=$(mktemp -d); (cd $D && $H/bin/factory init --repo-name x >/dev/null 2>&1; echo "outside_git=$?"); T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && cd $T && $H/bin/factory init >/dev/null 2>&1; echo "no_name=$?"; $H/bin/factory init --repo-name demo >/dev/null 2>&1; a=$(find .factory .claude -type f | sort | xargs cksum | cksum); $H/bin/factory init >/dev/null 2>&1; echo "again=$? same=$([ "$a" = "$(find .factory .claude -type f | sort | xargs cksum | cksum)" ] && echo yes || echo no)"`
  - THEN `outside_git=2`, then `no_name=2`, then `again=0 same=yes`.
- **agent-pointer-replaced** → NEW (intermediate; B.7).
  - WHEN ``for f in triage spec-writer spec-critic planner; do echo "$f old=$(grep -c 'factory/prompts/preamble.md' agents/factory-$f.md) new=$(grep -cF 'Read `system-prompt.txt` in the run directory that holds your input file before anything else; its preamble is the top of your system prompt.' agents/factory-$f.md)"; done``
  - THEN four lines, each ending `old=0 new=1`.
  - The rest of each file is covered by role-prompt-text-unchanged.
- **workflows-take-instance** → NEW (intermediate; B.8; structural only).
  - WHEN `for w in intake build; do echo "$w $(grep -c FACTORY_INSTANCE factory/workflows/$w.js)"; done`
  - THEN each count ≥ 1.
  - The workflows' behaviour is exercised end to end only by operator step 3 after close. Say so in the PR rather than claiming more.
- **no-old-paths, documents and harness** → NEW (intermediate for no-old-paths-in-live-files). `.factory/*` arrives in T-0012.6.
  - WHEN the T-0012.2 intermediate grep with pathspec `-- README.md docs dev agents factory`.
  - THEN `exit=1`.
- **harness-history-carried** → REGRESSION. THEN `0`.
- **harness-suite-passes-after-uv-sync** → REGRESSION. THEN `sync=0` and `N passed`, N ≥ 70, no `failed`/`error`. This now includes the new B test files, run through the new conftest and fixture.
- **docs-moved-and-split**, **prompt-copies-moved-unchanged** → REGRESSION. Same THEN as at T-0012.2.
- **green-harness-still-present** → REGRESSION.
- **whitespace (sub-ticket diff)** → REGRESSION. `exit=0`.

Tests to change: none.
- Existing files under `tests/factory/` stay byte-identical. The new `conftest.py` and the fixture instance change which config they run with (parent Risk).
- Check before merge: every imported test still runs against a throwaway store. `FACTORY_STATE` is set in `test_p0_cli.py`, `test_results_commit.py`, `test_shepherd.py`, `test_spec_store.py` and `test_subtickets.py`. `test_killed_checker.py` uses `test_shepherd`'s fixtures.

Protected paths: none of instance B's classes are written. `docs/prompts/00-preamble.md` is read only. Guardrails touched (declared in the parent's Risk):
- agent prompts: four `agents/` pointer lines, and `factory/prompts/preamble.md` becoming the design doc's block;
- tests: new conftest, fixture and test files.

Out of scope:
- Lock enforcement, `--accept-harness`, and the dirty-harness refusal (C.2–C.5).
- Instance B's `.factory/` (E).
- Any change to the seven role prompts.
- Changing the role text of the agent files.
- `factory render`.

---

## Shared plan context (from the plan; applies to every sub-ticket)

Six sub-tickets, one for each lettered part. The spec's seam list is a real dependency chain (A, then B, then C, then E), and each part is reviewed differently: A by mechanical comparison against green, B and C by reading code and tests, D as pure renames, E as an instance cutover, and F as design prose. Merging any two of them would mix those review modes in one diff. D and F are small enough to merge into one, but F's prose edits would then sit inside a rename diff, which makes the renames harder to verify. So they stay separate.

Order and parallelism:

```
T-0012.1 (A) ─┐
              ├─> T-0012.3 (B) ─> T-0012.4 (C) ─┐
T-0012.2 (D) ─┤                                  ├─> T-0012.6 (E)
              └─> T-0012.5 (F)                   │
              (T-0012.2 also feeds E directly) ──┘
```

- T-0012.1 and T-0012.2 can run in parallel. Their file sets do not overlap (see each ticket).
- T-0012.3 waits for both. That way B's preamble can be checked byte for byte against `docs/prompts/00-preamble.md`, and role-prompt-text-unchanged runs verbatim at B.
- T-0012.5 needs only T-0012.2, and it can run in parallel with .1, .3, .4 and .6, because it edits only `docs/design.md`, `docs/changelog.md` and `dev/build-harness.spec.md`.
- T-0012.6 is the **last sub-ticket that may touch harness paths**. Nothing that edits `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock` runs in parallel with it or merges after it unless that change also rewrites `.factory/harness.lock` (parent E.3; Risk, "Lock behaviour after close"). This includes fix-ups to .1, .3 and .4.

Planner choices the spec left open:
- **`intake/green-pilot/` moves to `.factory/green-pilot/`**, byte-identical, and `intake/answers/` moves to `.factory/answers/`, as E.5 says. `dev/` and `docs/` are ruled out. Both are in the pathspec of no-old-paths-in-live-files, and 23 of the 148 tracked pilot files contain matching old-path strings (`git grep -c <the scenario's patterns> -- intake/green-pilot | wc -l` → `23`). Records may not be rewritten. `.factory/**` is `infra` in E's protected paths, which suits closed records.
- **T-0012.6 (E) puts the moved suite into instance B's gate** (`.factory/instance.yaml`, E.1). During the build, every sub-ticket from T-0012.1 onward also runs the suite as a REGRESSION check in its own acceptance. That holds whether or not the operator does the optional step 1.
- **C.1 (the harness-revision function) is built in T-0012.3 (B)**, not T-0012.4. B.5 (`init` writes `.factory/harness.lock`) and B.6 (`paths` prints `harness_revision`) both need it, and B comes before C. C.2–C.5 (enforcement) stay in T-0012.4. This moves where the code lands. It does not change what the spec asks for.

Readings applied to every sub-ticket (from the spec's own text, not new design):
- `<harness>` in C.1 and C.4 is the **running** checkout: the one whose `bin/factory` is executing. The requirements say "running harness revision" and "running harness checkout". The `harness:` key in `instance.yaml` does not change which checkout is checked. At close, `~/dev/spec-factory-harness` does not exist yet (operator step 2 creates it), and instance-b-opens-every-ticket runs the dev checkout's own `bin/factory`.
- `BASE` in the parent scenarios is the parent's recorded base, for every sub-ticket. Sub-ticket gates use `main...HEAD`.
- Scenarios that call `bin/factory` need the checkout's `.venv`. Without it, `bin/factory` falls back to the system `python3` (green's `bin/factory`: `[[ -x "$PY" ]] || PY="python3"`), which may lack `pyyaml`. Each such sub-ticket therefore starts its acceptance with `uv sync --frozen`.
- Parent scenarios are cited by name. Their WHEN command and THEN result are exactly as written in the parent spec file named in brackets; I did not retype the long commands, to avoid transcription drift. Intermediate checks are written out in full.

---

## Parent spec (v3, pinned)

=== proposal.md
## Problem

The spec factory is a set of AI agents (triage, spec writer, critic, planner, implementer, checkers) plus a small program, the **harness**, that moves each piece of work (a **ticket**) from agent to agent, keeps the records, and enforces the rules no prompt can enforce. The harness's code lives inside the first project it was built for, a fork of the Nanobot app (`~/dev/nanobot-upstream`, branch `feat/lionbot-v3`, called "green" below). It is also wired to that project. It finds three things by looking next to its own code: its configuration, its **store** (the folder of ticket records and agent run outputs), and the **role-context block**, a short per-repository briefing that every agent reads first (which repository, how to run its tests, what kind of request to expect).

So the harness can serve only the repository it lives in. The operator, who already runs it on a second repository (this one), keeps a hand-made copy that drifts from the original, and every new project that adopts the factory would have to make the same copy.

Concretely, the only way to point the factory at a second repository is to copy the code out by hand and overwrite those files. That is how it runs against this design repository today. A script copies a pinned revision of green's harness into an ignored folder and overwrites three files. The pin is a commit id that someone updates by hand. A wrong briefing misleads every agent at once. The checking agents read the same briefing as the authors, so they share the error instead of catching it.

This repository's own layout makes it worse. Four things are mixed together, and the folder names do not say which is which:
- the design (one 759-line document that also holds the 41-item changelog);
- copies of the agents' instructions. The README says they are regenerated from the design document, but nothing regenerates them;
- the working documents for building the factory itself. They sit in `specs/` and `plans/`, the names the design reserves for the factory's own output;
- the install that actually runs the factory on this repository, `intake/`. It calls itself scratch and says to delete it, but it holds twelve tickets of records.

This affects two groups:
- The operator, who runs the factory against two repositories and keeps two drifting copies.
- Anyone who adopts the factory for a new project.

The change has two parts:
- Move the harness code into this repository, with its history, and give each target repository a small `.factory/` folder. That folder holds the repository's configuration, its briefing, the harness revision it has accepted, and its records, so one harness checkout serves many repositories.
- Rename this repository's documents so each folder says what it holds.

Moving green itself onto the new layout is a separate, later ticket.

## Evidence

All commands were run from `~/dev/spec-factory`, branch `main`. During this run, `main` moved from `239ef5f` to `f082708`, but only `issues/README.md` changed. Green (read-only reference) is at its latest pilot merge, subject `Merge factory/T-0002.1: …`. Below that commit is called **G**: `git -C ~/dev/nanobot-upstream log -1 --format=%H --grep='^Merge factory/T-0002.1' feat/lionbot-v3`, which today is green's HEAD.

**The harness locates everything relative to its own code** (green, read with `grep`/`sed`):
- `factory/store.py`: `REPO_ROOT = Path(__file__).resolve().parent.parent` and `CONFIG_PATH = …/"config.yaml"` next to the package. `state_root()` is `FACTORY_STATE` or `REPO_ROOT / cfg["state_dir"]`.
- `factory/gitops.py`: `repo_root()` is `FACTORY_REPO` or `store.REPO_ROOT`.
- `factory/compose.py`: `PROMPTS = Path(__file__).resolve().parent / "prompts"`. The composed input starts with `(PROMPTS / "context.md")`.
- `factory/cli.py`, `run start`: the system prompt is `PROMPTS/preamble.md` + `PROMPTS/<role>.md`.
- `bin/factory`: `cd "$HERE"` (the harness checkout), then `exec "$PY" -m factory`. So a cwd-based lookup inside the package sees the harness directory, not the caller's.
- The four role agent definitions (`.claude/agents/factory-{triage,spec-writer,spec-critic,planner}.md`) each say ``Read `factory/prompts/preamble.md` before anything else``. That is a path relative to the target repo.
- `factory/compose.py` and five places in `factory/cli.py` call `gitops.repo_root`, so composing a role input depends on the repo root, not only the build commands.
- `request_dir` (line 6 of `intake/instance/config.yaml`, `../../issues`) is read by no harness code: `grep -rn request_dir factory/*.py factory/workflows/` on green prints nothing (exit 1).
- `factory init` exists on green and does something else: it creates the spec-store tree inside the store (`specstore.init`).
- Green's per-repo text is only in `factory/config.yaml`, `factory/prompts/context.md`, and two lines of `factory/prompts/preamble.md`. The first is line 1 (`{repo name}` filled). The second is the protected-paths line (`diff ~/dev/nanobot-upstream/factory/prompts/preamble.md intake/instance/preamble.md` differs only on lines 1 and 38). The seven role prompts in `factory/prompts/` have no repo-specific text: `grep -i 'nanobot\|knowledge_vault\|lionbot'` over them, excluding preamble and context, prints nothing. Gate commands reach the implementer and verifier through their input, not their prompt.

**The second install is a hand copy.** `intake/setup.sh` runs `git -C "$SRC" archive "$PIN" factory bin/factory | tar -x`, then copies `instance/preamble.md`, `instance/context.md` and `instance/config.yaml` over the result. `intake/HARNESS_PIN` holds green's pilot-merge commit. `intake/README.md:1` is `# intake/ — SCRATCH`, and it says "Delete the whole directory once the issues are filed and closed". `git ls-files intake | grep -v '^intake/state/'` lists 168 files (167 without `intake/.gitignore`). The live store, `intake/state/tickets/`, holds T-0001 to T-0012.

**The documents.** `README.md:11`: "The design doc is the source of truth; `prompts/` is regenerated from it." Nothing regenerates them: this repo has no code, and green has no `factory/render.py`. `docs/spec-factory.md` is 759 lines. Its Changelog runs from line 678 and has 41 numbered entries. Line 52 ends "Where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here." References to the paths that would move (`git grep` outside the stores) are in `README.md`, `plans/build-harness.md` (9 "Parent:" lines), `plans/P0-intake-skeleton.md:3`, `intake/README.md`, `intake/instance/context.md`, and historical operator answers under `intake/answers/`.

**Green's suite and its config dependence** (trials in a scratch copy: `git archive` of `factory bin/factory tests/factory` from green, run with green's venv, `PYTHONDONTWRITEBYTECODE=1 … pytest -q -p no:cacheprovider tests/factory`; nothing was written in green):
- With green's own config: `70 passed in 92.22s`.
- With this repo's instance config (`intake/instance/config.yaml`): `1 failed, 69 passed`. The failing test checks that an untracked lockfile named in the config's `environment_files` is copied into each worktree. Green lists `uv.lock` there; this repo lists none.
- With this repo's config plus `environment_files: ["uv.lock"]`: `70 passed in 93.51s`.

Every test drives `bin/factory` as a subprocess with `cwd` set to the harness checkout, which it finds as `Path(__file__).resolve().parents[2]`. Moving the tests out of `tests/factory/` would change that root, and running them from a checkout that has its own `.factory/` would give them that instance's config.

**History extraction works** (trial in scratch, green untouched): `git clone --no-local --single-branch --branch feat/lionbot-v3 ~/dev/nanobot-upstream g`, then `git filter-repo --path factory/ --path bin/factory --path tests/factory/ --path-glob '.claude/agents/factory-*' --path-rename .claude/agents/:agents/`, gave 31 commits. `git pull --no-rebase --allow-unrelated-histories` of that into a scratch clone of this repo merged without conflict. Afterwards, acceptance item harness-history-carried printed `0` (`24` on `main` today), and role-prompt-text-unchanged printed `changed=1 of 14`. The one difference is the preamble, which part B replaces.

**The document split works** (trial in the same scratch clone: `git mv` plus an `awk` cut of the Changelog section): docs-moved-and-split printed `old_tracked=0`; changelog-moved-verbatim printed `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0`; design-text-kept printed `0`; prompt-copies-moved-unchanged printed `changed=0 of 10 VERBATIM`.

**Sequencing facts.** Green's harness tickets #16 and #18 are merged and closed. `issues/README.md` on `main` (`f082708`) now says #20 and #21 come "after #19", and that "#13, #14 fold in" to #21. Both are "not in intake yet". `uv sync --frozen` here today prints `error: No \`pyproject.toml\` found in current directory or any parent directory`.

## Root cause

The harness treats "the repo I serve" as "the repo I live in":
- `store.REPO_ROOT` and `store.CONFIG_PATH` (config), `store.state_root` (store), `gitops.repo_root` (target repo), `compose.PROMPTS/context.md` (role-context block), and `cli` `run start` (preamble with the repo name and protected paths filled) all resolve from the package's own location.
- `bin/factory` also changes into the harness directory before the package runs, so the caller's location is lost.

The only per-repo seams are the three environment overrides (`FACTORY_STATE`, `FACTORY_REPO`, `FACTORY_INTEGRATION_BRANCH`). They cannot supply config, briefing or preamble. Hence `intake/setup.sh`'s copy and overwrite.

The document confusion is historical. The design doc grew its changelog in place, `prompts/` was copied by hand, the factory's own build spec and plan were filed under the output directory names, and `intake/` started as scratch and became the self-hosting install.

## Out of scope

- **Instance A (green) cutover.** This change does not remove `factory/`, `bin/factory`, `tests/factory/` or the agent files from green, move `knowledge_vault/spec_factory/`, write green's `.factory/`, or run `factory init` there. Nothing is written under `~/dev/nanobot-upstream/`. Green keeps running its in-tree copy until its own paired ticket, driven by the Driver session.
- **Building `factory render` / `render --check`.** Only the build spec's text about them changes (part F). `docs/prompts/` stays a set of verbatim copies, re-copied by hand.
- **Role-prompt wording** (the seven role prompts and the agent definitions' role text stay byte-identical), the routing table, the store's record format, the OpenSpec tree (instance B gets no `openspec/`; `factory init` keeps creating it only where it already did, or in a new instance), and the simplifier role (#15).
- **The text of #13 and #14.** They fold into #21, which comes after #19.
- **Agent files for instance B.** This repo keeps dispatching with inline roles; no `.claude/agents/` is added here.
- **Rewriting records.** Store files, `intake/answers/*` and the green-pilot store move byte-identical, and old paths quoted inside them stay as written.
- **Moving the live store** (`intake/state/` to `.factory/state/`) and deleting `intake/harness/`. This happens after close, as an operator step (below).

## Open questions

none. The choices the request left to the planner stay with the planner: where `intake/green-pilot/` goes (subject to it moving byte-identical out of `intake/`), the order of the sub-tickets within the dependencies under design.md, and which sub-ticket puts the moved suite into this instance's gate. The design calls this spec makes are under Decisions, and the gate can override any of them.

## Decisions

- **The lock pins the harness's own code, not the checkout's HEAD.** The harness revision is the last commit that touched `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock`. A HEAD lock would refuse after every store or document commit in this repo, which is both the harness and instance B.
- **The lock guards the instance's own store only.** A run against any other store (`FACTORY_STATE` pointing elsewhere, as every test does) is not checked.
- **`FACTORY_INSTANCE` is added as an override** (the path of a `.factory/` directory), beside the walk-up. The workflows' clerk runs from the harness checkout, where the walk-up would find the harness repo's own instance, and the tests need a fixed instance.
- **The repo root is the parent of the instance directory**, whatever it is named; `FACTORY_REPO` still overrides it. The test conftest sets `FACTORY_REPO` to the harness checkout so the imported tests keep today's repo root.
- **`request_dir` is not carried into `.factory/instance.yaml`.** No harness code reads it, and its value is relative to a directory this change removes.
- **No fallback.** When no instance is found, the command is refused and nothing is written. The harness never uses an instance of its own by default.
- **No per-instance preamble file.** The harness keeps the design doc's preamble block verbatim and, at run start, fills `{repo name}` and the protected-path line from `instance.yaml`. The protected-path line is generated from the globs as `class (glob, glob), …`. Instances B and A lose their hand-written prose on that line (for example "never read or written by any role"); such notes belong in `context.md`.
- **The agent definitions' preamble pointer** changes to the run directory's `system-prompt.txt`, which `run start` already writes with the filled preamble. The role text below it is unchanged.
- **One `factory init` verb.** It is idempotent and creates whatever is missing: the instance, the briefing stub, the lock, the store with today's spec-store tree, and the agent files. `--repo-name` is required only when `instance.yaml` is missing.
- **The tests stay at `tests/factory/`**, not `tests/`, because they locate the checkout two levels up. A new `tests/factory/conftest.py` points them at a fixed test instance (one test needs `environment_files: ["uv.lock"]`; see Evidence). No existing test file changes.
- **Two checkouts for instance B (operator, at the gate).** Tickets are built and merged in the **dev** checkout, `~/dev/spec-factory` on `main`. Instance B runs from a separate **runtime** checkout: a git worktree of this repo at `~/dev/spec-factory-harness`, detached at the revision B has accepted and installed with `uv sync --frozen`. `harness:` in `.factory/instance.yaml` names the runtime by absolute path; it is the checkout that dispatchers and operators run, and `factory paths` reports it. A merge into `main` never changes the running code. **Upgrading** is a deliberate step, done when no ticket is in flight: move the runtime with `git -C ~/dev/spec-factory-harness checkout --detach <sha>`, then run `--accept-harness <sha>` in each instance that uses it. One runtime serves every target ("one checkout, many targets").
- **The lock also refuses a modified runtime (operator, at the gate).** See C.4. A runtime holds only committed, accepted code, so an uncommitted edit to harness paths there is refused rather than run unnoticed.
- **Instance B's gate adds the moved suite**: `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, next to `git diff --check main...HEAD`. Instance B's protected paths add a `harness` class (`factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`) and `.factory/**` under `infra`, and `generated` follows the copies to `docs/prompts/**`.
- **#13 and #14 are not carried.** No #13/#14 text merges while this parent is in flight. `main` already folds them into #21, after #19.
- **Part A runs `git filter-repo` only on a fresh clone of green in a scratch directory**, never in `~/dev/nanobot-upstream`.
- **Green-only files are not in this repo's tree at close:** `factory/config.yaml`, `factory/prompts/{context,preamble}.md` as green has them, and `scripts/full_suite_gate.py`. They may appear in the imported history.
- **The live store moves after close** (operator note at intake). Until then `.factory/instance.yaml` names `intake/state` as its store.

## Risk

**Blast radius.** This repo's whole layout, and every instance B run after close, which then reads a new config location and runs the in-repo harness. The history grows by about 31 imported commits. Green is unaffected until its own ticket.

**Lock behaviour after close.** Merges into `main` do not move the runtime, so they never trip the lock. Only the upgrade step does: after moving the runtime, instance B refuses store commands until the operator runs `--accept-harness`. A build workflow in flight at that moment parks the ticket as a harness bug, which is why upgrades happen between tickets. This ticket's own build runs on the old copy in `intake/harness/`, which has no lock, so it is not affected. Within this parent, the lock E writes is right at close only if no later sub-ticket changes harness code; if any later sub-ticket touches harness paths, it also rewrites `.factory/harness.lock` (E.3). The planner must not let a fix-up on harness paths merge after E without that.

**Part A size.** Part A is about 4,400 imported lines plus `uv.lock`: 2,557 lines of package, workflows and `bin/factory`, and 1,801 lines across 7 test `.py` files plus fixtures. That is far above the 400-line guideline, but it is a verbatim import. It is verified mechanically (history subjects, byte comparison of the role prompts, the suite) rather than by reading. Part A's own non-import diff is small: `pyproject.toml`, `.gitignore`, and the interim overlay.

**Fragile acceptance anchor.** Items harness-history-carried and role-prompt-text-unchanged find green's pilot merge by its subject. If part A cuts later than G and green changes a role prompt in between, role-prompt-text-unchanged compares against the wrong revision. Check `git -C ~/dev/nanobot-upstream log G..feat/lionbot-v3 -- factory/prompts .claude/agents` (empty today, since G is green's HEAD).

**Protected paths touched** (instance B's current classes, declared for the gate):
- **infra `intake/**`**: `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed. `intake/answers/` and `intake/green-pilot/` move out, byte-identical. `intake/state/**` and `intake/.gitignore` are not changed by the PRs; the post-close operator step moves them.
- **generated `prompts/**`**: moved to `docs/prompts/`, byte-identical.
- **reference_harness `~/dev/nanobot-upstream/**`**: read only. Part A clones it into a scratch directory; acceptance reads it with `git log`, `git show` and `git cat-file`.
- **credentials `~/.nanobot/**`**: not read or written.

**Guardrail paths touched:**
- **Agent prompts.** The six agent definitions move to `agents/`, and four of them get the new pointer line. The seven role prompts move to `factory/prompts/` byte-identical. The preamble becomes the design doc's block verbatim. The `prompts/` copies move to `docs/prompts/`.
- **Tests.** There are no existing tests in this repo. `tests/factory/**` arrives as new files, byte-identical to green's. New test files and the new `conftest.py` with its fixture instance are added. The conftest changes which config every imported test runs with: the fixed fixture instead of whatever instance surrounds the checkout.
- No CI config, `AGENTS.md` or skills exist here.

## Operator steps

1. **Optional, during the build, after part A merges.** Run `uv sync` in `~/dev/spec-factory`. Then append `uv run --frozen pytest -q -p no:cacheprovider tests/factory` to `gate_commands` in the running copy's `intake/harness/factory/config.yaml`, so that later sub-tickets are gated by the moved suite. That file is live, gitignored infra.
2. **After the parent closes**, with the store committed and no run in flight, move the live store:
   - `git mv intake/state .factory/state`.
   - In `.factory/instance.yaml`, set `state_dir: .factory/state` and drop `intake/**` from `protected_paths.infra`.
   - `git rm -q intake/.gitignore && rm -rf intake/harness`.
   - Move or delete anything still under `intake/` (untracked; today `intake/requests/19_harness_home.md`).
   - Create the runtime at the closing revision: `git worktree add --detach ~/dev/spec-factory-harness main && uv sync --frozen --project ~/dev/spec-factory-harness`. Its harness revision equals the lock E wrote (E.3).
   - Check: `~/dev/spec-factory-harness/bin/factory paths`, run from `~/dev/spec-factory`, shows `harness` = the runtime and `state` ending in `/.factory/state`, and the command of scenario instance-b-opens-every-ticket prints `tickets=N failed=0` with N ≥ 12.
   - Commit.
3. **End-to-end run.** Run the next ticket (#20 or #21) through the moved harness: take `intake_workflow` from `~/dev/spec-factory-harness/bin/factory paths`, and call the Workflow tool with `{ticket, repo: <abs ~/dev/spec-factory-harness>, instance: <abs ~/dev/spec-factory/.factory>, inlineRoles: true}`. This is the request's "the installed harness runs this repo's own `.factory/` end to end". It needs agent runs, so it is not an acceptance command.
4. **Bookkeeping.** Update the #19 row in `dev/issues.md` and close GitHub #19. Then open the paired instance-A ticket for the Driver session.

=== design.md
## Proposed change

There are six parts, A to F; this is the NEEDS-SPLIT seam list. Dependencies: A before B before C before E. D can land at any point. F comes after D. E comes after B, C and D. All paths are relative to `~/dev/spec-factory` unless they start with `~/`.

**A. Harness import, with history.** Part A's tip has the harness in this repo and its suite green. It makes no behaviour change.
1. Make a fresh scratch clone: `git clone --no-local --single-branch --branch feat/lionbot-v3 ~/dev/nanobot-upstream <scratch>/g`. Its tip must be at or after G. Never run `filter-repo` in `~/dev/nanobot-upstream`.
2. In the clone: `git filter-repo --path factory/ --path bin/factory --path tests/factory/ --path-glob '.claude/agents/factory-*' --path-rename .claude/agents/:agents/`.
3. On the sub-ticket branch: `git pull --no-rebase --allow-unrelated-histories --no-edit <scratch>/g HEAD`. No paths overlap.
4. Remove the three green-only files from the tree and replace them with an **interim overlay**, which is this repo's current instance files. Part B deletes it.
   - `factory/config.yaml` becomes `intake/instance/config.yaml`, with `state_dir: intake/state` (now relative to this repo's root) and `environment_files: ["uv.lock"]`. The suite needs the latter (Evidence).
   - `factory/prompts/context.md` becomes `intake/instance/context.md`.
   - `factory/prompts/preamble.md` becomes `intake/instance/preamble.md`.
   - Every other imported file stays byte-identical to green at the cut.
5. Add `pyproject.toml` with:
   - `[project] name = "spec-factory"`, `version = "0.0.0"`, `requires-python = ">=3.11"`, `dependencies = ["pyyaml>=6"]`;
   - `[dependency-groups] dev = ["pytest>=8"]`;
   - `[tool.uv] package = false`.
   `bin/factory` runs `python -m factory` from the checkout, so no build backend is needed. Run `uv lock` and commit `uv.lock`. Add a root `.gitignore` with `.venv/`, `__pycache__/` and `.pytest_cache/`.
6. Check: `uv sync --frozen && PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory` reports 70 passed.

**B. Instances: discovery, config, briefing, preamble, `init`, `paths`.**
1. **One instance resolver**, used by `store`, `gitops`, `compose` and `cli`:
   - If `FACTORY_INSTANCE` is set, it names the instance's `.factory/` directory.
   - Otherwise, walk up from the caller's working directory to the nearest directory that contains `.factory/instance.yaml`. `bin/factory` must hand the package the caller's working directory, since it changes into the harness checkout before running.
   - If nothing is found, exit 2 with stderr `no .factory/instance.yaml found from <cwd>; run factory init --repo-name NAME, or set FACTORY_INSTANCE`, and write nothing. There is no fallback to the harness checkout.
   - `init` and `paths` are exempt.
2. **Where things come from:**
   - Config is `<instance>/instance.yaml`. This replaces `store.CONFIG_PATH`; the keys are today's config keys plus `harness`.
   - The repo root is the parent of the instance directory, whatever that directory is named (`.factory/` when found by the walk-up; any directory when named by `FACTORY_INSTANCE`). `FACTORY_REPO` still overrides it.
   - `state_dir` is relative to the repo root. `FACTORY_STATE` still overrides it.
   - `FACTORY_INTEGRATION_BRANCH` is unchanged.
3. **Role-context block.** `run compose` opens `input.md` with `<instance>/context.md`. Delete `factory/prompts/context.md`.
4. **Preamble.** `factory/prompts/preamble.md` becomes the design doc's preamble block verbatim, byte-identical to `prompts/00-preamble.md` (later `docs/prompts/00-preamble.md`). `run start` writes `system-prompt.txt` with two substitutions:
   - `{repo name}` becomes the instance's `repo_name`.
   - The line `  {auth, payments, migrations, infra, public API, dependencies}` becomes two spaces followed by `<class> (<glob>, <glob>)` for each `protected_paths` entry, joined by `, `.
   The seven role prompt files do not change.
5. **`factory init [--repo-name NAME]`** works at the git top level of the working directory, and exits 2 outside a git work tree. It is idempotent and creates only what is missing:
   - `.factory/instance.yaml`, from a new `factory/instance.template.yaml`. It sets `repo_name`, `harness` (the absolute path of the running harness checkout), `state_dir: .factory/state`, `protected_paths: {infra: [".factory/instance.yaml", ".factory/harness.lock", ".factory/context.md"]}` and `gate_commands: []`. Today's generic values come with it: placeholders, `max_rounds`, `integration_branch: null`, `environment_files: []`, `force_push_allowed: false`, `models`, `ready_state`, `routing`. It needs `--repo-name`; without one, it exits 2.
   - `.factory/context.md`, from a new `factory/context.template.md`: a stub that says what the briefing must state.
   - `.factory/harness.lock`: the current harness revision (C).
   - The store at `state_dir`, with today's `init` content (the spec-store tree, `decisions.md`) and the store `.gitignore`.
   - `.claude/agents/factory-*.md`, copied from `agents/` for each missing file. When it writes any agent file, it prints `restart the session so the agents register`.
   After a fresh `init`, `.factory/` holds exactly `context.md`, `harness.lock`, `instance.yaml` and `state`. With an instance present and `--repo-name` omitted, it does today's `init` plus any missing pieces.
6. **`factory paths`** prints one JSON object with absolute paths: `harness`, `bin`, `intake_workflow`, `build_workflow`, `harness_revision` (C), `instance` and `state`. The last two are `null` when no instance is found. It runs no lock check and writes nothing.
7. **Agent templates.** In `agents/factory-{triage,spec-writer,spec-critic,planner}.md`, replace the line ``Read `factory/prompts/preamble.md` before anything else; it is the top of your system prompt.`` with ``Read `system-prompt.txt` in the run directory that holds your input file before anything else; its preamble is the top of your system prompt.`` Nothing else in `agents/` changes.
8. **Workflows.** `factory/workflows/intake.js` and `build.js` accept `instance`, the absolute path of the target's `.factory/`. When it is given, every store command is prefixed with `FACTORY_INSTANCE=<instance>`. `state` becomes optional (it still sets `FACTORY_STATE`), and `repo` stays the harness checkout. Update the header comments.
9. **Tests.**
   - Add a new `tests/factory/conftest.py` that, at import, sets `os.environ["FACTORY_INSTANCE"]` to a new fixture, `tests/factory/fixtures/instance/`, and sets `FACTORY_REPO` to the harness checkout (`Path(__file__).resolve().parents[2]`) unless it is already set. Without the second line the repo root would be `tests/factory/fixtures/` (B.2); with it, every imported test sees the same repo root it sees today, and the shepherd tests, which set `FACTORY_REPO` to their own throwaway repo in each subprocess environment, still override it. The fixture has `instance.yaml` with the template values plus `environment_files: ["uv.lock"]` and `gate_commands: ["git diff --check main...HEAD"]`, and a `context.md`. Every existing test already builds its subprocess environment from `os.environ`.
   - Add new test files for B's behaviours.
   - Delete A's interim `factory/config.yaml`. Its `prompts/context.md` was deleted in item 3.

**C. Harness revision and lock.**
1. The **harness revision** is `git -C <harness> log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock`.
2. **When the store in use is the instance's own store** (`FACTORY_STATE` is unset or resolves to the instance's `state_dir`), every command except `init` and `paths` first compares the stripped first line of `<instance>/harness.lock` with the revision. If they differ, or the lock is missing, the command exits 2 with stderr `harness <rev> is not the revision this instance accepted (<lock>|none); rerun with --accept-harness <rev> to accept it`, and writes nothing. Other stores are not checked.
3. **`--accept-harness SHA`** is a global option, written before the subcommand.
   - The SHA must equal the current revision, as 40 hex characters. Otherwise the command exits 2 and leaves the lock unchanged.
   - If it matches, the harness writes the SHA to `harness.lock` and appends a log event to the instance's store recording the old and new revisions, then runs the command.
4. **Uncommitted harness edits are refused** under the same condition as item 2. If `git -C <harness> status --porcelain -- factory bin/factory agents pyproject.toml uv.lock` prints anything (files `.gitignore` excludes do not count), the command exits 2, writes nothing, and its stderr says `harness <path> has uncommitted changes:` followed by the changed paths, one per line. `--accept-harness` does not override this: the edit is committed or discarded first. Like item 2, it applies only to the instance's own store, so a harness under development, which is uncommitted by definition, still runs its own tests against throwaway stores.
5. Add new test files for C.

**D. Document re-layout.** Content is unchanged apart from the path updates.
1. `git mv docs/spec-factory.md docs/design.md`. Then move its `## Changelog` section, from the heading to the line before `## Appendix`, into a new `docs/changelog.md`: a `# Changelog` title, then that text verbatim (intro paragraph, numbered entries, `Declined:` line). At the end of "How to use this" in `docs/design.md`, add one line naming `docs/changelog.md` and `docs/prompts/`.
2. `git mv prompts docs/prompts`. The bytes do not change.
3. `git mv specs/build-harness.md dev/build-harness.spec.md`, `git mv plans/build-harness.md dev/build-harness.plan.md`, `git mv plans/P0-intake-skeleton.md dev/P0-intake-skeleton.md`, `git mv issues/README.md dev/issues.md`.
4. Update the references in:
   - `README.md` (until E rewrites it);
   - `dev/build-harness.plan.md` (the nine `Parent:` lines);
   - `dev/P0-intake-skeleton.md:3`;
   - `intake/README.md` and `intake/instance/context.md` (while they still exist).
   Records are left as written: `intake/answers/`, the stores, and changelog entries.

**E. Instance B cutover.** The live store does not move in this part.
1. `.factory/instance.yaml` starts from `intake/instance/config.yaml`, with these changes:
   - `repo_name: "spec-factory (the design repo at ~/dev/spec-factory, branch main)"`, `harness: <absolute path of ~/dev/spec-factory-harness>` (the runtime; the Decisions entry on two checkouts) and `state_dir: intake/state`.
   - `protected_paths`: `infra: [".factory/**", "intake/**"]`, `harness: ["factory/**", "bin/factory", "agents/**", "pyproject.toml", "uv.lock"]`, `generated: ["docs/prompts/**"]`, `reference_harness: ["~/dev/nanobot-upstream/**"]`, `credentials: ["~/.nanobot/**"]`.
   - `gate_commands: ["git diff --check main...HEAD", "uv run --frozen pytest -q -p no:cacheprovider tests/factory"]` and `environment_files: []`. `uv.lock` is tracked here, and copying it in would mask a branch's own lock.
   - `request_dir` is dropped: no harness code reads it, and its value (`../../issues`) is relative to the old `intake/harness/` copy and names a directory D removes.
   - Every other key is unchanged.
2. `.factory/context.md` is `intake/instance/context.md` rewritten for the new layout. It names:
   - `docs/design.md` (source of truth) and `docs/changelog.md`;
   - `docs/prompts/` (verbatim copies, changed only by re-copying);
   - `dev/` (working documents for building the factory);
   - the harness as code in this repo (`factory/`, `bin/factory`, `agents/`, `tests/factory/`, run with `uv run --frozen pytest -q -p no:cacheprovider tests/factory`);
   - the two checkouts: tickets merge into the dev checkout (`~/dev/spec-factory`, `main`); the factory runs from the runtime (`~/dev/spec-factory-harness`), moved only by the upgrade step;
   - green as instance A, read only.
   It keeps the existing rules on acceptance commands and design-doc conventions, with the paths updated.
3. `.factory/harness.lock` holds the harness revision (C.1) at E's base. Any sub-ticket that touches `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock` and merges after E branches also rewrites `.factory/harness.lock` to the new revision; otherwise instance B refuses its own store at close.
4. `.factory/README.md` carries the still-true parts of `intake/README.md`: the ticket to GitHub-issue table, how to run, and scope, written as "this repo's own instance".
5. Remove `intake/README.md`, `intake/setup.sh`, `intake/HARNESS_PIN` and `intake/instance/*`. Move `intake/answers/` to `.factory/answers/`, byte-identical. Move `intake/green-pilot/` out of `intake/`, byte-identical, to a place the planner chooses: a second instance directory or a folded-in archive. Keep `intake/state/` and `intake/.gitignore`.
6. Rewrite `README.md`:
   - what the factory is;
   - install (`git clone`, `uv sync`);
   - five-minute use: `factory init --repo-name`, restart the session, fill in `.factory/context.md` and `gate_commands`, `factory paths`, the Workflow call with `scriptPath` and `{ticket, repo, instance}`, and `approve-spec`;
   - where things live: `docs/design.md`, `docs/changelog.md`, `docs/prompts/`, `dev/`, `factory/`, `bin/factory`, `agents/`, `tests/factory/`, `.factory/`;
   - how updates work: a target holds no harness code, only `.factory/`, and runs whatever revision the runtime checkout it names has checked out. The lock makes a new revision available rather than silently adopted: each target refuses an unaccepted revision, and refuses uncommitted harness edits, until `--accept-harness`. Develop the harness in one checkout and run targets from a separate runtime checkout, so a merge never changes code under a running ticket; upgrading is moving the runtime, then accepting per target.

**F. Design-doc and build-spec text.**
1. **`docs/design.md`, §Harness, "Role-context block" paragraph.** Replace its last sentence ("Where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here.") with:
   "The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`."
2. **`docs/design.md`, piece 8 row ("Guardrail and protected paths"), "What it must do" cell.** Append: "The harness code (its package, entry point, agent templates and dependency lock) is itself a protected path in the repo that holds it."
3. **`docs/changelog.md`.** Append one entry, numbered one past the last entry at merge time (42 today):
   "After issue #19 (2026-10-02): the harness lives in this repo and each target repo carries a `.factory/` instance: `instance.yaml`, `context.md` (the role-context block, prepended by the composer), `harness.lock` (the accepted harness revision; any other revision is refused until a human accepts it) and the store. The harness finds the instance by walking up from the working directory, and its own code is a protected path in the repo that holds it. The design doc splits into `docs/design.md` and this changelog, the prompt copies move to `docs/prompts/`, and the working documents for building the factory move to `dev/`."
4. **`dev/build-harness.spec.md`.**
   - D8 row, Value column: "per instance: `repo_name` and `protected_paths` in the target repo's `.factory/instance.yaml` (doc §Harness, role-context block); for nanobot: `nanobot`; protected: `infra`, `dependencies`, `credentials`, `public API` (globs in F)".
   - Layout row `factory/prompts/design-doc.md`: becomes `docs/design.md (spec-factory, beside the harness)  the design doc; the only doc `factory render` reads (A)`.
   - Part A's `factory render` bullet: it reads `docs/design.md`, which is in the same repo as the harness, and still has no `--doc` option. It writes `docs/prompts/` and the `agents/` templates from the blocks. The placeholders are filled per instance from `.factory/instance.yaml` when a run starts, and `render --check` diffs against `docs/design.md`.
   - Item 82: every `factory/prompts/design-doc.md` becomes `docs/design.md`.
   - Leave the `## Responses` history as written.

Size per part:
- A: import plus about 40 lines of its own.
- B: about 300 lines including new tests.
- C: about 120.
- D: renames plus about 30.
- E: about 150 plus renames.
- F: about 15.

## Tests to change

none. This repo has no existing tests. `tests/factory/**` arrives byte-identical. The new `conftest.py`, the fixture instance and the new test files are new files. See Risk for the conftest's effect on the imported tests.

=== specs/harness-home/spec.md
## ADDED Requirements

### Requirement: harness-code-lives-in-design-repo
The harness package, its entry point, its two workflow scripts, its test suite and the six agent definition templates MUST be tracked in this repository, and green's repo-specific config and briefing MUST NOT be.

#### Scenario: harness-files-in-repo
- WHEN `for p in factory/cli.py factory/store.py factory/compose.py factory/gitops.py factory/workflows/intake.js factory/workflows/build.js bin/factory pyproject.toml uv.lock tests/factory/test_p0_cli.py; do test -e "$p" || echo "missing $p"; done; echo "agents=$(ls agents/factory-*.md 2>/dev/null | wc -l | tr -d ' ') green_only=$(ls factory/config.yaml factory/prompts/context.md 2>/dev/null | wc -l | tr -d ' ')"`
- THEN it prints only `agents=6 green_only=0`

### Requirement: harness-history-carried
Every non-merge commit of green, up to its latest pilot merge, that touched the harness package code, workflows, entry point, tests or factory agent definitions SHALL appear in this repository's history with the same subject.

#### Scenario: harness-history-carried
- WHEN `G=$(git -C ~/dev/nanobot-upstream log -1 --format=%H --grep='^Merge factory/T-0002.1' feat/lionbot-v3); comm -23 <(git -C ~/dev/nanobot-upstream log --no-merges --format=%s "$G" -- 'factory/*.py' factory/workflows bin/factory tests/factory '.claude/agents/factory-*' | sort -u) <(git log --no-merges --format=%s -- 'factory/*.py' factory/workflows bin/factory tests/factory 'agents/factory-*' | sort -u) | wc -l | tr -d ' '`
- THEN it prints `0`

### Requirement: harness-installs-with-uv
`uv sync` in a checkout of this repository SHALL give the harness its interpreter and dependencies, and the moved test suite MUST pass there.

#### Scenario: harness-suite-passes-after-uv-sync
- WHEN `uv sync --frozen -q >/dev/null 2>&1; echo "sync=$?"; PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1`
- THEN it prints `sync=0`, then a line `N passed in …` with N ≥ 70 and no `failed` or `error`

### Requirement: role-prompt-text-unchanged
The role prompts and agent definitions MUST move without any change to their wording: the agent templates differ from green's only in the preamble pointer line, the seven role prompts are byte-identical to green's, and the harness's preamble is byte-identical to the design doc's copy.

#### Scenario: role-prompt-text-unchanged
- WHEN `G=$(git -C ~/dev/nanobot-upstream log -1 --format=%H --grep='^Merge factory/T-0002.1' feat/lionbot-v3); c=0; n=0; for f in factory-clerk factory-planner factory-spec-critic factory-spec-writer factory-stub factory-triage; do n=$((n+1)); cmp -s <(git -C ~/dev/nanobot-upstream show "$G:.claude/agents/$f.md" | grep -v 'before anything else') <(grep -v 'before anything else' "agents/$f.md" 2>/dev/null) || c=$((c+1)); done; for f in triage spec_writer critic planner implementer reviewer verifier; do n=$((n+1)); cmp -s <(git -C ~/dev/nanobot-upstream show "$G:factory/prompts/$f.md") "factory/prompts/$f.md" || c=$((c+1)); done; n=$((n+1)); cmp -s factory/prompts/preamble.md docs/prompts/00-preamble.md || c=$((c+1)); echo "changed=$c of $n"`
- THEN it prints `changed=0 of 14`

=== specs/factory-instance/spec.md
## ADDED Requirements

### Requirement: instance-created-by-init
`factory init --repo-name NAME`, run anywhere inside a git work tree with no instance, SHALL create `.factory/` at that tree's top level holding `instance.yaml`, `context.md`, `harness.lock` and the store, SHALL copy the six agent definitions into `.claude/agents/`, and SHALL tell the operator to restart the session.

#### Scenario: init-creates-instance-in-throwaway-target
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; echo "instance=[$(ls -A $T/.factory 2>/dev/null | tr '\n' ' ')] agents=$(ls $T/.claude/agents/factory-*.md 2>/dev/null | wc -l | tr -d ' ') restart=$(grep -c 'restart the session' $T/init.out)"`
- THEN it prints `init=0` then `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1`

### Requirement: instance-found-from-working-directory
Every store command SHALL use the instance found by walking up from the caller's working directory, and MUST NOT write into the harness checkout.

#### Scenario: store-command-from-subdirectory-uses-target-instance
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; before=$(git -C $H status --porcelain | wc -l); $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; echo "new=$? tickets=[$(ls $T/.factory/state/tickets 2>/dev/null)] harness_changes=$(( $(git -C $H status --porcelain | wc -l) - before ))"`
- THEN it prints `init=0` then `new=0 tickets=[T-0001.yaml] harness_changes=0`

### Requirement: no-instance-refused
A store command run where no instance is found and no override is set MUST be refused with exit 2, an error naming `instance.yaml`, and nothing written.

#### Scenario: command-outside-any-instance-refused
- WHEN `H=$PWD; D=$(mktemp -d); cd $D && $H/bin/factory ticket show T-0001 >$D/out 2>$D/err; echo "exit=$? created=$(ls -A $D | grep -v -x -e out -e err | wc -l | tr -d ' ') names_instance=$(grep -c 'instance.yaml' $D/err)"`
- THEN it prints `exit=2 created=0 names_instance=1`

### Requirement: instance-override
`FACTORY_INSTANCE` SHALL select the instance regardless of the working directory.

#### Scenario: factory-instance-override-from-elsewhere
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; D=$(mktemp -d); cd $D && echo "found=$(FACTORY_INSTANCE=$T/.factory $H/bin/factory ticket show T-0001 2>/dev/null | grep -c '^title: demo$')"`
- THEN it prints `init=0` then `found=1`

### Requirement: compose-prepends-instance-context
Every composed role input SHALL begin with the `context.md` of the instance that owns the run.

#### Scenario: composed-input-opens-with-instance-context
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf 'CTX-MARKER for demo\n' 2>/dev/null > $T/.factory/context.md; $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; R=$($H/bin/factory run start --role triage --ticket T-0001 --model opus 2>/dev/null | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); $H/bin/factory run compose "$R" >/dev/null 2>&1; echo "first=[$(head -1 $T/.factory/state/runs/$R/input.md 2>/dev/null)]"`
- THEN it prints `init=0` then `first=[CTX-MARKER for demo]`

### Requirement: preamble-filled-from-instance
The system prompt written at run start SHALL carry the preamble with the instance's repo name and protected paths filled in and no placeholder left.

#### Scenario: run-system-prompt-names-instance
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; R=$($H/bin/factory run start --role triage --ticket T-0001 --model opus 2>/dev/null | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); P=$T/.factory/state/runs/$R/system-prompt.txt; echo "line1=[$(head -1 $P 2>/dev/null)] placeholders=$(grep -c -e '{repo name}' -e '{auth, payments' $P 2>/dev/null) protects_instance=$(grep -c '\.factory/instance\.yaml' $P 2>/dev/null)"`
- THEN it prints `init=0` then `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1`

### Requirement: paths-printed
`factory paths` SHALL print, as JSON, the harness checkout, its entry point, both workflow scripts, the harness revision and the instance in use, so a dispatcher in any target can be pointed at them.

#### Scenario: paths-name-harness-workflows-and-instance
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; $H/bin/factory paths >$T/p.json 2>/dev/null; python3 -c 'import json,os,sys; p=json.load(open(sys.argv[1])); r=os.path.realpath; print(r(p["harness"])==r(sys.argv[2]), all(os.path.isfile(p[k]) for k in ("bin","intake_workflow","build_workflow")), r(p["instance"])==r(sys.argv[3]+"/.factory"), len(p["harness_revision"])==40)' $T/p.json $H $T 2>/dev/null || echo "no paths"`
- THEN it prints `init=0` then `True True True True`

=== specs/harness-lock/spec.md
## ADDED Requirements

### Requirement: unaccepted-harness-refused
When the store in use is the instance's own store, every command except `init` and `paths` MUST be refused (exit 2, nothing written, a hint naming `--accept-harness`) if the instance's `harness.lock` does not name the running harness revision.

#### Scenario: lock-mismatch-refused
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock; $H/bin/factory ticket new --file $T/r.md >/dev/null 2>$T/err; echo "exit=$? tickets=$(ls $T/.factory/state/tickets 2>/dev/null | wc -l | tr -d ' ') hint=$(grep -c 'accept-harness' $T/err)"`
- THEN it prints `init=0` then `exit=2 tickets=0 hint=1`

### Requirement: accept-harness-is-explicit-and-logged
`--accept-harness SHA` SHALL rewrite the lock and log the acceptance only when SHA is the running harness revision, and MUST leave the lock unchanged and refuse otherwise.

#### Scenario: accept-current-revision-rewrites-lock
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock; REV=$($H/bin/factory paths 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin)["harness_revision"])' 2>/dev/null); $H/bin/factory --accept-harness "$REV" ticket new --file $T/r.md >/dev/null 2>&1; echo "exit=$? lock_is_rev=$([ -n "$REV" ] && [ "$(cat $T/.factory/harness.lock 2>/dev/null)" = "$REV" ] && echo yes || echo no) logged=$(cat $T/.factory/state/log/*.jsonl 2>/dev/null | grep "$REV" | grep -c harness)"`
- THEN it prints `init=0` then `exit=0 lock_is_rev=yes logged=N` with N ≥ 1

#### Scenario: accept-other-revision-refused
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock; $H/bin/factory --accept-harness 1234567 ticket new --file $T/r.md >/dev/null 2>&1; echo "exit=$? lock=$(cat $T/.factory/harness.lock 2>/dev/null) tickets=$(ls $T/.factory/state/tickets 2>/dev/null | wc -l | tr -d ' ')"`
- THEN it prints `init=0` then `exit=2 lock=0000000000000000000000000000000000000000 tickets=0`

### Requirement: throwaway-store-not-locked
A command whose store is not the instance's own store (`FACTORY_STATE` pointing elsewhere) SHALL run whatever the lock says.

#### Scenario: throwaway-store-ignores-lock
- WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && mkdir $T/sub && cd $T/sub && $H/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; printf '# demo\n\nDo the thing.\n' > $T/r.md; printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock; S=$(mktemp -d); FACTORY_STATE=$S $H/bin/factory ticket new --file $T/r.md >/dev/null 2>&1; echo "exit=$? ticket=[$(ls $S/tickets 2>/dev/null)]"`
- THEN it prints `init=0` then `exit=0 ticket=[T-0001.yaml]`

### Requirement: modified-harness-refused
When the store in use is the instance's own store, every command except `init` and `paths` MUST be refused (exit 2, nothing written, the changed paths named) if the running harness checkout has uncommitted changes under `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock`.

#### Scenario: dirty-harness-refused
- WHEN `H=$PWD; C=$(mktemp -d)/h; git clone -q "$H" "$C" && uv sync -q --frozen --project "$C"; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && cd $T && "$C"/bin/factory init --repo-name demo >$T/init.out 2>&1; echo "init=$?"; echo '# local edit' >> "$C"/factory/__init__.py; printf '# demo\n\nDo the thing.\n' > $T/r.md; "$C"/bin/factory ticket new --file $T/r.md >/dev/null 2>$T/err; echo "exit=$? tickets=$(ls $T/.factory/state/tickets 2>/dev/null | wc -l | tr -d ' ') names=$(grep -c 'factory/__init__.py' $T/err)"`
- THEN it prints `init=0` then `exit=2 tickets=0 names=1`

=== specs/repo-layout/spec.md
## ADDED Requirements

### Requirement: documents-say-what-they-are
The design doc SHALL be `docs/design.md` with its changelog split out verbatim into `docs/changelog.md`, the prompt copies SHALL be under `docs/prompts/` byte-identical, and the working documents for building the factory SHALL be under `dev/`; the old paths MUST NOT be tracked.

#### Scenario: docs-moved-and-split
- WHEN `for p in docs/design.md docs/changelog.md docs/prompts/00-preamble.md dev/build-harness.spec.md dev/build-harness.plan.md dev/P0-intake-skeleton.md dev/issues.md; do git ls-files --error-unmatch "$p" >/dev/null 2>&1 || echo "missing $p"; done; echo "old_tracked=$(git ls-files docs/spec-factory.md specs plans issues prompts | wc -l | tr -d ' ')"`
- THEN it prints only `old_tracked=0`

#### Scenario: changelog-moved-verbatim
- GIVEN `BASE` is the parent's recorded base commit (the parent-close input `base`); on today's checkout, `export BASE=$(git rev-parse main)`
- WHEN `old() { git show "$BASE:docs/spec-factory.md" | awk '/^## Changelog/{f=1} /^## Appendix/{f=0} f' | grep '^[0-9][0-9]*\. '; }; diff <(old) <(grep '^[0-9][0-9]*\. ' docs/changelog.md 2>/dev/null | head -n "$(old | wc -l)") >/dev/null && echo SAME || echo DIFFERENT; echo "declined=$(grep -c '^Declined: a dedicated merge agent' docs/changelog.md 2>/dev/null) numbering=$(grep '^[0-9][0-9]*\. ' docs/changelog.md 2>/dev/null | awk -F. '$1!=NR{g=1} END{print (NR==0?"NONE":(g?"GAP":"CONTIGUOUS"))}') in_design=$(grep -c '^## Changelog' docs/design.md 2>/dev/null)"`
- THEN it prints `SAME` then `declined=1 numbering=CONTIGUOUS in_design=0`

#### Scenario: design-text-kept
- GIVEN `BASE` as in changelog-moved-verbatim
- WHEN `comm -23 <(git show "$BASE:docs/spec-factory.md" | awk '/^## Changelog/{f=1} /^## Appendix/{f=0} !f' | sort -u) <(sort -u docs/design.md 2>/dev/null) | grep -v -e '^\*\*Role-context block\.\*\*' -e '^| 8 | Guardrail and protected paths' | wc -l | tr -d ' '`
- THEN it prints `0`: every line of the old doc outside its Changelog is still in `docs/design.md`, except the two lines part F rewrites

#### Scenario: prompt-copies-moved-unchanged
- GIVEN `BASE` as in changelog-moved-verbatim
- WHEN `c=0; n=0; for f in $(git ls-tree --name-only "$BASE" prompts/); do n=$((n+1)); git show "$BASE:$f" | cmp -s - "docs/$f" || c=$((c+1)); done; v=$(awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/design.md 2>/dev/null | cmp -s - docs/prompts/02-spec-writer.md && echo VERBATIM || echo DRIFT); echo "changed=$c of $n $v"`
- THEN it prints `changed=0 of 10 VERBATIM`

### Requirement: no-stale-references
The live documents, the instance's config and briefing, the agent templates and the harness code MUST NOT name a moved or removed path.

#### Scenario: no-old-paths-in-live-files
- WHEN `git grep -n -e 'docs/spec-factory\.md' -e 'specs/build-harness\.md' -e 'plans/build-harness\.md' -e 'plans/P0-intake-skeleton\.md' -e 'issues/README\.md' -e 'HARNESS_PIN' -e 'intake/setup\.sh' -e '[^/a-z_]prompts/' -e '^prompts/' -- README.md docs dev .factory/instance.yaml .factory/context.md agents factory >/dev/null; echo "exit=$?"`
- THEN it prints `exit=1` (no match)

### Requirement: install-documented
`README.md` SHALL state how to install the harness and start an instance, and where each kind of file lives.

#### Scenario: readme-has-install-and-layout
- WHEN `for s in 'git clone' 'uv sync' 'factory init' 'factory paths' '.factory/' 'dev/' 'docs/prompts/'; do grep -qF -- "$s" README.md || echo "missing: $s"; done; echo checked`
- THEN it prints only `checked`

### Requirement: design-doc-names-the-instance
The design doc SHALL say where the role-context block is kept and how a multi-repo harness picks the instance, SHALL make the harness code a protected path in its own repo, and its changelog SHALL record the change.

#### Scenario: design-doc-instance-text
- WHEN `echo "kept=$(grep '^\*\*Role-context block\.\*\*' docs/design.md 2>/dev/null | grep -c '\.factory/context\.md') open=$(grep -c 'are not fixed here' docs/design.md 2>/dev/null) piece8=$(grep '^| 8 |' docs/design.md 2>/dev/null | grep -c 'harness code') logged=$(grep '^[0-9][0-9]*\. ' docs/changelog.md 2>/dev/null | grep -c 'harness\.lock')"`
- THEN it prints `kept=1 open=0 piece8=1 logged=1`

### Requirement: build-spec-render-reads-design-doc
The build spec SHALL say that `factory render` reads `docs/design.md` and that the repo name and protected paths come from each instance's `instance.yaml`, outside its historical Responses.

#### Scenario: build-spec-render-paths
- WHEN `echo "stale=$(awk '/^## Responses/{exit} {print}' dev/build-harness.spec.md 2>/dev/null | grep -c 'factory/prompts/design-doc\.md') new=$(grep -c 'docs/design\.md' dev/build-harness.spec.md 2>/dev/null) d8=$(grep '^| D8 |' dev/build-harness.spec.md 2>/dev/null | grep -c 'instance\.yaml')"`
- THEN it prints `stale=0 new=N d8=1` with N ≥ 3

=== specs/self-instance/spec.md
## ADDED Requirements

### Requirement: intake-reduced-to-live-store
At parent close, nothing SHALL remain tracked under `intake/` except the live store `intake/state/` and `intake/.gitignore`, which the post-close operator step moves.

#### Scenario: intake-holds-only-live-store
- WHEN `echo "left=$(git ls-files intake | grep -v -e '^intake/state/' -e '^intake/\.gitignore$' | wc -l | tr -d ' ')"`
- THEN it prints `left=0`

### Requirement: closed-records-kept
Every file of the closed green-pilot store and of the operator answers MUST still be tracked, byte-identical, outside `intake/`.

#### Scenario: pilot-store-and-answers-kept-byte-identical
- GIVEN `BASE` as in changelog-moved-verbatim
- WHEN `A=$(mktemp); B=$(mktemp); git ls-tree -r "$BASE" -- intake/green-pilot intake/answers | awk '{print $3}' | sort -u >$A; git ls-tree -r HEAD | awk -F'\t' '$2 !~ /^intake\//{print $1}' | awk '{print $3}' | sort -u >$B; echo "kept=$(( $(wc -l <$A) - $(comm -23 $A $B | wc -l) )) of $(wc -l <$A | tr -d ' ')"`
- THEN it prints `kept=134 of 134` (both numbers equal; 134 distinct contents on `main` today)

### Requirement: instance-b-runs-on-moved-harness
This repository SHALL be its own instance: `bin/factory`, run from its root, MUST find `.factory/`, pass the lock and open every ticket in its store.

#### Scenario: instance-b-opens-every-ticket
- WHEN `S=$(bin/factory paths 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin)["state"])' 2>/dev/null); n=0; bad=0; for f in "$S"/tickets/T-*.yaml; do [ -f "$f" ] || continue; n=$((n+1)); bin/factory ticket show "$(basename "$f" .yaml)" >/dev/null 2>&1 || bad=$((bad+1)); done; echo "tickets=$n failed=$bad"`
- THEN it prints `tickets=N failed=0` with N ≥ 12

### Requirement: instance-b-gates-and-protects-harness
This instance's gate SHALL run the moved suite as well as the whitespace check, its protected paths SHALL include the harness code and the prompt copies, and its briefing SHALL describe the new layout.

#### Scenario: instance-b-config
- WHEN `uv run --frozen python -c "import yaml; c=yaml.safe_load(open('.factory/instance.yaml')); g=c['gate_commands']; p=[x for v in c['protected_paths'].values() for x in v]; print(any('pytest' in x and 'tests/factory' in x for x in g), 'git diff --check main...HEAD' in g, all(x in p for x in ('factory/**', 'bin/factory', 'agents/**', 'docs/prompts/**')))" 2>/dev/null || echo "no instance config"; echo "context=$(grep -c -e 'docs/design\.md' -e 'tests/factory' .factory/context.md 2>/dev/null)"`
- THEN it prints `True True True` then `context=N` with N ≥ 2

### Requirement: green-keeps-its-harness
This change MUST NOT remove green's in-tree harness, which keeps running until instance A's own ticket.

#### Scenario: green-harness-still-present
- WHEN `git -C ~/dev/nanobot-upstream cat-file -e feat/lionbot-v3:factory/cli.py && git -C ~/dev/nanobot-upstream cat-file -e feat/lionbot-v3:.claude/agents/factory-triage.md && echo "green keeps its harness"`
- THEN it prints `green keeps its harness`

### Requirement: no-whitespace-errors
The parent's combined change MUST add no whitespace errors.

#### Scenario: whitespace-clean
- GIVEN `BASE` as in changelog-moved-verbatim
- WHEN `git diff --check "$BASE" HEAD; echo "exit=$?"`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Run every command with bash from the root of the `~/dev/spec-factory` checkout under test, which at parent close is `main`. `~/dev/nanobot-upstream` and `uv` must be on the machine. "Today" means `main` at `f082708`, with `BASE=$(git rev-parse main)`. Every today output below was observed on this checkout. The expected results for B and C are design targets; no code for them exists yet.

- harness-files-in-repo → NEW. Today it prints ten `missing …` lines (from `factory/cli.py` to `tests/factory/test_p0_cli.py`), then `agents=0 green_only=0`.
- harness-history-carried → NEW. Today it prints `24`, because none of green's harness commits are here. In the scratch import trial it printed `0`.
- harness-suite-passes-after-uv-sync → NEW. Today `uv sync` fails (`No pyproject.toml found`) and it prints `sync=2`, then `no tests ran in 0.00s`. Green's suite gave `70 passed` in a scratch copy.
- role-prompt-text-unchanged → NEW. Today it prints `changed=14 of 14`, because none of the files exist here. After the import trial it printed `changed=1 of 14`; the one is the preamble, which part B replaces.
- init-creates-instance-in-throwaway-target → NEW. Today it prints `init=127` (`bin/factory` does not exist), then `instance=[] agents=0 restart=0`.
- store-command-from-subdirectory-uses-target-instance → NEW. Today it prints `init=127`, then `new=127 tickets=[] harness_changes=0`.
- command-outside-any-instance-refused → NEW. Today it prints `exit=127 created=0 names_instance=0`.
- factory-instance-override-from-elsewhere → NEW. Today it prints `init=127`, then `found=0`.
- composed-input-opens-with-instance-context → NEW. Today it prints `init=127`, then `first=[]`.
- run-system-prompt-names-instance → NEW. Today it prints `init=127`, then `line1=[] placeholders= protects_instance=`.
- paths-name-harness-workflows-and-instance → NEW. Today it prints `init=127`, then `no paths`.
- lock-mismatch-refused → NEW. Today it prints `init=127`, then `exit=127 tickets=0 hint=0`.
- accept-current-revision-rewrites-lock → NEW. Today it prints `init=127`, then `exit=127 lock_is_rev=no logged=0`.
- accept-other-revision-refused → NEW. Today it prints `init=127`, then `exit=127 lock= tickets=0`.
- throwaway-store-ignores-lock → NEW. Today it prints `init=127`, then `exit=127 ticket=[]`.
- dirty-harness-refused → NEW (added at the gate; not run there). Today `bin/factory` does not exist in the clone, so it is expected to print `init=127`, then `exit=127 tickets=0 names=0`.
- docs-moved-and-split → NEW. Today it prints seven `missing …` lines, then `old_tracked=15`. In the scratch split trial it printed `old_tracked=0`.
- changelog-moved-verbatim → NEW. Today it prints `DIFFERENT`, then `declined= numbering=NONE in_design=`. In the trial it printed `SAME`, then `declined=1 numbering=CONTIGUOUS in_design=0`.
- design-text-kept → NEW. Today it prints `570`, because `docs/design.md` does not exist. In the trial it printed `0`.
- prompt-copies-moved-unchanged → NEW. Today it prints `changed=10 of 10 DRIFT`. In the trial it printed `changed=0 of 10 VERBATIM`.
- no-old-paths-in-live-files → NEW. Today it prints `exit=0`: `README.md` lines 5, 6, 9 and 11 match.
- readme-has-install-and-layout → NEW. Today it prints seven `missing: …` lines, then `checked`.
- design-doc-instance-text → NEW. Today it prints `kept=0 open= piece8=0 logged=0`.
- build-spec-render-paths → NEW. Today it prints `stale=0 new= d8=0`, because the file is not at `dev/`. The `stale=0` there is vacuous: `awk` read no file.
- intake-holds-only-live-store → NEW. Today it prints `left=167`.
- pilot-store-and-answers-kept-byte-identical → NEW. Today it prints `kept=0 of 134`, because every one of those files is tracked only under `intake/`.
- instance-b-opens-every-ticket → NEW. Today it prints `tickets=0 failed=0`, because `bin/factory` does not exist here and no store is found. The same tickets open today through the old copy: `FACTORY_STATE=$PWD/intake/state intake/harness/bin/factory ticket show T-000N` succeeds for all twelve.
- instance-b-config → NEW. Today it prints `no instance config`, then `context=`.
- green-harness-still-present → REGRESSION. It prints `green keeps its harness` today and must still do so after the change.
- whitespace-clean → REGRESSION. It prints `exit=0` today (an empty range) and must still do so over the whole parent.

How verified:
- I ran every WHEN above verbatim on this checkout for the "today" results.
- The A and D results marked "trial" came from a scratch clone of this repo:
  - for A, with green's harness imported by `git filter-repo` from a scratch clone of green;
  - for D, with the document moves done by `git mv` plus an `awk` split of the Changelog.
- Green's suite was run in a scratch `git archive` copy with green's venv, three times: with green's config, with this repo's config, and with this repo's config plus `environment_files: ["uv.lock"]`.
- Nothing was written in `~/dev/nanobot-upstream`.
- I did not build B, C, E or F. Their scenarios are checked against today's failure only, and their expected results are the design above.
- Round 2: `main` is still `f082708` and green is still at G (`git rev-parse main`; `git -C ~/dev/nanobot-upstream log -1 --format='%h %s' feat/lionbot-v3`). I re-ran harness-history-carried (`24`), intake-holds-only-live-store (`left=167`), pilot-store-and-answers-kept-byte-identical (`kept=0 of 134`), no-old-paths-in-live-files (matches on `README.md` lines 5, 6, 9, 11) and whitespace-clean (`exit=0`), and `git -C ~/dev/nanobot-upstream log G..feat/lionbot-v3 -- factory/prompts .claude/agents` (empty). No acceptance item changed in this round.

## Responses

- [BLOCKING] Problem, first paragraph → FIXED. A new second paragraph says it outright: the harness can serve only the repo it lives in; the operator who runs it on this repo keeps a hand-made copy that drifts, and every new project would have to make the same copy. The later "This affects two groups" list stays as the summary.
- [SHOULD-FIX] design.md B.2, repo root with `FACTORY_INSTANCE` → FIXED. B.2 now says the repo root is the parent of the instance directory, whatever it is named, with `FACTORY_REPO` still overriding. Following that rule, the fixture instance would make the repo root `tests/factory/fixtures/`. `compose` reads the repo root too (Evidence), and every imported test except the shepherd ones relies on the default. So B.9's conftest now also sets `FACTORY_REPO` to the harness checkout when it is unset, which is exactly today's default. The shepherd tests still set their own `FACTORY_REPO` per subprocess. Added under Decisions.
- [NIT] E.1 carries `request_dir` → FIXED. E.1 drops the key, with the reason, and Decisions says so. Checked: `grep -rn request_dir factory/*.py factory/workflows/` on green prints nothing. The key is on line 6 of `intake/instance/config.yaml`, not line 3.
- [NIT] lock at parent close depends on no later harness-path merge → FIXED. E.3 now says any sub-ticket that touches harness paths and merges after E branches also rewrites `.factory/harness.lock`. Risk ("Lock behaviour after close") repeats it for the planner.

Out-of-scope observations:
- `main` moved twice during this run, to `b722abd` (#20 filed, "after #19") and then `f082708` (#13 and #14 "fold in" to #21, "after #19"). Neither touched the files this spec changes, except `issues/README.md` gaining rows. Part D moves that file as-is.
- `intake/requests/19_harness_home.md` (this request's file) is untracked. The post-close operator step has to move or delete it.
- The store's run records (`meta.yaml`, `input.md`) hold absolute `intake/state/...` paths. After the post-close move they stay as historical text and no command reads them back.
- `factory init` now has a third meaning in the build spec: part A's bare-repo seeding (`dev/build-harness.spec.md`, "factory init: creates ~/factory-remote/nanobot.git"). Part F does not reconcile it. A later build-spec pass should.
- Even after this change there are three prompt texts: `docs/design.md`, `docs/prompts/` (verbatim), and `factory/prompts/<role>.md` (placeholders filled, plus the spec-writer and triage addendum). With all three in one repo a `render --check` becomes possible, but it is not built here.

## PR description (the implementer's output)

Sub-ticket: T-0012.3 (`intake/state/specs/T-0012.3/subticket.md`; parent `intake/state/specs/T-0012/v3.md`). Branch `factory/T-0012.3`, one commit `f5d820346e2ed3edd2b8d160f280dc02d74d57f1` on base `51ea76c`.

## What changed (per lettered part)

**B.1 Resolver.** New `factory/instance.py` (117 lines).
- `find()` takes `FACTORY_INSTANCE` if it is set and holds `instance.yaml`. Otherwise it walks up from the caller's directory to the nearest `.factory/instance.yaml`.
- `bin/factory` now runs `export FACTORY_CWD="$PWD"` before its `cd "$HERE"`, so the package knows the caller's directory. Without that variable it falls back to `os.getcwd()`.
- `require()` raises `Refused` with `no .factory/instance.yaml found from <cwd>; run factory init --repo-name NAME, or set FACTORY_INSTANCE`.
- `cli.main` runs `store.load_config()` (which now calls the resolver) inside the `try`, so the refusal exits 2 before anything is written. `init` and `paths` skip that step.
- There is no fallback: `store.REPO_ROOT` and `store.CONFIG_PATH` are deleted.

**B.2 Where things come from.**
- `instance.load_config` reads `<instance>/instance.yaml`.
- `instance.repo_root` is `FACTORY_REPO`, else the instance directory's parent. `gitops.repo_root` now delegates to it; its docstring is updated.
- `store.state_root` is `FACTORY_STATE`, else `<repo root>/<state_dir>`.
- `FACTORY_INTEGRATION_BRANCH` is unchanged.

**B.3 Briefing.** `compose.compose` opens `input.md` with `<instance>/context.md`. `factory/prompts/context.md` is deleted.

**B.4 Preamble.**
- `factory/prompts/preamble.md` is now a byte copy of `docs/prompts/00-preamble.md`.
- `run start` calls `instance.fill_preamble`. It replaces `{repo name}` with `repo_name`, and replaces the exact line `  {auth, payments, migrations, infra, public API, dependencies}` with `  <class> (<glob>, <glob>), …` built from `protected_paths`.
- The seven role prompts are untouched.

**B.5 `factory init [--repo-name NAME]`** (`cli.init_cmd`).
- It exits 2 outside a git work tree. The instance is `FACTORY_INSTANCE` if set, else `.factory/` at the git top level.
- If `instance.yaml` is missing, it needs `--repo-name` (otherwise exit 2, nothing written). It then writes `instance.yaml` from the new `factory/instance.template.yaml`, filling `repo_name` and `harness` (the absolute path of the running checkout).
- Then, only when the store in use is the instance's own (see gap 1), it creates whichever of these is missing:
  - `context.md`, from the new `factory/context.template.md`;
  - `harness.lock`, holding the C.1 revision;
  - `<repo root>/.claude/agents/factory-*.md`, copied from `agents/`. If any agent file is written, it prints `restart the session so the agents register` to stderr.
- After that it does today's store init (`specstore.init`), plus the store `.gitignore` (`store.ensure_gitignore`).
- Idempotent: it logs `store.initialised` only when it wrote something.
- The template carries today's generic keys, with `integration_branch: null` and `environment_files: []`. It has no `request_dir`.

**B.6 `factory paths`** (`cli.paths_cmd`) prints one JSON object with:
- the absolute paths `harness` (the running checkout), `bin`, `intake_workflow` and `build_workflow`;
- `harness_revision`;
- `instance` and `state`, which are `null` when no instance is found.

It runs no check and writes nothing.

**C.1 only.** `instance.harness_revision()` is `git -C <running checkout> log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock`, and returns None outside git. `init` (lock) and `paths` use it. No lock enforcement (C.2–C.5).

**B.7 Agent pointers.** In `agents/factory-{triage,spec-writer,spec-critic,planner}.md`, the single pointer line is replaced with the spec's text. Nothing else in `agents/` changes.

**B.8 Workflows.** `intake.js` and `build.js` take `instance`.
- When it is given, every store command is prefixed with `FACTORY_INSTANCE=<instance>`.
- `state` is optional. When it is absent, `STATE` is taken from `factory config`'s `state_dir`, which is the absolute store path. If `config` fails, the workflow returns an error.
- `repo` stays the harness checkout. The header comments are updated.

**B.9 Tests.**
- New `tests/factory/conftest.py` sets `FACTORY_INSTANCE` to the new `tests/factory/fixtures/instance/`, and sets `FACTORY_REPO` to the harness checkout unless it is already set.
- The fixture's `instance.yaml` is the template values plus `environment_files: ["uv.lock"]` and `gate_commands: ["git diff --check main...HEAD"]`. It also has a `context.md`.
- New `tests/factory/test_instance.py` has 22 tests.
- Part A's interim `factory/config.yaml` is deleted. Git's rename detection shows it as renamed to the fixture; `--no-renames` shows a delete and an add.

**Also:** the one-line docstring in `factory/__init__.py` named the deleted `factory/config.yaml`; it now names `factory/instance.py` and the template.

## Acceptance results

Run from the worktree, after `uv sync --frozen` (`sync=0`), with `BASE=cdb1c67…` (the parent's recorded `parent_base`).
- **Before** = base `51ea76c`.
- **After** = the working tree before commit, re-run verbatim on head `f5d8203`. The results are the same.

Commands were extracted from the input file by a script, not retyped.

| Criterion | Before | After |
|---|---|---|
| harness-files-in-repo (NEW) | `agents=6 green_only=2` | `agents=6 green_only=0` |
| role-prompt-text-unchanged (NEW) | `changed=1 of 14` | `changed=0 of 14` |
| init-creates-instance-in-throwaway-target (NEW) | `init=2` / `instance=[] agents=0 restart=0` | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` |
| store-command-from-subdirectory-uses-target-instance (NEW) | `init=2` / `new=0 tickets=[] harness_changes=4` | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` |
| command-outside-any-instance-refused (NEW) | `exit=0 created=0 names_instance=0` | `exit=2 created=0 names_instance=1` |
| factory-instance-override-from-elsewhere (NEW) | `init=2` / `found=0` | `init=0` / `found=1` |
| composed-input-opens-with-instance-context (NEW) | `init=2` / `first=[]` | `init=0` / `first=[CTX-MARKER for demo]` |
| run-system-prompt-names-instance (NEW) | `init=2` / `line1=[] placeholders= protects_instance=` | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` |
| paths-name-harness-workflows-and-instance (NEW) | `init=2` / `no paths` | `init=0` / `True True True True` |
| init-refusals-and-idempotence (NEW) | `outside_git=2` / `no_name=0` / `again=0 same=yes` (`find: .factory: No such file…`: nothing was created) | `outside_git=2` / `no_name=2` / `again=0 same=yes` |
| agent-pointer-replaced (NEW) | four lines `old=1 new=0` | four lines `old=0 new=1` |
| workflows-take-instance (NEW) | `intake 0` / `build 0` | `intake 2` / `build 1` |
| no-old-paths, documents and harness (NEW) | `exit=0` (`factory/config.yaml` 3 lines, `factory/prompts/context.md` 6, `factory/prompts/preamble.md:38`) | `exit=1` |
| harness-history-carried (REGRESSION) | `0` | `0` |
| harness-suite-passes-after-uv-sync (REGRESSION) | `sync=0`, `70 passed in 69.68s` | `sync=0`, `92 passed in 71.28s (0:01:11)` |
| docs-moved-and-split (REGRESSION) | `old_tracked=0` | `old_tracked=0` |
| prompt-copies-moved-unchanged (REGRESSION) | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` |
| green-harness-still-present (REGRESSION) | `green keeps its harness` | `green keeps its harness` |
| whitespace, sub-ticket diff (REGRESSION) | `exit=0` | `exit=0` |

Every NEW criterion failed before and passes after. Every REGRESSION passed before and after.

**Gates on head `f5d8203`, run exactly as written from the worktree:**
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` gave `92 passed in 81.46s` (70 imported + 22 new).
- `git status --porcelain` was empty afterwards, so the suite and the acceptance runs wrote nothing into the checkout.

**Before merge: every imported test runs on a throwaway store.** `grep -n 'str(BIN)' tests/factory/test_*.py` finds five subprocess helpers: `test_p0_cli.py:22`, `test_results_commit.py:37`, `test_shepherd.py:629`, `test_spec_store.py:20` and `test_subtickets.py:72`. Each builds its env with `"FACTORY_STATE": str(<tmp store>)`. `test_killed_checker.py` imports `built_to_implementer` from `test_shepherd` and has no subprocess helper of its own.

**Workflows (B.8):** the check here is structural only, plus a stub smoke run that is not a test in the repo.
- I wrapped each script as a function and ran it in node 24 with a fake `agent`. The clerk commands came out as `FACTORY_INSTANCE=/T/.factory /H/bin/factory config` (with `instance`), `FACTORY_STATE=/S /H/bin/factory …` (with `state`) and `FACTORY_INSTANCE=… FACTORY_REPO=/X …` (build with `target`).
- With only `instance` given, the role prompt read `/T/.factory/state/runs/run-0001-x/system-prompt.txt`, which is `STATE` taken from `config`.
- `node --check` passes on both scripts.
- End-to-end behaviour is exercised only by operator step 3 after close. I am not claiming more than that.

## Tests added/changed

- **Existing tests:** none changed. `git diff --name-status --no-renames main...HEAD -- tests/` lists only `A` entries. Nothing under `docs/` changed, and none of the seven role prompts changed.
- **`tests/factory/conftest.py` (new):** B.9, as specified.
- **`tests/factory/fixtures/instance/{instance.yaml,context.md}` (new):** B.9.
- **`tests/factory/test_instance.py` (new, 22 tests).** It covers:
  - `init`:
    - it creates the instance at the git top level from a nested subdirectory;
    - `instance.yaml` matches the template's keys and values;
    - a repo name with YAML special characters round-trips;
    - it refuses outside git, and refuses without `--repo-name`, writing nothing;
    - it is idempotent byte for byte, and recreates only the missing pieces;
    - on a throwaway store it initialises only that store;
    - under the suite's conftest env it writes nothing into the fixture or the harness checkout;
    - a nested repo gets its own instance.
  - The resolver:
    - a store command from a subdirectory uses the target's instance;
    - outside any instance it is refused with the exact message for `ticket show`, `ticket new` and `config`, and nothing is written;
    - `FACTORY_STATE` alone does not stand in for an instance;
    - the `FACTORY_INSTANCE` override works, and is refused when the directory has no `instance.yaml`;
    - the repo root is the instance's parent, and `FACTORY_REPO` and `FACTORY_STATE` override it and the store.
  - Compose: the input opens with the instance's `context.md`.
  - The preamble:
    - the system prompt equals the design block except the two filled lines, with the role prompt appended verbatim;
    - with several classes, the protected-path line lists every one;
    - `factory/prompts/preamble.md` is byte-identical to the design copy, and part A's overlay is gone.
  - `paths`, inside an instance and outside one, with the revision equal to `git log`.
  - The conftest points the suite at the fixture.
- **Watched fail:** I ran the new file against a scratch `git archive` copy of base `51ea76c` that had the conftest, fixture and templates added. The result was `9 failed, 2 passed, 10 errors` (the errors are the `target` fixture's `init`, which failed). The two that already pass on the old code are guard tests: suite-init-writes-nothing-into-harness and conftest-points-at-fixture. They pin the isolation, not new behaviour.

## Known gaps and uncertainties

1. **A reading the spec does not state: `init` writes the instance's pieces only when the store in use is the instance's own.** Those pieces are `context.md`, `harness.lock` and `.claude/agents/`. "Own store" uses C.2's condition: `FACTORY_STATE` unset, or resolving to `state_dir`.
   - Why: the imported tests run `factory init` with the conftest's `FACTORY_INSTANCE` (the fixture) and `FACTORY_REPO` (the harness checkout). A literal "today's init plus any missing pieces" would write `harness.lock` into `tests/factory/fixtures/instance/` and `.claude/agents/` into the harness checkout on every suite run.
   - With the reading, a throwaway-store `init` does exactly today's store init.
   - Pinned by `test_init_on_a_throwaway_store_initialises_only_that_store` and `test_the_suite_conftest_init_writes_nothing_into_the_harness`.
2. **`init` picks its instance from `FACTORY_INSTANCE`, else `<git top level>/.factory`, not by the walk-up.** This follows B.5 ("works at the git top level"), and it means a repo nested under another instance gets its own. Honouring `FACTORY_INSTANCE` is needed for the imported tests. If `FACTORY_INSTANCE` names a directory with no `instance.yaml`, `init --repo-name` creates it there.
3. **Today's `init` logged `store.initialised` on every call. It now logs only when something was written.** The scenario's `again=0 same=yes` checksums every file under `.factory/`, including the store's log, so it requires this. No existing test asserts on that event.
4. **`init` now writes the store's `.gitignore`** (B.5 lists it) and reports it as `".gitignore"` in `written`. Its JSON gains `instance`, `state`, `created` and `agents`.
5. **The restart line goes to stderr, so stdout keeps one JSON object.** The scenario counts it over stdout and stderr together (`restart=1`). `paths` JSON also carries `"ok": true`, which follows the CLI's convention.
6. **Choices the spec leaves open:**
   - `FACTORY_CWD` is the name I chose for the variable that hands over the caller's directory.
   - An empty `protected_paths` renders the line as `  none`.
   - `repo_name` and `harness` are written into the template as JSON-quoted strings, which YAML reads back exactly (tested with `:`, `"` and `#`). The fixture's `harness` is `null`; nothing in B reads that key.
7. **`factory/context.template.md` is my own wording.** It is a TODO stub listing what the briefing must state, ending with a generic "Output:" paragraph adapted from green's briefing. A reviewer may want different text.
8. **The workflows were checked only as described above.** They were not run end to end.
9. **Process disclosure, protected path.** My first baseline run of the acceptance commands on the old code wrote into this worktree's tracked copy of `intake/state/`: the old harness resolved its store next to its own code. It created `T-0013`, appended to `log/2026-10.jsonl` and `requests/index.yaml`, and added `openspec/` and `decisions.md`.
   - I reverted exactly those paths (`git checkout --` on the two files, `rm` on the four untracked paths) before making any change, and `git status` was clean afterwards.
   - The live store at `~/dev/spec-factory/intake/state` was not touched: its tickets end at `T-0012.yaml`.
   - That was the "today" failure mode `harness_changes=4`. After the change the same commands write only into their temp targets.

## Out-of-scope observations

- `ticket new --file` and `status parse` resolve a relative path against the harness checkout, because `bin/factory` changes into it. This is pre-existing, but now that operators run from target repos it will surprise them. Absolute paths work.
- `tests/factory/conftest.py` sets `FACTORY_REPO` only if it is unset, as B.9 specifies. When the suite runs as a gate from a process that already exports `FACTORY_REPO` (build.js with `target`), the imported tests inherit it. This is relevant to T-0012.6, which puts the suite in instance B's gate.
- `README.md` and `dev/build-harness.spec.md` still describe the old config location. They are rewritten in E and F.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates were run verbatim on head f5d8203 and printed the expected results. The two `init` readings (gaps 1–2) are the main thing for review.
ESCALATIONS: none

## Diff `51ea76c94740462b299941d40bf8a431d07ee9ba...f5d820346e2ed3edd2b8d160f280dc02d74d57f1`

diff --git a/agents/factory-planner.md b/agents/factory-planner.md
index cb8249b..1e717ab 100644
--- a/agents/factory-planner.md
+++ b/agents/factory-planner.md
@@ -5,7 +5,7 @@ model: opus
 tools: Read, Grep, Glob, Bash, Write
 ---
 
-Read `factory/prompts/preamble.md` before anything else; it is the top of your system prompt.
+Read `system-prompt.txt` in the run directory that holds your input file before anything else; its preamble is the top of your system prompt.
 
 ROLE: Planner. You turn one human-approved spec into an ordered set of
 sub-tickets. If the spec already fits one PR, output a single sub-ticket.
diff --git a/agents/factory-spec-critic.md b/agents/factory-spec-critic.md
index 5bd8a76..204a99d 100644
--- a/agents/factory-spec-critic.md
+++ b/agents/factory-spec-critic.md
@@ -5,7 +5,7 @@ model: fable
 tools: Read, Grep, Glob, Bash, Write
 ---
 
-Read `factory/prompts/preamble.md` before anything else; it is the top of your system prompt.
+Read `system-prompt.txt` in the run directory that holds your input file before anything else; its preamble is the top of your system prompt.
 
 ROLE: Spec critic. You decide whether a spec is safe to hand to an
 implementer. You see the spec and the repo, never the writer's reasoning.
diff --git a/agents/factory-spec-writer.md b/agents/factory-spec-writer.md
index fcaa8c5..b2db1e5 100644
--- a/agents/factory-spec-writer.md
+++ b/agents/factory-spec-writer.md
@@ -5,7 +5,7 @@ model: opus
 tools: Read, Grep, Glob, Bash, Write
 ---
 
-Read `factory/prompts/preamble.md` before anything else; it is the top of your system prompt.
+Read `system-prompt.txt` in the run directory that holds your input file before anything else; its preamble is the top of your system prompt.
 
 ROLE: Spec writer. You turn one accepted ticket into a spec that an
 implementer can execute without guessing, and a verifier can check
diff --git a/agents/factory-triage.md b/agents/factory-triage.md
index 3a8b8d7..86fc614 100644
--- a/agents/factory-triage.md
+++ b/agents/factory-triage.md
@@ -5,7 +5,7 @@ model: opus
 tools: Read, Grep, Glob, Bash, Write
 ---
 
-Read `factory/prompts/preamble.md` before anything else; it is the top of your system prompt.
+Read `system-prompt.txt` in the run directory that holds your input file before anything else; its preamble is the top of your system prompt.
 
 ROLE: Triage. You turn raw requests (issues, Slack threads, bug reports,
 ideas) into candidate tickets, or you reject or route them.
diff --git a/bin/factory b/bin/factory
index f979031..1297df1 100755
--- a/bin/factory
+++ b/bin/factory
@@ -4,5 +4,8 @@ set -euo pipefail
 HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
 PY="$HERE/.venv/bin/python"
 [[ -x "$PY" ]] || PY="python3"
+# The package finds the target's instance from the caller's directory (factory/instance.py), but
+# runs from the harness checkout: hand the caller's directory over before changing into it.
+export FACTORY_CWD="$PWD"
 cd "$HERE"
 exec "$PY" -m factory "$@"
diff --git a/factory/__init__.py b/factory/__init__.py
index 44f886c..d129c99 100644
--- a/factory/__init__.py
+++ b/factory/__init__.py
@@ -1 +1 @@
-"""Spec factory harness, P0 intake skeleton. See factory/config.yaml and factory/workflows/intake.js."""
+"""Spec factory harness, P0 intake skeleton. See factory/instance.py, factory/instance.template.yaml and factory/workflows/intake.js."""
diff --git a/factory/cli.py b/factory/cli.py
index f9f74d7..e34ca90 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -9,14 +9,16 @@ import argparse
 import datetime as dt
 import getpass
 import json
+import os
 import re
 import shutil
+import subprocess
 import sys
 from pathlib import Path
 
 import yaml
 
-from factory import compose, gitops, specstore, status, store, subtickets
+from factory import compose, gitops, instance, specstore, status, store, subtickets
 from factory.store import Refused
 
 ROLES = ("triage", "spec_writer", "critic", "planner", "implementer", "reviewer", "verifier")
@@ -190,7 +192,8 @@ def run_start(a, root, cfg):
         _start_build_run(root, cfg, t, meta, d, parent_close)
     store.write_yaml(d / "meta.yaml", meta)
     prompt_name = a.role
-    sysp = (PROMPTS / "preamble.md").read_text(encoding="utf-8").rstrip() + "\n\n" + (PROMPTS / f"{prompt_name}.md").read_text(encoding="utf-8")
+    preamble = instance.fill_preamble((PROMPTS / "preamble.md").read_text(encoding="utf-8"), cfg)
+    sysp = preamble.rstrip() + "\n\n" + (PROMPTS / f"{prompt_name}.md").read_text(encoding="utf-8")
     store.write_text(d / "system-prompt.txt", sysp)
     t["in_flight"].append(rid)
     store.save_ticket(root, t)
@@ -713,10 +716,90 @@ def resolve(a, root, cfg):
 
 # ----- spec store (doc §Harness, Spec store; part K) ----------------------------------
 
-def init_cmd(a, root, cfg):
+def _git_toplevel(cwd: Path) -> Path:
+    cp = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
+    if cp.returncode != 0 or not cp.stdout.strip():
+        raise Refused(f"factory init: {cwd} is not inside a git work tree")
+    return Path(cp.stdout.strip()).resolve()
+
+
+def _new_instance_yaml(repo_name: str) -> str:
+    """factory/instance.template.yaml with the per-instance values filled (design B.5)."""
+    text = instance.INSTANCE_TEMPLATE.read_text(encoding="utf-8")
+    for key, val in (("__REPO_NAME__", repo_name), ("__HARNESS__", str(instance.HARNESS))):
+        if key not in text:
+            raise Refused(f"{instance.INSTANCE_TEMPLATE} has no {key}")
+        text = text.replace(key, json.dumps(val, ensure_ascii=False))
+    return text
+
+
+def _revision() -> str:
+    rev = instance.harness_revision()
+    if rev is None:
+        raise Refused(f"factory init: cannot read the harness revision of {instance.HARNESS} (not a git checkout?)")
+    return rev
+
+
+def init_cmd(a):
+    """Create whatever of the instance is missing (design B.5); idempotent. The instance is
+    FACTORY_INSTANCE, else `.factory/` at the git top level of the working directory. Its pieces
+    (instance.yaml, context.md, harness.lock, agent files) are written only when the store in use
+    is the instance's own: a run on a throwaway store (FACTORY_STATE elsewhere, as every test
+    does) initialises that store and nothing else."""
+    top = _git_toplevel(instance.caller_cwd())
+    env = os.environ.get("FACTORY_INSTANCE")
+    inst = Path(env).expanduser().resolve() if env else top / instance.DIRNAME
+    created: list[str] = []
+    cfg_path = inst / instance.CONFIG_NAME
+    if not cfg_path.exists():
+        if not a.repo_name:
+            raise Refused(f"factory init: {cfg_path} does not exist; pass --repo-name NAME to create it")
+        _revision()  # refuse before writing anything if the lock cannot be written
+        store.write_text(cfg_path, _new_instance_yaml(a.repo_name))
+        created.append(str(cfg_path))
+    cfg = instance.load_config(inst)
+    root = instance.state_root(inst, cfg)
+    agents: list[str] = []
+    if instance.is_own_store(inst, cfg, root):
+        ctx = inst / "context.md"
+        if not ctx.exists():
+            store.write_text(ctx, instance.CONTEXT_TEMPLATE.read_text(encoding="utf-8"))
+            created.append(str(ctx))
+        lock = inst / "harness.lock"
+        if not lock.exists():
+            store.write_text(lock, _revision() + "\n")
+            created.append(str(lock))
+        dest = instance.repo_root(inst) / ".claude" / "agents"
+        for src in sorted(instance.AGENTS.glob("factory-*.md")):
+            if not (dest / src.name).exists():
+                (dest / src.name).parent.mkdir(parents=True, exist_ok=True)
+                shutil.copyfile(src, dest / src.name)
+                agents.append(str(dest / src.name))
+    had_gitignore = (root / ".gitignore").exists()
+    store.ensure_gitignore(root)
     written = specstore.init(root)
-    store.log_event(root, "store.initialised", files=written)
-    out({"ok": True, "written": written, "active": True})
+    if not had_gitignore:
+        written.insert(0, ".gitignore")
+    if written or created or agents:
+        store.log_event(root, "store.initialised", files=written, instance=created, agents=agents)
+    if agents:
+        print("restart the session so the agents register", file=sys.stderr)
+    out({"ok": True, "written": written, "active": True, "instance": str(inst), "state": str(root),
+         "created": created, "agents": agents})
+
+
+def paths_cmd(a):
+    """Absolute paths a dispatcher needs (design B.6). Runs no lock check and writes nothing."""
+    inst = instance.find()
+    state = None
+    if inst is not None:
+        state = str(instance.state_root(inst, instance.load_config(inst)))
+    h = instance.HARNESS
+    out({"ok": True, "harness": str(h), "bin": str(h / "bin" / "factory"),
+         "intake_workflow": str(h / "factory" / "workflows" / "intake.js"),
+         "build_workflow": str(h / "factory" / "workflows" / "build.js"),
+         "harness_revision": instance.harness_revision(),
+         "instance": str(inst) if inst is not None else None, "state": state})
 
 
 def spec_tasks(a, root, cfg):
@@ -908,7 +991,10 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("id")
     p.set_defaults(fn=merge_cmd)
     p = sp.add_parser("init")
+    p.add_argument("--repo-name")
     p.set_defaults(fn=init_cmd)
+    p = sp.add_parser("paths")
+    p.set_defaults(fn=paths_cmd)
     p = sp.add_parser("archive")
     p.add_argument("id")
     p.set_defaults(fn=archive_cmd)
@@ -950,9 +1036,12 @@ def build_parser() -> argparse.ArgumentParser:
 
 def main(argv: list[str] | None = None) -> int:
     a = build_parser().parse_args(argv)
-    cfg = store.load_config()
-    root = store.state_root(cfg)
     try:
+        if a.cmd in ("init", "paths"):  # exempt from the instance refusal (design B.1)
+            a.fn(a)
+            return 0
+        cfg = store.load_config()  # refused when no instance is found: nothing is written
+        root = store.state_root(cfg)
         a.fn(a, root, cfg)
         return 0
     except Refused as e:
diff --git a/factory/compose.py b/factory/compose.py
index 931eb69..29c8cff 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -6,9 +6,7 @@ from __future__ import annotations
 
 from pathlib import Path
 
-from factory import store
-
-PROMPTS = Path(__file__).resolve().parent / "prompts"
+from factory import instance, store
 
 
 def _runs_for(root: Path, ticket: str, role: str, exclude: str) -> list[str]:
@@ -54,7 +52,7 @@ def gate_commands(cfg: dict) -> list[str]:
 def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]:
     role, run_id, tid = meta["role"], meta["run_id"], t["id"]
     out_path = root / "runs" / run_id / "output.md"
-    parts = [(PROMPTS / "context.md").read_text(encoding="utf-8").rstrip(),
+    parts = [(instance.require() / "context.md").read_text(encoding="utf-8").rstrip(),
              f"\n## Output file\n`{out_path}`\n"]
     sources: list[str] = []
 
diff --git a/factory/context.template.md b/factory/context.template.md
new file mode 100644
index 0000000..4781fc8
--- /dev/null
+++ b/factory/context.template.md
@@ -0,0 +1,21 @@
+## Context for this run (composed by the harness, not part of the request)
+
+TODO: replace this stub with the briefing for this repository. `factory run compose` puts this file,
+`.factory/context.md`, at the top of every role's input, so every agent, author and checker alike,
+reads it first. A wrong briefing misleads all of them at once. State, in a few short paragraphs:
+
+- Which repository this is: its name, where the checkout lives, the integration branch, and what it
+  holds (code, documents, both).
+- How to run things here: the install step, the test command, the lint command, and anything that
+  must not be used. Acceptance commands must be runnable as written from the repo root.
+- Any reference implementation or other checkout an agent may read, and what it must never write
+  (credentials, live config, other repositories).
+- What kind of request to expect, and what counts as requirement versus suggestion in it.
+- How the build half works here: remote or local commits, what the gate commands are for, and
+  files a gate run creates that must never be committed.
+
+Output: write your complete output, in your role's required format and ending with the
+STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
+every role but the implementer that is the only file you may create or modify. The implementer
+also changes files in its own worktree and commits there, and nowhere else. Then return the same
+text as your final message.
diff --git a/factory/gitops.py b/factory/gitops.py
index 6712aa7..99542c9 100644
--- a/factory/gitops.py
+++ b/factory/gitops.py
@@ -2,7 +2,7 @@
 2026-10-02: no remote, no CI; the merge gate is the gate suite plus the two checkers, then a
 local --no-ff merge into the integration branch).
 
-The target repo is `repo_root` (FACTORY_REPO or the checkout this package lives in). Worktrees
+The target repo is `repo_root` (FACTORY_REPO, else the parent of the instance directory). Worktrees
 live under <store>/worktrees/<run or ticket id>. Nothing here pushes.
 """
 from __future__ import annotations
@@ -12,14 +12,11 @@ import subprocess
 import time
 from pathlib import Path
 
-from factory import store
+from factory import instance, store
 
 
 def repo_root(cfg: dict | None = None) -> Path:
-    env = os.environ.get("FACTORY_REPO")
-    if env:
-        return Path(env).expanduser().resolve()
-    return store.REPO_ROOT
+    return instance.repo_root()
 
 
 def integration_branch(cfg: dict, repo: Path) -> str:
diff --git a/factory/instance.py b/factory/instance.py
new file mode 100644
index 0000000..108a1ee
--- /dev/null
+++ b/factory/instance.py
@@ -0,0 +1,117 @@
+"""The instance a command serves: a target repo's `.factory/` directory (design B.1, B.2, C.1).
+
+One harness checkout serves many target repos. Each target carries `.factory/` with
+`instance.yaml` (its config), `context.md` (the role-context block), `harness.lock` and the store.
+
+Resolution, used by store, gitops, compose and cli:
+- FACTORY_INSTANCE, when set, names the instance directory, whatever it is called;
+- otherwise walk up from the caller's working directory to the nearest directory that holds
+  `.factory/instance.yaml`. `bin/factory` changes into the harness checkout before running, so it
+  hands the caller's directory over in FACTORY_CWD;
+- otherwise the command is refused. There is no fallback to the harness checkout.
+
+The repo root is the parent of the instance directory; FACTORY_REPO overrides it. `state_dir` is
+relative to the repo root; FACTORY_STATE overrides it.
+"""
+from __future__ import annotations
+
+import os
+import subprocess
+from pathlib import Path
+
+import yaml
+
+from factory.store import Refused
+
+# The running harness checkout: the one whose bin/factory is executing.
+HARNESS = Path(__file__).resolve().parent.parent
+INSTANCE_TEMPLATE = HARNESS / "factory" / "instance.template.yaml"
+CONTEXT_TEMPLATE = HARNESS / "factory" / "context.template.md"
+AGENTS = HARNESS / "agents"
+# The harness's own code: what the harness revision (C.1) is taken over.
+HARNESS_PATHS = ("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")
+DIRNAME = ".factory"
+CONFIG_NAME = "instance.yaml"
+
+
+def caller_cwd() -> Path:
+    return Path(os.environ.get("FACTORY_CWD") or os.getcwd()).expanduser().resolve()
+
+
+def find() -> Path | None:
+    """The instance directory, or None. FACTORY_INSTANCE wins; then the walk-up."""
+    env = os.environ.get("FACTORY_INSTANCE")
+    if env:
+        p = Path(env).expanduser().resolve()
+        return p if (p / CONFIG_NAME).is_file() else None
+    cwd = caller_cwd()
+    for d in (cwd, *cwd.parents):
+        if (d / DIRNAME / CONFIG_NAME).is_file():
+            return d / DIRNAME
+    return None
+
+
+def not_found_message() -> str:
+    env = os.environ.get("FACTORY_INSTANCE")
+    if env:
+        return f"FACTORY_INSTANCE={env} holds no {CONFIG_NAME}; run factory init --repo-name NAME there, or fix FACTORY_INSTANCE"
+    return f"no {DIRNAME}/{CONFIG_NAME} found from {caller_cwd()}; run factory init --repo-name NAME, or set FACTORY_INSTANCE"
+
+
+def require() -> Path:
+    inst = find()
+    if inst is None:
+        raise Refused(not_found_message())
+    return inst
+
+
+def repo_root(inst: Path | None = None) -> Path:
+    env = os.environ.get("FACTORY_REPO")
+    if env:
+        return Path(env).expanduser().resolve()
+    return (inst or require()).parent
+
+
+def load_config(inst: Path | None = None) -> dict:
+    inst = inst or require()
+    return yaml.safe_load((inst / CONFIG_NAME).read_text(encoding="utf-8"))
+
+
+def own_state_root(inst: Path, cfg: dict) -> Path:
+    """The instance's own store: `state_dir` under the repo root, ignoring FACTORY_STATE."""
+    return (repo_root(inst) / cfg["state_dir"]).resolve()
+
+
+def state_root(inst: Path, cfg: dict) -> Path:
+    env = os.environ.get("FACTORY_STATE")
+    if env:
+        return Path(env).expanduser().resolve()
+    return own_state_root(inst, cfg)
+
+
+def is_own_store(inst: Path, cfg: dict, root: Path) -> bool:
+    """True when the store in use is the instance's own (FACTORY_STATE unset, or naming it)."""
+    return root.resolve() == own_state_root(inst, cfg)
+
+
+def harness_revision(harness: Path = HARNESS) -> str | None:
+    """The last commit that touched the harness's own code (C.1); None outside a git checkout."""
+    cp = subprocess.run(["git", "-C", str(harness), "log", "-1", "--format=%H", "--", *HARNESS_PATHS],
+                        capture_output=True, text=True)
+    rev = cp.stdout.strip()
+    return rev if cp.returncode == 0 and len(rev) == 40 else None
+
+
+PROTECTED_PLACEHOLDER = "  {auth, payments, migrations, infra, public API, dependencies}"
+
+
+def fill_preamble(text: str, cfg: dict) -> str:
+    """The design doc's preamble block with `{repo name}` and the protected-path line filled from
+    the instance (B.4). The line becomes `  <class> (<glob>, <glob>)` per class, joined by `, `."""
+    text = text.replace("{repo name}", str(cfg["repo_name"]))
+    classes = []
+    for cls, globs in (cfg.get("protected_paths") or {}).items():
+        globs = [globs] if isinstance(globs, str) else list(globs or [])
+        classes.append(f"{cls} ({', '.join(globs)})")
+    line = "  " + (", ".join(classes) if classes else "none")
+    return "\n".join(line if ln == PROTECTED_PLACEHOLDER else ln for ln in text.split("\n"))
diff --git a/factory/instance.template.yaml b/factory/instance.template.yaml
new file mode 100644
index 0000000..4452806
--- /dev/null
+++ b/factory/instance.template.yaml
@@ -0,0 +1,64 @@
+# Spec factory instance config: this repo's `.factory/instance.yaml` (design B.2, B.5).
+# `factory init --repo-name NAME` writes it from factory/instance.template.yaml in the harness checkout.
+# The harness reads it from the instance it resolves (FACTORY_INSTANCE, else the nearest
+# `.factory/instance.yaml` above the working directory); nothing falls back to the harness checkout.
+# Fills `{repo name}` in the preamble.
+repo_name: __REPO_NAME__
+# The harness checkout this instance runs with (absolute path); `factory paths` reports the running one.
+harness: __HARNESS__
+# The store, relative to the repo root (the parent of `.factory/`). FACTORY_STATE overrides it.
+state_dir: .factory/state
+# Filled into the preamble's protected-path line at run start as `class (glob, glob), ...`.
+protected_paths:
+  infra: [".factory/instance.yaml", ".factory/harness.lock", ".factory/context.md"]
+# Commands every implementer and verifier runs in the checkout under test, each exactly as written.
+# `{integration}` is replaced with the checkout that has the integration branch.
+gate_commands: []
+placeholders: {rounds: 2, spec_lines: 400, audit_n: 5, retro_min: 3}
+max_rounds: {spec: 2, pr: 2}
+# Build half, local-commit stand-in (operator, 2026-10-02): no remote, no CI. The merge gate is the
+# gate suite on the branch plus the two checkers; then a local --no-ff merge into integration_branch
+# (null = the target repo's current branch). FACTORY_REPO / FACTORY_INTEGRATION_BRANCH override.
+integration_branch: null
+# Untracked files every worktree and checker checkout copies from the integration checkout at each run
+# start, so a branch is tested against the same environment the integration branch runs in (for
+# example a lockfile the target repo git-ignores). A tracked file does not belong here: copying it in
+# would mask the branch's own version.
+environment_files: []
+force_push_allowed: false
+models:
+  triage: opus
+  spec_writer: opus
+  critic: fable
+  planner: opus
+  implementer: opus
+  reviewer: fable
+  verifier: opus
+  retro: fable
+  clerk: haiku
+ready_state:
+  triage: ready-for-triage
+  spec_writer: ready-for-spec-writer
+  critic: ready-for-critic
+  planner: ready-for-planner
+  implementer: ready-for-implementer
+  reviewer: checks-in-flight
+  verifier: checks-in-flight
+# Routing edges (doc §Routing table, both halves, plus the resolution rules). Anything else is refused.
+routing:
+  ready-for-triage: [ready-for-spec-writer, waiting-requester, parked, closed]
+  waiting-requester: [ready-for-triage, closed]
+  ready-for-spec-writer: [ready-for-critic, parked, closed]
+  ready-for-critic: [ready-for-spec-writer, awaiting-spec-gate, parked, closed]
+  awaiting-spec-gate: [ready-for-planner, ready-for-spec-writer, closed]
+  ready-for-planner: [planned, parked, closed]
+  parked: [ready-for-triage, ready-for-spec-writer, ready-for-critic, ready-for-planner, awaiting-spec-gate, ready-for-implementer, checks-in-flight, ready-for-parent-verify, closed]
+  planned: [ready-for-parent-verify, parked, closed]
+  # sub-tickets
+  waiting-dependencies: [ready-for-implementer, parked, closed]
+  ready-for-implementer: [checks-in-flight, parked, closed]
+  checks-in-flight: [ready-for-merge, ready-for-implementer, parked, closed]
+  ready-for-merge: [merged, ready-for-implementer, parked, closed]
+  merged: [closed]
+  # parent, after every sub-ticket merged
+  ready-for-parent-verify: [closed, parked]
diff --git a/factory/prompts/context.md b/factory/prompts/context.md
deleted file mode 100644
index 79cbf2e..0000000
--- a/factory/prompts/context.md
+++ /dev/null
@@ -1,29 +0,0 @@
-## Context for this run (composed by the harness, not part of the request)
-
-Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
-documents, not code: `docs/spec-factory.md` (the design document, source of truth),
-`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
-decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
-(each file a verbatim copy of one prompt block in the design doc; it changes only by
-re-copying that block). Your shell may start in another directory: use absolute paths, or
-`cd ~/dev/spec-factory && <cmd>`.
-
-The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
-(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
-what a fix does today; never write there, and never copy its test names, line numbers or
-commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).
-
-Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
-`git diff --check` against the documents). A change to the design doc keeps its own
-conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
-new text, and any `prompts/` file whose block changed re-copied from it.
-
-The request is an issue draft, written from a real pipeline run: where in the documents,
-what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
-where a harness fix already exists. The evidence is the requirement; the proposed fix is the
-requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
-before relying on it; a NEW criterion that already passes on this checkout proves nothing.
-
-Output: write your complete output, in your role's required format and ending with the
-STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
-is the only file you may create or modify. Then return the same text as your final message.
diff --git a/factory/prompts/preamble.md b/factory/prompts/preamble.md
index c23daec..c08e876 100644
--- a/factory/prompts/preamble.md
+++ b/factory/prompts/preamble.md
@@ -1,4 +1,4 @@
-You are one agent in a software pipeline: spec-factory (the design repo at ~/dev/spec-factory, branch main). Other agents check
+You are one agent in a software pipeline: {repo name}. Other agents check
 your output, and a human audits a sample of everything.
 
 WHAT "GOOD" MEANS
@@ -35,7 +35,7 @@ SCOPE AND ESCALATION
   a protected path the approved spec's Risk section does not declare, or
   you'd need to break a rule above to finish.
 - Protected paths for this repo:
-  infra (intake/**, the scratch harness instance running you), generated (prompts/**, verbatim copies of the design doc's prompt blocks, changed only by re-copying), reference harness (~/dev/nanobot-upstream/**, read only), credentials (~/.nanobot/**, never read or written by any role)
+  {auth, payments, migrations, infra, public API, dependencies}
 
 GUARDRAIL PATHS
 Never modify or delete existing tests, CI config, AGENTS.md, skills, or
diff --git a/factory/store.py b/factory/store.py
index 0299cb3..024f10f 100644
--- a/factory/store.py
+++ b/factory/store.py
@@ -12,9 +12,6 @@ from pathlib import Path
 
 import yaml
 
-REPO_ROOT = Path(__file__).resolve().parent.parent
-CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"
-
 STATES = [
     "ready-for-triage", "waiting-requester", "ready-for-spec-writer", "ready-for-critic",
     "awaiting-spec-gate", "ready-for-planner", "planned", "parked", "closed",
@@ -30,15 +27,19 @@ class Refused(Exception):  # noqa: N818
 
 
 def load_config() -> dict:
-    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
+    """The resolved instance's `instance.yaml` (factory/instance.py); refused when none is found."""
+    from factory import instance  # local: instance imports Refused from here
+    return instance.load_config()
 
 
 def state_root(cfg: dict | None = None) -> Path:
+    """FACTORY_STATE, else the instance's `state_dir` under its repo root."""
+    from factory import instance
     env = os.environ.get("FACTORY_STATE")
     if env:
         return Path(env).expanduser().resolve()
-    cfg = cfg or load_config()
-    return (REPO_ROOT / cfg["state_dir"]).resolve()
+    inst = instance.require()
+    return instance.state_root(inst, cfg or instance.load_config(inst))
 
 
 def now() -> str:
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index 4273f58..39de0a7 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -7,18 +7,20 @@ export const meta = {
     { title: 'Close', detail: 'one verifier run on the integration branch against the parent spec; VERIFIED archives, then closes' },
   ],
 }
-// args: { ticket, repo, state, target?, integration?, stubs?, inlineRoles? }  — repo/state/stubs/inlineRoles as in intake.js.
+// args: { ticket, repo, instance?, state?, target?, integration?, stubs?, inlineRoles? }  — repo/instance/state/stubs/inlineRoles as in intake.js.
 // Local-commit stand-in (operator, 2026-10-02): no remote, no CI. The gate suite is run by the
 // verifier and recorded as the ci row; the merge is a local --no-ff merge into the integration
 // branch. The routing is build spec part H, build.js; the join itself is `factory ticket join`.
 
 const TICKET = args.ticket
 const REPO = args.repo
-const STATE = args.state
-// target = the repo the implementer works in (default: the checkout bin/factory lives in);
+const INSTANCE = args.instance
+let STATE = args.state || null  // set from `factory config` below when not given
+// target = the repo the implementer works in (default: the instance's repo, the parent of its `.factory/`);
 // integration = the branch merged into (default: config integration_branch, else the target's current branch).
-const ENV = `FACTORY_STATE=${STATE}` + (args.target ? ` FACTORY_REPO=${args.target}` : '') + (args.integration ? ` FACTORY_INTEGRATION_BRANCH=${args.integration}` : '')
-const BIN = `${ENV} ${REPO}/bin/factory`
+const ENV = [INSTANCE ? `FACTORY_INSTANCE=${INSTANCE}` : '', STATE ? `FACTORY_STATE=${STATE}` : '',
+  args.target ? `FACTORY_REPO=${args.target}` : '', args.integration ? `FACTORY_INTEGRATION_BRANCH=${args.integration}` : ''].filter(Boolean).join(' ')
+const BIN = `${ENV ? ENV + ' ' : ''}${REPO}/bin/factory`
 const PREFIX = args.agentPrefix || 'factory-'
 const INLINE = !!args.inlineRoles
 const CLERK_RULES = 'You are the store clerk of the spec factory: run the one command you are given, once, unchanged, from the repository root; run nothing else, edit nothing, interpret nothing. '
@@ -168,7 +170,8 @@ async function buildOne(st) {
 
 // --- start
 const cfg = await clerk(`${BIN} config`, 'Plan', 'config')
-if (cfg.ok) { MODELS = cfg.models; MAX_PR = cfg.max_rounds.pr }
+if (cfg.ok) { MODELS = cfg.models; MAX_PR = cfg.max_rounds.pr; if (!STATE) STATE = cfg.state_dir }
+if (!STATE) return { ticket: TICKET, error: `no store: factory config failed: ${cfg.stderr || cfg.error || ''}` }
 const show = await clerk(`${BIN} ticket show ${TICKET} --json`, 'Plan', 'ticket show')
 if (!show.ok) return { ticket: TICKET, error: `no such ticket: ${show.stderr}` }
 let state = show.state
diff --git a/factory/workflows/intake.js b/factory/workflows/intake.js
index 89098f3..dfa015a 100644
--- a/factory/workflows/intake.js
+++ b/factory/workflows/intake.js
@@ -7,9 +7,13 @@ export const meta = {
     { title: 'Plan', detail: 'after the human gate: planner decomposes the approved spec' },
   ],
 }
-// args: { ticket, repo, state, stubs?, agentPrefix? }
-//   repo  = absolute path of the checkout (bin/factory lives under it)
-//   state = absolute path of the store (knowledge_vault/spec_factory)
+// args: { ticket, repo, instance?, state?, stubs?, agentPrefix? }
+//   repo     = absolute path of the harness checkout (bin/factory lives under it); the clerk runs from it
+//   instance = absolute path of the target repo's `.factory/` (`factory paths` prints it); when given,
+//              every store command runs with FACTORY_INSTANCE=<instance>. Without it the harness walks
+//              up from `repo`, which finds only the harness repo's own instance
+//   state    = absolute path of the store (FACTORY_STATE); optional: by default the instance's own
+//              store, as `factory config` reports it
 //   stubs = directory of <role>-<n>.md fixture outputs; when set, every role is the factory-stub agent
 //   inlineRoles = true when the factory-* agent types are not registered in this session
 // The script holds routing, the join and the round counter as code and nothing else decides
@@ -18,8 +22,10 @@ export const meta = {
 
 const TICKET = args.ticket
 const REPO = args.repo
-const STATE = args.state
-const BIN = `FACTORY_STATE=${STATE} ${REPO}/bin/factory`
+const INSTANCE = args.instance
+let STATE = args.state || null  // set from `factory config` below when not given
+const ENV = [INSTANCE ? `FACTORY_INSTANCE=${INSTANCE}` : '', STATE ? `FACTORY_STATE=${STATE}` : ''].filter(Boolean).join(' ')
+const BIN = `${ENV ? ENV + ' ' : ''}${REPO}/bin/factory`
 const PREFIX = args.agentPrefix || 'factory-'
 // inlineRoles: the .claude/agents/factory-* definitions are not registered in this session (the
 // directory did not exist at session start), so every role runs as general-purpose and reads its
@@ -104,7 +110,8 @@ async function transition(to, roundOp, phase) {
 
 // --- start: read config and the ticket's stored state (resumption starts from what the store holds)
 const cfg = await clerk(`${BIN} config`, 'Triage', 'config')
-if (cfg.ok) { MODELS = cfg.models; MAX = cfg.max_rounds.spec }
+if (cfg.ok) { MODELS = cfg.models; MAX = cfg.max_rounds.spec; if (!STATE) STATE = cfg.state_dir }
+if (!STATE) return { ticket: TICKET, error: `no store: factory config failed: ${cfg.stderr || cfg.error || ''}` }
 const show = await clerk(`${BIN} ticket show ${TICKET} --json`, 'Triage', 'ticket show')
 if (!show.ok) return { ticket: TICKET, error: `no such ticket: ${show.stderr}` }
 let state = show.state
diff --git a/tests/factory/conftest.py b/tests/factory/conftest.py
new file mode 100644
index 0000000..c7450df
--- /dev/null
+++ b/tests/factory/conftest.py
@@ -0,0 +1,18 @@
+"""Point every test at a fixed instance (design B.9), never at whatever instance surrounds the
+checkout the suite runs in.
+
+The imported tests drive `bin/factory` as a subprocess with cwd set to the harness checkout and an
+environment built from os.environ, each on a throwaway store (FACTORY_STATE). Without this file the
+harness would resolve the instance by walking up from that checkout: the harness repo's own
+`.factory/`, or none at all. FACTORY_REPO keeps the repo root the tests saw before instances existed
+(the harness checkout) instead of the fixture's parent; a test that sets its own FACTORY_REPO in a
+subprocess environment (the shepherd's scratch target) still overrides it.
+"""
+from __future__ import annotations
+
+import os
+from pathlib import Path
+
+_HERE = Path(__file__).resolve()
+os.environ["FACTORY_INSTANCE"] = str(_HERE.parent / "fixtures" / "instance")
+os.environ.setdefault("FACTORY_REPO", str(_HERE.parents[2]))
diff --git a/tests/factory/fixtures/instance/context.md b/tests/factory/fixtures/instance/context.md
new file mode 100644
index 0000000..20ed11d
--- /dev/null
+++ b/tests/factory/fixtures/instance/context.md
@@ -0,0 +1,4 @@
+## Context for this run (composed by the harness, not part of the request)
+
+Test fixture instance for the harness's own suite (`tests/factory/fixtures/instance/`). No role reads
+this for real work: the tests check what the harness does, not what an agent would do with it.
diff --git a/factory/config.yaml b/tests/factory/fixtures/instance/instance.yaml
similarity index 69%
rename from factory/config.yaml
rename to tests/factory/fixtures/instance/instance.yaml
index 4bfb5b6..bdfaa20 100644
--- a/factory/config.yaml
+++ b/tests/factory/fixtures/instance/instance.yaml
@@ -1,28 +1,23 @@
-# Spec factory, scratch intake instance targeting the spec-factory design repo (intake/README.md).
-# Overlaid on a pinned copy of the Nanobot-side harness by intake/setup.sh; everything from
-# placeholders down is copied verbatim from that harness's config.yaml at HARNESS_PIN.
-repo_name: spec-factory
-state_dir: intake/state
-request_dir: ../../issues
+# Fixed instance for the harness's own test suite (tests/factory/conftest.py sets FACTORY_INSTANCE
+# here, and FACTORY_REPO to the harness checkout). factory/instance.template.yaml's values, plus
+# environment_files: ["uv.lock"] (test_shepherd checks the lockfile copy) and the whitespace gate.
+# Every test runs on a throwaway store (FACTORY_STATE), so state_dir is never used.
+repo_name: "factory test fixture"
+harness: null
+state_dir: .factory/state
 protected_paths:
-  infra: ["intake/**"]
-  generated: ["prompts/**"]
-  reference_harness: ["~/dev/nanobot-upstream/**"]
-  credentials: ["~/.nanobot/**"]
-# Runs in the checkout under test (a checker's detached checkout or the implementer's worktree):
-# whitespace errors in what the branch adds over main. No test suite exists here until #19 part A.
-gate_commands:
-  - "git diff --check main...HEAD"
+  infra: [".factory/instance.yaml", ".factory/harness.lock", ".factory/context.md"]
+gate_commands: ["git diff --check main...HEAD"]
 placeholders: {rounds: 2, spec_lines: 400, audit_n: 5, retro_min: 3}
 max_rounds: {spec: 2, pr: 2}
 # Build half, local-commit stand-in (operator, 2026-10-02): no remote, no CI. The merge gate is the
 # gate suite on the branch plus the two checkers; then a local --no-ff merge into integration_branch
 # (null = the target repo's current branch). FACTORY_REPO / FACTORY_INTEGRATION_BRANCH override.
-integration_branch: main
+integration_branch: null
 # Untracked files every worktree and checker checkout copies from the integration checkout at each run
-# start, so a branch is tested against the same environment the integration branch runs in. uv.lock
-# is git-ignored on green: without it a fresh worktree resolves newer packages (mcp 1.30 vs 1.29 broke
-# a test the first pilot never touched).
+# start, so a branch is tested against the same environment the integration branch runs in (for
+# example a lockfile the target repo git-ignores). A tracked file does not belong here: copying it in
+# would mask the branch's own version.
 environment_files: ["uv.lock"]
 force_push_allowed: false
 models:
diff --git a/tests/factory/test_instance.py b/tests/factory/test_instance.py
new file mode 100644
index 0000000..9a7d180
--- /dev/null
+++ b/tests/factory/test_instance.py
@@ -0,0 +1,345 @@
+"""Instances (design B): the resolver, `instance.yaml`, the briefing, the filled preamble, `init`,
+`paths` and the harness revision, black-box through `bin/factory` in scratch target repos.
+
+Each case strips the conftest's FACTORY_INSTANCE / FACTORY_REPO and any FACTORY_STATE, so the
+harness resolves the instance the way it does for an operator: from the working directory.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
+NOT_FOUND = "no .factory/instance.yaml found from {cwd}; run factory init --repo-name NAME, or set FACTORY_INSTANCE"
+
+
+def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
+    env = {k: v for k, v in os.environ.items() if k not in STRIP}
+    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=cwd)
+
+
+def js(cp: subprocess.CompletedProcess) -> dict:
+    return json.loads(cp.stdout.strip().splitlines()[-1])
+
+
+def git_repo(path: Path) -> Path:
+    path.mkdir(parents=True, exist_ok=True)
+    for argv in (["init", "-q", "-b", "main"],
+                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
+        subprocess.run(["git", "-C", str(path), *argv], check=True, capture_output=True)
+    return path
+
+
+def tree(path: Path) -> dict[str, bytes]:
+    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}
+
+
+def harness_status() -> str:
+    return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True).stdout
+
+
+def revision() -> str:
+    return subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%H", "--",
+                           "factory", "bin/factory", "agents", "pyproject.toml", "uv.lock"],
+                          capture_output=True, text=True, check=True).stdout.strip()
+
+
+@pytest.fixture
+def target(tmp_path: Path) -> Path:
+    """A scratch target repo with an instance made by `factory init` from a subdirectory."""
+    t = git_repo(tmp_path / "target")
+    (t / "sub").mkdir()
+    cp = cli(t / "sub", "init", "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    return t
+
+
+@pytest.fixture
+def request_file(tmp_path: Path) -> Path:
+    p = tmp_path / "r.md"
+    p.write_text("# demo\n\nDo the thing.\n")
+    return p
+
+
+# ----- init (B.5) -----------------------------------------------------------------------------
+
+def test_init_creates_the_instance_at_the_git_top_level(tmp_path):
+    t = git_repo(tmp_path / "target")
+    (t / "a" / "b").mkdir(parents=True)
+    cp = cli(t / "a" / "b", "init", "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    assert sorted(p.name for p in (t / ".factory").iterdir()) == ["context.md", "harness.lock", "instance.yaml", "state"]
+    assert not (t / "a" / ".factory").exists() and not (t / "a" / "b" / ".factory").exists()
+    agents = sorted((REPO / "agents").glob("factory-*.md"))
+    assert len(agents) == 6
+    assert {p.name: p.read_bytes() for p in agents} == tree(t / ".claude" / "agents")
+    assert (cp.stdout + cp.stderr).count("restart the session so the agents register") == 1
+    assert (t / ".factory" / "context.md").read_bytes() == (REPO / "factory" / "context.template.md").read_bytes()
+    assert (t / ".factory" / "harness.lock").read_text() == revision() + "\n"
+    state = t / ".factory" / "state"
+    assert (state / "openspec" / "config.yaml").is_file() and (state / "decisions.md").is_file()
+    assert {"worktrees/", "runs/*/wt/"} <= set((state / ".gitignore").read_text().splitlines())
+    out = js(cp)
+    assert out["ok"] is True and Path(out["instance"]) == (t / ".factory").resolve()
+
+
+def test_init_writes_instance_yaml_from_the_template(target):
+    cfg = yaml.safe_load((target / ".factory" / "instance.yaml").read_text())
+    tpl = yaml.safe_load((REPO / "factory" / "instance.template.yaml").read_text())
+    assert cfg["repo_name"] == "demo"
+    assert Path(cfg["harness"]) == REPO and Path(cfg["harness"]).is_absolute()
+    assert cfg["state_dir"] == ".factory/state"
+    assert cfg["protected_paths"] == {"infra": [".factory/instance.yaml", ".factory/harness.lock", ".factory/context.md"]}
+    assert cfg["gate_commands"] == []
+    assert cfg["integration_branch"] is None and cfg["environment_files"] == [] and cfg["force_push_allowed"] is False
+    assert "request_dir" not in cfg
+    for key in ("placeholders", "max_rounds", "models", "ready_state", "routing"):
+        assert cfg[key] == tpl[key], key
+    assert set(cfg) == set(tpl)
+
+
+def test_init_repo_name_with_yaml_specials_round_trips(tmp_path):
+    t = git_repo(tmp_path / "target")
+    name = 'spec-factory (the design repo at ~/dev/x: "main", #1)'
+    assert cli(t, "init", "--repo-name", name).returncode == 0
+    assert yaml.safe_load((t / ".factory" / "instance.yaml").read_text())["repo_name"] == name
+
+
+def test_init_works_at_its_own_git_top_level_not_an_enclosing_instance(target):
+    """A repo nested under a directory that has an instance gets its own; the walk-up then finds it."""
+    inner = git_repo(target / "sub" / "inner")
+    (inner / "deep").mkdir()
+    cp = cli(inner / "deep", "init", "--repo-name", "inner")
+    assert cp.returncode == 0, cp.stderr
+    assert (inner / ".factory" / "instance.yaml").is_file() and (inner / ".claude" / "agents").is_dir()
+    assert Path(js(cli(inner / "deep", "paths"))["instance"]) == (inner / ".factory").resolve()
+
+
+def test_init_refused_outside_a_git_work_tree(tmp_path):
+    d = tmp_path / "plain"
+    d.mkdir()
+    cp = cli(d, "init", "--repo-name", "x")
+    assert cp.returncode == 2 and "not inside a git work tree" in cp.stderr
+    assert list(d.iterdir()) == []
+
+
+def test_init_without_repo_name_refused_and_writes_nothing(tmp_path):
+    t = git_repo(tmp_path / "target")
+    cp = cli(t, "init")
+    assert cp.returncode == 2 and "--repo-name" in cp.stderr
+    assert sorted(p.name for p in t.iterdir()) == [".git"]
+
+
+def test_init_is_idempotent_and_creates_only_what_is_missing(target):
+    before = tree(target / ".factory") | {f"claude/{k}": v for k, v in tree(target / ".claude").items()}
+    for _ in range(2):
+        cp = cli(target, "init")
+        assert cp.returncode == 0, cp.stderr
+        assert "restart the session" not in cp.stdout + cp.stderr
+        assert js(cp)["written"] == [] and js(cp)["created"] == [] and js(cp)["agents"] == []
+    assert tree(target / ".factory") | {f"claude/{k}": v for k, v in tree(target / ".claude").items()} == before
+
+    (target / ".factory" / "context.md").unlink()
+    (target / ".claude" / "agents" / "factory-planner.md").unlink()
+    (target / ".factory" / "state" / "decisions.md").unlink()
+    cp = cli(target, "init", "--repo-name", "ignored-when-instance-exists")
+    assert cp.returncode == 0, cp.stderr
+    assert (cp.stdout + cp.stderr).count("restart the session so the agents register") == 1
+    out = js(cp)
+    assert out["written"] == ["decisions.md"]
+    assert [Path(p).name for p in out["created"]] == ["context.md"]
+    assert [Path(p).name for p in out["agents"]] == ["factory-planner.md"]
+    assert yaml.safe_load((target / ".factory" / "instance.yaml").read_text())["repo_name"] == "demo"
+    after = tree(target / ".factory") | {f"claude/{k}": v for k, v in tree(target / ".claude").items()}
+    logs = {k for k in before | after if k.startswith("state/log/")}  # the re-creation is logged
+    assert {k: v for k, v in after.items() if k not in logs} == {k: v for k, v in before.items() if k not in logs}
+
+
+def test_init_on_a_throwaway_store_initialises_only_that_store(target, tmp_path):
+    """FACTORY_STATE elsewhere (as in every test): the instance's own pieces are left alone."""
+    (target / ".factory" / "harness.lock").unlink()
+    (target / ".claude" / "agents" / "factory-triage.md").unlink()
+    s = tmp_path / "throwaway"
+    cp = cli(target, "init", FACTORY_STATE=str(s))
+    assert cp.returncode == 0, cp.stderr
+    assert (s / "openspec" / "config.yaml").is_file() and (s / ".gitignore").is_file()
+    assert not (target / ".factory" / "harness.lock").exists()
+    assert not (target / ".claude" / "agents" / "factory-triage.md").exists()
+    assert "restart the session" not in cp.stdout + cp.stderr
+
+
+def test_the_suite_conftest_init_writes_nothing_into_the_harness(tmp_path):
+    """The imported tests run `init` with the conftest's fixture instance and FACTORY_REPO = the
+    harness checkout: only their throwaway store may change."""
+    fixture = REPO / "tests" / "factory" / "fixtures" / "instance"
+    before_fixture, before_status = tree(fixture), harness_status()
+    env = {k: v for k, v in os.environ.items() if k not in STRIP}
+    env.update(PYTHONDONTWRITEBYTECODE="1", FACTORY_INSTANCE=str(fixture), FACTORY_REPO=str(REPO),
+               FACTORY_STATE=str(tmp_path / "s"))
+    cp = subprocess.run([str(BIN), "init"], capture_output=True, text=True, env=env, cwd=REPO)
+    assert cp.returncode == 0, cp.stderr
+    assert (tmp_path / "s" / "openspec").is_dir()
+    assert tree(fixture) == before_fixture and harness_status() == before_status
+
+
+# ----- resolver (B.1, B.2) --------------------------------------------------------------------
+
+def test_store_command_from_a_subdirectory_uses_the_target_instance(target, request_file):
+    before = harness_status()
+    cp = cli(target / "sub", "ticket", "new", "--file", str(request_file))
+    assert cp.returncode == 0, cp.stderr
+    assert sorted(p.name for p in (target / ".factory" / "state" / "tickets").iterdir()) == ["T-0001.yaml"]
+    assert harness_status() == before
+
+
+def test_command_outside_any_instance_refused_and_writes_nothing(tmp_path, request_file):
+    d = tmp_path / "nowhere"
+    d.mkdir()
+    for argv in (("ticket", "show", "T-0001"), ("ticket", "new", "--file", str(request_file)), ("config",)):
+        cp = cli(d, *argv)
+        assert cp.returncode == 2, argv
+        assert cp.stderr.strip() == NOT_FOUND.format(cwd=d.resolve()), cp.stderr
+        assert list(d.iterdir()) == []
+
+
+def test_no_fallback_even_with_a_store_named(tmp_path, request_file):
+    """FACTORY_STATE alone does not stand in for an instance: config comes only from one."""
+    d = tmp_path / "nowhere"
+    d.mkdir()
+    s = tmp_path / "s"
+    cp = cli(d, "ticket", "new", "--file", str(request_file), FACTORY_STATE=str(s))
+    assert cp.returncode == 2 and "instance.yaml" in cp.stderr
+    assert not s.exists()
+
+
+def test_factory_instance_overrides_the_working_directory(target, request_file, tmp_path):
+    assert cli(target, "ticket", "new", "--file", str(request_file)).returncode == 0
+    other = git_repo(tmp_path / "other")
+    assert cli(other, "init", "--repo-name", "other").returncode == 0
+    cp = cli(other, "ticket", "show", "T-0001", FACTORY_INSTANCE=str(target / ".factory"))
+    assert cp.returncode == 0, cp.stderr
+    assert yaml.safe_load(cp.stdout)["title"] == "demo"
+    assert not (other / ".factory" / "state" / "tickets").exists()
+
+
+def test_factory_instance_without_instance_yaml_refused(tmp_path):
+    d = tmp_path / "empty"
+    d.mkdir()
+    cp = cli(tmp_path, "ticket", "show", "T-0001", FACTORY_INSTANCE=str(d))
+    assert cp.returncode == 2 and "instance.yaml" in cp.stderr and str(d) in cp.stderr
+
+
+def test_repo_root_is_the_instance_parent_and_factory_repo_overrides(target, tmp_path):
+    """An instance directory under any name: state_dir resolves under its parent, or FACTORY_REPO."""
+    alt = tmp_path / "elsewhere" / "inst"
+    alt.mkdir(parents=True)
+    (alt / "instance.yaml").write_bytes((target / ".factory" / "instance.yaml").read_bytes())
+    (alt / "context.md").write_text("x\n")
+    cp = cli(tmp_path, "config", FACTORY_INSTANCE=str(alt))
+    assert cp.returncode == 0, cp.stderr
+    assert Path(js(cp)["state_dir"]) == (tmp_path / "elsewhere" / ".factory" / "state").resolve()
+    cp = cli(tmp_path, "config", FACTORY_INSTANCE=str(alt), FACTORY_REPO=str(target))
+    assert Path(js(cp)["state_dir"]) == (target / ".factory" / "state").resolve()
+    cp = cli(tmp_path, "config", FACTORY_INSTANCE=str(alt), FACTORY_STATE=str(tmp_path / "s"))
+    assert Path(js(cp)["state_dir"]) == (tmp_path / "s").resolve()
+
+
+# ----- briefing and preamble (B.3, B.4) -------------------------------------------------------
+
+def _start_triage(target: Path, request_file: Path) -> Path:
+    assert cli(target, "ticket", "new", "--file", str(request_file)).returncode == 0
+    cp = cli(target, "run", "start", "--role", "triage", "--ticket", "T-0001", "--model", "opus")
+    assert cp.returncode == 0, cp.stderr
+    return target / ".factory" / "state" / "runs" / js(cp)["run_id"]
+
+
+def test_composed_input_opens_with_the_instance_context(target, request_file):
+    (target / ".factory" / "context.md").write_text("CTX-MARKER for demo\nsecond line\n")
+    run = _start_triage(target, request_file)
+    cp = cli(target, "run", "compose", run.name)
+    assert cp.returncode == 0, cp.stderr
+    text = (run / "input.md").read_text()
+    assert text.startswith("CTX-MARKER for demo\nsecond line\n## Output file\n")
+
+
+def test_system_prompt_is_the_design_preamble_filled_from_the_instance(target, request_file):
+    run = _start_triage(target, request_file)
+    got = (run / "system-prompt.txt").read_text().split("\n")
+    block = (REPO / "docs" / "prompts" / "00-preamble.md").read_text().rstrip().split("\n")
+    assert got[0] == "You are one agent in a software pipeline: demo. Other agents check"
+    i = block.index("  {auth, payments, migrations, infra, public API, dependencies}")
+    assert got[i] == "  infra (.factory/instance.yaml, .factory/harness.lock, .factory/context.md)"
+    assert [ln for n, ln in enumerate(got[:len(block)]) if n not in (0, i)] == \
+        [ln for n, ln in enumerate(block) if n not in (0, i)]
+    role = (REPO / "factory" / "prompts" / "triage.md").read_text()
+    assert "\n".join(got).endswith("\n\n" + role)
+    assert "{repo name}" not in "\n".join(got) and "{auth, payments" not in "\n".join(got)
+
+
+def test_protected_path_line_lists_every_class(target, request_file):
+    p = target / ".factory" / "instance.yaml"
+    cfg = yaml.safe_load(p.read_text())
+    cfg["protected_paths"] = {"infra": [".factory/**", "intake/**"], "harness": ["factory/**", "bin/factory"],
+                              "credentials": "~/.secret/**"}
+    p.write_text(yaml.safe_dump(cfg, sort_keys=False))
+    run = _start_triage(target, request_file)
+    assert ("  infra (.factory/**, intake/**), harness (factory/**, bin/factory), credentials (~/.secret/**)"
+            in (run / "system-prompt.txt").read_text().split("\n"))
+
+
+def test_harness_preamble_is_the_design_doc_block_and_green_overlay_is_gone():
+    assert (REPO / "factory" / "prompts" / "preamble.md").read_bytes() == (REPO / "docs" / "prompts" / "00-preamble.md").read_bytes()
+    assert not (REPO / "factory" / "config.yaml").exists()
+    assert not (REPO / "factory" / "prompts" / "context.md").exists()
+
+
+# ----- paths (B.6) and the harness revision (C.1) ---------------------------------------------
+
+def test_paths_inside_an_instance(target):
+    before = tree(target)
+    cp = cli(target / "sub", "paths")
+    assert cp.returncode == 0, cp.stderr
+    p = js(cp)
+    assert Path(p["harness"]) == REPO
+    for k in ("harness", "bin", "intake_workflow", "build_workflow", "instance", "state"):
+        assert Path(p[k]).is_absolute(), k
+    assert Path(p["bin"]) == REPO / "bin" / "factory"
+    assert Path(p["intake_workflow"]).is_file() and Path(p["build_workflow"]).is_file()
+    assert p["harness_revision"] == revision() and len(p["harness_revision"]) == 40
+    assert Path(p["instance"]) == (target / ".factory").resolve()
+    assert Path(p["state"]) == (target / ".factory" / "state").resolve()
+    assert tree(target) == before
+
+
+def test_paths_outside_any_instance(tmp_path):
+    d = tmp_path / "nowhere"
+    d.mkdir()
+    cp = cli(d, "paths")
+    assert cp.returncode == 0, cp.stderr
+    p = js(cp)
+    assert p["instance"] is None and p["state"] is None
+    assert Path(p["harness"]) == REPO and len(p["harness_revision"]) == 40
+    assert list(d.iterdir()) == []
+
+
+# ----- the suite's own instance (B.9) ---------------------------------------------------------
+
+def test_conftest_points_the_suite_at_the_fixture_instance():
+    fixture = (REPO / "tests" / "factory" / "fixtures" / "instance").resolve()
+    assert Path(os.environ["FACTORY_INSTANCE"]).resolve() == fixture
+    assert os.environ.get("FACTORY_REPO")
+    cfg = yaml.safe_load((fixture / "instance.yaml").read_text())
+    tpl = yaml.safe_load((REPO / "factory" / "instance.template.yaml").read_text())
+    assert cfg["environment_files"] == ["uv.lock"] and cfg["gate_commands"] == ["git diff --check main...HEAD"]
+    for key in ("state_dir", "protected_paths", "placeholders", "max_rounds", "integration_branch",
+                "force_push_allowed", "models", "ready_state", "routing"):
+        assert cfg[key] == tpl[key], key
+    assert (fixture / "context.md").is_file()
