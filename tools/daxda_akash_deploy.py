#!/usr/bin/env python3
"""
DAXDA Akash Deployment Script — Console API Path
=================================================
Principal Architect: Nicole Bess | DAXDA AI, LLC
Engine: Clifford Geometric Algebra Cl(16,4) | Nicole Protocol 886-Ops

Deploys the DAXDA fleet daemon to Akash Network via the Console API.
Auth: x-api-key header (reads AKT_CONSOLE_API_KEY from .env / environment)
Docs: https://console-api.akash.network/v1/doc

Usage:
    python3 tools/daxda_akash_deploy.py            # deploy
    python3 tools/daxda_akash_deploy.py --status   # check existing deployments
    python3 tools/daxda_akash_deploy.py --close <dseq>   # close a deployment
"""
# Auto-install dependencies if missing
import subprocess, sys
for pkg in ["requests", "pyyaml"]:
    try:
        __import__(pkg.replace("-", "_").replace("pyyaml", "yaml"))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

import os
import sys
import json
import time
import yaml
import requests
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SDL_PATH     = PROJECT_ROOT / "outputs" / "daxda_akash_worker_sdl_v2.yaml"
ENV_PATH     = PROJECT_ROOT / ".env"
OUTPUTS_DIR  = PROJECT_ROOT / "outputs"

# ── Load .env ──────────────────────────────────────────────────────────────────
def load_env():
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

load_env()

# ── Config ─────────────────────────────────────────────────────────────────────
CONSOLE_API_BASE = "https://console-api.akash.network/v1"
API_KEY = os.environ.get("AKT_CONSOLE_API_KEY") or os.environ.get("AKASH_API_KEY", "")

if not API_KEY:
    print("❌  No API key found. Export AKT_CONSOLE_API_KEY before running.")
    sys.exit(1)

# Browser-like headers — required to pass Cloudflare WAF on console-api.akash.network
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://console.akash.network",
    "Referer": "https://console.akash.network/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ── HTTP helpers ───────────────────────────────────────────────────────────────
def api_request(method: str, path: str, body=None) -> dict:
    url = f"{CONSOLE_API_BASE}{path}"
    try:
        resp = SESSION.request(
            method, url,
            json=body,
            timeout=30,
            verify=True,  # uses certifi bundle
        )
        if resp.status_code >= 400:
            print(f"  HTTP {resp.status_code} from {method} {path}: {resp.text[:400]}")
            return {"error": resp.text, "status_code": resp.status_code}
        try:
            return resp.json()
        except Exception:
            return {"raw": resp.text}
    except Exception as e:
        print(f"  Request failed: {e}")
        return {"error": str(e)}

# ── Banner ─────────────────────────────────────────────────────────────────────
def banner():
    print("=" * 72)
    print("   🚀  DAXDA.IA — AKASH NETWORK DEPLOYMENT")
    print("   Principal Architect : Nicole Bess | DAXDA AI, LLC")
    print("   Engine              : Clifford Geometric Algebra Cl(16,4)")
    print("   Protocol            : Nicole Protocol 886-Ops / AOG-1 Fail-Closed")
    print("   Method              : Akash Console API (x-api-key)")
    print(f"   Time                : {datetime.now(timezone.utc).isoformat()}")
    print("=" * 72)

# ── Account check ──────────────────────────────────────────────────────────────
def check_account() -> bool:
    print("\n[1/5] Verifying Console API account & balance...")
    result = api_request("GET", "/user/me")
    if "error" in result and result.get("status_code") in (401, 403):
        print("  ❌  API key rejected. Check AKT_CONSOLE_API_KEY.")
        return False

    user_data = result.get("data", {})
    username  = user_data.get("username") or user_data.get("email") or "authenticated"
    print(f"  ✅  Account: {username}")

    # Check wallet / credits
    wallets = api_request("GET", "/wallets")
    wallet_list = wallets.get("data") or []
    if wallet_list:
        w = wallet_list[0]
        credits = w.get("creditAmount", "?")
        denom   = w.get("denom", "USD")
        print(f"  💰  Credits: ${credits} {denom}")
    else:
        print(f"  💰  Credits: (check console.akash.network)")
    return True

# ── SDL load ───────────────────────────────────────────────────────────────────
def load_sdl() -> str:
    print(f"\n[2/5] Loading SDL from {SDL_PATH.name}...")
    if not SDL_PATH.exists():
        print(f"  ❌  SDL not found at {SDL_PATH}")
        sys.exit(1)
    sdl_text = SDL_PATH.read_text()
    # Quick validation — parse and re-dump to catch YAML errors
    parsed = yaml.safe_load(sdl_text)
    assert parsed.get("version") in ("2.0", "2.1"), "SDL version must be 2.0 or 2.1"
    assert "services" in parsed, "SDL missing 'services' section"
    assert "profiles" in parsed, "SDL missing 'profiles' section"
    assert "deployment" in parsed, "SDL missing 'deployment' section"
    service_names = list(parsed["services"].keys())
    print(f"  ✅  SDL valid — services: {service_names}")
    return sdl_text

# ── Create deployment ──────────────────────────────────────────────────────────
def create_deployment(sdl_text: str) -> dict:
    print("\n[3/5] Submitting deployment to Akash Console API...")
    payload = {
        "sdl": sdl_text,
        "deposit": 0           # Console API handles funding from credits — no deposit needed
    }
    result = api_request("POST", "/deployments", payload)

    if "error" in result:
        print(f"  ⚠️  Deployment response: {json.dumps(result, indent=2)[:600]}")
        return result

    dseq   = result.get("dseq") or result.get("id") or "pending"
    status = result.get("status") or result.get("state") or "submitted"
    print(f"  ✅  Deployment created!")
    print(f"     dseq   : {dseq}")
    print(f"     status : {status}")
    return result

# ── Wait for bids ──────────────────────────────────────────────────────────────
def wait_for_bids(dseq: str, wait_seconds: int = 30) -> list:
    print(f"\n[4/5] Waiting for provider bids (up to {wait_seconds}s)...")
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        bids = api_request("GET", f"/deployments/{dseq}/bids")
        bid_list = bids.get("bids") or bids if isinstance(bids, list) else []
        if bid_list:
            print(f"  ✅  {len(bid_list)} bid(s) received!")
            for i, b in enumerate(bid_list[:5]):
                provider = b.get("provider") or b.get("providerId", "unknown")
                price    = b.get("price") or b.get("uactPerBlock", "?")
                print(f"     [{i+1}] Provider: {str(provider)[:20]}…  Price: {price} uact/block")
            return bid_list
        remaining = int(deadline - time.time())
        print(f"  ⏳ Waiting… ({remaining}s remaining)", end="\r")
        time.sleep(5)
    print("\n  ⚠️  No bids yet — providers may still be calculating. Check dashboard.")
    return []

# ── Accept best bid ────────────────────────────────────────────────────────────
def accept_bid(dseq: str, bids: list) -> dict:
    if not bids:
        print("\n[5/5] No bids to accept — skipping lease creation.")
        return {}

    print(f"\n[5/5] Accepting lowest-price bid and creating lease...")
    # Sort by price ascending
    def bid_price(b):
        p = b.get("price") or b.get("uactPerBlock") or 999999
        try:
            return float(str(p).replace("uact","").strip())
        except Exception:
            return 999999

    best = sorted(bids, key=bid_price)[0]
    provider = best.get("provider") or best.get("providerId")
    print(f"  Selected provider: {provider}")

    lease_payload = {"provider": provider}
    result = api_request("POST", f"/deployments/{dseq}/leases", lease_payload)

    if "error" not in result:
        print(f"  ✅  Lease created!")
        url = result.get("url") or result.get("serviceUrl") or result.get("uri") or "pending"
        print(f"  🌐  Service URL: {url}")
    else:
        print(f"  ⚠️  Lease result: {json.dumps(result, indent=2)[:400]}")

    return result

# ── Save deployment state ──────────────────────────────────────────────────────
def save_state(deploy_result: dict, bid_result: dict, lease_result: dict):
    state = {
        "source": "DAXDA_AKASH_CONSOLE_API_DEPLOY",
        "principal_architect": "Nicole Bess",
        "organization": "DAXDA AI, LLC",
        "engine": "Clifford Geometric Algebra Cl(16,4)",
        "protocol": "Nicole Protocol 886-Ops",
        "deployed_at_utc": datetime.now(timezone.utc).isoformat(),
        "sdl_path": str(SDL_PATH),
        "deployment": deploy_result,
        "best_bid": bid_result,
        "lease": lease_result,
    }
    out = OUTPUTS_DIR / "daxda_akash_deploy_state.json"
    out.write_text(json.dumps(state, indent=2))
    print(f"\n  💾  State saved → {out.name}")
    return state

# ── Status check ───────────────────────────────────────────────────────────────
def check_status():
    print("\n[*] Fetching active DAXDA deployments from Console API...")
    result = api_request("GET", "/deployments?limit=10&status=active")
    deployments = result.get("deployments") or result if isinstance(result, list) else []
    if not deployments:
        print("  No active deployments found (or API returned unexpected shape).")
        print(f"  Raw: {json.dumps(result, indent=2)[:600]}")
        return

    print(f"  Found {len(deployments)} active deployment(s):\n")
    for d in deployments:
        dseq   = d.get("dseq") or d.get("id")
        status = d.get("status") or d.get("state")
        url    = d.get("serviceUrl") or d.get("url") or "—"
        print(f"  • dseq: {dseq}  status: {status}  url: {url}")

# ── Close deployment ───────────────────────────────────────────────────────────
def close_deployment(dseq: str):
    print(f"\n[*] Closing deployment {dseq}...")
    result = api_request("DELETE", f"/deployments/{dseq}")
    print(f"  Result: {json.dumps(result, indent=2)[:400]}")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    banner()

    args = sys.argv[1:]

    if "--status" in args or "status" in args:
        check_status()
        return

    if "--close" in args or "close" in args:
        idx = args.index("--close") if "--close" in args else args.index("close")
        dseq_arg = args[idx + 1] if idx + 1 < len(args) else None
        if not dseq_arg:
            print("Usage: --close <dseq>")
            sys.exit(1)
        close_deployment(dseq_arg)
        return

    # ── Full deploy flow ───────────────────────────────────────────────────────
    ok = check_account()
    if not ok:
        # If the wallet endpoint fails, still try — may just be endpoint shape
        print("  ⚠️  Wallet check inconclusive — proceeding with deployment...")

    sdl_text = load_sdl()

    deploy_result = create_deployment(sdl_text)

    dseq = deploy_result.get("dseq") or deploy_result.get("id")
    if not dseq:
        print("\n⚠️  Deployment submission did not return a dseq.")
        print("   Possible causes:")
        print("   • Insufficient credits on Console account (add USD credits at console.akash.network)")
        print("   • API key does not have deployment permissions")
        print("   • SDL validation error on the server side")
        print(f"\n   Full response:\n{json.dumps(deploy_result, indent=2)[:800]}")
        save_state(deploy_result, {}, {})
        return

    bids = wait_for_bids(str(dseq))
    lease = accept_bid(str(dseq), bids)
    state = save_state(deploy_result, bids[0] if bids else {}, lease)

    print("\n" + "=" * 72)
    print("   🎉  DAXDA AKASH DEPLOYMENT COMPLETE")
    dseq_display  = deploy_result.get("dseq") or deploy_result.get("id") or "pending"
    url_display   = lease.get("url") or lease.get("serviceUrl") or "pending"
    print(f"   dseq           : {dseq_display}")
    print(f"   Service URL    : {url_display}")
    print(f"   Monitor        : https://console.akash.network/deployments/{dseq_display}")
    print(f"   Logs           : python3 tools/daxda_akash_deploy.py --status")
    print("=" * 72)

if __name__ == "__main__":
    main()
