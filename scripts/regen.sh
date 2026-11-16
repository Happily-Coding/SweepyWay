#!/usr/bin/env bash
# Regenerate everything Ergogen can produce, without Docker.
#
#   ./scripts/regen.sh              # config.yaml -> ergogen/output/{pcbs,outlines,cases}
#   ./scripts/regen.sh --debug      # also dump the preprocessed source for debugging
#   ./scripts/regen.sh --out /tmp/x # write somewhere else (leaves ergogen/output alone)
#
# This is the fast local loop. Gerbers/POS/BOM/DRC/3D exports still need CI (or Docker
# Desktop), see docs/PIPELINE.md §6.
set -euo pipefail

cd "$(dirname "$0")/.."

OUT="./ergogen/output"
DEBUG=()
while [ $# -gt 0 ]; do
  case "$1" in
    --debug) DEBUG=(--debug); shift ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ ! -d node_modules/ergogen ]; then
  echo "ergogen is not installed; run: npm install" >&2
  exit 1
fi

# Node lives in Windows (fnm) on this machine, so `node` is often not on PATH inside WSL.
NODE="$(command -v node || true)"
if [ -z "$NODE" ] && command -v node.exe >/dev/null 2>&1; then
  NODE="node.exe"
fi
if [ -z "$NODE" ]; then
  echo "no node/node.exe on PATH" >&2
  exit 1
fi

echo "==> $NODE $(node.exe --version 2>/dev/null || $NODE --version 2>/dev/null || true)  ergogen -> $OUT"
"$NODE" node_modules/ergogen/src/cli.js ./ergogen/ --output "$OUT" --clear "${DEBUG[@]}"

echo
echo "==> generated:"
ls -1 "$OUT"/pcbs/*.kicad_pcb 2>/dev/null | sed 's/^/    /'
echo "    $OUT/outlines/*.dxf  ($(ls -1 "$OUT"/outlines/*.dxf 2>/dev/null | wc -l) files)"
echo "    $OUT/cases/*.jscad   ($(ls -1 "$OUT"/cases/*.jscad 2>/dev/null | wc -l) files)"
echo
echo "==> next: ./scripts/check_matrix.py"
