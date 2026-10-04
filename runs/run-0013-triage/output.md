Type: feature

Title: The harness cannot point a second store at a second target repo, and the per-repo role-context file every role reads is not in the design doc

Summary: The requester ran this repo's issue drafts through intake and found that the only built harness names its target repo in three files inside the harness itself: the preamble, the role context and `config.yaml`. `FACTORY_STATE` moves the store, but nothing moves the target. Running the drafts took a hand-built overlay (`intake/`). The design says "fill in `{braces}` per repo", but it gives no way to take a ticket against a second repo, and it never mentions the role-context block. That block holds per-repo facts that every role reads first, so a wrong one quietly misleads every role. The requester proposes making the target a property of the store: `instance.yaml` and `context.md` at the store root, read by `run start`, `run compose` and `factory render`. They also propose naming the role-context block in the design doc's Harness section. Choosing between that and the other models below is a design decision, so this is not ACCEPT.

Evidence:
- Request: "The only built harness ... hardcodes the target in three places: `factory/prompts/preamble.md` line 1 and its protected-path list, `factory/prompts/context.md` ..., and `factory/config.yaml` (`repo_name`, `protected_paths`, `gate_commands`). `FACTORY_STATE` relocates the store but nothing relocates the target." Fix on the Nanobot side: "none. The workaround is `intake/` in this repo."
- Checked in the reference harness (read only; `~/dev/nanobot-upstream`, `feat/lionbot-v3` at `053a7bd5e`):
  - `factory/prompts/preamble.md` line 1 reads `You are one agent in a software pipeline: nanobot (the lionbot fork, branch feat/lionbot-v3).` The protected-path list is at line 37.
  - `factory/prompts/context.md` begins `Repository: \`nanobot\`, the lionbot fork`. It gives `uv run` and pytest commands and says "The request is a legacy 'faux spec'".
  - `factory/config.yaml` has `repo_name: nanobot`, nanobot `protected_paths` and nanobot `gate_commands`.
  - `factory/store.py:16` loads `CONFIG_PATH` from the package directory. `state_root()` (`store.py:32-37`) honours `FACTORY_STATE` for the store root only.
  - `factory/compose.py:11,35` reads `context.md` from the package `prompts/` directory and puts it first in every composed input. `factory/cli.py:175` reads `preamble.md` the same way.
  - So the requester's claim holds: the store location can be overridden, but the target is fixed by the harness's own files.
- Checked in this repo (`~/dev/spec-factory`, `main`):
  - `specs/build-harness.md:127`: D8, `{repo name}` and protected paths, value `nanobot`, marked "default".
  - `specs/build-harness.md:158`: `factory render` fills `{repo name}`, protected paths and `{gate commands}` "from `config.yaml`", reading only `factory/prompts/design-doc.md`.
  - `README.md:11` and `docs/spec-factory.md:7`: "Fill in `{braces}` per repo."
  - `grep -n -i "context.md\|role context\|role-context"` over `docs/spec-factory.md`, `specs/build-harness.md`, `plans/*.md` and `README.md` finds nothing. The role-context block is not specified anywhere in the design documents.
  - The workaround exists as described. `intake/setup.sh` copies `factory` and `bin/factory` out of the harness at the pinned commit in `intake/HARNESS_PIN` (`053a7bd5e…`), then copies `intake/instance/{preamble.md,context.md,config.yaml}` over the copy.

Assumptions:
- (inference) The single-target behaviour comes from the design and is not a reference-harness bug. D8 records one repo name as a "default" decision, and render fills placeholders from one harness-local `config.yaml`. So the fix belongs in the design doc and spec, as the requester says.
- (inference) "Run tickets against a second repo" means one harness serving several stores and targets. It is not a request to build a separate harness from scratch for each repo. The proposal implies this reading but does not state it.
- (inference) The design doc's Harness section, at `docs/spec-factory.md:50`, says the harness composes "each role's input from *only* its declared sources". A role-context block put in front of every role's input is a source that the routing table's Receives column does not declare. Whatever option is chosen, the doc has to either declare that block or explain why it is exempt.
- (inference) The proposed `instance.yaml` would hold the protected paths. `config.yaml` is itself a protected path in the reference harness (`infra: [... "factory/config.yaml" ...]`). Moving the protected-path list into the store changes who can edit it and through which gate. That is part of the decision, not a detail.
- Priority (suggestion only, a human call): medium. A working workaround exists (`intake/`), but every retargeted run depends on a hand-maintained overlay.

Question for human: Where should the target repo's identity live (repo name, repo path, protected paths, gate commands and the role-context block that every role reads first)?
- A. In the store, as the requester proposes. The store root holds `instance.yaml` and `context.md`. `run start` and `run compose` read them from there, and `factory render` takes the instance as input, so one harness can serve several stores and targets. The design doc names the role-context block as a per-repo input that the composer puts first. The spec also has to say which gate protects `instance.yaml`, since it replaces a protected `config.yaml`.
- B. In a harness copy, one per target repo, which is the model today. `config.yaml` stays with the harness. The design doc and spec document the per-target copy as the supported pattern (what `intake/` does by hand), with the copy and fill done by a defined step rather than ad hoc. The design doc names the role-context block as a per-repo input that `factory render` fills from config. Multi-target from one harness stays out of scope.
- C. Document only for now. Add the role-context block to the design doc's Harness section, declared as a per-repo input every role receives, and leave the location of the target open (D8 unchanged) until a second real target exists beyond this scratch run. File multi-target as a follow-up.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. Every claim above was read from the cited files and lines. The only open point is the design choice among A, B and C.
ESCALATIONS: none
