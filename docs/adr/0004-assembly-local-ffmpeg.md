# ADR 0004: Assembly via local FFmpeg, not a hosted video API

**Date:** 2026-09-07
**Status:** Superseded by [ADR 0007](0007-cut-n8n-python-orchestrator-on-gpu-box.md) —
the conclusion (local FFmpeg, not a hosted API) still holds and carries
forward into ADR 0007; only the invocation mechanism changed, from an n8n
Execute Command node to a direct subprocess call from the Python
orchestrator.

## Context

The final assembly stage needs to stitch generated video clips, narration
audio, captions, and music into finished output video(s). This can be done
with a hosted video-editing API (captions/transitions/timing solved by a
vendor) or with FFmpeg run locally, driven from n8n via an Execute Command
node.

## Decision

Use local FFmpeg via an n8n Execute Command node.

## Rejected alternative

A hosted video API — rejected to keep the pipeline fully self-hosted (no
new external dependency or per-video vendor cost) and because the project
explicitly wants every intermediate artifact inspectable, which is more
natural to guarantee when assembly is a local, scriptable step.

## Consequences

- Captions, transitions, and timing logic are this project's own code to
  write and maintain, not a vendor feature.
- No per-video assembly cost beyond local compute.
- Assembly logic needs to be built to reflow correctly for both output
  aspect ratios (see [ADR 0005](0005-output-format-dual-aspect-5min.md)) —
  a hosted API might have handled multi-aspect delivery natively; this now
  needs to be designed explicitly.
