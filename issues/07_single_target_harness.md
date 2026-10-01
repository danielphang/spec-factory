---
title: Harness instance is single-target: running tickets against this repo needs a hand-built overlay
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` D8 (`{repo name}` and protected paths: `nanobot`, default) and `factory render` (fills `{repo name}`, protected paths and gate commands from one `config.yaml`); `README.md` ("Fill in `{braces}` per repo"). The P0 plan builds one instance, for Nanobot.

**What happened (2026-10-01):** issue drafts 01–06 are requests against this repo's documents, and the operator asked for them to go through intake. The only built harness (`~/dev/nanobot-upstream/factory/`, `feat/lionbot-v3`) hardcodes the target in three places: `factory/prompts/preamble.md` line 1 and its protected-path list, `factory/prompts/context.md` (repository, how to run tests, "the request is a legacy faux spec"), and `factory/config.yaml` (`repo_name`, `protected_paths`, `gate_commands`). `FACTORY_STATE` relocates the store but nothing relocates the target. Running the drafts needed `intake/` here: a pinned copy of the harness with those three files replaced by hand.

**Why it matters:** the design says the doc is filled in per repo, but the harness has one instance and no way to point a second store at a second target. The role context file (`context.md`) is not in the design doc at all; it carries per-repo facts (how to run things, what kind of request to expect) that every role reads first, so a wrong one silently misdirects every role.

**Proposed fix (design doc + spec):** make the target a property of the store, not the harness: the store's root carries `instance.yaml` (repo name, repo path, protected paths, gate commands) and `context.md`, `run start`/`run compose` read them from there, and `factory render` takes the instance as input. Name the role-context block in the design doc's Harness section as a per-repo input the composer prepends.

**Fix as implemented on the Nanobot side:** none. The workaround is `intake/` in this repo (scratch; `intake/README.md`).
