"""Stage 4 — image generation: shots.json -> shots/NN.png, via ComfyUI.

Uses comfy.ComfyClient. No Midjourney-style flags in prompts — see
docs/adr/0002-no-midjourney-syntax.md. Aspect ratio is set via the graph's
Empty Latent Image node, not prompt text.
"""


def run(shots: list[dict]) -> list[str]:
    raise NotImplementedError
