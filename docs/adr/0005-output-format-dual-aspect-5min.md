# ADR 0005: Output format is two ~5-minute renders (9:16 and 16:9), not a single short-form vertical video

**Date:** 2026-09-07
**Status:** Accepted

## Context

The original project framing (and its working description, "short-form
vertical video") assumed a single vertical output in the ~30-90 second
range, aimed at a short-form platform (YouTube Shorts/TikTok/Reels). When
asked to confirm target length and platform for v1 during repo
bootstrapping, the actual answer given was different from that framing.

## Decision

v1 targets **two renders per input, same content**: one vertical (9:16)
and one horizontal (16:9), each approximately **5 minutes** long.

## Rejected alternative

A single ~30-90 second vertical-only output matching the original
short-form framing — superseded by the answer above.

## Consequences

This is a materially larger scope per run than the original framing, and
several parts of the architecture that assumed "short-form vertical" need
to account for it instead:

- **Image generation and composition:** source images/shots need to work
  in both a 9:16 and a 16:9 crop, or two image sets are generated per shot.
  Not yet decided which — flagged in
  [05-open-decisions.md](../05-open-decisions.md).
- **Shot count and render time:** a 5-minute video requires many more shots
  than a 30-second short, which directly multiplies image-to-video
  diffusion time (see [ADR 0003](0003-motion-image-to-video-diffusion.md))
  and therefore cost and wall-clock time per run.
- **Assembly:** FFmpeg assembly (see
  [ADR 0004](0004-assembly-local-ffmpeg.md)) needs to produce two edits
  from the same underlying content rather than one.
- **Publish target:** "short-form platform" no longer describes where a
  5-minute video would go. Not decided — flagged in
  [05-open-decisions.md](../05-open-decisions.md). Doesn't block v1 since
  publishing itself is out of scope, but affects what "finished video"
  should optimize for (e.g. YouTube long-form retention conventions vs.
  short-form hook conventions).

This ADR exists specifically to flag that the scope changed from the
original brief, so a future session doesn't assume the "short-form
vertical" framing still holds.
