"""ComfyUI client: local HTTP + WebSocket API.

Per ADR 0007 (docs/adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md):
ComfyUI runs on the same machine as the orchestrator, reachable at
127.0.0.1:8188. No tunnel, no auth headers.

Flow, matching ComfyUI's own script_examples/websockets_api_example.py:
    POST /prompt              -> queue a graph, returns prompt_id
    WS   /ws?clientId=...     -> progress + completion events for that job
    GET  /history/{prompt_id} -> output file references once complete
    GET  /view                -> retrieve a specific output file's bytes

Not yet run against a live ComfyUI instance — this follows ComfyUI's
documented/example API exactly, but validate it on the GPU machine as part
of Phase 1 (see BUILD_PLAN.md) before relying on it.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

import requests
import websocket  # from the websocket-client package

DEFAULT_BASE_URL = "http://127.0.0.1:8188"


class ComfyError(RuntimeError):
    """Raised when ComfyUI rejects a graph or reports an execution error."""


class ComfyClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, client_id: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id or uuid.uuid4().hex

    def queue_prompt(self, graph: dict[str, Any]) -> str:
        """POST the given API-format graph to /prompt, return its prompt_id."""
        resp = requests.post(
            f"{self.base_url}/prompt",
            json={"prompt": graph, "client_id": self.client_id},
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        if body.get("node_errors"):
            raise ComfyError(f"ComfyUI rejected the graph: {body['node_errors']}")
        return body["prompt_id"]

    def wait_for_completion(self, prompt_id: str, timeout: float | None = None) -> None:
        """Block until ComfyUI's WebSocket reports this prompt_id complete.

        Raises ComfyError on an execution_error message for this prompt, or
        TimeoutError if `timeout` seconds pass first.
        """
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws = websocket.WebSocket()
        ws.connect(f"{ws_url}/ws?clientId={self.client_id}", timeout=timeout)
        try:
            deadline = time.monotonic() + timeout if timeout else None
            while True:
                if deadline is not None and time.monotonic() > deadline:
                    raise TimeoutError(f"Timed out waiting for prompt {prompt_id}")
                message = ws.recv()
                if not isinstance(message, str):
                    continue  # binary frame (preview image), not a status message
                event = json.loads(message)
                payload = event.get("data", {})
                if payload.get("prompt_id") not in (None, prompt_id):
                    continue
                if event.get("type") == "executing" and payload.get("node") is None:
                    return
                if event.get("type") == "execution_error":
                    raise ComfyError(f"ComfyUI execution error for {prompt_id}: {payload}")
        finally:
            ws.close()

    def get_history(self, prompt_id: str) -> dict[str, Any]:
        """Raw /history entry for a completed prompt (node outputs, etc.)."""
        resp = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=30)
        resp.raise_for_status()
        history = resp.json()
        if prompt_id not in history:
            raise ComfyError(f"No history entry for prompt {prompt_id}")
        return history[prompt_id]

    def get_images(self, prompt_id: str) -> dict[str, list[bytes]]:
        """Fetch every image output of a completed prompt, keyed by node id."""
        outputs = self.get_history(prompt_id).get("outputs", {})
        images: dict[str, list[bytes]] = {}
        for node_id, node_output in outputs.items():
            for image_info in node_output.get("images", []):
                data = self._fetch_view(
                    filename=image_info["filename"],
                    subfolder=image_info.get("subfolder", ""),
                    file_type=image_info.get("type", "output"),
                )
                images.setdefault(node_id, []).append(data)
        return images

    def fetch_output(self, prompt_id: str) -> bytes:
        """Convenience: return the first image produced by this prompt.

        Fine for this pipeline's per-shot graphs, which are expected to
        have a single SaveImage node. Use get_images() for anything with
        multiple outputs.
        """
        for node_images in self.get_images(prompt_id).values():
            if node_images:
                return node_images[0]
        raise ComfyError(f"No image output found for prompt {prompt_id}")

    def _fetch_view(self, filename: str, subfolder: str, file_type: str) -> bytes:
        resp = requests.get(
            f"{self.base_url}/view",
            params={"filename": filename, "subfolder": subfolder, "type": file_type},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.content
