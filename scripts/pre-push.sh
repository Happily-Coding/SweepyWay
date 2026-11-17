#!/usr/bin/env bash
# Fast pre-push gate. NOT a stand-in for CI.
#
# It runs only what takes seconds, and only *blocks* on things that must always hold:
#   1. ergogen still parses the config            (catches YAML/unit-order breakage)
#   2. the configurator can still generate        (catches the CRLF trap in generate.mjs)
#   3. the configurator output == config.yaml     (B22: a run must never revert a hand-fix)
#   4. the vertical stack + screws are consistent (hardware_bom.py, B17/B21)
# Everything that is known-open today is REPORTED but not enforced, because a hook that is red
# on arrival just gets --no-verify'd.
#
# The heavy artifacts (gerbers, routing, 3D) deliberately do NOT run here: they need Docker and
# minutes. They are produced by CI, which now wipes + stamps + gates filtered-output/.
#
# Install:   ln -sf ../../scripts/pre-push.sh .git/hooks/pre-push
# Bypass:    PREPUSH_SKIP=1 git push     (or git push --no-verify)
set -uo pipefail

[ "${PREPUSH_SKIP:-0}" = "1" ] && { echo "pre-push: skipped (PREPUSH_SKIP=1)"; exit 0; }
# Resolve the repo root robustly. Git invokes this through a symlink at
# .git/hooks/pre-push, where `dirname "$0"` is `.git/hooks`, not the repo — which made every
# relative path below fail even though the same script worked when run by hand.
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[ -n "${ROOT:-}" ] || ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1

PY="./.venv/Scripts/python.exe"
NODE="node.exe"
command -v "$NODE" >/dev/null 2>&1 || NODE="node"
red=0

say() { printf '\n\033[1m== %s\033[0m\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m %s\n' "$1"; red=1; }
ok() { printf '  ok   %s\n' "$1"; }
warn() { printf '  \033[33mwarn\033[0m %s\n' "$1"; }

say "1/4 ergogen parses the config"
if ./scripts/regen.sh >/tmp/prepush-regen.log 2>&1; then ok "regen"; else
  fail "regen failed — see /tmp/prepush-regen.log"; tail -5 /tmp/prepush-regen.log | sed 's/^/       /'
fi

say "2/4 configurator can generate from the canonical config"
if $NODE configurator/lib/generate.mjs configurator/presets/sweepyway.json \
      --out C:/tmp/prepush-gen.yaml >/tmp/prepush-gen.log 2>&1; then
  ok "generate.mjs"
else
  fail "generate.mjs failed (CRLF in config.yaml, or a marker/units change)"
  grep -iE "error|start marker" /tmp/prepush-gen.log | head -3 | sed 's/^/       /'
fi

say "3/4 configurator output has not drifted from config.yaml (B22)"
if $NODE scripts/check_config_drift.mjs >/tmp/prepush-drift.log 2>&1; then
  ok "check_config_drift.mjs"
else
  fail "generating would change the keyboard — see /tmp/prepush-drift.log"
  grep -E "^  |committed:|generated:" /tmp/prepush-drift.log | head -8 | sed 's/^/       /'
fi

say "4/4 vertical stack + fasteners (B17/B21)"
if $PY scripts/hardware_bom.py >/tmp/prepush-bom.log 2>&1; then ok "hardware_bom.py"; else
  fail "the screw/standoff combination cannot be assembled"
  grep -E "^- " /tmp/prepush-bom.log | head -6 | sed 's/^/       /'
fi

say "reported, not enforced (known-open blockers)"
$PY scripts/check_matrix.py --counts 2>&1 | grep -E "^ *FAIL" | sed 's/^ */  /' | head -8
$PY scripts/check_assembly.py 2>&1 | grep -E "^ *FAIL" | sed 's/^ */  /' | head -4
if [ -f filtered-output/BUILD-STAMP.txt ]; then
  $PY scripts/check_published.py >/dev/null 2>&1 && ok "filtered-output is stamped + consistent" \
    || warn "filtered-output is stale/mixed (CI rebuilds it; check_published.py gates the publish)"
else
  warn "filtered-output has no BUILD-STAMP.txt — it is a manual merge, CI will replace it"
fi

if [ "$red" = "1" ]; then
  printf '\n\033[31mpre-push: BLOCKED\033[0m  (PREPUSH_SKIP=1 git push to override)\n'
  exit 1
fi
printf '\n\033[32mpre-push: ok\033[0m\n'
