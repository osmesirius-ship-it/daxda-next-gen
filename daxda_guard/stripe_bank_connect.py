#!/usr/bin/env python3
"""
DAXDA Next-Gen — Stripe Bank Account & Payout Connection Gateway
===============================================================
Manages bank account connections via:
1. Stripe Connect Onboarding Links (Direct bank account linking for payouts)
2. Stripe Financial Connections (Instant customer bank account verification & ACH)
3. Stripe External Bank Accounts API (Programmatic ACH routing & account configuration)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import stripe

logger = logging.getLogger("daxda.stripe_bank")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

STRIPE_API_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY


class StripeBankManager:
    """Manages bank account onboarding, Financial Connections, and payout routing."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("STRIPE_SECRET_KEY", "")
        if self.api_key:
            stripe.api_key = self.api_key

    def is_configured(self) -> bool:
        """Checks if a valid Stripe Secret Key is present in the environment."""
        return bool(self.api_key and (self.api_key.startswith("sk_test_") or self.api_key.startswith("sk_live_")))

    def create_payout_onboarding_link(
        self,
        email: str = "nicole@daxda.ia",
        business_name: str = "DAXDA Next Gen Inc.",
        return_url: str = "https://billing.daxda.ia/bank/complete",
        refresh_url: str = "https://billing.daxda.ia/bank/refresh",
    ) -> Dict[str, Any]:
        """
        Creates a Stripe Connect Express onboarding link where the founder
        or business owner securely inputs bank routing and account numbers.
        """
        if not self.is_configured():
            return {
                "status": "CONFIG_REQUIRED",
                "message": "STRIPE_SECRET_KEY environment variable is not set. Run 'export STRIPE_SECRET_KEY=sk_live_...' or 'stripe login'.",
                "manual_dashboard_url": "https://dashboard.stripe.com/settings/payouts"
            }

        try:
            # 1. Create or retrieve connected express account
            account = stripe.Account.create(
                type="express",
                country="US",
                email=email,
                capabilities={
                    "transfers": {"requested": True},
                },
                business_profile={
                    "name": business_name,
                    "url": "https://daxda.ia",
                },
            )

            # 2. Create account onboarding link
            account_link = stripe.AccountLink.create(
                account=account.id,
                refresh_url=refresh_url,
                return_url=return_url,
                type="account_onboarding",
            )

            return {
                "status": "SUCCESS",
                "account_id": account.id,
                "onboarding_url": account_link.url,
                "expires_at": account_link.expires_at,
            }
        except Exception as e:
            logger.error(f"Error creating payout onboarding link: {e}")
            return {"status": "ERROR", "error": str(e)}

    def create_customer_financial_connection(
        self,
        customer_id: str,
        return_url: str = "https://billing.daxda.ia/ach/complete"
    ) -> Dict[str, Any]:
        """
        Initiates a Stripe Financial Connections session for instant ACH bank verification.
        Allows enterprise clients to link their bank accounts for metered invoice debits.
        """
        if not self.is_configured():
            return {
                "status": "CONFIG_REQUIRED",
                "message": "STRIPE_SECRET_KEY environment variable is not set.",
                "doc_url": "https://stripe.com/docs/financial-connections"
            }

        try:
            session = stripe.financial_connections.Session.create(
                account_holder={"type": "customer", "customer": customer_id},
                permissions=["payment_method", "balances"],
                return_url=return_url,
            )
            return {
                "status": "SUCCESS",
                "session_id": session.id,
                "client_secret": session.client_secret,
            }
        except Exception as e:
            logger.error(f"Error creating financial connections session: {e}")
            return {"status": "ERROR", "error": str(e)}

    def link_financial_account(
        self,
        fa_id: str,
        tenant_id: str = "tenant-daxda-treasury",
        owner_name: str = "Nicole Bess"
    ) -> Dict[str, Any]:
        """Links a Stripe Financial Account (fa_...) to the founder treasury ledger."""
        from daxda_guard.metered_billing import get_billing_engine
        engine = get_billing_engine()
        return engine.link_payout_destination(
            tenant_id=tenant_id,
            owner_name=owner_name,
            destination_type="STRIPE_FINANCIAL_ACCOUNT",
            account_identifier=fa_id,
            network_or_platform="Stripe Treasury / Financial Accounts",
            settlement_currency="USD",
            is_default=1
        )


def main():
    parser = argparse.ArgumentParser(description="DAXDA Stripe Bank Account Connection Tool")
    parser.add_argument("--onboard-payout", action="store_true", help="Generate Stripe Connect bank onboarding link for payouts")
    parser.add_argument("--status", action="store_true", help="Check Stripe API configuration and environment status")
    parser.add_argument("--link-fa", type=str, help="Link a Stripe Financial Account ID (fa_...) to the founder treasury")
    parser.add_argument("--list-destinations", action="store_true", help="List all linked payout destinations")
    args = parser.parse_args()

    manager = StripeBankManager()

    if args.status:
        configured = manager.is_configured()
        print(f"Stripe SDK Version: {stripe.VERSION}")
        print(f"API Key Configured: {'YES' if configured else 'NO (Set STRIPE_SECRET_KEY or run stripe login)'}")
        print(f"Dashboard Payouts URL: https://dashboard.stripe.com/settings/payouts")
        from daxda_guard.metered_billing import get_billing_engine
        dests = get_billing_engine().get_payout_destinations()
        print(f"Linked Payout Destinations ({len(dests)}):")
        for d in dests:
            default_tag = " [DEFAULT]" if d["is_default"] else ""
            print(f" - {d['destination_type']}: {d['account_identifier']} ({d['network_or_platform']}){default_tag}")
        return

    if args.link_fa:
        res = manager.link_financial_account(args.link_fa)
        print(json.dumps(res, indent=2))
        return

    if args.list_destinations:
        from daxda_guard.metered_billing import get_billing_engine
        dests = get_billing_engine().get_payout_destinations()
        print(json.dumps(dests, indent=2))
        return

    if getattr(args, "onboard_payout", False):
        res = manager.create_payout_onboarding_link()
        print(json.dumps(res, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
