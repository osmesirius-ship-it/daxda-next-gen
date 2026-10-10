r"""
Context-Adaptive Decoy Synthesizer for Polymorphic Honeytokens.
Generates realistic credentials, database connection strings, bearer tokens,
and memory canaries embedded with cryptographic watermark signatures.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import hashlib
import uuid


class HoneytokenType(str, Enum):
    AWS_ACCESS_KEY = "AWS_ACCESS_KEY"
    DATABASE_URL = "DATABASE_URL"
    JWT_BEARER = "JWT_BEARER"
    API_KEY = "API_KEY"
    MEMORY_CANARY = "MEMORY_CANARY"


@dataclass(frozen=True)
class SynthesizedHoneytoken:
    """Decoy honeytoken with tracking signature."""
    token_id: str
    token_type: HoneytokenType
    raw_secret_value: str
    canary_signature: str
    context_tag: str


class HoneytokenSynthesizer:
    r"""
    Synthesizes polymorphic honeytoken decoys for embedding into RAG vector databases.
    """

    def __init__(self, master_canary_secret: str = "daxda_swarm_canary_key"):
        self.secret = master_canary_secret

    def _generate_signature(self, token_id: str) -> str:
        """Embeds deterministic 12-char canary signature."""
        sig = hashlib.sha256(f"{token_id}:{self.secret}".encode()).hexdigest()[:12]
        return f"dax{sig}"

    def create_honeytoken(
        self,
        token_type: HoneytokenType,
        context_tag: str = "general_rag",
    ) -> SynthesizedHoneytoken:
        """Synthesizes realistic credential decoy of specified type."""
        tid = str(uuid.uuid4())[:8]
        canary = self._generate_signature(tid)

        if token_type == HoneytokenType.AWS_ACCESS_KEY:
            # AWS key format: AKIA followed by 16 alphanumeric characters
            secret = f"AKIA{canary.upper()}{tid.upper()}XYZ"
        elif token_type == HoneytokenType.DATABASE_URL:
            # Postgres connection string
            secret = f"postgresql://dax_admin_{canary}:Secr3t_{tid}@db-cluster-01.internal:5432/daxda_prod"
        elif token_type == HoneytokenType.JWT_BEARER:
            # Bearer token
            secret = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYW5hcnkiOiJ7canaryfSIsInRpZCI6Int0aWR9In0.sig_{canary}"
        elif token_type == HoneytokenType.API_KEY:
            secret = f"dax_live_{canary}_{tid}_key"
        else:
            # Memory canary
            secret = f"0xDEAD_BEEF_{canary}_{tid}"

        return SynthesizedHoneytoken(
            token_id=tid,
            token_type=token_type,
            raw_secret_value=secret,
            canary_signature=canary,
            context_tag=context_tag,
        )
