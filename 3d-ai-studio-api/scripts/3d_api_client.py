#!/usr/bin/env python3
"""
3D AI Studio API Client
Handles authentication, job submission, status polling, and result fetching.
"""

import os
import sys
import json
import argparse
import requests
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load .env from current directory or parent directories
def load_env():
    """Load .env from workspace root."""
    env_path = Path.cwd()
    while env_path != env_path.parent:
        env_file = env_path / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return
        env_path = env_path.parent
    # If no .env found, try current directory
    load_dotenv()

load_env()

class ThreeDAPIClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize the 3D AI Studio API client.
        
        Args:
            api_key: Bearer token (defaults to 3D_AI_STUDIO_API_KEY env var)
            base_url: Base URL (defaults to 3D_AI_STUDIO_API_URL env var)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("3D_AI_STUDIO_API_KEY")
        self.base_url = (base_url or os.getenv("3D_AI_STUDIO_API_URL", "https://api.3dstudio.ai")).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        
        if not self.api_key:
            raise ValueError("API key not found. Set 3D_AI_STUDIO_API_KEY in .env or pass --api-key")
        
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to API."""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def start_miniature(self, description: str, style: str = "realistic", 
                       size: int = 10, output_format: str = "gltf") -> str:
        """Start a miniature generation job."""
        payload = {
            "description": description,
            "style": style,
            "size_cm": size,
            "output_format": output_format
        }
        result = self._request("POST", "/api/v1/miniature", json=payload)
        return result.get("job_id")
    
    def start_generation(self, prompt: str, model: str = "default", 
                        output_format: str = "gltf") -> str:
        """Start a generic 3D generation job."""
        payload = {
            "prompt": prompt,
            "model": model,
            "output_format": output_format
        }
        result = self._request("POST", "/api/v1/generate", json=payload)
        return result.get("job_id")
    
    def get_status(self, job_id: str) -> Dict[str, Any]:
        """Poll job status."""
        result = self._request("GET", f"/api/v1/status/{job_id}")
        return result
    
    def fetch_result(self, job_id: str, output_dir: str = "./results") -> str:
        """Download generated file(s)."""
        result = self._request("GET", f"/api/v1/result/{job_id}")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Handle result based on response format
        file_url = result.get("file_url") or result.get("model_url")
        if not file_url:
            raise ValueError(f"No file URL in result: {result}")
        
        # Download file
        filename = file_url.split("/")[-1]
        filepath = Path(output_dir) / filename
        
        print(f"Downloading {filename}...", file=sys.stderr)
        response = self.session.get(file_url, timeout=self.timeout)
        response.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        return str(filepath)
    
    def wait_for_completion(self, job_id: str, max_attempts: int = 60, 
                           poll_interval: int = 5) -> Dict[str, Any]:
        """Poll until job completes or fails."""
        for attempt in range(max_attempts):
            status_result = self.get_status(job_id)
            status = status_result.get("status")
            
            if status in ("completed", "failed"):
                return status_result
            
            print(f"[{attempt+1}/{max_attempts}] Status: {status} "
                  f"(Progress: {status_result.get('progress', 0)}%)", file=sys.stderr)
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {max_attempts * poll_interval}s")


def main():
    parser = argparse.ArgumentParser(description="3D AI Studio API Client")
    parser.add_argument("--api-key", help="Override API key from env")
    parser.add_argument("--base-url", help="Override API base URL from env")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # start-miniature
    miniature_parser = subparsers.add_parser("start-miniature", help="Start miniature generation")
    miniature_parser.add_argument("--description", required=True, help="Description of the miniature")
    miniature_parser.add_argument("--style", default="realistic", choices=["realistic", "stylized", "cartoon"])
    miniature_parser.add_argument("--size", type=int, default=10, help="Size in cm")
    miniature_parser.add_argument("--output-format", default="gltf", choices=["gltf", "obj", "stl"])
    miniature_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    
    # start-generation
    gen_parser = subparsers.add_parser("start-generation", help="Start generic 3D generation")
    gen_parser.add_argument("--prompt", required=True, help="Generation prompt")
    gen_parser.add_argument("--model", default="default", choices=["default", "detailed", "fast"])
    gen_parser.add_argument("--output-format", default="gltf", choices=["gltf", "obj", "stl"])
    gen_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    
    # status
    status_parser = subparsers.add_parser("status", help="Check job status")
    status_parser.add_argument("--job-id", required=True, help="Job ID to check")
    status_parser.add_argument("--poll", action="store_true", help="Keep polling until complete")
    status_parser.add_argument("--poll-interval", type=int, default=5, help="Poll interval in seconds")
    
    # fetch-result
    fetch_parser = subparsers.add_parser("fetch-result", help="Download generated result")
    fetch_parser.add_argument("--job-id", required=True, help="Job ID")
    fetch_parser.add_argument("--output-dir", default="./results", help="Output directory")
    fetch_parser.add_argument("--wait", action="store_true", help="Wait for job to complete first")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = ThreeDAPIClient(api_key=args.api_key, base_url=args.base_url, timeout=args.timeout)
        
        if args.command == "start-miniature":
            job_id = client.start_miniature(
                description=args.description,
                style=args.style,
                size=args.size,
                output_format=args.output_format
            )
            print(json.dumps({"job_id": job_id, "status": "submitted"}))
            
            if args.wait:
                result = client.wait_for_completion(job_id)
                print(f"Job completed: {json.dumps(result)}")
        
        elif args.command == "start-generation":
            job_id = client.start_generation(
                prompt=args.prompt,
                model=args.model,
                output_format=args.output_format
            )
            print(json.dumps({"job_id": job_id, "status": "submitted"}))
            
            if args.wait:
                result = client.wait_for_completion(job_id)
                print(f"Job completed: {json.dumps(result)}")
        
        elif args.command == "status":
            result = client.get_status(args.job_id)
            print(json.dumps(result))
            
            if args.poll:
                while result.get("status") not in ("completed", "failed"):
                    time.sleep(args.poll_interval)
                    result = client.get_status(args.job_id)
                    print(json.dumps(result))
        
        elif args.command == "fetch-result":
            if args.wait:
                client.wait_for_completion(args.job_id)
            
            filepath = client.fetch_result(args.job_id, args.output_dir)
            print(json.dumps({"filepath": filepath, "status": "downloaded"}))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
