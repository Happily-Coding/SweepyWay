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
import { plateCutout, KEYCAPS, ROW_PIN_POOL, COLUMN_PIN_POOL, matrixPairs } from "./schema.mjs";

const REPO = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
export const CANONICAL_CONFIG = resolve(REPO, "ergogen/config.yaml");

const yamlQuote = (s) => `"${String(s).replace(/"/g, '\\"')}"`;
const num = (n) => (Number.isInteger(n) ? String(n) : String(Number(n.toFixed(4))));

function rowsToNets(cfg) {
  // canonical naming: the first row in the list gets the highest row net (R5 for 5 rows)
  const out = {};
  cfg.layout.rows.forEach((r, i) => {
    out[r] = `R${cfg.layout.rows.length - i}`;
  });
  return out;
}

function buildPresets(cfg) {
  const cap = KEYCAPS[cfg.spacing.keycap] ?? KEYCAPS.cfx;
  const plate = plateCutout(cfg);
  const presetName = cfg.spacing.keycap === "mbk" ? "mbk_spacing" : "cfx_spacing";
  const presets = `presets:
  choc_spacing:
    # Standard Choc spacing. Keycaps are 16.5 x 16.5 (CFX) or 17.5 x 16.5 (MBK):
    # the pitch must always be a bit larger than the cap or they collide.
    kx: ${num(cfg.spacing.kx)}
    ky: ${num(cfg.spacing.ky)}
    keycap_x_1u: ${num(cap.w)}
    keycap_y_1u: ${num(cap.h)}

    px: 5
    py: 5
    plate_kx: ${num(plate)} # switch cutout: 13.8 = choc v1, 13.95 = v2, 14.0 = both
    plate_ky: ${num(plate)}
    vertical_diode_shift: 1.5
    horizontal_diode_shift: -0.5 plate_kx - 0.85
    diode_rotation: 0

  cfx_spacing:
    $extends: presets.choc_spacing
  mbk_spacing:
    $extends: presets.choc_spacing

units:
  $extends: presets.${presetName}
`;
  return { text: presets, presetName };
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
    if (col.stagger) lines.push(`          key.stagger: ${num(col.stagger)}`);
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
  for (const [name, ref] of screws) {
    const rRef = ref.startsWith("mirror_") ? ref : `mirror_${ref}`;
    lines.push(`    ${name}:`);
    lines.push("      anchor:");
    lines.push(`        - ref: ${ref}`);
    lines.push("          shift: [screw_offset_x , screw_offset_y]");
    lines.push("      key.tags:");
    lines.push("        - left_screw");
    lines.push(`    r_${name.replace(/^l_/, "")}:`);
    lines.push("      anchor:");
    lines.push(`        - ref: ${rRef}`);
    lines.push("          shift: [screw_offset_x , screw_offset_y]");
    lines.push("      key.tags:");
    lines.push("        - right_screw");
  }
  return lines.join("\n") + "\n";
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
 * Rewrite the canonical outlines' hardcoded point references so they follow a different
 * layout. Applied ONLY to the `outlines:` section - the generated `points:` section
 * already uses the new names and must not be touched.
 */
function rewritePointRefs(text, cfg) {
  const R = layoutRefs(cfg);
  const cut = text.indexOf("\noutlines:\n");
  if (cut === -1) throw new Error("canonical config: outlines section not found");
  let head = text.slice(0, cut);
  let tail = text.slice(cut);

  // old canonical references -> names in the generated layout
  const map = {
    "matrix_col1_row4": `matrix_${R.firstCol.name}_${R.bottomCellOf(R.firstCol)}`,
    "matrix_col6_row4": `matrix_${R.secondLastCol.name}_${R.bottomCellOf(R.secondLastCol)}`,
    "matrix_col6_row3": `matrix_${R.secondLastCol.name}_${R.bottomCellOf(R.secondLastCol)}`,
    "matrix_col2_row4": `matrix_${R.firstCol.name}_${R.bottomCellOf(R.firstCol)}`,
    "matrix_col2_row3": `matrix_${R.firstCol.name}_${R.bottomCellOf(R.firstCol)}`,
    "matrix_col1_row1": `matrix_${R.firstCol.name}_${R.topRow}`,
  };
  for (const [oldName, newName] of Object.entries(map)) {
    if (oldName === newName) continue;
    tail = tail.split(`mirror_${oldName}`).join(`mirror_${newName}`);
    tail = tail.split(oldName).join(newName);
  }

  if (!cfg.layout.thumb.enabled) {
    // the hand-rest polygons use the thumb keys as their front edge; drop those points
    tail = tail.replace(/ *- ref: (mirror_)?thumbfan_col\d_thumb_row_1\n(?: +shift: [^\n]*\n)?/g, "");
  }
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
  text = replaceSpan(text, "points:\n", "outlines:\n", buildPoints(cfg), "points", true);

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
  // unify the MCU 3D offset (the canonical file had 2.5 on the left and 5 on the right)
  text = text.replace(/mcu_3dmodel_xyz_offset: \[0, 0, [\d.]+\]/g, "mcu_3dmodel_xyz_offset: [0, 0, 5]");

  // 4. pin maps (both halves)
  text = rewritePinBlocks(text, buildPinMap(cfg));

  // 5. outline references follow the layout
  text = rewritePointRefs(text, cfg);

  // 6. right half needs its own mounting holes (the canonical config only has them on the left)
  if (!/^      r_screws:/m.test(text)) {
    const marker = "      r_standoffs:";
    if (!text.includes(marker)) throw new Error("canonical config: r_standoffs block not found");
    text = text.replace(
      marker,
      `      r_screws:
        what: ceoloide/mounting_hole_npth
        where: right_screw
        params:
          hole_size: screw_diameter
          hole_drill: screw_diameter

${marker}`,
    );
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
