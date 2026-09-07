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

## Phase 1 — Fix the 403, prove one image round-trip

- [ ] Apply the ComfyUI fix (`--enable-cors-header`, preferred — see
      [docs/03-infrastructure.md](docs/03-infrastructure.md))
- [ ] Rebuild the ComfyUI call in n8n as explicit HTTP Request nodes
      (`POST /prompt` → poll `GET /history/{id}` → `GET /view`), per
      [ADR 0001](docs/adr/0001-drop-n8n-nodes-comfyui.md)
- [ ] Export the working ComfyUI graph in API format to `comfy/`
- [ ] Export the working n8n workflow to `workflows/`
- [ ] Prove one full round trip: n8n triggers → ComfyUI generates over the
      tunnel → image comes back to n8n → saved as an artifact
- [ ] Document the actual polling interval / timeout values used, once
      chosen

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

- [ ] Build the local FFmpeg assembly step (Execute Command node), per
      [ADR 0004](docs/adr/0004-assembly-local-ffmpeg.md)
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
