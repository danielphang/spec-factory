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

