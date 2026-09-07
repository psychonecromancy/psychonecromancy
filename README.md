# Psychonecromancy

An automated pipeline that turns a single input string naming a society and
time period — e.g. `"1300's Bulgarian Empire"` — into a finished
historically-grounded short depicting a day in the life of a 22-year-old man
at the **median** socio-economic stratum of that society.

Most historical content depicts elites or the destitute, because those are
the people the sources talk about. This project deliberately targets the
unremarkable middle, and most of the engineering effort exists to make that
middle *accurate* rather than generic.

The system is meant to run unattended: feed it a queue of polities, get
videos out, no human opens a video editor.

## Status

Documentation and repo scaffolding only. No pipeline code has been written
yet. See [BUILD_PLAN.md](BUILD_PLAN.md) for phasing and
[docs/05-open-decisions.md](docs/05-open-decisions.md) for what's still
undecided.

Current blocker (diagnosed, not yet fixed in the running system): n8n's call
to ComfyUI returns `403 - "403: Forbidden"`. Root cause and fix options are
written up in [docs/03-infrastructure.md](docs/03-infrastructure.md).

## How to run it

Nothing is runnable end-to-end yet. Once Phase 1 lands, this section will
describe how to trigger the n8n workflow and where output artifacts land.

## Repo map

| Path | Contents |
|---|---|
| `docs/` | Design docs, architecture, infra runbook, ADRs |
| `workflows/` | Exported n8n workflow JSON (source of truth, not the n8n UI) |
| `comfy/` | Exported ComfyUI graphs, API format |
| `prompts/` | Versioned system prompts used by AI Agent nodes |
| `scripts/` | Health checks, ffmpeg helpers, export tooling |
| `samples/` | Reference outputs — good and bad — for calibrating quality |

See [CLAUDE.md](CLAUDE.md) for standing conventions and context for future
work sessions on this repo.
