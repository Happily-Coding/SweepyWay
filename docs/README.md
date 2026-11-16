# Documentation index

Start here. Each doc answers one class of question; don't read them all.

| If you need to know… | Read |
|---|---|
| **you are a NEW agent picking this up mid-flight** | **[`HANDOFF.md`](HANDOFF.md)** — read it first, in full |
| how to work in this repo at all (agent or human) | [`../AGENTS.md`](../AGENTS.md) |
| where the project stands right now, what blocks ordering | [`STATUS.md`](STATUS.md) |
| why something is the way it is (locked choices + rationale) | [`DECISIONS.md`](DECISIONS.md) |
| the physical stack-up: heights, gaps, screws, tolerances | [`HARDWARE-STACK.md`](HARDWARE-STACK.md) |
| what to buy, how many of each, from where | [`BOM.md`](BOM.md) |
| exactly what to upload to JLCPCB (PCB, assembly, 3D print) | [`ORDER-CHECKLIST.md`](ORDER-CHECKLIST.md) |
| domain concepts, part specs, vendor limits (the facts file) | [`KEYBOARD-REFERENCE.md`](KEYBOARD-REFERENCE.md) |
| how `config.yaml` is structured and how to change it safely | [`ERGOGEN-GUIDE.md`](ERGOGEN-GUIDE.md) |
| how the build pipeline works and what each artifact is | [`PIPELINE.md`](PIPELINE.md) |
| why the 3D preview is missing pieces / how it was debugged | [`TROUBLESHOOTING-3D.md`](TROUBLESHOOTING-3D.md) |
| what comes next, and the configurator-website question | [`ROADMAP.md`](ROADMAP.md) |
| the local configurator web app (JSON → YAML → PCB → 3D) | [`CONFIGURATOR.md`](CONFIGURATOR.md) |

## 2. Uncertainty conventions

The author stepped away from this project several times and does not remember every decision.
These markers are used everywhere and are meant to be *resolved*, then removed:

- `⚠️ UNVERIFIED` — a claim taken from an external source that was **not** checked. Web search is
  available (`node tools/websearch/websearch.mjs` in the dev_agents repo — see `AGENTS.md` §4), so
  prefer verifying: when you do, replace the marker with the number and the source URL.
- `🟡 BEST-GUESS` — an inference from repo evidence (config values, notes, 3D models, CI output)
  that is probably right but was never confirmed by the author.
- `❓ OPEN` — a genuine open question that needs a human decision. Collected in
  [`STATUS.md`](STATUS.md) §7.

When a question is answered, replace the marker with the answer, the date and the source, and log
the decision in [`DECISIONS.md`](DECISIONS.md). The first verification pass (2026-11-15) already
resolved the choc plate geometry, keycap dimensions, the JLC thickness/finish options and the
"9600" material mystery — see `KEYBOARD-REFERENCE.md` §2, §3, §7.

## 3. External sources (how to check a fact)

Verified facts in these docs carry a source URL inline. To check something new:

```bash
# from anywhere; needs the dev_agents repo (key lives in its .env, never printed)
node.exe C:/a/d/dev_agents/tools/websearch/websearch.mjs search "<query>" --count 5
node.exe C:/a/d/dev_agents/tools/websearch/websearch.mjs fetch  <url> --max-chars 6000
```

Best sources, roughly in order of trust for this project:
1. **The ergogen source in `node_modules/ergogen/src`** — the only ground truth for config
   semantics (`points.js` for zones/stagger/shift, `outlines.js`, `pcbs.js`). Faster and more
   reliable than any discussion.
2. **Vendor drawings/datasheets** (Kailh, Chosfox, JLC) and KiCad footprint libraries that encode
   them (e.g. `daprice/keyboard_parts`).
3. **Reference keyboards' repos** (see "Easy to modify" links in `../README.md`).
4. **Discord — Absolem Club** (`https://discord.gg/u4QG8t52w`), the ergogen/ceoloide community.
   Great for "how do people usually do X" and for the ceoloide footprints, but it is a chat log,
   not a spec: prefer the source when they disagree.
5. Reddit r/ErgoMechKeyboards — good for physical/build experience, weak for dimensions.

### Discord access (open item)

An agent cannot join a server or hold a Discord identity, so access has to be *exported*:

- **Recommended:** run `DiscordChatExporter` (Tyrrrz) once to dump the channels that matter
  (`#ergogen`, `#help`, `#footprints`, ceoloide's channel) to JSON in a folder like
  `C:/a/d/dev_agents/discord/absolem/`, and let agents grep that corpus. Cheap, offline, no
  secrets, and re-exportable when needed.
- **Live alternative:** create a Discord application, add a **bot** to the server with
  *View Channel* + *Read Message History* and the **MESSAGE_CONTENT** privileged intent, put the
  bot token in `dev_agents/.env`, and query the REST API. Streaming an account (user) token is
  against Discord's ToS, so a bot is the only supported path.
- Either way the useful scope is small: ergogen syntax questions, ceoloide footprint usage, and
  build-fit reports. Do not index the whole server.

## 4. Historical material (do not treat as current)

These were written for past debugging efforts. They are kept because they contain real
measurements and dead ends worth not repeating, but they are **not** maintained:

- `plans/*.md` — plans for previous work sessions (3D merge variants, POS activation,
  submodule fix, hotswap BOM, tenting alignment). Reference: `TROUBLESHOOTING-3D.md` has the
  distilled current version.
- `create_full_3d_visual_v1..v11*.py` — the eleven approaches to merging the PCB GLB with the
  STL parts. v11 is the current pipeline; the rest are experiments. Results table in
  `TROUBLESHOOTING-3D.md`.
- `debugging/` — one-off scripts; paths inside may be stale.
- `research case 2025-08-03/`, `case_opnjscad/` — pre-Ergogen-exploration of case/palm rest
  shapes (OpenJSCAD experiments).
- `manualboms/` — hand-produced POS files from 2026-02-01, useful to know what a *working* POS
  looked like before the pipeline regressed.
- Root-level `*.txt` — the author's raw notes. Some are decisive (`estado_de_situacion.txt`,
  `notas teclado.txt`, `pensando sobre el tenting kit.txt`), some are scratch. Spanish.
