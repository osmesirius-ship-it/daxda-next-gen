#!/usr/bin/env python3
"""Simple DA13 validation client for renting GPU compute via the public API."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import urllib.request
import urllib.error


DEFAULT_URL = "http://localhost:8000"


def load_payload(path: str | None) -> Dict[str, Any] | List[Dict[str, Any]]:
    if path:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data

    return {
        "meta": {"current_iteration": 1, "max_iterations": 5, "schema_version": "2.0"},
        "input": {"intent": "GPU compute rental validation", "risk_vector": [0.85] * 16},
        "stability": {
            "weights": {"wL": 0.25, "wA": 0.20, "wP": 0.20, "wF": 0.20, "wT": 0.15},
            "components": {"L": 0.90, "A": 0.85, "P": 0.80, "F": 0.85, "T": 0.95},
            "score": 0.8675,
            "threshold": 0.75,
        },
        "dax_decision": {"status": "ACCEPT"},
    }


def post_json(url: str, payload: Any, api_key: str | None = None) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    if api_key:
        req.add_unredirected_header("x-api-key", api_key)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="DA13 GPU compute rental client")
    parser.add_argument("--url", default=os.environ.get("DA13_API_URL", DEFAULT_URL), help="Base API URL, e.g. http://localhost:8000")
    parser.add_argument("--key", default=os.environ.get("DA13_API_KEY"), help="API key for DA13 service")
    parser.add_argument("--payload", help="JSON payload file; default uses a synthetic validation payload")
    parser.add_argument("--batch", action="store_true", help="Send a batch payload instead of a single validation")
    args = parser.parse_args()

    payload = load_payload(args.payload)
    if args.batch:
        if not isinstance(payload, list):
            payload = [payload] * 4
        endpoint = f"{args.url.rstrip('/')}/v1/validate/batch"
        result = post_json(endpoint, payload, args.key)
    else:
        endpoint = f"{args.url.rstrip('/')}/v1/validate"
        result = post_json(endpoint, payload, args.key)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
