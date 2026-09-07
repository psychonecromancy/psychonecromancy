# ADR 0002: No Midjourney-style syntax in ComfyUI prompts

**Date:** 2026-09-07
**Status:** Accepted

## Context

Midjourney-style prompt flags (`--ar 9:16`, `--v 6.0`, etc.) are a common
convention in AI image generation content and could plausibly leak into
prompts written for this project, either by habit or because an LLM
generating prompts has seen them in training data.

## Decision

Never include Midjourney-style flags in ComfyUI prompts. ComfyUI's CLIP
text encoder does not parse them — they enter as literal tokens and degrade
the conditioning instead of controlling generation. Aspect ratio is
controlled by the Empty Latent Image node's width/height parameters, not by
prompt text.

## Consequences

Prompt-writing (whether by a human or the AI Agent node producing prompts
from the grounding brief) must not assume Midjourney conventions apply.
Any prompt template or system prompt in `prompts/` should be checked for
this.
