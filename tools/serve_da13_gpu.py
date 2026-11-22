#!/usr/bin/env python3
"""Launch the DA13 GPU compute service in a Dockerized environment."""

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("DA13_BILLING_RATE", "0.008")
os.environ.setdefault("DA13_API_KEYS", "da13-public-renter:validator,da13-admin-renter:admin")
os.environ.setdefault("DA13_PUBLIC_API_KEY", "da13-public-renter")

from da13_validator.api.rest_server import create_fastapi_app


app = create_fastapi_app()
if app is None:
    raise RuntimeError("FastAPI is not available. Install requirements first.")


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Run the DA13 GPU validator service.")
    parser.add_argument("--host", default=os.environ.get("DA13_HOST", "0.0.0.0"), help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("DA13_API_PORT", "8000")), help="Bind port (default: 8000)")
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
