# CLAUDE.md — standing context for this repo

Read this before doing anything else in this repo. It exists so a future
session can pick this project up cold.

## What this is

Psychonecromancy: an automated pipeline that takes a single input string
naming a society and time period (e.g. `"1300's Bulgarian Empire"`) and
produces a historically grounded video of a day in the life of a
22-year-old man at the **median** socio-economic stratum of that society —
not an elite, not the destitute. That deliberate focus on the unremarkable
middle is the project's creative thesis; see
[docs/01-overview.md](docs/01-overview.md).

Full design context lives in `docs/`. Read
[docs/01-overview.md](docs/01-overview.md) through
[docs/05-open-decisions.md](docs/05-open-decisions.md) in order before
making architectural changes.

## Where things live

| Path | What |
|---|---|
| `docs/` | Overview, architecture, infra runbook, grounding approach, open decisions |
| `docs/adr/` | One file per decision made, numbered, with rejected alternatives |
| `workflows/` | Exported n8n workflow JSON — **this is the source of truth**, not the n8n canvas |
| `comfy/` | Exported ComfyUI graphs, API format (requires dev mode enabled in ComfyUI to export) |
| `prompts/` | Versioned system prompts for AI Agent nodes |
| `scripts/` | Health checks, ffmpeg helpers, export tooling |
| `samples/` | Reference outputs, good and bad, for calibrating quality |
| `BUILD_PLAN.md` | Phased plan with checkboxes — check status here before assuming what's built |

## Conventions

- **The repo is the source of truth, not the n8n canvas.** If you change
  something in the n8n UI, export it to `workflows/` and commit it. A
  change that lives only in n8n is a change that will be lost.
- **Decisions get recorded as ADRs.** One file per decision in
  `docs/adr/`, numbered, dated, including rejected alternatives and why.
  Don't silently change an architectural decision — write a new ADR or
  update the existing one and note what changed.
- **Never commit secrets.** No VPS IPs, API keys, tunnel tokens, or
  Cloudflare credentials, ever. `.env.example` holds placeholder keys only.
  Hostnames like `comfy.psychonecromancy.com` are fine to commit.
- **Prefer plain text and small files.** Docs should be readable on GitHub
  without tooling.
- **Don't invent specifics for the docs.** If something isn't decided,
  write it as an open question in
  [docs/05-open-decisions.md](docs/05-open-decisions.md), don't guess a
  plausible-sounding answer.

## Solved problems — do not re-litigate these

### n8n → ComfyUI 403 Forbidden
ComfyUI rejects requests where `Origin` doesn't match `Host`, enforced on
`POST`/`PUT`/`PATCH` but not `GET` — which is why the n8n credential test
(a GET) passes while actual node execution (a POST) 403s. This is **not**
a Cloudflare WAF or Bot Fight Mode issue; both were checked and ruled out
already. Fix: start ComfyUI with `--enable-cors-header` (preferred), or
align Origin/Host headers via a Cloudflare Transform Rule plus leaving the
tunnel's Host Header override blank, or scope an Access Bypass policy to
the VPS's actual egress IP (get it with `curl ifconfig.me` run from the
VPS, not from Hostinger's panel). Full writeup:
[docs/03-infrastructure.md](docs/03-infrastructure.md).

### Drop `n8n-nodes-comfyui`
Use explicit HTTP Request nodes (`POST /prompt` → poll
`GET /history/{id}` → `GET /view`) instead of the community node. The
community node hides the polling loop and blocks custom headers, which
blocks Cloudflare Access service tokens. See
[ADR 0001](docs/adr/0001-drop-n8n-nodes-comfyui.md).

### No Midjourney syntax in ComfyUI prompts
`--ar`, `--v`, etc. are not parsed by ComfyUI — they become literal tokens
in the CLIP text encoder and degrade conditioning. Aspect ratio is set via
the Empty Latent Image node's width/height. See
[ADR 0002](docs/adr/0002-no-midjourney-syntax.md).

## Decisions already made (don't re-ask, revisit only if the user raises it)

- Motion: image-to-video diffusion, not programmatic camera moves.
  ([ADR 0003](docs/adr/0003-motion-image-to-video-diffusion.md))
- Assembly: local FFmpeg via Execute Command, not a hosted video API.
  ([ADR 0004](docs/adr/0004-assembly-local-ffmpeg.md))
- Narration: first-person voice. TTS vendor still unchosen.
- Grounding: new project-specific research step, not a reuse of the
  existing pre-modern polity narrative pipeline.
  ([ADR 0006](docs/adr/0006-grounding-build-new-research-step.md))
- Output format: **two renders per input** — 9:16 and 16:9, ~5 minutes
  each — not a single short-form vertical video as originally framed. This
  is a real scope change from the project's original description; see
  [ADR 0005](docs/adr/0005-output-format-dual-aspect-5min.md) before
  assuming "short-form vertical" still applies anywhere in the docs or
  code.

## Still genuinely open — see docs/05-open-decisions.md

TTS vendor, publish target platform, durable output storage location, GPU
dependency migration path. Don't pick one of these unilaterally in code
without flagging it — surface the decision to the user first.

## Scope

v1 is one input string in, one pair of finished videos out (see output
format decision above), run manually, reproducibly, with every
intermediate artifact inspectable. Multi-tenant, UI, automated publishing,
scheduling, cross-video continuity, and non-English narration are
explicitly out of scope for v1 — see
[docs/01-overview.md](docs/01-overview.md).
