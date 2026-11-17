#!/usr/bin/env bash
# Reproduce the CI publish pipeline locally, step for step.
#
#   .github/workflows/build.yaml  →  this script
#
# Why: the site at happily-coding.github.io/SweepyWay serves filtered-output/, which is a stale,
# mixed snapshot with no BUILD-STAMP. Checking "what the site shows" and "what I measure" must be
# the same artifact, produced by the same steps, or every audit is guesswork.
# See docs/OUTPUT-INVENTORY.md for what each output contains.
#
# Stages (default = fast local path: ergogen + gates + copy + jscad):
#   --ergogen    regenerate everything from ergogen/config.yaml
#   --gates      check_assembly --cases, hardware_bom, check_matrix, config drift
#   --kibot      KiBot in docker: default, boards, 3d_preview, pdf, jlpcb_pos  (slow, needs docker)
#   --copy       copy ergogen/output/{pcbs,outlines,pos,gerbers,images,pdfs,cases} -> filtered-output/
#   --jscad      OpenJSCAD: .jscad -> .stl in filtered-output/cases
#   --assembly   palm rest + tenting + fix_glb_scale + create_full_3d_visual  (needs uv or venv+pygltflib)
#   --stamp      write filtered-output/BUILD-STAMP.txt (sha1 of config.yaml + commit)
#   --verify     measure the produced artifacts and assert today's known dimensions
#   --all        everything above
#
# Fidelity notes:
#  * CI converts jscad inside a docker openjscad image; this script uses the local @jscad/cli by
#    default. The tessellation differs slightly (the published case.stl and l_case_3d.stl are not
#    byte-identical for that reason), so compare *measured geometry*, never bytes.
#  * Everything runs with the repo root as CWD; Windows paths are passed to docker.exe as C:/... and
#    MSYS_NO_PATHCONV=1 is set, or docker mangles them.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

WS="$(pwd)"
# docker -v needs a Windows-style path (C:/...) on this host, and MSYS_NO_PATHCONV=1 stops the
# shell from fixing it up for us.
WSM="$(cygpath -m "$WS" 2>/dev/null || echo "$WS")"
PY="./.venv/Scripts/python.exe"
[ -x "$PY" ] || PY="python3"
NODE="node.exe"; command -v node.exe >/dev/null 2>&1 || NODE="node"
KICAD_IMAGE="ghcr.io/inti-cmnb/kicad9_auto:latest"
DOCKER="docker.exe"; command -v docker.exe >/dev/null 2>&1 || DOCKER="docker"
FAIL=0
step() { printf '\n\033[1m== %s ==\033[0m\n' "$*"; }
ok()   { printf '   \033[32mok\033[0m %s\n' "$*"; }
bad()  { printf '   \033[31mFAIL\033[0m %s\n' "$*"; FAIL=1; }

DO_ERGOGEN=0 DO_GATES=0 DO_KIBOT=0 DO_COPY=0 DO_JSCAD=0 DO_ASSEMBLY=0 DO_STAMP=0 DO_VERIFY=0
[ $# -eq 0 ] && { DO_ERGOGEN=1; DO_GATES=1; DO_COPY=1; DO_JSCAD=1; DO_VERIFY=1; }
for a in "$@"; do case "$a" in
  --ergogen) DO_ERGOGEN=1;; --gates) DO_GATES=1;; --kibot) DO_KIBOT=1;; --copy) DO_COPY=1;;
  --jscad) DO_JSCAD=1;; --assembly) DO_ASSEMBLY=1;; --stamp) DO_STAMP=1;; --verify) DO_VERIFY=1;;
  --all) DO_ERGOGEN=1; DO_GATES=1; DO_KIBOT=1; DO_COPY=1; DO_JSCAD=1; DO_ASSEMBLY=1; DO_STAMP=1; DO_VERIFY=1;;
  *) echo "unknown flag: $a"; exit 2;;
esac; done

# ---------------------------------------------------------------- 1. ergogen
if [ "$DO_ERGOGEN" = 1 ]; then
  step "ergogen (regenerate from ergogen/config.yaml)"
  if $NODE node_modules/ergogen/src/cli.js ./ergogen/ --output ./ergogen/output --clear >/tmp/ergogen.log 2>&1; then
    ok "regenerated"
  else bad "ergogen failed — see /tmp/ergogen.log"; tail -5 /tmp/ergogen.log; fi
fi

# ---------------------------------------------------------------- 2. gates
if [ "$DO_GATES" = 1 ]; then
  step "gates (the ones that must stay honest)"
  $PY scripts/check_assembly.py --cases ergogen/output/cases >/tmp/ca.log 2>&1 \
    && ok "check_assembly --cases" || { bad "check_assembly"; tail -12 /tmp/ca.log; }
  $PY scripts/hardware_bom.py --no-write >/tmp/hb.log 2>&1 \
    && ok "hardware_bom" || { bad "hardware_bom"; tail -8 /tmp/hb.log; }
  $PY scripts/check_matrix.py >/tmp/cm.log 2>&1 \
    && ok "check_matrix" || { bad "check_matrix"; tail -8 /tmp/cm.log; }
  $NODE scripts/check_config_drift.mjs >/tmp/cd.log 2>&1 \
    && ok "config drift" || { bad "config drift"; tail -6 /tmp/cd.log; }
fi

# ---------------------------------------------------------------- 3. kibot
if [ "$DO_KIBOT" = 1 ]; then
  step "KiBot in docker ($KICAD_IMAGE)"
  for cfg in default boards 3d_preview pdf jlpcb_pos; do
    for board in left_pcb right_pcb; do
      printf '   kibot %-12s %-10s ' "$cfg" "$board"
      MSYS_NO_PATHCONV=1 "$DOCKER" run --rm \
        -v "$WSM:/workspace" -w /workspace \
        -e KICAD9_3DMODEL_DIR=/workspace/component_3d_models \
        -e PATH_TO_SWEEPYWAY_COMPONENT_MODELS=/workspace/component_3d_models \
        --entrypoint /bin/bash "$KICAD_IMAGE" \
        -c "kibot -b /workspace/ergogen/output/pcbs/${board}.kicad_pcb -c /workspace/kibot/${cfg}.kibot.yaml" \
        >"/tmp/kibot_${cfg}_${board}.log" 2>&1 && echo "ok" || { echo "FAIL (see /tmp/kibot_${cfg}_${board}.log)"; FAIL=1; }
    done
  done
fi

# ---------------------------------------------------------------- 4. copy
if [ "$DO_COPY" = 1 ]; then
  step "copy ergogen output -> filtered-output (mirrors the CI block exactly)"
  mkdir -p filtered-output/{cases,palmrest} filtered-output/pcbs/{cad,outlines,pos,gerbers,images,pdfs,bom}
  cp ergogen/output/pcbs/*.kicad_pcb filtered-output/pcbs/cad/ 2>/dev/null
  cp ergogen/output/pcbs/*.kicad_pro filtered-output/pcbs/cad/ 2>/dev/null
  cp ergogen/output/pcbs/*.kicad_prl filtered-output/pcbs/cad/ 2>/dev/null
  for d in outlines pos gerbers images pdfs; do
    if command -v rsync >/dev/null 2>&1; then rsync -a --delete "ergogen/output/$d/" "filtered-output/pcbs/$d/" 2>/dev/null
    else rm -rf "filtered-output/pcbs/$d" && cp -r "ergogen/output/$d" "filtered-output/pcbs/"; fi
  done
  # CI also rsyncs cases here; the STLs come later from convert-all, so keep them:
  command -v rsync >/dev/null 2>&1 && rsync -a --exclude '*.stl' "ergogen/output/cases/" "filtered-output/cases/" 2>/dev/null \
    || cp ergogen/output/cases/*.jscad filtered-output/cases/ 2>/dev/null
  ok "copied ($(find filtered-output -type f | wc -l) files total)"
fi

# ---------------------------------------------------------------- 5. jscad
if [ "$DO_JSCAD" = 1 ]; then
  step "OpenJSCAD: .jscad -> .stl"
  # NB: pass *relative* paths. node.exe is a Windows binary and cannot write to MSYS paths like
  # /c/a/..., and it exits 0 anyway — a silent no-op that leaves the previous STL in place.
  # (That is how a 16 mm case survived a "successful" conversion.) Hence: delete first, then assert.
  for f in filtered-output/cases/*.jscad; do
    [ -e "$f" ] || continue
    out="${f%.jscad}.stl"
    rm -f "$out"
    if $NODE node_modules/@jscad/cli/cli.js "$f" -of stla -o "$out" >"/tmp/jscad_$(basename "$f").log" 2>&1 && [ -s "$out" ]; then
      ok "$(basename "$out")"
    else
      bad "$(basename "$out") — no output written (see /tmp/jscad_$(basename "$f").log)"
    fi
  done
fi

# ---------------------------------------------------------------- 6. assembly
if [ "$DO_ASSEMBLY" = 1 ]; then
  step "palm rest + tenting + glb scale fix + full 3D scene"
  if command -v uv >/dev/null 2>&1; then RUN="uv run python"; else RUN="$PY"; fi
  $RUN palmrest_and_tenting_creation/create_palmrest.py >/tmp/palm.log 2>&1 \
    && ok "palm rest" || { bad "palm rest — see /tmp/palm.log"; tail -3 /tmp/palm.log; }
  $RUN palmrest_and_tenting_creation/create_tenting_system.py >/tmp/tent.log 2>&1 \
    && ok "tenting system" || { bad "tenting — see /tmp/tent.log"; tail -3 /tmp/tent.log; }
  $RUN fix_glb_scale.py --verbose >/tmp/scale.log 2>&1 \
    && ok "fix_glb_scale" || { bad "fix_glb_scale — see /tmp/scale.log"; tail -3 /tmp/scale.log; }
  $RUN create_full_3d_visual.py >/tmp/scene.log 2>&1 \
    && ok "combined scene" || { bad "combined scene — see /tmp/scene.log"; tail -3 /tmp/scene.log; }
  echo "   NOTE: create_full_3d_visual.py still hardcodes a -90 deg X rotation and 'PCB up 7 units'"
  echo "         (tuned to the old 16 mm case). Until that is derived from config.yaml the scene"
  echo "         is not dimensionally trustworthy — see docs/HANDOFF-NEXT.md 1c."
fi

# ---------------------------------------------------------------- 7. stamp
if [ "$DO_STAMP" = 1 ]; then
  step "build stamp (what B14 exists for)"
  { echo "commit:      $(git rev-parse HEAD)"
    echo "branch:      $(git rev-parse --abbrev-ref HEAD)"
    echo "config_sha1: $(sha1sum ergogen/config.yaml | cut -d' ' -f1)"
    echo "built:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "builder:     local (scripts/build_outputs.sh)"
  } > filtered-output/BUILD-STAMP.txt
  ok "filtered-output/BUILD-STAMP.txt"
fi

# ---------------------------------------------------------------- 8. verify
if [ "$DO_VERIFY" = 1 ]; then
  step "verify measured geometry against today's design"
  $PY - <<'PY'
import trimesh, re, sys
bad = 0
def mesh(f):
    try: return trimesh.load(f, force='mesh', process=True)
    except Exception: return None
for f, want_h in (("filtered-output/cases/l_case_3d.stl", 11.20),
                  ("filtered-output/cases/r_case_3d.stl", 11.20),
                  ("filtered-output/cases/l_cover.stl", None)):
    m = mesh(f)
    if m is None: print(f"   ?  {f}: missing"); continue
    h = m.bounds[1][2] - m.bounds[0][2]
    tag = "ok " if (want_h is None or abs(h-want_h) < 0.05) else "STALE"
    if tag == "STALE": bad = 1
    print(f"   {tag}{f}: height {h:.2f} mm" + (f" (expected {want_h:.2f})" if want_h else ""))
def plate_stats(p):
    t = open(p, encoding='utf-8').read()
    return t.count('gr_line'), t.count('gr_arc')
for p, label in (("ergogen/output/pcbs/plate_left_full.kicad_pcb", "D2 main"),
                 ("ergogen/output/pcbs/plate_left_bay.kicad_pcb", "D1 optional")):
    a, b = plate_stats(p); print(f"   ok {label:12s} {p.split('/')[-1]:28s} gr_line={a} gr_arc={b}")
v = mesh("filtered-output/cases/tenting_system.stl")
if v is not None and v.volume < 0:
    print(f"   WARN tenting_system.stl volume {v.volume/1000:.1f} cm3 (inverted normals)")
# case.stl is a legacy duplicate that no step regenerates; if present it must agree with
# l_case_3d.stl, otherwise it is a stale file masquerading as the case.
legacy = mesh("filtered-output/cases/case.stl")
main = mesh("filtered-output/cases/l_case_3d.stl")
if legacy is not None and main is not None:
    hl = legacy.bounds[1][2] - legacy.bounds[0][2]; hm = main.bounds[1][2] - main.bounds[0][2]
    if abs(hl - hm) > 0.05:
        print(f"   STALE case.stl is {hl:.2f} mm but l_case_3d.stl is {hm:.2f} -> delete case.stl"); bad = 1
sys.exit(bad)
PY
  [ $? -eq 0 ] && ok "geometry matches" || bad "see rows tagged STALE/WARN"
fi

step "summary"
[ "$FAIL" = 0 ] && echo "   all requested stages passed" || { echo "   some stages failed (see above)"; exit 1; }
echo "   filtered-output: $(find filtered-output -type f | wc -l) files, stamp: $([ -f filtered-output/BUILD-STAMP.txt ] && echo yes || echo NO)"
