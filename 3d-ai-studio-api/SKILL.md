---
name: 3d-ai-studio-api
description: Interact with the 3D AI Studio API. Use when generating 3D models from text or images, creating miniature figurines, generating/editing images, using tools (convert, render, repair, optimize), or polling job status. All operations are async — submit a request, get a task_id, poll until FINISHED. Authenticates via Bearer token from env var 3D_AI_STUDIO_API_KEY.
---

# 3D AI Studio API Skill

Programmatic access to 3D AI Studio: text-to-3D, image-to-3D, AI image generation, 3D tools (convert, render, repair, optimize, bake), and the miniature figurine flow.

## Quick Start

### Environment Setup

Set your API key in `.env`:

```bash
3D_AI_STUDIO_API_KEY=your_api_key_here
```

### Core Pattern — All Operations Are Async

Every generation or tool request returns a `task_id`. Poll status until `FINISHED`.

```bash
# 1. Submit a request → get task_id
python scripts/3d_api_client.py tencent-rapid --prompt "a wooden chair" --enable-pbr

# 2. Poll status
python scripts/3d_api_client.py status --task-id <task_id>

# 3. Download results when FINISHED
python scripts/3d_api_client.py download --task-id <task_id> --output-dir ./results
```

Or use `--wait` to poll automatically:

```bash
python scripts/3d_api_client.py tencent-rapid --prompt "a wooden chair" --enable-pbr --wait --output-dir ./results
```

## Authentication

Bearer token from environment variable `3D_AI_STUDIO_API_KEY`.

```
Authorization: Bearer <your_api_key>
```

**Base URL:** `https://api.3daistudio.com`

## Available Commands

### Credit Balance

```bash
python scripts/3d_api_client.py balance
```

### 3D Generation

**Tencent Hunyuan — Rapid** (35 credits, fast)
```bash
python scripts/3d_api_client.py tencent-rapid \
  --prompt "a red sports car" \
  [--enable-pbr] \
  [--wait] [--output-dir ./results]
```

**Tencent Hunyuan — Pro** (60 credits + 20 for PBR + 20 for multi-view)
```bash
python scripts/3d_api_client.py tencent-pro \
  --prompt "a medieval sword with ornate handle" \
  [--model 3.0] \
  [--enable-pbr] \
  [--face-count 500000] \
  [--generate-type Normal|Cartoon|Sculpture] \
  [--wait] [--output-dir ./results]

# Image-to-3D
python scripts/3d_api_client.py tencent-pro \
  --image path/to/image.jpg \
  [--enable-pbr] [--wait]
```

**TRELLIS.2** (10–50 credits, image-to-3D only)
```bash
python scripts/3d_api_client.py trellis \
  --image path/to/image.jpg \
  [--enable-pbr] \
  [--wait] [--output-dir ./results]
```

**Tripo v3.0/v3.1** (0–120 credits, text or image)
```bash
python scripts/3d_api_client.py tripo \
  --prompt "a fantasy castle" \
  [--version v3.0|v3.1] \
  [--enable-pbr] \
  [--wait] [--output-dir ./results]

# Image-to-3D
python scripts/3d_api_client.py tripo \
  --image path/to/image.jpg \
  [--version v3.1] [--enable-pbr] [--wait]
```

**Tripo P1** (60–160 credits, premium)
```bash
python scripts/3d_api_client.py tripo-p1 \
  --prompt "a detailed spaceship" \
  [--wait] [--output-dir ./results]

# Image-to-3D
python scripts/3d_api_client.py tripo-p1 \
  --image path/to/image.jpg \
  [--wait]
```

### Image Generation

**Gemini 3 Pro** (10 credits/image)
```bash
python scripts/3d_api_client.py image-gemini3pro \
  --prompt "a sunset over mountains" \
  [--count 1] \
  [--wait] [--output-dir ./results]
```

**Gemini 3.1 Flash** (7 credits/image)
```bash
python scripts/3d_api_client.py image-gemini31flash \
  --prompt "product photo of a sneaker" \
  [--count 1] [--wait]
```

**Gemini 2.5 Flash** (5 credits/image, high-volume)
```bash
python scripts/3d_api_client.py image-gemini25flash \
  --prompt "a futuristic city" \
  [--count 1] [--wait]
```

**SeeDream v5 Lite** (cost varies)
```bash
python scripts/3d_api_client.py image-seedream \
  --prompt "anime style warrior" \
  [--wait]
```

### Tools

**Convert format** (10 credits)
```bash
python scripts/3d_api_client.py convert \
  --model-url "https://..." \
  --output-format obj|fbx|stl|ply \
  [--wait]
```

**Render to image/video** (5–20 credits)
```bash
python scripts/3d_api_client.py render \
  --model-url "https://..." \
  [--wait] [--output-dir ./results]
```

**Repair mesh / print prep** (60–90 credits)
```bash
python scripts/3d_api_client.py repair \
  --model-url "https://..." \
  [--wait]
```

**Optimize / compress** (10 credits)
```bash
python scripts/3d_api_client.py optimize \
  --model-url "https://..." \
  [--wait]
```

**Bake texture** (5 credits)
```bash
python scripts/3d_api_client.py bake-texture \
  --high-poly-url "https://..." \
  --low-poly-url "https://..." \
  [--wait]
```

**Remove background** (3–5 credits)
```bash
python scripts/3d_api_client.py remove-bg \
  --image path/to/image.jpg \
  [--wait] [--output-dir ./results]
```

**Image enhance** (15–20 credits)
```bash
python scripts/3d_api_client.py image-enhance \
  --image path/to/image.jpg \
  [--wait] [--output-dir ./results]
```

**Calculate volume** (20 credits, beta)
```bash
python scripts/3d_api_client.py volume \
  --model-url "https://..." \
  [--wait]
```

### Miniature Flow

Transform any photo into a 3D-printable miniature figurine (200–300 credits).

```bash
python scripts/3d_api_client.py miniature \
  --image path/to/photo.jpg \
  --preset miniature_human_full_body \
  [--edition default|fast] \
  [--scale none|h0|o|g|1:150|custom] \
  [--scale-height-cm 5.0] \
  [--wait] [--output-dir ./results]
```

**Presets:**
- `miniature_human_full_body` — stylized full-body human
- `miniature_human_bust` — head and shoulders
- `miniature_animal` — animal figurine
- `miniature_object` — object figurine
- `v2_*` / `v3_*` / `v4_*` — improved versions (no pedestal)
- `v3_miniature_human_full_body_crossed_arms` — crossed arms pose
- `v3_miniature_human_full_body_hands_on_hips` — hands on hips
- `v4_miniature_general` — universal preset (people, animals, vehicles, composites)
- `realistic_human_full_body` / `realistic_human_bust` — realistic style

**Scale options:** `none` (default), `z` (1:220), `n` (1:160), `tt` (1:120), `h0` (1:87), `o` (1:48), `g` (1:22.5), `1:NUMBER` (custom ratio), `custom` (requires `--scale-height-cm`)

### Status & Download

```bash
# Check status once
python scripts/3d_api_client.py status --task-id <task_id>

# Poll until complete
python scripts/3d_api_client.py status --task-id <task_id> --poll

# Download results
python scripts/3d_api_client.py download --task-id <task_id> --output-dir ./results
```

## Status Values

| Status | Meaning |
|--------|---------|
| `PENDING` | Queued, not yet processing |
| `IN_PROGRESS` | Currently generating |
| `FINISHED` | Complete — results array has download URLs |
| `FAILED` | Failed — credits automatically refunded |

## Status Response Format

```json
{
  "status": "FINISHED",
  "progress": 100,
  "failure_reason": null,
  "results": [
    {
      "asset": "https://storage.3daistudio.com/assets/model.glb",
      "asset_type": "3D_MODEL",
      "metadata": null
    }
  ]
}
```

Asset types: `3D_MODEL`, `SCALED_3D_MODEL`, `EDITED_IMAGE`, `IMAGE`, `ARCHIVE`

## Rate Limits

- Default: **3 requests per minute**
- HTTP 429 when exceeded — wait and retry
- Custom limits available via dashboard

## Error Codes

| Status | Code | Action |
|--------|------|--------|
| 401 | `invalid_api_key` | Check your API key |
| 401 | `api_key_expired` | Create a new key in the dashboard |
| 402 | `insufficient_credits` | Purchase credits |
| 429 | `rate_limited` | Wait and retry |
| 400 | `validation_failed` | Fix request parameters |

## Workflow Example — Full Miniature Pipeline

```bash
# 1. Check balance
python scripts/3d_api_client.py balance

# 2. Create miniature with auto-polling
python scripts/3d_api_client.py miniature \
  --image ./photo.jpg \
  --preset v3_miniature_human_full_body \
  --edition default \
  --scale h0 \
  --wait \
  --output-dir ./my_miniature
# → Downloads styled image, GLB, and scaled GLB (H0 1:87)
```

## Implementation Notes

- All endpoints output **GLB** by default; use the Convert tool for OBJ/FBX/STL/PLY
- Result URLs expire after **24 hours** — download promptly
- Poll every **10 seconds** for generation tasks (3–8 min typical)
- The `--wait` flag polls automatically and downloads on completion
- Images passed as `--image` are auto-encoded to base64 by the client
- SKILL.md is the agent-facing reference; see `references/api_reference.md` for full endpoint details
