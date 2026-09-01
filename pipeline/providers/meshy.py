"""
Aurelia 3D Pipeline -- Meshy Provider
=====================================
Implements the BaseProvider interface for Meshy's Image-to-3D API.
Supports multi-image generation (up to 4 views) for better accuracy.

API Docs: https://docs.meshy.ai/
"""

import base64
import json
import time
import requests
from pathlib import Path
from typing import Optional

from .base import BaseProvider, GenerationRequest, GenerationResult


class MeshyProvider(BaseProvider):
    """Meshy AI 3D generation provider."""

    @property
    def name(self) -> str:
        return "meshy"

    def _headers(self) -> dict:
        """Build API request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _upload_image(self, image_path: Path) -> str:
        """
        Encode an image as a data URL for the Meshy API.
        Meshy accepts either URLs or base64-encoded data URIs.
        """
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")
        suffix = image_path.suffix.lower().strip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(suffix, "image/png")
        return f"data:{mime};base64,{img_data}"

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Generate a 3D model using Meshy's multi-image-to-3D endpoint.

        Flow:
        1. Encode reference images as base64 data URIs
        2. POST to /openapi/v1/image-to-3d (or multi-image endpoint)
        3. Poll task status until complete
        4. Download the GLB result
        """
        api_base = self.config.get("api_base", "https://api.meshy.ai")
        print(f"  [{self.name}] Starting 3D generation...")
        print(f"  [{self.name}] Reference images: {len(request.reference_images)}")

        # Prepare image data URIs
        image_urls = []
        for img_path in request.reference_images[:4]:  # Meshy supports up to 4
            if img_path.exists():
                print(f"    Encoding: {img_path.name}")
                image_urls.append(self._upload_image(img_path))
            else:
                print(f"    [WARN] Skipping missing: {img_path}")

        if not image_urls:
            return GenerationResult(
                success=False,
                provider=self.name,
                error_message="No valid reference images found"
            )

        # Determine endpoint based on image count
        if len(image_urls) > 1:
            endpoint = f"{api_base}/openapi/v1/multi-image-to-3d"
            payload = {
                "image_urls": image_urls,
                "should_texture": request.enable_texture,
                "topology": request.topology,
                "target_polycount": 50000,
            }
        else:
            endpoint = f"{api_base}/openapi/v1/image-to-3d"
            payload = {
                "image_url": image_urls[0],
                "should_texture": request.enable_texture,
                "topology": request.topology,
                "target_polycount": 50000,
            }

        # Submit generation task
        print(f"  [{self.name}] Submitting to {endpoint}...")
        try:
            resp = requests.post(endpoint, headers=self._headers(), json=payload, timeout=30)
            resp.raise_for_status()
            task_data = resp.json()
            task_id = task_data.get("result", task_data.get("id", ""))
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
                "images_used": len(image_urls),
                "topology": request.topology,
                "textured": request.enable_texture,
            }
        )

    def _poll_task(self, api_base: str, task_id: str, timeout: int = 600, interval: int = 10) -> dict:
        """
        Poll a Meshy task until completion or timeout.

        Args:
            api_base: API base URL
            task_id: Task ID to poll
            timeout: Maximum wait time in seconds
            interval: Polling interval in seconds

        Returns:
            dict with 'success', 'model_url', or 'error'
        """
        endpoint = f"{api_base}/openapi/v1/image-to-3d/{task_id}"
        elapsed = 0

        while elapsed < timeout:
            try:
                resp = requests.get(endpoint, headers=self._headers(), timeout=15)
                resp.raise_for_status()
                data = resp.json()
                status = data.get("status", "").lower()

                if status == "succeeded":
                    print(f"  [{self.name}] [OK] Generation completed!")
                    model_urls = data.get("model_urls", {})
                    glb_url = model_urls.get("glb") or model_urls.get("obj")
                    return {"success": True, "model_url": glb_url, "data": data}

                elif status in ("failed", "expired"):
                    error = data.get("task_error", {}).get("message", "Unknown error")
                    print(f"  [{self.name}] [FAIL] Generation failed: {error}")
                    return {"success": False, "error": error}

                else:
                    progress = data.get("progress", 0)
                    print(f"  [{self.name}] Status: {status} ({progress}%) -- waiting {interval}s...")

            except requests.exceptions.RequestException as e:
                print(f"  [{self.name}] Poll error: {e} -- retrying...")

            time.sleep(interval)
            elapsed += interval

        return {"success": False, "error": f"Timed out after {timeout}s"}

    def _download_model(self, url: str, output_dir: Path, name: str) -> Path:
        """Download a GLB model from Meshy."""
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
        api_base = self.config.get("api_base", "https://api.meshy.ai")
        endpoint = f"{api_base}/openapi/v1/image-to-3d/{task_id}"

        resp = requests.get(endpoint, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()
