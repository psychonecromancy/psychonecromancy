# Open decisions

Living document. Update this file when a decision below is revisited —
don't just edit silently; if a decision changes, write a new ADR noting
what changed and why, and update the status here.

## Decided

### Motion approach
**Decision:** Image-to-video diffusion on the local GPU, not programmatic
camera moves (Ken Burns/parallax).
**Trade-off accepted:** Higher visual ceiling, at the cost of longer render
times and a harder failure mode (flicker, morphing artifacts) than a
deterministic pan/zoom would have. Retry/fallback behavior for repeated
diffusion failure on a shot is not yet designed — flagged in
[02-architecture.md](02-architecture.md).
See [ADR 0003](adr/0003-motion-image-to-video-diffusion.md).

### Assembly layer
**Decision:** Local FFmpeg via an n8n Execute Command node, not a hosted
video API.
**Trade-off accepted:** Full control and no per-video marginal cost;
captions, transitions, and timing logic are the project's own
responsibility to build rather than solved by a vendor.
See [ADR 0004](adr/0004-assembly-local-ffmpeg.md).

### Narration
**Decision:** First-person narration ("I wake before dawn..."), not
third-person documentary or on-screen-text-only.
**Trade-off accepted:** More immersive and better suited to short-form
convention, but riskier for hedging historical uncertainty — a first-person
voice states things as lived fact where a third-person documentary voice
could hedge ("a man in his position would typically..."). The grounding
brief (see [04-grounding.md](04-grounding.md)) needs to support enough
interiority/specificity for this to work.
**Still open:** TTS engine/vendor is not chosen. Needs a decision before
Phase 3.

### Grounding source
**Decision:** Build a research step specific to this project rather than
reuse/adapt the existing pre-modern polity narrative pipeline.
See [04-grounding.md](04-grounding.md) for reasoning.

### Target length and platform
**Decision:** v1 produces **two renders per input, same content**: one
vertical (9:16) and one horizontal (16:9), each approximately **5
minutes**.
**Note — this revises the original brief.** The initial project framing
(and the working title "short-form vertical video") assumed a single
short-form vertical output (~30-90s, one platform target). Producing two
5-minute videos in different aspect ratios is a materially larger scope per
run: roughly 5-10x the runtime of a typical short, and dual-aspect delivery
means either two separate edits or an edit designed to reflow between 9:16
and 16:9 safely (title-safe/action-safe framing for both from the same
source images/clips). This has real implications for:
- Image generation: source images/compositions need to work in both crops,
  or two image sets are needed per shot.
- Render time and cost per video, given motion is image-to-video diffusion
  (see above) — a 5-minute video is many more shots than a 30-second one.
- Which platforms this is actually for, since "short-form" (YouTube
  Shorts/TikTok/Reels) does not fit 5-minute content. Not yet decided where
  a 5-minute video is meant to be published — flagged as still open below.
See [ADR 0005](adr/0005-output-format-dual-aspect-5min.md).

## Still open

### Publish target platform
5-minute dual-aspect output doesn't fit the Shorts/TikTok/Reels form factor
implied by the original brief. Where this is actually meant to go
(YouTube long-form, other) is not decided. Doesn't block v1 (publishing is
out of scope for v1 per [01-overview.md](01-overview.md)), but should be
settled before Phase 5.

### TTS vendor/engine
Narration style is decided (first-person); which TTS service or local
model produces it is not.

### GPU dependency
The pipeline depends on a home machine, behind a Cloudflare Tunnel, being
awake and reachable whenever a run needs image generation or
image-to-video diffusion. This is acceptable for development but is a
single point of failure for anything scheduled or unattended (the
project's own longer-term goal, per the top-level project description).
**Not decided:** at what point this needs to move to always-on GPU
infrastructure (e.g. a rented GPU instance), and what that migration would
require of the ComfyUI-calling code (mainly: does it stay HTTP-based
against `/prompt`, `/history`, `/view`, in which case migration is mostly a
hostname/auth change, or does switching providers require a different
integration entirely). Revisit this once Phase 1 is proven and before any
work on Phase 5/6 (scheduling, reliability) begins.

### Durable output storage
Where finished videos and intermediate artifacts actually live once
produced (VPS disk, object storage, elsewhere) is not decided. Flagged in
[03-infrastructure.md](03-infrastructure.md).
