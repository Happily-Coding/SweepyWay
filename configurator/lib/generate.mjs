/**
 * JSON config -> a complete Ergogen `config.yaml`.
 *
 * Strategy: the repository's canonical `ergogen/config.yaml` is the source of truth for
 * everything that is *not* parameterised here (outlines, cases, footprint wiring). We
 * splice in freshly generated `presets:`, `points:` and the handful of scalars that the
 * configurator owns. That keeps the two files from drifting apart.
 *
 * If the canonical file stops parsing the way this module expects, `generate()` throws
 * instead of silently emitting something broken - every anchor is asserted.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { plateCutout, KEYCAPS, ROW_PIN_POOL, COLUMN_PIN_POOL, matrixPairs, PRESETS, SCREW_SHIFTS, SPACING_KEYS, spacingValues } from "./schema.mjs";

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
export const CANONICAL_CONFIG = resolve(REPO, "ergogen/config.yaml");

const yamlQuote = (s) => `"${String(s).replace(/"/g, '\\"')}"`;
const num = (n) => (Number.isInteger(n) ? String(n) : String(Number(n.toFixed(4))));
/** `2` -> "+ 2", `-3.506` -> "- 3.506": the way the committed config spells its deltas. */
const signed = (n) => `${n < 0 ? "-" : "+"} ${num(Math.abs(n))}`;

function rowsToNets(cfg) {
  // canonical naming: the first row in the list gets the highest row net (R5 for 5 rows)
  const out = {};
  cfg.layout.rows.forEach((r, i) => {
    out[r] = `R${cfg.layout.rows.length - i}`;
  });
  return out;
}

function buildPresets(cfg) {
  const presetName = cfg.spacing.keycap === "mbk" ? "mbk_spacing" : "cfx_spacing";
  const selected = spacingValues(cfg);
  // Emit every preset declared in the data table; the SELECTED one takes its spacing numbers
  // from the JSON config, the others keep their documented values. A selected preset that the
  // table does not know (mbk_spacing) is appended as a thin extension of the choc baseline.
  const blocks = Object.entries(PRESETS).map(([name, preset]) => {
    const values = preset.values.map(([key, value]) =>
      name === presetName && SPACING_KEYS.includes(key) ? [key, selected[key]] : [key, value],
    );
    return { name, $extends: preset.$extends ?? null, values };
  });
  if (!blocks.some((b) => b.name === presetName)) {
    blocks.push({
      name: presetName,
      $extends: "presets.choc_spacing",
      values: SPACING_KEYS.map((key) => [key, selected[key]]),
    });
  }

  const out = ["presets:"];
  for (const block of blocks) {
    out.push(`  ${block.name}:`);
    if (block.name === "choc_spacing") {
      out.push("    # Standard Choc spacing, compatible with MBK keycaps which are 16.5 x 17.5");
    }
    if (block.$extends) out.push(`    $extends: ${block.$extends}`);
    for (const [key, value] of block.values) out.push(`    ${key}: ${typeof value === "number" ? num(value) : value}`);
    out.push("");
  }
  out.push("units:");
  out.push(`  $extends: presets.${presetName}`);
  out.push("");
  return { text: out.join("\n"), presetName };
}

/**
 * Named references into the generated layout. Ergogen lists rows bottom-first, so a
 * column's FIRST cell is its bottom key and the LAST row of the list is the top row.
 */
function layoutRefs(cfg) {
  const cols = cfg.layout.columns;
  const rows = cfg.layout.rows;
  const bottomCellOf = (col) => col.cells[0] || rows[0];
  return {
    cols,
    rows,
    bottomCellOf,
    topRow: rows[rows.length - 1],
    anchorCol: cols[Math.max(0, cols.length - 2)],
    firstCol: cols[0],
    secondLastCol: cols[Math.max(0, cols.length - 2)],
    midCol: cols[Math.floor((cols.length - 1) / 2)],
  };
}

function buildPoints(cfg) {
  const nets = rowsToNets(cfg);
  const cols = cfg.layout.columns;
  const rows = cfg.layout.rows;
  const rowStagger = Array.isArray(cfg.layout.rowStagger) && cfg.layout.rowStagger.length
    ? cfg.layout.rowStagger
    : null;

  // Where the points really are: used by rewritePointRefs() to retarget the hand-authored
  // outline polygons, and to refuse to point them at a key that does not exist.
  const names = new Set();
  for (const col of cols) {
    for (const cell of col.cells) names.add(`matrix_${col.name}_${cell}`);
  }

  const lines = [];
  lines.push("points:");
  lines.push("  key:");
  lines.push("    padding: ky");
  lines.push("    spread: kx");
  lines.push("    width: keycap_x_1u");
  lines.push("    height: keycap_x_1u");
  lines.push("    mirror:");
  lines.push('      tags: ["key", "rightkey"]');
  lines.push("  zones:");
  lines.push("    matrix:");
  lines.push("      anchor:");
  lines.push("        shift: [35, -150]");
  lines.push('      key.tags: ["key", "leftkey"]');
  lines.push("      columns:");
  for (const col of cols) {
    lines.push(`        ${col.name}:`);
    lines.push(`          key.column_net: ${col.net}`);
    // emitted unconditionally so the text matches the committed file (which spells out 0)
    lines.push(`          key.stagger: ${num(col.stagger)}`);
    if (col.spread != null) lines.push(`          key.spread: ${num(col.spread)}`);
    if (col.splay) lines.push(`          key.splay: ${num(col.splay)}`);
    const missing = rows.filter((r) => !col.cells.includes(r));
    if (missing.length) {
      lines.push("          rows:");
      for (const r of missing) {
        lines.push(`            ${r}:`);
        lines.push("              skip: true");
      }
    }
  }
  lines.push("      rows:");
  for (const r of rows) {
    lines.push(`        ${r}:`);
    lines.push(`          row_net: ${nets[r]}`);
    if (rowStagger) {
      // rowStagger is authored as ABSOLUTE x offsets per row; ergogen's `shift` applies
      // against a running anchor, so convert to deltas here.
      const idx = rows.indexOf(r);
      const abs = Number(rowStagger[idx] ?? 0);
      const prev = idx > 0 ? Number(rowStagger[idx - 1] ?? 0) : 0;
      const delta = abs - prev;
      if (delta) lines.push(`          shift: [${num(delta)}, 0]`);
    }
  }
  lines.push("      mirror:");
  lines.push("        distance: 340");

  // ---- thumb cluster
  const thumb = cfg.layout.thumb;
  const thumbCount = thumb.enabled ? Math.max(0, Math.min(3, thumb.count)) : 0;
  const R = layoutRefs(cfg);
  const { bottomCellOf, topRow, anchorCol } = R;
  const anchorCell = bottomCellOf(anchorCol);
  const anchorRef = `matrix_${anchorCol.name}_${anchorCell}`;
  const thumbNets = cols.slice(-thumbCount).map((c) => c.net);
  const thumbRowNet = thumb.rowNet || nets[rows[0]];

  if (thumbCount) {
    for (let i = 0; i < thumbCount; i += 1) names.add(`thumbfan_col${i + 1}_thumb_row_1`);
    lines.push("    thumbfan:");
    lines.push('      key.tags: ["key", "leftkey"]');
    lines.push("      anchor:");
    lines.push(`        ref: ${anchorRef}`);
    lines.push(`        shift: [-0.66 kx, -1 ky]`);
    lines.push(`        rotate: ${num(thumb.rotate)}`);
    lines.push("      columns:");
    for (let i = 0; i < thumbCount; i += 1) {
      lines.push(`        col${i + 1}:`);
      lines.push("          key:");
      lines.push(`            spread: ${num(thumb.spread)}`);
      const splay = Array.isArray(thumb.splay) ? thumb.splay[i - 1] : null;
      if (i > 0 && splay != null) {
        lines.push(`            splay: ${num(splay)}`);
        lines.push("            origin: [-0.5 kx, -0.5 ky]");
      }
      lines.push(`            column_net: ${thumbNets[i]}`);
    }
    lines.push("      rows:");
    lines.push("        thumb_row_1:");
    lines.push(`          row_net: ${thumbRowNet}`);
    lines.push("      mirror:");
    lines.push(`        ref: ${anchorRef}`);
    lines.push("        distance: 100");
  }

  // ---- controller + helper areas
  const midCol = R.midCol;
  const botRow = rows[rows.length - 1];
  const midRef = `matrix_${midCol.name}_${botRow}`;
  lines.push(`    controller_center: #The point exactly in the middle of the controller, the controller is drawn arround it`);
  lines.push("      anchor:");
  lines.push(`        ref: ${midRef}`);
  lines.push("        shift: [-0.25*kx, 0.5 ky + mcu_y/2 + controller_center_y_shift]");
  lines.push("      key:");
  lines.push("        name: mcu");
  lines.push("        width: mcu_y");
  lines.push("        height: mcu_x");
  lines.push('        tags: ["controller_center", "left_controller_center"]');
  lines.push('        mirror.tags: ["controller_center", "right_controller_center"]');
  lines.push("      mirror:");
  lines.push(`        ref: ${midRef}`);
  lines.push("        distance: 165");
  lines.push("");
  lines.push("    l_jsph_area_center:");
  lines.push("      anchor:");
  lines.push("        ref: mcu");
  lines.push("        shift: [mcu_x/2 +19, -14]");
  lines.push("        rotate: 270");
  lines.push("      key:");
  lines.push("        tags:");
  lines.push("          ['l_jsph_area_center']");
  lines.push("");
  lines.push("    r_jsph_area_center:");
  lines.push("      anchor:");
  lines.push("        ref: mirror_mcu");
  lines.push("        shift: [mcu_x/2 +19, -14]");
  lines.push("        rotate: 270");
  lines.push("      key:");
  lines.push("        tags:");
  lines.push("          ['r_jsph_area_center']");
  lines.push("");
  lines.push("    l_controller_area_center:");
  lines.push("      anchor:");
  lines.push("        ref: mcu");
  lines.push("        shift: [l_controller_area_x_shift, l_controller_area_y_shift]");
  lines.push("      key:");
  lines.push("        tags: ['l_controller_area_center']");
  lines.push("");
  lines.push("    r_controller_area_center:");
  lines.push("      anchor:");
  lines.push("        ref: mirror_mcu");
  lines.push("        shift: [r_controller_area_x_shift, r_controller_area_y_shift]");
  lines.push("      key:");
  lines.push("        tags: ['r_controller_area_center']");

  // ---- screw points: corners of the key field + the thumb cluster
  const { firstCol, secondLastCol } = R;
  const screws = [
    ["l_screw_left_top", `matrix_${firstCol.name}_${topRow}`],
    ["l_screw_left_bottom", `matrix_${firstCol.name}_${bottomCellOf(firstCol)}`],
    ["l_screw_right_top", `matrix_${secondLastCol.name}_${topRow}`],
    ["l_screw_right_bottom", `matrix_${secondLastCol.name}_${bottomCellOf(secondLastCol)}`],
  ];
  if (thumbCount) {
    const mid = Math.max(0, Math.ceil(thumbCount / 2));
    screws.push(["l_screw_thumb", `thumbfan_col${mid}_thumb_row_1`]);
  }
  lines.push("");
  lines.push("");
  lines.push("    # Screw points. The right half gets EXPLICIT r_ twins anchored to the mirrored key");
  lines.push("    # points: ergogen appends the global mirror tags (rightkey) to any mirrored point, so a");
  lines.push("    # mirrored screw would be caught by the right half's key/diode filters.");
  lines.push("    # The per-point deltas are the B13 fix; they live in schema.mjs SCREW_SHIFTS as FINAL");
  lines.push("    # ergogen-space offsets (the thumb frame is rotated, so it is not derivable from the rest).");
  for (const [name, ref] of screws) {
    const delta = SCREW_SHIFTS[name];
    if (!delta) throw new Error(`schema.mjs SCREW_SHIFTS: no B13 offset for ${name}`);
    const shift = `screw_offset_x ${signed(delta[0])}, screw_offset_y ${signed(delta[1])}`;
    const rRef = ref.startsWith("mirror_") ? ref : `mirror_${ref}`;
    const rName = `r_${name.replace(/^l_/, "")}`;
    for (const [pointName, anchorRef, tag] of [
      [name, ref, "left_screw"],
      [rName, rRef, "right_screw"],
    ]) {
      lines.push(`    ${pointName}:`);
      lines.push("      anchor:");
      lines.push(`        - ref: ${anchorRef}`);
      lines.push(`          shift: [${shift}]`);
      lines.push("      key.tags:");
      lines.push(`        - ${tag}`);
      names.add(pointName);
    }
  }
  return { text: lines.join("\n") + "\n", names };
}

function buildPinMap(cfg) {
  const nets = rowsToNets(cfg);
  const rowPins = cfg.layout.rows.map((r) => [ROW_PIN_POOL[cfg.layout.rows.indexOf(r)], nets[r]]);
  const colPins = cfg.layout.columns.map((c, i) => [COLUMN_PIN_POOL[i], c.net]);
  const lines = [];
  lines.push("          # Pins (generated by the configurator)");
  lines.push("          # Right Side");
  lines.push("          P0: \"DPD\" # Display Data");
  lines.push("          P1: \"DPC\" # Display Clock");
  lines.push("          P2: \"DPE\" # Display CS (nice!view)");
  for (const [pin, net] of rowPins) {
    if (!pin) throw new Error(`not enough row pins for ${cfg.layout.rows.length} rows`);
    lines.push(`          ${pin}: ${yamlQuote(net)} # Row`);
  }
  lines.push("          # Left Side");
  lines.push("          # RAW / GND / RST / VCC are fixed");
  for (const [pin, net] of colPins) {
    if (!pin) throw new Error(`not enough column pins for ${cfg.layout.columns.length} columns`);
    lines.push(`          ${pin}: ${yamlQuote(net)} # Column`);
  }
  return lines.join("\n");
}

function replaceSpan(text, startMarker, endMarker, replacement, label, keepEnd = false) {
  const start = text.indexOf(startMarker);
  if (start === -1) throw new Error(`canonical config: start marker not found for ${label} (${startMarker})`);
  const end = text.indexOf(endMarker, start);
  if (end === -1) throw new Error(`canonical config: end marker not found for ${label} (${endMarker})`);
  const rest = keepEnd ? end : end + endMarker.length;
  return text.slice(0, start) + replacement + text.slice(rest);
}

function rewritePinBlocks(text, pinMap) {
  // Replace the pin map inside every `promicro:` footprint params block.
  // The block runs from "# Pin Assignments" to the dedented `adjust:` line.
  let out = text;
  let count = 0;
  let from = 0;
  for (;;) {
    if (count > 8) throw new Error("rewritePinBlocks: too many pin blocks, aborting");
    const start = out.indexOf("# Pin Assignments", from);
    if (start === -1) break;
    const dedent = out.indexOf("\n        adjust:", start);
    if (dedent === -1) throw new Error("canonical config: could not find the end of a promicro params block");
    // keep the newline that ends the block
    out = out.slice(0, start) + pinMap + out.slice(dedent);
    from = start + pinMap.length;
    count += 1;
  }
  if (count !== 2) throw new Error(`expected 2 promicro pin blocks, rewrote ${count}`);
  return out;
}

/**
 * Rewrite the canonical outlines' hardcoded point references so they follow a different layout.
 * Applied ONLY to the `outlines:` section - the generated `points:` section already uses the new
 * names and must not be touched.
 *
 * A reference that still exists in the generated layout is left EXACTLY as written: the polygons
 * are hand-tuned against specific keys, so "col2_row4" is not a synonym for "col1_row4" (that
 * mis-mapping silently reshaped the thumb/hand-rest polygons - part of B22). When a name really
 * has to move (renamed columns/rows) it is retargeted by position and must resolve to an existing
 * point, otherwise this throws instead of quietly snapping the outline to the wrong key.
 */
function retargetPointRef(name, cfg, names) {
  if (names.has(name)) return name;
  const m = /^matrix_(.+)_row(\d+)$/.exec(name);
  if (!m) throw new Error(`canonical outline references "${name}", which this layout does not define`);
  const [, colPart, rowDigits] = m;
  const cols = cfg.layout.columns;
  const rows = cfg.layout.rows;
  const positional = /^col(\d+)$/.exec(colPart);
  const col = cols.find((c) => c.name === colPart) || (positional ? cols[Number(positional[1]) - 1] : null);
  // rowN counts from the TOP of the field (row1 = top), while `rows` is listed bottom-first
  const rowName = rows.includes(`row${rowDigits}`) ? `row${rowDigits}` : rows[rows.length - Number(rowDigits)];
  const target = col && rowName ? `matrix_${col.name}_${rowName}` : null;
  if (!target || !names.has(target)) {
    throw new Error(
      `canonical outline references "${name}"; this layout has no ${target ?? "equivalent point"}. ` +
        "Retarget the outline for this preset before generating from it (see docs/CONFIGURATOR-DRIFT.md B22).",
    );
  }
  return target;
}

function rewritePointRefs(text, cfg, names) {
  const cut = text.indexOf("\noutlines:\n");
  if (cut === -1) throw new Error("canonical config: outlines section not found");
  const head = text.slice(0, cut);
  let tail = text.slice(cut);

  // the hand-rest polygons use the thumb keys as their front edge; drop the vertices whose
  // thumb key this layout does not have (all of them when the thumb cluster is disabled)
  tail = tail.replace(
    / *- ref: (mirror_)?thumbfan_col(\d+)_thumb_row_1\n(?: +shift: [^\n]*\n)?/g,
    (match, _mirror, colNum) => (names.has(`thumbfan_col${colNum}_thumb_row_1`) ? match : ""),
  );

  tail = tail.replace(/(mirror_)?(matrix_[A-Za-z0-9_]+_row\d+)/g, (_match, mirror, name) =>
    `${mirror ?? ""}${retargetPointRef(name, cfg, names)}`,
  );
  return head + tail;
}

export function generate(cfg) {
  let text = readFileSync(CANONICAL_CONFIG, "utf8");

  // 1. presets + units
  const { text: presetsText, presetName } = buildPresets(cfg);
  text = replaceSpan(text, "presets:\n", "units:\n  $extends: presets.cfx_spacing\n", presetsText, "presets");
  if (!text.includes(`presets.${presetName}`)) {
    text = text.replace("units:\n  $extends: presets.choc_spacing", `units:\n  $extends: presets.${presetName}`);
  }

  // 2. points
  const points = buildPoints(cfg);
  text = replaceSpan(text, "points:\n", "outlines:\n", points.text, "points", true);

  // 3. scalars owned by the configurator
  const cap = KEYCAPS[cfg.spacing.keycap] ?? KEYCAPS.cfx;
  const setScalar = (re, value, label) => {
    if (!re.test(text)) throw new Error(`canonical config: could not set ${label}`);
    text = text.replace(re, value);
  };
  setScalar(/  top_plate_thickness: [\d.]+[^\n]*/, `  top_plate_thickness: ${num(cfg.fab.plateThickness)}`, "top_plate_thickness");
  setScalar(/  case_bottom_thickness: [\d.]+/, `  case_bottom_thickness: ${num(cfg.case.bottomThickness)}`, "case_bottom_thickness");
  setScalar(/  pcb_thickness: [\d.]+[^\n]*/, `  pcb_thickness: ${num(cfg.fab.pcbThickness)}`, "pcb_thickness");
  // B17: keep the derived formula unless the user deliberately overrode the rim height, so the
  // generated config can never silently disagree with itself again.
  setScalar(/  standoff_length: [\d.]+[^\n]*/, `  standoff_length: ${num(cfg.case.standoffLength)}`, "standoff_length");
  setScalar(/  standoff_body_length: [\d.]+[^\n]*/,
    `  standoff_body_length: ${num(cfg.case.standoffBodyLength)}`, "standoff_body_length");
  {
    const PLATE_BAND = 2.2;
    const derived =
      Number(cfg.case.bottomThickness) + Number(cfg.case.standoffLength) + Number(cfg.fab.pcbThickness) + PLATE_BAND;
    const override = cfg.case.borderHeight == null || cfg.case.borderHeight === "" ? null : cfg.case.borderHeight;
    const rim =
      override == null || Math.abs(Number(override) - derived) < 0.05
        ? "case_bottom_thickness + standoff_length + pcb_thickness + plate_top_above_pcb_top"
        : num(override);
    setScalar(/  case_border_height: [^\n]*/, `  case_border_height: ${rim}`, "case_border_height");
  }
  setScalar(/  case_wall_thickness: [\d.]+/, `  case_wall_thickness: ${num(cfg.case.wallThickness)}`, "case_wall_thickness");
  setScalar(/          keycap_width: [\d.]+/g, `          keycap_width: ${num(cap.w)}`, "keycap_width");
  setScalar(/          keycap_height: [\d.]+/g, `          keycap_height: ${num(cap.h)}`, "keycap_height");

  const hotswapV2 = cfg.switch.support !== "v1";
  text = text.replace(/choc_v2_support: (true|false)/g, `choc_v2_support: ${hotswapV2}`);
  // NB: `mcu_3dmodel_xyz_offset` is NOT unified here any more (B22). The committed config has
  // 2.5 on the left and 5 on the right; rewriting it made every configurator run change the
  // left half's 3D preview without anybody asking. That is a hand-value in config.yaml, so it
  // is the config's business until someone edits both files on purpose.

  // 4. pin maps (both halves)
  text = rewritePinBlocks(text, buildPinMap(cfg));

  // 5. outline references follow the layout (identity for the default layout)
  text = rewritePointRefs(text, cfg, points.names);

  // 6. B4 guard: BOTH halves must carry an NPTH mounting hole on their screw points. The canonical
  // file already owns these footprints (`screws:` on each side); the old code injected a second,
  // coincident `r_screws:` block beside the existing one. Assert instead of adding.
  const mountingHoles = [...text.matchAll(/what: ceoloide\/mounting_hole_npth\n\s+where: (\w+)/g)].map(
    (m) => m[1],
  );
  for (const side of ["left_screw", "right_screw"]) {
    if (!mountingHoles.includes(side)) {
      throw new Error(
        `canonical config: no ceoloide/mounting_hole_npth footprint on ${side} - ` +
          "B4 requires a mounting hole on both halves (see docs/CONFIGURATOR-DRIFT.md)",
      );
    }
  }

  const header = `# Generated by the SweepyWay configurator - DO NOT EDIT BY HAND.
# Source config: configurator/configs/${cfg.name}.json
# Regenerate: node configurator/lib/generate.mjs configurator/configs/${cfg.name}.json
# Keyboard: ${cfg.name}, ${cfg.layout.columns.length} cols x ${cfg.layout.rows.length} rows,
# ${matrixPairs(cfg).length} keys, ${cfg.spacing.keycap} keycaps at ${cfg.spacing.kx}x${cfg.spacing.ky} mm
`;
  return header + text;
}

// ---------------------------------------------------------------- CLI
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { readFileSync: rf, writeFileSync, mkdirSync } = await import("node:fs");
  const { normalize, validate } = await import("./schema.mjs");
  const src = process.argv[2];
  if (!src) {
    console.error("usage: node configurator/lib/generate.mjs <config.json> [--out config.yaml]");
    process.exit(2);
  }
  const cfg = normalize(JSON.parse(rf(resolve(src), "utf8")));
  const { errors, warnings } = validate(cfg);
  for (const w of warnings) console.error(`warning: ${w}`);
  if (errors.length) {
    for (const e of errors) console.error(`error: ${e}`);
    process.exit(1);
  }
  const yaml = generate(cfg);
  const outIdx = process.argv.indexOf("--out");
  if (outIdx > 0) {
    const out = resolve(process.argv[outIdx + 1]);
    mkdirSync(dirname(out), { recursive: true });
    writeFileSync(out, yaml, "utf8");
    console.log(`wrote ${out}`);
  } else {
    process.stdout.write(yaml);
  }
}
