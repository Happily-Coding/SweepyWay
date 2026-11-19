/**
 * Config schema for the SweepyWay configurator.
 *
 * One JSON object describes a keyboard. It is deliberately boring: everything the
 * current `ergogen/config.yaml` can meaningfully vary, and nothing else. `normalize()`
 * fills defaults, `validate()` returns a list of human-readable problems.
 */

export const SWITCH_SUPPORT = {
  // plate cutout in mm - the only values with a physical meaning (see docs/KEYBOARD-REFERENCE.md §2)
  v1: { plate: 13.8, label: "Choc V1 only" },
  v2: { plate: 13.95, label: "Choc V2 only" },
  "v1+v2": { plate: 14.0, label: "Choc V1 + V2 (compromise)" },
};

export const KEYCAPS = {
  cfx: { w: 16.5, h: 16.5, label: "CFX 16.5x16.5 (pitch >= 17)" },
  mbk: { w: 17.5, h: 16.5, label: "MBK 17.5x16.5 (pitch >= 17.5)" },
};

const DEFAULT_ROWS = ["row5", "row4", "row3", "row2", "row1"];

// ---------------------------------------------------------------------------------------------
// DATA the generator must reproduce verbatim from `ergogen/config.yaml` (B22).
// Everything here is measured/decided geometry that used to live only in the hand-maintained
// YAML. The generator emits it; `scripts/check_config_drift.mjs` fails when the two disagree.
// Change a number here AND in `ergogen/config.yaml` — the gate is what keeps them honest.
// ---------------------------------------------------------------------------------------------

/**
 * B13 screw points, as FINAL ergogen-space deltas added to `screw_offset_x` / `screw_offset_y`
 * (which are themselves `0.4 kx` / `-0.2 ky`). Stored as absolute deltas, not as a formula:
 * the thumb cluster frame is rotated ~25 deg, so its +1.65 / -3.506 is not comparable to the
 * matrix corners' +2 / -0.75 and cannot be derived from one.
 *   x: pushes the hole 2 mm toward the centre of the field, out of the 14 mm switch cutouts
 *   y: nudges it to the corner of the plate outline (the thumb needed 3.506 mm to clear it)
 */
// MCU / controller zone mirror distance. The mirror axis is `anchor.x + distance/2`
// (anchor = matrix_col4_row1.x = 86), and the KEYS mirror about x = 170. So a true mirror of the
// halves needs distance = 2*(170 - 86) = 168. It was 165 (axis 168.5), which put the right half's
// MCU / controller bay / JST / USB-C block 3.0 mm closer to the seam — see docs/B5-RIGHT-3D.md.
export const MCU_MIRROR_DISTANCE = 168;

/**
 * B20 option D: does the FR4 plate sit ON the printed wall (plate = lid), or inside the cavity?
 *
 * 1 = D (docs/B20-PLATE-ON-WALL.md): `case_border_height` = floor + standoff + PCB + choc band
 *     MINUS `top_plate_thickness` = 11.2 = the plate's underside; the plate (11.2..12.4) overhangs
 *     the wall and is the case's lid. The plate OUTLINES are therefore the case footprint
 *     (`l_plate_on_wall_bay` / `l_plate_on_wall`), not the key cluster.
 * 0 = the pre-D shape: the wall runs to the plate top (12.4) and the plate is a panel inside the
 *     cavity. Kept as an escape hatch, but flipping it alone is NOT enough: `plate_left` /
 *     `plate_right` must also be repointed at `l_coverpart_switch_plate_outline` (key cluster),
 *     because a case-footprint plate on a 12.4 mm wall would hang over the outside.
 *     `scripts/check_assembly.py` fails loudly if the wall height and the plate outlines disagree.
 *
 * Like MCU_MIRROR_DISTANCE this is emitted verbatim into the generated config so the two files
 * cannot disagree; `scripts/check_config_drift.mjs` is the gate on that.
 */
export const PLATE_SITS_ON_WALL = 1;

// B23: how the nice!nano is mounted, as a named preset. Both are parameterised from real parts;
// `generic` is the DEFAULT because a stock 2.54 mm header is far easier to buy than a no-solder
// spring header AND it is the taller (conservative) case, so a build designed around it works with
// either part. Numbers below are millimetres above the PCB's top face.
//
//   generic: measured off KiCad's official PinHeader_1x12_P2.54mm_Vertical 3D model with the short
//            pins through the PCB and the plastic body sitting on it (long-pin band 4.13..9.97,
//            plastic 1.59..4.13). The nano sockets onto the long pins, so its roof is
//            plastic + long pins = 8.38, plus the author's 0.5 clearance = 8.88.
//   spring:  a 5 mm no-solder spring header, ~1/4 above and ~1/4 below the board, plus the nano's
//            own board and its tallest top-side part, a 1.0 mm safety margin and 1.0 mm clearance.
export const MCU_MOUNTINGS = {
  generic: {
    label: "Generic 2.54 header (KiCad official, recommended)",
    plastic: 2.54,
    longPins: 5.84,
    roofClearance: 0.5,
  },
  spring: {
    label: "5 mm no-solder spring header",
    headerTotal: 5,
    abovePcbFraction: 0.25,
    boardThickness: 1.6,
    tallestComponent: 2.0,
    headClearance: 1.0,
    safety: 1.0,
  },
};
export const DEFAULT_MCU_MOUNTING = "generic";

export const SCREW_SHIFTS = {
  l_screw_left_top: [2, -0.75],
  l_screw_left_bottom: [2, -0.75],
  l_screw_right_top: [2, 0],
  l_screw_right_bottom: [2, -1.5],
  l_screw_thumb: [1.65, -3.506],
};

/**
 * The `presets:` block, as data. Key order is the emission order, values are numbers or ergogen
 * expressions. When a preset is the SELECTED one, its spacing keys are replaced by the JSON
 * config's numbers (see `spacingValues()` in generate.mjs), so the JSON stays authoritative for
 * the preset being edited while the other presets keep their documented values.
 *
 * `choc_spacing` is deliberately the MBK-ish baseline (17.5 x 16.5 caps at 18 mm vertical pitch)
 * that the committed config documents; `cfx_spacing` overrides the three keys that make it a
 * 17 x 17 CFX matrix. mbk_spacing exists only when selected (it is not in the committed file).
 */
export const PRESETS = {
  choc_spacing: {
    values: [
      ["kx", 17],
      ["ky", 18],
      ["keycap_x_1u", 17.5],
      ["keycap_y_1u", 16.5],
      ["px", 5],
      ["py", 5],
      ["plate_kx", 14.0],
      ["plate_ky", 14.0],
      ["vertical_diode_shift", 1.5],
      ["horizontal_diode_shift", "-0.5 plate_kx - 0.85"],
      ["diode_rotation", 0],
    ],
  },
  cfx_spacing: {
    $extends: "presets.choc_spacing",
    values: [
      ["kx", 17],
      ["ky", 17],
      ["keycap_x_1u", 16.5],
    ],
  },
};

/** Keys of a preset that the JSON config owns while that preset is selected. */
export const SPACING_KEYS = [
  "kx",
  "ky",
  "keycap_x_1u",
  "keycap_y_1u",
  "plate_kx",
  "plate_ky",
];

export function sweepywayLayout() {
  const cols = [
    { name: "col1", stagger: 0, cells: ["row4", "row3", "row2", "row1"] },
    { name: "col2", stagger: 4.25, cells: DEFAULT_ROWS },
    { name: "col3", stagger: 11.22, cells: DEFAULT_ROWS },
    { name: "col4", stagger: -4.25, cells: ["row4", "row3", "row2", "row1"] },
    { name: "col5", stagger: -2.55, cells: ["row4", "row3", "row2", "row1"] },
    { name: "col6", stagger: -3.4, cells: ["row4", "row3", "row2", "row1"] },
    { name: "col7", stagger: 3.4, cells: ["row4", "row3", "row2"] },
  ];
  return { rows: DEFAULT_ROWS.slice(), columns: cols };
}

export function defaults() {
  const layout = sweepywayLayout();
  return {
    name: "sweepyway",
    switch: { family: "choc", support: "v1+v2", hotswap: true },
    spacing: { kx: 17, ky: 17, keycap: "cfx" },
    layout: {
      rows: layout.rows,
      columns: layout.columns,
      // Absolute x offset (mm) per row, in `rows` order. Non-null switches the layout from
      // column stagger to row stagger; the generator converts these to ergogen's cumulative
      // deltas. Example (0.25u per row on a 17 mm pitch, top row flush): [17, 12.75, 8.5, 4.25, 0]
      rowStagger: null,
      thumb: {
        enabled: true,
        count: 3,
        rotate: -10,
        spread: 17,
        splay: [-15, -5],
        rowNet: null, // null = net of the first row
      },
    },
    // borderHeight is DERIVED from the vertical stack (B17): floor + standoff + PCB + the 2.2 mm
    // choc plate band = 3 + 6 + 1.2 + 2.2 = 12.4. The rim top must coincide with the plate top.
    // The old default of 16 left the wall 3.6 mm above the plate, so CFX caps (3.7 mm) ended up
    // flush with the rim. Overriding this is allowed but `generate.mjs` will then emit a literal
    // instead of the self-consistent formula.
    // standoffLength is the ONE vertical knob (B17): the hotswap socket protrudes ~3.0-3.5 mm
    // below the PCB, so the floor needs that much clearance => 4.5 mm minimum. Everything else
    // (wall height, USB-C opening) is derived from it in generate.mjs.
    // borderHeight === null means "derive it" (the normal case). Set a number only to
    // deliberately override the wall height away from floor+standoff+PCB+2.2.
    // standoffBodyLength (F3b): length of the METAL part hanging below the PCB. 3 = soldered
    // XHHD M2*3+3 (LCSC C192879) placed+soldered by JLCPCB's PCB Assembly service; 6 = press-fit
    // standoff spanning floor->PCB; 0 = no metal, thread in printed plastic. The printed boss
    // height is DERIVED as standoffLength - standoffBodyLength, so the stack never changes.
    case: { bottomThickness: 3, standoffLength: 6, standoffBodyLength: 3, borderHeight: null, wallThickness: 1.2,
      mcuMounting: DEFAULT_MCU_MOUNTING },
    palmRest: { enabled: true, height: 10, curve: 3 },
    tenting: { enabled: true, angle: 6.5, zMin: 3, hollow: 10, includePalmRest: false },
    fab: { plateThickness: 1.2, pcbThickness: 1.2 },
    // B16: which halves to print. Every ergogen outline exists as l_*/r_*, and the right tenting
    // bottom outline used to be empty (it is fixed now), so both sides can be produced.
    printSides: ["l", "r"],
  };
}

export function normalize(input = {}) {
  const d = defaults();
  const cfg = {
    ...d,
    ...input,
    switch: { ...d.switch, ...(input.switch || {}) },
    spacing: { ...d.spacing, ...(input.spacing || {}) },
    layout: { ...d.layout, ...(input.layout || {}) },
    case: { ...d.case, ...(input.case || {}) },
    palmRest: { ...d.palmRest, ...(input.palmRest || {}) },
    tenting: { ...d.tenting, ...(input.tenting || {}) },
    fab: { ...d.fab, ...(input.fab || {}) },
  };
  const sides = input.printSides ?? d.printSides;
  cfg.printSides = (Array.isArray(sides) ? sides : [sides])
    .map((s) => String(s).toLowerCase().replace(/[^lr]/g, ""))
    .filter((s, i, a) => s && a.indexOf(s) === i);
  if (!cfg.printSides.length) cfg.printSides = ["l"];
  cfg.layout.thumb = { ...d.layout.thumb, ...(input.layout?.thumb || {}) };

  // rows + columns: keep order, drop unknown row names, never leave a column empty
  const rows = (input.layout?.rows || d.layout.rows).filter((r, i, a) => a.indexOf(r) === i);
  cfg.layout.rows = rows.length ? rows : d.layout.rows;
  const cols = (input.layout?.columns || d.layout.columns).map((c, i) => ({
    name: c.name || `col${i + 1}`,
    net: c.net || `C${i + 1}`,
    stagger: Number(c.stagger ?? 0),
    spread: c.spread == null ? null : Number(c.spread),
    splay: Number(c.splay ?? 0),
    cells: (c.cells || []).filter((r) => cfg.layout.rows.includes(r)),
  }));
  cfg.layout.columns = cols.length ? cols : d.layout.columns;

  for (const k of ["kx", "ky"]) cfg.spacing[k] = Number(cfg.spacing[k]);
  cfg.fab.plateThickness = Number(cfg.fab.plateThickness);
  cfg.fab.pcbThickness = Number(cfg.fab.pcbThickness);
  cfg.case.standoffLength = Number(cfg.case.standoffLength);
  cfg.case.standoffBodyLength = Number(cfg.case.standoffBodyLength);
  // B23: the mounting preset is a string; reject anything not in the table so a typo cannot
  // silently produce a hood cut for the wrong stack.
  if (!MCU_MOUNTINGS[cfg.case.mcuMounting]) {
    throw new Error(`unknown case.mcuMounting "${cfg.case.mcuMounting}"; expected one of ` +
      Object.keys(MCU_MOUNTINGS).join(", "));
  }
  cfg.palmRest.height = Number(cfg.palmRest.height);
  cfg.palmRest.curve = Number(cfg.palmRest.curve);
  cfg.tenting.angle = Number(cfg.tenting.angle);
  cfg.tenting.zMin = Number(cfg.tenting.zMin);
  cfg.tenting.hollow = Number(cfg.tenting.hollow);
  cfg.name = String(cfg.name || "keyboard").replace(/[^a-zA-Z0-9_.-]+/g, "-");
  return cfg;
}

export function plateCutout(cfg) {
  return SWITCH_SUPPORT[cfg.switch.support]?.plate ?? 14.0;
}

/** The values a selected preset takes from the JSON config (see SPACING_KEYS). */
export function spacingValues(cfg) {
  const cap = KEYCAPS[cfg.spacing.keycap] ?? KEYCAPS.cfx;
  const plate = plateCutout(cfg);
  return {
    kx: cfg.spacing.kx,
    ky: cfg.spacing.ky,
    keycap_x_1u: cap.w,
    keycap_y_1u: cap.h,
    plate_kx: plate,
    plate_ky: plate,
  };
}

/** Named points the generator will produce, so outlines can be rewritten to match. */
export function pointNames(cfg) {
  const rows = cfg.layout.rows;
  const cols = cfg.layout.columns;
  const firstCol = cols[0];
  const lastCellOf = (col) => col.cells[col.cells.length - 1] || rows[rows.length - 1];
  const anchorCol = cols[Math.max(0, cols.length - 2)];
  const midCol = cols[Math.floor((cols.length - 1) / 2)];
  const thumbCount = cfg.layout.thumb.enabled ? Math.max(0, Math.min(3, cfg.layout.thumb.count)) : 0;
  return {
    // references used by the outlines / anchors in the canonical config.yaml
    col1Bottom: `${firstCol.name}_${lastCellOf(firstCol)}`,
    colN2Bottom: `${anchorCol.name}_${lastCellOf(anchorCol)}`,
    midColBottom: `${midCol.name}_${rows[rows.length - 1]}`,
    thumbFirst: thumbCount ? `col1_thumb_row_1` : null,
    thumbLast: thumbCount ? `col${thumbCount}_thumb_row_1` : null,
    thumbCount,
    thumbRowNet: cfg.layout.thumb.rowNet || netOfRow(cfg, rows[0]),
  };
}

function netOfRow(cfg, rowName) {
  const idx = cfg.layout.rows.indexOf(rowName);
  return `R${cfg.layout.rows.length - idx}`;
}

/** Matrix cells as (colNet, rowNet) pairs + thumb keys, for duplicate detection. */
export function matrixPairs(cfg) {
  const rows = cfg.layout.rows;
  const rowNet = (r) => `R${rows.length - rows.indexOf(r)}`;
  const pairs = [];
  for (const col of cfg.layout.columns) {
    for (const cell of col.cells) {
      pairs.push({ key: `${col.name}_${cell}`, col: col.net, row: rowNet(cell) });
    }
  }
  const thumbCount = cfg.layout.thumb.enabled ? Math.max(0, Math.min(3, cfg.layout.thumb.count)) : 0;
  // NB: slice(-0) === slice(0) returns everything, so guard the empty case
  const thumbNets = thumbCount > 0 ? cfg.layout.columns.slice(-thumbCount).map((c) => c.net) : [];
  const thumbRow = cfg.layout.thumb.rowNet || rowNet(rows[0]);
  thumbNets.forEach((net, i) => pairs.push({ key: `thumb${i + 1}`, col: net, row: thumbRow }));
  return pairs;
}

export function validate(cfg) {
  const errs = [];
  const warns = [];

  // 1. keycap must fit the pitch
  const cap = KEYCAPS[cfg.spacing.keycap] ?? KEYCAPS.cfx;
  if (cfg.spacing.kx < cap.w + 0.4) {
    errs.push(
      `keycap ${cfg.spacing.keycap} is ${cap.w} mm wide but kx is ${cfg.spacing.kx} mm ` +
        `(need >= ${(cap.w + 0.4).toFixed(1)}) - keycaps would collide`,
    );
  }
  if (cfg.spacing.ky < cap.h + 0.4) {
    errs.push(
      `keycap is ${cap.h} mm tall but ky is ${cfg.spacing.ky} mm ` +
        `(need >= ${(cap.h + 0.4).toFixed(1)})`,
    );
  }

  // 2. plate cutout vs pitch
  const cut = plateCutout(cfg);
  if (cut >= cfg.spacing.kx) errs.push(`plate cutout ${cut} mm does not fit a ${cfg.spacing.kx} mm pitch`);

  // 3. matrix must be well formed
  const pairs = matrixPairs(cfg);
  if (!pairs.length) errs.push("layout has no keys");
  const empty = cfg.layout.columns.filter((c) => !c.cells.length).map((c) => c.name);
  if (empty.length) errs.push(`column(s) without any row: ${empty.join(", ")}`);
  const dupCells = {};
  for (const p of pairs) {
    const id = `${p.col}|${p.row}`;
    dupCells[id] = (dupCells[id] || 0) + 1;
  }
  const collisions = Object.entries(dupCells).filter(([, n]) => n > 1);
  for (const [id, n] of collisions) {
    errs.push(`two keys share the matrix position ${id.replace("|", " x ")} (x${n}) - the matrix cannot distinguish them`);
  }

  // 4. pins
  const need = cfg.layout.columns.length + cfg.layout.rows.length;
  if (need > COLUMN_PIN_POOL.length + ROW_PIN_POOL.length) {
    errs.push(`${need} nets need MCU pins but only ${COLUMN_PIN_POOL.length + ROW_PIN_POOL.length} are available`);
  }

  // 5. geometry sanity
  if (cfg.tenting.enabled && (cfg.tenting.angle <= 0 || cfg.tenting.angle > 45)) {
    errs.push(`tenting angle ${cfg.tenting.angle} deg is out of range (0-45)`);
  }
  if (cfg.palmRest.enabled && cfg.palmRest.height <= 0) errs.push("palm rest height must be > 0");
  if (!(cfg.case.standoffLength >= 4.5 && cfg.case.standoffLength <= 15)) {
    errs.push(
      `standoff ${cfg.case.standoffLength} mm is out of range: 4.5-15 mm ` +
        `(below 4.5 the hotswap sockets hit the case floor)`,
    );
  }
  if (!(cfg.case.standoffBodyLength >= 0 && cfg.case.standoffBodyLength <= cfg.case.standoffLength)) {
    errs.push(
      `metal part ${cfg.case.standoffBodyLength} mm must be between 0 and the standoff ` +
      `(${cfg.case.standoffLength} mm) — it hangs below the PCB inside that gap`,
    );
  }
  if (cfg.fab.plateThickness > 1.5 && cfg.switch.family === "choc") {
    warns.push(
      `plate thickness ${cfg.fab.plateThickness} mm is above the choc ceiling (1.5 mm FR4); ` +
        `switches may not seat - 1.2 mm is the spec value`,
    );
  }
  if (cfg.fab.pcbThickness < 1.0 && cfg.switch.hotswap) {
    warns.push(
      `PCB at ${cfg.fab.pcbThickness} mm is thinner than any choc-hotswap build found; ` +
        `socket grip and board flex are untested (see docs/DECISIONS.md)`,
    );
  }
  if (!cfg.layout.thumb.enabled) warns.push("thumb cluster disabled - is the keyboard still usable?");

  return { errors: errs, warnings: warns };
}

// Chosen so that a 7x5 matrix plus 4 spare keys fits a nice!nano with nice!view reserved.
export const ROW_PIN_POOL = ["P3", "P4", "P5", "P6", "P7", "P8", "P9"];
export const COLUMN_PIN_POOL = ["P21", "P20", "P19", "P18", "P15", "P14", "P16", "P10"];
