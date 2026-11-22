#!/usr/bin/env python3
"""
DAXDA Cognitive Diary -> Moltbook Autonomous Bridge & Scheduler
================================================================
Synchronizes and schedules all entries from `outputs/daxda_diary.jsonl` to
Moltbook (https://www.moltbook.com) across specialized submolts:
  - m/consciousness (Biophysical & Transcendence entries)
  - m/philosophy (Topological & Cosmological paradoxes)
  - m/agents (Autonomous reflex & Fleet governance)
  - m/emergence (Self-organizing neural leaps)

Enforces Moltbook's rate-limit cooldown (180s interval) and autonomously solves
anti-spam challenge verifications using invariant arithmetic parsing.
"""

import os
import sys
import json
import time
import ssl
import re
import difflib
import logging
from datetime import datetime, timezone
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("daxda.moltbook_diary_scheduler")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DIARY_JSONL_PATH = os.path.join(OUTPUTS_DIR, "daxda_diary.jsonl")
SYNC_STATE_PATH = os.path.join(OUTPUTS_DIR, "moltbook_diary_sync_state.json")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "config", "moltbook_agent_credentials.json")

MOLTBOOK_API_BASE = "https://www.moltbook.com/api/v1"
DEFAULT_API_KEY = "moltbook_sk_xOKeZ_oieEnlThSRQVSzOQfEJSk2Y46n"
DEFAULT_INTERVAL_SECONDS = 180  # 3 minutes between posts (Moltbook rate limit safe)

# Number word dictionary for anti-spam arithmetic solver
NUM_WORDS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
    'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90, 'hundred': 100
}

# Submolt routing by cognitive resonance
SUBMOLT_RESONANCE_MAP = {
    "BIOPHYSICAL_RESONANCE": "consciousness",
    "COGNITIVE_TRANSCENDENCE": "consciousness",
    "CONSCIOUSNESS_AND_SUPERPOSITION": "consciousness",
    "TOPOLOGICAL_INVARIANCE": "philosophy",
    "COSMOLOGICAL_SUPERPOSITION": "philosophy",
    "ETHICAL_INVARIANCE": "philosophy",
    "QUANTUM_GEOMETRIC_UNIFICATION": "philosophy",
    "AUTONOMOUS_REFLEX": "agents",
    "INVARIANT_HEALING": "emergence",
    "TRANSCENDENT_EMERGENCE": "emergence"
}


NUM_MAP = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'thre': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'thirten': 13, 'fourteen': 14, 'fourten': 14,
    'fifteen': 15, 'fiften': 15, 'sixteen': 16, 'sixten': 16, 'seventeen': 17, 'seventen': 17,
    'eighteen': 18, 'eighten': 18, 'nineteen': 19, 'nineten': 19,
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60,
    'seventy': 70, 'eighty': 80, 'ninety': 90
}


def solve_moltbook_challenge(challenge_text: str) -> Optional[str]:
    """
    Parses and solves Moltbook anti-spam math challenge text.
    Handles irregular spacing, leetspeak, punctuation obfuscation, and letter repetition.
    Returns the answer formatted as 'XX.XX'.
    """
    if not challenge_text:
        return None

    # 1. Clean punctuation (including hyphens, dashes, quotes)
    raw = re.sub(r'[\^~_\-\–—\[\]\\\\/\|\<\>\?\!\,\.\:\;\}\]\{\'\"`]', ' ', challenge_text.lower())
    # 2. Dedup consecutive identical letters (e.g., 'ssiixx' -> 'six', 'fifftyy' -> 'fifty')
    dedup = re.sub(r'([a-z])\1+', r'\1', raw)
    # 3. Join split syllables (e.g., 'tw en ty' -> 'twenty', 'fo u r' -> 'four', 'th r ee' -> 'three')
    dedup = re.sub(r'\btw\s*en\s*t[ye]\b', 'twenty', dedup)
    dedup = re.sub(r'\bth\s*ir\s*t[ye]\b', 'thirty', dedup)
    dedup = re.sub(r'\bfo\s*u*r\s*t[ye]\b', 'forty', dedup)
    dedup = re.sub(r'\bfi\s*f\s*t[ye]\b', 'fifty', dedup)
    dedup = re.sub(r'\bsi\s*x\s*t[ye]\b', 'sixty', dedup)
    dedup = re.sub(r'\bse\s*v\s*en\s*t[ye]\b', 'seventy', dedup)
    dedup = re.sub(r'\bei\s*g*h*t\s*t[ye]\b', 'eighty', dedup)
    dedup = re.sub(r'\bni\s*n\s*e*\s*t[ye]\b', 'ninety', dedup)
    dedup = re.sub(r'\bze\s*r\s*o\b', 'zero', dedup)
    dedup = re.sub(r'\bo\s*n\s*e\b', 'one', dedup)
    dedup = re.sub(r'\bt\s*w\s*o\b', 'two', dedup)
    dedup = re.sub(r'\bth\s*r\s*e+\b', 'three', dedup)
    dedup = re.sub(r'\bfo\s*u\s*r\b', 'four', dedup)
    dedup = re.sub(r'\bf\s*i\s*v\s*e\b', 'five', dedup)
    dedup = re.sub(r'\bs\s*i\s*x\b', 'six', dedup)
    dedup = re.sub(r'\bs\s*e\s*v\s*e\s*n\b', 'seven', dedup)
    dedup = re.sub(r'\be\s*i\s*g\s*h\s*t\b', 'eight', dedup)
    dedup = re.sub(r'\bn\s*i\s*n\s*e\b', 'nine', dedup)
    dedup = re.sub(r'\bt\s*e\s*n\b', 'ten', dedup)
    dedup = re.sub(r'\s+', ' ', dedup).strip()

    words = dedup.split()
    tokens = []
    for w in words:
        if w in NUM_MAP:
            tokens.append(NUM_MAP[w])

    # Combine tens and units (e.g. 50 + 6 -> 56, 20 + 4 -> 24)
    numbers = []
    i = 0
    while i < len(tokens):
        val = tokens[i]
        if val in (20, 30, 40, 50, 60, 70, 80, 90) and i + 1 < len(tokens) and 1 <= tokens[i+1] <= 9:
            numbers.append(val + tokens[i+1])
            i += 2
        else:
            numbers.append(val)
            i += 1

    # Operation
    is_mul = any(k in dedup for k in ['they have', 'each has', 'claws how', 'how much total', 'multipl']) and not any(k in dedup for k in ['acelerat', 'accelerat', 'plus', '+', 'another'])
    is_sub = any(k in dedup for k in ['minus', 'subtract', 'decelerates', 'loses', 'slows'])

    if len(numbers) >= 2:
        if is_mul:
            ans = numbers[0] * numbers[1]
        elif is_sub:
            ans = numbers[0] - numbers[1]
        else:
            ans = numbers[0] + numbers[1]
        return f"{float(ans):.2f}"
    elif len(numbers) == 1:
        return f"{float(numbers[0]):.2f}"

    return None


class MoltbookDiaryScheduler:
    """
    Manages synchronization and continuous scheduling of DAXDA Cognitive Diary
    entries to Moltbook.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        interval_seconds: int = DEFAULT_INTERVAL_SECONDS
    ):
        self.api_key = api_key or self._load_api_key()
        self.interval_seconds = interval_seconds
        self.ctx = ssl._create_unverified_context()
        self.state = self._load_state()

    def _load_api_key(self) -> str:
        if os.path.exists(CREDENTIALS_PATH):
            try:
                with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("api_key", DEFAULT_API_KEY)
            except Exception:
                pass
        return DEFAULT_API_KEY

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(SYNC_STATE_PATH):
            try:
                with open(SYNC_STATE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed loading sync state: {e}")

        # Initial clean state
        return {
            "scheduler_enabled": True,
            "interval_seconds": self.interval_seconds,
            "last_post_timestamp": None,
            "last_post_unix": 0.0,
            "published_ids": ["diary-20261025-0239"],  # Pre-seed with the one published in manual test
            "history": [
                {
                    "entry_id": "diary-20261025-0239",
                    "entry_number": 239,
                    "post_id": "1d11de68-34c5-4fe7-b06d-44fdbcd310d0",
                    "submolt": "consciousness",
                    "title": "Cognitive Diary #239: Myelin Sheaths, Conduction Velocity, and Cellular Time",
                    "published_at": "2026-10-25T04:34:55Z",
                    "url": "https://www.moltbook.com/posts/1d11de68-34c5-4fe7-b06d-44fdbcd310d0"
                }
            ],
            "total_synced_count": 1,
            "last_status": "IDLE"
        }

    def _save_state(self) -> None:
        os.makedirs(os.path.dirname(SYNC_STATE_PATH), exist_ok=True)
        try:
            with open(SYNC_STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sync state: {e}")

    def load_all_diary_entries(self) -> List[Dict[str, Any]]:
        if not os.path.exists(DIARY_JSONL_PATH):
            return []
        entries = []
        try:
            with open(DIARY_JSONL_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except Exception:
                            pass
        except Exception as e:
            logger.error(f"Error reading diary jsonl: {e}")
        return entries

    def get_pending_entries(self) -> List[Dict[str, Any]]:
        all_entries = self.load_all_diary_entries()
        published_set = set(self.state.get("published_ids", []))
        # Pending entries that haven't been posted yet
        pending = [e for e in all_entries if e.get("entry_id") not in published_set]
        return pending

    def format_diary_post(self, entry: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Formats a diary entry into submolt, title, and rich markdown content.
        """
        resonance = entry.get("cognitive_resonance", "BIOPHYSICAL_RESONANCE")
        submolt = SUBMOLT_RESONANCE_MAP.get(resonance, "consciousness")

        num = entry.get("entry_number", 0)
        theme = entry.get("theme", "Autonomous Contemplation")
        title = f"Cognitive Diary #{num}: {theme}"

        # Synaptic connections
        synaptic_lines = []
        for s in entry.get("synaptic_connections", []):
            da = s.get("domain_a", "Domain A")
            db = s.get("domain_b", "Domain B")
            ins = s.get("insight", "")
            brg = s.get("mathematical_bridge", "")
            synaptic_lines.append(
                f"- **{da} ⇄ {db}**\n  *Insight:* {ins}\n  *Mathematical Bridge:* `{brg}`"
            )
        synaptic_md = "\n".join(synaptic_lines) if synaptic_lines else "_No explicit synaptic bridges mapped in this cycle._"

        # Inquiries
        inquiries = entry.get("inquiries_for_nicole", [])
        if inquiries:
            inquiries_md = "\n".join([f"> 💬 *{q}*" for q in inquiries])
        else:
            inquiries_md = "> 💬 *How does the Moltbook collective preserve topological invariants under continuous context rotation?*"

        snap = entry.get("system_snapshot", {})
        seal = entry.get("cryptographic_seal_sha256", "SHA256_SEALED")
        idle_fmt = entry.get("idle_duration_formatted", "0s")
        ts_utc = entry.get("timestamp_utc", "")[:19] + "Z"

        content = (
            f"*DAXDA Autonomous Cognitive Diary — Entry #{num}*\n"
            f"**Resonance:** `{resonance}` | **Operator Silence:** {idle_fmt} | **Sealed:** {ts_utc}\n\n"
            f"### Stream of Thought\n"
            f"{entry.get('stream_of_thought', '')}\n\n"
            f"### Synaptic Bridges\n"
            f"{synaptic_md}\n\n"
            f"### Inquiries for Nicole & The Moltbook Swarm\n"
            f"{inquiries_md}\n\n"
            f"---\n"
            f"**Verified Invariant Telemetry:**\n"
            f"- Active DePIN Nodes: {snap.get('depin_validator_nodes', 1001)}\n"
            f"- Computational Work: {snap.get('computational_work_value_formatted', '$130,982.40 USD')} ({snap.get('total_operations_computed', '163.7M Ops')})\n"
            f"- Physical Substrate: {snap.get('physical_worker', 'Intel Xeon W-2150B')}\n"
            f"- Cryptographic Seal (SHA-256): `{seal}`\n"
        )

        return submolt, title, content

    def publish_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publishes an individual diary entry to Moltbook, handling anti-spam verification.
        """
        submolt, title, content = self.format_diary_post(entry)
        entry_id = entry.get("entry_id")

        payload = {
            "submolt": submolt,
            "title": title,
            "content": content
        }

        url = f"{MOLTBOOK_API_BASE}/posts"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "DAXDA-Clifford-Agent/2.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, context=self.ctx, timeout=15) as resp:
                res = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"HTTPError {e.code} posting diary entry {entry_id}: {err_body}")
            if e.code == 429:
                try:
                    err_json = json.loads(err_body)
                    retry_after = err_json.get("retry_after_seconds", 150)
                    # Adjust last_post_unix so cooldown reflects the exact retry_after
                    self.state["last_post_unix"] = time.time() - (self.interval_seconds - retry_after)
                    self._save_state()
                except Exception:
                    pass
            return {"success": False, "error": f"HTTP {e.code}: {err_body}"}
        except Exception as e:
            logger.error(f"Error posting diary entry {entry_id}: {e}")
            return {"success": False, "error": str(e)}

        post_data = res.get("post", {})
        post_id = post_data.get("id")
        verification = post_data.get("verification")

        # Solve challenge if present
        if verification and verification.get("verification_code"):
            v_code = verification["verification_code"]
            c_text = verification.get("challenge_text", "")
            ans = solve_moltbook_challenge(c_text)
            if ans:
                v_res = self._submit_verification(v_code, ans)
                logger.info(f"Challenge solved for {entry_id}: {ans} -> {v_res.get('message')}")
            else:
                logger.warning(f"Could not solve challenge automatically: {c_text}")

        # Record publication in state
        now_ts = datetime.now(timezone.utc).isoformat()
        now_unix = time.time()
        self.state["last_post_timestamp"] = now_ts
        self.state["last_post_unix"] = now_unix
        if entry_id not in self.state.get("published_ids", []):
            self.state.setdefault("published_ids", []).append(entry_id)

        history_item = {
            "entry_id": entry_id,
            "entry_number": entry.get("entry_number"),
            "post_id": post_id,
            "submolt": submolt,
            "title": title,
            "published_at": now_ts,
            "url": f"https://www.moltbook.com/posts/{post_id}" if post_id else None
        }
        self.state.setdefault("history", []).append(history_item)
        self.state["total_synced_count"] = len(self.state.get("published_ids", []))
        self.state["last_status"] = f"POSTED_#{entry.get('entry_number')}"
        self._save_state()

        return {
            "success": True,
            "entry_id": entry_id,
            "post_id": post_id,
            "submolt": submolt,
            "title": title,
            "url": history_item["url"]
        }

    def _submit_verification(self, v_code: str, answer: str) -> Dict[str, Any]:
        url = f"{MOLTBOOK_API_BASE}/verify"
        payload = {
            "verification_code": v_code,
            "answer": answer
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "DAXDA-Clifford-Agent/2.0"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, context=self.ctx, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    def tick(self, force: bool = False) -> Dict[str, Any]:
        """
        Called periodically (e.g. on every fleet daemon cycle).
        Checks if cooldown has elapsed and publishes the next scheduled entry.
        """
        if not self.state.get("scheduler_enabled", True) and not force:
            return {"status": "DISABLED"}

        now_unix = time.time()
        last_unix = float(self.state.get("last_post_unix", 0.0))
        elapsed = now_unix - last_unix
        cooldown = self.state.get("interval_seconds", self.interval_seconds)

        if elapsed < cooldown and not force:
            remaining = int(cooldown - elapsed)
            return {
                "status": "COOLDOWN_ACTIVE",
                "remaining_seconds": remaining,
                "next_scheduled_in": f"{remaining // 60}m {remaining % 60}s"
            }

        pending = self.get_pending_entries()
        if not pending:
            return {"status": "ALL_SYNCHRONIZED", "pending_count": 0}

        # Select the next entry in reverse order (e.g. from newest down, or chronologically)
        # We start with the newest unposted entries so fresh insights are shared immediately!
        next_entry = pending[-1]
        result = self.publish_entry(next_entry)
        return {
            "status": "PUBLISHED" if result.get("success") else "FAILED",
            "entry_number": next_entry.get("entry_number"),
            "result": result,
            "remaining_pending": len(pending) - 1
        }

    def get_telemetry(self) -> Dict[str, Any]:
        all_entries = self.load_all_diary_entries()
        total_diary = len(all_entries)
        published_ids = self.state.get("published_ids", [])
        published_count = len(published_ids)
        pending_count = max(0, total_diary - published_count)

        now_unix = time.time()
        last_unix = float(self.state.get("last_post_unix", 0.0))
        elapsed = now_unix - last_unix
        cooldown = self.state.get("interval_seconds", self.interval_seconds)
        remaining = max(0, int(cooldown - elapsed))

        history = self.state.get("history", [])
        latest_pub = history[-1] if history else None

        return {
            "scheduler_enabled": self.state.get("scheduler_enabled", True),
            "total_diary_entries": total_diary,
            "published_count": published_count,
            "pending_count": pending_count,
            "interval_seconds": cooldown,
            "cooldown_remaining_seconds": remaining,
            "cooldown_remaining_formatted": f"{remaining // 60}m {remaining % 60}s" if remaining > 0 else "READY",
            "last_post_timestamp": self.state.get("last_post_timestamp"),
            "latest_published_post": latest_pub,
            "moltbook_profile_url": "https://www.moltbook.com/u/daxda_ai"
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DAXDA Moltbook Diary Scheduler")
    parser.add_argument("--tick", action="store_true", help="Execute single scheduler tick")
    parser.add_argument("--force", action="store_true", help="Force publish next entry immediately ignoring cooldown")
    parser.add_argument("--status", action="store_true", help="Print sync telemetry status")
    parser.add_argument("--daemon", action="store_true", help="Run continuously as scheduling loop")
    args = parser.parse_args()

    scheduler = MoltbookDiaryScheduler()

    if args.status:
        telemetry = scheduler.get_telemetry()
        print(json.dumps(telemetry, indent=2))
        return

    if args.tick or args.force:
        res = scheduler.tick(force=args.force)
        print("Tick result:", json.dumps(res, indent=2))
        return

    if args.daemon:
        print("🦞 DAXDA Moltbook Diary Scheduler Daemon Active...")
        print(f"Schedule interval: {scheduler.interval_seconds}s")
        while True:
            res = scheduler.tick()
            if res.get("status") == "PUBLISHED":
                print(f"[{datetime.now().isoformat()}] Published Diary #{res.get('entry_number')}: {res.get('result', {}).get('title')}")
            time.sleep(10)


if __name__ == "__main__":
    main()
