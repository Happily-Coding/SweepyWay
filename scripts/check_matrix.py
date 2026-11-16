#!/usr/bin/env python3
"""Validate the generated KiCad PCB(s) against the design rules that actually break keyboards.

Checks (per board):
  1. every row net used by a diode is connected to exactly one MCU pin
  2. every column net used by a switch is connected to exactly one MCU pin
  3. no MCU pin group is duplicated on a row/column net (two GPIOs shorted)
  4. no MCU pin is wasted on a row/column net that has no keys
  5. every key has both a switch and a diode, and (col,row) pairs are unique
  6. --routing: the board actually has copper (segments + vias)
  7. --plates: every switch-plate cutout is a full switch size (catches half-size holes)
  7. left/right parity: both halves contain the same footprint types

Exit code 0 = all good, 1 = at least one FAIL.

Usage:
  ./scripts/check_matrix.py                       # default board paths
  ./scripts/check_matrix.py --routing
  ./scripts/check_matrix.py --counts
  ./scripts/check_matrix.py --board path/to.kicad_pcb

Pure stdlib, no dependencies.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

DEFAULT_BOARDS = [
    "ergogen/output/pcbs/left_pcb.kicad_pcb",
    "ergogen/output/pcbs/right_pcb.kicad_pcb",
]

# Nets that are allowed to appear on many MCU pins (power/ground/special).
POWER_NETS = {"GND", "RAW", "VCC", "RST", "VBUS", "3V3", "AGND", "PWR"}

MCU_HINTS = ("mcu_nice_nano", "promicro", "elite_c", "kb2040", "xiao")
# Key nets look like col1_row4 on the left half and mirror_col1_row4 on the right,
# plus thumb nets such as col1_thumb_row_1.
KEY_NET_RE = re.compile(r"(?:mirror_)?col\d+_.*row.*")

def is_key_net(name: str) -> bool:
    return bool(KEY_NET_RE.fullmatch(name))
DIODE_HINTS = ("diode",)
SWITCH_HINTS = ("switch_choc", "choc_v1_v2", "switch_mx", "switch_gateron")


def fail(msg: str) -> None:
    print(f"  FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def warn(msg: str) -> None:
    print(f"  warn  {msg}")


def balanced(text: str, start: int) -> str:
    """Return the s-expression starting at text[start] (which must be '(')."""
    depth = 0
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i += 1
            while i < n and text[i] != '"':
                if text[i] == "\\":
                    i += 1
                i += 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    return text[start:]


def split_footprints(text: str):
    """Yield (footprint_name, block_text) for every footprint in the board."""
    for m in re.finditer(r'\(footprint\s+"([^"]+)"', text):
        yield m.group(1), balanced(text, m.start())


def footprint_ref(block: str) -> str | None:
    m = re.search(r'\(property\s+"Reference"\s+"([^"]*)"', block)
    if m:
        return m.group(1)
    m = re.search(r'\(fp_text\s+reference\s+"([^"]*)"', block)
    return m.group(1) if m else None


def block_net_pads(block: str):
    """Return list of (pad_name, net_name) for the pads of one footprint."""
    out = []
    for m in re.finditer(r'\(pad\s+"([^"]*)"', block):
        expr = balanced(block, m.start())
        net = re.search(r'\(net\s+\d+\s+"([^"]*)"\)', expr)
        out.append((m.group(1), net.group(1) if net else ""))
    return out


def classify(name: str) -> str:
    low = name.lower()
    if any(h in low for h in MCU_HINTS):
        return "mcu"
    if any(h in low for h in DIODE_HINTS):
        return "diode"
    if any(h in low for h in SWITCH_HINTS):
        return "switch"
    return "other"



def edge_loops(text: str):
    """Return [(w, h, x, y)] for each connected Edge.Cuts loop (holes and outline)."""
    segs = []
    for m in re.finditer(r"\((?:gr_line|gr_arc)\b", text):
        body = balanced(text, m.start())
        if "Edge.Cuts" not in body:
            continue
        pts = [(round(float(a), 2), round(float(b), 2)) for a, b in
               re.findall(r"\((?:start|end)\s+(-?[\d.]+)\s+(-?[\d.]+)\)", body)]
        if len(pts) >= 2:
            segs.append((pts[0], pts[1]))
    if not segs:
        return []
    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in segs:
        union(a, b)
    groups = {}
    for a, b in segs:
        groups.setdefault(find(a), set()).update([a, b])
    out = []
    for pts in groups.values():
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        out.append((round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2),
                    round(min(xs), 2), round(min(ys), 2)))
    return out


def check_plate(path: Path, expect_min: float, expect_max: float):
    """Every switch hole in a plate must be a full cutout; deliberate small holes are fine.

    Tiny loops (< 3.5 mm) are mounting/screw holes and degenerate arc slivers -> ignored.
    Anything between that and a switch cutout is a bug (e.g. the half-size-hole regression).
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    loops = edge_loops(text)
    big = [l for l in loops if min(l[0], l[1]) < 120]     # ignore the outer border
    tiny = [l for l in big if min(l[0], l[1]) < 3.5]      # screw holes + arc slivers
    suspicious = [l for l in big if 3.5 <= min(l[0], l[1]) < expect_min]
    good = [l for l in big if expect_min <= min(l[0], l[1]) <= expect_max + 3]
    print(f"\n=== plate {path} ===")
    print(f"  switch cutouts: {len(good)}   small (screw/artefact): {len(tiny)}   suspicious: {len(suspicious)}")
    if suspicious:
        worst = min(suspicious, key=lambda l: min(l[0], l[1]))
        fail(f"{len(suspicious)} cutout(s) between 3.5 and {expect_min} mm "
             f"(smallest {worst[0]} x {worst[1]} at {worst[2]},{worst[3]}) "
             f"-> switches cannot pass through; check l_keys_outline size (it is FULL extent)")
        return False
    if not good:
        fail("no switch-sized cutouts found in the plate")
        return False
    ok(f"{len(good)} switch cutouts are full size (>= {expect_min} mm)")
    return True


def analyse(path: Path, routing: bool, counts: bool):
    text = path.read_text(encoding="utf-8", errors="ignore")
    result = {
        "path": path,
        "footprints": collections.Counter(),
        "mcu_net_pads": collections.defaultdict(list),  # net -> [pad names]
        "row_diodes": collections.Counter(),
        "col_switches": collections.Counter(),
        "keys": collections.Counter(),  # colrow net -> count (switch+diode)
        "problems": [],
    }

    for name, block in split_footprints(text):
        kind = classify(name)
        short = name.split("/")[-1].split(":")[-1]
        result["footprints"][short] += 1
        nets = block_net_pads(block)
        net_names = {n for _, n in nets if n}

        if kind == "mcu":
            for pad, net in nets:
                if net:
                    result["mcu_net_pads"][net].append(pad)
        elif kind == "diode":
            for net in net_names:
                if re.fullmatch(r"R\d+", net):
                    result["row_diodes"][net] += 1
            for net in net_names:
                if is_key_net(net):
                    result["keys"][net] += 1
        elif kind == "switch":
            for net in net_names:
                if re.fullmatch(r"C\d+", net):
                    result["col_switches"][net] += 1
            for net in net_names:
                if is_key_net(net):
                    result["keys"][net] += 1

    # ---- 1 & 2: every row/col used by a key must reach exactly one MCU pin
    for label, nets in (("row", result["row_diodes"]), ("column", result["col_switches"])):
        for net in sorted(nets, key=natural):
            pins = result["mcu_net_pads"].get(net, [])
            if not pins:
                result["problems"].append(
                    f"{label} net {net} has {nets[net]} key(s) but NO MCU pin (dead {label})"
                )
            elif len(pins) > 1:
                result["problems"].append(
                    f"{label} net {net} is on {len(pins)} MCU pins {pins} (shorted GPIOs)"
                )

    # ---- 4: MCU pins wasted on row/col nets without keys
    key_nets = set(result["row_diodes"]) | set(result["col_switches"])
    for net, pads in sorted(result["mcu_net_pads"].items(), key=lambda kv: natural(kv[0])):
        if re.fullmatch(r"[RC]\d+", net) and net not in key_nets:
            result["problems"].append(
                f"MCU pin(s) {pads} assigned to {net}, but no keys use {net} (wasted pin)"
            )

    # ---- 3: duplicate MCU pins on the same non-power net
    for net, pads in result["mcu_net_pads"].items():
        if net.upper() in POWER_NETS:
            continue
        if len(pads) > 1:
            msg = f"MCU pins {pads} are all on net {net}"
            if msg not in result["problems"]:
                result["problems"].append(msg)

    # ---- 5: keys must have both a switch and a diode, unique (col,row)
    for keynet, n in sorted(result["keys"].items(), key=lambda kv: natural(kv[0])):
        if n != 2:
            result["problems"].append(
                f"key {keynet} appears {n} time(s) among switches+diodes (expected 2: one of each)"
            )

    # ---- 6: routing
    segments = len(re.findall(r"\(segment\b", text))
    vias = len(re.findall(r"\(via\b", text))
    result["segments"], result["vias"] = segments, vias
    if routing and (segments == 0 or vias == 0):
        result["problems"].append(
            f"board has {segments} track segments and {vias} vias -> NOT routed, do not order"
        )

    # board size from Edge.Cuts
    xs, ys = [], []
    for m in re.finditer(r"\((?:gr_line|gr_arc)\b", text):
        body = balanced(text, m.start())
        if "Edge.Cuts" not in body:
            continue
        for c in re.finditer(r"\((?:start|mid|end)\s+(-?[\d.]+)\s+(-?[\d.]+)\)", body):
            xs.append(float(c.group(1)))
            ys.append(float(c.group(2)))
    result["bbox"] = (max(xs) - min(xs), max(ys) - min(ys)) if xs else None
    result["thickness"] = re.search(r"\(thickness\s+([\d.]+)\)", text)
    result["thickness"] = result["thickness"].group(1) if result["thickness"] else "?"

    return result


def natural(s: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


def report(res, counts: bool, routing: bool) -> bool:
    p = res["path"]
    print(f"\n=== {p} ===")
    keys = len(res["keys"])
    if keys == 0:
        # Without this guard, pointing --board at a config YAML (or any non-PCB file) printed a
        # reassuring PASS with 0 keys in it - the worst possible failure mode for a gate.
        fail(f"{p}: no matrix keys found - not a generated PCB (0 keys cannot be validated)")
        return False
    if res["bbox"]:
        print(f"  board {res['bbox'][0]:.1f} x {res['bbox'][1]:.1f} mm   "
              f"thickness field: {res['thickness']} mm   "
              f"segments: {res['segments']}   vias: {res['vias']}")
    print(f"  keys: {keys}   rows: {len(res['row_diodes'])}   columns: {len(res['col_switches'])}")
    if counts:
        for name, n in res["footprints"].most_common():
            print(f"    {n:3d}  {name}")

    rows = ", ".join(f"{k}x{v}" for k, v in sorted(res["row_diodes"].items(), key=lambda kv: natural(kv[0])))
    print(f"  keys per row: {rows}")
    mc = ", ".join(
        f"{net}:{','.join(pads)}"
        for net, pads in sorted(res["mcu_net_pads"].items(), key=lambda kv: natural(kv[0]))
        if re.fullmatch(r"[RC]\d+", net)
    )
    print(f"  MCU row/column pins: {mc}")

    if res["problems"]:
        for prob in res["problems"]:
            fail(prob)
        return False
    ok("matrix, pin map and net usage are consistent")
    if routing:
        ok(f"board is routed ({res['segments']} segments, {res['vias']} vias)")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", action="append", default=None, help="kicad_pcb path (repeatable)")
    ap.add_argument("--routing", action="store_true", help="also require routed copper")
    ap.add_argument("--counts", action="store_true", help="print footprint counts")
    ap.add_argument("--plates", action="store_true",
                    help="also verify switch-plate cutout sizes (plate_*.kicad_pcb)")
    ap.add_argument("--pcbs-dir", default="ergogen/output/pcbs",
                    help="directory holding the generated pcbs/plates (default ergogen/output/pcbs)")
    ap.add_argument("--json", action="store_true", help="machine-readable summary on stdout")
    ap.add_argument("--plate-size", type=float, default=13.8,
                    help="minimum acceptable switch cutout in mm (default 13.8)")
    args = ap.parse_args()

    paths = [Path(b) for b in (args.board or DEFAULT_BOARDS)]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print("Missing generated boards (run ./scripts/regen.sh first):")
        for m in missing:
            print(f"  - {m}")
        return 1

    results = [analyse(p, args.routing, args.counts) for p in paths]
    good = all([report(r, args.counts, args.routing) for r in results])

    if args.plates:
        for plate in sorted(Path(args.pcbs_dir).glob("plate_*.kicad_pcb")):
            good = check_plate(plate, args.plate_size, args.plate_size + 1.2) and good

    # ---- 7: parity between halves
    if len(results) == 2:
        a, b = results
        print("\n=== left/right parity ===")
        types_a, types_b = set(a["footprints"]), set(b["footprints"])
        only_a = sorted(types_a - types_b)
        only_b = sorted(types_b - types_a)
        diffs = {t for t in types_a & types_b if a["footprints"][t] != b["footprints"][t]}
        if only_a or only_b or diffs:
            for t in only_a:
                fail(f"{t} exists only on {a['path'].name} ({a['footprints'][t]}×)")
            for t in only_b:
                fail(f"{t} exists only on {b['path'].name} ({b['footprints'][t]}×)")
            for t in sorted(diffs):
                fail(f"{t}: {a['footprints'][t]}× on left vs {b['footprints'][t]}× on right")
            good = False
        else:
            ok("both halves have identical footprint composition")

    if args.json:
        summary = {
            "ok": good,
            "boards": [
                {
                    "path": str(r["path"]),
                    "keys": len(r["keys"]),
                    "rows": len(r["row_diodes"]),
                    "columns": len(r["col_switches"]),
                    "segments": r["segments"],
                    "vias": r["vias"],
                    "bbox": r["bbox"],
                    "thickness": r["thickness"],
                    "footprints": dict(r["footprints"]),
                    "problems": r["problems"],
                }
                for r in results
            ],
        }
        print("__JSON__" + json.dumps(summary))
    else:
        print("\n" + ("PASS" if good else "FAIL"))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
