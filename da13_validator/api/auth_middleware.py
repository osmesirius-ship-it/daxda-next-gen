"""
DA13 Authentication & Authorization Middleware
==============================================

Provides API key validation, role-based access control (RBAC),
and token-bucket rate limiting for the DA13 cluster API.
"""

import time
import hmac
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Set


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

    ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
        UserRole.ADMIN: {"validate", "validate_batch", "scale", "health", "metrics"},
        UserRole.VALIDATOR: {"validate", "validate_batch", "health", "metrics"},
        UserRole.OPERATOR: {"scale", "health", "metrics"},
        UserRole.READONLY: {"health", "metrics"}
    }

    def __init__(self, custom_keys: Optional[Dict[str, Any]] = None):
        self.key_store = self.DEFAULT_KEYS.copy()
        if custom_keys:
            self.key_store.update(custom_keys)
        self.clients: Dict[str, ClientContext] = {}

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
