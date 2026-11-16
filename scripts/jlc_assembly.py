#!/usr/bin/env python3
"""Build the files JLCPCB's PCB Assembly service actually consumes, and gate them.

JLC reads five declarations and silently drops the part if any one is missing (FASTENERS.md §5.1):
a BoM line with an LCSC code, a CPL row with X/Y/rotation/layer, a footprint with real pads, the
KiCad `attr` flags, and the package/height. B3 was a *declaration* bug: `kibot/jlpcb_pos.kibot.yaml`
had `only_smd: true` while the diode footprint declared no `attr` at all, so the CPL carried 2 of
98 placements. The declarations are fixed in `ergogen/footprints/ceoloide/*.js`; this script turns
the board + KiBot's position export into the two files JLC wants, and refuses to let a part vanish
without saying so.

    ./.venv/Scripts/python.exe scripts/jlc_assembly.py cpl     # KiBot raw CSV -> JLC CPL(s)
    ./.venv/Scripts/python.exe scripts/jlc_assembly.py bom     # PCB        -> JLC BoM(s)
    ./.venv/Scripts/python.exe scripts/jlc_assembly.py check    # gate: does it all agree?

Why a script at all, when KiBot can write a JLC-style CPL:

  * **The BoM cannot come from KiBot.** KiBot's `bom` and `kibom` outputs are schematic outputs;
    Ergogen emits no schematic, so they fail with "No SCH file found" -- which is why the old
    `kibot/jlpcb_bom.kibot.yaml` never produced anything (docs/STATUS.md B7). A PCB-only board has
    to be turned into a BoM by reading the footprints, which is what this script does.
  * **Rotations.** `pre_transform: _rot_footprint_jlcpcb` is a *component* transform, and there
    are no components without a schematic. JLC reads a bottom-side rotation mirrored -- `(180 -
    rot)` -- which is exactly what that transform does (see KiBot's `fil_base.py` and
    docs/JLC-ASSEMBLY.md §3); the mirroring is applied here instead.

Conventions, both verified against `kicad-cli pcb export pos` on this board:

  * Y is **positive up** (KiCad's own .pos convention, `PosY = -Y_board`). No negation, no offset:
    this board has no aux origin, so the gerbers and the CPL share the page origin.
  * X/Y are the footprint's origin, which for every part here is the symmetry centre JLC wants.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PARTS_MAP = REPO / "kibot" / "jlc_parts.csv"

CPL_COLUMNS = ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]
BOM_COLUMNS = ["Comment", "Designator", "Footprint", "LCSC Part #"]
AUDIT_COLUMNS = BOM_COLUMNS + ["Quantity", "Assemble", "Status"]

# KiCad pad types that can be soldered, i.e. that make a footprint a *part* and not a drawing.
SOLDERABLE = {"smd", "thru_hole"}
EXCLUDE_ATTRS = {"exclude_from_pos_files", "exclude_from_bom"}


# --------------------------------------------------------------------------- KiCad PCB parsing

def sexpr(text: str):
    """Minimal S-expression parser: '(' -> list, quoted strings -> str, atoms -> str.

    Regex-parsing `.kicad_pcb` headers fails because KiCad puts `(tstamp ...)` between `(layer
    ...)` and `(at ...)` (HANDOFF.md §8, trap 4) -- this is the same parser check_assembly.py uses.
    """
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack: list[list] = []
    cur: list = []
    for tok in tokens:
        if tok == "(":
            stack.append(cur)
            cur = []
        elif tok == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif tok.startswith('"'):
            cur.append(tok[1:-1])
        else:
            cur.append(tok)
    return cur


def _kids(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def _first(node, key, default=None):
    got = _kids(node, key)
    return got[0] if got else default


@dataclass
class Part:
    """One footprint on the board."""
    ref: str
    footprint: str            # short name, no library prefix
    layer: str                # F.Cu / B.Cu
    x: float
    y: float
    rot: float
    attrs: frozenset[str]
    pad_types: list[str] = field(default_factory=list)
    value: str = ""
    props: dict[str, str] = field(default_factory=dict)

    @property
    def solderable(self) -> bool:
        """A part JLC can physically place: at least one solderable pad (FASTENERS.md §5.1 #3)."""
        return any(t in SOLDERABLE for t in self.pad_types)

    @property
    def excluded(self) -> bool:
        return bool(self.attrs & EXCLUDE_ATTRS)

    @property
    def is_smd(self) -> bool:
        """SMD by *declaration*, not by pad sniffing.

        The choc footprint carries one plated `thru_hole` pad (its centre hole) besides the two
        SMD hotswap pads, so "has a through-hole pad" is the wrong question -- that is the very
        ambiguity that let `kicad-cli pos --smd-only` and KiBot disagree. JLC works from the
        declared class too, and on this board the switch's declared class is `smd`.
        """
        return "smd" in self.attrs and "through_hole" not in self.attrs

    @property
    def side(self) -> str:
        return "Bottom" if self.layer.startswith("B.") else "Top"


def read_board(path: Path) -> list[Part]:
    tree = sexpr(path.read_text(encoding="utf-8", errors="ignore"))
    top = tree[0] if tree and isinstance(tree[0], list) else tree
    parts: list[Part] = []
    for node in _kids(top, "footprint"):
        full = node[1] if len(node) > 1 and isinstance(node[1], str) else ""
        layer_node = _first(node, "layer")
        layer = layer_node[1] if layer_node and len(layer_node) > 1 else "F.Cu"
        at = _first(node, "at")
        vals = [float(v) for v in (at[1:] if at else []) if isinstance(v, str) and _is_num(v)]
        x, y = (vals[0], vals[1]) if len(vals) >= 2 else (0.0, 0.0)
        rot = vals[2] if len(vals) > 2 else 0.0
        attr = _first(node, "attr")
        attrs = frozenset(a for a in (attr[1:] if attr else []) if isinstance(a, str))
        props, value, ref = {}, "", ""
        for prop in _kids(node, "property"):
            if len(prop) > 2 and isinstance(prop[1], str):
                props[prop[1]] = prop[2]
        ref = props.get("Reference", "")
        value = props.get("Value", "")
        pads = []
        for pad in _kids(node, "pad"):
            if len(pad) > 2 and isinstance(pad[2], str):
                pads.append(pad[2])
        parts.append(Part(ref=ref, footprint=full.split(":")[-1], layer=layer, x=x, y=y,
                          rot=rot, attrs=attrs, pad_types=pads, value=value, props=props))
    return parts


def _is_num(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def board_bbox(path: Path) -> tuple[float, float, float, float]:
    """Board outline extent in *board* coordinates (y down), from the Edge.Cuts entities."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    tree = sexpr(text)
    top = tree[0] if tree and isinstance(tree[0], list) else tree
    xs: list[float] = []
    ys: list[float] = []
    for node in top:
        if not (isinstance(node, list) and node and isinstance(node[0], str)):
            continue
        if not node[0].startswith("gr_"):
            continue
        layer = _first(node, "layer")
        if not layer or len(layer) < 2 or layer[1] != "Edge.Cuts":
            continue
        for key in ("start", "end", "mid", "center"):
            for ent in _kids(node, key):
                nums = [v for v in ent[1:] if isinstance(v, str) and _is_num(v)]
                if len(nums) >= 2:
                    xs.append(float(nums[0]))
                    ys.append(float(nums[1]))
        for ent in _kids(node, "xy"):
            nums = [v for v in ent[1:] if isinstance(v, str) and _is_num(v)]
            if len(nums) >= 2:
                xs.append(float(nums[0]))
                ys.append(float(nums[1]))
    if not xs:
        raise SystemExit(f"could not find Edge.Cuts geometry in {path}")
    return min(xs), min(ys), max(xs), max(ys)


# --------------------------------------------------------------------------- parts map

def load_parts_map(path: Path = PARTS_MAP) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh if not ln.lstrip().startswith("#")]
    for row in csv.DictReader(lines):
        name = (row.get("footprint") or "").strip()
        if not name:
            continue
        rows[name] = {
            "comment": (row.get("comment") or "").strip(),
            "lcsc": (row.get("lcsc") or "").strip(),
            "assemble": (row.get("assemble") or "").strip().lower() == "yes",
            "jlc_lib": (row.get("jlc_lib") or "").strip().lower() or "unverified",
        }
    return rows


def natural_key(ref: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", ref)]


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def read_cpl(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


# --------------------------------------------------------------------------- CPL

def jlc_rotation(rot: float, side: str) -> float:
    """JLC reads a bottom-side rotation mirrored: (180 - rot).

    Same rule as KiBot's `_rot_footprint_jlcpcb` transform (`mirror_bottom: True` in
    fil_base.py, documented upstream as "This is used by JLCPCB"), which cannot be used directly
    here because it is a *component* transform and this board has no schematic components.
    A choc hotswap socket is a symmetric 2-pad part, so 180 -> 0 is invisible on the grid keys,
    but the thumbs sit at 170/155/150 and must become 10/25/30 or the pads land 120 deg off.
    """
    if side == "Bottom":
        return round((180.0 - rot) % 360.0, 4)
    return round(rot % 360.0, 4)


def cmd_cpl(args) -> int:
    boards = args.boards
    rc = 0
    for name in boards:
        board = args.pcbs / f"{name}.kicad_pcb"
        raw = args.out / "pcbs" / "pos" / name / f"{name}_cpl_raw.csv"
        if not raw.exists():
            print(f"FAIL  {raw} missing - run KiBot with kibot/jlpcb_pos.kibot.yaml first",
                  file=sys.stderr)
            rc = 1
            continue
        parts = {p.ref: p for p in read_board(board)}
        rows = read_cpl(raw)

        unknown = sorted({p.footprint for p in parts.values()
                          if p.solderable and not p.excluded and p.footprint not in args.parts},
                         key=natural_key)
        if unknown:
            print(f"FAIL  {name}: placeable footprint(s) missing from {PARTS_MAP.name}: {unknown}",
                  file=sys.stderr)
            rc = 1

        assembled, smd, dropped = [], [], []
        for row in rows:
            ref = row["Designator"]
            part = parts.get(ref)
            if part is None:
                print(f"FAIL  {name}: CPL row {ref} is not a footprint on the board", file=sys.stderr)
                rc = 1
                continue
            scope = args.parts.get(part.footprint, {})
            if part.excluded or not part.solderable or not scope.get("assemble", False):
                dropped.append((ref, part.footprint))
                continue
            side = part.side
            # The CPL's Layer/Side comes from the board, and must agree with KiBot's export.
            if row["Layer"].strip().lower()[:3] != side.lower()[:3]:
                print(f"FAIL  {name}: {ref} layer mismatch (board {side}, KiBot {row['Layer']})",
                      file=sys.stderr)
                rc = 1
            out = [ref, f"{float(row['Mid X']):.4f}", f"{float(row['Mid Y']):.4f}",
                   side, f"{jlc_rotation(float(row['Rotation']), side):.4f}"]
            assembled.append(out)
            if part.is_smd:
                smd.append(out)

        assembled.sort(key=lambda r: natural_key(r[0]))
        smd.sort(key=lambda r: natural_key(r[0]))
        write_csv(args.out / "pcbs" / "pos" / name / f"{name}_cpl_jlc.csv", CPL_COLUMNS, assembled)
        write_csv(args.out / "pcbs" / "pos" / name / f"{name}_cpl_jlc_smd.csv", CPL_COLUMNS, smd)
        print(f"  {name}: {len(assembled)} placements for JLC ({len(smd)} SMD + "
              f"{len(assembled) - len(smd)} THT), {len(dropped)} footprint(s) left out")
        for ref, fp in sorted(dropped, key=lambda r: natural_key(r[0])):
            why = ("3D/mechanical preview, no pads" if not parts[ref].solderable
                   else "declared exclude_from_pos_files" if parts[ref].excluded
                   else "assemble=no in kibot/jlc_parts.csv")
            print(f"    - {ref:<6} {fp:<32} {why}")
    return rc


# --------------------------------------------------------------------------- BoM

def bom_groups(parts: list[Part], pmap: dict[str, dict]) -> list[dict]:
    groups: dict[tuple, dict] = {}
    for part in sorted(parts, key=lambda p: natural_key(p.ref)):
        if part.excluded or not part.solderable:
            continue
        scope = pmap.get(part.footprint, {})
        comment = part.value or scope.get("comment", "") or part.footprint
        lcsc = scope.get("lcsc", "") or part.props.get("LCSC", "")
        key = (part.footprint, comment, lcsc, scope.get("assemble", False), scope.get("jlc_lib", ""))
        g = groups.setdefault(key, {"footprint": part.footprint, "comment": comment, "lcsc": lcsc,
                                    "assemble": scope.get("assemble", False),
                                    "jlc_lib": scope.get("jlc_lib", "unverified"), "refs": []})
        g["refs"].append(part.ref)
    out = list(groups.values())
    for g in out:
        if not g["assemble"]:
            status = "HAND-SOLDER"
        elif g["lcsc"]:
            status = "ok"
        elif g["jlc_lib"] == "no":
            status = "NOT-IN-JLC-LIBRARY"
        else:
            status = "MISSING-LCSC"
        g["status"] = status
    return sorted(out, key=lambda g: (g["status"] != "ok", natural_key(g["footprint"])))


def cmd_bom(args) -> int:
    rc = 0
    for name in args.boards:
        board = args.pcbs / f"{name}.kicad_pcb"
        parts = read_board(board)
        groups = bom_groups(parts, args.parts)
        jlc = [[g["comment"], ",".join(g["refs"]), g["footprint"], g["lcsc"]]
               for g in groups if g["assemble"] and g["lcsc"]]
        audit = [[g["comment"], ",".join(g["refs"]), g["footprint"], g["lcsc"],
                  len(g["refs"]), "yes" if g["assemble"] else "no", g["status"]] for g in groups]
        write_csv(args.out / "pcbs" / "bom" / name / f"{name}_bom_jlc.csv", BOM_COLUMNS, jlc)
        write_csv(args.out / "pcbs" / "bom" / name / f"{name}_bom_audit.csv", AUDIT_COLUMNS, audit)

        placed = sum(len(g["refs"]) for g in groups if g["assemble"])
        coded = sum(len(g["refs"]) for g in groups if g["assemble"] and g["lcsc"])
        print(f"  {name}: {len(groups)} unique part(s), {placed} placements for JLC, "
              f"{coded} with an LCSC code -> {len(jlc)} BoM line(s)")
        gaps = [g for g in groups if g["status"] not in ("ok", "HAND-SOLDER")]
        if gaps:
            print(f"  {name}: {len(gaps)} part(s) JLC cannot place until an LCSC code is entered "
                  f"in kibot/jlc_parts.csv:")
            for g in gaps:
                print(f"    ! {g['footprint']:<32} {len(g['refs']):>3}x  "
                      f"{g['comment']:<48} {g['status']}")
    return rc


# --------------------------------------------------------------------------- gate

def cmd_check(args) -> int:
    fails: list[str] = []
    warns: list[str] = []
    print(f"\n=== JLCPCB assembly gate: {args.out}/pcbs")
    for name in args.boards:
        board = args.pcbs / f"{name}.kicad_pcb"
        if not board.exists():
            fails.append(f"{board} missing")
            continue
        parts = read_board(board)
        by_ref = {p.ref: p for p in parts}
        x0, y0, x1, y1 = board_bbox(board)

        # ---- files
        cpl_path = args.out / "pcbs" / "pos" / name / f"{name}_cpl_jlc.csv"
        smd_path = args.out / "pcbs" / "pos" / name / f"{name}_cpl_jlc_smd.csv"
        bom_path = args.out / "pcbs" / "bom" / name / f"{name}_bom_jlc.csv"
        missing = [p.name for p in (cpl_path, smd_path, bom_path) if not p.exists()]
        if missing:
            fails.append(f"{name}: missing {', '.join(missing)}")
            continue
        cpl = read_cpl(cpl_path)
        cpl_smd = read_cpl(smd_path)
        bom = read_cpl(bom_path)

        # ---- CPL shape
        if list(cpl[0].keys() if cpl else CPL_COLUMNS) != CPL_COLUMNS:
            fails.append(f"{name}: CPL columns are {list(cpl[0].keys()) if cpl else '?'}, "
                         f"JLC needs {CPL_COLUMNS}")
        refs = [r["Designator"] for r in cpl]
        dupes = sorted({r for r in refs if refs.count(r) > 1}, key=natural_key)
        if dupes:
            fails.append(f"{name}: duplicate designator(s) in the CPL: {dupes[:6]}")
        bad_layer = sorted({r["Layer"] for r in cpl} - {"Top", "Bottom"})
        if bad_layer:
            fails.append(f"{name}: CPL Layer must be Top/Bottom, found {bad_layer}")

        # ---- every row must be a real, declared, assembled part
        ghost = [r["Designator"] for r in cpl if r["Designator"] not in by_ref]
        if ghost:
            fails.append(f"{name}: CPL designator(s) that are not on the board: {ghost[:6]}")
        leaked = [r["Designator"] for r in cpl
                  if r["Designator"] in by_ref and (by_ref[r["Designator"]].excluded
                                                    or not by_ref[r["Designator"]].solderable)]
        if leaked:
            fails.append(f"{name}: virtual/mechanical footprints leaked into the CPL: {leaked[:6]} "
                         f"(this is what B3 looked like from the other side)")
        unmapped = sorted({by_ref[r["Designator"]].footprint for r in cpl
                           if r["Designator"] in by_ref
                           and by_ref[r["Designator"]].footprint not in args.parts})
        if unmapped:
            fails.append(f"{name}: placeable footprint(s) absent from {PARTS_MAP.name}: {unmapped}")

        # ---- nothing placeable may be missing
        expected = {p.ref for p in parts
                    if p.solderable and not p.excluded
                    and args.parts.get(p.footprint, {}).get("assemble", False)}
        absent = sorted(expected - set(refs), key=natural_key)
        if absent:
            fails.append(f"{name}: {len(absent)} assembled part(s) missing from the CPL: "
                         f"{absent[:8]}")
        tht = {p.ref for p in parts if not p.is_smd}
        if set(r["Designator"] for r in cpl_smd) != expected - tht:
            fails.append(f"{name}: the SMT-only CPL is not the mixed CPL minus the THT parts")
        if set(r["Designator"] for r in cpl) != expected:
            fails.append(f"{name}: mixed CPL is not exactly the assembled part set")

        # ---- coordinates must be inside the board and carry KiCad's y-up convention
        for r in cpl:
            px, py = float(r["Mid X"]), float(r["Mid Y"])
            if not (x0 - 1 <= px <= x1 + 1 and -y1 - 1 <= py <= -y0 + 1):
                fails.append(f"{name}: {r['Designator']} at ({px}, {py}) is outside the board "
                             f"outline x {x0:.1f}..{x1:.1f}, y {-y1:.1f}..{-y0:.1f} "
                             f"(a y-flip puts every placement at y {y0:.1f}..{y1:.1f})")
                break
        if any(not (0 <= float(r["Rotation"]) < 360) for r in cpl):
            fails.append(f"{name}: CPL rotation outside [0, 360)")

        # ---- BoM/CPL agreement
        groups = bom_groups(parts, args.parts)
        gaps = [g for g in groups if g["status"] not in ("ok", "HAND-SOLDER")]
        if gaps:
            missing = sum(len(g["refs"]) for g in gaps)
            first = sorted((r for g in gaps for r in g["refs"]), key=natural_key)[:4]
            warns.append(
                f"{name}: {missing}/{len(expected)} placement(s) have no LCSC code, so they are "
                f"not in the JLC BoM and JLC will not place them: "
                + ", ".join(f"{g['footprint']} {len(g['refs'])}x" for g in gaps)
                + f" (e.g. {first}) -> fill kibot/jlc_parts.csv, docs/JLC-ASSEMBLY.md §6")
        else:
            bom_refs: set[str] = set()
            for row in bom:
                bom_refs |= {d.strip() for d in row["Designator"].split(",") if d.strip()}
            orphan = sorted((expected & set(refs)) - bom_refs, key=natural_key)
            if orphan:
                fails.append(f"{name}: {len(orphan)} placement(s) are in the CPL but not in the "
                             f"JLC BoM even though they have an LCSC code: {orphan[:6]}")
        print(f"  ok    {name}: {len(cpl)} placements in the JLC CPL "
              f"({len(cpl_smd)} SMT-only), {len(bom)} BoM line(s), "
              f"{len(groups)} unique part(s), {len(gaps)} LCSC gap(s)")

    for w in warns:
        print(f"WARN  {w}")
    for f in fails:
        print(f"FAIL  {f}")
    if fails:
        print(f"\nFAIL - {len(fails)} problem(s); do not upload this assembly data\n", file=sys.stderr)
        return 1
    print("\nPASS  CPL rows, declarations and BoM agree\n")
    return 0


# --------------------------------------------------------------------------- main

def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["cpl", "bom", "check"])
    ap.add_argument("--pcbs", default="ergogen/output/pcbs",
                    help="folder with <board>.kicad_pcb (default: ergogen/output/pcbs)")
    ap.add_argument("--out", default="filtered-output",
                    help="published root, i.e. the parent of pcbs/ (default: filtered-output)")
    ap.add_argument("--parts", default=str(PARTS_MAP), help="parts map (default: kibot/jlc_parts.csv)")
    ap.add_argument("--boards", nargs="+", default=["left_pcb", "right_pcb"])
    args = ap.parse_args()
    args.pcbs = Path(args.pcbs)
    args.out = Path(args.out)
    args.parts = load_parts_map(Path(args.parts))
    return {"cpl": cmd_cpl, "bom": cmd_bom, "check": cmd_check}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
