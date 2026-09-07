# Architecture

## Pipeline stages

```
1. Trigger / queue
2. Historical grounding
3. Scene decomposition
4. Image generation        (ComfyUI, local GPU, over tunnel)
5. Motion                  (image-to-video diffusion, local GPU)
6. Narration                (TTS, first-person)
7. Assembly                 (local FFmpeg)
8. Publish / storage        (v1: land in durable storage; no upload)
```

Each stage is a distinct step orchestrated by n8n. The intent is that any
stage can be re-run in isolation given the previous stage's artifact,
without re-running the whole pipeline — see "Idempotency and resumability"
below.

### 1. Trigger / queue

A polity + period string enters the system. v1: a human triggers a single
run manually in n8n. Queueing multiple polities unattended is explicitly
future work (see [01-overview.md](01-overview.md)).

### 2. Historical grounding

Research step producing a structured brief: material culture, dress, food,
labour, built environment, daily rhythm — specifically, what a median
22-year-old man's day actually contained in that society and period. This
is the project's quality bottleneck; see
[04-grounding.md](04-grounding.md).

**Output artifact:** grounding brief (structured text/JSON — exact schema
TBD when this stage is built).

### 3. Scene decomposition

The grounding brief becomes N shots, each with an image generation prompt
and a narration line for that shot.

**Output artifact:** scene list (JSON array of `{shot_index, image_prompt,
narration_line}` or similar — exact schema TBD).

### 4. Image generation

ComfyUI running on local hardware (the author's GPU), reached from n8n
(on the VPS) over the Cloudflare Tunnel. Graphs are authored in the ComfyUI
UI, exported in **API format** (requires enabling dev mode in ComfyUI
settings), and committed to `comfy/`.

n8n drives ComfyUI with explicit HTTP Request nodes, not the
`n8n-nodes-comfyui` community node (see
[ADR 0001](adr/0001-drop-n8n-nodes-comfyui.md)):

```
POST /prompt              → queue the job, get prompt_id
Wait node (poll interval)
GET /history/{prompt_id}  → poll until the job shows complete
GET /view                 → retrieve the generated image file
```

No Midjourney-style flags (`--ar`, `--v`, etc.) in prompts — ComfyUI doesn't
parse them; they'd enter the CLIP text encoder as literal tokens. Aspect
ratio is set via the Empty Latent node's width/height. See
[ADR 0002](adr/0002-no-midjourney-syntax.md).

**Output artifact:** one still image per shot.

### 5. Motion

Turning still images into moving shots via image-to-video diffusion,
running on the local GPU (same machine as image generation). This was
chosen over programmatic camera moves (Ken Burns/parallax) for higher
visual ceiling, at the cost of longer render times and a harder failure
mode (flicker, morphing artifacts) — see
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

Local FFmpeg via an Execute Command node stitches visuals, narration,
captions, and music into the finished video(s). Chosen over a hosted video
API to keep the pipeline fully self-hosted and keep per-video cost at
compute-only — see
[ADR 0004](adr/0004-assembly-local-ffmpeg.md).

v1 produces **two renders per input, same content**: one vertical (9:16)
and one horizontal (16:9), each ~5 minutes — see
[ADR 0005](adr/0005-output-format-dual-aspect-5min.md) for why this departs
from the original short-form-vertical framing.

**Output artifact:** two finished video files.

### 8. Publish / storage

v1: output lands in durable storage (destination TBD — not yet decided
where "durable" means in practice: VPS disk, object storage, etc.).
Automated publishing to any platform is out of scope for v1.

## Cross-cutting concerns

These are meant to be designed for from the start, not retrofitted later.
None are resolved yet — this section records what needs an answer as each
stage is actually built, not the answer itself.

- **Idempotency and resumability per stage.** Each stage should be
  re-runnable from its input artifact without side effects from a prior
  partial run. Needs a convention for artifact IDs/paths keyed by run, and
  a way to detect "this stage already succeeded for this run."
- **Artifact storage between stages.** Where grounding briefs, scene lists,
  images, clips, and audio physically live between stages, and how
  downstream stages find them. Not yet decided.
- **Retry behaviour on the ComfyUI hop specifically.** The local GPU
  machine is not always on. The pipeline needs to distinguish "ComfyUI is
  unreachable right now, retry later" from "ComfyUI rejected the request,
  fail the run" — the 403 in [03-infrastructure.md](03-infrastructure.md)
  is an example of the latter that was initially mistaken for the former.
- **Cost per video.** Not yet tracked. Once TTS and any hosted components
  are chosen, this should be measurable per run.
- **Logging / stage attribution.** Enough logging to tell which stage
  produced a bad output, given that a bad final video could stem from a
  bad grounding brief, a bad prompt, a bad generation, or a bad edit
  decision in assembly. No logging convention chosen yet.
