"""
DA13 Authentication & Authorization Middleware
==============================================

Provides API key validation, role-based access control (RBAC),
and token-bucket rate limiting for the DA13 cluster API.
"""

import os
import time
import json
import base64
import hmac
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Set, List


class UserRole(str, Enum):
    ADMIN = "admin"            # Full cluster control + scaling + validation
    VALIDATOR = "validator"    # Submit validation and batch tasks
    OPERATOR = "operator"      # View health, scale cluster, view metrics
    READONLY = "readonly"      # View metrics and health only


@dataclass
class ClientContext:
    client_id: str
    role: UserRole
    rate_limit_qps: float = 1000.0
    tokens: float = 1000.0
    last_update: float = field(default_factory=time.time)


class AuthMiddleware:
    """Authenticates API keys and enforces RBAC permissions."""

    # Default configured keys
    DEFAULT_KEYS = {
        "da13-admin-key-2026": ("admin-client", UserRole.ADMIN),
        "da13-validator-key-2026": ("validator-app", UserRole.VALIDATOR),
        "da13-operator-key-2026": ("ops-agent", UserRole.OPERATOR),
        "da13-readonly-key-2026": ("monitor-reader", UserRole.READONLY)
    }

    @classmethod
    def from_env(cls, env: Optional[Dict[str, str]] = None) -> "AuthMiddleware":
        """Load additional public API keys from environment variables."""
        env_map = os.environ if env is None else env
        custom_keys: Dict[str, Any] = {}

        raw_keys = env_map.get("DA13_API_KEYS", "").strip()
        if raw_keys:
            for chunk in raw_keys.split(","):
                item = chunk.strip()
                if not item or ":" not in item:
                    continue
                key, role_name = [part.strip() for part in item.split(":", 1)]
                try:
                    role = UserRole(role_name.lower())
                except ValueError:
                    continue
                custom_keys[key] = (f"env-client-{len(custom_keys) + 1}", role)

        legacy_key = env_map.get("DA13_PUBLIC_API_KEY", "").strip()
        if legacy_key:
            custom_keys.setdefault(legacy_key, ("public-renter", UserRole.VALIDATOR))

        return cls(custom_keys=custom_keys)

    ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
        UserRole.ADMIN: {"validate", "validate_batch", "scale", "health", "metrics", "billing", "clients"},
        UserRole.VALIDATOR: {"validate", "validate_batch", "health", "metrics", "billing"},
        UserRole.OPERATOR: {"scale", "health", "metrics", "billing", "clients"},
        UserRole.READONLY: {"health", "metrics", "billing"}
    }

    def __init__(self, custom_keys: Optional[Dict[str, Any]] = None):
        self.key_store = self.DEFAULT_KEYS.copy()
        if custom_keys:
            self.key_store.update(custom_keys)
        self.clients: Dict[str, ClientContext] = {}
        self.registered_clients: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

    @classmethod
    def issue_jwt_token(cls, client_id: str, role: UserRole, secret: Optional[str] = None, ttl_seconds: int = 3600) -> str:
        """Signs a compact HS256 JWT for dashboard/admin access."""
        secret_value = (secret or os.environ.get("DA13_JWT_SECRET") or "daxda-da13-dev-secret").encode("utf-8")
        issued_at = int(time.time())
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": client_id,
            "role": role.value if isinstance(role, UserRole) else str(role),
            "iat": issued_at,
            "exp": issued_at + ttl_seconds,
        }
        header_b64 = cls._b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        payload_b64 = cls._b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature = hmac.new(secret_value, signing_input, hashlib.sha256).digest()
        return f"{header_b64}.{payload_b64}.{cls._b64url_encode(signature)}"

    def authenticate_jwt(self, token: Optional[str]) -> Optional[ClientContext]:
        """Verifies an HS256 JWT and returns the associated client context."""
        if not token:
            return None
        token = token.strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, signature = parts
        secret_value = (os.environ.get("DA13_JWT_SECRET") or "daxda-da13-dev-secret").encode("utf-8")
        expected_signature = self._b64url_encode(hmac.new(secret_value, f"{header_b64}.{payload_b64}".encode("utf-8"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected_signature):
            return None

        try:
            padding = "=" * (-len(payload_b64) % 4)
            payload = json.loads(base64.urlsafe_b64decode((payload_b64 + padding).encode("utf-8")))
        except (TypeError, ValueError):
            return None

        exp = payload.get("exp")
        if exp is not None and int(exp) < time.time():
            return None

        client_id = payload.get("sub") or "anonymous-guest"
        role_name = payload.get("role", "validator")
        try:
            role = UserRole(role_name.lower())
        except ValueError:
            role = UserRole.VALIDATOR

        if client_id not in self.clients:
            self.clients[client_id] = ClientContext(client_id=client_id, role=role)
        return self.clients[client_id]

    def register_client(self, client_id: str, api_key: str, role: UserRole, **metadata: Any) -> Dict[str, Any]:
        """Registers a new approved client key for external rental access."""
        if not client_id or not api_key:
            raise ValueError("client_id and api_key are required")
        self.key_store[api_key] = (client_id, role)
        record = {
            "client_id": client_id,
            "role": role.value,
            "api_key": api_key,
            "active": True,
            "registered_at": time.time(),
            "metadata": metadata,
        }
        self.registered_clients[client_id] = record
        self.clients.setdefault(client_id, ClientContext(client_id=client_id, role=role))
        return record

    def list_clients(self) -> List[Dict[str, Any]]:
        """Returns a list of all registered clients."""
        return [
            {
                "client_id": client_id,
                "role": entry["role"],
                "active": entry["active"],
                "registered_at": entry["registered_at"],
            }
            for client_id, entry in sorted(self.registered_clients.items())
        ]

    def authenticate(self, api_key: Optional[str]) -> Optional[ClientContext]:
        """Validates API key and returns client context."""
        if not api_key:
            # Default anonymous guest mapped to validator for development/testing
            return ClientContext(client_id="anonymous-guest", role=UserRole.VALIDATOR)

        # Constant-time comparison
        for valid_key, (client_id, role) in self.key_store.items():
            if hmac.compare_digest(api_key, valid_key):
                if client_id not in self.clients:
                    self.clients[client_id] = ClientContext(client_id=client_id, role=role)
                return self.clients[client_id]

        return None

    def check_permission(self, client: ClientContext, action: str) -> bool:
        """Verifies if the client has permission to perform the requested action."""
        perms = self.ROLE_PERMISSIONS.get(client.role, set())
        return action in perms

    def check_rate_limit(self, client: ClientContext) -> bool:
        """Token-bucket rate limit algorithm."""
        now = time.time()
        elapsed = now - client.last_update
        client.last_update = now

        # Replenish tokens
        client.tokens = min(client.rate_limit_qps, client.tokens + (elapsed * client.rate_limit_qps))

        if client.tokens >= 1.0:
            client.tokens -= 1.0
            return True
        return False
