# shared/dub_runpod.py — RunPod sync polling for dubbing
from __future__ import annotations

import time

import requests

from shared import config


def is_runpod_backend_url(backend_url: str) -> bool:
    url = (backend_url or "").lower()
    return "runpod.ai" in url or "runpod.io" in url


def poll_runpod_until_output(backend_url: str, payload: dict, timeout: int = 1500) -> dict:
    headers = {
        "Authorization": f"Bearer {config.RUNPOD_API_KEY}",
        "Content-Type": "application/json",
    }
    base = backend_url.rstrip("/")
    run_resp = requests.post(
        f"{base}/run",
        json={"input": payload},
        headers=headers,
        timeout=60,
    )
    run_resp.raise_for_status()
    runpod_job_id = run_resp.json().get("id")
    deadline = time.time() + timeout

    while time.time() < deadline:
        status_data = requests.get(
            f"{base}/status/{runpod_job_id}",
            headers=headers,
            timeout=30,
        ).json()
        status = status_data.get("status")
        if status == "COMPLETED":
            return status_data.get("output") or {}
        if status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"RunPod failed: {status_data.get('error')}")
        time.sleep(5)
    raise TimeoutError("RunPod dubbing timed out")
