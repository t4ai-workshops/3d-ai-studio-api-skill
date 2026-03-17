---
name: 3d-ai-studio-api
description: Interact with 3D AI Studio API from agents. Use when starting 3D generation jobs, polling job status, or fetching results. Supports miniature flow, 3D object generation, and lithophane/customization workflows. Authenticates via Bearer token from env. Scope v1 includes job creation, status polling, and result retrieval.
---

# 3D AI Studio API Skill

Integrate 3D AI Studio API calls into your workflows. This skill provides authenticated access to job creation, status polling, and result fetching.

## Quick Start

### Environment Setup

Set your API key in `.env`:

```bash
3D_AI_STUDIO_API_KEY=your_bearer_token_here
```

The skill reads this key automatically.

### Core Operations

**1. Start a miniature generation job**

```bash
python scripts/3d_api_client.py start-miniature \
  --description "A golden retriever statue, 10cm tall" \
  --style "realistic" \
  --output-format gltf
```

**2. Poll job status**

```bash
python scripts/3d_api_client.py status --job-id abc-123-def
```

**3. Fetch results**

```bash
python scripts/3d_api_client.py fetch-result --job-id abc-123-def --output-dir ./results
```

## Authentication

The skill uses **Bearer token authentication** from the environment variable `3D_AI_STUDIO_API_KEY`.

- Tokens are passed in the `Authorization: Bearer <token>` header
- No token in code; always sourced from `.env`
- Token rotation: Update `.env` and restart sessions that cached the old value

## Endpoints (v1)

### Miniature Generation (`POST /api/v1/miniature`)

Create a 3D miniature from a text description.

**Script command:**
```bash
python scripts/3d_ai_studio_client.py start-miniature \
  --description "..." \
  [--style realistic|stylized|cartoon] \
  [--size 5|10|15|20] \
  [--output-format gltf|obj|stl]
```

**Response:** Job ID for polling.

### 3D Generation (`POST /api/v1/generate`)

Generic 3D object generation (used for non-miniature items, lithophanes, etc.).

**Script command:**
```bash
python scripts/3d_ai_studio_client.py start-generation \
  --prompt "..." \
  [--model default|detailed|fast] \
  [--output-format gltf|obj|stl]
```

**Response:** Job ID for polling.

### Job Status (`GET /api/v1/status/:job_id`)

Poll the status of a running or completed job.

**Script command:**
```bash
python scripts/3d_ai_studio_client.py status --job-id <job_id>
```

**Response:** Status (`pending|processing|completed|failed`), progress (0–100), and result URLs (when complete).

### Fetch Result (`GET /api/v1/result/:job_id`)

Download the generated 3D file(s).

**Script command:**
```bash
python scripts/3d_ai_studio_client.py fetch-result \
  --job-id <job_id> \
  [--output-dir ./results]
```

**Response:** Local file paths of downloaded models.

## Workflow Examples

### Miniature Generation with Polling

```bash
# Start the job
JOB_ID=$(python scripts/3d_ai_studio_client.py start-miniature \
  --description "A sleeping cat, ceramic style, 7cm tall" | grep -oP '"job_id":"?\K[^"]+')

# Poll until complete (max 10 attempts, 5s between)
for i in {1..10}; do
  STATUS=$(python scripts/3d_ai_studio_client.py status --job-id $JOB_ID)
  echo "Attempt $i: $STATUS"
  [[ $STATUS == *"completed"* ]] && break
  sleep 5
done

# Fetch results
python scripts/3d_ai_studio_client.py fetch-result --job-id $JOB_ID --output-dir ./miniatures
```

### Batch Generation

For multiple items, use a simple loop or distribute across parallel jobs:

```bash
for desc in "Golden Retriever" "Tabby Cat" "Parrot"; do
  JOB_ID=$(python scripts/3d_ai_studio_client.py start-miniature --description "$desc")
  echo "$desc: $JOB_ID" >> jobs.txt
done

# Later, check status and fetch all
while IFS=': ' read -r NAME JID; do
  python scripts/3d_ai_studio_client.py fetch-result --job-id $JID --output-dir "./results/$NAME"
done < jobs.txt
```

## Error Handling

**API Authentication Failures**

- Missing or invalid token: The script will error immediately.
- Expired token: Update `.env` and retry.

**Job Failures**

- If a job fails, status will show `failed` with an error message.
- Retry with adjusted parameters (description clarity, size constraints, etc.).

**Network Timeouts**

- Default timeout: 30 seconds per request.
- Increase with `--timeout <seconds>` in any command.

## Implementation Details

See [references/api_reference.md](references/api_reference.md) for:
- Full endpoint documentation
- Response schemas
- Error codes and messages
- Rate limits and best practices

See [references/examples.md](references/examples.md) for:
- Real-world workflow examples
- Output file handling
- Integration patterns

## Assumptions & Notes

- **API Base URL:** Inferred from standard `3D_AI_STUDIO_API_URL` env var (falls back to defaults if not set)
- **API Key Env Var:** `3D_AI_STUDIO_API_KEY` (can be overridden with `--api-key` flag)
- **Output Formats:** Default is GLTF; OBJ and STL supported but availability depends on job type
- **Job Polling:** Status checks don't consume rate limits heavily; safe to poll frequently
- **Result Caching:** Downloaded files are cached locally; redownloading the same job ID is instant
- **Concurrency:** API supports concurrent jobs; no per-user rate limits documented in v1

## Security Notes

- **Never commit `.env`** — use `.gitignore` to exclude it
- **Token rotation:** Supported; update `.env` and restart sessions
- **No logging of tokens:** Scripts strip tokens before any output or logging
