#!/usr/bin/env python3
"""Generate the *fastener* BOM from the vertical stack, and gate it.

The stack (B17) is derived from `standoff_length`, so the screws that hold it must be derived too
(B21): a screw has to cross the fixed stack on its own side of the standoff and then bite into it,
without the two screws meeting in the middle and without the heads sticking out.

B20 option D (`plate_sits_on_wall: 1`, docs/B20-PLATE-ON-WALL.md) splits the top of the stack in
two, and this file is where that must NOT be fudged:

    wall top / case_border_height = floor + standoff + PCB + band - plate   = 11.2
    plate TOP (rim in the old sense) = floor + standoff + PCB + band        = 12.4

Before D they were the same number and `case_border_height` was both. A `--case-stl` assertion that
still compared the STL height to 12.4 would now be asserting the wrong thing, so the case height and
the plate top are carried separately (`wall_top` vs `plate_top`).

Reads the units from `ergogen/config.yaml`, computes everything, and writes
`docs/HARDWARE-BOM.md`. Exits non-zero if the screw/stack combination does not work, so it can be
used as a gate after changing `standoff_length`.

    ./.venv/Scripts/python.exe scripts/hardware_bom.py
    ./.venv/Scripts/python.exe scripts/hardware_bom.py --standoff 8     # what-if
    ./.venv/Scripts/python.exe scripts/hardware_bom.py --case-stl build/l_case_3d.stl
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "ergogen" / "config.yaml"
OUT = REPO / "docs" / "HARDWARE-BOM.md"

# From ceoloide/screw-preview-top.js + McMaster listings it references.
HEAD_HEIGHT = {"pan": 1.2, "low_socket": 1.0, "flat": 0.0}
STD_M2 = [4, 5, 6, 8, 10, 12]
MCMASTER_M2_LOW_SOCKET = {
    4: "93070A274", 5: "93070A275", 6: "93070A276",
    8: "93070A277", 10: "93070A278", 12: "92855A841",
}
SOCKET_DEPTH = 3.5  # Kailh choc hotswap socket protrusion below the PCB (HARDWARE-STACK §2)
BOSS_MIN = 1.0  # thinnest printed boss worth printing under a soldered standoff (F3b)
MOUNT_GAP_IDEAL = 0.5  # keep the two screws from meeting inside the standoff
# M2 heat-set insert (the common brass type), used by the "boss" topology.
INSERT_LEN, INSERT_OD = 3.2, 3.6
INSERT_WALL = 1.2


def units(path: Path) -> dict[str, float]:
    """Pull the plain numeric scalars we need out of the units block."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    want = [
        "case_bottom_thickness", "standoff_length", "standoff_body_length", "pcb_thickness",
        "plate_top_above_pcb_top", "top_plate_thickness", "screw_engagement",
    ]
    got: dict[str, float] = {}
    for key in want:
        m = re.search(rf"^  {key}:\s*([-\d.]+)", text, flags=re.M)
        if not m:
            raise SystemExit(f"could not find units.{key} in {path}")
        got[key] = float(m.group(1))
    # B20-D. Optional on purpose: a config without the flag is the pre-D stack (wall top == plate top).
    m = re.search(r"^  plate_sits_on_wall:\s*([-\d.]+)", text, flags=re.M)
    got["plate_sits_on_wall"] = float(m.group(1)) if m else 0.0
    m = re.search(r"^  screw_top_length:\s*([-\d.]+)", text, flags=re.M)
    got["screw_top_length"] = float(m.group(1)) if m else float("nan")
    m = re.search(r"^  screw_bottom_length:\s*([-\d.]+)", text, flags=re.M)
    got["screw_bottom_length"] = float(m.group(1)) if m else float("nan")
    return got


def evaluate(u: dict[str, float], standoff: float | None = None) -> dict:
    s = u["standoff_length"] if standoff is None else standoff
    floor, pcb = u["case_bottom_thickness"], u["pcb_thickness"]
    # F3b: the metal part hangs `body` mm below the PCB; the printed boss fills the rest.
    body = u.get("standoff_body_length", s)
    boss = s - body
    band, plate = u["plate_top_above_pcb_top"], u["top_plate_thickness"]
    eng = u["screw_engagement"]
    air = band - plate
    # B20-D: `plate_top` is where the FR4 plate's TOP face ends up (12.4, unchanged since B17).
    # `wall_top` is the printed wall (case_border_height): equal to plate_top before D, and one
    # plate thickness lower under D, because the plate then sits ON the wall and overhangs it.
    plate_top = floor + s + pcb + band
    sits = 1 if u.get("plate_sits_on_wall", 0) else 0
    wall_top = plate_top - sits * plate
    top_stack = plate + air + pcb
    bottom_stack = floor
    head_t, head_b = HEAD_HEIGHT["low_socket"], HEAD_HEIGHT["low_socket"]
    bite_t = u["screw_top_length"] - top_stack
    bite_b = u["screw_bottom_length"] - bottom_stack
    return {
        "s": s, "floor": floor, "pcb": pcb, "band": band, "plate": plate, "eng": eng,
        "body": body, "boss": boss, "bottom_stack_f3b": floor + max(boss, 0.0),
        "air": air, "rim": plate_top, "plate_top": plate_top, "wall_top": wall_top,
        "plate_sits_on_wall": sits,
        "top_stack": top_stack, "bottom_stack": bottom_stack,
        "bite_top": bite_t, "bite_bottom": bite_b,
        "middle_gap": s - (bite_t + bite_b),
        "socket_clearance": s - SOCKET_DEPTH,
        "head_t": head_t, "head_b": head_b,
        "counterbore_left": floor - head_b,
        "screw_top": u["screw_top_length"], "screw_bottom": u["screw_bottom_length"],
    }


def min_standoff(u: dict[str, float]) -> float:
    """Smallest standoff that keeps MOUNT_GAP_IDEAL between the two screws."""
    r = evaluate(u)
    return r["bite_top"] + r["bite_bottom"] + MOUNT_GAP_IDEAL


def main() -> int:
    # the report uses → and ≥; the Windows console defaults to cp1252
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(CONFIG))
    ap.add_argument("--standoff", type=float, default=None, help="what-if standoff length")
    ap.add_argument("--case-stl", default=None, help="optional: assert this STL's height == rim")
    ap.add_argument("--topology", choices=["auto", "standoff", "soldered", "printed", "boss"],
                    default="auto",
                    help="auto (default) picks from standoff_body_length: 0 < body < standoff_length "
                         "-> soldered (F3b), body == standoff_length -> press-fit standoff, "
                         "body == 0 -> printed post (thread in plastic). 'boss' = legacy heat-set.")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    u = units(Path(args.config))
    r = evaluate(u, args.standoff)
    if args.topology == "auto":
        body, s = r["body"], r["s"]
        args.topology = ("soldered" if 0 < body < s else
                         "standoff" if body >= s else "printed")
    fails: list[str] = []
    warns: list[str] = []

    def chk(ok: bool, msg: str, warn: bool = False) -> None:
        if not ok:
            (warns if warn else fails).append(msg)

    chk(abs(r["air"] - 1.0) < 0.05,
        f"choc air gap is {r['air']:.2f} mm, must be 1.00 (plate top = PCB top + 2.2)")
    if r["plate_sits_on_wall"]:
        chk(abs(r["plate_top"] - r["wall_top"] - r["plate"]) < 1e-6,
            f"plate_sits_on_wall is set but plate top {r['plate_top']:.2f} - wall top "
            f"{r['wall_top']:.2f} is not the plate thickness {r['plate']:.2f}")
    chk(r["socket_clearance"] >= 1.0,
        f"only {r['socket_clearance']:.2f} mm between the hotswap sockets and the case floor "
        f"(need >= 1.0; sockets are {SOCKET_DEPTH} mm deep)")
    if args.topology == "standoff":
        chk(r["bite_top"] >= r["eng"],
            f"top screw bites only {r['bite_top']:.2f} mm (want >= {r['eng']:.1f})")
    if args.topology in ("soldered", "printed"):
        chk(r["boss"] >= 0,
            f"standoff_body_length {r['body']:.1f} exceeds standoff_length {r['s']:.1f} — the metal "
            f"part would not fit")
        if args.topology == "soldered":
            chk(r["boss"] >= BOSS_MIN,
                f"printed boss is only {r['boss']:.2f} mm tall (need >= {BOSS_MIN:.1f} to print reliably)")
    if args.topology == "standoff":
        chk(r["bite_bottom"] >= r["eng"],
            f"bottom screw bites only {r['bite_bottom']:.2f} mm (want >= {r['eng']:.1f})")
        chk(r["middle_gap"] >= 0,
            f"the two screws overlap by {-r['middle_gap']:.2f} mm inside the standoff")
        chk(r["middle_gap"] >= MOUNT_GAP_IDEAL,
            f"only {r['middle_gap']:.2f} mm between the screw tips (want >= {MOUNT_GAP_IDEAL}); "
            f"a standoff of {min_standoff(u):.1f} mm would fix it", warn=True)
        chk(r["screw_top"] in STD_M2 and r["screw_bottom"] in STD_M2,
            f"non-standard screw length ({r['screw_top']} / {r['screw_bottom']}); stock M2: {STD_M2}")
        chk(r["counterbore_left"] >= 1.5,
            f"counterboring the bottom head ({r['head_b']:.1f} mm) leaves only "
            f"{r['counterbore_left']:.2f} mm of case floor")

    if args.case_stl:
        import trimesh
        h = round(float(trimesh.load(args.case_stl).extents[2]), 2)
        # B20-D: the STL is the PRINTED WALL, so it must equal the wall top, not the plate top.
        chk(abs(h - r["wall_top"]) < 0.05,
            f"case STL is {h:.2f} mm tall but the stack says the wall top (case_border_height) "
            f"must be {r['wall_top']:.2f}"
            + (f" (plate top stays {r['plate_top']:.2f})" if r["plate_sits_on_wall"] else ""))

    per_half = 5
    if args.topology in ("soldered", "printed"):
        # ONE screw per point, from below: floor + boss, then into the metal thread (or plastic).
        need = r["bottom_stack_f3b"] + r["eng"]
        bottom_screw = min([L for L in STD_M2 if L >= need], default=None)
        chk(bottom_screw is not None, f"no stock M2 length reaches {need:.1f} mm")
        top_screw = bottom_screw or 0
        bite = (bottom_screw or 0) - r["bottom_stack_f3b"]
        chk(bite >= r["eng"],
            f"single screw bites only {bite:.2f} mm (want >= {r['eng']:.1f})")
        if args.topology == "soldered":
            chk(bite <= r["body"] + 0.6,
                f"the screw would run {bite - r['body']:.1f} mm past the far end of the "
                f"{r['body']:.1f} mm standoff thread (it stops on the stud — harmless, but check)",
                warn=True)
            rows = [
                ("Standoff, soldered into the PCB by JLCPCB (supplies the ONLY thread)",
                 "XHHD M2×3+3, LCSC **C192879** (5 333 in stock, $0.013)", per_half * 2),
                ("Screw (from below: through floor + boss, into the standoff)",
                 f"M2 × {bottom_screw} mm low-profile socket head", per_half * 2),
                ("Printed boss (part of the case — nothing to buy)",
                 f"Ø{2 * 2.1:.1f} × {r['boss']:.1f} mm, threadless, derived", "-"),
            ]
            extra = [
                f"- **No top screw.** The 32 switches hold the plate; the metal part holds the PCB.",
                f"- Boss height is DERIVED: `standoff_length {r['s']:.1f} − body {r['body']:.1f} = "
                f"{r['boss']:.1f} mm`. Change `standoff_body_length` and this follows.",
                f"- Load path: PCB → standoff top face → boss → floor, i.e. **metal in compression** "
                f"under typing force. The solder joint only retains.",
                f"- Screw head sits {r['head_b']:.1f} mm below the floor unless counterbored "
                f"(floor is {r['floor']:.1f} mm, so a counterbore is available).",
            ]
        else:
            rows = [
                ("Screw (from below: through floor + printed post)",
                 f"M2 × {bottom_screw} mm low-profile socket head", per_half * 2),
                ("Printed post (part of the case)",
                 f"Ø{2 * 2.1:.1f} × {r['s']:.1f} mm, thread in plastic", "-"),
            ]
            extra = [
                "- `standoff_body_length: 0` — no metal part at all: the thread is in the printed "
                "plastic. Cheapest, weakest (F1).",
            ]
        rows_ready = True
    else:
        rows_ready = False
    if args.topology == "boss":
        top_screw = min([L for L in STD_M2 if L >= r["top_stack"] + r["eng"]], default=None)
        boss_ok = r["s"] >= INSERT_LEN + 1.0
        od = INSERT_OD + 2 * INSERT_WALL
        chk(top_screw is not None, "no stock M2 length reaches the insert")
        chk(boss_ok, f"boss is only {r['s']:.1f} mm tall; an M2 heat-set insert is {INSERT_LEN} mm "
                     f"and needs >= {INSERT_LEN + 1.0:.1f} mm of plastic")
        rows = [
            (f"Heat-set insert M2 (Ø{INSERT_OD} × {INSERT_LEN} mm) in the printed boss",
             "brass, heat-set", per_half * 2),
            ("Screw (through plate + air + PCB, into the insert)",
             f"M2 × {top_screw} mm low-profile socket head", per_half * 2),
        ]
        extra = [
            f"- **No standoff and no bottom screw** — the boss is part of the case floor, so the",
            f"  counterbore problem disappears entirely.",
            f"- Printed boss: **{r['s']:.1f} mm tall, Ø{od:.1f} mm min** (insert Ø{INSERT_OD} + "
            f"2 × {INSERT_WALL} wall). Check it clears the hotswap sockets below the PCB.",
            f"- Screw crosses {r['top_stack']:.1f} mm then bites {top_screw - r['top_stack']:.2f} mm "
            f"into the insert.",
        ]
    elif args.topology == "standoff":
        top_screw = r["screw_top"]
        extra = [
            f"- Gap between the two screw tips inside the standoff: **{r['middle_gap']:.2f} mm**",
            f"  (blind-threaded needs ≥ {MOUNT_GAP_IDEAL}; through-threaded tolerates 0)",
            f"- Minimum standoff for a {MOUNT_GAP_IDEAL} mm tip gap: **{min_standoff(u):.1f} mm**",
        ]
        rows = [
            ("Standoff (female-female, splined press-fit)", f"M2 × {r['s']:.1f} mm", per_half * 2),
            ("Top screw (into the standoff, from above)",
             f"M2 × {r['screw_top']:.0f} mm low-profile socket head"
             + (f" ({MCMASTER_M2_LOW_SOCKET.get(r['screw_top'], '?')})" if r['screw_top'] in MCMASTER_M2_LOW_SOCKET else ""),
             per_half * 2),
            ("Bottom screw (into the standoff, from below)",
             f"M2 × {r['screw_bottom']:.0f} mm low-profile socket head"
             + (f" ({MCMASTER_M2_LOW_SOCKET.get(r['screw_bottom'], '?')})" if r['screw_bottom'] in MCMASTER_M2_LOW_SOCKET else ""),
             per_half * 2),
        ]

    md = [
        "# Hardware BOM — fasteners (GENERATED)",
        "",
        "> Generated by `scripts/hardware_bom.py` from `ergogen/config.yaml`. **Do not edit by hand**;",
        "> change `standoff_length` / `screw_*_length` and re-run. Re-run it after any change to the",
        "> vertical stack — that is the point of it (B17 + B21).",
        "",
        f"## Vertical stack  (topology = {args.topology}, standoff = {r['s']:.1f} mm"
        + (f", metal part {r['body']:.1f} mm, printed boss {r['boss']:.1f} mm)"
           if args.topology in ("soldered", "printed") else ")"),
        "",
        "| Layer | Thickness | Running top |",
        "|---|---:|---:|",
        f"| case floor | {r['floor']:.1f} | {r['floor']:.1f} |",
    ]
    if args.topology == "soldered":
        md += [
            f"| boss printed on the floor (threadless) | {r['boss']:.1f} | {r['floor'] + r['boss']:.1f} |",
            f"| **soldered standoff** {r['body']:.1f} mm (holds the thread) | {r['body']:.1f} | "
            f"{r['floor'] + r['s']:.1f} = PCB bottom |",
        ]
    else:
        md += [f"| {'boss (printed)' if args.topology == 'boss' else 'standoff'} — sets the PCB height | "
               f"{r['s']:.1f} | {r['floor'] + r['s']:.1f} |"]
    md += [
        f"| PCB | {r['pcb']:.1f} | {r['floor'] + r['s'] + r['pcb']:.1f} |",
        f"| air gap (choc rule) | {r['air']:.1f} | {r['plate_top'] - r['plate']:.1f} = plate underside |",
        (f"| plate `top_plate_thickness` **sits ON the wall** | {r['plate']:.1f} | "
         f"**{r['plate_top']:.1f}** = plate top (= the old rim) |"
         if r["plate_sits_on_wall"] else
         f"| plate `top_plate_thickness` | {r['plate']:.1f} | **{r['plate_top']:.1f}** = case rim |"),
        "",
        (f"- **B20 option D**: the printed wall stops at the plate's underside "
         f"(`case_border_height` = **{r['wall_top']:.1f}** mm); the FR4 plate overhangs it and is the lid, "
         f"so its edge has full-perimeter support and nothing extra is printed. The plate top stays "
         f"{r['plate_top']:.1f} mm, so keycaps, USB-C and the screw stack do not move."
         if r["plate_sits_on_wall"] else
         f"- `plate_sits_on_wall: 0` (pre-B20-D): the wall runs to the plate TOP "
         f"({r['plate_top']:.1f} mm) and the plate hangs inside the cavity on the switch latches."),
        f"- Wall height (`case_border_height`) = **{r['wall_top']:.1f} mm** — this is what a case STL must measure.",
        f"- Hotswap sockets need {SOCKET_DEPTH} mm under the PCB -> clearance **{r['socket_clearance']:.2f} mm**",
        f"- Keycap tops sit {3.7:.1f} mm above the plate -> **{3.7:.1f} mm above the plate top** (never walled in)",
        "",
        "## Fasteners  (a full keyboard = 2 halves)",
        "",
        "| Part | Spec | Qty |",
        "|---|---|---:|",
    ]
    md += [f"| {a} | {b} | {c} |" for a, b, c in rows]
    md += [
        "",
        "## Screw engagement",
        "",
        "| Screw | Crosses | Length | Bites in | Head |",
        "|---|---|---:|---:|---|",
    ]
    if args.topology in ("soldered", "printed", "boss"):
        md += [f"| single (from below) | floor {r['floor']:.1f} + boss {r['boss']:.1f} = "
               f"{r['bottom_stack_f3b']:.1f} | {top_screw:.0f} | "
               f"**{(top_screw - r['bottom_stack_f3b']):.2f}** | {r['head_b']:.1f} mm proud below "
               f"the floor (floor is {r['floor']:.1f} mm → counterbore available) |"]
    else:
        md += [f"| top/single | plate {r['plate']:.1f} + air {r['air']:.1f} + PCB {r['pcb']:.1f} = "
               f"{r['top_stack']:.1f} | {top_screw:.0f} | **{top_screw - r['top_stack']:.2f}** | "
               f"{r['head_t']:.1f} mm proud of the plate (under the keycaps, fine) |"]
    if args.topology == "standoff":
        md += [f"| bottom | floor {r['bottom_stack']:.1f} | {r['screw_bottom']:.0f} | "
               f"**{r['bite_bottom']:.2f}** | {r['head_b']:.1f} mm proud below the floor → **needs "
               f"a {r['head_b']:.1f} mm counterbore** (or rubber feet ≥ {r['head_b']:.1f} mm) |"]
    md += [""] + extra + [""]
    if args.topology in ("standoff", "soldered", "printed"):
        md += [
            "## Case bottom ↔ tenting base / rubber feet",
            "",
            f"- The bottom screw heads stand **{r['head_b']:.1f} mm proud of the case floor**. If the case",
            f"  sits directly on the tenting base, that gap must exist in the base: put **{r['head_b']:.1f} mm-deep,",
            f"  Ø5 mm pockets** at the 5 screw positions (the base is a ring, so this is a local cut, not a",
            f"  redesign).",
            f"- If rubber feet go on the **case** floor instead, the feet must be ≥ {r['head_b']:.1f} mm tall so the",
            f"  case rests on the feet and not on the screw heads.",
            "- If rubber feet go under the **tenting base**, add foot recesses to its bottom face; the base is",
            "  already hollow, so recesses only need to clear the ring thickness.",
            "",
        ]
    if fails:
        md += ["## FAIL", ""] + [f"- {f}" for f in fails] + [""]
    if warns:
        md += ["## Warnings", ""] + [f"- {w}" for w in warns] + [""]

    text = "\n".join(md)
    print(text)
    if not args.no_write:
        # newline="\n": Windows text mode would otherwise write CRLF, which the repo
        # normalises (see .gitattributes) and which shows up as spurious diffs.
        OUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"\nwrote {OUT.relative_to(REPO)}")
    if fails:
        print(f"\nFAIL — {len(fails)} problem(s); the stack cannot be assembled as configured.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
