from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SOURCE_FILES"
EXPECTED = {
    "daxda_engine_v5_2.py": "4a41aba1268fcd3aae60904c76dff0a6d5c9c5cc6865380079c0eedd65000cb7",
    "build_v5_2_hidden_dataset.py": "91093b32fd2bfce2d615e694065f28ec67a5ca3f2920da06c91f035f4dbbebc8",
    "daxda_v5_2_hidden_test.json": "6540fcf2d4d5e61e5c50b16ef584cb1c058136799370eff5e702cdd1b5159ee9",
    "run_v5_2_hidden_audit.py": "e700f4c64914468a7eb512ebc33fb82cec441801ea338079f23190b8d65c662d",
    "daxda_v5_2_preregistered_manifest.json": "db97a763f1897678e63b336f5cf694c46493b6ccc740dc4c0784244f69fb8f45"
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    print("DAXDA-o V5.2 package integrity check")
    print("=" * 44)
    failures = 0
    for name, expected in EXPECTED.items():
        path = SOURCE / name
        if not path.exists():
            print(f"MISSING  {name}")
            failures += 1
            continue
        observed = sha256(path)
        status = "MATCH" if observed == expected else "MISMATCH"
        print(f"{status:8} {name}")
        print(f"  expected: {expected}")
        print(f"  observed: {observed}")
        if observed != expected:
            failures += 1

    if failures:
        print(f"\nIntegrity check completed with {failures} issue(s).")
        return 1
    print("\nAll required source hashes match.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
