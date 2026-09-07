# Infrastructure

## Components

| Component | Where | Notes |
|---|---|---|
| Orchestrator | GPU machine, Windows, native (no WSL) | Python package, `src/psychonecromancy/`. Runs the whole pipeline. |
| ComfyUI | Same GPU machine | Listens on `127.0.0.1:8188`. Reached directly by the orchestrator — no tunnel. |
| GitHub | `https://github.com/psychonecromancy` | This repo. |

**No longer part of this project's infrastructure:** the Hostinger VPS
(n8n), the Cloudflare Tunnel, the Cloudflare Zero Trust Access application
in front of it, and `psychonecromancy.com`'s DNS/WAF configuration. n8n was
dropped in favor of a Python orchestrator colocated with ComfyUI — see
[ADR 0007](adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md). The VPS
and n8n instance may still exist and run other, unrelated workflows; they
just aren't this project's concern anymore. If a domain is needed later
(e.g. for publishing or a status page), that's a separate, future decision
— not assumed to be `psychonecromancy.com` on the prior Cloudflare setup.

## Historical — no longer applicable

These are kept for the record per this repo's convention of not
re-litigating solved problems, but they describe infrastructure that no
longer exists for this project as of
[ADR 0007](adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md). Do not
spend time re-verifying or re-fixing these unless the orchestrator moves
off the GPU machine again in the future.

### n8n → ComfyUI 403 Forbidden

**Symptom:** n8n's HTTP request to ComfyUI (via the tunnel) returned
`403 - "403: Forbidden"`. The n8n credential test against the same host
succeeded (went green), which was misleading.

**Root cause:** ComfyUI was rejecting the request — not a Cloudflare WAF or
Bot Fight Mode issue (both were investigated and ruled out). By default,
ComfyUI only accepts requests whose `Origin` header matches its `Host`
header, and it enforces this on state-changing methods
(`POST`/`PUT`/`PATCH`) but not on `GET` — which is why the credential test
(a `GET`) went green while actual node execution (a `POST /prompt`) 403'd.

**Fix, had this topology been kept:**
1. Start ComfyUI with `--enable-cors-header` (disables the origin check
   entirely; the tunnel + Access remained the real perimeter).
2. Or: a Cloudflare Transform Rule stripping the `Origin` header, plus
   confirming the tunnel's public hostname config didn't override the HTTP
   Host Header to `localhost:8188` (that field needed to stay blank).
3. Or: an Access Bypass policy scoped to the VPS's actual egress IP
   (`curl ifconfig.me` run from the VPS itself, not Hostinger's panel) as
   a `/32`.

This entire problem class is eliminated by ADR 0007: with the orchestrator
and ComfyUI on the same machine, there is no tunnel, no cross-origin
request, and no Access policy in the path.

### Decided (superseded): no `n8n-nodes-comfyui` community node

Was: explicit HTTP Request nodes (`POST /prompt` → poll
`GET /history/{prompt_id}` → `GET /view`) instead of the community node,
because it hid the polling loop and blocked custom headers needed for
Cloudflare Access service tokens. Moot now that n8n itself is gone — see
[ADR 0001](adr/0001-drop-n8n-nodes-comfyui.md) (superseded) and
[ADR 0007](adr/0007-cut-n8n-python-orchestrator-on-gpu-box.md). The
underlying preference (explicit, debuggable calls over a wrapping
abstraction) carries forward into `comfy.py`.

## Runbook

### Starting ComfyUI (Windows, native)
```
python main.py --listen
```
No `--enable-cors-header` needed — the orchestrator calls
`127.0.0.1:8188` directly, so there's no cross-origin request to reject in
the first place.

### Checking ComfyUI is reachable locally
```
curl http://127.0.0.1:8188/system_stats
```

### ComfyUI's WebSocket API (for progress tracking)
`ws://127.0.0.1:8188/ws?clientId=<client_id>` pushes execution progress and
completion events for a queued prompt. See ComfyUI's
`script_examples/websockets_api_example.py` for the reference
client-side flow. This is what `comfy.py` is meant to use instead of
polling `/history/{prompt_id}` on a timer — see
[02-architecture.md](02-architecture.md).

## Open infrastructure questions

- Where does durable output storage live (the GPU machine's disk long
  term, external drive, object storage, elsewhere)? Not decided.
- The pipeline now depends on one Windows machine being on and awake for
  any run — simpler than the tunnel setup, but still a single point of
  failure for anything scheduled/unattended. No migration path off a
  single workstation decided yet; see
  [05-open-decisions.md](05-open-decisions.md). Not a v1 concern
  (scheduling is out of scope for v1 per
  [01-overview.md](01-overview.md)).
