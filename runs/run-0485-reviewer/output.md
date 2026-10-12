Commit: 634117766e31f55980921ec1f9250d3d40e07c04 (one commit on `factory/T-0047.2`, base 700ce73e216d1fe5d218a9fe9b46e53545cf6674)

## What I checked, in the role's order

1. Test integrity. `git diff --stat 700ce73..HEAD` touches two files, `factory/cli.py` and `factory/setup.py`; nothing under `tests/` changes. No test weakened, skipped or rewritten.
2. Correctness. The moved block is byte for byte the old one: I sliced `factory/cli.py` at the base from `def _git_toplevel(` to the line before `def stats_cmd(` (trailing blank lines stripped) and compared it with `factory/setup.py` from `def _git_toplevel(` to its end; `cmp` printed nothing and both are 331 lines. Definition order is unchanged. The fourteen names the scenario demands are the only top-level definitions in `factory/setup.py`. The patch point survives: `tests/factory/test_store_migrate.py:157-163` rebinds `shutil.copy2` on the module, and `factory/setup.py:1425` still calls `shutil.copy2(...)` through `import shutil` (Decision 6). `uv run --frozen python -B -c 'import factory.setup; import factory.cli'` under a fresh HOME printed `ok`: no import cycle, and `factory/common.py` imports only `gitops`, `instance`, `store` and `Refused`, so no new module reaches `factory.cli`.
3. Scope. Only part C. `stats_cmd` stays (Decision 4); no rename; no doc change; no edit to a moved body.
4. Silent behaviour changes. None found. `factory/cli.py` keeps `build_parser` wiring the three commands (`cli.py:1400,1405,1407`) through `from factory.setup import init_cmd, paths_cmd, store_migrate` (`cli.py:24`). Nothing else in `factory/cli.py` names a moved definition.
5. Security and data safety. A pure move; no new I/O, no new paths.
6. Protected paths. `factory/cli.py` and `factory/setup.py`, both declared by the sub-ticket and the spec's Risk section. Listed under ESCALATIONS for the record.
7. Coding standard. Nothing added beyond the module header: a docstring, `from __future__ import annotations` and imports, every one used (`json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `Path`, `yaml`, `gitops`, `instance`, `specstore`, `store`, `_in_flight`, `fence`, `out`, `Refused`). In `factory/cli.py` the two dropped imports, `os` and `_in_flight`, have no remaining use (`grep -nE '\bos\.|_in_flight' factory/cli.py` finds only the local variable `was_in_flight`); each kept shared import still has at least one call (`json` 4, `shutil` 1, `subprocess` 1, `sys` 5, `yaml` 4, `specstore` 31). No run of three blank lines in `factory/*.py` (the awk check printed `0`). Lean already.
8. PR description. What changed glosses the store and names the three commands in words; Known gaps states the flaky-test evidence honestly, including that it does not prove the flake is pre-existing. One nit below.

Not re-run here (the verifier owns them): the suite, ruff, M and R1 to R19. The implementer's reported M result, `pairs=2 added=0 removed=0 lines=35`, is consistent with my byte comparison and with `wc -l`: `factory/cli.py` 1,841 to 1,508 (-333), `factory/setup.py` 349 (+349), net +16 for this sub-ticket.

## Findings

- [NIT] PR description: Known gaps: the coding standard's rule 3 asks Known gaps to list each `factory:` marker added or to say "factory: markers added: none"; the section says neither → a reader checking the rule has to read the diff to learn the answer (it is none; the diff adds no comment).

Section-comment decision in Known gaps: the implementer left `# ----- spec store ...` in `factory/cli.py:1140` because `stats_cmd` and the spec commands still follow it. That reading of the design's "move it with its code, or drop it where its section is now empty" is sound; no finding.

Note for the record: my import check ran `uv run` in the reviewer worktree, which created its `.venv/`; `git check-ignore` confirms `.venv` is ignored and `git status --porcelain` shows the tree otherwise clean.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. The moved text is byte-identical to the base by direct comparison, the two new imports and two dropped imports were each checked by grep, and both modules import in a fresh interpreter; what I did not run (suite, ruff, M) the verifier runs on this head.
ESCALATIONS: protected paths touched, both declared by the sub-ticket and the spec's Risk section: `factory/cli.py`, `factory/setup.py`.
