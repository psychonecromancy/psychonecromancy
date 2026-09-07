# Architecture

## Orchestration

The pipeline is a Python package (`src/psychonecromancy/`) running
natively on the same machine as ComfyUI — a Windows GPU box, no WSL. There
is no separate orchestrator host and no n8n; see
[ADR 0007](adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md) for why.

Proposed layout:
```
src/psychonecromancy/
  cli.py           # psycho run "1300s Bulgarian Empire"
  comfy.py         # ComfyUI client (HTTP + WebSocket)
  stages/
    ground.py      # LLM research      -> brief.json
    script.py      # brief             -> shots.json
    images.py      # shots             -> shots/NN.png
    motion.py      # i2v               -> shots/NN.mp4
    voice.py       # TTS               -> narration/NN.wav
    assemble.py    # ffmpeg            -> out/{aspect}.mp4
runs/<run-id>/      # gitignored artifacts + manifest.json
```

A run is triggered from the CLI with the input string. Queueing multiple
polities unattended is future work (see
[01-overview.md](01-overview.md)) and would sit in front of this same
package (a cron job, a systemd timer, or Windows Task Scheduler calling
the CLI in a loop) rather than requiring a different orchestration
mechanism.

## Pipeline stages

```
1. Trigger            (CLI invocation)
2. Historical grounding
3. Scene decomposition
4. Image generation        (ComfyUI, local — same machine)
5. Motion                  (image-to-video diffusion, same machine)
6. Narration                (TTS, first-person)
7. Assembly                 (direct FFmpeg subprocess)
8. Publish / storage        (v1: land in durable storage; no upload)
```

Each stage is a Python module under `stages/` taking the previous stage's
artifact as input and producing its own artifact under `runs/<run-id>/`.
Any stage should be re-runnable in isolation given its input artifact —
see "Idempotency and resumability" below.

### 1. Trigger

`psycho run "<society and period>"` starts a new run, or resumes an
existing one if invoked again for a run that didn't complete (see
resumability below). v1 is single-run, human-triggered, no queue.

### 2. Historical grounding

Research step producing a structured brief: material culture, dress, food,
labour, built environment, daily rhythm — specifically, what a median
22-year-old man's day actually contained in that society and period. This
is the project's quality bottleneck; see
[04-grounding.md](04-grounding.md).

**Output artifact:** `brief.json` (exact schema TBD when this stage is
built).

### 3. Scene decomposition

The grounding brief becomes N shots, each with an image generation prompt
and a narration line for that shot.

**Output artifact:** `shots.json` (exact schema TBD).

### 4. Image generation

`comfy.py` drives ComfyUI over its local HTTP + WebSocket API:

```
POST /prompt                 → queue the job, get prompt_id
WS   /ws?clientId=...        → receive progress/completion events
GET  /view                   → retrieve the generated image file
```

This replaces polling `GET /history/{prompt_id}` on a timer (the only
option available when n8n's HTTP Request nodes were driving ComfyUI) with
ComfyUI's own push-based progress notifications. ComfyUI's
`script_examples/websockets_api_example.py` is the reference for this.

Graphs are authored in the ComfyUI UI, exported in **API format** (requires
enabling dev mode in ComfyUI settings), and committed to `comfy/`.

No Midjourney-style flags (`--ar`, `--v`, etc.) in prompts — ComfyUI doesn't
parse them; they'd enter the CLIP text encoder as literal tokens. Aspect
ratio is set via the Empty Latent node's width/height. See
[ADR 0002](adr/0002-no-midjourney-syntax.md).

**Output artifact:** one still image per shot.

### 5. Motion

Turning still images into moving shots via image-to-video diffusion,
running on the same GPU. Chosen over programmatic camera moves (Ken
Burns/parallax) for higher visual ceiling, at the cost of longer render
times and a harder failure mode (flicker, morphing artifacts) — see
[ADR 0003](adr/0003-motion-image-to-video-diffusion.md). Retry/fallback
behavior for this stage (e.g. falling back to a static pan on repeated
diffusion failure) is not yet designed.

**Output artifact:** one video clip per shot.

### 6. Narration

TTS over the scene text, first-person point of view (the median man
narrating his own day). TTS engine is not yet chosen — see
[05-open-decisions.md](05-open-decisions.md).

**Output artifact:** one narration audio file per shot (or one file for the
whole video, TBD when this stage is built).

### 7. Assembly

`assemble.py` invokes FFmpeg directly as a subprocess to stitch visuals,
narration, captions, and music into the finished video(s) — no workflow
engine in between. Chosen over a hosted video API to keep the pipeline
fully self-hosted and keep per-video cost at compute-only; see
[ADR 0004](adr/0004-assembly-local-ffmpeg.md) (superseded in mechanism, not
conclusion, by [ADR 0007](adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md)).

v1 produces **two renders per input, same content**: one vertical (9:16)
and one horizontal (16:9), each ~5 minutes — see
[ADR 0005](adr/0005-output-format-dual-aspect-5min.md) for why this departs
from the original short-form-vertical framing.

**Output artifact:** two finished video files.

### 8. Publish / storage

v1: output lands in durable storage (destination TBD — not yet decided
where "durable" means in practice). Automated publishing to any platform
is out of scope for v1.

## Cross-cutting concerns

### Idempotency and resumability

Each run has a `manifest.json` under `runs/<run-id>/` recording, per
stage: status, a hash of its recorded input, and its output path. Running
`psycho run` again for an existing run re-executes a stage only if its
output is missing or its input hash no longer matches what's recorded —
otherwise the stage is skipped and its existing output is reused. This is
the mechanism that handles the GPU machine going idle or the process being
interrupted partway through a run: re-invoking the CLI resumes rather than
restarts.

### Artifact storage between stages

Artifacts live under `runs/<run-id>/` on the GPU machine's local disk,
gitignored. Where finished videos move to for durable storage is a
separate, still-open decision — see
[03-infrastructure.md](03-infrastructure.md).

### Retry behaviour on the ComfyUI hop

With the orchestrator and ComfyUI on the same machine (see
[ADR 0007](adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md)), this is no
longer a network/tunnel reliability question. It's now: does the pipeline
distinguish "ComfyUI process isn't running" (fail fast, clear error) from
"a generation job failed" (retry the job, or fail that shot without
aborting the whole run)? Not yet designed.

### Cost per video

Not yet tracked. Once TTS and any hosted components are chosen, this
should be measurable per run.

### Logging / stage attribution

Enough logging to tell which stage produced a bad output, given that a bad
final video could stem from a bad grounding brief, a bad prompt, a bad
generation, or a bad edit decision in assembly. Structured per-stage logs
plus the run manifest are intended to cover this, replacing n8n's
execution history UI (a real loss — see
[ADR 0007](adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md)); exact log
format not yet designed.
