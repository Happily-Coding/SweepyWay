/**
 * SweepyWay configurator - local server.
 *
 * Zero dependencies: node's http + child_process only. It drives the tools that already
 * exist in this repo, so what the browser shows is exactly what the CLI pipeline produces:
 *
 *   JSON config -> config.yaml (lib/generate.mjs)
 *              -> ergogen (PCB, plates, outlines, .jscad cases)
 *              -> checks (scripts/check_matrix.py, scripts/check_print_files.py)
 *              -> fabrication assets (openjscad -> STL, palm rest + tenting python scripts)
 *
 * Run:  node configurator/server.mjs [--port 5173]
 * Then: http://localhost:5173
 */
import http from "node:http";
import { createHash } from "node:crypto";
import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, readFile, readdir, rm, stat, writeFile, cp } from "node:fs/promises";
import { dirname, extname, join, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";

import { normalize, validate, matrixPairs, plateCutout, KEYCAPS } from "./lib/schema.mjs";
import { generate } from "./lib/generate.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "..");
const PUBLIC = join(HERE, "public");
const BUILDS = join(HERE, "builds");
const PRESETS = join(HERE, "presets");
const ERGOGEN_BIN = join(REPO, "node_modules/ergogen/src/cli.js");
const FOOTPRINTS_SRC = join(REPO, "ergogen/footprints");
const PYTHON = join(REPO, ".venv/Scripts/python.exe");
const JSCAD = join(REPO, "node_modules/@jscad/cli/cli.js");

const args = process.argv.slice(2);
const PORT = Number(args[args.indexOf("--port") + 1]) || 5173;

// ------------------------------------------------------------------ process helpers
const NODE = process.platform === "win32" ? "node.exe" : "node";

function run(cmd, cmdArgs, opts = {}) {
  return new Promise((res) => {
    const started = Date.now();
    execFile(
      cmd,
      cmdArgs,
      { cwd: opts.cwd || REPO, maxBuffer: 32 * 1024 * 1024, windowsHide: true, timeout: opts.timeout || 240_000 },
      (err, stdout, stderr) => {
        res({
          ok: !err,
          code: err?.code ?? 0,
          ms: Date.now() - started,
          stdout: (stdout || "").toString(),
          stderr: (stderr || "").toString(),
        });
      },
    );
  });
}

const nodeRun = (scriptArgs, opts) => run(NODE, scriptArgs, opts);

/** Parse the `__JSON__` line emitted by the python checks. */
function parseCheckJson(stdout) {
  const line = stdout.split("\n").reverse().find((l) => l.startsWith("__JSON__"));
  if (!line) return null;
  try {
    return JSON.parse(line.slice("__JSON__".length));
  } catch {
    return null;
  }
}

// ------------------------------------------------------------------ build workspace
function slugFor(cfg) {
  const hash = createHash("sha1").update(JSON.stringify(cfg)).digest("hex").slice(0, 8);
  return `${cfg.name}-${hash}`;
}

async function ensureWorkspace(slug) {
  const dir = join(BUILDS, slug);
  await mkdir(join(dir, "assets"), { recursive: true });
  const link = join(dir, "footprints");
  if (!existsSync(link)) {
    if (process.platform === "win32") {
      // a junction avoids copying 600 KB of footprints on every build
      const r = await run("cmd.exe", ["/c", "mklink", "/J", link, FOOTPRINTS_SRC]);
      if (!r.ok) await cp(FOOTPRINTS_SRC, link, { recursive: true });
    } else {
      await cp(FOOTPRINTS_SRC, link, { recursive: true });
    }
  }
  return dir;
}

// ------------------------------------------------------------------ stages
async function stageGenerate(cfg, dir) {
  const { errors, warnings } = validate(cfg);
  if (errors.length) {
    return { name: "validate", ok: false, ms: 0, log: errors.join("\n"), errors, warnings, data: null };
  }
  const yaml = generate(cfg);
  await writeFile(join(dir, "config.yaml"), yaml, "utf8");
  const pairs = matrixPairs(cfg);
  return {
    name: "generate",
    ok: true,
    ms: 0,
    log: `config.yaml written (${yaml.split("\n").length} lines)\n${pairs.length} keys, ${cfg.layout.columns.length} columns, ${cfg.layout.rows.length} rows`,
    errors: [],
    warnings,
    data: { keys: pairs.length, plateCutout: plateCutout(cfg), keycap: KEYCAPS[cfg.spacing.keycap] },
  };
}

async function stageErgogen(dir) {
  const r = await nodeRun([ERGOGEN_BIN, dir + "/", "--output", join(dir, "out"), "--clear", "--debug"]);
  const tail = `${r.stdout}\n${r.stderr}`.trim().split("\n").slice(-6).join("\n");
  return { name: "ergogen", ok: r.ok, ms: r.ms, log: tail, errors: r.ok ? [] : [tail], data: null };
}

async function stageChecks(dir) {
  const pcbs = join(dir, "out", "pcbs");
  const r = await run(PYTHON, [
    join(REPO, "scripts/check_matrix.py"),
    "--json", "--plates", "--pcbs-dir", pcbs,
    "--board", join(pcbs, "left_pcb.kicad_pcb"),
    "--board", join(pcbs, "right_pcb.kicad_pcb"),
  ]);
  const data = parseCheckJson(r.stdout);
  const problems = data ? data.boards.flatMap((b) => b.problems) : [r.stderr || r.stdout];
  return {
    name: "checks",
    ok: Boolean(data?.ok),
    ms: r.ms,
    log: data
      ? data.boards
          .map(
            (b) =>
              `${relative(REPO, b.path)}: ${b.keys} keys, ${b.rows}x${b.columns}, ` +
              `${b.bbox ? `${b.bbox[0].toFixed(1)}x${b.bbox[1].toFixed(1)} mm` : "?"}, ` +
              `${b.segments} segments, ${b.vias} vias`,
          )
          .join("\n")
      : (r.stderr || "").slice(0, 2000),
    errors: data?.ok ? [] : problems.filter(Boolean).slice(0, 12),
    data: data ? { boards: data.boards } : null,
  };
}

async function stagePlates(dir) {
  // the check above already validates cutout sizes; here we expose the plate geometry
  const pcbs = join(dir, "out", "pcbs");
  const out = [];
  for (const plate of ["plate_left", "plate_right"]) {
    const p = join(pcbs, `${plate}.kicad_pcb`);
    if (existsSync(p)) out.push({ plate, file: relative(BUILDS, p).replace(/\\/g, "/") });
  }
  return { name: "plates", ok: out.length > 0, ms: 0, log: out.map((o) => o.plate).join(", "), errors: [], data: { plates: out } };
}

async function stageCases(dir, cfg) {
  // ergogen emits .jscad; openjscad turns them into printable STL
  const casesDir = join(dir, "out", "cases");
  const assets = join(dir, "assets");
  if (!existsSync(casesDir)) return { name: "cases", ok: false, ms: 0, log: "no cases in the ergogen output", errors: ["no cases"], data: null };
  const files = (await readdir(casesDir)).filter((f) => f.endsWith(".jscad"));
  const want = files.filter((f) => !f.includes("3d_preview"));
  const results = [];
  for (const f of want) {
    const out = join(assets, f.replace(/\.jscad$/, ".stl"));
    const r = await run(NODE, [JSCAD, join(casesDir, f), "-of", "stla", "-o", out], { timeout: 300_000 });
    let log = r.ok ? "" : (r.stderr || "").slice(0, 400);
    let ok = r.ok && existsSync(out);
    if (ok) {
      // OpenJSCAD's CSG leaves coplanar T-junctions in the case shell; weld + orient it
      const rep = await run(PYTHON, [join(REPO, "scripts/repair_stl.py"), out, "--json", "--drop-to-bed"]);
      if (!rep.ok) log = `repair: ${(rep.stdout || rep.stderr).slice(-300)}`;
    }
    results.push({ name: f, ok, log });
  }
  const ok = results.every((r) => r.ok);
  return {
    name: "cases",
    ok,
    ms: 0,
    log: results.map((r) => `${r.ok ? "ok  " : "FAIL"} ${r.name}`).join("\n"),
    errors: results.filter((r) => !r.ok).map((r) => `${r.name}: ${r.log}`),
    data: { stls: results.filter((r) => r.ok).map((r) => `assets/${r.name.replace(/\.jscad$/, ".stl")}`) },
  };
}

async function stagePrints(dir, cfg) {
  const outlines = join(dir, "out", "outlines");
  const assets = join(dir, "assets");
  const produced = [];
  const errors = [];

  // B16: every outline exists per side (l_/r_). The print stage used to hard-code the `l_` names,
  // so only a LEFT tenting base / palm rest could ever be produced even though the right outlines
  // are valid. An empty/absent outline is reported as an error instead of a cryptic Python failure.
  const sides = cfg.printSides ?? ["l", "r"];
  const dxfOk = async (name) => {
    const p = join(outlines, `${name}.dxf`);
    if (!existsSync(p)) return `outline ${name}.dxf is missing`;
    const txt = await readFile(p, "utf8").catch(() => "");
    return /\n(LINE|ARC|LWPOLYLINE|POLYLINE)\n/.test(txt) ? null : `outline ${name}.dxf is EMPTY`;
  };

  for (const side of sides) {
    const suffix = side === "l" ? "" : `_${side}`;

    if (cfg.palmRest.enabled) {
      const bad = await dxfOk(`${side}_hand_rest_polygon`);
      const out = join(assets, `palm_rest${suffix}.stl`);
      if (bad) errors.push(`palm rest (${side}): ${bad}`);
      else {
        const r = await run(PYTHON, [
          join(REPO, "palmrest_and_tenting_creation/create_palmrest.py"),
          "--dxf", join(outlines, `${side}_hand_rest_polygon.dxf`),
          "--out", out,
          "--height", String(cfg.palmRest.height),
          "--curve", String(cfg.palmRest.curve),
        ]);
        if (r.ok && existsSync(out)) produced.push(`assets/palm_rest${suffix}.stl`);
        else errors.push(`palm rest (${side}): ${(r.stderr || r.stdout).slice(-500)}`);
      }
    }

    if (cfg.tenting.enabled) {
      const bad = await dxfOk(`${side}_tenting_base_bottom_outline`);
      const out = join(assets, `tenting_base${suffix}.stl`);
      if (bad) errors.push(`tenting (${side}): ${bad}`);
      else {
        const cargs = [
          join(REPO, "palmrest_and_tenting_creation/create_tenting_system.py"),
          "--dxf", join(outlines, `${side}_tenting_base_bottom_outline.dxf`),
          "--palm-dxf", join(outlines, `${side}_hand_rest_polygon.dxf`),
          "--out", out,
          "--angle", String(cfg.tenting.angle),
          "--z-min", String(cfg.tenting.zMin),
          "--hollow", String(cfg.tenting.hollow),
        ];
        if (cfg.tenting.includePalmRest) cargs.push("--include-palm-rest");
        const r = await run(PYTHON, cargs);
        if (r.ok && existsSync(out)) produced.push(`assets/tenting_base${suffix}.stl`);
        else errors.push(`tenting (${side}): ${(r.stderr || r.stdout).slice(-500)}`);
      }
    }
  }

  const all = [...produced];
  for (const f of await readdir(assets).catch(() => [])) {
    if (f.endsWith(".stl") && !all.includes(`assets/${f}`)) all.push(`assets/${f}`);
  }
  if (!all.length) {
    return { name: "prints", ok: false, ms: 0, log: "nothing produced", errors: errors.length ? errors : ["nothing produced"], data: null };
  }

  const check = await run(PYTHON, [
    join(REPO, "scripts/check_print_files.py"),
    "--json",
    ...all.map((f) => join(dir, f)),
  ]);
  const data = parseCheckJson(check.stdout);
  return {
    name: "prints",
    ok: Boolean(data?.ok) && errors.length === 0,
    ms: check.ms,
    log: (data?.files ?? [])
      .map(
        (f) =>
          `${f.ok ? "ok  " : "FAIL"} ${f.path.split(/[\\/]/).pop()}: ` +
          `${f.bbox.join(" x ")} mm, ${f.volume_cm3} cm3, ` +
          `${f.watertight ? "watertight" : `${f.boundary_edges} boundary edges`}`,
      )
      .join("\n"),
    errors: [...errors, ...(data?.files ?? []).filter((f) => !f.ok).map((f) => `${f.path}: not printable`)],
    data: { files: data?.files ?? [], stls: all },
  };
}

function stageSvgs(dir) {
  // ergogen writes an SVG next to every DXF outline; expose the interesting ones
  const outlines = join(dir, "out", "outlines");
  const wanted = [
    "l_pcb_outline",
    "l_coverpart_switch_plate_outline",
    "l_case_bottom",
    "l_keys_outline",
    "l_hand_rest_polygon",
    "l_tenting_base_bottom_outline",
    "l_all_key_clusters_outline",
    "r_coverpart_switch_plate_outline",
    "r_hand_rest_polygon",
    "r_tenting_base_bottom_outline",
  ];
  const svgs = [];
  for (const w of wanted) {
    const p = join(outlines, `${w}.svg`);
    if (existsSync(p)) svgs.push({ name: w, url: `/builds/${relative(BUILDS, p).replace(/\\/g, "/")}` });
  }
  const pointsPreview = join(dir, "out", "points", "demo.svg");
  if (existsSync(pointsPreview)) svgs.unshift({ name: "key positions", url: `/builds/${relative(BUILDS, pointsPreview).replace(/\\/g, "/")}` });
  return svgs;
}

// ------------------------------------------------------------------ HTTP
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".stl": "model/stl",
  ".glb": "model/gltf-binary",
  ".dxf": "application/dxf",
  ".yaml": "text/plain; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
};

async function serveFile(res, path) {
  try {
    const s = await stat(path);
    if (!s.isFile()) throw new Error("not a file");
    const buf = await readFile(path);
    res.writeHead(200, {
      "content-type": MIME[extname(path).toLowerCase()] || "application/octet-stream",
      "cache-control": "no-store",
    });
    res.end(buf);
  } catch {
    res.writeHead(404, { "content-type": "text/plain" });
    res.end("not found");
  }
}

async function readBody(req) {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString("utf8");
  if (!raw) return {};
  return JSON.parse(raw);
}

function json(res, code, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(code, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" });
  res.end(body);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const p = decodeURIComponent(url.pathname);

  try {
    if (p === "/api/presets" && req.method === "GET") {
      const files = (await readdir(PRESETS)).filter((f) => f.endsWith(".json"));
      const presets = [];
      for (const f of files) {
        const cfg = JSON.parse(await readFile(join(PRESETS, f), "utf8"));
        presets.push({ file: f, config: cfg });
      }
      return json(res, 200, { presets });
    }

    if (p === "/api/validate" && req.method === "POST") {
      const cfg = normalize(await readBody(req));
      const v = validate(cfg);
      return json(res, 200, { ...v, normalized: cfg, keys: matrixPairs(cfg).length, plateCutout: plateCutout(cfg) });
    }

    if (p === "/api/build" && req.method === "POST") {
      const body = await readBody(req);
      const cfg = normalize(body.config || {});
      const stages = body.stages || ["geometry"];
      const slug = slugFor(cfg);
      const dir = await ensureWorkspace(slug);
      const results = [];

      const gen = await stageGenerate(cfg, dir);
      results.push(gen);
      if (!gen.ok) return json(res, 200, { ok: false, slug, stages: results });

      if (stages.includes("geometry")) {
        const ergo = await stageErgogen(dir);
        results.push(ergo);
        if (ergo.ok) {
          results.push(await stageChecks(dir));
          results.push(await stagePlates(dir));
          results.push(await stageCases(dir, cfg));
        }
      }
      if (stages.includes("prints")) {
        if (!existsSync(join(dir, "out", "outlines", "l_pcb_outline.dxf"))) {
          const ergo = await stageErgogen(dir);
          if (!results.some((r) => r.name === "ergogen")) results.push(ergo);
        }
        results.push(await stagePrints(dir, cfg));
      }

      const ok = results.every((r) => r.ok);
      const meta = {
        slug,
        config: cfg,
        ok,
        builtAt: new Date().toISOString(),
        stages: results.map(({ name, ok: o, ms, log, errors, data }) => ({ name, ok: o, ms, log, errors, data })),
        svgs: stageSvgs(dir),
      };
      await writeFile(join(dir, "meta.json"), JSON.stringify(meta, null, 2), "utf8");
      return json(res, 200, { ok, slug, stages: results, svgs: meta.svgs });
    }

    if (p.startsWith("/builds/") && req.method === "GET") {
      const rel = p.slice("/builds/".length);
      const target = resolve(BUILDS, rel);
      if (!target.startsWith(BUILDS)) return json(res, 400, { error: "bad path" });
      return serveFile(res, target);
    }

    if (p === "/" || p === "/index.html") return serveFile(res, join(PUBLIC, "index.html"));
    if (p.startsWith("/public/")) return serveFile(res, join(PUBLIC, p.slice("/public/".length)));

    // anything else: try the public dir
    return serveFile(res, join(PUBLIC, p.replace(/^\/+/, "")));
  } catch (err) {
    console.error(err);
    return json(res, 500, { error: String(err?.message || err) });
  }
});

server.listen(PORT, () => {
  console.log(`SweepyWay configurator -> http://localhost:${PORT}`);
  console.log(`  repo:   ${REPO}`);
  console.log(`  builds: ${BUILDS}`);
});
