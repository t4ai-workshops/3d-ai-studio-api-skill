#!/usr/bin/env python3
"""
3D AI Studio API Client
Supports all endpoints: 3D generation, image generation, tools, flows, status polling.
"""

import os
import sys
import json
import base64
import argparse
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests
from dotenv import load_dotenv


def load_env():
    env_path = Path.cwd()
    while env_path != env_path.parent:
        env_file = env_path / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return
        env_path = env_path.parent
    load_dotenv()


load_env()

BASE_URL = "https://api.3daistudio.com"


def encode_image(path: str) -> str:
    """Encode local image file to data URI."""
    p = Path(path)
    suffix = p.suffix.lower()
    mime = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(suffix, "image/jpeg")
    data = p.read_bytes()
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


class Client:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 60):
        self.api_key = api_key or os.getenv("3D_AI_STUDIO_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set 3D_AI_STUDIO_API_KEY in .env or pass --api-key")
        self.base_url = (base_url or os.getenv("3D_AI_STUDIO_API_URL", BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        r = self.session.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def balance(self) -> Dict[str, Any]:
        return self._get("/account/user/wallet/")

    def status(self, task_id: str) -> Dict[str, Any]:
        return self._get(f"/v1/generation-request/{task_id}/status/")

    def wait_for_completion(self, task_id: str, poll_interval: int = 10,
                            max_attempts: int = 120) -> Dict[str, Any]:
        for attempt in range(1, max_attempts + 1):
            result = self.status(task_id)
            s = result.get("status")
            progress = result.get("progress", 0)
            print(f"  [{attempt}/{max_attempts}] {s} ({progress}%)", file=sys.stderr)
            if s in ("FINISHED", "FAILED"):
                return result
            time.sleep(poll_interval)
        raise TimeoutError(f"Task {task_id} did not complete within {max_attempts * poll_interval}s")

    def download_results(self, result: Dict[str, Any], output_dir: str) -> List[str]:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        paths = []
        for item in result.get("results", []):
            url = item.get("asset")
            if not url:
                continue
            filename = url.split("/")[-1].split("?")[0]
            filepath = Path(output_dir) / filename
            print(f"  Downloading {filename}...", file=sys.stderr)
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
            filepath.write_bytes(r.content)
            paths.append(str(filepath))
        return paths

    # --- 3D Generation ---

    def tencent_rapid(self, prompt: Optional[str] = None, image: Optional[str] = None,
                      enable_pbr: bool = False) -> str:
        payload: Dict[str, Any] = {"enable_pbr": enable_pbr}
        if image:
            payload["image"] = image
        else:
            payload["prompt"] = prompt
        r = self._post("/v1/3d-models/tencent/generate/rapid/", payload)
        return r["task_id"]

    def tencent_pro(self, prompt: Optional[str] = None, image: Optional[str] = None,
                    multi_view_images: Optional[list] = None, model: str = "3.0",
                    enable_pbr: bool = False, face_count: Optional[int] = None,
                    generate_type: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {"model": model, "enable_pbr": enable_pbr}
        if multi_view_images:
            payload["multi_view_images"] = multi_view_images
        elif image:
            payload["image"] = image
        else:
            payload["prompt"] = prompt
        if face_count:
            payload["face_count"] = face_count
        if generate_type:
            payload["generate_type"] = generate_type
        r = self._post("/v1/3d-models/tencent/generate/pro/", payload)
        return r["task_id"]

    def trellis(self, image: str, enable_pbr: bool = False) -> str:
        payload: Dict[str, Any] = {"enable_pbr": enable_pbr}
        if image.startswith("http"):
            payload["image_url"] = image
        else:
            payload["image"] = image
        r = self._post("/v1/3d-models/trellis2/generate/", payload)
        return r["task_id"]

    def tripo(self, prompt: Optional[str] = None, image: Optional[str] = None,
              version: str = "v3.1", enable_pbr: bool = False) -> str:
        payload: Dict[str, Any] = {"version": version, "enable_pbr": enable_pbr}
        if image:
            payload["image"] = image
            r = self._post("/v1/3d-models/tripo/image-to-3d/", payload)
        else:
            payload["prompt"] = prompt
            r = self._post("/v1/3d-models/tripo/text-to-3d/", payload)
        return r["task_id"]

    def tripo_p1(self, prompt: Optional[str] = None, image: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {}
        if image:
            payload["image"] = image
            r = self._post("/v1/3d-models/tripo/image-to-3d/p1/", payload)
        else:
            payload["prompt"] = prompt
            r = self._post("/v1/3d-models/tripo/text-to-3d/p1/", payload)
        return r["task_id"]

    # --- Image Generation ---

    def image_generate(self, endpoint: str, prompt: str, count: int = 1) -> str:
        r = self._post(endpoint, {"prompt": prompt, "count": count})
        return r["task_id"]

    # --- Tools ---

    def convert(self, model_url: str, output_format: str) -> str:
        r = self._post("/v1/tools/convert/", {"model_url": model_url, "output_format": output_format})
        return r["task_id"]

    def render(self, model_url: str) -> str:
        r = self._post("/v1/tools/render/", {"model_url": model_url})
        return r["task_id"]

    def repair(self, model_url: str) -> str:
        r = self._post("/v1/tools/repair/", {"model_url": model_url})
        return r["task_id"]

    def optimize(self, model_url: str) -> str:
        r = self._post("/v1/tools/optimize/", {"model_url": model_url})
        return r["task_id"]

    def bake_texture(self, high_poly_url: str, low_poly_url: str) -> str:
        r = self._post("/v1/tools/bake-texture/", {
            "high_poly_model_url": high_poly_url,
            "low_poly_model_url": low_poly_url,
        })
        return r["task_id"]

    def remove_bg(self, image: str) -> str:
        r = self._post("/v1/tools/remove-bg/", {"image": image})
        return r["task_id"]

    def image_enhance(self, image: str) -> str:
        r = self._post("/v1/tools/image-enhance/", {"image": image})
        return r["task_id"]

    def volume(self, model_url: str) -> str:
        r = self._post("/v1/tools/calculate-volume/", {"model_url": model_url})
        return r["task_id"]

    # --- Flows ---

    def miniature(self, image: str, preset: str, edition: str = "default",
                  scale: Optional[str] = None, scale_height_cm: Optional[float] = None,
                  face_count: Optional[int] = None, two_d_engine: Optional[str] = None,
                  three_d_engine: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {"image": image, "preset": preset, "edition": edition}
        if scale and scale != "none":
            payload["scale"] = scale
        if scale_height_cm:
            payload["scale_height_cm"] = scale_height_cm
        if face_count:
            payload["face_count"] = face_count
        if two_d_engine:
            payload["2d_engine"] = two_d_engine
        if three_d_engine:
            payload["3d_engine"] = three_d_engine
        r = self._post("/v1/flow/miniature/", payload)
        return r["task_id"]


def run_and_maybe_wait(client: Client, task_id: str, args) -> None:
    """Print task_id, optionally wait and download."""
    print(json.dumps({"task_id": task_id, "status": "submitted"}))
    if getattr(args, "wait", False):
        print("Polling for completion...", file=sys.stderr)
        result = client.wait_for_completion(task_id)
        print(json.dumps(result))
        if result.get("status") == "FINISHED" and getattr(args, "output_dir", None):
            paths = client.download_results(result, args.output_dir)
            print(json.dumps({"downloaded": paths}))


def main():
    parser = argparse.ArgumentParser(description="3D AI Studio API Client")
    parser.add_argument("--api-key", help="Override API key")
    parser.add_argument("--base-url", help="Override base URL")
    parser.add_argument("--timeout", type=int, default=60)

    sub = parser.add_subparsers(dest="command")

    # balance
    sub.add_parser("balance", help="Check credit balance")

    # status
    p = sub.add_parser("status", help="Check task status")
    p.add_argument("--task-id", required=True)
    p.add_argument("--poll", action="store_true", help="Keep polling until finished")
    p.add_argument("--poll-interval", type=int, default=10)

    # download
    p = sub.add_parser("download", help="Download results for a finished task")
    p.add_argument("--task-id", required=True)
    p.add_argument("--output-dir", default="./results")

    # tencent-rapid
    p = sub.add_parser("tencent-rapid", help="Tencent Hunyuan Rapid (35 cr)")
    p.add_argument("--prompt")
    p.add_argument("--image", help="Local image path or URL")
    p.add_argument("--enable-pbr", action="store_true")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # tencent-pro
    p = sub.add_parser("tencent-pro", help="Tencent Hunyuan Pro (60+ cr)")
    p.add_argument("--prompt")
    p.add_argument("--image", help="Local image path or URL")
    p.add_argument("--model", default="3.0")
    p.add_argument("--enable-pbr", action="store_true")
    p.add_argument("--face-count", type=int)
    p.add_argument("--generate-type", choices=["Normal", "Cartoon", "Sculpture"])
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # trellis
    p = sub.add_parser("trellis", help="TRELLIS.2 image-to-3D (10–50 cr)")
    p.add_argument("--image", required=True, help="Local image path or URL")
    p.add_argument("--enable-pbr", action="store_true")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # tripo
    p = sub.add_parser("tripo", help="Tripo v3.0/v3.1 (0–120 cr)")
    p.add_argument("--prompt")
    p.add_argument("--image", help="Local image path")
    p.add_argument("--version", default="v3.1", choices=["v3.0", "v3.1"])
    p.add_argument("--enable-pbr", action="store_true")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # tripo-p1
    p = sub.add_parser("tripo-p1", help="Tripo P1 premium (60–160 cr)")
    p.add_argument("--prompt")
    p.add_argument("--image", help="Local image path")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # image-gemini3pro
    p = sub.add_parser("image-gemini3pro", help="Gemini 3 Pro image generation (10 cr/image)")
    p.add_argument("--prompt", required=True)
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # image-gemini31flash
    p = sub.add_parser("image-gemini31flash", help="Gemini 3.1 Flash image generation (7 cr/image)")
    p.add_argument("--prompt", required=True)
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # image-gemini25flash
    p = sub.add_parser("image-gemini25flash", help="Gemini 2.5 Flash image generation (5 cr/image, max 4)")
    p.add_argument("--prompt", required=True)
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # image-seedream
    p = sub.add_parser("image-seedream", help="SeeDream v5 Lite image generation")
    p.add_argument("--prompt", required=True)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # convert
    p = sub.add_parser("convert", help="Convert 3D format (10 cr)")
    p.add_argument("--model-url", required=True)
    p.add_argument("--output-format", required=True, choices=["obj", "fbx", "stl", "ply"])
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # render
    p = sub.add_parser("render", help="Render 3D model to image (5–20 cr)")
    p.add_argument("--model-url", required=True)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # repair
    p = sub.add_parser("repair", help="Repair mesh / print prep (60–90 cr)")
    p.add_argument("--model-url", required=True)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # optimize
    p = sub.add_parser("optimize", help="Optimize/compress GLB (10 cr)")
    p.add_argument("--model-url", required=True)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # bake-texture
    p = sub.add_parser("bake-texture", help="Bake texture high-poly → low-poly (5 cr)")
    p.add_argument("--high-poly-url", required=True)
    p.add_argument("--low-poly-url", required=True)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # remove-bg
    p = sub.add_parser("remove-bg", help="Remove image background (3–5 cr)")
    p.add_argument("--image", required=True, help="Local image path")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # image-enhance
    p = sub.add_parser("image-enhance", help="Enhance/upscale image (15–20 cr)")
    p.add_argument("--image", required=True, help="Local image path")
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    # volume
    p = sub.add_parser("volume", help="Calculate model volume (20 cr, beta)")
    p.add_argument("--model-url", required=True)
    p.add_argument("--wait", action="store_true")

    # miniature
    p = sub.add_parser("miniature", help="Photo → 3D miniature figurine (200–300 cr)")
    p.add_argument("--image", required=True, help="Local image path")
    p.add_argument("--preset", required=True, help="Style preset")
    p.add_argument("--edition", default="default", choices=["default", "fast"])
    p.add_argument("--scale", default="none",
                   help="Scale: none, h0, o, g, z, n, tt, 1:NUMBER, custom")
    p.add_argument("--scale-height-cm", type=float,
                   help="Required when --scale=custom. Height in cm (max 100)")
    p.add_argument("--face-count", type=int, help="3000–1500000")
    p.add_argument("--2d-engine", dest="two_d_engine", choices=["v3", "v3.1", "v3.2"])
    p.add_argument("--3d-engine", dest="three_d_engine", choices=["hunyuan", "prism"])
    p.add_argument("--wait", action="store_true")
    p.add_argument("--output-dir", default="./results")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = Client(api_key=args.api_key, base_url=args.base_url, timeout=args.timeout)

        if args.command == "balance":
            print(json.dumps(client.balance()))

        elif args.command == "status":
            result = client.status(args.task_id)
            print(json.dumps(result))
            if args.poll:
                while result.get("status") not in ("FINISHED", "FAILED"):
                    time.sleep(args.poll_interval)
                    result = client.status(args.task_id)
                    print(json.dumps(result))

        elif args.command == "download":
            result = client.status(args.task_id)
            if result.get("status") != "FINISHED":
                print(f"Task is {result.get('status')}, not FINISHED", file=sys.stderr)
                sys.exit(1)
            paths = client.download_results(result, args.output_dir)
            print(json.dumps({"downloaded": paths}))

        elif args.command == "tencent-rapid":
            image = encode_image(args.image) if args.image and not args.image.startswith("http") else args.image
            task_id = client.tencent_rapid(prompt=args.prompt, image=image, enable_pbr=args.enable_pbr)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "tencent-pro":
            image = encode_image(args.image) if args.image and not args.image.startswith("http") else args.image
            task_id = client.tencent_pro(
                prompt=args.prompt, image=image, model=args.model,
                enable_pbr=args.enable_pbr, face_count=args.face_count,
                generate_type=args.generate_type,
            )
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "trellis":
            image = encode_image(args.image) if not args.image.startswith("http") else args.image
            task_id = client.trellis(image=image, enable_pbr=args.enable_pbr)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "tripo":
            image = encode_image(args.image) if args.image and not args.image.startswith("http") else args.image
            task_id = client.tripo(prompt=args.prompt, image=image,
                                   version=args.version, enable_pbr=args.enable_pbr)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "tripo-p1":
            image = encode_image(args.image) if args.image and not args.image.startswith("http") else args.image
            task_id = client.tripo_p1(prompt=args.prompt, image=image)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "image-gemini3pro":
            task_id = client.image_generate("/v1/images/gemini/3/pro/generate/", args.prompt, args.count)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "image-gemini31flash":
            task_id = client.image_generate("/v1/images/gemini/3.1/flash/generate/", args.prompt, args.count)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "image-gemini25flash":
            task_id = client.image_generate("/v1/images/gemini/2.5/flash/generate/", args.prompt, args.count)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "image-seedream":
            task_id = client.image_generate("/v1/images/seedream/v5/lite/generate/", args.prompt)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "convert":
            task_id = client.convert(args.model_url, args.output_format)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "render":
            task_id = client.render(args.model_url)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "repair":
            task_id = client.repair(args.model_url)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "optimize":
            task_id = client.optimize(args.model_url)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "bake-texture":
            task_id = client.bake_texture(args.high_poly_url, args.low_poly_url)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "remove-bg":
            task_id = client.remove_bg(encode_image(args.image))
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "image-enhance":
            task_id = client.image_enhance(encode_image(args.image))
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "volume":
            task_id = client.volume(args.model_url)
            run_and_maybe_wait(client, task_id, args)

        elif args.command == "miniature":
            task_id = client.miniature(
                image=encode_image(args.image),
                preset=args.preset,
                edition=args.edition,
                scale=args.scale if args.scale != "none" else None,
                scale_height_cm=args.scale_height_cm,
                face_count=args.face_count,
                two_d_engine=args.two_d_engine,
                three_d_engine=args.three_d_engine,
            )
            run_and_maybe_wait(client, task_id, args)

    except requests.exceptions.HTTPError as e:
        body = {}
        try:
            body = e.response.json()
        except Exception:
            pass
        print(json.dumps({"error": str(e), "detail": body}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
