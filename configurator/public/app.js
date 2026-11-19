/**
 * SweepyWay configurator UI.
 *
 * Everything the page shows comes from the server, which runs the same tools as CI:
 * no geometry is re-implemented here. The form only edits the JSON config.
 */
const $ = (id) => document.getElementById(id);
const state = {
  config: null,
  presets: [],
  lastBuild: null,
  viewer: null,
};

// ------------------------------------------------------------------ fetch helpers
async function api(path, body) {
  const res = await fetch(path, body ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) } : {});
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  return res.json();
}

function setStatus(msg, busy = false) {
  const el = $("status");
  el.textContent = msg || "";
  el.className = `status${busy ? " busy" : ""}`;
}

// ------------------------------------------------------------------ config binding
function bindField(id, get, set, transform = (v) => v) {
  const el = $(id);
  el.addEventListener("input", () => {
    const v = el.type === "checkbox" ? el.checked : el.type === "number" ? Number(el.value) : el.value;
    set(transform(v));
    scheduleValidate();
  });
  return () => {
    const v = get();
    if (el.type === "checkbox") el.checked = Boolean(v);
    else el.value = v ?? "";
  };
}

const binders = [];

function renderForm() {
  const c = state.config;
  $("name").value = c.name;

  binders.length = 0;
  binders.push(bindField("switch-family", () => c.switch.family, (v) => (c.switch.family = v)));
  binders.push(bindField("switch-support", () => c.switch.support, (v) => (c.switch.support = v)));
  binders.push(bindField("keycap", () => c.spacing.keycap, (v) => (c.spacing.keycap = v)));
  binders.push(bindField("kx", () => c.spacing.kx, (v) => (c.spacing.kx = v)));
  binders.push(bindField("ky", () => c.spacing.ky, (v) => (c.spacing.ky = v)));

  binders.push(bindField("rowstagger-on", () => Array.isArray(c.layout.rowStagger), (v) => {
    c.layout.rowStagger = v ? c.layout.rows.map((_, i) => i * (c.spacing.kx * 0.25)) : null;
    renderRowStagger();
  }));
  binders.push(bindField("thumb-on", () => c.layout.thumb.enabled, (v) => (c.layout.thumb.enabled = v)));
  binders.push(bindField("thumb-count", () => c.layout.thumb.count, (v) => (c.layout.thumb.count = v)));
  binders.push(bindField("thumb-rotate", () => c.layout.thumb.rotate, (v) => (c.layout.thumb.rotate = v)));
  binders.push(bindField("thumb-spread", () => c.layout.thumb.spread, (v) => (c.layout.thumb.spread = v)));

  binders.push(bindField("case-bottom", () => c.case.bottomThickness, (v) => (c.case.bottomThickness = v)));
  binders.push(bindField("case-standoff", () => c.case.standoffLength, (v) => (c.case.standoffLength = v)));
  binders.push(bindField("case-body", () => c.case.standoffBodyLength, (v) => (c.case.standoffBodyLength = v)));
  // B23: MCU mounting preset (generic = default). Drives the controller-hood height.
  binders.push(bindField("case-mcu-mounting", () => c.case.mcuMounting, (v) => { c.case.mcuMounting = v; }));
  binders.push(bindField("case-height", () => c.case.borderHeight, (v) => (c.case.borderHeight = v)));
  binders.push(bindField("case-wall", () => c.case.wallThickness, (v) => (c.case.wallThickness = v)));

  binders.push(bindField("palm-on", () => c.palmRest.enabled, (v) => (c.palmRest.enabled = v)));
  binders.push(bindField("palm-height", () => c.palmRest.height, (v) => (c.palmRest.height = v)));
  binders.push(bindField("palm-curve", () => c.palmRest.curve, (v) => (c.palmRest.curve = v)));

  binders.push(bindField("tent-on", () => c.tenting.enabled, (v) => (c.tenting.enabled = v)));
  binders.push(bindField("tent-angle", () => c.tenting.angle, (v) => (c.tenting.angle = v)));
  binders.push(bindField("tent-zmin", () => c.tenting.zMin, (v) => (c.tenting.zMin = v)));
  binders.push(bindField("tent-hollow", () => c.tenting.hollow, (v) => (c.tenting.hollow = v)));
  binders.push(bindField("tent-palm", () => c.tenting.includePalmRest, (v) => (c.tenting.includePalmRest = v)));

  binders.push(bindField("pcb-thickness", () => c.fab.pcbThickness, (v) => (c.fab.pcbThickness = v)));
  binders.push(bindField("plate-thickness", () => c.fab.plateThickness, (v) => (c.fab.plateThickness = v)));

  for (const b of binders) b();
  renderGrid();
  renderRowStagger();
  updatePitchHint();
}

function updatePitchHint() {
  const c = state.config;
  const cap = c.spacing.keycap === "mbk" ? { w: 17.5, h: 16.5 } : { w: 16.5, h: 16.5 };
  const minX = (cap.w + 0.4).toFixed(1);
  const minY = (cap.h + 0.4).toFixed(1);
  $("pitch-hint").textContent =
    `${c.spacing.keycap.toUpperCase()} caps are ${cap.w} x ${cap.h} mm; the pitch must be at least ` +
    `${minX} x ${minY} mm. Current: ${c.spacing.kx} x ${c.spacing.ky} mm.`;
}

// ------------------------------------------------------------------ layout grid
function renderGrid() {
  const c = state.config;
  const grid = $("grid");
  grid.innerHTML = "";
  c.layout.columns.forEach((col, ci) => {
    const div = document.createElement("div");
    div.className = "col";
    const head = document.createElement("h3");
    head.textContent = `${col.name} (${col.net})`;
    div.appendChild(head);

    const mk = (label, value, onChange, step = 0.25) => {
      const l = document.createElement("label");
      l.textContent = label;
      const i = document.createElement("input");
      i.type = "number";
      i.step = String(step);
      i.value = value;
      i.addEventListener("input", () => {
        onChange(Number(i.value));
        scheduleValidate();
      });
      l.appendChild(i);
      return l;
    };
    div.appendChild(mk("stagger", col.stagger ?? 0, (v) => (col.stagger = v)));
    div.appendChild(mk("spread", col.spread ?? c.spacing.kx, (v) => (col.spread = v), 0.5));
    div.appendChild(mk("splay", col.splay ?? 0, (v) => (col.splay = v), 1));

    const cells = document.createElement("div");
    cells.className = "cells";
    // display top-first (the YAML lists rows bottom-first)
    [...c.layout.rows].reverse().forEach((row) => {
      const l = document.createElement("label");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = col.cells.includes(row);
      cb.addEventListener("change", () => {
        if (cb.checked) {
          col.cells.push(row);
          // keep the config order (bottom-first) so the generator keeps the same geometry
          col.cells.sort((a, b) => c.layout.rows.indexOf(a) - c.layout.rows.indexOf(b));
        } else {
          col.cells = col.cells.filter((r) => r !== row);
        }
        scheduleValidate();
      });
      l.appendChild(cb);
      l.appendChild(document.createTextNode(row));
      cells.appendChild(l);
    });
    div.appendChild(cells);

    const add = document.createElement("div");
    add.className = "row";
    add.style.marginTop = "6px";
    const del = document.createElement("button");
    del.className = "ghost";
    del.textContent = "remove";
    del.style.padding = "2px 6px";
    del.style.fontSize = "11px";
    del.addEventListener("click", () => {
      c.layout.columns.splice(ci, 1);
      c.layout.columns.forEach((cc, i) => {
        cc.name = `col${i + 1}`;
        cc.net = `C${i + 1}`;
      });
      renderForm();
      scheduleValidate();
    });
    add.appendChild(del);
    div.appendChild(add);
    grid.appendChild(div);
  });

  const addCol = document.createElement("div");
  addCol.className = "col";
  const h = document.createElement("h3");
  h.textContent = "+";
  addCol.appendChild(h);
  const btn = document.createElement("button");
  btn.className = "ghost";
  btn.textContent = "add column";
  btn.style.fontSize = "11px";
  btn.addEventListener("click", () => {
    const n = c.layout.columns.length + 1;
    c.layout.columns.push({ name: `col${n}`, net: `C${n}`, stagger: 0, spread: null, splay: 0, cells: c.layout.rows.slice() });
    renderForm();
    scheduleValidate();
  });
  addCol.appendChild(btn);
  grid.appendChild(addCol);
}

function renderRowStagger() {
  const c = state.config;
  const box = $("rowstagger");
  const on = Array.isArray(c.layout.rowStagger);
  box.classList.toggle("hidden", !on);
  $("rowstagger-on").checked = on;
  if (!on) return;
  box.innerHTML = "";
  c.layout.rows.forEach((row, i) => {
    const l = document.createElement("label");
    l.textContent = `${row} x (abs)`;
    const input = document.createElement("input");
    input.type = "number";
    input.step = "0.25";
    input.value = c.layout.rowStagger[i] ?? 0;
    input.addEventListener("input", () => {
      c.layout.rowStagger[i] = Number(input.value);
      scheduleValidate();
    });
    l.appendChild(input);
    box.appendChild(l);
  });
}

// ------------------------------------------------------------------ validation
let validateTimer = null;
function scheduleValidate() {
  clearTimeout(validateTimer);
  validateTimer = setTimeout(doValidate, 250);
  updatePitchHint();
}

async function doValidate() {
  const issues = $("issues");
  try {
    const v = await api("/api/validate", state.config);
    state.config = v.normalized;
    const parts = [];
    if (v.errors.length) parts.push(`<div class="issue error"><b>${v.errors.length} error(s)</b><ul>${v.errors.map((e) => `<li>${e}</li>`).join("")}</ul></div>`);
    if (v.warnings.length) parts.push(`<div class="issue warn"><b>${v.warnings.length} warning(s)</b><ul>${v.warnings.map((e) => `<li>${e}</li>`).join("")}</ul></div>`);
    if (!v.errors.length && !v.warnings.length) parts.push(`<div class="issue ok">Configuration is valid - ${v.keys} keys, plate cutout ${v.plateCutout} mm.</div>`);
    issues.innerHTML = parts.join("");
  } catch (err) {
    issues.innerHTML = `<div class="issue error">${err.message}</div>`;
  }
}

// ------------------------------------------------------------------ build
async function build(withPrints) {
  setStatus(withPrints ? "building geometry + print files (this takes ~30 s)..." : "building geometry...", true);
  $("btn-preview").disabled = true;
  $("btn-prints").disabled = true;
  renderStages([{ name: withPrints ? "geometry + prints" : "geometry", ok: null, ms: 0, log: "running..." }]);
  try {
    const stages = withPrints ? ["geometry", "prints"] : ["geometry"];
    const res = await api("/api/build", { config: state.config, stages });
    state.lastBuild = res;
    renderStages(res.stages);
    renderMetrics(res);
    renderSvgs(res.svgs || []);
    renderFiles(res);
    await renderViewer(res);
    setStatus(res.ok ? `done - build ${res.slug}` : "finished with problems (see stages)", false);
  } catch (err) {
    renderStages([{ name: "build", ok: false, ms: 0, log: String(err.message) }]);
    setStatus("build failed", false);
  } finally {
    $("btn-preview").disabled = false;
    $("btn-prints").disabled = false;
  }
}

function renderStages(stages) {
  const ol = $("stages");
  ol.innerHTML = "";
  for (const s of stages) {
    const li = document.createElement("li");
    li.className = `stage ${s.ok === true ? "ok" : s.ok === false ? "fail" : ""}`;
    const head = document.createElement("header");
    head.innerHTML = `<span class="dot ${s.ok === true ? "ok" : s.ok === false ? "fail" : ""}"></span>
      <span>${s.name}</span><span class="ms">${s.ms ? `${s.ms} ms` : ""}</span>`;
    li.appendChild(head);
    if (s.log) {
      const pre = document.createElement("pre");
      pre.textContent = s.log.split("\n").slice(0, 14).join("\n");
      li.appendChild(pre);
    }
    if (s.errors && s.errors.length) {
      const ul = document.createElement("ul");
      ul.className = "errlist";
      for (const e of s.errors.slice(0, 8)) {
        const el = document.createElement("li");
        el.textContent = String(e).slice(0, 400);
        ul.appendChild(el);
      }
      li.appendChild(ul);
    }
    ol.appendChild(li);
  }
}

function renderMetrics(res) {
  const box = $("metrics");
  box.innerHTML = "";
  const gen = res.stages.find((s) => s.name === "generate");
  const chk = res.stages.find((s) => s.name === "checks");
  const prn = res.stages.find((s) => s.name === "prints");
  const board = chk?.data?.boards?.[0];
  const add = (value, label) => {
    const d = document.createElement("div");
    d.className = "metric";
    d.innerHTML = `<b>${value}</b><span>${label}</span>`;
    box.appendChild(d);
  };
  if (gen?.data?.keys) add(gen.data.keys, "keys / half");
  if (gen?.data?.plateCutout) add(`${gen.data.plateCutout}`, "plate cutout mm");
  if (board) {
    add(board.rows + " x " + board.columns, "rows x cols");
    if (board.bbox) add(`${board.bbox[0].toFixed(1)} x ${board.bbox[1].toFixed(1)}`, "board mm");
    add(board.footprints?.choc_v1_v2 ?? 0, "switch footprints");
  }
  if (prn?.data?.files?.length) add(prn.data.files.length, "print files");
}

function renderSvgs(svgs) {
  const box = $("svgs");
  box.innerHTML = "";
  if (!svgs.length) {
    box.innerHTML = `<span class="hint">No previews yet.</span>`;
    return;
  }
  for (const s of svgs) {
    const card = document.createElement("div");
    card.className = "svgcard";
    const img = document.createElement("img");
    img.src = s.url;
    img.alt = s.name;
    img.loading = "lazy";
    const cap = document.createElement("small");
    cap.textContent = s.name;
    card.appendChild(img);
    card.appendChild(cap);
    box.appendChild(card);
  }
}

function renderFiles(res) {
  const box = $("files");
  box.innerHTML = "";
  if (!res.slug) return;
  const base = `/builds/${res.slug}`;
  const links = [
    ["config.yaml (generated)", `${base}/config.yaml`],
    ["build metadata", `${base}/meta.json`],
  ];
  for (const s of res.stages) {
    for (const f of s.data?.stls ?? []) links.push([f, `${base}/${f}`]);
    for (const p of s.data?.plates ?? []) links.push([p.plate, `${base}/out/pcbs/${p.plate}.kicad_pcb`]);
  }
  for (const [label, url] of links) {
    const a = document.createElement("a");
    a.href = url;
    a.textContent = label;
    a.target = "_blank";
    box.appendChild(a);
  }
}

// ------------------------------------------------------------------ 3D viewer
async function renderViewer(res) {
  const picker = $("stl-picker");
  picker.innerHTML = "";
  const stls = (res.stages || []).flatMap((s) => s.data?.stls ?? []);
  if (!stls.length) {
    $("viewer").innerHTML = "<span>No STL produced in this build.</span>";
    return;
  }
  for (const f of stls) {
    const b = document.createElement("button");
    b.className = "ghost";
    b.textContent = f.split("/").pop();
    b.addEventListener("click", () => showStl(`/builds/${res.slug}/${f}`));
    picker.appendChild(b);
  }
  await showStl(`/builds/${res.slug}/${stls[0]}`);
}

async function showStl(url) {
  const host = $("viewer");
  try {
    const [{ default: THREE }, { STLLoader }, { OrbitControls }] = await Promise.all([
      import("three"),
      import("three/addons/loaders/STLLoader.js"),
      import("three/addons/controls/OrbitControls.js"),
    ]);
    if (!state.viewer) {
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0d1014);
      const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 5000);
      const controls = new OrbitControls(camera, renderer.domElement);
      scene.add(new THREE.AmbientLight(0xffffff, 0.7));
      const dir = new THREE.DirectionalLight(0xffffff, 1.1);
      dir.position.set(200, -300, 400);
      scene.add(dir);
      const dir2 = new THREE.DirectionalLight(0x99bbff, 0.5);
      dir2.position.set(-300, 200, -200);
      scene.add(dir2);
      host.innerHTML = "";
      host.appendChild(renderer.domElement);
      state.viewer = { renderer, scene, camera, controls, mesh: null, THREE };
      const resize = () => {
        const w = host.clientWidth, h = host.clientHeight;
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      };
      new ResizeObserver(resize).observe(host);
      resize();
      const animate = () => {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
      };
      animate();
    }
    const { scene, camera, controls } = state.viewer;
    if (state.viewer.mesh) {
      scene.remove(state.viewer.mesh);
      state.viewer.mesh.geometry.dispose();
    }
    const buf = await (await fetch(url)).arrayBuffer();
    const geom = new STLLoader().parse(buf);
    geom.computeVertexNormals();
    const mesh = new THREE.Mesh(geom, new THREE.MeshStandardMaterial({ color: 0x8ecae6, metalness: 0.1, roughness: 0.7, flatShading: false }));
    // STLs from these scripts are in mm with the model sitting on z=0
    geom.computeBoundingBox();
    const bb = geom.boundingBox;
    const center = new THREE.Vector3();
    bb.getCenter(center);
    mesh.position.set(-center.x, -center.y, -bb.min.z);
    scene.add(mesh);
    state.viewer.mesh = mesh;
    const size = new THREE.Vector3();
    bb.getSize(size);
    const radius = Math.max(size.x, size.y, size.z);
    camera.position.set(radius * 0.9, -radius * 1.2, radius * 1.1);
    camera.near = radius / 100;
    camera.far = radius * 20;
    camera.updateProjectionMatrix();
    controls.target.set(0, 0, size.z / 2);
    controls.update();
  } catch (err) {
    host.innerHTML = `<span>3D viewer unavailable (${err.message}). The STL links below still work.</span>`;
  }
}

// ------------------------------------------------------------------ boot
async function boot() {
  const { presets } = await api("/api/presets");
  state.presets = presets;
  const sel = $("preset");
  sel.innerHTML = "";
  for (const p of presets) {
    const o = document.createElement("option");
    o.value = p.file;
    o.textContent = `${p.config.name} - ${p.config.comment ? p.config.comment.slice(0, 60) : p.file}`;
    sel.appendChild(o);
  }
  const preferred = presets.find((p) => p.config.name === "sweepyway") || presets[0];
  sel.value = preferred.file;
  state.config = preferred.config;
  sel.addEventListener("change", () => {
    const p = presets.find((x) => x.file === sel.value);
    if (!p) return;
    state.config = structuredClone(p.config);
    renderForm();
    doValidate();
  });

  $("name").addEventListener("input", () => {
    state.config.name = $("name").value;
  });
  $("btn-preview").addEventListener("click", () => build(false));
  $("btn-prints").addEventListener("click", () => build(true));
  $("btn-download").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(state.config, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${state.config.name}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  });
  $("file").addEventListener("change", async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    state.config = JSON.parse(await f.text());
    renderForm();
    doValidate();
  });

  renderForm();
  doValidate();
}

boot().catch((err) => {
  document.body.innerHTML = `<pre style="padding:20px;color:#f87171">Failed to start configurator:\n${err.stack || err}</pre>`;
});
