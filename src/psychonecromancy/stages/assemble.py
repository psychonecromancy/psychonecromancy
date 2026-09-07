"""Stage 7 — assembly: clips + narration + captions + music -> out/{aspect}.mp4.

Invokes FFmpeg as a direct subprocess — see
docs/adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md (supersedes the
n8n Execute Command mechanism in docs/adr/0004-assembly-local-ffmpeg.md).
Produces both aspect ratios (9:16 and 16:9) from the same shot/narration
set — see docs/adr/0005-output-format-dual-aspect-5min.md.
"""


def run(clip_paths: list[str], narration_paths: list[str]) -> dict[str, str]:
    raise NotImplementedError
