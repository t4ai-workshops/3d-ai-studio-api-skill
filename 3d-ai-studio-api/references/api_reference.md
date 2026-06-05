# 3D AI Studio API Reference

Full endpoint documentation for the 3D AI Studio REST API.

## Base URL

```
https://api.3daistudio.com
```

Override with env var `3D_AI_STUDIO_API_URL`.

## Authentication

```
Authorization: Bearer <3D_AI_STUDIO_API_KEY>
```

## Async Pattern

All generation/tool requests are async. Submit → get `task_id` → poll status.

```
POST /v1/<endpoint>/   →  { "task_id": "abc-123", "created_at": "..." }
GET  /v1/generation-request/<task_id>/status/
Poll until status is "FINISHED"  →  results[] with asset URLs
```

---

## Credit Balance

### GET /account/user/wallet/

```bash
curl https://api.3daistudio.com/account/user/wallet/ \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Response:
```json
{ "balance": "150.00" }
```

Credit expiry: purchased 365 days, promotional 31 days, refunded never.

---

## Generation Status (All Endpoints)

### GET /v1/generation-request/{task_id}/status/

```bash
curl https://api.3daistudio.com/v1/generation-request/TASK_ID/status/ \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Response:
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

Status values: `PENDING` | `IN_PROGRESS` | `FINISHED` | `FAILED`

Asset types: `3D_MODEL`, `SCALED_3D_MODEL`, `EDITED_IMAGE`, `IMAGE`, `ARCHIVE`

---

## 3D Generation

### POST /v1/3d-models/tencent/generate/rapid/

Tencent Hunyuan Rapid. Fast, text-to-3D or image-to-3D. Cost: 35 credits (+15 for PBR).

```json
{
  "prompt": "a red sports car",
  "enable_pbr": true
}
```

```json
{
  "image": "data:image/png;base64,...",
  "enable_pbr": false
}
```

### POST /v1/3d-models/tencent/generate/pro/

Tencent Hunyuan Pro. High quality with advanced controls. Cost: 60 credits (+20 PBR, +20 multi-view).

Parameters:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | No* | Text description (*required if no image) |
| `image` | string | No* | Base64 image for image-to-3D |
| `multi_view_images` | array | No | Array of `{view_type, view_image}` — view_type: front/left/right/back |
| `model` | string | No | Model version. Default: `"3.0"` |
| `enable_pbr` | boolean | No | Enable PBR textures. Default: false |
| `face_count` | integer | No | Max polygon count |
| `generate_type` | string | No | `Normal` \| `Cartoon` \| `Sculpture` |

### POST /v1/3d-models/trellis2/generate/

TRELLIS.2. Image-to-3D only. Cost: 10–50 credits.

```json
{
  "image": "data:image/png;base64,...",
  "enable_pbr": true
}
```

Also accepts `"image_url": "https://..."` instead of base64.

### POST /v1/3d-models/tripo/text-to-3d/

Tripo v3.0/v3.1. Text-to-3D. Cost: 0–120 credits.

```json
{
  "prompt": "a fantasy castle",
  "version": "v3.1",
  "enable_pbr": true
}
```

### POST /v1/3d-models/tripo/image-to-3d/

Tripo image-to-3D (v3.0/v3.1).

```json
{
  "image": "data:image/png;base64,...",
  "version": "v3.1",
  "enable_pbr": true
}
```

Also supports `multi_view_images` (2–4 images).

### POST /v1/3d-models/tripo/text-to-3d/p1/

Tripo P1 premium text-to-3D. Cost: 60–160 credits.

```json
{
  "prompt": "a detailed spaceship"
}
```

### POST /v1/3d-models/tripo/image-to-3d/p1/

Tripo P1 premium image-to-3D.

```json
{
  "image": "data:image/png;base64,..."
}
```

Also supports multi-view images.

---

## Texturing

### POST /v1/3d-models/tencent/texture-edit/

Edit/re-texture an existing 3D model using a reference image or text prompt.

```json
{
  "model_url": "https://storage.3daistudio.com/assets/model.glb",
  "prompt": "make it look like polished gold"
}
```

### POST /v1/3d-models/tripo/texture-model/

Apply textures to an existing Tripo model.

```json
{
  "model_url": "https://storage.3daistudio.com/assets/model.glb"
}
```

---

## Remeshing

### POST /v1/3d-models/tencent/topology/

Smart topology / remeshing.

```json
{
  "model_url": "https://...",
  "face_type": "triangle"
}
```

`face_type`: `triangle` (games/AR) or `quadrilateral` (modeling/animation).

### POST /v1/3d-models/tripo/convert-model/

Tripo model conversion/remesh.

```json
{
  "model_url": "https://..."
}
```

---

## Segmentation

### POST /v1/3d-models/tripo/mesh-segmentation/

Break a 3D model into semantic parts (for selective texturing, rigging prep, etc.).

```json
{
  "model_url": "https://..."
}
```

---

## Image Generation

### POST /v1/images/gemini/3/pro/generate/

Gemini 3 Pro. Cost: 10 credits/image.

```json
{
  "prompt": "a sunset over mountains",
  "count": 1
}
```

### POST /v1/images/gemini/3.1/flash/generate/

Gemini 3.1 Flash. Cost: 7 credits/image. Best speed/quality balance.

```json
{
  "prompt": "product photo of a sneaker",
  "count": 1
}
```

### POST /v1/images/gemini/2.5/flash/generate/

Gemini 2.5 Flash. Cost: 5 credits/image. Up to 4 images per request. High-volume.

```json
{
  "prompt": "a futuristic city",
  "count": 4
}
```

### POST /v1/images/seedream/v5/lite/generate/

SeeDream v5 Lite image generation.

```json
{
  "prompt": "anime style warrior"
}
```

---

## Tools

### POST /v1/tools/convert/

Convert 3D format. Cost: 10 credits.

```json
{
  "model_url": "https://...",
  "output_format": "fbx"
}
```

Supported output: `obj`, `fbx`, `stl`, `ply`

### POST /v1/tools/render/

Render 3D model to image(s) or video. Cost: 5–20 credits.

```json
{
  "model_url": "https://..."
}
```

### POST /v1/tools/repair/

Repair mesh issues, prepare for 3D printing, hollow models. Cost: 60–90 credits.

```json
{
  "model_url": "https://..."
}
```

### POST /v1/tools/optimize/

Compress and optimize GLB (Draco compression, texture compression, simplification). Cost: 10 credits.

```json
{
  "model_url": "https://..."
}
```

### POST /v1/tools/bake-texture/

Transfer textures from high-poly to retopologized mesh. Cost: 5 credits.

```json
{
  "high_poly_model_url": "https://...",
  "low_poly_model_url": "https://..."
}
```

### POST /v1/tools/calculate-volume/

Calculate volume, surface area, and material estimates at a given height. Cost: 20 credits. (Beta)

```json
{
  "model_url": "https://..."
}
```

### POST /v1/tools/image-enhance/

Upscale and enhance images, remove noise/artifacts, optionally remove background. Cost: 15–20 credits.

```json
{
  "image": "data:image/jpeg;base64,..."
}
```

### POST /v1/tools/remove-bg/

Remove image background with transparent PNG output. Cost: 3–5 credits.

```json
{
  "image": "data:image/jpeg;base64,..."
}
```

---

## Flows

### POST /v1/flow/miniature/

Transform any photo into a 3D-printable miniature figurine. Cost: 200 (fast) or 300 (default) credits.

```json
{
  "image": "data:image/png;base64,...",
  "preset": "miniature_human_full_body",
  "edition": "default"
}
```

Parameters:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | string | Yes | Base64-encoded source image |
| `preset` | string | Yes | Style preset (see below) |
| `edition` | string | No | `default` (300 cr) or `fast` (200 cr). Default: `default` |
| `2d_engine` | string | No | `v3`, `v3.1`, `v3.2`. Default: `v3` |
| `3d_engine` | string | No | `hunyuan` or `prism`. Default: `hunyuan` |
| `scale` | string | No | Named scale, ratio, or `custom`. Default: `none` |
| `scale_height_cm` | number | No | Required when `scale=custom`. Max 100cm |
| `face_count` | integer | No | 3,000–1,500,000 |
| `obj_scale_multiplier` | number | No | OBJ coordinate multiplier. Default: 1000 (mm) |

Preset options:
| Preset | Description |
|--------|-------------|
| `miniature_human_full_body` | Stylized full-body human |
| `miniature_human_bust` | Head and shoulders |
| `miniature_animal` | Animal figurine |
| `miniature_object` | Object figurine |
| `v2_miniature_human_full_body` | Improved, no pedestal |
| `v2_miniature_human_bust` | Improved, no pedestal |
| `v2_miniature_animal` | Improved, no pedestal |
| `v2_miniature_object` | Improved, no pedestal |
| `v3_miniature_human_full_body` | No pedestal, removes unprintable accessories |
| `v3_miniature_human_bust` | No pedestal |
| `v3_miniature_animal` | Preserves fur and markings |
| `v3_miniature_object` | No pedestal |
| `v3_miniature_human_full_body_crossed_arms` | Crossed arms pose |
| `v3_miniature_human_full_body_hands_on_hips` | Hands on hips pose |
| `v3_miniature_human_full_body_thumbs_up` | Thumbs up pose |
| `v3_miniature_human_full_body_hands_in_pockets` | Hands in pockets pose |
| `v3_miniature_human_full_body_arms_behind_back` | Arms behind back |
| `v3_miniature_human_full_body_waving` | Waving pose |
| `v4_miniature_human_full_body` | Preserves clothing colors, keeps original pose |
| `v4_miniature_general` | Universal — people, animals, vehicles, composites |
| `realistic_human_full_body` | Realistic full-body |
| `realistic_human_bust` | Realistic bust |
| `realistic_animal` | Realistic animal |
| `realistic_object` | Realistic object |

Scale options:
| Scale | Ratio |
|-------|-------|
| `none` | No scaling (default) |
| `z` | 1:220 |
| `n` | 1:160 |
| `tt` | 1:120 |
| `h0` | 1:87 |
| `o` | 1:48 |
| `g` | 1:22.5 |
| `1:NUMBER` | Custom ratio (e.g. `1:150`) |
| `custom` | Exact height; requires `scale_height_cm` |

Status response for miniature includes:
- `EDITED_IMAGE` — styled 2D preview image
- `3D_MODEL` — unscaled GLB
- `SCALED_3D_MODEL` — scaled GLB (when scale is set)
- `ARCHIVE` — ZIP with OBJ (when scale is set)

---

## Error Reference

| HTTP | Code | Description |
|------|------|-------------|
| 401 | `invalid_api_key` | Missing or invalid API key |
| 401 | `api_key_expired` | Key expired — create a new one |
| 401 | `api_key_revoked` | Key revoked |
| 402 | `insufficient_credits` | Purchase credits |
| 429 | `rate_limited` | 3 req/min default — wait and retry |
| 400 | `validation_failed` | Invalid or missing parameters |

## Rate Limits

- Default: 3 requests per minute
- Custom limits available via dashboard
- HTTP 429 on exceed

## Best Practices

1. Poll every 10 seconds for generation tasks (typical: 3–8 min)
2. Download results within 24 hours — URLs expire
3. Use `--wait` flag in the client for automated polling
4. On 429: wait and retry (do not retry immediately)
5. Failed jobs refund credits automatically
6. All generation outputs GLB — use Convert tool for other formats
