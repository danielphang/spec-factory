#!/usr/bin/env bash
# Build the scratch harness: a pinned copy of the Nanobot-side harness (factory/ and bin/factory
# from feat/lionbot-v3) with instance/ overlaid so the roles target this repo. Idempotent.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${HARNESS_SRC:-$HOME/dev/nanobot-upstream}"
PIN="$(cat "$HERE/HARNESS_PIN")"
rm -rf "$HERE/harness"
mkdir -p "$HERE/harness"
git -C "$SRC" archive "$PIN" factory bin/factory | tar -x -C "$HERE/harness"
cp "$HERE/instance/preamble.md" "$HERE/instance/context.md" "$HERE/harness/factory/prompts/"
cp "$HERE/instance/config.yaml" "$HERE/harness/factory/config.yaml"
mkdir -p "$HERE/state"
echo "harness at $PIN -> $HERE/harness; store $HERE/state"
