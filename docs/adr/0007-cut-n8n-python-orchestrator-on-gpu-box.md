# ADR 0007: Cut n8n; orchestrate as a Python package colocated with the GPU

**Date:** 2026-09-07
**Status:** Accepted. Supersedes
[ADR 0001](0001-drop-n8n-nodes-comfyui.md) and
[ADR 0004](0004-assembly-local-ffmpeg.md).

## Context

n8n, running on a Hostinger VPS, was the orchestrator, while ComfyUI runs on
a separate machine (the GPU box) reached over a Cloudflare Tunnel. Nearly
all infrastructure effort so far went into that split: Cloudflare Tunnel
configuration, a Zero Trust Access application, Transform Rules, WAF/Bot
Fight Mode investigation (both ruled out and irrelevant), and the
Origin/Host header 403 documented in
[docs/03-infrastructure.md](../03-infrastructure.md). None of that
complexity is inherent to the project — it exists solely because the
orchestrator and the GPU live on different machines.

Looking at where the pipeline's work actually wants to happen: image
generation and image-to-video diffusion need the GPU. FFmpeg assembly
needs to sit next to the (potentially 60+ per run, at 5 minutes output)
clips that come off the GPU. LLM grounding/scene-decomposition calls and
TTS calls are outbound HTTPS and work from anywhere. There is exactly one
machine everything wants to be near, and n8n's VPS isn't it.

Beyond the topology problem, n8n has costs specific to this project:
- Binary artifacts (images, video clips, audio) moving through n8n
  execution data is a poor fit at this volume, even in filesystem binary
  mode.
- The assembly stage is already "shell out to FFmpeg" via an Execute
  Command node — n8n was adding no value there beyond being a worse shell.
- This repo already commits to the workflow JSON export as source of truth
  (per top-level `CLAUDE.md` conventions). n8n's export format is close to
  unreviewable in a diff, which cuts against that convention's purpose.
- Development on this project happens through Claude Code, which is far
  more effective writing and refactoring Python than surgically editing a
  visual workflow graph's JSON.

## Decision

Drop n8n entirely, for this project. Replace it with a Python package
living in this repo, running natively on the GPU machine (Windows,
confirmed no WSL2 — orchestrator and ComfyUI both run directly on Windows,
not inside a Linux subsystem).

- ComfyUI is reached at `127.0.0.1:8188`. No tunnel, no Cloudflare Access,
  no origin-header workaround needed — the 403 investigation in
  [docs/03-infrastructure.md](../03-infrastructure.md) is retained for the
  historical record but no longer describes live infrastructure.
- The orchestrator queues ComfyUI jobs via `POST /prompt` and tracks
  progress via ComfyUI's WebSocket endpoint (`/ws?clientId=...`), which
  pushes execution progress and completion events — rather than polling
  `GET /history/{prompt_id}` on a timer, which was the only option
  available to n8n's HTTP Request nodes. ComfyUI ships a
  `websockets_api_example.py` in `script_examples/` as a starting point.
  Final output is still retrieved via `GET /view`.
- Assembly (FFmpeg) is invoked as a direct subprocess call from the
  orchestrator, not an n8n Execute Command node.
- Proposed package layout:
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
- Resumability is a per-run `manifest.json`: each stage's output is
  considered valid if it exists and the hash of its recorded input still
  matches. A stage is re-run only if that check fails. This is the
  mechanism that handles "the GPU machine went idle/slept partway through
  a run" — previously a genuinely awkward case for n8n given the tunnel
  dependency, now just an interrupted-and-resumed local process.

## Rejected alternatives

- **Keep n8n, fix the 403, and move on.** Rejected: this fixes the
  symptom (one specific 403) while leaving the actual cause (orchestrator
  and GPU on different machines, connected by a tunnel and an Access
  policy) in place as a standing source of fragility and future
  troubleshooting.
- **Keep n8n but move it onto the GPU machine too.** Rejected: this
  removes the tunnel but keeps every other cost listed above (binary
  artifact handling, unreviewable JSON diffs, poor fit with Claude-Code
  driven development) for no remaining benefit specific to this project.
- **Adopt a general workflow orchestration framework (Prefect, Dagster, or
  similar) instead of a bespoke Python package.** Rejected for now: these
  solve real problems at multi-user, multi-schedule scale. Adopting one on
  day one, before there is a working pipeline to orchestrate, would repeat
  the same mistake as n8n — paying a framework tax before it's earned.

## Consequences

**Lost, and not free:**
- Execution history UI. Replaced by the run manifest plus structured
  per-stage logs; this is a real loss of at-a-glance visibility into what
  failed where, mitigated but not fully replaced by the manifest.
- Built-in credential storage. Replaced by `.env` (see `.env.example`).
- Built-in scheduler. Replaced by cron / a systemd timer / Windows Task
  Scheduler, if and when scheduling is built — out of scope for v1
  regardless (see [docs/01-overview.md](../01-overview.md)).
- Easy webhook triggers. Only matters if a non-CLI way to queue topics is
  wanted later; addable as a thin front-end without reintroducing n8n.

**Not lost:** all external integrations (LLM calls, TTS, eventual
publishing/upload) are plain outbound HTTPS and are unaffected by dropping
n8n.

**Gained:**
- The entire Cloudflare Tunnel / Zero Trust Access / Transform Rule
  troubleshooting surface stops being part of this project's
  infrastructure.
- WebSocket-based progress tracking instead of timer-based polling.
- Pipeline logic lives in reviewable, diffable Python instead of an
  exported workflow graph.

**Scope note:** the VPS and n8n instance are not being decommissioned —
they may still run other, unrelated workflows. They simply stop being part
of Psychonecromancy.

This also changes Phase 1 of [BUILD_PLAN.md](../../BUILD_PLAN.md) from
"prove a round trip through the tunnel" to "prove a local round trip from
Python to ComfyUI on the same machine" — a substantially easier bar to
clear.
