Commit: e375b16232346cc46947937e750c4f3be25a7472 (branch `factory/T-0043.1`, base `5215c5f8449c4e09e89acd27bd99f64fb3fc1ba9`)

## What I checked

1. Test integrity. `git diff --stat 5215c5f...e375b16` touches two files: `factory/cost.py` (+197/−20) and the new `tests/factory/test_cost_once.py` (+207). No existing test, CI config, AGENTS.md, skill or prompt changed. "Tests to change: none" holds.

2. Correctness, read against spec v2 part A and the Decisions.
   - `transcript_usage()` (cost.py:64-73) keeps the last `usage` per `message.id`, keys an id-less record by its record index so it counts alone, and reports `len(last)` as calls. This is the Decision "Usage counts each message id once, taking its last record. A record with no id counts alone."
   - `tally()` (85-97) now takes its figures from `transcript_usage()` and the model from `_model()`; the header, columns and `main()` are untouched, so `python -m factory.cost DIR...` keeps its interface. The old loop's model selection (`m.get("model") or model`, last non-empty wins) is preserved in `_model()`.
   - `_opening()` (108-122): `first` is the first record's timestamp of any type, as the spec's "the transcript's first timestamp" says; relay messages (`RELAY_PREFIX`) are skipped and scanning continues to the next user message; `RUN_DIR` is non-greedy from the leftmost `/`, so `P` is everything before `/runs/<R>/`, and `\w+` admits `spec_writer`. Tool-result user records yield an empty text (`_user_text` joins `text` fields only), so a path echoed in a tool result cannot become the candidate.
   - `_store_paths()` (125-138) handles the live stores' `store.migrated` shape: I read the event from both live logs, `{"from": ".factory/state", "to": ".factory/store", ...}`, relative paths. The code resolves a relative `from` against the store's parent after checking `here` ends with `to`. A `from` that is absolute is taken as is. Matches the Decision "S's path before a `store.migrated` event".
   - `match_transcripts()` (154-186): window check is inclusive at both ends and unbounded when `finished` is null; another given store's path rules a transcript out for S but still admits it for that other store (the loop reaches `s == o`); own-path candidates win, earliest first; otherwise a single remaining candidate. This is the Decision's four-step rule. The earliest-of-several choice is the spec's silence, and it carries a `factory:` marker (171-172) and a Known-gaps entry.
   - `gate_failures()` (189-227): splits on the first "Gate commands", so the backticked worktree and branch names before it on the real input line (I read run-043x-implementer's `input.md`: `Worktree: \`...\` (branch \`...\`, base \`...\`) ... Gate commands (...): \`(...; git diff --check main...HEAD)\`, ...`) are not taken as gates. Each gate is the text after the wrapper's last `; ` less the closing `)`, matched as a substring of each Bash `command`; a gate counts once on the first error-then-success sequence. Both are the Decision's rule. An input with no gate line, or with a gate line holding no backticks, returns None; the second case is named in Known gaps.
   - `_when()` relies on `datetime.fromisoformat` accepting `Z`, which needs Python 3.11; `pyproject.toml:4` has `requires-python = ">=3.11"`. `import yaml`: `pyproject.toml:5` lists `pyyaml>=6`.
   - Narrow confirmation: `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_cost_once.py` through the briefing's wrapper printed `11 passed in 2.49s`: the eleven tests the PR description lists pass on this head. The test file covers each clause the sub-ticket's acceptance names (repeated ids, own-path preference, migrated path, relay skipped, other store ruled out and the single-candidate fallback, the window, nesting, gate fixed / never fixed / no gate line).

3. Scope. Only part A and `tests/factory/test_cost_once.py`. The `_user_text()` extraction out of `_role()` is a same-file refactor that the new `_opening()` reuses; `_role()`'s behaviour is unchanged except that a user record with a null `content` no longer raises. No `factory/stats.py`, `factory/cli.py` or document change.

4. Silent behaviour changes. `python -m factory.cost` figures roughly halve; this is the spec's intended change and its Risk section declares it. Nothing else a caller would notice; `grep -rnE "tally|_role\(|factory\.cost|import cost" factory bin agents tests` finds no caller outside `cost.py` and the new test.

5. Security and data safety. Every file is opened for reading only; YAML goes through `yaml.safe_load`; no subprocess, no write.

6. Protected paths. `factory/cost.py` is touched. The sub-ticket declares it and the spec's Risk section lists it. Recorded under ESCALATIONS; no further approval needed at the gate.

7. Coding standard. `_window()` reads `meta.yaml` with `yaml.safe_load` instead of `factory/store.py:98` `read_yaml()`. I do not tag this `reuse:`: `cost.py` imports nothing from the package today, and the repo's precedent for loading a harness module from its file in tests (`tests/factory/test_subtickets.py:180`, because `tests/factory` is itself a package named `factory`) means a package import would break that load; `factory/subtickets.py` likewise imports only `re`. The implementer named the rung and the reason, as rule 1 asks. `_when()` has no repo counterpart (`factory/cli.py:472` calls `fromisoformat` inline). The one shortcut carries its `factory:` marker (rule 3). Names follow the spec (rule 5). No path patching (rule 6). Lean already.

8. PR description. What changed says in words what each new reader does, glosses "gate commands" at first use, and names the callers it grepped. Known gaps lists the marker and each rule the spec left open. Acceptance results quote before and after output with what each shows. Readable at the gate.

## Findings

none

Prior findings: none (round 1)

STATUS: APPROVE
CONFIDENCE: high. The diff is small and self-contained, every Decision for part A maps to a specific function I read, the live-store event shapes and the real gate line match what the code parses, and the new test file passes on this head.
ESCALATIONS: protected path `factory/cost.py` modified; declared by sub-ticket T-0043.1 ("Protected paths: `factory/cost.py`") and by spec v2's Risk section. For the record only.
