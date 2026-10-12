Type: chore

Title: De-bloat D: split factory/cli.py into modules by job (drift, setup, gates, human decisions), with cli.py keeping the parser and main

Summary:
`factory/cli.py` is the harness's command-line module, and it is now 2,020 lines out of 5,073 lines of harness Python. Every ticket that touches a refusal, a gate or a human command edits it, and every role run that reads it reads the whole file. The requester wants it split into job-sized modules: spec-drift checks, instance and store setup, gates (results, merge, join, parent close), and human decisions (approve-spec, request-changes, resolve, decision, spec amend), with shared small helpers in one common module. This is a pure move. Function bodies change only in their imports, and every refusal string, exit code, event shape and JSON output stays the same. Docs that name `cli.py` functions are updated in the same change. `cli.main`, `build_parser` and `ROLES` must stay importable from `factory.cli`, and no new module may import `factory.cli`.

Evidence:
- Request: GitHub issue danielphang/spec-factory#100 (de-bloat round, #96 row 2a.4). Its index row is at `dev/issues.md:103`, which lists it as T-0047, the ticket this run triages.
- Duplicate search: T-0044, T-0045 and T-0046 (de-bloat A to C) are closed and none of them split `cli.py`. T-0048 (#101, docs) and T-0049 (#104, README diagram) are other work. I found no other ticket or request that splits `cli.py`.
- Checked on `main` at 6203096:
  - `wc -l factory/cli.py` gives 2020. The request's figure of 2,035 is from `927bc53`, so its line ranges are stale, as the request itself warns.
  - `wc -l factory/*.py` gives 5073 in total.
  - Function definitions: `build_parser` at `cli.py:1764`, `resolve` at `:1144`, `init_cmd` at `:1400`, `store_migrate` at `:1519`, `spec_amend` at `:592`, `merge_cmd` at `:954`, `_check_sibling_tests` at `:249`, `_check_drift` at `:280`, `READ_ONLY`/`_in_flight`/`fence` at `:1960-1970`, `ROLES` at `:25`, `out` at `:30`.
- In-process uses of `factory.cli`:
  - `factory/drive.py:39` (`from factory import cli`) and `factory/stats.py:23` (`from factory.cli import ROLES`).
  - `factory/__main__.py:1` (`from factory.cli import main`). The request leaves this one out.
  - `tests/factory/clean_harness_cli.py:25` and `tests/factory/test_store_migrate.py:155` (`from factory import cli, instance`).
  - `test_drive.py:130-132` calls `drive.role_argv` in a subprocess, not in-process.
- The `shutil.copy2` patch is real. `tests/factory/test_store_migrate.py:149-163` (`ALTERING_COPY`) replaces the global `shutil.copy2`. The only harness caller is `factory/cli.py:1586`, as `shutil.copy2(...)`, inside `store_migrate`.
- `store_migrate` still exists. #83 part D, which would delete it, is "not in intake" per `dev/issues.md:87`, so the setup module must carry `store migrate`.
- Docs that name `cli.py`: `README.md:1170`, `:1171` and `:1173`, and `docs/principles.md:106` and `:164`. These match the request.
- The helper ticket the request says must land first (#96 row 2a, T-0046 "De-bloat C") is closed.

Capabilities: harness-code, harness-docs, harness-suite, store-setup, live-store-guard, merge-gate, human-resolution, spec-amendment, build-dispatch, factory-stats

Assumptions:
- (Inference) The acceptance line "only `drive.py` and `stats.py` among `factory/*.py` import `factory.cli`, as today" is wrong as written, because `factory/__main__.py` also imports `factory.cli.main`. I read the intent as "no module beyond today's three importers (`__main__.py`, `drive.py`, `stats.py`) imports `factory.cli`". The spec writer should state the criterion that way.
- (Inference) The four module names (`drift.py`, `setup.py`, `gates.py`, `human.py`), the common-helpers module and where `fence` goes (`instance.py` or a new `fence.py`) are the requester's suggestions. The spec writer and planner may adjust them, as long as the stated rules hold.
- (Inference) `factory/**` is a protected harness path. The approved spec's Risk section must declare every module this change creates or edits, or the merge gate refuses it. This is expected for a harness ticket, not an escalation.
- (Inference) The "under 900 lines" and "within ±50 total Python lines" figures are the requester's own targets. They are acceptance for this ticket, not standing rules.
- Suggested priority: p2, after T-0046 (now closed) and in #96's order. This is a suggestion; priority is a human call.

Reason: ACCEPT. The intent is clear: move code to new modules with no change in behaviour, under stated rules, with runnable acceptance. No product decision is needed. The request's out-of-scope list settles the two adjacent questions: the `merge_cmd` vs `ready_implementers` sibling difference, and retiring the P0 mode. The one factual error, the importer list, does not change the intent and is noted above.

STATUS: ACCEPT
CONFIDENCE: high. I verified the line counts, the importers, the `copy2` patch, the doc references and the duplicate search on the current `main`.
ESCALATIONS: none
