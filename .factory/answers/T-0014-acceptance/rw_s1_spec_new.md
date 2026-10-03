## Problem

The spec factory's harness can serve only the repository its code lives in. The operator already runs the factory on a second repository, this one, and keeps a hand-made copy of the harness for it that drifts from the original. Every new project that adopts the factory would have to make the same copy.

The spec factory is a set of AI agents plus a small program, the **harness**. The agents are triage, spec writer, critic, planner, implementer and checkers. The harness moves each piece of work, a **ticket**, from agent to agent. It keeps the records. It enforces the rules no prompt can enforce.

The harness's code lives inside the first project it was built for: a fork of the Nanobot app at `~/dev/nanobot-upstream`, branch `feat/lionbot-v3`, called **green** below. The harness is also wired to that project. It finds three things by looking next to its own code:
- its configuration;
- its **store**: the folder of ticket records and agent run outputs;
- its **briefing**: a short per-repository text that every agent reads first. The briefing says which repository this is, how to run its tests and what kind of request to expect. The design calls it the role-context block.

The only way to point the factory at a second repository is to copy the code out by hand and overwrite those files. That is how the factory runs against this design repository today. A script copies a pinned revision of green's harness into an ignored folder and overwrites three files. The pin is a commit id that someone updates by hand.

A wrong briefing misleads every agent at once. The checking agents read the same briefing as the authors. So they share the error instead of catching it.

### This repository's layout mixes four kinds of content

This repository's own layout makes the problem worse. Four kinds of content are mixed together, and the folder names do not say which is which.

| Content | What is wrong |
|---|---|
| The design | It is one 759-line document that also holds the 41-item changelog. |
| Copies of the agents' instructions | The README says they are regenerated from the design document, but nothing regenerates them. |
| The working documents for building the factory itself | They sit in `specs/` and `plans/`, the names the design reserves for the factory's own output. |
| `intake/`, the install that actually runs the factory on this repository | It calls itself scratch and says to delete it, but it holds twelve tickets of records. |

### Who is affected

- The operator, who runs the factory against two repositories and keeps two drifting copies.
- Anyone who adopts the factory for a new project.

### What this change does

- Move the harness code into this repository, with its history. Give each target repository a small `.factory/` folder, called its **instance**. The instance holds the repository's configuration, its briefing, the harness revision it has accepted, and its records. One harness checkout then serves many repositories.
- Rename this repository's documents so each folder says what it holds.

Moving green itself onto the new layout is a separate, later ticket.

## Decisions

**Instance B** is this repository's own instance. This repository is both the harness and instance B.

### The lock pins harness code

The **lock** is the instance's record of the harness revision it has accepted.

- **The lock pins the harness's own code, not the checkout's HEAD.** The harness revision is the last commit that touched `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock`. Rejected: a HEAD lock. It would refuse after every store or document commit in this repository.
- **The lock guards only the instance's own store.** A run against any other store is not checked. Every test runs against another store, by pointing `FACTORY_STATE` elsewhere.

### How the harness finds the instance and the repository root

- **`FACTORY_INSTANCE` is added as an override beside the walk-up.** The walk-up is the harness's default search for an instance. `FACTORY_INSTANCE` takes the path of a `.factory/` directory instead. The workflows' clerk needs it: the clerk runs from the harness checkout, where the walk-up would find the harness repository's own instance. The tests need it too, because they need a fixed instance.
- **The repository root is the parent of the instance directory**, whatever that directory is named. `FACTORY_REPO` still overrides it. The test conftest sets `FACTORY_REPO` to the harness checkout, so the imported tests keep today's repository root.
- **No fallback.** When no instance is found, the command is refused and nothing is written. The harness never uses an instance of its own by default.
- **`request_dir` is not carried into `.factory/instance.yaml`.** No harness code reads it. Its value is relative to a directory this change removes.

### The preamble is filled from the instance

- **No per-instance preamble file.** The harness keeps the design doc's preamble block verbatim. At run start it fills `{repo name}` and the protected-path line from `instance.yaml`. It generates the protected-path line from the globs, in the form `class (glob, glob), …`.
- **Hand-written notes on the protected-path line move to `context.md`.** Instances A and B lose their hand-written prose on that line, for example "never read or written by any role".
- **The agent definitions point to the filled preamble.** Their preamble pointer changes to the run directory's `system-prompt.txt`. `run start` already writes that file with the filled preamble. The role text below the pointer is unchanged.

### One setup command

- **One `factory init` verb.** It is idempotent: it creates whatever is missing. It can create the instance, the briefing stub, the lock, the store with today's spec-store tree, and the agent files. `--repo-name` is required only when `instance.yaml` is missing.

### Tests stay where they are

- **The tests stay at `tests/factory/`, not `tests/`.** They locate the checkout two levels up. A new `tests/factory/conftest.py` points them at a fixed test instance. One test needs `environment_files: ["uv.lock"]`; see Evidence. No existing test file changes.

### Instance B runs from a separate runtime checkout

The operator decided this at the spec gate.

- **Two checkouts.** Tickets are built and merged in the **dev** checkout, `~/dev/spec-factory` on `main`. Instance B runs from a separate **runtime** checkout. The runtime is a git worktree of this repository at `~/dev/spec-factory-harness`. It is detached at the revision instance B has accepted and installed with `uv sync --frozen`.
- **The instance names its runtime.** `harness:` in `.factory/instance.yaml` names the runtime by absolute path. The runtime is the checkout that dispatchers and operators run, and `factory paths` reports it.
- **A merge into `main` never changes the running code.** One runtime serves every target ("one checkout, many targets").
- **The lock also refuses a modified runtime.** The operator decided this at the spec gate; see C.4. A runtime holds only committed, accepted code. So an uncommitted edit to harness paths there is refused rather than run unnoticed.

#### Upgrading the runtime

Upgrading is a deliberate step, done when no ticket is in flight.

1. Move the runtime: `git -C ~/dev/spec-factory-harness checkout --detach <sha>`.
2. Run `--accept-harness <sha>` in each instance that uses that runtime.

### Instance B's checks and protected paths

- **Instance B's gate adds the moved suite:** `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, next to `git diff --check main...HEAD`.
- **Instance B's protected paths change in three classes:**

| Class | Change |
|---|---|
| `harness` | New class: `factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock` |
| `infra` | Adds `.factory/**` |
| `generated` | Follows the instruction copies to `docs/prompts/**` |

### Migration limits

- **The history rewrite never runs in green's own checkout.** Part A runs `git filter-repo` only on a fresh clone of green in a scratch directory, never in `~/dev/nanobot-upstream`.
- **Green-only files are not in this repository's tree at close.** They may appear in the imported history. The files are `factory/config.yaml`, `factory/prompts/{context,preamble}.md` as green has them, and `scripts/full_suite_gate.py`.
- **The live store moves after close.** This follows the operator's note at intake. Until then `.factory/instance.yaml` names `intake/state` as its store.
- **No text from #13 or #14 merges while this parent ticket is in flight.** `main` already folds both into #21, after #19.

---

Closing note on internal references: #13, #14, #19 and #21 are other numbered items in this project. Part A and C.4 are parts of this spec.
