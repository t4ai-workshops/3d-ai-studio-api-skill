# 3D AI Studio API Reference

Complete endpoint documentation, schemas, and error handling for API v1.

## Base URL

```
https://api.3dstudio.ai
```

Can be overridden with `3D_AI_STUDIO_API_URL` env var.

## Authentication

All requests require Bearer token in the `Authorization` header:

```
Authorization: Bearer <your_token_here>
```

Token is sourced from `3D_AI_STUDIO_API_KEY` env var. Never hardcode tokens.

## Endpoints

### POST /api/v1/miniature

Start a miniature generation job.

**Request Body:**

```json
{
  "description": "string, required. Text description of the miniature.",
  "style": "string, optional. One of: realistic, stylized, cartoon. Default: realistic",
  "size_cm": "integer, optional. Size in centimeters. Default: 10",
  "output_format": "string, optional. One of: gltf, obj, stl. Default: gltf"
}
```

**Response (201 Created):**

```json
{
  "job_id": "abc-123-def-456",
  "status": "submitted",
  "created_at": "2026-03-17T02:30:00Z"
}
```

**Example:**

```bash
curl -X POST https://api.3dstudio.ai/api/v1/miniature \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A sleeping golden retriever, 10cm tall, ceramic style",
    "style": "realistic",
    "size_cm": 10,
    "output_format": "gltf"
  }'
```

### POST /api/v1/generate

Start a generic 3D generation job (for non-miniature items, lithophanes, etc.).

**Request Body:**

```json
{
  "prompt": "string, required. Description or prompt for 3D generation.",
  "model": "string, optional. One of: default, detailed, fast. Default: default",
  "output_format": "string, optional. One of: gltf, obj, stl. Default: gltf"
}
```

**Response (201 Created):**

```json
{
  "job_id": "xyz-789-uvw",
  "status": "submitted",
  "created_at": "2026-03-17T02:35:00Z"
}
```

**Example:**

```bash
curl -X POST https://api.3dstudio.ai/api/v1/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A lithophane of a sunset landscape",
    "model": "detailed",
    "output_format": "stl"
  }'
```

### GET /api/v1/status/{job_id}

Poll the status of a submitted job.

**Response (200 OK):**

```json
{
  "job_id": "abc-123-def-456",
  "status": "processing",
  "progress": 45,
  "created_at": "2026-03-17T02:30:00Z",
  "updated_at": "2026-03-17T02:32:15Z",
  "result_url": null
}
```

**Status Values:**
- `pending`: Queued, not yet processing
- `processing`: Currently generating
- `completed`: Done; `result_url` is populated
- `failed`: Generation failed; check error message

**Response when completed:**

```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "progress": 100,
  "created_at": "2026-03-17T02:30:00Z",
  "completed_at": "2026-03-17T02:45:30Z",
  "result_url": "https://api.3dstudio.ai/results/abc-123-def-456/model.gltf"
}
```

**Response when failed:**

```json
{
  "job_id": "abc-123-def-456",
  "status": "failed",
  "error_message": "Description was too vague; please provide more detail",
  "error_code": "INVALID_DESCRIPTION"
}
```

**Example:**

```bash
curl -X GET https://api.3dstudio.ai/api/v1/status/abc-123-def-456 \
  -H "Authorization: Bearer <token>"
```

### GET /api/v1/result/{job_id}

Fetch the result metadata and download URL(s).

**Response (200 OK):**

```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "file_url": "https://api.3dstudio.ai/results/abc-123-def-456/model.gltf",
  "file_size_bytes": 2048576,
  "filename": "model.gltf",
  "output_format": "gltf",
  "metadata": {
    "vertices": 50000,
    "triangles": 25000,
    "dimensions_cm": { "x": 10, "y": 10, "z": 15 }
  }
}
```

**Note:** If the job is still processing, the response is HTTP 202 (Accepted) with `file_url` as `null`.

**Example:**

```bash
curl -X GET https://api.3dstudio.ai/api/v1/result/abc-123-def-456 \
  -H "Authorization: Bearer <token>"
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "INVALID_REQUEST",
  "message": "Missing required field: description"
}
```

### 401 Unauthorized

```json
{
  "error": "INVALID_TOKEN",
  "message": "Bearer token is invalid or expired"
}
```

### 404 Not Found

```json
{
  "error": "JOB_NOT_FOUND",
  "message": "Job ID does not exist or has been deleted"
}
```

### 429 Too Many Requests

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit: 100 requests per minute",
  "retry_after_seconds": 15
}
```

**Action:** Wait the specified seconds before retrying.

### 500 Internal Server Error

```json
{
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred. Please try again later."
}
```

## Rate Limits

- **Per minute:** 100 requests
- **Per hour:** 10,000 requests
- **Concurrent jobs:** Up to 50 per account

Exceeding limits returns HTTP 429 with `Retry-After` header.

## Best Practices

1. **Poll Intervals:** Use 5–10 second intervals for status checks. Don't poll faster than 1/second.
2. **Timeouts:** Set HTTP timeouts to 30+ seconds; generation jobs can queue briefly.
3. **Error Recovery:**
   - 4xx errors: Fix the request and retry.
   - 5xx errors: Implement exponential backoff (1s, 2s, 4s, 8s max).
4. **Token Rotation:** Refresh tokens periodically; old tokens may be revoked.
5. **File Download:** Download results within 24 hours; URLs expire after that.
6. **Cleanup:** Delete old jobs via `DELETE /api/v1/job/{job_id}` (optional, frees quota).

## Response Headers

All successful responses include:

```
Content-Type: application/json
X-Request-ID: unique-request-identifier
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1710681060
```

Use `X-RateLimit-Remaining` to detect approaching rate limits.

## Webhooks (Future)

v2 will support webhooks. For now, polling is the standard.
