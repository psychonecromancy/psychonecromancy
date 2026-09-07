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

Documentation and repo scaffolding. No pipeline logic has shipped yet. See
[BUILD_PLAN.md](BUILD_PLAN.md) for phasing and
[docs/05-open-decisions.md](docs/05-open-decisions.md) for what's still
undecided.

The pipeline is orchestrated by a Python package
(`src/psychonecromancy/`), running natively on the GPU machine (Windows,
no WSL) alongside ComfyUI — there is no n8n and no separate VPS/tunnel in
this project's infrastructure. See
[ADR 0007](docs/adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md) for
why an earlier n8n-on-a-VPS design was cut.

## How to run it

Nothing is runnable end-to-end yet. Once Phase 1 lands, this section will
describe `psycho run "<society and period>"` and where output artifacts
land under `runs/`.

## Repo map

| Path | Contents |
|---|---|
| `docs/` | Design docs, architecture, infra runbook, ADRs |
| `src/psychonecromancy/` | The pipeline — CLI, ComfyUI client, per-stage modules |
| `runs/` | Gitignored per-run artifacts and manifest |
| `comfy/` | Exported ComfyUI graphs, API format |
| `prompts/` | Versioned system prompts for the grounding/scene-decomposition LLM calls |
| `scripts/` | Health checks, ffmpeg helpers, export tooling |
| `samples/` | Reference outputs — good and bad — for calibrating quality |

See [CLAUDE.md](CLAUDE.md) for standing conventions and context for future
work sessions on this repo.
