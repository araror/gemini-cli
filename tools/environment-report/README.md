# Environment Report Builder

A small, dependency-free Python utility that turns a JSON snapshot of your
Claude / Cowork environment into a formatted Markdown report of what you are
connected to — MCP connectors (grouped by state), enabled skills, and enabled
plugins.

The snapshot is the raw output of the `ListConnectors`, `ListSkills`, and
`ListPlugins` tools; this script only formats it. It intentionally does **not**
report account usage, quota, or billing — that data is not available from a
session (check **Settings → Usage / Billing** instead).

## Usage

```bash
python3 build_report.py <input.json> [--out report.md] [--lang en|he] [--now "YYYY-MM-DD HH:MM"]
```

Options:

| Flag      | Default                  | Description                                        |
| --------- | ------------------------ | -------------------------------------------------- |
| `input`   | _(required)_             | Path to the JSON snapshot.                         |
| `--out`   | `environment_report.md`  | Output Markdown file.                              |
| `--lang`  | `en`                     | Report language: `en` (English) or `he` (Hebrew, rendered right-to-left). |
| `--now`   | current local time       | Timestamp string stamped into the report header.   |

Requires only the Python 3 standard library.

## Example

```bash
python3 build_report.py example/snapshot.example.json --out example/report.example.md
```

See [`example/snapshot.example.json`](example/snapshot.example.json) for the
expected input shape and [`example/report.example.md`](example/report.example.md)
for the generated output.

## Input format

```jsonc
{
  "connectors": [
    // "connected": true + "enabledInChat": true  -> Active (usable now)
    // "connected": true + "enabledInChat": false -> Connected but off in this chat
    // "connected" missing/false                  -> Not connected (needs auth/setup)
    { "name": "GitHub", "description": "...", "connected": true, "enabledInChat": true }
  ],
  "skills":  [ { "name": "pdf" } ],   // list of {"name": ...} objects, or plain strings
  "plugins": [ { "name": "design" } ] // list of {"name": ...} objects, or plain strings
}
```

Any of the three top-level keys may be omitted; missing sections render as
_(none)_. Within each section, entries are sorted case-insensitively by name.
