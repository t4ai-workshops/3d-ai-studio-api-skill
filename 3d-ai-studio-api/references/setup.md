# Setup and Configuration

How to set up the 3D AI Studio API skill in your OpenClaw environment.

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Bash (for shell scripts)
- 3D AI Studio API credentials (bearer token)

## Installation

### 1. Ensure Skill is in Place

The skill directory should be at:
```
~/.openclaw/workspace/skills/3d-ai-studio-api/
```

With structure:
```
3d-ai-studio-api/
├── SKILL.md
├── scripts/
│   ├── 3d_api_client.py
│   ├── 3d_api.sh
│   └── requirements.txt
└── references/
    ├── api_reference.md
    ├── examples.md
    └── setup.md
```

### 2. Install Python Dependencies

```bash
pip install -r scripts/requirements.txt
```

Or install globally:
```bash
pip install requests python-dotenv
```

### 3. Configure Environment

Create a `.env` file in your workspace root (`~/.openclaw/workspace/`):

```bash
# Required: Your 3D AI Studio API bearer token
3D_AI_STUDIO_API_KEY=your_actual_bearer_token_here

# Optional: Override API base URL (defaults to https://api.3daistudio.com)
3D_AI_STUDIO_API_URL=https://api.3daistudio.com
```

**Security:** Never commit `.env` to version control. Add to `.gitignore`:

```bash
echo ".env" >> ~/.openclaw/workspace/.gitignore
```

### 4. Verify Setup

Test the client:

```bash
python scripts/3d_api_client.py status --job-id test-id
```

If you see an error about missing API key, double-check `.env` is in the right location and has the correct format.

## Configuration Details

### Environment Variables

| Variable | Required | Default | Notes |
|---|---|---|---|
| `3D_AI_STUDIO_API_KEY` | Yes | None | Bearer token from 3D Studio account |
| `3D_AI_STUDIO_API_URL` | No | `https://api.3daistudio.com` | Override if using staging/custom endpoint |

### Python Client Configuration

The `3d_api_client.py` script supports command-line overrides:

```bash
# Override API key
python scripts/3d_api_client.py \
  --api-key "different-token" \
  status --job-id abc-123

# Override API URL
python scripts/3d_api_client.py \
  --base-url "https://staging-api.3dstudio.ai" \
  start-miniature --description "test"

# Override timeout
python scripts/3d_api_client.py \
  --timeout 60 \
  fetch-result --job-id abc-123
```

### Shell Wrapper

For convenience, use the provided shell wrapper:

```bash
# Instead of: python scripts/3d_api_client.py start-miniature --description "..."
# Use: scripts/3d_api.sh start-miniature --description "..."

scripts/3d_api.sh start-miniature \
  --description "A sleeping cat, 10cm tall" \
  --wait
```

The wrapper automatically checks dependencies and runs the Python client.

## Environment Variable Resolution

The skill searches for `.env` in this order:

1. Current working directory
2. Parent directories (up the tree)
3. System environment variables

Example: If you run `python scripts/3d_api_client.py` from any subdirectory of `~/.openclaw/workspace/`, the skill will find `.env` at the workspace root.

## Token Management

### Obtaining Your Token

1. Log in to 3D Studio dashboard
2. Go to **Settings → API Keys**
3. Generate a new bearer token
4. Copy the full token (do not truncate)
5. Paste into `.env` as `3D_AI_STUDIO_API_KEY`

### Token Rotation

To rotate your token:

1. Revoke the old token in the 3D Studio dashboard
2. Generate a new token
3. Update `.env` with the new token
4. Restart any running agent sessions (they cache env vars at startup)

### Token Security

- **Never log tokens** — the script strips tokens before any output
- **Never commit to git** — always exclude `.env`
- **Never share tokens** — treat like passwords
- **Rotate periodically** — recommended every 90 days

## Troubleshooting

### "API key not found"

**Symptom:** Error message: `API key not found. Set 3D_AI_STUDIO_API_KEY in .env`

**Solutions:**
1. Verify `.env` exists at `~/.openclaw/workspace/.env`
2. Verify file contains `3D_AI_STUDIO_API_KEY=your_token` (no extra spaces)
3. Verify no syntax errors in `.env` (e.g., quotes, special chars)
4. Verify you're running from workspace or a subdirectory

### "Bearer token is invalid or expired"

**Symptom:** Error: `401 Unauthorized` or `INVALID_TOKEN`

**Solutions:**
1. Verify token is complete (no truncation, no extra spaces)
2. Check token expiration in 3D Studio dashboard
3. Regenerate token if expired
4. Update `.env` and restart agent session

### "Request timeout"

**Symptom:** Error after 30 seconds of waiting

**Solutions:**
1. Check network connectivity
2. Increase timeout: `--timeout 60`
3. API may be temporarily slow — retry in 30 seconds
4. Contact 3D Studio support if persistent

### "Rate limit exceeded"

**Symptom:** HTTP 429 with `Retry-After: 15`

**Solutions:**
1. Wait the specified number of seconds
2. Reduce polling frequency (don't poll faster than 1/second)
3. Consider batch submission instead of individual jobs
4. Check `X-RateLimit-Remaining` header to plan ahead

### "Job not found"

**Symptom:** Error: `404 Not Found` or `JOB_NOT_FOUND`

**Solutions:**
1. Verify job ID is correct (copy-paste exact value)
2. Job may have been deleted — check creation time
3. Job results expire after 24 hours; download sooner

## Advanced: Custom Base URLs

To use a staging or custom API endpoint:

```bash
# Via environment variable
export 3D_AI_STUDIO_API_URL=https://staging-api.3dstudio.ai
python scripts/3d_api_client.py status --job-id abc-123

# Via command line (takes precedence over env var)
python scripts/3d_api_client.py \
  --base-url https://custom-api.internal.example.com \
  status --job-id abc-123

# Via .env
3D_AI_STUDIO_API_URL=https://staging-api.3dstudio.ai
```

## Integration Examples

See [examples.md](examples.md) for:
- Single job with polling
- Batch job submission
- Lithophane generation
- Odoo integration
- Error handling and retry
- Status monitoring
- Concurrent polling

## Maintenance

### Checking Skill Version

```bash
# View SKILL.md to see current spec
cat ~/.openclaw/workspace/skills/3d-ai-studio-api/SKILL.md
```

### Updating Dependencies

```bash
pip install --upgrade requests python-dotenv
```

### Logs and Debugging

The Python client outputs errors to `stderr` and results to `stdout`:

```bash
# Capture error details
python scripts/3d_api_client.py status --job-id bad-id 2>&1

# Separate output
python scripts/3d_api_client.py status --job-id abc-123 > result.json 2> error.log
```

### Testing Endpoints Manually

Use `curl` to test directly:

```bash
# Test status endpoint
curl -X GET https://api.3dstudio.ai/api/v1/status/test-job-id \
  -H "Authorization: Bearer $3D_AI_STUDIO_API_KEY" \
  -H "Content-Type: application/json"
```

Store token in env first:
```bash
export 3D_AI_STUDIO_API_KEY="your-token-here"
```

## Support

For issues with:
- **Skill functionality** — check [api_reference.md](api_reference.md) and [examples.md](examples.md)
- **3D AI Studio API** — contact api-support@3dstudio.ai
- **OpenClaw integration** — refer to OpenClaw documentation

---

_Last updated: March 2026_
