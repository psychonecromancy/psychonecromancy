# ADR 0001: Drop `n8n-nodes-comfyui`, use explicit HTTP Request nodes

**Date:** 2026-09-07
**Status:** Superseded by [ADR 0007](0007-cut-n8n-python-orchestrator-on-gpu-box.md) —
n8n itself was dropped from this project, making the choice between n8n
node styles moot. Kept for historical record of why explicit HTTP calls
were preferred over a wrapping node, which remains true in spirit of the
Python `comfy.py` client ADR 0007 describes.

## Context

The `n8n-nodes-comfyui` community node wraps the ComfyUI job lifecycle
(queue a prompt, poll for completion, fetch the result) behind a single
node.

## Decision

Do not use it. Instead, build the ComfyUI call as explicit n8n nodes:

```
HTTP Request: POST /prompt          → get prompt_id
Wait node (poll interval)
HTTP Request: GET /history/{id}     → poll until complete
HTTP Request: GET /view             → retrieve the generated file
```

## Rejected alternative

`n8n-nodes-comfyui` community node — rejected because:
- It hides the polling loop, making failures at that stage opaque.
- It offers no custom header control on the requests it makes, which
  blocks attaching Cloudflare Access service token headers to the ComfyUI
  call — a hard requirement given Cloudflare Access sits in front of the
  tunnel (see [03-infrastructure.md](../03-infrastructure.md)).

## Consequences

More nodes in the n8n canvas and more surface area to build and maintain,
but every step of the ComfyUI interaction is individually visible and
debuggable in the n8n execution log, and custom headers (including Access
service tokens) can be attached to any of the three requests.
