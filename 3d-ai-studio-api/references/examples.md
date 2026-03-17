# 3D AI Studio API Examples

Real-world workflows and integration patterns.

## Example 1: Single Miniature with Polling

Generate a miniature and wait for completion, then download.

```bash
#!/bin/bash

# 1. Start the job
RESPONSE=$(python scripts/3d_api_client.py start-miniature \
  --description "A sleeping tabby cat, 8cm tall, ceramic finish" \
  --style realistic \
  --size 8 \
  --output-format gltf)

JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')
echo "Started job: $JOB_ID"

# 2. Wait for completion (up to 10 minutes)
for i in {1..120}; do
  STATUS=$(python scripts/3d_api_client.py status --job-id "$JOB_ID" | jq -r '.status')
  PROGRESS=$(python scripts/3d_api_client.py status --job-id "$JOB_ID" | jq -r '.progress')
  
  echo "[$i/120] Status: $STATUS (${PROGRESS}%)"
  
  [[ "$STATUS" == "completed" ]] && break
  [[ "$STATUS" == "failed" ]] && {
    echo "Job failed!"
    python scripts/3d_api_client.py status --job-id "$JOB_ID" | jq .
    exit 1
  }
  
  sleep 5
done

# 3. Download result
python scripts/3d_api_client.py fetch-result \
  --job-id "$JOB_ID" \
  --output-dir ./miniatures

echo "Downloaded to ./miniatures/"
```

## Example 2: Batch Job Submission and Tracking

Submit multiple jobs, track them, and download results.

```bash
#!/bin/bash

# List of miniatures to generate
declare -a MINIATURES=(
  "A golden retriever sitting, 10cm, realistic"
  "A tabby cat standing, 8cm, stylized"
  "A German Shepherd head, 12cm, realistic"
  "A parrot on a perch, 7cm, cartoon"
)

# Create tracking file
: > jobs_tracking.txt

# 1. Submit all jobs
for desc in "${MINIATURES[@]}"; do
  RESPONSE=$(python scripts/3d_api_client.py start-miniature \
    --description "$desc" \
    --style realistic)
  
  JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')
  echo "$desc|$JOB_ID|pending" >> jobs_tracking.txt
  echo "Submitted: $desc -> $JOB_ID"
done

# 2. Poll all jobs until complete
PENDING_COUNT=$(grep -c 'pending\|processing' jobs_tracking.txt)
while [[ $PENDING_COUNT -gt 0 ]]; do
  echo "Checking status... ($PENDING_COUNT jobs remaining)"
  
  while IFS='|' read -r DESC JOB_ID STATUS; do
    [[ "$STATUS" != "completed" && "$STATUS" != "failed" ]] || continue
    
    STATUS=$(python scripts/3d_api_client.py status --job-id "$JOB_ID" | jq -r '.status')
    sed -i "s|^$DESC\|$JOB_ID\|.*|$DESC\|$JOB_ID\|$STATUS|" jobs_tracking.txt
  done < jobs_tracking.txt
  
  PENDING_COUNT=$(grep -c 'pending\|processing' jobs_tracking.txt)
  [[ $PENDING_COUNT -gt 0 ]] && sleep 10
done

# 3. Download all completed results
mkdir -p ./batch_results

while IFS='|' read -r DESC JOB_ID STATUS; do
  if [[ "$STATUS" == "completed" ]]; then
    python scripts/3d_api_client.py fetch-result \
      --job-id "$JOB_ID" \
      --output-dir "./batch_results/$JOB_ID"
    echo "Downloaded: $DESC"
  elif [[ "$STATUS" == "failed" ]]; then
    echo "FAILED: $DESC ($JOB_ID)"
  fi
done < jobs_tracking.txt

echo "Batch complete. Results in ./batch_results/"
```

## Example 3: Lithophane Generation (Generic 3D)

Generate lithophanes from image descriptions.

```bash
#!/bin/bash

# 1. Start lithophane generation
JOB_ID=$(python scripts/3d_api_client.py start-generation \
  --prompt "A detailed lithophane of a sunset over mountains, 200x150mm" \
  --model detailed \
  --output-format stl | jq -r '.job_id')

echo "Lithophane job: $JOB_ID"

# 2. Wait and download
python scripts/3d_api_client.py status --job-id "$JOB_ID" --poll &
POLL_PID=$!

# Show progress while waiting
while kill -0 $POLL_PID 2>/dev/null; do
  sleep 1
done

# 3. Fetch result
python scripts/3d_api_client.py fetch-result \
  --job-id "$JOB_ID" \
  --output-dir ./lithophanes

echo "Lithophane ready for 3D printing"
```

## Example 4: Integration with Odoo (Order → Generation)

Generate miniatures for Odoo orders automatically.

```bash
#!/usr/bin/env python3
"""
Pseudo-code: Process Odoo sale orders and generate corresponding miniatures.
Requires odoo-manager skill integration.
"""

import subprocess
import json

def generate_for_order(order_id: str, pet_description: str, size: int = 10):
    """Generate a miniature for an Odoo order."""
    
    # 1. Start generation
    result = subprocess.run([
        "python", "scripts/3d_api_client.py", "start-miniature",
        "--description", pet_description,
        "--size", str(size),
        "--output-format", "gltf"
    ], capture_output=True, text=True)
    
    job_data = json.loads(result.stdout)
    job_id = job_data["job_id"]
    
    # 2. Store job_id in Odoo (sale.order extra field)
    # odoo_update_order(order_id, {"generation_job_id": job_id})
    
    # 3. Wait for completion (async, maybe via cron)
    return job_id

def check_and_download_orders():
    """Cron job: Check pending generation jobs and download results."""
    
    # Get all orders with pending jobs
    # pending_orders = odoo_get_orders(generation_status='pending')
    
    # For each pending order:
    # - Check job status
    # - If complete, download and attach file
    # - Update order status
    # - Notify customer
    
    pass
```

## Example 5: Error Handling and Retry

Robust error handling with exponential backoff.

```bash
#!/bin/bash

# Configuration
MAX_RETRIES=3
BACKOFF_INITIAL=2
BACKOFF_MAX=30

submit_job_with_retry() {
  local description="$1"
  local retries=0
  local backoff=$BACKOFF_INITIAL
  
  while [[ $retries -lt $MAX_RETRIES ]]; do
    echo "Submitting job (attempt $((retries+1))/$MAX_RETRIES)..."
    
    if RESPONSE=$(python scripts/3d_api_client.py start-miniature \
      --description "$description" 2>&1); then
      
      echo "$RESPONSE" | jq .
      return 0
    else
      echo "Error: $RESPONSE"
      retries=$((retries+1))
      
      if [[ $retries -lt $MAX_RETRIES ]]; then
        echo "Retrying in ${backoff}s..."
        sleep $backoff
        backoff=$((backoff * 2))
        [[ $backoff -gt $BACKOFF_MAX ]] && backoff=$BACKOFF_MAX
      fi
    fi
  done
  
  echo "Job submission failed after $MAX_RETRIES attempts"
  return 1
}

# Usage
submit_job_with_retry "A sleeping cat, 10cm tall"
```

## Example 6: Status Monitoring Dashboard (Bash)

Real-time job status overview.

```bash
#!/bin/bash

JOBS_FILE="active_jobs.txt"

# Format: JOB_ID|DESCRIPTION|SUBMITTED_TIME

watch_jobs() {
  while IFS='|' read -r JOB_ID DESC TIME; do
    STATUS=$(python scripts/3d_api_client.py status --job-id "$JOB_ID" 2>/dev/null | jq -r '.status // "unknown"')
    PROGRESS=$(python scripts/3d_api_client.py status --job-id "$JOB_ID" 2>/dev/null | jq -r '.progress // 0')
    
    printf "%-40s %-20s %3d%% (%s)\n" "$JOB_ID" "$STATUS" "$PROGRESS" "$DESC"
  done < "$JOBS_FILE"
}

# Watch in a loop
clear
while true; do
  echo "=== 3D AI Studio Jobs (Updated $(date)) ==="
  watch_jobs
  echo
  sleep 5
  clear
done
```

## Example 7: Concurrent Polling with Parallel (GNU parallel)

Speed up status checks with parallel processing.

```bash
#!/bin/bash

# Get all job IDs from a file (one per line)
cat active_jobs.txt | parallel -j 4 \
  'python scripts/3d_api_client.py status --job-id {} | \
   jq -r "\"{} \(.status) (\(.progress)%)\"" '

# Or use xargs
cat active_jobs.txt | xargs -P 4 -I {} \
  python scripts/3d_api_client.py status --job-id {}
```

## Integration Checklist

When integrating into a larger system:

- [ ] Store job IDs in a database or file for tracking
- [ ] Implement exponential backoff for errors
- [ ] Set appropriate timeouts (30+ seconds)
- [ ] Log all API interactions (job IDs, timestamps, responses)
- [ ] Handle 429 (rate limit) gracefully
- [ ] Download results within 24 hours (URLs expire)
- [ ] Validate downloaded files (check file size, mime type)
- [ ] Clean up old jobs via DELETE endpoint (optional)
- [ ] Test with invalid descriptions (expected failures)
- [ ] Monitor rate limits via `X-RateLimit-*` headers

## Testing

```bash
# Test authentication
python scripts/3d_api_client.py status --job-id test-job-id

# Test with explicit token
python scripts/3d_api_client.py \
  --api-key "your-token" \
  start-miniature --description "test"

# Test with custom base URL
python scripts/3d_api_client.py \
  --base-url "https://staging-api.3dstudio.ai" \
  status --job-id test-id
```
