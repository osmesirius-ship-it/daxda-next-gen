#!/usr/bin/env python3
"""Build a deterministic content manifest for the V10 package."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXCLUDE = {"MANIFEST.json"}


def main() -> None:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.name in EXCLUDE or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        raw = path.read_bytes()
        files.append({
            "path": relative,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    manifest = {
        "package": "DAXDA_V10_MASTER",
        "version": "10.0.0-REASONER-FIREWALL-EVAL-CANDIDATE",
        "created_utc": "2026-07-21",
        "claim_boundary": "Architecture and integration candidate; no external reasoner or capability validation is bundled.",
        "full_run_operation_count": 886,
        "files": files,
    }
    encoded = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    (ROOT / "MANIFEST.json").write_bytes(encoded)
    print(json.dumps({"files": len(files), "manifest_sha256": hashlib.sha256(encoded).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()

