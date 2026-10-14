## ADDED Requirements

### Requirement: Every role agent template has valid frontmatter
Each `agents/*.md` template's frontmatter MUST parse as a YAML mapping that carries `name`, `description`, `model` and `tools`. The four templates whose descriptions did not parse SHALL keep their description's words and every other line unchanged.

#### Scenario: Every role agent template's frontmatter parses and carries name, description, model and tools
Run from the repository root after `uv sync --frozen`.
- WHEN `(for f in agents/*.md; do echo "$(basename $f) $(sed -n '2,/^---$/p' $f | sed '$d' | uv run --frozen python -c 'import sys, yaml; m = yaml.safe_load(sys.stdin); print("keys=" + ("ok" if {"name", "description", "model", "tools"} <= set(m) else "missing"))' 2>/dev/null || echo keys=unparsed)"; done)`
- THEN it prints exactly `factory-clerk.md keys=ok`, `factory-planner.md keys=ok`, `factory-spec-critic.md keys=ok`, `factory-spec-writer.md keys=ok`, `factory-stub.md keys=ok`, `factory-triage.md keys=ok`, one per line

#### Scenario: The four fixed templates keep their description's words and every other line
`525d73f` is `main` before this change.
- WHEN `(B=525d73f; for f in planner spec-critic spec-writer triage; do p=agents/factory-$f.md; old=$(git show $B:$p | sed -n 's/^description: //p'); new=$(sed -n '2,/^---$/p' $p | sed '$d' | uv run --frozen python -c 'import sys, yaml; print(yaml.safe_load(sys.stdin)["description"])' 2>/dev/null); echo "$f text=$([ -n "$new" ] && [ "$old" = "$new" ] && echo same || echo changed) rest=$(diff <(git show $B:$p | grep -v '^description: ') <(grep -v '^description: ' $p) >/dev/null && echo same || echo changed)"; done; echo "others=$(git diff --quiet $B -- agents/factory-clerk.md agents/factory-stub.md && echo same || echo changed)")`
- THEN it prints exactly `planner text=same rest=same`, `spec-critic text=same rest=same`, `spec-writer text=same rest=same`, `triage text=same rest=same`, then `others=same`, one per line

### Requirement: The harness suite fails on a role agent template with broken frontmatter
The harness suite MUST fail when any `agents/*.md` template's frontmatter does not parse or lacks one of `name`, `description`, `model` and `tools`, and its output SHALL name each such template.

#### Scenario: The suite fails on a template with broken frontmatter and names it
Copies the committed tree to a throwaway repo, breaks the clerk's header and drops the stub's `tools:` line, and runs the whole suite there with this checkout's environment. About 100 seconds.
- WHEN `(export TMPDIR=$(mktemp -d /tmp/sf.XXXXXX); T=$(cd "$(mktemp -d)" && pwd -P); R=$PWD; mkdir $T/c && git archive HEAD | tar -x -C $T/c && ln -s $R/.venv $T/c/.venv && cd $T/c && git init -q -b main && printf '.venv\n' >> .git/info/exclude && sed 's/^description: Spec factory store clerk\./description: Spec factory store clerk: broken./' $R/agents/factory-clerk.md > agents/factory-clerk.md && grep -v '^tools:' $R/agents/factory-stub.md > agents/factory-stub.md && git add -A && git -c user.email=f@x -c user.name=f commit -qm broken && .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory > $T/log 2>&1; rc=$?; echo "suite=$([ $rc -eq 0 ] && echo passed || echo failed) clerk=$(grep -c 'factory-clerk' $T/log | awk '{print ($1 > 0)}') stub=$(grep -c 'factory-stub' $T/log | awk '{print ($1 > 0)}')"; rm -rf $TMPDIR)`
- THEN it prints exactly `suite=failed clerk=1 stub=1`

### Requirement: init reports an agent copy that differs from its template and never overwrites it
When `factory init` runs for an instance's own store, it SHALL list each existing `.claude/agents/factory-*.md` copy whose bytes differ from its template under `stale_agents` in its JSON output and name it on stderr, MUST leave that copy unchanged and exit 0, and SHALL still create a missing copy without listing any matching copy.

#### Scenario: init reports an edited agent copy and leaves it as it is
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf 'local edit\n' >> .claude/agents/factory-planner.md && cp .claude/agents/factory-planner.md $T/kept && $B init >$T/out 2>$T/err; rc=$?; echo "exit=$rc stale=$(python3 -c 'import json, sys; o = json.load(sys.stdin); print(",".join(p.rsplit("/", 1)[-1] for p in o["stale_agents"]) if "stale_agents" in o else "absent")' < $T/out) kept=$(cmp -s $T/kept .claude/agents/factory-planner.md && echo yes || echo no) named=$(grep -c 'factory-planner\.md' $T/err) others=$(grep -v 'factory-planner\.md' $T/err | grep -c .)")`
- THEN it prints exactly `exit=0 stale=factory-planner.md kept=yes named=1 others=0`

#### Scenario: init still creates a missing agent copy and lists no matching copy
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; A=$PWD/agents; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .claude/agents/factory-triage.md && $B init >$T/out 2>$T/err; rc=$?; echo "exit=$rc $(python3 -c 'import json, sys; o = json.load(sys.stdin); print("created=" + ",".join(p.rsplit("/", 1)[-1] for p in o["agents"]) + " stale=" + str(len(o.get("stale_agents", []))))' < $T/out) same=$(for f in $A/factory-*.md; do cmp -s $f .claude/agents/$(basename $f) && echo x; done | grep -c .) differs=$(grep -c 'differs' $T/err)")`
- THEN it prints exactly `exit=0 created=factory-triage.md stale=0 same=6 differs=0`

