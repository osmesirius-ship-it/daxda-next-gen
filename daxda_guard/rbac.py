"""DAXDA Guard Tenant Role-Based Access Control & Scope Manager (rbac.py).

Manages enterprise tenant API keys, role permissions (ADMIN, AUDITOR, OPERATOR),
and fine-grained domain scope whitelists.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class TenantProfile:
    tenant_id: str
    tenant_name: str
    api_key: str
    roles: List[str]
    allowed_domains: List[str]
    rate_limit_per_min: int = 10000


MOCK_TENANT_DB: Dict[str, TenantProfile] = {
    "daxda_live_bank_98214": TenantProfile(
        tenant_id="BANK_01",
        tenant_name="JPMorgan Chase & Co.",
        api_key="daxda_live_bank_98214",
        roles=["ADMIN", "OPERATOR"],
        allowed_domains=["finance", "software", "general"]
    ),
    "daxda_live_def_77182": TenantProfile(
        tenant_id="DEFENSE_01",
        tenant_name="Lockheed Martin Corporation",
        api_key="daxda_live_def_77182",
        roles=["ADMIN", "AUDITOR"],
        allowed_domains=["defense", "physics", "software"]
    )
}


class TenantRBACManager:
    def __init__(self):
        self.tenants = MOCK_TENANT_DB

    def authenticate_api_key(self, api_key: str) -> Optional[TenantProfile]:
        """Authenticates an enterprise tenant API key."""
        return self.tenants.get(api_key, None)

    def validate_tenant_scope(self, api_key: str, requested_domain: str) -> Dict[str, Any]:
        """Validates tenant API key and checks whether requested domain is authorized."""
        profile = self.authenticate_api_key(api_key)

        if not profile:
            return {
                "authorized": False,
                "error_code": "GOV_FAIL_01_INVALID_KEY",
                "reason": "Invalid or unauthenticated API Key."
            }

        if requested_domain not in profile.allowed_domains and "*" not in profile.allowed_domains:
            return {
                "authorized": False,
                "error_code": "GOV_FAIL_01_UNAUTHORIZED_SCOPE",
                "reason": f"Domain '{requested_domain}' is not in authorized domain scope for tenant '{profile.tenant_name}'."
            }

        return {
            "authorized": True,
            "tenant_id": profile.tenant_id,
            "tenant_name": profile.tenant_name,
            "roles": profile.roles,
            "allowed_domains": profile.allowed_domains
        }


if __name__ == "__main__":
    rbac = TenantRBACManager()
    
    # Test valid key & scope
    res1 = rbac.validate_tenant_scope("daxda_live_bank_98214", "finance")
    print(f"Test 1 (Valid Bank Key): {res1}")

    # Test unauthorized scope
    res2 = rbac.validate_tenant_scope("daxda_live_bank_98214", "defense")
    print(f"Test 2 (Unauthorized Scope): {res2}")
