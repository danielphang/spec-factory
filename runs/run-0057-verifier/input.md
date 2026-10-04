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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0057-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/intake/state/runs/run-0057-verifier/wt` (branch `factory/T-0012.2`, base `cdb1c6769ecc39208e62edc65578f62f5a23908f`, head `c367bef72e2ed70a4417e98de907c91dbbe31320`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`

## Sub-ticket T-0012.2

## T-0012.2 / Document re-layout: `docs/design.md` + `docs/changelog.md`, `docs/prompts/`, `dev/`

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: none

Parallel-safe: yes, with T-0012.1. Its files are `docs/**`, `prompts/**`, `specs/build-harness.md`, `plans/**`, `issues/README.md`, `dev/**`, `README.md`, `intake/README.md` and `intake/instance/context.md`, and T-0012.1 touches none of them. Every later sub-ticket waits for it.

Scope: D.1–D.4.
- Content is unchanged apart from the path updates D.4 lists, plus the one added line in "How to use this".
- Records are left as written: `intake/answers/`, `intake/green-pilot/`, `intake/state/`, and the changelog entries.

Acceptance:
- **docs-moved-and-split** → NEW [specs/repo-layout]. THEN only `old_tracked=0`.
- **changelog-moved-verbatim** → NEW [specs/repo-layout]. THEN `SAME`, then `declined=1 numbering=CONTIGUOUS in_design=0`.
- **design-text-kept** → NEW [specs/repo-layout]. THEN `0`.
- **prompt-copies-moved-unchanged** → NEW [specs/repo-layout]. THEN `changed=0 of 10 VERBATIM`.
- **no-old-paths, documents only** → NEW (intermediate for no-old-paths-in-live-files). `agents`, `factory` and `.factory/*` are left out here because T-0012.1's overlay may be on `main` until T-0012.3, and `.factory/` arrives in T-0012.6.
  - WHEN `git grep -n -e 'docs/spec-factory\.md' -e 'specs/build-harness\.md' -e 'plans/build-harness\.md' -e 'plans/P0-intake-skeleton\.md' -e 'issues/README\.md' -e 'HARNESS_PIN' -e 'intake/setup\.sh' -e '[^/a-z_]prompts/' -e '^prompts/' -- README.md docs dev >/dev/null; echo "exit=$?"`
  - THEN `exit=1`. Today the matches are in `README.md` (4), `plans/build-harness.md` (9) and `plans/P0-intake-skeleton.md` (1). `docs/`, `specs/`, `issues/` and `prompts/` have none (`git grep -c`, run today).
- **how-to-use-names-new-homes** → NEW (intermediate; D.1's added line).
  - WHEN `awk '/^## How to use this/{f=1;next} /^## /{f=0} f' docs/design.md | grep 'docs/changelog\.md' | grep -c 'docs/prompts/'`
  - THEN `1`.
- **records-untouched** → NEW (intermediate).
  - WHEN `git diff --name-only main...HEAD -- intake/state intake/answers intake/green-pilot intake/.gitignore | wc -l | tr -d ' '`
  - THEN `0`.
- **green-harness-still-present** → REGRESSION. THEN `green keeps its harness`.
- **whitespace (sub-ticket diff)** → REGRESSION. WHEN `git diff --check main...HEAD; echo "exit=$?"`. THEN only `exit=0`.

Tests to change: none

Protected paths:
- generated `prompts/**`: moved to `docs/prompts/`, byte-identical.
- infra `intake/**`: only `intake/README.md` and `intake/instance/context.md`, for reference updates (D.4).

Out of scope:
- The design-doc and build-spec text changes (F), including the changelog entry 42.
- README's full rewrite (E.6). Only references are updated here.
- Removing anything under `intake/` (E).
- Any harness file.

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

Sub-ticket: T-0012.2, Document re-layout (parent `intake/state/specs/T-0012/v3.md`, part D, D.1–D.4)
Branch: `factory/T-0012.2` in `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.2`, base `cdb1c6769ecc39208e62edc65578f62f5a23908f` (still `main`), head `c367bef72e2ed70a4417e98de907c91dbbe31320` (one commit).

What changed:
- D.1:
  - `git mv docs/spec-factory.md docs/design.md`.
  - The `## Changelog` section (old lines 678–725, from the heading to the line before `## Appendix`) is cut out of `docs/design.md` and becomes the new `docs/changelog.md`. That file is a `# Changelog` title followed by old lines 679–724 verbatim: the intro paragraph, entries 1–41 and the `Declined:` line. Old line 725, the blank separator before `## Appendix`, is dropped so the file does not end in a blank line.
  - At the end of "How to use this" (after the last wiring-rule bullet, before `## Harness: functional pieces`) there is one new paragraph line: "This document's changelog is `docs/changelog.md`, and `docs/prompts/` holds a verbatim copy of each prompt block in it, changed only by re-copying that block." A blank line separates it from the bullet list.
  - Every other line of `docs/design.md` is unchanged. Checked with `diff <(sed -n '1,29p;32,$p' docs/design.md) <(old lines 1–677 + 726–759)`, which printed nothing.
- D.2: `git mv prompts docs/prompts`. All 10 files are renamed at 100% similarity.
- D.3: `specs/build-harness.md` → `dev/build-harness.spec.md`, `plans/build-harness.md` → `dev/build-harness.plan.md`, `plans/P0-intake-skeleton.md` → `dev/P0-intake-skeleton.md`, `issues/README.md` → `dev/issues.md` (all `git mv`). The spec and the issues index are 100% renames.
- D.4: reference updates.
  - `README.md`, lines 5–11:
    - `docs/spec-factory.md` → `docs/design.md`, and the changelog is now named as `docs/changelog.md`;
    - `prompts/` → `docs/prompts/` (lines 6 and 11);
    - `plans/P0-intake-skeleton.md` → `dev/P0-intake-skeleton.md`;
    - the `specs/<ticket>.md` and `plans/<ticket>.md` bullets now name `dev/build-harness.spec.md` and `dev/build-harness.plan.md`, because the directories they described no longer exist here (see Known gaps);
    - added one bullet for `dev/issues.md`.
  - `dev/build-harness.plan.md`: the 9 `Parent:` lines now read `dev/build-harness.spec.md`. Line 3's GitHub URL now ends `/blob/main/dev/build-harness.spec.md`.
  - `dev/P0-intake-skeleton.md:3`: `specs/build-harness.md` → `dev/build-harness.spec.md`, `plans/build-harness.md` → `dev/build-harness.plan.md`.
  - `intake/README.md`: line 4 `../issues/README.md` → `../dev/issues.md`; line 42 `issues/README.md` → `dev/issues.md`. `HARNESS_PIN` and `intake/setup.sh` are left alone: D does not move them, and E removes them.
  - `intake/instance/context.md`, lines 3–20: the design doc, changelog, build spec, build plan, P0 skeleton and prompt-copy paths now point to the new homes. "the Changelog section at its end" now reads "its changelog entry in `docs/changelog.md`", because the changelog no longer sits at the end of the design doc.
- Records are untouched: `intake/state/`, `intake/answers/`, `intake/green-pilot/`, `intake/.gitignore` and the changelog entries.

Acceptance results (run from the worktree with bash; `BASE=$(git rev-parse main)` = `cdb1c67…`):

| Criterion | Before (at base) | After (at `c367bef`) |
|---|---|---|
| docs-moved-and-split | seven `missing …` lines, `old_tracked=15` | `old_tracked=0` |
| changelog-moved-verbatim | `DIFFERENT` / `declined= numbering=NONE in_design=` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` |
| design-text-kept | `570` | `0` |
| prompt-copies-moved-unchanged | `changed=10 of 10 DRIFT` | `changed=0 of 10 VERBATIM` |
| no-old-paths, documents only | `exit=0` | `exit=1` |
| how-to-use-names-new-homes | `awk: can't open file docs/design.md` then `0` | `1` |
| records-untouched | `0` (vacuous: the branch had no commits yet) | `0` |
| green-harness-still-present (REGRESSION) | `green keeps its harness` | `green keeps its harness` |
| whitespace (REGRESSION) | `exit=0` | `exit=0` |

Gate, as written: `git diff --check main...HEAD` printed nothing, exit 0.

Extra checks:
- `diff <(tail -n +2 docs/changelog.md) <(sed -n '679,724p' <base design doc>)` matched, so the whole changelog body is byte-identical, not only the numbered lines.
- `git diff --name-status -M main...HEAD` touches only `docs/**`, `dev/**`, `README.md`, `intake/README.md` and `intake/instance/context.md`.
- `git status --short` is empty after the commit.

Tests added/changed: none. This repo has no tests, and part D is a document move whose checks are the acceptance commands above. "Tests to change: none" is respected.

Known gaps and uncertainties:
- **Reviewers should compare the README hunk, not only the path tokens.** D.4 says "only references are updated" in `README.md`, but lines 7–8 described `specs/<ticket>.md` and `plans/<ticket>.md` as this repo's directories, and both directories are gone. I reworded them to name the two moved files (`dev/build-harness.spec.md`, `dev/build-harness.plan.md`) and added one `dev/issues.md` bullet. That is slightly more than a token swap. E.6 rewrites README in full anyway.
- `README.md:11` still says `docs/prompts/` "is regenerated from" the design doc. The parent Evidence says nothing regenerates the copies. I kept the claim because only the path is in D's scope, and E.6 rewrites it.
- One unintended edit happened during the work and was reverted. An Edit call replaced part of `docs/design.md` line 29 with `x`. I did not patch it by hand: I regenerated `docs/design.md` from `git show HEAD:docs/spec-factory.md` with the same split, then re-applied the insertion with a scripted line-29 insert. The full-file `diff` against the base (above) and `design-text-kept` = `0` show no trace of it in the commit.
- The "one added line" sits in its own paragraph, so it brings one blank separator line with it.
- Process note: the session scratchpad is shared with the parallel T-0012.1 run. My first acceptance script there (`acc.sh`) was overwritten mid-run with T-0012.1's checks. I re-ran everything from a uniquely named `T-0012.2-acc.sh`. All "after" results above come from that file, run against the committed head.

Out-of-scope observations:
- `intake/instance/config.yaml:9` (`generated: ["prompts/**"]`) and `intake/instance/preamble.md:38` (`generated (prompts/**, …)`) still name the old prompt-copy path. Both files are outside this sub-ticket's file list, which allows only `intake/README.md` and `intake/instance/context.md` under `intake/`. E.5 deletes them. Until then, the running copy's protected-paths line names `prompts/**` rather than `docs/prompts/**`. The live harness under `intake/harness/` changes only when `setup.sh` is re-run, so editing `context.md` here does not change the briefing the running copy uses either.
- The changelog's intro paragraph (kept verbatim) says the review rounds used "the reviewer prompt in the appendix". That appendix is now in `docs/design.md`, not in `docs/changelog.md`. Part F, or a later doc pass, may want a cross-reference. I did not add one, because records are left as written.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance criterion and the gate were run on the committed head and gave the expected output; the changelog body and the rest of the design doc were checked byte for byte against the base.
ESCALATIONS: none

## Diff `cdb1c6769ecc39208e62edc65578f62f5a23908f...c367bef72e2ed70a4417e98de907c91dbbe31320`

diff --git a/README.md b/README.md
index 7a9c098..ec62c80 100644
--- a/README.md
+++ b/README.md
@@ -2,10 +2,11 @@
 
 An AI software pipeline: eight agent roles, a harness that enforces the wiring rules, a routing table, and human gates.
 
-- `docs/spec-factory.md` — the design document (roles, harness pieces, routing, gates, changelog).
-- `prompts/` — each role's system prompt, extracted verbatim from the design doc. `00-preamble.md` goes at the top of every role.
-- `specs/<ticket>.md` — a spec: the Spec writer's output for one ticket, approved at the human gate. `build-harness.md` is the spec for building the harness itself, produced by running the pipeline on the design doc (bootstrap run).
-- `plans/<ticket>.md` — the Planner's decomposition of the spec of the same name into ordered sub-tickets. One plan per spec; same filename, one stage later.
-- `plans/P0-intake-skeleton.md` — the first walking skeleton: a cut through the build-harness plan that runs the intake half (Triage → Spec writer ⇄ Critic → gate → Planner) on real faux-specs before any enforcement is built.
+- `docs/design.md` — the design document (roles, harness pieces, routing, gates). Its changelog is `docs/changelog.md`.
+- `docs/prompts/` — each role's system prompt, extracted verbatim from the design doc. `00-preamble.md` goes at the top of every role.
+- `dev/build-harness.spec.md` — the spec for building the harness itself, produced by running the pipeline on the design doc (bootstrap run).
+- `dev/build-harness.plan.md` — the Planner's decomposition of that spec into ordered sub-tickets.
+- `dev/P0-intake-skeleton.md` — the first walking skeleton: a cut through the build-harness plan that runs the intake half (Triage → Spec writer ⇄ Critic → gate → Planner) on real faux-specs before any enforcement is built.
+- `dev/issues.md` — the index of this repo's GitHub issues and where each one stands.
 
-Fill in `{braces}` per repo. The design doc is the source of truth; `prompts/` is regenerated from it.
+Fill in `{braces}` per repo. The design doc is the source of truth; `docs/prompts/` is regenerated from it.
diff --git a/plans/P0-intake-skeleton.md b/dev/P0-intake-skeleton.md
similarity index 96%
rename from plans/P0-intake-skeleton.md
rename to dev/P0-intake-skeleton.md
index 287d457..a284fbd 100644
--- a/plans/P0-intake-skeleton.md
+++ b/dev/P0-intake-skeleton.md
@@ -1,6 +1,6 @@
 # P0: intake walking skeleton
 
-Parent: `specs/build-harness.md` (v4). This is not a sub-ticket of `plans/build-harness.md`; it is a cut through it. It builds BH-1-lite, BH-4, and BH-5 and defers BH-2a, BH-2b, BH-3, BH-6, BH-7. Nothing built here is thrown away: the agent definitions, the `factory` CLI, and `intake.js` are the same files the full plan grows.
+Parent: `dev/build-harness.spec.md` (v4). This is not a sub-ticket of `dev/build-harness.plan.md`; it is a cut through it. It builds BH-1-lite, BH-4, and BH-5 and defers BH-2a, BH-2b, BH-3, BH-6, BH-7. Nothing built here is thrown away: the agent definitions, the `factory` CLI, and `intake.js` are the same files the full plan grows.
 
 ## Why first
 
diff --git a/plans/build-harness.md b/dev/build-harness.plan.md
similarity index 97%
rename from plans/build-harness.md
rename to dev/build-harness.plan.md
index cf3c1d8..78ed91b 100644
--- a/plans/build-harness.md
+++ b/dev/build-harness.plan.md
@@ -1,6 +1,6 @@
 # Plan: Build the spec factory, local-Mac v0 — sub-tickets (plan v2)
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory` (https://github.com/danielphang/spec-factory/blob/main/specs/build-harness.md); approved text = `spec-build-v4.md` (STATUS NEEDS-SPLIT; 84 acceptance items, of which 71–84 are the gate's round-4 amendments A–N), pinned by the human gate. The v1 rulings stand (every Open question on its proposed default; same-user deploy keys for v0; post-hoc budget kill; standing allowlist for real runs, never `bypassPermissions`; first acceptance run interactive; Nanobot gate commands unknown and carried as BH-1's open question; split along seams S1–S5), plus the amendments and the doc-v5 deltas folded into them.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory` (https://github.com/danielphang/spec-factory/blob/main/dev/build-harness.spec.md); approved text = `spec-build-v4.md` (STATUS NEEDS-SPLIT; 84 acceptance items, of which 71–84 are the gate's round-4 amendments A–N), pinned by the human gate. The v1 rulings stand (every Open question on its proposed default; same-user deploy keys for v0; post-hoc budget kill; standing allowlist for real runs, never `bypassPermissions`; first acceptance run interactive; Nanobot gate commands unknown and carried as BH-1's open question; split along seams S1–S5), plus the amendments and the doc-v5 deltas folded into them.
 Planner: planner · Plan version: 2 (re-plan after the gate amended the pinned spec; supersedes `plan-build-v1.md`) · Design doc: `spec-factory-v5.md`
 
 ## What changed from plan v1
@@ -51,7 +51,7 @@ Re-plans (item 84's "next free ids") and a later Docker or cron ticket enter the
 
 ## BH-1 — Store, requests, audit log, results table, STATUS parser, composer, CLI guards, config
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
 
 Depends on: none
 Parallel-safe: no (first in chain; everything else edits `factory/cli.py` after it)
@@ -89,7 +89,7 @@ Open question carried (per the gate's ruling): Nanobot's own test and lint comma
 
 ## BH-2a — Bare repo, identities and keys, `factory init`, pre-receive hook rules 1–3 and 5, state push
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
 
 Depends on: BH-1
 Parallel-safe: no (edits `factory/cli.py`, `store.py`, `results.py` from BH-1)
@@ -114,7 +114,7 @@ Not verified by the spec writer and therefore an implementer stop-and-escalate p
 
 ## BH-2b — Merge gate (hook rule 4 via `gate.py`), `factory merge`, gate runner, approval-row writers
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
 
 Depends on: BH-2a
 Parallel-safe: no (edits `factory/hook.py`, `factory/cli.py`, `store.py` from BH-2a/BH-1)
@@ -138,7 +138,7 @@ Out of scope: `approve-spec`, `request-changes`, `resolve`, `queue`, `queue appl
 
 ## BH-3 — Human surface, resolution commands, spec approval and export
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
 
 Depends on: BH-2b
 Parallel-safe: no (edits `factory/cli.py`, which BH-4 also edits)
@@ -164,7 +164,7 @@ Out of scope: `approve-pr`/`approve-guardrail` (BH-2b); `factory render`, agent
 
 ## BH-4 — `factory render` from the in-repo design doc, preamble, the ten agent definitions, AGENTS.md section
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
 
 Depends on: BH-2b (item 56 needs the bare repo and a `ticket/*` branch), BH-3 (both edit `factory/cli.py`; BH-3 merges first)
 Parallel-safe: no (edits `factory/cli.py`; must not be in flight with BH-3)
@@ -186,7 +186,7 @@ Out of scope: `.claude/skills/factory/SKILL.md` (BH-5, since it documents the wo
 
 ## BH-5 — Intake workflow: `runRole`, clerk calls, stub seam, `/factory` entry skill
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
 
 Depends on: BH-3, BH-4
 Parallel-safe: no (edits `factory/cli.py`; next in chain)
@@ -209,7 +209,7 @@ Out of scope: `build.js`, `retro.js`, `ready-implementers`, `ready-checkers`, `t
 
 ## BH-6 — Build workflow: planner → implementer → reviewer ‖ verifier → join → merge; parent close; checker isolation; verifier as CI
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
 
 Depends on: BH-5
 Parallel-safe: no (edits `factory/cli.py`, `compose.py`, `results.py`, SKILL.md; next in chain)
@@ -232,7 +232,7 @@ Out of scope: `retro.js`, `retro-input`, `audit-sample`; Docker, cron, pre-empti
 
 ## BH-7 — Audit sample, retro input, retro workflow
 
-Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
+Parent: `dev/build-harness.spec.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.
 
 Depends on: BH-6
 Parallel-safe: no (last in chain; edits `factory/cli.py`, `compose.py`, SKILL.md)
diff --git a/specs/build-harness.md b/dev/build-harness.spec.md
similarity index 100%
rename from specs/build-harness.md
rename to dev/build-harness.spec.md
diff --git a/issues/README.md b/dev/issues.md
similarity index 100%
rename from issues/README.md
rename to dev/issues.md
diff --git a/docs/changelog.md b/docs/changelog.md
new file mode 100644
index 0000000..66c27e3
--- /dev/null
+++ b/docs/changelog.md
@@ -0,0 +1,47 @@
+# Changelog
+
+Six review rounds ran on this doc, using the reviewer prompt in the appendix. Round 1 was a self-review by the drafting agent; rounds 2 and 3 were separate sessions; rounds 4 and 5 ran a reviewer, a critic, and a copy editor in parallel, each in a fresh context, with round 5 checking only prior findings and changed text; round 6 was a full pass after the bootstrap run. Findings applied, in order:
+
+1. Acceptance criteria are labeled NEW (must fail today) or REGRESSION (must pass before and after).
+2. Only existing tests are protected; adding tests is expected.
+3. UNTRUSTED INPUT rule added to the preamble.
+4. CI failures and merge conflicts route to the implementer as findings.
+5. The sycophancy red flag is a FIXED with no matching diff, not blanket acceptance.
+6. Merge requires green CI plus APPROVE and VERIFIED on the current head commit; both checkers record the commit.
+7. "Tests to change" section in the spec is the only authorization to alter an existing test; critic, planner, implementer, reviewer, and the human gate all reference it.
+8. NEW criteria must fail today for the reason the spec states, not because a test file doesn't exist yet.
+9. A spec marked NEEDS-SPLIT with named seams passes critic rubric #3.
+10. Checkers run in a disposable checkout with no push credentials; guardrail files are enforced by CODEOWNERS and branch protection.
+11. FAILED and REQUEST-CHANGES route to the implementer; SPEC-DEFECT routes to the human queue.
+12. Harness pieces and routing table added.
+13. Protected paths no longer deadlock the merge: the spec's Risk section declares them, the human approves them at the spec gate, and the reviewer gives the STATUS the code earns instead of always escalating.
+14. The PR loop joins: the dispatcher waits for CI and both checkers on a head before routing, and one implementer run receives both outputs.
+15. Round-2 inputs are declared: prior findings and the author's responses reach the checkers, and both the spec and the PR description have a Responses section.
+16. A round is one checker pass; the counter increments on author re-entry, not on rebases.
+17. Merge conflicts have a routing row; the merge gate requires the head to contain current main, so the last verification covers the merged state.
+18. New tests go in new files, matching path-based enforcement; the spec gate's "Tests to change" approval is the piece-8 record for exactly those files.
+19. Guardrail paths and protected paths are defined once and named everywhere else.
+20. Checker and gate-runner runs hold no secrets, since they execute PR code before any security check.
+21. Verifier: gate failure is FAILED; a wrong-reason NEW criterion is SPEC-DEFECT; probes FAIL only on special-casing or a stated criterion.
+22. Retro no longer proposes deleting rules for lack of incidents.
+23. Triage routes on STATUS; Triage and Retro have entry rows; max-round and ESCALATIONS resolution defined; fix rounds push to the existing branch.
+24. No merge-gate override: a max-round or SPEC-DEFECT ticket returns to the implementer with the human's ruling, or closes. The human may amend the sub-ticket or spec first.
+25. A gate failure counts as a round (it is a verifier FAILED); the CI result joins the single implementer dispatch.
+26. CODEOWNERS is not used for tests, since it fires on added files; existing tests get a modified-or-deleted check against "Tests to change".
+27. Retro is mandatory: after the weekly audit or on demand. It writes a causal chain per incident, separates harness defects from prompt problems, and every proposed rule names the metric it should move; rules that don't move it are reverted (after agent-retro and the autoresearch keep/discard loop).
+28. A run that exceeds its time or token budget is killed and its ticket parked (piece 3).
+29. Retro PRs and verified git reverts can merge: the one stated exception to the merge gate, since a human reads the whole diff and there are no acceptance commands to verify.
+30. Budget kills are a parking state with a resolution path and placeholders; only the harness identity and humans write the ticket store.
+31. Retro receives run and outcome counts so its metrics have denominators; reversion waits {2} retros.
+32. Full pass after the bootstrap run: CI failure joins the PR-loop dispatch; a parent closes only after one verifier run on main against its full Acceptance list; a revert is the inverse of a recorded merge diff, human-authored, approved at the guardrail gate; the ticket store is a dedicated branch with a store CLI that holds the guards; checker containers hold no secrets even in the smallest build; the Workflow v0 note states it gives fresh context, not isolation; verifier defaults to Opus; REVISE and REQUEST-CHANGES require a BLOCKING finding; CLARIFY, BLOCKED, and ESCALATE resolutions defined; retro counts are broken down by model and reversion needs {N} runs.
+33. Round 2 of the full pass: the parent-close verifier run declares its inputs (head = main, base = main before the parent's first merge) and the verifier prompt accepts them; a parent-close failure or a closed sub-ticket parks the parent for re-plan or close; a not-parallel-safe sub-ticket excludes siblings in both directions; the no-sub-ticket row dispatches the gate runner; humans record approvals by pushing to the tickets branch as themselves; the verifier is the stated exception to the checker-model rules.
+34. After two real runs parked valid verdicts as harness bugs (2026-10-01), the trailer is read by its labels: a wrapped CONFIDENCE reason or a remark between STATUS and CONFIDENCE is continuation, not a parse failure; an ESCALATIONS line of `none` followed by prose routes as none and the prose is kept with the run; `none` with further lines below it is a real list.
+35. After the P0 intake run: the clerk relays the store CLI's stdout verbatim with the exit code and stderr, and the workflow script parses the JSON itself; given a schema shaped like the command's output, a clerk re-typed a ticket read (an invented field, the nested object stringified), the answer still validated, and the ticket was misrouted.
+36. After the P0 run (2026-10-01): a question returns to the role that asked with the answer and that role's previous output, so a re-run Triage or Spec writer reads the answer against the question it asked instead of re-deriving it; a requester's CLARIFY answer follows the same rule, and two Answered rows in the routing table carry the same inputs.
+37. The spec FORMAT gains an optional Operator steps section: actions or checks on live or protected state that only the operator can perform after merge. They are not acceptance and change no routing; the human approves them at the spec gate, and critic rubric 2 checks that they sit there and not under Acceptance. No tracked post-merge obligation.
+38. After the intake run against this repo (2026-10-01): the role-context block is declared in the Harness section as a per-repo input every role receives first, ahead of its declared INPUT and the routing table's "Receives"; where the block is kept stays open.
+39. Specs live in an OpenSpec tree under a forked `spec-factory` schema (Harness, Spec store): current truth per capability, one change folder per ticket (proposal, design, delta, tasks, and the factory-only `verification.md`), and a repo-level `decisions.md`. The spec writer's FORMAT is one document in those parts, and the delta's scenarios are the Acceptance items; the spec writer and the critic receive current truth; the planner's output is the change's `tasks.md`; the spec gate pins the change folder; parent close archives it (apply the deltas, move the folder, append the decisions). Roles, round limits, gates and harness pieces 1–12 are unchanged.
+40. After the pilot specs on Nanobot green (2026-10-01): archive has two more refusals, no change folder (a spec pinned before the repo had an `openspec/` tree) and no spec store. Each parks the parent like a delta that does not apply, but the human closes that parent as applied: current truth and `decisions.md` are not updated, and the spec is re-intaken as a new ticket if current truth should carry it.
+41. After the T-0010 spec gate (2026-10-02), where the operator could not read an approved Problem section without a translation: the spec writer writes the Problem section in plain words for the operator who approves the spec at the gate, a deeply technical reader new to this system's internals, with each term of art specific to this system glossed on first use and the detail left to Evidence and Root cause; critic rubric 6 reads the Problem as that operator, and a first paragraph that does not say what is wrong and for whom, or uses an unglossed term specific to this system (even one a careful reader could infer), is BLOCKING.
+
+Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/spec-factory.md b/docs/design.md
similarity index 85%
rename from docs/spec-factory.md
rename to docs/design.md
index f7d825a..a150126 100644
--- a/docs/spec-factory.md
+++ b/docs/design.md
@@ -28,6 +28,8 @@ Three wiring rules matter more than any wording:
 - **Checkers can't edit.** Reviewers and verifiers run in a disposable checkout with no push or merge credentials. They report; authors fix.
 - **Guardrail paths are human-owned.** They change only through PRs a human approves. Enforce this with CODEOWNERS and branch protection, not prompt wording. New tests in new files need no extra approval.
 
+This document's changelog is `docs/changelog.md`, and `docs/prompts/` holds a verbatim copy of each prompt block in it, changed only by re-copying that block.
+
 ## Harness: functional pieces
 
 The prompts say what each role does. The harness enforces the wiring rules: fresh context per checker, checkers without write access, approvals bound to a commit, round limits, and routing by STATUS. Prompt text cannot enforce any of that. The table lists the pieces any harness needs, what GitHub provides for each, and the minimum a portable substitute must do. Build against the "What it must do" column, not GitHub's shape.
@@ -675,54 +677,6 @@ STATUS: PROPOSED | NO-CHANGES
 CONFIDENCE / ESCALATIONS
 ```
 
-## Changelog
-
-Six review rounds ran on this doc, using the reviewer prompt in the appendix. Round 1 was a self-review by the drafting agent; rounds 2 and 3 were separate sessions; rounds 4 and 5 ran a reviewer, a critic, and a copy editor in parallel, each in a fresh context, with round 5 checking only prior findings and changed text; round 6 was a full pass after the bootstrap run. Findings applied, in order:
-
-1. Acceptance criteria are labeled NEW (must fail today) or REGRESSION (must pass before and after).
-2. Only existing tests are protected; adding tests is expected.
-3. UNTRUSTED INPUT rule added to the preamble.
-4. CI failures and merge conflicts route to the implementer as findings.
-5. The sycophancy red flag is a FIXED with no matching diff, not blanket acceptance.
-6. Merge requires green CI plus APPROVE and VERIFIED on the current head commit; both checkers record the commit.
-7. "Tests to change" section in the spec is the only authorization to alter an existing test; critic, planner, implementer, reviewer, and the human gate all reference it.
-8. NEW criteria must fail today for the reason the spec states, not because a test file doesn't exist yet.
-9. A spec marked NEEDS-SPLIT with named seams passes critic rubric #3.
-10. Checkers run in a disposable checkout with no push credentials; guardrail files are enforced by CODEOWNERS and branch protection.
-11. FAILED and REQUEST-CHANGES route to the implementer; SPEC-DEFECT routes to the human queue.
-12. Harness pieces and routing table added.
-13. Protected paths no longer deadlock the merge: the spec's Risk section declares them, the human approves them at the spec gate, and the reviewer gives the STATUS the code earns instead of always escalating.
-14. The PR loop joins: the dispatcher waits for CI and both checkers on a head before routing, and one implementer run receives both outputs.
-15. Round-2 inputs are declared: prior findings and the author's responses reach the checkers, and both the spec and the PR description have a Responses section.
-16. A round is one checker pass; the counter increments on author re-entry, not on rebases.
-17. Merge conflicts have a routing row; the merge gate requires the head to contain current main, so the last verification covers the merged state.
-18. New tests go in new files, matching path-based enforcement; the spec gate's "Tests to change" approval is the piece-8 record for exactly those files.
-19. Guardrail paths and protected paths are defined once and named everywhere else.
-20. Checker and gate-runner runs hold no secrets, since they execute PR code before any security check.
-21. Verifier: gate failure is FAILED; a wrong-reason NEW criterion is SPEC-DEFECT; probes FAIL only on special-casing or a stated criterion.
-22. Retro no longer proposes deleting rules for lack of incidents.
-23. Triage routes on STATUS; Triage and Retro have entry rows; max-round and ESCALATIONS resolution defined; fix rounds push to the existing branch.
-24. No merge-gate override: a max-round or SPEC-DEFECT ticket returns to the implementer with the human's ruling, or closes. The human may amend the sub-ticket or spec first.
-25. A gate failure counts as a round (it is a verifier FAILED); the CI result joins the single implementer dispatch.
-26. CODEOWNERS is not used for tests, since it fires on added files; existing tests get a modified-or-deleted check against "Tests to change".
-27. Retro is mandatory: after the weekly audit or on demand. It writes a causal chain per incident, separates harness defects from prompt problems, and every proposed rule names the metric it should move; rules that don't move it are reverted (after agent-retro and the autoresearch keep/discard loop).
-28. A run that exceeds its time or token budget is killed and its ticket parked (piece 3).
-29. Retro PRs and verified git reverts can merge: the one stated exception to the merge gate, since a human reads the whole diff and there are no acceptance commands to verify.
-30. Budget kills are a parking state with a resolution path and placeholders; only the harness identity and humans write the ticket store.
-31. Retro receives run and outcome counts so its metrics have denominators; reversion waits {2} retros.
-32. Full pass after the bootstrap run: CI failure joins the PR-loop dispatch; a parent closes only after one verifier run on main against its full Acceptance list; a revert is the inverse of a recorded merge diff, human-authored, approved at the guardrail gate; the ticket store is a dedicated branch with a store CLI that holds the guards; checker containers hold no secrets even in the smallest build; the Workflow v0 note states it gives fresh context, not isolation; verifier defaults to Opus; REVISE and REQUEST-CHANGES require a BLOCKING finding; CLARIFY, BLOCKED, and ESCALATE resolutions defined; retro counts are broken down by model and reversion needs {N} runs.
-33. Round 2 of the full pass: the parent-close verifier run declares its inputs (head = main, base = main before the parent's first merge) and the verifier prompt accepts them; a parent-close failure or a closed sub-ticket parks the parent for re-plan or close; a not-parallel-safe sub-ticket excludes siblings in both directions; the no-sub-ticket row dispatches the gate runner; humans record approvals by pushing to the tickets branch as themselves; the verifier is the stated exception to the checker-model rules.
-34. After two real runs parked valid verdicts as harness bugs (2026-10-01), the trailer is read by its labels: a wrapped CONFIDENCE reason or a remark between STATUS and CONFIDENCE is continuation, not a parse failure; an ESCALATIONS line of `none` followed by prose routes as none and the prose is kept with the run; `none` with further lines below it is a real list.
-35. After the P0 intake run: the clerk relays the store CLI's stdout verbatim with the exit code and stderr, and the workflow script parses the JSON itself; given a schema shaped like the command's output, a clerk re-typed a ticket read (an invented field, the nested object stringified), the answer still validated, and the ticket was misrouted.
-36. After the P0 run (2026-10-01): a question returns to the role that asked with the answer and that role's previous output, so a re-run Triage or Spec writer reads the answer against the question it asked instead of re-deriving it; a requester's CLARIFY answer follows the same rule, and two Answered rows in the routing table carry the same inputs.
-37. The spec FORMAT gains an optional Operator steps section: actions or checks on live or protected state that only the operator can perform after merge. They are not acceptance and change no routing; the human approves them at the spec gate, and critic rubric 2 checks that they sit there and not under Acceptance. No tracked post-merge obligation.
-38. After the intake run against this repo (2026-10-01): the role-context block is declared in the Harness section as a per-repo input every role receives first, ahead of its declared INPUT and the routing table's "Receives"; where the block is kept stays open.
-39. Specs live in an OpenSpec tree under a forked `spec-factory` schema (Harness, Spec store): current truth per capability, one change folder per ticket (proposal, design, delta, tasks, and the factory-only `verification.md`), and a repo-level `decisions.md`. The spec writer's FORMAT is one document in those parts, and the delta's scenarios are the Acceptance items; the spec writer and the critic receive current truth; the planner's output is the change's `tasks.md`; the spec gate pins the change folder; parent close archives it (apply the deltas, move the folder, append the decisions). Roles, round limits, gates and harness pieces 1–12 are unchanged.
-40. After the pilot specs on Nanobot green (2026-10-01): archive has two more refusals, no change folder (a spec pinned before the repo had an `openspec/` tree) and no spec store. Each parks the parent like a delta that does not apply, but the human closes that parent as applied: current truth and `decisions.md` are not updated, and the spec is re-intaken as a new ticket if current truth should carry it.
-41. After the T-0010 spec gate (2026-10-02), where the operator could not read an approved Problem section without a translation: the spec writer writes the Problem section in plain words for the operator who approves the spec at the gate, a deeply technical reader new to this system's internals, with each term of art specific to this system glossed on first use and the detail left to Evidence and Root cause; critic rubric 6 reads the Problem as that operator, and a first paragraph that does not say what is wrong and for whom, or uses an unglossed term specific to this system (even one a careful reader could infer), is BLOCKING.
-
-Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
-
 ## Appendix: reviewer prompt
 
 Reusable for reviewing any prompt set.
diff --git a/prompts/00-preamble.md b/docs/prompts/00-preamble.md
similarity index 100%
rename from prompts/00-preamble.md
rename to docs/prompts/00-preamble.md
diff --git a/prompts/01-triage.md b/docs/prompts/01-triage.md
similarity index 100%
rename from prompts/01-triage.md
rename to docs/prompts/01-triage.md
diff --git a/prompts/02-spec-writer.md b/docs/prompts/02-spec-writer.md
similarity index 100%
rename from prompts/02-spec-writer.md
rename to docs/prompts/02-spec-writer.md
diff --git a/prompts/03-spec-critic.md b/docs/prompts/03-spec-critic.md
similarity index 100%
rename from prompts/03-spec-critic.md
rename to docs/prompts/03-spec-critic.md
diff --git a/prompts/04-planner.md b/docs/prompts/04-planner.md
similarity index 100%
rename from prompts/04-planner.md
rename to docs/prompts/04-planner.md
diff --git a/prompts/05-implementer.md b/docs/prompts/05-implementer.md
similarity index 100%
rename from prompts/05-implementer.md
rename to docs/prompts/05-implementer.md
diff --git a/prompts/06-code-reviewer.md b/docs/prompts/06-code-reviewer.md
similarity index 100%
rename from prompts/06-code-reviewer.md
rename to docs/prompts/06-code-reviewer.md
diff --git a/prompts/07-verifier.md b/docs/prompts/07-verifier.md
similarity index 100%
rename from prompts/07-verifier.md
rename to docs/prompts/07-verifier.md
diff --git a/prompts/08-retro.md b/docs/prompts/08-retro.md
similarity index 100%
rename from prompts/08-retro.md
rename to docs/prompts/08-retro.md
diff --git a/prompts/99-doc-reviewer.md b/docs/prompts/99-doc-reviewer.md
similarity index 100%
rename from prompts/99-doc-reviewer.md
rename to docs/prompts/99-doc-reviewer.md
diff --git a/intake/README.md b/intake/README.md
index d0af6b0..de69e67 100644
--- a/intake/README.md
+++ b/intake/README.md
@@ -1,7 +1,7 @@
 # intake/ — SCRATCH
 
 **Scratch area, not part of the design.** A throwaway spec-factory intake instance that runs
-this repo's GitHub issues (index: `../issues/README.md`) through intake (Triage → Spec writer ⇄ Critic → human gate →
+this repo's GitHub issues (index: `../dev/issues.md`) through intake (Triage → Spec writer ⇄ Critic → human gate →
 Planner) against this repo. Delete the whole directory once the issues are filed and closed;
 nothing outside it depends on it.
 
@@ -39,7 +39,7 @@ Ticket ids are local to this store: T-0001 here is issue 01, not green's SPEC-21
 | T-0010 | [#10](https://github.com/danielphang/spec-factory/issues/10) |
 | T-0011 | [#11](https://github.com/danielphang/spec-factory/issues/11) |
 
-T-0001..T-0007: spec approved at the gate and applied on `main` (merges listed in `issues/README.md`).
+T-0001..T-0007: spec approved at the gate and applied on `main` (merges listed in `dev/issues.md`).
 Closed 2026-10-01 as applied by hand. The Planner was run on T-0001..T-0003 anyway, as its first
 real test: each run found the spec already on `main` and escalated instead of planning no-op
 work, which is the right call. Lesson for the design (feeds T-0008's lifecycle): the store has no
diff --git a/intake/instance/context.md b/intake/instance/context.md
index 79cbf2e..2e7f98a 100644
--- a/intake/instance/context.md
+++ b/intake/instance/context.md
@@ -1,22 +1,24 @@
 ## Context for this run (composed by the harness, not part of the request)
 
 Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
-documents, not code: `docs/spec-factory.md` (the design document, source of truth),
-`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
-decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
+documents, not code: `docs/design.md` (the design document, source of truth) with its
+changelog in `docs/changelog.md`, `dev/build-harness.spec.md` (the spec for building the
+harness), `dev/build-harness.plan.md` (the Planner's decomposition of it;
+`dev/P0-intake-skeleton.md` is the walking skeleton), and `docs/prompts/`
 (each file a verbatim copy of one prompt block in the design doc; it changes only by
 re-copying that block). Your shell may start in another directory: use absolute paths, or
 `cd ~/dev/spec-factory && <cmd>`.
 
 The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
-(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
+(branch `feat/lionbot-v3`, built from `dev/P0-intake-skeleton.md`). Read it only to observe
 what a fix does today; never write there, and never copy its test names, line numbers or
 commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).
 
 Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
 `git diff --check` against the documents). A change to the design doc keeps its own
-conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
-new text, and any `prompts/` file whose block changed re-copied from it.
+conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
+consistent with the new text, and any `docs/prompts/` file whose block changed re-copied
+from it.
 
 The request is an issue draft, written from a real pipeline run: where in the documents,
 what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
