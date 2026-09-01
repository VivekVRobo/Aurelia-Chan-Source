"""
Aurelia 3D Pipeline -- Tripo Provider
======================================
Implements the BaseProvider interface for Tripo's V3 Image-to-3D API.
Supports single and multi-view image generation.

API Docs: https://developers.tripo3d.com
"""

import base64
import json
import time
import requests
from pathlib import Path
from typing import Optional

from .base import BaseProvider, GenerationRequest, GenerationResult


class TripoProvider(BaseProvider):
    """Tripo AI 3D generation provider (V3 API)."""

    @property
    def name(self) -> str:
        return "tripo"

    def _headers(self) -> dict:
        """Build API request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _upload_image_to_tripo(self, image_path: Path) -> str:
        """
        Upload an image to Tripo and get a file token.
        Tripo V3 requires pre-uploading images before generation.
        """
        api_base = self.config.get("api_base", "https://api.tripo3d.ai/v3")
        upload_url = f"{api_base}/upload"

        with open(image_path, "rb") as f:
            files = {"file": (image_path.name, f, "image/png")}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            resp = requests.post(upload_url, headers=headers, files=files, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("image_token", "")

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate a 3D model using Tripo's V3 image-to-model endpoint.

        Flow:
        1. Upload reference images to Tripo
        2. POST generation task
        3. Poll for completion
        4. Download the GLB result
        """
        api_base = self.config.get("api_base", "https://api.tripo3d.ai/v3")
        print(f"  [{self.name}] Starting 3D generation...")
        print(f"  [{self.name}] Reference images: {len(request.reference_images)}")

        # Upload images and get tokens
        image_tokens = []
        for img_path in request.reference_images[:4]:
            if img_path.exists():
                print(f"    Uploading: {img_path.name}")
                try:
                    token = self._upload_image_to_tripo(img_path)
                    if token:
                        image_tokens.append(token)
                except Exception as e:
                    print(f"    [WARN] Upload failed for {img_path.name}: {e}")
            else:
                print(f"    [WARN] Skipping missing: {img_path}")

        if not image_tokens:
            return GenerationResult(
                success=False,
                provider=self.name,
                error_message="No images could be uploaded"
            )

        # Determine endpoint based on image count
        if len(image_tokens) > 1:
            endpoint = f"{api_base}/task"
            payload = {
                "type": "multi_view_to_model",
                "file": {
                    "type": "image",
                    "file_tokens": image_tokens
                }
            }
        else:
            endpoint = f"{api_base}/task"
            payload = {
                "type": "image_to_model",
                "file": {
                    "type": "image",
                    "file_token": image_tokens[0]
                }
            }

        # Submit generation task
        print(f"  [{self.name}] Submitting generation task...")
        try:
            resp = requests.post(endpoint, headers=self._headers(), json=payload, timeout=30)
            resp.raise_for_status()
            task_data = resp.json()
            task_id = task_data.get("data", {}).get("task_id", "")
            print(f"  [{self.name}] Task created: {task_id}")
        except requests.exceptions.RequestException as e:
            return GenerationResult(
                success=False,
                provider=self.name,
                error_message=f"API request failed: {e}"
            )

        # Poll for completion
        result = self._poll_task(api_base, task_id)
        if not result["success"]:
            return GenerationResult(
                success=False,
                provider=self.name,
                task_id=task_id,
                error_message=result.get("error", "Generation failed")
            )

        # Download the GLB
        model_url = result.get("model_url")
        if not model_url:
            return GenerationResult(
                success=False,
                provider=self.name,
                task_id=task_id,
                error_message="No model URL in completed task"
            )

        output_path = self._download_model(model_url, request.output_dir, request.generation_name)

        return GenerationResult(
            success=True,
            provider=self.name,
            model_path=output_path,
            task_id=task_id,
            metadata={
                "images_used": len(image_tokens),
            }
        )

    def _poll_task(self, api_base: str, task_id: str, timeout: int = 600, interval: int = 10) -> dict:
        """Poll a Tripo task until completion or timeout."""
        endpoint = f"{api_base}/task/{task_id}"
        elapsed = 0

        while elapsed < timeout:
            try:
                resp = requests.get(endpoint, headers=self._headers(), timeout=15)
                resp.raise_for_status()
                data = resp.json()
                task_data = data.get("data", {})
                status = task_data.get("status", "").lower()

                if status == "success":
                    print(f"  [{self.name}] [OK] Generation completed!")
                    output = task_data.get("output", {})
                    model_url = output.get("model", output.get("pbr_model", ""))
                    return {"success": True, "model_url": model_url, "data": task_data}

                elif status in ("failed", "cancelled", "expired"):
                    error = task_data.get("message", "Unknown error")
                    print(f"  [{self.name}] [FAIL] Generation failed: {error}")
                    return {"success": False, "error": error}

                else:
                    progress = task_data.get("progress", 0)
                    print(f"  [{self.name}] Status: {status} ({progress}%) -- waiting {interval}s...")

            except requests.exceptions.RequestException as e:
                print(f"  [{self.name}] Poll error: {e} -- retrying...")

            time.sleep(interval)
            elapsed += interval

        return {"success": False, "error": f"Timed out after {timeout}s"}

    def _download_model(self, url: str, output_dir: Path, name: str) -> Path:
        """Download a GLB model from Tripo."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{name}.glb"

        print(f"  [{self.name}] Downloading model to {output_path}...")
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(resp.content)

        size_mb = len(resp.content) / (1024 * 1024)
        print(f"  [{self.name}] [OK] Downloaded: {output_path} ({size_mb:.1f} MB)")
        return output_path

    def check_status(self, task_id: str) -> dict:
        """Check the status of a pending generation task."""
        api_base = self.config.get("api_base", "https://api.tripo3d.ai/v3")
        endpoint = f"{api_base}/task/{task_id}"

        resp = requests.get(endpoint, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()
