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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0076-reviewer/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/intake/state/runs/run-0076-reviewer/wt` (branch `factory/T-0012.4`, base `f809c694fed21286bd2c1c234943c3dd96656db3`, head `010d1b00c5835c7022a72771c63f63f8b6ab3707`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Sub-ticket T-0012.4

## T-0012.4 / Harness lock: refuse an unaccepted or modified harness on the instance's own store, `--accept-harness`

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: T-0012.3

Parallel-safe: no, with T-0012.6. E's lock must be written after this sub-ticket's harness commits have merged. It is parallel-safe with T-0012.5.

Scope: C.2–C.5.
- C.1 already exists from T-0012.3.
- The check runs only when the store in use is the instance's own store.
- `init` and `paths` are exempt.
- The dirty check uses `git -C <running harness> status --porcelain -- factory bin/factory agents pyproject.toml uv.lock`.

Acceptance (first `uv sync --frozen`):
- **lock-mismatch-refused** → NEW [specs/harness-lock]. THEN `init=0`, then `exit=2 tickets=0 hint=1`.
- **accept-current-revision-rewrites-lock** → NEW [specs/harness-lock]. THEN `init=0`, then `exit=0 lock_is_rev=yes logged=N`, N ≥ 1.
- **accept-other-revision-refused** → REGRESSION (relabelled by the operator, 2026-10-03: passes at base vacuously, per implementer run-0069; the discriminating evidence is the new C tests) [specs/harness-lock]. THEN `init=0`, then `exit=2 lock=0000000000000000000000000000000000000000 tickets=0`.
- **throwaway-store-ignores-lock** → REGRESSION (relabelled by the operator, 2026-10-03: passes at base vacuously, per implementer run-0069; the discriminating evidence is the new C tests) [specs/harness-lock]. THEN `init=0`, then `exit=0 ticket=[T-0001.yaml]`.
- **dirty-harness-refused** → NEW [specs/harness-lock]. THEN `init=0`, then `exit=2 tickets=0 names=1`.
- **missing-lock-refused** → NEW (intermediate; C.2 "or the lock is missing").
  - WHEN the parent's lock-mismatch-refused command, with `printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock` replaced by `rm -f $T/.factory/harness.lock`.
  - THEN `init=0`, then `exit=2 tickets=0 hint=1`.
- **init-and-paths-exempt** → REGRESSION (relabelled by the operator, 2026-10-03: passes at base vacuously, per implementer run-0069; the discriminating evidence is the new C tests) (intermediate; C.2).
  - WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && cd $T && $H/bin/factory init --repo-name demo >/dev/null 2>&1; printf '%040d\n' 0 > .factory/harness.lock; $H/bin/factory paths >/dev/null 2>&1; p=$?; $H/bin/factory init >/dev/null 2>&1; echo "paths=$p init=$? lock=$(cat .factory/harness.lock)"`
  - THEN `paths=0 init=0 lock=0000000000000000000000000000000000000000`.
- **accept-does-not-override-dirty** → REGRESSION (relabelled by the operator, 2026-10-03: passes at base vacuously, per implementer run-0069; the discriminating evidence is the new C tests) (intermediate; C.4).
  - WHEN `H=$PWD; C=$(mktemp -d)/h; git clone -q "$H" "$C" && uv sync -q --frozen --project "$C"; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && cd $T && "$C"/bin/factory init --repo-name demo >/dev/null 2>&1; L=$(cat .factory/harness.lock); REV=$("$C"/bin/factory paths | python3 -c 'import json,sys; print(json.load(sys.stdin)["harness_revision"])'); echo '# local edit' >> "$C"/factory/__init__.py; printf '# demo\n\nDo the thing.\n' > r.md; "$C"/bin/factory --accept-harness "$REV" ticket new --file r.md >/dev/null 2>&1; echo "exit=$? lock_same=$([ "$(cat .factory/harness.lock)" = "$L" ] && echo yes || echo no) tickets=$(ls .factory/state/tickets 2>/dev/null | wc -l | tr -d ' ')"`
  - THEN `exit=2 lock_same=yes tickets=0`.
- **All nine T-0012.3 factory-instance and harness-home scenarios** → REGRESSION, with the same THEN as at T-0012.3. Each makes a fresh `init`, whose lock matches, so the new checks must not refuse them. Run from a clean checkout: an uncommitted harness edit in the checkout under test would now refuse them, by design.
- **harness-suite-passes-after-uv-sync** → REGRESSION. N ≥ 70, plus the new C tests, no `failed`/`error`.
- **green-harness-still-present** → REGRESSION.
- **whitespace (sub-ticket diff)** → REGRESSION. `exit=0`.

Tests to change: `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides` (operator ruling, 2026-10-03, on implementer run-0069's escalation). It was written in T-0012.3, before the lock, and builds an instance `alt` with no `harness.lock`, which C.2 now refuses. Add one line after `(alt / "context.md").write_text("x\n")`: `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`. C.2 stands as written; `config` is not exempted. Otherwise new C test files only.

Protected paths: none of instance B's classes.

Out of scope:
- Writing instance B's `.factory/harness.lock` (E).
- Any refusal of a mismatch between `instance.yaml`'s `harness:` value and the running checkout. The spec has none.
- Changes to `init` or `paths` beyond keeping them exempt.

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

Sub-ticket: T-0012.4 (parent `intake/state/specs/T-0012/v3.md`, design C.2–C.5). Branch `factory/T-0012.4`, worktree `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.4`. There is no remote, so the branch is the PR. Head is `010d1b00c5835c7022a72771c63f63f8b6ab3707`. Merge-base with `main` is `bed7e28`. `main` is `f809c69`, which changes only `intake/state/**`. I did not merge it in: this is not a conflict run, and the gate uses `main...HEAD`.

This run continues implementer run-0069, which left the C implementation on the branch and stopped as BLOCKED on one existing test. The operator has since ruled on that test (Tests to change). This run applied that ruling, fixed a whitespace slip in run-0069's commit, re-read the C code, and re-ran every acceptance command and gate.

Commits (`git log --oneline main..HEAD`):
- `7a89605` test(T-0012.4): harness lock tests (C.2-C.5), red before the guard (run-0069)
- `fe6303c` harness(T-0012.4): harness lock — refuse an unaccepted or modified harness on the instance's own store, --accept-harness (C.2-C.4) (run-0069)
- `954eff7` test(T-0012.4): changed paths are listed in git's order; compare them as a set (run-0069)
- `1ac0ec3` test(T-0012.4): give the pre-lock instance test a lock (operator ruling 2026-10-03; C.2 stands) (this run)
- `010d1b0` harness(T-0012.4): restore the space lost before = on PROTECTED_PLACEHOLDER (this run)

Final diff (`git diff --stat main...HEAD`): `factory/cli.py` +6/-1, `factory/instance.py` +52, `tests/factory/test_harness_lock.py` +281 (new), `tests/factory/test_instance.py` +1. In total, 4 files, 340 insertions and 1 deletion.

## What changed (per lettered part)

- **C.2: lock check on the instance's own store.**
  - `factory/cli.py` `main()` now resolves the instance (`instance.require()`), loads its config and gets the store root. It then calls `instance.guard(inst, cfg, root, a.accept_harness)` before running the command.
  - `init` and `paths` still return through the existing early branch, so they are exempt.
  - `guard()` (`factory/instance.py`) returns at once unless `is_own_store()` is true, which means `FACTORY_STATE` is unset or resolves to the instance's `state_dir`.
  - It compares `read_lock()`, the stripped first line of `<instance>/harness.lock` (`None` when the file is missing or empty), with `harness_revision()` (C.1, from T-0012.3).
  - On a mismatch it refuses with `harness <rev> is not the revision this instance accepted (<lock>|none); rerun with --accept-harness <rev> to accept it`, and the command exits 2. Every refusal happens before the command runs, so nothing is written.
- **C.3: `--accept-harness SHA`.**
  - It is a top-level argparse option (`factory/cli.py`, `build_parser`), so it is written before the subcommand.
  - The SHA must match `[0-9a-f]{40}` and equal the running revision. Otherwise the command exits 2, and the lock is unchanged and nothing is logged.
  - On a match, the harness writes `<rev>\n` to the lock and logs a `harness.accepted` event (`instance`, `old`, `new`) in the instance's store. Then the command runs.
- **C.4: uncommitted harness edits are refused.**
  - `harness_changes()` runs `git -C <HARNESS> status --porcelain -- factory bin/factory agents pyproject.toml uv.lock`. `<HARNESS>` is the running checkout.
  - If git prints anything, the command is refused with `harness <path> has uncommitted changes:` followed by one path per line.
  - This check runs before the accept step, so `--accept-harness` cannot override it.
  - If `git status` fails, or the revision cannot be read, the command is also refused (exit 2) rather than allowed through.
- **C.5:** new test file `tests/factory/test_harness_lock.py` (24 cases).
- **Changes in this run:**
  - `tests/factory/test_instance.py`: one line, exactly as the operator ruled (see Tests added/changed).
  - `factory/instance.py`: `fe6303c` had turned `PROTECTED_PLACEHOLDER = "…"` into `PROTECTED_PLACEHOLDER ="…"`. That was an accidental formatting change. `010d1b0` restores the line, which is now identical to `main` again. Behaviour does not change.

## Acceptance results

Method:
- I extracted every WHEN from input.md with a script (`str` slicing between the backticks), not by retyping, and ran each one with `bash` from the checkout under test after `uv sync --frozen`.
- For missing-lock-refused, the script substituted `rm -f $T/.factory/harness.lock` for the `printf … > $T/.factory/harness.lock` part of lock-mismatch-refused, after asserting that the original text appears exactly once.
- **Before:** a scratch clone of the branch, detached at `main` (`f809c69`, the recorded base, with harness code identical to `bed7e28`), with its own `uv sync --frozen`.
- **After:** the worktree at `010d1b0`. `git status --porcelain` was empty before and after the runs.

| Scenario | Label | Before (`f809c69`) | After (`010d1b0`) |
|---|---|---|---|
| lock-mismatch-refused | NEW | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` |
| accept-current-revision-rewrites-lock | NEW | `init=0` / `exit=2 lock_is_rev=no logged=0` | `init=0` / `exit=0 lock_is_rev=yes logged=1` |
| accept-other-revision-refused | REGRESSION | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` | same |
| throwaway-store-ignores-lock | REGRESSION | `init=0` / `exit=0 ticket=[T-0001.yaml]` | same |
| dirty-harness-refused | NEW | `init=0` / `exit=0 tickets=1 names=0` | `init=0` / `exit=2 tickets=0 names=1` |
| missing-lock-refused | NEW | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` |
| init-and-paths-exempt | REGRESSION | `paths=0 init=0 lock=0000000000000000000000000000000000000000` | same |
| accept-does-not-override-dirty | REGRESSION | `exit=2 lock_same=yes tickets=0` | same |
| harness-files-in-repo | REGRESSION (T-0012.3) | — | `agents=6 green_only=0` |
| role-prompt-text-unchanged | REGRESSION (T-0012.3) | — | `changed=0 of 14` |
| init-creates-instance-in-throwaway-target | REGRESSION (T-0012.3) | — | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` |
| store-command-from-subdirectory-uses-target-instance | REGRESSION (T-0012.3) | — | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` |
| command-outside-any-instance-refused | REGRESSION (T-0012.3) | — | `exit=2 created=0 names_instance=1` |
| factory-instance-override-from-elsewhere | REGRESSION (T-0012.3) | — | `init=0` / `found=1` |
| composed-input-opens-with-instance-context | REGRESSION (T-0012.3) | — | `init=0` / `first=[CTX-MARKER for demo]` |
| run-system-prompt-names-instance | REGRESSION (T-0012.3) | — | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` |
| paths-name-harness-workflows-and-instance | REGRESSION (T-0012.3) | — | `init=0` / `True True True True` |
| harness-suite-passes-after-uv-sync | REGRESSION | (run-0069 at `bed7e28`: `sync=0` / `92 passed`) | `sync=0` / `116 passed in 76.71s (0:01:16)` |
| green-harness-still-present | REGRESSION | — | `green keeps its harness` |
| whitespace (sub-ticket diff) | REGRESSION | — | `git diff --check main...HEAD` → `exit=0` |

Every NEW criterion failed at base as described and now passes. Every REGRESSION criterion passes. The four C regressions pass at base vacuously, as the operator's relabel notes. The discriminating evidence is the new tests below.

I also ran whitespace-clean with `BASE=$(git rev-parse main)`: `git diff --check "$BASE" HEAD` → `exit=0`.

Gate commands, run from the worktree exactly as written:
- `git diff --check main...HEAD` → no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 77.48s (0:01:17)`.

## Tests added/changed

- **Added: `tests/factory/test_harness_lock.py`** (24 cases, run-0069).
  - Red evidence, re-run this run: I copied the file into the base clone and ran it against base code, which gave `18 failed, 6 passed in 5.10s`.
  - The 6 that pass at base are the "must not refuse" cases: `test_fresh_init_lock_is_the_running_revision_and_commands_run`, `test_lock_compares_its_stripped_first_line`, `test_init_and_paths_are_exempt_and_leave_the_lock`, `test_throwaway_store_runs_whatever_the_lock_says`, `test_ignored_and_non_harness_changes_do_not_count` and `test_modified_harness_still_runs_throwaway_stores_init_and_paths`.
  - All 24 pass at head.
  - Coverage:
    - **C.2:** a mismatched, empty or missing lock is refused with the exact message. Five different commands are refused. `init` and `paths` are exempt. `FACTORY_STATE` pointing elsewhere is not checked, and `FACTORY_STATE` naming the own store is checked.
    - **C.3:** accepting the current revision rewrites the lock and logs `old`/`new`. A short SHA, another 40-hex value, a prefix and an uppercase SHA are each refused, with the tree unchanged.
    - **C.4**, on a local clone so this checkout is never edited: a modified tracked file and an untracked file under `agents/` are refused and named. `--accept-harness` does not override a dirty harness. Ignored files and non-harness edits do not count. A dirty harness still runs throwaway stores, `init` and `paths`.
    - **Upgrade flow:** a docs-only commit does not trip the lock, a `factory/` commit does, and `--accept-harness <new>` clears it.
- **Changed: `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides`.**
  - It is listed under Tests to change by the operator's ruling of 2026-10-03.
  - The change is one added line after `(alt / "context.md").write_text("x\n")`: `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`.
  - **Why:** the test predates the lock and builds an instance with no `harness.lock`, which C.2 refuses.
  - Before the line, at `954eff7` with a clean tree: `1 failed, 21 deselected`, and the assertion at line 247 fails. After it: `1 passed, 21 deselected in 0.61s`.
  - No assertion was changed, and `config` was not exempted.

## Known gaps and uncertainties

- **The suite passes only from a committed harness tree.**
  - Evidence: in a scratch clone of head, I appended `# dev edit` to `factory/__init__.py` and ran the suite. It gave `23 failed, 93 passed`: 17 in `test_harness_lock.py` and 6 in `test_instance.py`.
  - Cause: those tests build own-store targets (`FACTORY_STATE` unset) driven by this checkout's `bin/factory`, so C.4 refuses them by design.
  - C.4's prose says "a harness under development ... still runs its own tests against throwaway stores". That holds for the imported suite but not for the B/C tests, which use own stores.
  - The gate runs on committed branches, so it is unaffected.
  - I hit this myself in this run. A run with `factory/instance.py` uncommitted failed the listed test with the C.4 message. I confirmed the cause with a reverted probe edit (`harness … has uncommitted changes:\nfactory/__init__.py`), and the test passed once committed.
  - I did not change the tests, because that would be a design choice beyond this sub-ticket.
- **`--accept-harness` is silently ignored where the guard does not apply:** with `init` or `paths`, and when the store in use is not the instance's own. The spec does not say what should happen there, and a reviewer may prefer a refusal.
- **Format of changed paths in the C.4 message.** They come out in `git status --porcelain` order, taken as `line[3:]`. A rename prints `old -> new`, and git quotes paths that contain special characters.
- **Names and formats the spec leaves open.** The log event is called `harness.accepted`; the spec does not name it. The lock is written as `<rev>\n`, the same format `init` writes.
- **Which checkout is checked.** The revision and dirty checks use the running checkout (`instance.HARNESS`), not `instance.yaml`'s `harness:` value. This follows the plan's reading. A refusal on a mismatch between the two is out of scope.
- **Merge-base.** The branch does not contain `f809c69`, the recorded base, which changes only `intake/state/**`. I did not merge `main` in, because this is not a conflict run.
- **Who wrote what.** The C code and tests were written by run-0069. I re-read the code diff in full (`git diff main...HEAD -- factory`) and re-ran everything above, but I did not write it.
- **Commit messages.** My two commits follow the branch's existing message style (no trailers).

## Out-of-scope observations

- The `factory/workflows/*.js` header comments do not mention `--accept-harness` or the upgrade step (run-0069 noted this too). The README is covered by E.6.
- See the first gap above: if the B/C tests should run from a dirty dev checkout, as C.4's text implies, they would need to drive a clean clone or a throwaway store. That is a spec/test-design question for a later ticket.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW criterion moved from failing to its target, and every REGRESSION criterion and both gates pass on a clean tree (`116 passed`). The one existing-test change is the operator-ruled line.
ESCALATIONS: none

## Diff `f809c694fed21286bd2c1c234943c3dd96656db3...010d1b00c5835c7022a72771c63f63f8b6ab3707`

diff --git a/factory/cli.py b/factory/cli.py
index e34ca90..702329b 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -894,6 +894,9 @@ def log_tail(a, root, cfg):
 
 def build_parser() -> argparse.ArgumentParser:
     ap = argparse.ArgumentParser(prog="factory", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
+    ap.add_argument("--accept-harness", metavar="SHA", default=None,
+                    help="accept the running harness revision SHA for this instance (design C.3); "
+                         "written before the subcommand")
     sp = ap.add_subparsers(dest="cmd", required=True)
 
     tk = sp.add_parser("ticket").add_subparsers(dest="sub", required=True)
@@ -1040,8 +1043,10 @@ def main(argv: list[str] | None = None) -> int:
         if a.cmd in ("init", "paths"):  # exempt from the instance refusal (design B.1)
             a.fn(a)
             return 0
-        cfg = store.load_config()  # refused when no instance is found: nothing is written
+        inst = instance.require()  # refused when no instance is found: nothing is written
+        cfg = instance.load_config(inst)
         root = store.state_root(cfg)
+        instance.guard(inst, cfg, root, a.accept_harness)  # the harness lock (design C.2-C.4)
         a.fn(a, root, cfg)
         return 0
     except Refused as e:
diff --git a/factory/instance.py b/factory/instance.py
index 108a1ee..fb344d3 100644
--- a/factory/instance.py
+++ b/factory/instance.py
@@ -16,6 +16,7 @@ relative to the repo root; FACTORY_STATE overrides it.
 from __future__ import annotations
 
 import os
+import re
 import subprocess
 from pathlib import Path
 
@@ -102,6 +103,57 @@ def harness_revision(harness: Path = HARNESS) -> str | None:
     return rev if cp.returncode == 0 and len(rev) == 40 else None
 
 
+LOCK_NAME = "harness.lock"
+_SHA = re.compile(r"[0-9a-f]{40}")
+
+
+def harness_changes(harness: Path = HARNESS) -> list[str]:
+    """Uncommitted changes to the harness's own code (C.4), one path per entry; files .gitignore
+    excludes do not count. Refused when git cannot tell."""
+    cp = subprocess.run(["git", "-C", str(harness), "status", "--porcelain", "--", *HARNESS_PATHS],
+                        capture_output=True, text=True)
+    if cp.returncode != 0:
+        raise Refused(f"cannot read the status of harness {harness}: {cp.stderr.strip()}")
+    return [ln[3:] for ln in cp.stdout.splitlines() if ln.strip()]
+
+
+def read_lock(inst: Path) -> str | None:
+    """The stripped first line of `<instance>/harness.lock`, or None when it is missing or empty."""
+    p = inst / LOCK_NAME
+    if not p.is_file():
+        return None
+    lines = p.read_text(encoding="utf-8").splitlines()
+    return (lines[0].strip() or None) if lines else None
+
+
+def guard(inst: Path, cfg: dict, root: Path, accept: str | None) -> None:
+    """The harness lock (C.2–C.4), for every command except `init` and `paths`. Applies only when
+    the store in use is the instance's own; other stores (FACTORY_STATE elsewhere) are not checked.
+    Order: uncommitted harness edits are refused first, so `--accept-harness` cannot override them;
+    then `--accept-harness SHA` rewrites the lock (and logs it) only when SHA is the running
+    revision; then the lock must name the running revision. Every refusal writes nothing."""
+    if not is_own_store(inst, cfg, root):
+        return
+    changed = harness_changes()
+    if changed:
+        raise Refused(f"harness {HARNESS} has uncommitted changes:\n" + "\n".join(changed))
+    rev = harness_revision()
+    if rev is None:
+        raise Refused(f"cannot read the harness revision of {HARNESS} (not a git checkout?)")
+    lock = read_lock(inst)
+    if accept is not None:
+        if not _SHA.fullmatch(accept) or accept != rev:
+            raise Refused(f"--accept-harness {accept} is not the running harness revision {rev}; "
+                          f"{inst / LOCK_NAME} is unchanged")
+        from factory import store  # local: store imports this module lazily
+        store.write_text(inst / LOCK_NAME, rev + "\n")
+        store.log_event(root, "harness.accepted", instance=str(inst), old=lock, new=rev)
+        return
+    if lock != rev:
+        raise Refused(f"harness {rev} is not the revision this instance accepted ({lock or 'none'}); "
+                      f"rerun with --accept-harness {rev} to accept it")
+
+
 PROTECTED_PLACEHOLDER = "  {auth, payments, migrations, infra, public API, dependencies}"
 
 
diff --git a/tests/factory/test_harness_lock.py b/tests/factory/test_harness_lock.py
new file mode 100644
index 0000000..2078c49
--- /dev/null
+++ b/tests/factory/test_harness_lock.py
@@ -0,0 +1,281 @@
+"""The harness lock (design C.2-C.5), black-box through `bin/factory` in scratch target repos.
+
+The lock guards only the instance's own store: every command except `init` and `paths` is refused
+when `<instance>/harness.lock` does not name the running harness revision (C.2), or when the running
+harness checkout has uncommitted changes to its own code (C.4). `--accept-harness SHA` (C.3) rewrites
+the lock and logs it only when SHA is the running revision, and never overrides C.4.
+
+Cases that run this checkout's own `bin/factory` against an instance's own store need this checkout
+to be clean under the harness paths (C.4, by design). Cases that need a modified or newly committed
+harness run a local clone of this checkout instead, so this checkout is never edited.
+
+Each case strips the conftest's FACTORY_INSTANCE / FACTORY_REPO and any FACTORY_STATE, so the
+harness resolves the instance from the working directory, as it does for an operator.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+import pytest
+
+REPO = Path(__file__).resolve().parents[2]
+STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
+HARNESS_PATHS = ("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")
+ZERO = "0" * 40
+
+
+def cli(harness: Path, cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
+    env = {k: v for k, v in os.environ.items() if k not in STRIP}
+    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
+    return subprocess.run([str(harness / "bin" / "factory"), *argv], capture_output=True, text=True, env=env, cwd=cwd)
+
+
+def git(path: Path, *argv: str) -> str:
+    return subprocess.run(["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@t", *argv],
+                          check=True, capture_output=True, text=True).stdout
+
+
+def revision(harness: Path) -> str:
+    return git(harness, "log", "-1", "--format=%H", "--", *HARNESS_PATHS).strip()
+
+
+def tree(path: Path) -> dict[str, bytes]:
+    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}
+
+
+def js(cp: subprocess.CompletedProcess) -> dict:
+    return json.loads(cp.stdout.strip().splitlines()[-1])
+
+
+def make_target(path: Path, harness: Path) -> Path:
+    path.mkdir(parents=True)
+    git(path, "init", "-q", "-b", "main")
+    git(path, "commit", "-q", "--allow-empty", "-m", "init")
+    cp = cli(harness, path, "init", "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    return path
+
+
+def lock(target: Path) -> Path:
+    return target / ".factory" / "harness.lock"
+
+
+def tickets(target: Path) -> list[str]:
+    d = target / ".factory" / "state" / "tickets"
+    return sorted(p.name for p in d.iterdir()) if d.exists() else []
+
+
+def mismatch(rev: str, locked: str) -> str:
+    return (f"harness {rev} is not the revision this instance accepted ({locked}); "
+            f"rerun with --accept-harness {rev} to accept it")
+
+
+@pytest.fixture
+def target(tmp_path: Path) -> Path:
+    return make_target(tmp_path / "target", REPO)
+
+
+@pytest.fixture
+def request_file(tmp_path: Path) -> Path:
+    p = tmp_path / "r.md"
+    p.write_text("# demo\n\nDo the thing.\n")
+    return p
+
+
+@pytest.fixture
+def clone(tmp_path: Path) -> Path:
+    """A local clone of this checkout's HEAD, running on this suite's interpreter environment."""
+    c = tmp_path / "h"
+    subprocess.run(["git", "clone", "-q", str(REPO), str(c)], check=True, capture_output=True)
+    (c / ".venv").symlink_to(Path(sys.prefix))  # untracked, outside the harness paths
+    assert (c / ".venv" / "bin" / "python").exists()
+    return c
+
+
+# ----- C.2: the lock must name the running revision -------------------------------------------
+
+def test_fresh_init_lock_is_the_running_revision_and_commands_run(target, request_file):
+    assert lock(target).read_text() == revision(REPO) + "\n"
+    cp = cli(REPO, target, "ticket", "new", "--file", str(request_file))
+    assert cp.returncode == 0, cp.stderr
+    assert tickets(target) == ["T-0001.yaml"]
+
+
+@pytest.mark.parametrize("content,shown", [(ZERO + "\n", ZERO), ("", "none"), (None, "none")],
+                         ids=["other-revision", "empty", "missing"])
+def test_unaccepted_lock_refused_and_nothing_written(target, request_file, content, shown):
+    if content is None:
+        lock(target).unlink()
+    else:
+        lock(target).write_text(content)
+    before = tree(target)
+    cp = cli(REPO, target, "ticket", "new", "--file", str(request_file))
+    assert cp.returncode == 2
+    assert cp.stderr.strip() == mismatch(revision(REPO), shown)
+    assert tree(target) == before
+
+
+def test_lock_compares_its_stripped_first_line(target, request_file):
+    lock(target).write_text(f"  {revision(REPO)}  \nanything else\n")
+    assert cli(REPO, target, "ticket", "new", "--file", str(request_file)).returncode == 0
+
+
+@pytest.mark.parametrize("argv", [("ticket", "show", "T-0001"), ("config",), ("log", "tail"),
+                                  ("ticket", "transition", "T-0001", "--to", "parked", "--by", "t"),
+                                  ("run", "start", "--role", "triage", "--ticket", "T-0001")])
+def test_every_store_command_is_refused_under_a_mismatch(target, request_file, argv):
+    assert cli(REPO, target, "ticket", "new", "--file", str(request_file)).returncode == 0
+    lock(target).write_text(ZERO + "\n")
+    before = tree(target)
+    cp = cli(REPO, target / ".factory", *argv)
+    assert cp.returncode == 2, argv
+    assert cp.stderr.strip() == mismatch(revision(REPO), ZERO)
+    assert tree(target) == before
+
+
+def test_init_and_paths_are_exempt_and_leave_the_lock(target):
+    lock(target).write_text(ZERO + "\n")
+    cp = cli(REPO, target, "paths")
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["harness_revision"] == revision(REPO)
+    cp = cli(REPO, target, "init")
+    assert cp.returncode == 0, cp.stderr
+    assert lock(target).read_text() == ZERO + "\n"
+
+
+def test_throwaway_store_runs_whatever_the_lock_says(target, request_file, tmp_path):
+    lock(target).write_text(ZERO + "\n")
+    s = tmp_path / "throwaway"
+    cp = cli(REPO, target, "ticket", "new", "--file", str(request_file), FACTORY_STATE=str(s))
+    assert cp.returncode == 0, cp.stderr
+    assert sorted(p.name for p in (s / "tickets").iterdir()) == ["T-0001.yaml"]
+    assert tickets(target) == []
+
+
+def test_factory_state_naming_the_own_store_is_still_checked(target, request_file):
+    lock(target).write_text(ZERO + "\n")
+    cp = cli(REPO, target, "ticket", "new", "--file", str(request_file),
+             FACTORY_STATE=str(target / ".factory" / "state"))
+    assert cp.returncode == 2 and "--accept-harness" in cp.stderr
+    assert tickets(target) == []
+
+
+# ----- C.3: --accept-harness ------------------------------------------------------------------
+
+def test_accept_current_revision_rewrites_lock_logs_and_runs(target, request_file):
+    lock(target).write_text(ZERO + "\n")
+    rev = revision(REPO)
+    cp = cli(REPO, target, "--accept-harness", rev, "ticket", "new", "--file", str(request_file))
+    assert cp.returncode == 0, cp.stderr
+    assert lock(target).read_text() == rev + "\n"
+    assert tickets(target) == ["T-0001.yaml"]
+    events = [json.loads(ln) for p in sorted((target / ".factory" / "state" / "log").glob("*.jsonl"))
+              for ln in p.read_text().splitlines()]
+    accepted = [e for e in events if e["event"] == "harness.accepted"]
+    assert len(accepted) == 1
+    assert accepted[0]["old"] == ZERO and accepted[0]["new"] == rev
+    # the acceptance is logged before the command it runs
+    assert events.index(accepted[0]) < next(i for i, e in enumerate(events) if e["event"] == "ticket.created")
+    # accepted: later commands run without the option
+    assert cli(REPO, target, "ticket", "show", "T-0001").returncode == 0
+
+
+def test_accept_records_a_missing_lock_as_none(target):
+    lock(target).unlink()
+    rev = revision(REPO)
+    cp = cli(REPO, target, "--accept-harness", rev, "config")
+    assert cp.returncode == 0, cp.stderr
+    assert lock(target).read_text() == rev + "\n"
+    logs = (target / ".factory" / "state" / "log").glob("*.jsonl")
+    accepted = [json.loads(ln) for p in logs for ln in p.read_text().splitlines()
+                if json.loads(ln)["event"] == "harness.accepted"]
+    assert [(e["old"], e["new"]) for e in accepted] == [(None, rev)]
+
+
+@pytest.mark.parametrize("sha", ["1234567", ZERO, "short", "UPPER"], ids=["abbrev", "other-40", "junk", "uppercase"])
+def test_accept_other_revision_refused_and_lock_unchanged(target, request_file, sha):
+    rev = revision(REPO)
+    if sha == "short":
+        sha = rev[:12]
+    elif sha == "UPPER":
+        sha = rev.upper()
+    lock(target).write_text(ZERO + "\n")
+    before = tree(target)
+    cp = cli(REPO, target, "--accept-harness", sha, "ticket", "new", "--file", str(request_file))
+    assert cp.returncode == 2
+    assert sha in cp.stderr and rev in cp.stderr
+    assert tree(target) == before
+
+
+# ----- C.4: uncommitted harness edits ----------------------------------------------------------
+
+def test_modified_harness_refused_naming_the_paths(clone, tmp_path, request_file):
+    t = make_target(tmp_path / "t", clone)
+    with (clone / "factory" / "__init__.py").open("a") as fh:
+        fh.write("# local edit\n")
+    (clone / "agents" / "new-note.md").write_text("x\n")
+    before = tree(t)
+    cp = cli(clone, t, "ticket", "new", "--file", str(request_file))
+    assert cp.returncode == 2
+    lines = cp.stderr.strip().split("\n")
+    assert lines[0] == f"harness {clone.resolve()} has uncommitted changes:"
+    assert sorted(lines[1:]) == ["agents/new-note.md", "factory/__init__.py"]
+    assert tree(t) == before
+
+
+def test_accept_does_not_override_a_modified_harness(clone, tmp_path, request_file):
+    t = make_target(tmp_path / "t", clone)
+    rev = revision(clone)
+    lock(t).write_text(ZERO + "\n")
+    with (clone / "bin" / "factory").open("a") as fh:
+        fh.write("# local edit\n")
+    before = tree(t)
+    cp = cli(clone, t, "--accept-harness", rev, "ticket", "new", "--file", str(request_file))
+    assert cp.returncode == 2 and "bin/factory" in cp.stderr and "uncommitted changes" in cp.stderr
+    assert tree(t) == before
+
+
+def test_ignored_and_non_harness_changes_do_not_count(clone, tmp_path, request_file):
+    t = make_target(tmp_path / "t", clone)
+    (clone / "factory" / "__pycache__").mkdir(exist_ok=True)
+    (clone / "factory" / "__pycache__" / "x.cpython-311.pyc").write_bytes(b"\0")  # .gitignore'd
+    (clone / "README.md").write_text("edited\n")  # not a harness path
+    (clone / "tests" / "factory" / "scratch.txt").write_text("x\n")
+    cp = cli(clone, t, "ticket", "new", "--file", str(request_file))
+    assert cp.returncode == 0, cp.stderr
+
+
+def test_modified_harness_still_runs_throwaway_stores_init_and_paths(clone, tmp_path, request_file):
+    t = make_target(tmp_path / "t", clone)
+    with (clone / "factory" / "__init__.py").open("a") as fh:
+        fh.write("# local edit\n")
+    s = tmp_path / "throwaway"
+    cp = cli(clone, t, "ticket", "new", "--file", str(request_file), FACTORY_STATE=str(s))
+    assert cp.returncode == 0, cp.stderr
+    assert cli(clone, t, "paths").returncode == 0
+    assert cli(clone, t, "init").returncode == 0
+
+
+# ----- the upgrade flow: the revision moves only with harness code (C.1 with C.2, C.3) ---------
+
+def test_upgrade_needs_acceptance_but_other_commits_do_not(clone, tmp_path, request_file):
+    t = make_target(tmp_path / "t", clone)
+    (clone / "README.md").write_text("docs commit\n")
+    git(clone, "commit", "-q", "-am", "docs only")
+    assert cli(clone, t, "ticket", "new", "--file", str(request_file)).returncode == 0
+
+    old = revision(clone)
+    with (clone / "factory" / "__init__.py").open("a") as fh:
+        fh.write("# upgrade\n")
+    git(clone, "commit", "-q", "-am", "harness change")
+    new = revision(clone)
+    assert new != old
+    cp = cli(clone, t, "ticket", "show", "T-0001")
+    assert cp.returncode == 2 and cp.stderr.strip() == mismatch(new, old)
+    assert cli(clone, t, "--accept-harness", new, "ticket", "show", "T-0001").returncode == 0
+    assert lock(t).read_text() == new + "\n"
+    assert cli(clone, t, "ticket", "show", "T-0001").returncode == 0
diff --git a/tests/factory/test_instance.py b/tests/factory/test_instance.py
index 9a7d180..0410001 100644
--- a/tests/factory/test_instance.py
+++ b/tests/factory/test_instance.py
@@ -243,6 +243,7 @@ def test_repo_root_is_the_instance_parent_and_factory_repo_overrides(target, tmp
     alt.mkdir(parents=True)
     (alt / "instance.yaml").write_bytes((target / ".factory" / "instance.yaml").read_bytes())
     (alt / "context.md").write_text("x\n")
+    (alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())
     cp = cli(tmp_path, "config", FACTORY_INSTANCE=str(alt))
     assert cp.returncode == 0, cp.stderr
     assert Path(js(cp)["state_dir"]) == (tmp_path / "elsewhere" / ".factory" / "state").resolve()
