"""Stage 5 — motion: shots/NN.png -> shots/NN.mp4, via image-to-video diffusion.

See docs/adr/0003-motion-image-to-video-diffusion.md. Retry/fallback
behavior for diffusion failures (flicker, morphing) not yet designed.
"""


def run(image_paths: list[str]) -> list[str]:
    raise NotImplementedError
