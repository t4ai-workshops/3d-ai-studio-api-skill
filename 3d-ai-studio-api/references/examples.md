# 3D AI Studio API — Examples

Real-world workflow examples using the Python client.

## 1. Check Balance Before Starting

```bash
python scripts/3d_api_client.py balance
# → {"balance": "150.00"}
```

## 2. Quick 3D Model from Text (Tencent Rapid)

```bash
python scripts/3d_api_client.py tencent-rapid \
  --prompt "a wooden chair with armrests" \
  --enable-pbr \
  --wait \
  --output-dir ./models
# → {"task_id": "abc-123", "status": "submitted"}
# → [1/120] IN_PROGRESS (33%)
# → [2/120] FINISHED (100%)
# → {"downloaded": ["./models/model.glb"]}
```

## 3. Miniature Figurine from Photo

```bash
python scripts/3d_api_client.py miniature \
  --image ./portrait.jpg \
  --preset v3_miniature_human_full_body \
  --edition default \
  --scale h0 \
  --wait \
  --output-dir ./miniature_output
# Results include styled_image.jpeg, figurine.glb, figurine_h0.glb (1:87), figurine_h0.zip
```

## 4. Image-to-3D with TRELLIS.2

```bash
python scripts/3d_api_client.py trellis \
  --image ./product_photo.png \
  --enable-pbr \
  --wait \
  --output-dir ./product_3d
```

## 5. Manual Polling Loop (Bash)

```bash
# Submit jobs and save task IDs
TASK1=$(python scripts/3d_api_client.py tencent-rapid \
  --prompt "a golden retriever" | python -c "import sys,json; print(json.load(sys.stdin)['task_id'])")

TASK2=$(python scripts/3d_api_client.py tripo \
  --prompt "a tabby cat" --version v3.1 | python -c "import sys,json; print(json.load(sys.stdin)['task_id'])")

for TASK in $TASK1 $TASK2; do
  while true; do
    STATUS=$(python scripts/3d_api_client.py status --task-id $TASK \
      | python -c "import sys,json; print(json.load(sys.stdin)['status'])")
    [[ "$STATUS" == "FINISHED" || "$STATUS" == "FAILED" ]] && break
    sleep 10
  done
  python scripts/3d_api_client.py download --task-id $TASK --output-dir "./results/$TASK"
done
```

## 6. Image Generation → 3D Pipeline

```bash
# Generate clean product image
python scripts/3d_api_client.py image-gemini31flash \
  --prompt "a sleek modern chair, white background, product photo" \
  --wait --output-dir ./ref_images

# Use it for 3D generation
python scripts/3d_api_client.py trellis \
  --image ./ref_images/output.jpeg \
  --enable-pbr --wait --output-dir ./chair_3d
```

## 7. Post-Processing: Generate → Repair → Convert

```bash
# Generate
python scripts/3d_api_client.py tencent-rapid \
  --prompt "a ceramic vase" --enable-pbr --wait --output-dir ./raw

# Repair for 3D printing (use URL from result)
python scripts/3d_api_client.py repair \
  --model-url "https://storage.3daistudio.com/assets/model.glb" \
  --wait --output-dir ./repaired

# Convert to STL
python scripts/3d_api_client.py convert \
  --model-url "https://storage.3daistudio.com/assets/repaired.glb" \
  --output-format stl --wait --output-dir ./final
```

## 8. Remove Background Before 3D

```bash
python scripts/3d_api_client.py remove-bg \
  --image ./product.jpg --wait --output-dir ./cleaned

python scripts/3d_api_client.py trellis \
  --image ./cleaned/output.png \
  --enable-pbr --wait --output-dir ./product_3d
```

## 9. Python Library Usage

```python
import base64
from pathlib import Path
from scripts.api_client import Client  # adjust import path as needed

def encode_image(path):
    data = Path(path).read_bytes()
    return f"data:image/jpeg;base64,{base64.b64encode(data).decode()}"

client = Client()  # reads 3D_AI_STUDIO_API_KEY from env

# Check balance
print(client.balance())  # {"balance": "150.00"}

# Generate miniature
task_id = client.miniature(
    image=encode_image("./portrait.jpg"),
    preset="v3_miniature_human_full_body",
    edition="fast",
)

result = client.wait_for_completion(task_id)
if result["status"] == "FINISHED":
    paths = client.download_results(result, "./output")
    print(paths)
```

## Status Values

| Status | Meaning |
|--------|---------|
| `PENDING` | Queued |
| `IN_PROGRESS` | Running |
| `FINISHED` | Done — download results[] |
| `FAILED` | Failed — credits refunded automatically |

## Credit Cost Reference

| Operation | Credits |
|-----------|---------|
| Tencent Rapid | 35 |
| Tencent Pro | 60–100 |
| TRELLIS.2 | 10–50 |
| Tripo v3 | 0–120 |
| Tripo P1 | 60–160 |
| Gemini 3 Pro image | 10/image |
| Gemini 3.1 Flash image | 7/image |
| Gemini 2.5 Flash image | 5/image |
| Miniature fast | 200 |
| Miniature default | 300 |
| Convert | 10 |
| Render | 5–20 |
| Repair | 60–90 |
| Optimize | 10 |
| Bake Texture | 5 |
| Remove BG | 3–5 |
| Image Enhance | 15–20 |
| Volume Calculator | 20 |
