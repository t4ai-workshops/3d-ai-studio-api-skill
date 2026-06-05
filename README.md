# 3D AI Studio API Skill

<br>

[![Windows](https://img.shields.io/badge/Windows-supported-blue.svg)](#supported-platforms)
[![macOS](https://img.shields.io/badge/macOS-supported-blue.svg)](#supported-platforms)
[![Linux](https://img.shields.io/badge/Linux-supported-blue.svg)](#supported-platforms)

[![Claude Code](https://img.shields.io/badge/Claude_Code-supported-blueviolet.svg)](#supported-agents)
[![Cursor](https://img.shields.io/badge/Cursor-supported-blueviolet.svg)](#supported-agents)
[![Codex](https://img.shields.io/badge/Codex-supported-blueviolet.svg)](#supported-agents)
[![opencode](https://img.shields.io/badge/opencode-supported-blueviolet.svg)](#supported-agents)
[![Hermes Agent](https://img.shields.io/badge/Hermes_Agent-supported-blueviolet.svg)](#supported-agents)
[![Gemini](https://img.shields.io/badge/Gemini-supported-blueviolet.svg)](#supported-agents)
[![Antigravity](https://img.shields.io/badge/Antigravity-supported-blueviolet.svg)](#supported-agents)
[![Kiro](https://img.shields.io/badge/Kiro-supported-blueviolet.svg)](#supported-agents)

An agent skill for the [3D AI Studio API](https://www.3daistudio.com/Platform/API). Gives Claude and Hermes agents programmatic access to 3D model generation, AI image generation, 3D tools, and the miniature figurine flow.

## What This Skill Does

- **3D Generation** — text-to-3D and image-to-3D via Tencent Hunyuan (Rapid & Pro), TRELLIS.2, Tripo v3, and Tripo P1
- **Image Generation** — Gemini 3 Pro, Gemini 3.1 Flash, Gemini 2.5 Flash, SeeDream v5 Lite
- **3D Tools** — format conversion, rendering, mesh repair, optimization, texture baking, volume calculation
- **Image Tools** — background removal, image enhance & upscale
- **Miniature Flow** — transform any photo into a 3D-printable figurine (200–300 credits)
- **Credit Balance** — check available credits at any time

All API operations are asynchronous: submit a request, receive a `task_id`, poll until `FINISHED`.

## Repository Structure

```
3d-ai-studio-api-skill/
├── README.md
├── CHANGELOG.md
├── 3d-ai-studio-api/
│   ├── SKILL.md                    # Agent-facing skill documentation
│   ├── scripts/
│   │   ├── 3d_api_client.py        # Python CLI client (all endpoints)
│   │   ├── 3d_api.sh               # Bash wrapper
│   │   └── requirements.txt
│   └── references/
│       ├── api_reference.md        # Full endpoint & parameter reference
│       ├── examples.md             # Workflow examples
│       └── setup.md                # Setup and troubleshooting guide
└── dist/
    └── 3d-ai-studio-api.skill      # Packaged skill bundle
```

## Setup

### 1. Install Python dependencies

```bash
pip install -r 3d-ai-studio-api/scripts/requirements.txt
```

### 2. Configure your API key

Create a `.env` file in your workspace root:

```env
3D_AI_STUDIO_API_KEY=your_api_key_here
```

Get your API key from the [3D AI Studio API Dashboard](https://www.3daistudio.com/Platform/API#api-keys).

> The key is only shown once at creation — store it securely. Never commit `.env` to version control.

### 3. Verify the setup

```bash
python 3d-ai-studio-api/scripts/3d_api_client.py balance
# → {"balance": "150.00"}
```

## Quick Usage Examples

```bash
# Generate a 3D model from text (Tencent Rapid, 35 credits)
python scripts/3d_api_client.py tencent-rapid \
  --prompt "a wooden chair" --enable-pbr --wait --output-dir ./models

# Photo → 3D miniature figurine (300 credits)
python scripts/3d_api_client.py miniature \
  --image ./portrait.jpg \
  --preset v3_miniature_human_full_body \
  --scale h0 \
  --wait --output-dir ./miniature

# Image-to-3D with TRELLIS.2 (10–50 credits)
python scripts/3d_api_client.py trellis \
  --image ./product.png --enable-pbr --wait

# Convert GLB to STL (10 credits)
python scripts/3d_api_client.py convert \
  --model-url "https://storage.3daistudio.com/assets/model.glb" \
  --output-format stl --wait

# Check credit balance
python scripts/3d_api_client.py balance
```

## API Base URL

```
https://api.3daistudio.com
```

## Authentication

All requests use a Bearer token:

```
Authorization: Bearer YOUR_API_KEY
```

The client reads this automatically from `3D_AI_STUDIO_API_KEY` in your `.env`.

## Rate Limits

The default rate limit is **3 requests per minute**. The client handles `429` responses — wait and retry. Custom limits can be configured through the dashboard.

## Credit System

Every generation request costs credits. Credits are prepaid and valid for 365 days from purchase. Failed jobs are automatically refunded. Check your balance with:

```bash
python scripts/3d_api_client.py balance
```

## Available Commands

| Command | Description | Credits |
|---------|-------------|---------|
| `balance` | Check credit balance | — |
| `status` | Poll task status | — |
| `download` | Download finished task results | — |
| `tencent-rapid` | Tencent Hunyuan Rapid text/image-to-3D | 35 |
| `tencent-pro` | Tencent Hunyuan Pro text/image-to-3D | 60–100 |
| `trellis` | TRELLIS.2 image-to-3D | 10–50 |
| `tripo` | Tripo v3.0/v3.1 text/image-to-3D | 0–120 |
| `tripo-p1` | Tripo P1 premium text/image-to-3D | 60–160 |
| `image-gemini3pro` | Gemini 3 Pro image generation | 10/image |
| `image-gemini31flash` | Gemini 3.1 Flash image generation | 7/image |
| `image-gemini25flash` | Gemini 2.5 Flash image generation | 5/image |
| `image-seedream` | SeeDream v5 Lite image generation | varies |
| `convert` | Convert 3D format (GLB → OBJ/FBX/STL/PLY) | 10 |
| `render` | Render 3D model to image/video | 5–20 |
| `repair` | Repair mesh / 3D print prep | 60–90 |
| `optimize` | Compress and optimize GLB | 10 |
| `bake-texture` | Transfer textures high-poly → low-poly | 5 |
| `remove-bg` | Remove image background | 3–5 |
| `image-enhance` | Upscale and enhance image | 15–20 |
| `volume` | Calculate volume & material estimates (beta) | 20 |
| `miniature` | Photo → 3D-printable miniature figurine | 200–300 |

## Further Documentation

- [`3d-ai-studio-api/SKILL.md`](3d-ai-studio-api/SKILL.md) — full skill reference for agents
- [`3d-ai-studio-api/references/api_reference.md`](3d-ai-studio-api/references/api_reference.md) — all endpoints, parameters, and response formats
- [`3d-ai-studio-api/references/examples.md`](3d-ai-studio-api/references/examples.md) — workflow examples and pipeline patterns
- [`3d-ai-studio-api/references/setup.md`](3d-ai-studio-api/references/setup.md) — setup and troubleshooting
