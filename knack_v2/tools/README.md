# Tools Layout

`knack_v2/tools/` is the local container for OpenClaw plugin roots.

Each child folder under `tools/` should be one OpenClaw plugin root.

Example:

- `tools/knack-v2/`

Each plugin root should contain:

- `openclaw.plugin.json`
- optional `package.json`
- optional `src/`
- optional `skills/`
- optional `openclaw.json.example`

This matches the OpenClaw plugin model:

- OpenClaw loads plugin directories from configured paths
- each plugin root must contain `openclaw.plugin.json`
- plugins can ship skills through their `skills/` folder
- plugin config values belong in the main OpenClaw config under `plugins.entries.<plugin-id>.config`
