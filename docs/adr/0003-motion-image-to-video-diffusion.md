# ADR 0003: Motion via image-to-video diffusion, not programmatic camera moves

**Date:** 2026-09-07
**Status:** Accepted

## Context

Turning generated stills into moving shots can be done either by applying
programmatic camera motion (Ken Burns pans/zooms, parallax layers) to
static images, or by running true image-to-video diffusion on the local
GPU. These have very different render times, output quality ceilings, and
failure modes.

## Decision

Use image-to-video diffusion on the local GPU.

## Rejected alternative

Programmatic camera moves (Ken Burns/parallax) — rejected in favor of the
higher visual ceiling of true generative motion, despite programmatic
motion being far cheaper, faster, and more deterministic.

## Consequences

- Render time per shot is substantially higher than a programmatic pan
  would be, which compounds given the output format decision (5-minute
  videos — see [ADR 0005](0005-output-format-dual-aspect-5min.md)) means
  many shots per run.
- New failure modes to handle that a programmatic pan wouldn't have:
  flicker, morphing/warping artifacts, temporal incoherence. Retry or
  fallback behavior for a shot that fails generation acceptably is not yet
  designed (tracked in [02-architecture.md](../02-architecture.md) and
  [05-open-decisions.md](../05-open-decisions.md)).
- This keeps the entire visual pipeline (stills and motion) on the same
  local-GPU dependency, which is already a known fragility — see the GPU
  dependency item in [05-open-decisions.md](../05-open-decisions.md).
