"""ComfyUI client: local HTTP + WebSocket API.

Per ADR 0007 (docs/adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md):
ComfyUI runs on the same machine as the orchestrator, reachable at
127.0.0.1:8188. No tunnel, no auth headers.

Intended flow:
    POST /prompt              -> queue a graph, returns prompt_id
    WS   /ws?clientId=...     -> progress + completion events for that job
    GET  /view                -> retrieve the generated file

Not implemented yet — Phase 1 of BUILD_PLAN.md. See ComfyUI's own
script_examples/websockets_api_example.py for the reference client flow
before implementing this.
"""

DEFAULT_BASE_URL = "http://127.0.0.1:8188"


class ComfyClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL) -> None:
        self.base_url = base_url

    def queue_prompt(self, graph: dict) -> str:
        """POST the given API-format graph to /prompt, return its prompt_id."""
        raise NotImplementedError

    def wait_for_completion(self, prompt_id: str) -> None:
        """Block until ComfyUI's WebSocket reports this prompt_id complete."""
        raise NotImplementedError

    def fetch_output(self, prompt_id: str) -> bytes:
        """Retrieve the generated file for a completed prompt via /view."""
        raise NotImplementedError
