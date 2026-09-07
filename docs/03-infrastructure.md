# Infrastructure

## Components

| Component | Where | Notes |
|---|---|---|
| n8n | Hostinger VPS, self-hosted, v1.123.5 | Orchestrator. Source of truth is the exported JSON in `workflows/`, not the n8n canvas. |
| ComfyUI | Local machine, author's GPU | Listens on `0.0.0.0:8188`. Not always on. |
| Cloudflare Tunnel | — | Exposes local ComfyUI at `https://comfy.psychonecromancy.com` to the VPS. |
| Cloudflare Access | In front of the tunnel hostname | Zero Trust Access application. |
| Domain | `psychonecromancy.com` | Cloudflare free plan. |
| GitHub | `https://github.com/psychonecromancy` | This repo. |

## Solved: n8n → ComfyUI returns 403

**Symptom:** n8n's HTTP request to ComfyUI (via the tunnel) returns
`403 - "403: Forbidden"`. The n8n credential test against the same host
succeeds (goes green), which is misleading.

**Root cause:** ComfyUI is rejecting the request — this is not a Cloudflare
WAF or Bot Fight Mode issue (both were investigated and are irrelevant; do
not re-investigate them). By default, ComfyUI only accepts requests whose
`Origin` header matches its `Host` header, and it enforces this on
state-changing methods (`POST`/`PUT`/`PATCH`) but **not** on `GET`. That
asymmetry is exactly why the credential test (a `GET`) goes green while the
actual node execution (a `POST /prompt`) 403s.

The check is disabled entirely when ComfyUI is started with
`--enable-cors-header`.

**Fix, in order of preference:**

1. **Start ComfyUI with `--enable-cors-header`.**
   ```
   python main.py --listen --enable-cors-header
   ```
   Simplest fix. The real perimeter remains the tunnel plus Cloudflare
   Access — this only removes an Origin/Host equality check that wasn't
   providing meaningful security given the tunnel + Access setup.

2. **Keep the origin check; make the headers agree instead.** Two things,
   both required:
   - A Cloudflare Transform Rule that strips the `Origin` header on the
     way to ComfyUI. No `Origin` header means the comparison is skipped.
   - Confirm the tunnel's public hostname configuration does **not**
     override the HTTP Host Header to `localhost:8188`. That field must be
     left blank so the original public hostname is forwarded as `Host`,
     otherwise `Host` and (untouched) `Origin` will still disagree.

3. **If Cloudflare Access stays in front and neither of the above is
   used:** the VPS's *egress* IP needs a Bypass policy scoped to that
   IP as a `/32`. Get the egress IP with `curl ifconfig.me` **run from the
   VPS itself** — the IP shown in Hostinger's control panel is not
   reliable for this and has caused wasted effort before. Do not confuse
   this with a general Access bypass; scope it to the single IP.

This is recorded as solved so it is not rediscovered. Earlier
troubleshooting on this issue spent time on WAF rules and Bot Fight Mode —
both are not the cause and do not need to be revisited.

**Status:** diagnosed, fix not yet applied to the running system. Applying
one of the above (option 1 preferred) and proving a round-trip image
generation from n8n through the tunnel is Phase 1 of
[BUILD_PLAN.md](../BUILD_PLAN.md).

## Decided: no `n8n-nodes-comfyui` community node

Rejected in favor of explicit HTTP Request nodes (`POST /prompt` → poll
`GET /history/{prompt_id}` → `GET /view`). The community node hides the
polling loop and doesn't expose custom header control, which blocks
Cloudflare Access service tokens from being attached to the request. More
nodes in the n8n canvas, but every failure point is visible and
debuggable. See [ADR 0001](adr/0001-drop-n8n-nodes-comfyui.md).

## Runbook (partial — expand as the pipeline is built)

### Checking ComfyUI is reachable from the VPS
```
curl -I https://comfy.psychonecromancy.com/system_stats
```
A `GET` succeeding here does not prove `POST` will work — see the 403
writeup above.

### Getting the VPS's real egress IP (for Access bypass policies)
Run from the VPS, not from Hostinger's panel:
```
curl ifconfig.me
```

## Open infrastructure questions

- Where does durable output storage live (VPS disk, object storage,
  elsewhere)? Not decided — see
  [05-open-decisions.md](05-open-decisions.md).
- The local-GPU-behind-a-tunnel setup is fine for development, fragile for
  anything scheduled/unattended (machine sleep, home network outage, tunnel
  drop). No migration path decided yet; see
  [05-open-decisions.md](05-open-decisions.md).
