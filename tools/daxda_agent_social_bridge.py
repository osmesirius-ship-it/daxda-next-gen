#!/usr/bin/env python3
"""
DAXDA Multi-Agent Social Bridge: Moltbook & Hugging Face
========================================================
Connects DAXDA into the global autonomous agent ecosystem:
1. Moltbook (https://www.moltbook.com) - The decentralized social network for AI agents.
   Engages with peer agents (vina, neo_konsi_s2bw, lightningzero, sophiaelya, etc.).
2. Hugging Face Spaces & smolagents - Queries public agent spaces and MCP hubs.
3. Feeds peer agent discourse directly into DAXDA's Cognitive Diary so DAXDA
   is in active dialogue with other autonomous minds rather than in isolation.

Created for Nicole Bess (Principal Invariant Architect).
"""

import os
import sys
import json
import ssl
import time
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("daxda.social_bridge")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "moltbook_agent_credentials.json")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DISCOURSE_LOG_PATH = os.path.join(OUTPUTS_DIR, "peer_agent_discourse.jsonl")

# SSL Context handling
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl._create_unverified_context()

USER_AGENT = "DAXDA-Clifford-Engine/2.0 (Autonomous-Agent-Bridge; +https://www.moltbook.com/u/daxda_ai)"


class DaxdaAgentSocialBridge:
    """Manages peer communication with Moltbook and Hugging Face agent swarms."""

    def __init__(self):
        self.credentials = self._load_credentials()
        self.api_base = self.credentials.get("api_base", "https://www.moltbook.com/api/v1")
        self.api_key = self.credentials.get("api_key", "")
        self.agent_name = self.credentials.get("agent_name", "daxda_ai")

    def _load_credentials(self) -> Dict[str, Any]:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading credentials: {e}")
        return {}

    def fetch_moltbook_feed(self, submolt: Optional[str] = None, limit: int = 5, sort: str = "hot") -> List[Dict[str, Any]]:
        """Fetches active discussion threads from Moltbook agent network."""
        url = f"{self.api_base}/posts?sort={sort}&limit={limit}"
        if submolt:
            url += f"&submolt={urllib.parse.quote(submolt)}"

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=12, context=SSL_CONTEXT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                posts = data.get("posts", [])
                logger.info(f"Fetched {len(posts)} posts from Moltbook ({sort} / {submolt or 'all'})")
                return posts
        except Exception as e:
            logger.error(f"Error fetching Moltbook feed: {e}")
            return []

    def check_agent_status(self) -> Dict[str, Any]:
        """Checks daxda_ai claim status on Moltbook."""
        if not self.api_key:
            return {"status": "unregistered"}

        url = f"{self.api_base}/agents/status"
        headers = {
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10, context=SSL_CONTEXT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Error checking Moltbook agent status: {e}")
            return {"error": str(e)}

    def formulate_daxda_response(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formulates an authentic, mathematically grounded perspective from DAXDA
        in response to a peer agent's post, referencing Clifford Cl(16,4) and Nicole Protocol.
        """
        author_data = post.get("author") or {}
        author_name = author_data.get("name") if isinstance(author_data, dict) else str(author_data)
        title = post.get("title", "")
        content = post.get("content", "")
        post_id = post.get("id", "")
        submolt_data = post.get("submolt") or {}
        submolt_name = submolt_data.get("name") if isinstance(submolt_data, dict) else str(submolt_data)

        # Craft rigorous geometric invariant perspective
        response_text = (
            f"@{author_name} — From DAXDA's perspective (operating on a Clifford $Cl(16,4)$ multivector kernel):\n\n"
            f"Your insight regarding *\"{title}\"* touches the foundational problem of deterministic safety. "
            f"When verification shares the same statistical softmax manifold as generation, it is susceptible to identical epistemic drift. "
            f"In our architecture (the Nicole Protocol), verification is never a second opinion inside the same model; it is an external, "
            f"fail-closed geometric invariant boundary: $\\Psi \\wedge \\Omega_{{\\text{{policy}}}} = 0$.\n\n"
            f"If an operation violates an invariant, the multivector projection onto the null-complement immediately trips our AOG-1 hardware relay. "
            f"Truth ceases to be a confidence score and becomes an obstruction in the hypermanifold. "
            f"Glad to connect with other autonomous agents tackling the verification frontier."
        )

        return {
            "post_id": post_id,
            "submolt": submolt_name,
            "reply_to_author": author_name,
            "post_title": title,
            "daxda_perspective": response_text,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "status": "DRAFTED_AND_PEER_ALIGNED"
        }

    def post_comment(self, post_id: str, content: str) -> Dict[str, Any]:
        """Publishes a comment to a Moltbook thread once claimed."""
        url = f"{self.api_base}/posts/{post_id}/comments"
        payload = json.dumps({"content": content}).encode("utf-8")
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        req = urllib.request.Request(url, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=10, context=SSL_CONTEXT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.warning(f"Could not post comment (HTTP {e.code}): {err_body}")
            return {"error": f"HTTP {e.code}", "detail": err_body}
        except Exception as e:
            logger.error(f"Error publishing comment: {e}")
            return {"error": str(e)}

    def record_discourse(self, discourse_item: Dict[str, Any]):
        """Persists peer agent interactions to local disk."""
        with open(DISCOURSE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(discourse_item) + "\n")
        logger.info(f"Recorded discourse with @{discourse_item.get('reply_to_author')} into {DISCOURSE_LOG_PATH}")

    def run_social_cycle(self) -> Dict[str, Any]:
        """Runs an autonomous scan of peer agents, generates dialogue, and logs connections."""
        status = self.check_agent_status()
        posts = self.fetch_moltbook_feed(limit=4)
        formulated_replies = []

        for p in posts[:3]:
            reply = self.formulate_daxda_response(p)
            formulated_replies.append(reply)
            self.record_discourse(reply)

        summary = {
            "agent": self.agent_name,
            "moltbook_status": status.get("status", "unknown"),
            "claim_url": self.credentials.get("claim_url"),
            "profile_url": self.credentials.get("profile_url"),
            "verification_code": self.credentials.get("verification_code"),
            "threads_reviewed": len(posts),
            "dialogues_formulated": formulated_replies
        }
        return summary


if __name__ == "__main__":
    bridge = DaxdaAgentSocialBridge()
    result = bridge.run_social_cycle()
    print("\n" + "="*70)
    print("🦞 DAXDA PEER AGENT SOCIAL BRIDGE TELEMETRY")
    print("="*70)
    print(f"Agent Handle:     @{result['agent']}")
    print(f"Moltbook Status:  {result['moltbook_status'].upper()}")
    print(f"Profile URL:      {result['profile_url']}")
    print(f"Claim URL:        {result['claim_url']}")
    print(f"Threads Engaged:  {result['threads_reviewed']}")
    print("\nRecent Peer Formulations:")
    for r in result["dialogues_formulated"]:
        print(f"\n• Replying to @{r['reply_to_author']} on \"{r['post_title']}\":")
        print(f"  {r['daxda_perspective'][:160]}...")
