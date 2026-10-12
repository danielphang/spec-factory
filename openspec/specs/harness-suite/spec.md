# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

### Requirement: Test files share code only through helper modules
No file of the harness suite SHALL import from another test file; code that more than one test file uses MUST live in a non-test helper module.

#### Scenario: No test file imports from another test file
- WHEN `.venv/bin/python -c 'import ast,pathlib; bad=[f"{p.name}:{n.lineno}" for p in sorted(pathlib.Path("tests/factory").glob("*.py")) for n in ast.walk(ast.parse(p.read_text())) if (isinstance(n,ast.ImportFrom) and (any(s.startswith("test_") for s in (n.module or "").split(".")) or any(a.name.startswith("test_") for a in n.names))) or (isinstance(n,ast.Import) and any(s.startswith("test_") for a in n.names for s in a.name.split(".")))]; print(f"cross-test imports: {len(bad)}", *bad)'`
- THEN it prints `cross-test imports: 0`

### Requirement: Each shared test helper is written once
The repository and entry-point constants, the call wrapper, the JSON reader, the ticket reader, the empty-repository setup and the approved-parent setup SHALL each be defined in exactly one place in the harness suite, and this stays a standing guard: a later test file that needs one of them imports it.

#### Scenario: The shared constants and wrappers are defined once
- WHEN `.venv/bin/python -c 'import ast,pathlib,collections; c=collections.Counter(t.id if isinstance(n,ast.Assign) else n.name for p in pathlib.Path("tests/factory").glob("*.py") for n in ast.parse(p.read_text()).body for t in (n.targets if isinstance(n,ast.Assign) else [n]) if isinstance(t,(ast.Name,ast.FunctionDef))); print(*(f"{k}={c[k]}" for k in ("REPO","BIN","run","js","ticket","git_repo","approved_parent")))'`
- THEN it prints `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1`

#### Scenario: The approved-parent and empty-repository setups are written once
- WHEN `.venv/bin/python -c 'import pathlib; L={p:p.read_text().splitlines() for p in sorted(pathlib.Path("tests/factory").glob("*.py"))}; ap=[f"{p.name}:{i+1}" for p,l in L.items() for i in range(1,len(l)-3) if "ready-for-spec-writer" in l[i-1] and "\"spec\", \"add\"" in l[i] and "\"spec:init\"" in l[i+1] and "awaiting-spec-gate" in l[i+2] and "\"approve-spec\"" in l[i+3] and "assert" not in l[i+3] and " = " not in l[i+3]]; gr=[f"{p.name}:{i+1}" for p,l in L.items() for i,x in enumerate(l) if "\"-b\", \"main\"" in x and "\"init\"" in x and any("--allow-empty" in y for y in l[i:i+4])]; print(f"approved-parent sequences: {len(ap)}", *ap); print(f"empty-commit repo setups: {len(gr)}", *gr)'`
- THEN each of the two lines reports either `0`, or `1` followed by a single site in `_cli.py`

### Requirement: The refactor keeps every test and assertion but the one duplicate
Across this change's own merges and unmerged commits, the harness suite SHALL lose exactly the one duplicate test and gain none, and every assert statement in every other test function MUST still be present in that function.

#### Scenario: Only the duplicate test and its assertions are gone
The command compares each `Merge factory/T-0045.<n>` commit reachable from HEAD with its first parent, and `git merge-base HEAD main` with HEAD, and adds up the results, so changes other tickets make to the same files are never counted. A collection failure shows as removed tests. tar may print a locale warning on stderr; it is not part of the result.
- WHEN `T=$(mktemp -d); { for m in $(git log --format=%H --grep='^Merge factory/T-0045[.]' HEAD); do echo "$(git rev-parse "$m^1") $m"; done; echo "$(git merge-base HEAD main) $(git rev-parse HEAD)"; } | while read b h; do [ "$b" = "$h" ] && continue; for s in $b $h; do [ -d "$T/$s" ] || { mkdir "$T/$s" && git archive "$s" | tar -x -C "$T/$s" && ln -s "$PWD/.venv" "$T/$s/.venv" && (cd "$T/$s" && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest --collect-only -q -p no:cacheprovider tests/factory 2>&1 | grep '::' | sort > ids); }; done; echo "pair $b $h"; comm -23 "$T/$b/ids" "$T/$h/ids" | sed 's/^/removed /'; comm -13 "$T/$b/ids" "$T/$h/ids" | sed 's/^/added /'; .venv/bin/python -c 'import ast,pathlib,sys; A=lambda r: {f"{p.name}::{n.name}": {ast.unparse(a) for a in ast.walk(n) if isinstance(a,ast.Assert)} for p in sorted(pathlib.Path(r,"tests/factory").glob("test_*.py")) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith("test_")}; b,h=A(sys.argv[1]),A(sys.argv[2]); [print(f"missing {k}: {a[:80]}") for k in sorted(b) for a in sorted(b[k]-h.get(k,set()))]' "$T/$b" "$T/$h"; done > "$T/out"; for k in pair removed added missing; do echo "$k: $(grep -c "^$k " "$T/out")"; grep "^$k " "$T/out" | grep -v '^pair '; done; rm -rf "$T"`
- THEN `pair:` is at least 1; `removed: 1` is followed by exactly `removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`; it prints `added: 0`; and it prints `missing: 2`, followed by two lines that both start `missing test_p0_cli.py::test_run_finish_without_output_is_killed:`

#### Scenario: The suite is shorter
The command adds up the test-file line counts over the same pairs as the scenario above.
- WHEN `{ for m in $(git log --format=%H --grep='^Merge factory/T-0045[.]' HEAD); do echo "$(git rev-parse "$m^1") $m"; done; echo "$(git merge-base HEAD main) $(git rev-parse HEAD)"; } | while read b h; do [ "$b" = "$h" ] && continue; for s in $b $h; do printf '%s ' $(git ls-tree --name-only "$s" tests/factory/ | grep '\.py$' | while read f; do git show "$s:$f"; done | wc -l); done; echo; done | awk '{n++; b+=$1; h+=$2} END {print "pairs: " n+0 "; test lines before: " b+0 ", after: " h+0 ", change: " h-b}'`
- THEN `pairs` is at least 1 and `change` is negative, and the verifier reports the line

### Requirement: A suite run writes nothing into the checkout
A run of the harness suite SHALL pass and leave every path of the checkout as it was, except pytest's own cache of the test modules in `tests/factory/__pycache__`.

#### Scenario: A suite run in a fresh clone passes and adds nothing to the checkout
The command gives pytest its own temporary directory under `/tmp`, as the existing harness-suite scenario does, and removes it when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0045-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && cd $T/c && find . \( -path ./.git -o -path ./tests/factory/__pycache__ \) -prune -o -print | sort > $T/before && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; find . \( -path ./.git -o -path ./tests/factory/__pycache__ \) -prune -o -print | sort > $T/after; echo "paths changed: $(comm -3 $T/before $T/after | wc -l | tr -d ' ')"; comm -3 $T/before $T/after; rm -rf "$P")`
- THEN the first line reports a number of passed tests and no `failed` or `error`, and the next line is `paths changed: 0` with nothing after it
