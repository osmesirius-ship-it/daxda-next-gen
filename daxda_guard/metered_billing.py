#!/usr/bin/env python3
"""
DAXDA Next-Gen — Metered API Billing & Stripe Credit Gateway
============================================================
Enforces micro-metering at $0.0008 per governed inference call ($0.80 / 1,000 calls).
Manages tenant API keys, prepaid credit ledgers, Stripe payment webhooks,
and atomic fail-closed balance enforcement.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import secrets
import sqlite3
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
DB_PATH = os.path.join(OUTPUTS_DIR, "billing_ledger.db")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

logger = logging.getLogger("daxda.billing")

# Base commercial tariff
PRICE_PER_INFERENCE_CALL_USD = 0.0008  # $0.80 per 1,000 calls; 1.25M calls = $1,000/day
DEFAULT_FREE_TIER_CREDIT_USD = 10.00   # 12,500 initial complimentary calls for new accounts


class BillingErrorCode:
    MISSING_API_KEY = "DAX_BILLING_401_MISSING_KEY"
    INVALID_API_KEY = "DAX_BILLING_401_INVALID_KEY"
    KEY_SUSPENDED = "DAX_BILLING_403_KEY_SUSPENDED"
    INSUFFICIENT_CREDITS = "DAX_BILLING_402_INSUFFICIENT_CREDITS"
    RATE_LIMIT_EXCEEDED = "DAX_BILLING_429_RATE_LIMIT"


class MeteredBillingEngine:
    """
    High-performance, atomic billing engine backed by SQLite.
    Manages accounts, prepaid balances, usage metering, and Stripe top-ups.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()
        self._seed_default_accounts()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self):
        """Initializes tables for tenant accounts, API keys, usage logs, and deposits."""
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                company_name TEXT,
                credit_balance_usd REAL NOT NULL DEFAULT 0.0,
                total_billed_usd REAL NOT NULL DEFAULT 0.0,
                total_calls_metered INTEGER NOT NULL DEFAULT 0,
                tier TEXT NOT NULL DEFAULT 'COMMERCIAL_PAYG',
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                key_prefix TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE,
                key_name TEXT NOT NULL,
                rate_limit_qps REAL NOT NULL DEFAULT 200.0,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at_utc TEXT NOT NULL,
                last_used_at_utc TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS usage_records (
                call_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                key_prefix TEXT NOT NULL,
                service TEXT NOT NULL,
                charge_usd REAL NOT NULL,
                balance_after_usd REAL NOT NULL,
                timestamp_utc TEXT NOT NULL,
                merkle_receipt_sha256 TEXT,
                client_ip TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                deposit_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                amount_usd REAL NOT NULL,
                payment_provider TEXT NOT NULL,
                provider_ref TEXT,
                status TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS payout_destinations (
                destination_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                owner_name TEXT NOT NULL,
                destination_type TEXT NOT NULL,
                account_identifier TEXT NOT NULL UNIQUE,
                network_or_platform TEXT NOT NULL,
                settlement_currency TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'LINKED_ACTIVE',
                is_default INTEGER NOT NULL DEFAULT 1,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            );
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_tenant ON usage_records(tenant_id, timestamp_utc);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_deposits_tenant ON deposits(tenant_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_payout_tenant ON payout_destinations(tenant_id);")

    def _hash_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    def _seed_default_accounts(self):
        """Seeds default internal and enterprise demo keys if empty."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM tenants;").fetchone()
            if row["cnt"] == 0:
                now_iso = datetime.now(timezone.utc).isoformat()
                # 1. Enterprise Demo Account
                demo_tenant_id = "tenant-enterprise-demo"
                conn.execute("""
                    INSERT INTO tenants (tenant_id, customer_name, customer_email, company_name, credit_balance_usd, tier, status, created_at_utc, updated_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (demo_tenant_id, "Enterprise Demo Account", "enterprise@daxda.ia", "DAXDA Enterprise Client", 250.00, "ENTERPRISE", "ACTIVE", now_iso, now_iso))

                # Key: dax_live_enterprise_demo_key_2026
                demo_raw_key = "dax_live_enterprise_demo_key_2026"
                conn.execute("""
                    INSERT INTO api_keys (key_id, tenant_id, key_prefix, key_hash, key_name, rate_limit_qps, status, created_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, ("key-demo-01", demo_tenant_id, demo_raw_key[:12], self._hash_key(demo_raw_key), "Production Primary Key", 500.0, "ACTIVE", now_iso))

                # 2. Public Starter Account
                starter_tenant_id = "tenant-starter-client"
                conn.execute("""
                    INSERT INTO tenants (tenant_id, customer_name, customer_email, company_name, credit_balance_usd, tier, status, created_at_utc, updated_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (starter_tenant_id, "Commercial Starter", "developer@client.com", "Autonomous Agent Lab", 50.00, "COMMERCIAL_PAYG", "ACTIVE", now_iso, now_iso))

                starter_raw_key = "dax_live_starter_developer_key_2026"
                conn.execute("""
                    INSERT INTO api_keys (key_id, tenant_id, key_prefix, key_hash, key_name, rate_limit_qps, status, created_at_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """, ("key-starter-01", starter_tenant_id, starter_raw_key[:12], self._hash_key(starter_raw_key), "Standard Agent Key", 100.0, "ACTIVE", now_iso))

    def create_account(
        self,
        customer_name: str,
        customer_email: str,
        company_name: Optional[str] = None,
        initial_credit_usd: float = DEFAULT_FREE_TIER_CREDIT_USD,
        tier: str = "COMMERCIAL_PAYG",
    ) -> Tuple[Dict[str, Any], str]:
        """
        Creates a new customer account, issues a production API key, and pre-funds credits.
        Returns (account_metadata, raw_api_key).
        """
        tenant_id = f"tenant-{secrets.token_hex(6)}"
        raw_key = f"dax_live_{secrets.token_hex(20)}"
        key_id = f"key-{secrets.token_hex(6)}"
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO tenants (tenant_id, customer_name, customer_email, company_name, credit_balance_usd, tier, status, created_at_utc, updated_at_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (tenant_id, customer_name, customer_email, company_name or customer_name, initial_credit_usd, tier, "ACTIVE", now_iso, now_iso))

            conn.execute("""
                INSERT INTO api_keys (key_id, tenant_id, key_prefix, key_hash, key_name, rate_limit_qps, status, created_at_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (key_id, tenant_id, raw_key[:12], self._hash_key(raw_key), "Primary Production Key", 250.0, "ACTIVE", now_iso))

            if initial_credit_usd > 0:
                deposit_id = f"dep-{secrets.token_hex(8)}"
                conn.execute("""
                    INSERT INTO deposits (deposit_id, tenant_id, amount_usd, payment_provider, provider_ref, status, timestamp_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (deposit_id, tenant_id, initial_credit_usd, "WELCOME_CREDIT", "SYSTEM_SIGNUP_GRANT", "CONFIRMED", now_iso))

        account_info = {
            "tenant_id": tenant_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "credit_balance_usd": initial_credit_usd,
            "key_prefix": raw_key[:12] + "...",
            "tier": tier,
            "price_per_call_usd": PRICE_PER_INFERENCE_CALL_USD,
            "created_at_utc": now_iso
        }
        return account_info, raw_key

    def deposit_credits(
        self,
        tenant_id: str,
        amount_usd: float,
        provider: str = "STRIPE",
        provider_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Atomically credits customer account following a confirmed payment."""
        if amount_usd <= 0:
            raise ValueError("Deposit amount must be strictly positive")

        deposit_id = f"dep-{secrets.token_hex(8)}"
        now_iso = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            # Check tenant exists
            t = conn.execute("SELECT tenant_id, credit_balance_usd FROM tenants WHERE tenant_id = ?;", (tenant_id,)).fetchone()
            if not t:
                raise KeyError(f"Tenant {tenant_id} not found")

            new_balance = round(t["credit_balance_usd"] + amount_usd, 6)

            conn.execute("""
                UPDATE tenants
                SET credit_balance_usd = ?, updated_at_utc = ?
                WHERE tenant_id = ?;
            """, (new_balance, now_iso, tenant_id))

            conn.execute("""
                INSERT INTO deposits (deposit_id, tenant_id, amount_usd, payment_provider, provider_ref, status, timestamp_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (deposit_id, tenant_id, amount_usd, provider, provider_ref or "manual_topup", "CONFIRMED", now_iso))

        return {
            "deposit_id": deposit_id,
            "tenant_id": tenant_id,
            "amount_deposited_usd": amount_usd,
            "new_balance_usd": new_balance,
            "timestamp_utc": now_iso,
            "status": "CONFIRMED"
        }

    def authenticate_and_meter(
        self,
        auth_header_or_key: Optional[str],
        service: str = "INFERENCE_SCAN",
        charge_usd: float = PRICE_PER_INFERENCE_CALL_USD,
        merkle_receipt_sha256: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validates the API key and atomically meters the call at $0.0008.
        Returns (success: bool, error_code: Optional[str], context: Dict[str, Any]).
        Fail-closed: Rejects instantly if missing, invalid, or balance < charge.
        """
        if not auth_header_or_key:
            return False, BillingErrorCode.MISSING_API_KEY, {
                "error": "Missing Authorization header. Required: 'Authorization: Bearer dax_live_...'",
                "http_status": 401
            }

        raw_key = auth_header_or_key.strip()
        if raw_key.startswith("Bearer "):
            raw_key = raw_key[7:].strip()

        key_hash = self._hash_key(raw_key)
        now_iso = datetime.now(timezone.utc).isoformat()
        call_id = f"tx-{secrets.token_hex(10)}"

        with self._get_connection() as conn:
            # 1. Lookup key
            query = """
                SELECT k.key_id, k.tenant_id, k.key_prefix, k.status as key_status, k.rate_limit_qps,
                       t.credit_balance_usd, t.total_billed_usd, t.total_calls_metered, t.status as tenant_status
                FROM api_keys k
                JOIN tenants t ON k.tenant_id = t.tenant_id
                WHERE k.key_hash = ?;
            """
            row = conn.execute(query, (key_hash,)).fetchone()
            if not row:
                return False, BillingErrorCode.INVALID_API_KEY, {
                    "error": "Invalid API key provided. Obtain keys at https://daxda.ia/portal",
                    "http_status": 401
                }

            if row["key_status"] != "ACTIVE" or row["tenant_status"] != "ACTIVE":
                return False, BillingErrorCode.KEY_SUSPENDED, {
                    "error": "API key or customer account is suspended. Contact billing@daxda.ia",
                    "http_status": 403
                }

            # 2. Check balance
            current_balance = row["credit_balance_usd"]
            if current_balance < charge_usd:
                return False, BillingErrorCode.INSUFFICIENT_CREDITS, {
                    "error": f"Insufficient credit balance (${current_balance:.4f} USD). Required: ${charge_usd:.4f} USD. Top up at https://daxda.ia/billing",
                    "http_status": 402,
                    "tenant_id": row["tenant_id"],
                    "current_balance_usd": current_balance,
                    "topup_url": f"https://api.daxda.ia/api/v1/billing/topup?tenant_id={row['tenant_id']}"
                }

            # 3. Atomically deduct charge
            new_balance = round(current_balance - charge_usd, 6)
            new_billed = round(row["total_billed_usd"] + charge_usd, 6)
            new_count = row["total_calls_metered"] + 1

            conn.execute("""
                UPDATE tenants
                SET credit_balance_usd = ?, total_billed_usd = ?, total_calls_metered = ?, updated_at_utc = ?
                WHERE tenant_id = ?;
            """, (new_balance, new_billed, new_count, now_iso, row["tenant_id"]))

            conn.execute("""
                UPDATE api_keys
                SET last_used_at_utc = ?
                WHERE key_id = ?;
            """, (now_iso, row["key_id"]))

            conn.execute("""
                INSERT INTO usage_records (call_id, tenant_id, key_prefix, service, charge_usd, balance_after_usd, timestamp_utc, merkle_receipt_sha256, client_ip)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (call_id, row["tenant_id"], row["key_prefix"], service, charge_usd, new_balance, now_iso, merkle_receipt_sha256, client_ip or "127.0.0.1"))

        return True, None, {
            "call_id": call_id,
            "tenant_id": row["tenant_id"],
            "charge_usd": charge_usd,
            "remaining_balance_usd": new_balance,
            "total_calls_metered": new_count,
            "status": "BILLED_AND_AUTHORIZED"
        }

    def process_stripe_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses Stripe webhook events (checkout.session.completed, payment_intent.succeeded)
        and automatically credits the customer's prepaid balance.
        """
        event_type = payload.get("type", "")
        data_object = payload.get("data", {}).get("object", {})

        if event_type in ("checkout.session.completed", "payment_intent.succeeded"):
            # Extract tenant ID and amount
            tenant_id = data_object.get("metadata", {}).get("tenant_id") or data_object.get("client_reference_id")
            amount_cents = data_object.get("amount_total") or data_object.get("amount") or 0
            amount_usd = amount_cents / 100.0
            provider_ref = data_object.get("id", f"stripe_{secrets.token_hex(8)}")

            if not tenant_id:
                # Try finding customer by email
                customer_email = data_object.get("customer_details", {}).get("email") or data_object.get("receipt_email")
                if customer_email:
                    with self._get_connection() as conn:
                        row = conn.execute("SELECT tenant_id FROM tenants WHERE customer_email = ? LIMIT 1;", (customer_email,)).fetchone()
                        if row:
                            tenant_id = row["tenant_id"]

            if tenant_id and amount_usd > 0:
                result = self.deposit_credits(
                    tenant_id=tenant_id,
                    amount_usd=amount_usd,
                    provider="STRIPE",
                    provider_ref=provider_ref
                )
                logger.info(f"Stripe deposit of ${amount_usd:.2f} credited to {tenant_id}")
                return {"status": "SUCCESS", "event": event_type, "deposit": result}

        return {"status": "IGNORED", "event": event_type, "message": "Unhandled event or zero amount"}

    def link_payout_destination(
        self,
        tenant_id: str,
        owner_name: str,
        destination_type: str,
        account_identifier: str,
        network_or_platform: str,
        settlement_currency: str = "USD",
        is_default: int = 1
    ) -> Dict[str, Any]:
        """Registers or updates a verified payout destination (Stripe Financial Account, EVM, ACH)."""
        now_iso = datetime.now(timezone.utc).isoformat()
        dest_id = f"payout-{uuid.uuid4().hex[:12]}"

        with self._get_connection() as conn:
            existing = conn.execute(
                "SELECT destination_id FROM payout_destinations WHERE account_identifier = ?;",
                (account_identifier,)
            ).fetchone()

            if existing:
                conn.execute("""
                    UPDATE payout_destinations
                    SET owner_name = ?, destination_type = ?, network_or_platform = ?,
                        settlement_currency = ?, status = 'LINKED_ACTIVE', is_default = ?, updated_at_utc = ?
                    WHERE account_identifier = ?;
                """, (owner_name, destination_type, network_or_platform, settlement_currency, is_default, now_iso, account_identifier))
                dest_id = existing["destination_id"]
            else:
                conn.execute("""
                    INSERT INTO payout_destinations (
                        destination_id, tenant_id, owner_name, destination_type,
                        account_identifier, network_or_platform, settlement_currency,
                        status, is_default, created_at_utc, updated_at_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'LINKED_ACTIVE', ?, ?, ?);
                """, (dest_id, tenant_id, owner_name, destination_type, account_identifier, network_or_platform, settlement_currency, is_default, now_iso, now_iso))

        logger.info(f"Payout destination linked: {destination_type} {account_identifier} for {owner_name}")
        return {
            "status": "SUCCESS",
            "destination_id": dest_id,
            "tenant_id": tenant_id,
            "owner_name": owner_name,
            "destination_type": destination_type,
            "account_identifier": account_identifier,
            "network_or_platform": network_or_platform,
            "settlement_currency": settlement_currency,
            "is_default": bool(is_default)
        }

    def get_payout_destinations(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if tenant_id:
                rows = conn.execute(
                    "SELECT * FROM payout_destinations WHERE tenant_id = ? ORDER BY is_default DESC, created_at_utc ASC;",
                    (tenant_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM payout_destinations ORDER BY is_default DESC, created_at_utc ASC;"
                ).fetchall()

            return [
                {
                    "destination_id": r["destination_id"],
                    "tenant_id": r["tenant_id"],
                    "owner_name": r["owner_name"],
                    "destination_type": r["destination_type"],
                    "account_identifier": r["account_identifier"],
                    "network_or_platform": r["network_or_platform"],
                    "settlement_currency": r["settlement_currency"],
                    "status": r["status"],
                    "is_default": bool(r["is_default"]),
                    "created_at_utc": r["created_at_utc"]
                }
                for r in rows
            ]

    def get_telemetry(self) -> Dict[str, Any]:
        """Computes live commercial billing and ARR run-rate telemetry."""
        with self._get_connection() as conn:
            tenants_cnt = conn.execute("SELECT COUNT(*) as c FROM tenants;").fetchone()["c"]
            keys_cnt = conn.execute("SELECT COUNT(*) as c FROM api_keys WHERE status = 'ACTIVE';").fetchone()["c"]
            total_rev = conn.execute("SELECT SUM(total_billed_usd) as rev, SUM(total_calls_metered) as calls FROM tenants;").fetchone()
            rev = total_rev["rev"] or 0.0
            calls = total_rev["calls"] or 0

            # Today's billed volume
            today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            today_rev = conn.execute("""
                SELECT SUM(charge_usd) as rev, COUNT(*) as cnt
                FROM usage_records
                WHERE timestamp_utc LIKE ?;
            """, (f"{today_prefix}%",)).fetchone()
            today_usd = today_rev["rev"] or 0.0
            today_calls = today_rev["cnt"] or 0

            # Recent accounts
            tenants_list = []
            for t in conn.execute("SELECT tenant_id, customer_name, customer_email, credit_balance_usd, total_billed_usd, total_calls_metered, tier FROM tenants LIMIT 10;").fetchall():
                tenants_list.append({
                    "tenant_id": t["tenant_id"],
                    "customer_name": t["customer_name"],
                    "credit_balance_usd": round(t["credit_balance_usd"], 4),
                    "total_billed_usd": round(t["total_billed_usd"], 4),
                    "total_calls": t["total_calls_metered"],
                    "tier": t["tier"]
                })

            # Recent deposits
            deposits_list = []
            for d in conn.execute("SELECT deposit_id, tenant_id, amount_usd, payment_provider, status, timestamp_utc FROM deposits ORDER BY timestamp_utc DESC LIMIT 5;").fetchall():
                deposits_list.append({
                    "deposit_id": d["deposit_id"],
                    "tenant_id": d["tenant_id"],
                    "amount_usd": d["amount_usd"],
                    "provider": d["payment_provider"],
                    "status": d["status"],
                    "timestamp_utc": d["timestamp_utc"]
                })

            # Payout destinations
            payouts_list = []
            for p in conn.execute("SELECT destination_id, tenant_id, owner_name, destination_type, account_identifier, network_or_platform, settlement_currency, status, is_default FROM payout_destinations ORDER BY is_default DESC;").fetchall():
                payouts_list.append({
                    "destination_id": p["destination_id"],
                    "tenant_id": p["tenant_id"],
                    "owner_name": p["owner_name"],
                    "destination_type": p["destination_type"],
                    "account_identifier": p["account_identifier"],
                    "network_or_platform": p["network_or_platform"],
                    "settlement_currency": p["settlement_currency"],
                    "status": p["status"],
                    "is_default": bool(p["is_default"])
                })

        return {
            "billing_status": "METERED_COMMERCIAL_GATEWAY_ACTIVE",
            "price_per_inference_call_usd": PRICE_PER_INFERENCE_CALL_USD,
            "price_per_1000_calls_usd": PRICE_PER_INFERENCE_CALL_USD * 1000,
            "total_tenants_registered": tenants_cnt,
            "active_api_keys": keys_cnt,
            "all_time_billed_revenue_usd": round(rev, 4),
            "all_time_calls_metered": calls,
            "today_billed_revenue_usd": round(today_usd, 4),
            "today_calls_metered": today_calls,
            "daily_projected_run_rate_usd": round(today_usd, 2),
            "active_accounts": tenants_list,
            "recent_deposits": deposits_list,
            "payout_destinations": payouts_list
        }


# Global singleton instance
BILLING_ENGINE: Optional[MeteredBillingEngine] = None


def get_billing_engine() -> MeteredBillingEngine:
    global BILLING_ENGINE
    if BILLING_ENGINE is None:
        BILLING_ENGINE = MeteredBillingEngine()
    return BILLING_ENGINE
