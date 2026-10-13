## ADDED Requirements

### Requirement: The documents record that run start owns each role's model
`dev/build-harness.spec.md`'s `run start` entry MUST say the model comes from the instance's `models[R]` and SHALL list the refusal of a differing `--model` among its guards, with its error; `README.md`'s role-call paragraph under "The intake workflow, step by step" SHALL say that `run start` refuses a `--model` the instance does not name.

#### Scenario: The build spec and the README describe the model check
- WHEN `echo "old=$(grep -c 'default .config.yaml. .models\[R\]' dev/build-harness.spec.md) guard=$(grep -c 'refused for <R>: the instance names' dev/build-harness.spec.md) readme=$(sed -n '/^### The intake workflow, step by step/,/sequenceDiagram/p' README.md | grep -c -- '--model')"`
- THEN it prints `old=0 guard=1 readme=<n>` with n of 1 or more

