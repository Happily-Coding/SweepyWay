# Configurator (local web app)

Edits a JSON config, generates `ergogen/config.yaml`, runs Ergogen + the repo's check scripts,
builds the printable STLs, and shows everything in the browser (3D viewer included).

```bash
node configurator/server.mjs        # Windows; from WSL use node.exe
# -> http://localhost:5173
```

- Presets live in `presets/` (`sweepyway.json` is auto-selected; it *is* this repo's keyboard).
- Builds are content-addressed in `builds/` (gitignored): `config.yaml`, `meta.json`, `out/`
  (Ergogen), `assets/` (STLs).
- CLI equivalent of "just generate the YAML":
  `node configurator/lib/generate.mjs presets/sweepyway.json --out /tmp/sweepyway.yaml`

Full documentation, schema, endpoints and known limits: [`../docs/CONFIGURATOR.md`](../docs/CONFIGURATOR.md).
