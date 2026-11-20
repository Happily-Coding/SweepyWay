#!/usr/bin/env python3
"""Set the board thickness on the PLATE boards that ergogen emits.

ergogen stamps every kicad_pcb it writes with a `(thickness 1.6)` default. For the main PCB that is
correct, but the switch plate must be `top_plate_thickness` (1.2 mm): choc switches do not seat in
anything thicker than 1.5 mm, and the case's `case_border_height` is derived from that 1.2 mm, so a
1.6 mm plate would also sit 0.4 mm proud of the wall.

The thickness in the file is what any fab tool reads by default, and it is one more thing to remember
to type into a JLCPCB order form - so set it here, once, and let `check_assembly` assert it.

Usage:
  fix_plate_thickness.py                       # ergogen/output/pcbs/plate_*.kicad_pcb, from config
  fix_plate_thickness.py --dir some/dir --thickness 1.2
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def unit_from_config(config: Path, key: str) -> float | None:
    """Read a plain numeric unit out of ergogen/config.yaml (no yaml dep: match the literal line)."""
    m = re.search(rf"^  {re.escape(key)}:\s*([\d.]+)", config.read_text(encoding="utf-8"),
                  flags=re.M)
    try:
        return float(m.group(1)) if m else None
    except (TypeError, ValueError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="ergogen/output/pcbs")
    ap.add_argument("--config", default="ergogen/config.yaml")
    ap.add_argument("--thickness", type=float,
                    help="defaults to units.top_plate_thickness from the config")
    ap.add_argument("--glob", default="plate_*.kicad_pcb")
    args = ap.parse_args()

    want = args.thickness
    if want is None:
        want = unit_from_config(REPO / args.config, "top_plate_thickness")
    if want is None:
        print("fix_plate_thickness: no --thickness and no units.top_plate_thickness in the config",
              file=sys.stderr)
        return 2

    files = sorted(Path(args.dir).glob(args.glob))
    if not files:
        print(f"fix_plate_thickness: no {args.glob} in {args.dir}", file=sys.stderr)
        return 2

    changed = 0
    print(f"fix_plate_thickness: plate thickness -> {want} mm")
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        new, n = re.subn(r"\(thickness [\d.]+\)", f"(thickness {want})", text, count=1)
        if n == 0:
            print(f"  FAIL {f.name}: no (thickness ...) line", file=sys.stderr)
            return 1
        delta = "unchanged" if new == text else "rewritten"
        if new != text:
            f.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
        print(f"  ok   {f.name:34s} {want} mm ({delta})")

    print(f"\nfix_plate_thickness: {changed} file(s) rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
