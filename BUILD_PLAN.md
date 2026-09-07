# Build plan

Phased. Check items off as they're actually done, not as they're started.
See [docs/05-open-decisions.md](docs/05-open-decisions.md) for decisions
that gate later phases.

## Phase 0 — Repo and docs

- [x] Create repo, directory structure
- [x] Write README.md, CLAUDE.md, BUILD_PLAN.md
- [x] Write docs/01-overview.md through docs/05-open-decisions.md
- [x] Record ADRs for decisions already made
- [x] `.env.example` and `.gitignore`, no secrets committed
- [ ] Initial commit pushed

## Phase 1 — Local Python round-trip to ComfyUI

Per [ADR 0007](docs/adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md):
n8n and the tunnel are gone, so this phase is now "prove a local round
trip," not "fix the 403."

- [x] Scaffold the `src/psychonecromancy/` package (`cli.py`, `comfy.py`,
      `manifest.py`, `stages/`)
- [x] Implement `comfy.py`: `POST /prompt`, WebSocket progress via
      `/ws?clientId=...`, `GET /history` + `GET /view` to retrieve the
      result. Written to ComfyUI's documented API but **not yet run
      against a live ComfyUI instance** — validate on the GPU machine
      before trusting it.
- [x] Implement the per-run `manifest.json` (stage status, input hash,
      output path) described in
      [docs/02-architecture.md](docs/02-architecture.md). Unlike
      `comfy.py`, this has no external dependency and has been exercised
      directly (create/load/save round-trip, cache hit/miss on input
      change, re-run on missing output, failure recording).
- [ ] Author a minimal ComfyUI graph, export it in API format to `comfy/`
- [ ] Prove one full local round trip on the actual GPU machine: CLI
      invocation → ComfyUI generates on `127.0.0.1:8188` → image saved
      under `runs/<run-id>/` — this is the step that validates `comfy.py`
      for real
- [ ] Document the actual ComfyUI startup command and any flags used in
      [docs/03-infrastructure.md](docs/03-infrastructure.md)'s runbook

## Phase 2 — Grounding and scene decomposition

- [ ] Design the grounding brief schema (see open question in
      [docs/04-grounding.md](docs/04-grounding.md))
- [ ] Build the research step (per
      [ADR 0006](docs/adr/0006-grounding-build-new-research-step.md) —
      not a reuse of the existing polity narrative pipeline)
- [ ] Build scene decomposition (brief → N shots, each with an image
      prompt and a narration line)
- [ ] Prove N coherent images generated from one input string, sharing a
      consistent grounded aesthetic
- [ ] Decide and implement how source images/composition work for both
      output aspect ratios (flagged in
      [ADR 0005](docs/adr/0005-output-format-dual-aspect-5min.md))

## Phase 3 — Narration

- [ ] Choose a TTS engine/vendor (open — see
      [docs/05-open-decisions.md](docs/05-open-decisions.md))
- [ ] Generate first-person narration audio per shot from scene text
- [ ] Validate narration timing against shot/clip length

## Phase 4 — Assembly

- [ ] Build `assemble.py`: local FFmpeg invoked as a direct subprocess,
      per [ADR 0007](docs/adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md)
      (supersedes the n8n Execute Command mechanism in
      [ADR 0004](docs/adr/0004-assembly-local-ffmpeg.md))
- [ ] Produce both output renders (9:16 and 16:9, ~5 min each) from the
      same underlying shots/narration/music
- [ ] Add captions
- [ ] Add music
- [ ] Produce first finished end-to-end video (both aspect ratios) from a
      single input string

## Phase 5 — Publishing and scheduling

- [ ] Decide durable output storage location (open — see
      [docs/03-infrastructure.md](docs/03-infrastructure.md))
- [ ] Decide publish target platform(s) given the 5-minute dual-aspect
      format (open — see
      [docs/05-open-decisions.md](docs/05-open-decisions.md))
- [ ] Automated publishing (out of scope for v1; design when reached)
- [ ] Queue processing for multiple polities unattended (out of scope for
      v1; design when reached)

## Phase 6 — Reliability, observability, cost tracking

- [ ] Idempotency/resumability per stage (see cross-cutting concerns in
      [docs/02-architecture.md](docs/02-architecture.md))
- [ ] Artifact storage convention between stages
- [ ] Retry behaviour for the ComfyUI hop specifically (local GPU machine
      not always on)
- [ ] Retry/fallback behaviour for image-to-video diffusion failures
      (flicker/morphing, per
      [ADR 0003](docs/adr/0003-motion-image-to-video-diffusion.md))
- [ ] Cost-per-video tracking
- [ ] Logging sufficient to attribute a bad output to the stage that
      produced it
- [ ] Revisit GPU dependency / migration path off the local-machine tunnel
      setup (see [docs/05-open-decisions.md](docs/05-open-decisions.md))
