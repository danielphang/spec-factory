"""The instance a command serves: a target repo's `.factory/` directory (design B.1, B.2, C.1).

One harness checkout serves many target repos. Each target carries `.factory/` with
`instance.yaml` (its config), `context.md` (the role-context block), `harness.lock` and the store.

Resolution, used by store, gitops, compose and cli:
- FACTORY_INSTANCE, when set, names the instance directory, whatever it is called;
- otherwise walk up from the caller's working directory to the nearest directory that holds
  `.factory/instance.yaml`. `bin/factory` changes into the harness checkout before running, so it
  hands the caller's directory over in FACTORY_CWD;
- otherwise the command is refused. There is no fallback to the harness checkout.

The repo root is the parent of the instance directory; FACTORY_REPO overrides it. `state_dir` is
relative to the repo root; FACTORY_STATE overrides it.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import yaml

from factory.store import Refused

# The running harness checkout: the one whose bin/factory is executing.
HARNESS = Path(__file__).resolve().parent.parent
INSTANCE_TEMPLATE = HARNESS / "factory" / "instance.template.yaml"
CONTEXT_TEMPLATE = HARNESS / "factory" / "context.template.md"
AGENTS = HARNESS / "agents"
# The harness's own code: what the harness revision (C.1) is taken over.
HARNESS_PATHS = ("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")
DIRNAME = ".factory"
CONFIG_NAME = "instance.yaml"


def caller_cwd() -> Path:
    return Path(os.environ.get("FACTORY_CWD") or os.getcwd()).expanduser().resolve()


def find() -> Path | None:
    """The instance directory, or None. FACTORY_INSTANCE wins; then the walk-up."""
    env = os.environ.get("FACTORY_INSTANCE")
    if env:
        p = Path(env).expanduser().resolve()
        return p if (p / CONFIG_NAME).is_file() else None
    cwd = caller_cwd()
    for d in (cwd, *cwd.parents):
        if (d / DIRNAME / CONFIG_NAME).is_file():
            return d / DIRNAME
    return None


def not_found_message() -> str:
    env = os.environ.get("FACTORY_INSTANCE")
    if env:
        return f"FACTORY_INSTANCE={env} holds no {CONFIG_NAME}; run factory init --repo-name NAME there, or fix FACTORY_INSTANCE"
    return f"no {DIRNAME}/{CONFIG_NAME} found from {caller_cwd()}; run factory init --repo-name NAME, or set FACTORY_INSTANCE"


def require() -> Path:
    inst = find()
    if inst is None:
        raise Refused(not_found_message())
    return inst


def repo_root(inst: Path | None = None) -> Path:
    env = os.environ.get("FACTORY_REPO")
    if env:
        return Path(env).expanduser().resolve()
    return (inst or require()).parent


def load_config(inst: Path | None = None) -> dict:
    inst = inst or require()
    return yaml.safe_load((inst / CONFIG_NAME).read_text(encoding="utf-8"))


def own_state_root(inst: Path, cfg: dict) -> Path:
    """The instance's own store: `state_dir` under the repo root, ignoring FACTORY_STATE."""
    return (repo_root(inst) / cfg["state_dir"]).resolve()


def state_root(inst: Path, cfg: dict) -> Path:
    env = os.environ.get("FACTORY_STATE")
    if env:
        return Path(env).expanduser().resolve()
    return own_state_root(inst, cfg)


def is_own_store(inst: Path, cfg: dict, root: Path) -> bool:
    """True when the store in use is the instance's own (FACTORY_STATE unset, or naming it)."""
    return root.resolve() == own_state_root(inst, cfg)


def harness_revision(harness: Path = HARNESS) -> str | None:
    """The last commit that touched the harness's own code (C.1); None outside a git checkout."""
    cp = subprocess.run(["git", "-C", str(harness), "log", "-1", "--format=%H", "--", *HARNESS_PATHS],
                        capture_output=True, text=True)
    rev = cp.stdout.strip()
    return rev if cp.returncode == 0 and len(rev) == 40 else None


PROTECTED_PLACEHOLDER = "  {auth, payments, migrations, infra, public API, dependencies}"


def fill_preamble(text: str, cfg: dict) -> str:
    """The design doc's preamble block with `{repo name}` and the protected-path line filled from
    the instance (B.4). The line becomes `  <class> (<glob>, <glob>)` per class, joined by `, `."""
    text = text.replace("{repo name}", str(cfg["repo_name"]))
    classes = []
    for cls, globs in (cfg.get("protected_paths") or {}).items():
        globs = [globs] if isinstance(globs, str) else list(globs or [])
        classes.append(f"{cls} ({', '.join(globs)})")
    line = "  " + (", ".join(classes) if classes else "none")
    return "\n".join(line if ln == PROTECTED_PLACEHOLDER else ln for ln in text.split("\n"))
