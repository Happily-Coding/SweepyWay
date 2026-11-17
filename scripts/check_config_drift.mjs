#!/usr/bin/env node
/**
 * B22 drift gate: would running the configurator change the keyboard?
 *
 * `configurator/lib/generate.mjs` reads `ergogen/config.yaml` as a template and rewrites the
 * regions it owns (presets, points, the screw shifts, pin maps, a few scalars). Nothing forced
 * the result to still *mean* the committed file, so a hand-fix (B13 screws, B4 twins, F3b bosses,
 * B17 rim) could be silently reverted by clicking "generate".
 *
 * This script regenerates the DEFAULT preset entirely IN MEMORY and compares it, structurally,
 * with the committed file. It never writes `ergogen/config.yaml` (or anything else).
 *
 * The comparison is semantic, not textual: comments and YAML key order are irrelevant, and
 * ergogen expressions are evaluated against each document's own `units`/`presets`, so
 * `key.stagger: 0.25 ky` equals `key.stagger: 4.25` when ky is 17. Anything else - a moved
 * screw, a lost boss, a changed pin net, a dropped key - fails with the path and both values.
 *
 *   node scripts/check_config_drift.mjs [preset.json]
 *
 * exit 0 = the generator reproduces the committed config, 1 = drift, 2 = cannot run.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, resolve } from "node:path";
import { createRequire } from "node:module";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "..");
const DEFAULT_PRESET = resolve(REPO, "configurator/presets/sweepyway.json");
const require = createRequire(resolve(REPO, "package.json"));

// ---------------------------------------------------------------- YAML
let yaml;
try {
  yaml = require("js-yaml");
} catch {
  console.error("check_config_drift: js-yaml is missing - run `npm install` (the configurator needs it).");
  process.exit(2);
}

const load = (text, label) => {
  try {
    return yaml.safeLoad ? yaml.safeLoad(text) : yaml.load(text);
  } catch (err) {
    console.error(`check_config_drift: ${label} is not valid YAML: ${err.message}`);
    process.exit(2);
  }
};

// ---------------------------------------------------------------- ergogen expressions
// The values we compare are ergogen units: numbers, symbols (`kx`, `standoff_length`) and
// arithmetic over them. Evaluating both sides with each file's own symbol table is what makes
// `0.25 ky` and `4.25`, or `14.0` and `14`, compare equal without blinding the gate.
const expression = (() => {
  const NUMBER = /^\d*\.?\d+/;
  const IDENT = /^[A-Za-z_][A-Za-z0-9_]*/;

  function tokenize(src) {
    const tokens = [];
    let rest = String(src);
    while (rest.length) {
      const space = /^\s+/.exec(rest);
      if (space) {
        rest = rest.slice(space[0].length);
        continue;
      }
      const num = NUMBER.exec(rest);
      if (num) {
        tokens.push({ t: "num", v: Number(num[0]) });
        rest = rest.slice(num[0].length);
        continue;
      }
      const ident = IDENT.exec(rest);
      if (ident) {
        tokens.push({ t: "id", v: ident[0] });
        rest = rest.slice(ident[0].length);
        continue;
      }
      if ("+-*/()".includes(rest[0])) {
        tokens.push({ t: "op", v: rest[0] });
        rest = rest.slice(1);
        continue;
      }
      throw new Error(`cannot parse "${src}"`);
    }
    return tokens;
  }

  /** @returns {number} or throws when the string is not a (resolvable) numeric expression. */
  return function evaluate(src, units) {
    const tokens = tokenize(src);
    let pos = 0;
    const peek = () => tokens[pos];
    const isOp = (...ops) => peek()?.t === "op" && ops.includes(peek().v);
    const startsFactor = () => {
      const token = peek();
      return token && (token.t === "num" || token.t === "id" || (token.t === "op" && token.v === "("));
    };

    const atom = () => {
      const token = tokens[pos];
      if (!token) throw new Error("unexpected end");
      if (token.t === "num") {
        pos += 1;
        return token.v;
      }
      if (token.t === "id") {
        pos += 1;
        return units.value(token.v);
      }
      if (token.t === "op" && token.v === "(") {
        pos += 1;
        const value = sum();
        if (!isOp(")")) throw new Error("missing )");
        pos += 1;
        return value;
      }
      throw new Error(`unexpected "${token.v}"`);
    };
    const unary = () => {
      if (isOp("-")) {
        pos += 1;
        return -unary();
      }
      if (isOp("+")) {
        pos += 1;
        return unary();
      }
      return atom();
    };
    const product = () => {
      let value = unary();
      for (;;) {
        if (isOp("*")) {
          pos += 1;
          value *= unary();
        } else if (isOp("/")) {
          pos += 1;
          value /= unary();
        } else if (startsFactor()) {
          value *= unary(); // `0.5px`, `-0.25*kx y` - ergogen allows the implied product
        } else {
          return value;
        }
      }
    };
    const sum = () => {
      let value = product();
      for (;;) {
        if (isOp("+")) {
          pos += 1;
          value += product();
        } else if (isOp("-")) {
          pos += 1;
          value -= product();
        } else {
          return value;
        }
      }
    };

    const value = sum();
    if (pos !== tokens.length) throw new Error("trailing tokens");
    if (!Number.isFinite(value)) throw new Error("not finite");
    return value;
  };
})();

/** Presets with `$extends` resolved, then `units`, as one lazy symbol table. */
class Units {
  constructor(doc, label) {
    this.label = label;
    const presets = doc?.presets ?? {};
    const resolved = {};
    const resolvePreset = (name, seen = []) => {
      if (Object.hasOwn(resolved, name)) return resolved[name];
      if (seen.includes(name)) throw new Error(`preset cycle: ${[...seen, name].join(" -> ")}`);
      const preset = presets[name];
      if (!preset) throw new Error(`missing preset "${name}"`);
      const ext = preset.$extends;
      const base = ext ? resolvePreset(String(ext).replace(/^presets\./, ""), [...seen, name]) : {};
      const own = { ...preset };
      delete own.$extends;
      resolved[name] = { ...base, ...own };
      return resolved[name];
    };
    for (const name of Object.keys(presets)) resolvePreset(name);
    this.presets = resolved;

    const ext = doc?.units?.$extends;
    const base = ext ? resolved[String(ext).replace(/^presets\./, "")] ?? {} : {};
    this.symbols = { ...base, ...(doc?.units ?? {}) };
    delete this.symbols.$extends;
    this.cache = new Map();
    this.inProgress = new Set();
  }

  value(name) {
    if (this.cache.has(name)) return this.cache.get(name);
    if (!Object.hasOwn(this.symbols, name)) throw new Error(`unknown symbol "${name}"`);
    if (this.inProgress.has(name)) throw new Error(`cycle at "${name}"`);
    this.inProgress.add(name);
    try {
      const raw = this.symbols[name];
      const value = typeof raw === "number" ? raw : expression(String(raw), this);
      this.cache.set(name, value);
      return value;
    } finally {
      this.inProgress.delete(name);
    }
  }
}

const asNumber = (value, units) => {
  if (typeof value === "number") return value;
  if (typeof value !== "string") return null;
  try {
    return expression(value, units);
  } catch {
    return null;
  }
};

// ---------------------------------------------------------------- structural comparison
const EPSILON = 1e-9;
const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);

function describe(value) {
  const text = JSON.stringify(value);
  return text === undefined ? String(value) : text.length > 160 ? `${text.slice(0, 157)}...` : text;
}

function compare(committed, generated) {
  const diffs = [];
  const committedUnits = new Units(committed, "committed");
  const generatedUnits = new Units(generated, "generated");

  const add = (path, a, b, extra = "") => diffs.push({ path, committed: a, generated: b, extra });

  const scalar = (path, a, b) => {
    const na = asNumber(a, committedUnits);
    const nb = asNumber(b, generatedUnits);
    if (na !== null && nb !== null) {
      if (Math.abs(na - nb) > EPSILON) add(path, a, b, `-> ${na} vs ${nb}`);
      return;
    }
    if (a === b) return;
    add(path, a, b);
  };

  const walk = (a, b, path) => {
    if (Array.isArray(a) || Array.isArray(b)) {
      if (!Array.isArray(a) || !Array.isArray(b)) return add(path, a, b, "list vs scalar");
      if (a.length !== b.length) add(path, `[${a.length} items]`, `[${b.length} items]`);
      for (let i = 0; i < Math.min(a.length, b.length); i += 1) walk(a[i], b[i], `${path}[${i}]`);
      return;
    }
    if (isObject(a) || isObject(b)) {
      if (!isObject(a) || !isObject(b)) return add(path, a, b, "mapping vs scalar");
      for (const key of Object.keys(a)) {
        const child = path ? `${path}.${key}` : key;
        if (!Object.hasOwn(b, key)) add(child, describe(a[key]), "(missing)", "present in config.yaml only");
        else walk(a[key], b[key], child);
      }
      for (const key of Object.keys(b)) {
        if (Object.hasOwn(a, key)) continue;
        const child = path ? `${path}.${key}` : key;
        add(child, "(missing)", describe(b[key]), "produced by the generator only");
      }
      return;
    }
    scalar(path || "<root>", a, b);
  };

  walk(committed, generated, "");
  return diffs;
}

// ---------------------------------------------------------------- main
const presetPath = resolve(process.argv[2] ?? DEFAULT_PRESET);
const relPreset = presetPath.replace(REPO, "").replace(/^[\\/]/, "").replace(/\\/g, "/");

let generatedText;
try {
  const { generate, CANONICAL_CONFIG } = await import(pathToFileURL(resolve(REPO, "configurator/lib/generate.mjs")));
  const { normalize } = await import(pathToFileURL(resolve(REPO, "configurator/lib/schema.mjs")));
  const cfg = normalize(JSON.parse(readFileSync(presetPath, "utf8")));
  generatedText = generate(cfg); // in memory: nothing is written, config.yaml is never touched
  console.log(`generator   : ${relPreset} -> in memory (ergogen/config.yaml untouched)`);
  console.log(`canonical   : ${CANONICAL_CONFIG.replace(REPO, "").replace(/^[\\/]/, "").replace(/\\/g, "/")}`);
} catch (err) {
  console.error(`\nB22 DRIFT: the configurator cannot generate from ${relPreset} at all.`);
  console.error(`  ${err.message}`);
  console.error("  (the generator asserts every anchor it splices; a red gate here means the");
  console.error("   template changed shape, not that the values drifted)");
  process.exit(1);
}

const committedText = readFileSync(resolve(REPO, "ergogen/config.yaml"), "utf8");
const diffs = compare(load(committedText, "ergogen/config.yaml"), load(generatedText, "generator output"));

if (diffs.length === 0) {
  console.log("drift       : none - the generator reproduces ergogen/config.yaml");
  console.log("\nB22 gate: PASS");
  process.exit(0);
}

console.error(`\nB22 DRIFT: ${diffs.length} difference(s) between the generated config and ergogen/config.yaml`);
console.error("           (comments/key order are ignored; ergogen unit expressions are evaluated)\n");
for (const diff of diffs.slice(0, 60)) {
  console.error(`  ${diff.path}`);
  console.error(`      committed: ${describe(diff.committed)}`);
  console.error(`      generated: ${describe(diff.generated)}`);
  if (diff.extra) console.error(`      ${diff.extra}`);
}
if (diffs.length > 60) console.error(`  ... and ${diffs.length - 60} more`);
console.error("\nFix: teach configurator/lib/generate.mjs (data lives in configurator/lib/schema.mjs:");
console.error("     SCREW_SHIFTS, PRESETS, ...) to emit the committed value, or change ergogen/config.yaml");
console.error("     on purpose - but never let the two disagree. See docs/CONFIGURATOR-DRIFT.md (B22).");
console.error("\nB22 gate: FAIL");
process.exit(1);
