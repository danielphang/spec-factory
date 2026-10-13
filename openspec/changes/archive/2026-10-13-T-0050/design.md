## Proposed change
A. `factory/cli.py` `run_start`
   1. Directly after the unknown-role check, and before the ticket is loaded, refuse when `a.model is not None` and it differs from `cfg["models"][a.role]`. Raise `Refused(f"model {a.model} refused for {a.role}: the instance names {cfg['models'][a.role]}")`. Exit 2, and write nothing: no run directory, no `in_flight` entry, no event.
   2. Replace `model = a.model or cfg["models"][a.role]` with `model = cfg["models"][a.role]`. `meta.yaml`, the `run.started` event and the printed JSON keep carrying `model`, as today.
   3. Optionally, give `--model` (line 702) a help string saying it must match the instance's model for the role. Keep `factory/cli.py` under 900 lines.

B. Tests
   1. Add a new file, `tests/factory/test_run_start_model.py`. Use a throwaway store with `FACTORY_INSTANCE` pointing at a copy of `factory/instance.template.yaml` in which the triage model is changed to a value no other role uses (for example `sonnet`). Cover four cases.
      - A differing `--model` is refused with exit 2 and the exact error text. No run directory, `run.started` event or `in_flight` entry is written.
      - `--model` equal to the instance's model is accepted and recorded.
      - No `--model` records the instance's model, in `meta.yaml`, in the event and in the printed JSON.
      - A reviewer, verifier or other non-triage role is checked against its own entry, not triage's.
   2. Make the two fixture edits listed under Tests to change.

C. Docs
   1. `dev/build-harness.spec.md:203`, the `run start` entry. Replace "(`model: M`, default `config.yaml` `models[R]`; …)" with text saying the model is the instance's `models[R]`. Add the new guard to its **Guards** list with its error, `model <M> refused for <R>: the instance names <model>`.
   2. `README.md`, the role-call paragraph under "The intake workflow, step by step" (line 254). After "refuses unless the ticket is in that role's ready state", add that `run start` takes the role's model from `instance.yaml` and refuses a `--model` that names another. Bump the status-header date per "Maintaining this page".
   3. No change to `docs/design.md`. It already says the harness owns "choosing the model per role" (line 56). So no changelog entry is needed and no `docs/prompts/` copy changes.

## Tests to change
- `tests/factory/test_coding_standard.py`, fixture `system_prompts` (line 50). It starts an implementer run and a reviewer run with `--model opus`, but the instance template names `reviewer: fable`. Under the Decision that a differing `--model` is refused, the reviewer start fails and both parametrised tests error. Drop the `"--model", "opus"` arguments from that call and change nothing else. The tests read the system prompt, not the model.
- `tests/factory/test_turn_economy.py`, fixture `run_prompts` (line 105). The same call, for triage, planner, implementer, reviewer and verifier. The reviewer start is refused, so all five parametrised tests error. Drop the `"--model", "opus"` arguments from that call and change nothing else.

