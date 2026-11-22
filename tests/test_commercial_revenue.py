"""
Unit and integration test suite for DAXDA Commercial Revenue Engine:
1. Public Ingress configuration files (Cloudflare Tunnel, Nginx TLS 1.3)
2. Metered API Billing ($0.0008/call, Stripe webhook, credit balances, fail-closed enforcement)
3. DePIN Compute Broker Bridge (io.net, Bittensor, Render/Akash, dual-track duty cycling)
4. Live REST Endpoints (/api/v1/govern, /api/v1/billing/*, /api/depin/broker/*)
"""

import os
import tempfile
import json
import yaml
import pytest
from daxda_guard.metered_billing import (
    MeteredBillingEngine,
    PRICE_PER_INFERENCE_CALL_USD,
)
from daxda_engine.level3.depin_validator_network.compute_broker_bridge import (
    DePINComputeBrokerBridge,
    BrokerProtocol,
    HardwareRateCard,
    ComputeJobReceipt,
)


def test_ingress_config_validity():
    """Verify Cloudflare Tunnel and Nginx ingress configuration schemas."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cf_path = os.path.join(repo_root, "config", "ingress", "cloudflared_tunnel.yml")
    nginx_path = os.path.join(repo_root, "config", "ingress", "nginx_daxda.conf")

    assert os.path.exists(cf_path), f"Missing {cf_path}"
    assert os.path.exists(nginx_path), f"Missing {nginx_path}"

    with open(cf_path, "r", encoding="utf-8") as f:
        cf_config = yaml.safe_load(f)

    assert "tunnel" in cf_config
    assert "ingress" in cf_config
    ingress_hosts = [r.get("hostname") for r in cf_config["ingress"] if "hostname" in r]
    assert "api.daxda.ia" in ingress_hosts
    assert "dashboard.daxda.ia" in ingress_hosts
    assert "billing.daxda.ia" in ingress_hosts
    assert "depin.daxda.ia" in ingress_hosts

    with open(nginx_path, "r", encoding="utf-8") as f:
        nginx_content = f.read()

    assert "server_name api.daxda.ia" in nginx_content
    assert "TLSv1.3" in nginx_content
    assert "limit_req_zone" in nginx_content
    assert "127.0.0.1:8088" in nginx_content


def test_metered_billing_engine_lifecycle():
    """Verify account provisioning, deposit, per-call billing, and balance exhaustion."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    try:
        engine = MeteredBillingEngine(db_path=db_path)
        
        # 1. Create tenant account with 0 initial credits
        acct_info, raw_key = engine.create_account(
            customer_name="Biotech Alpha Corp",
            customer_email="research@biotechalpha.com",
            initial_credit_usd=0.00,
            tier="COMMERCIAL_PAYG"
        )
        tenant_id = acct_info["tenant_id"]
        assert raw_key.startswith("dax_live_")

        # 2. Attempt call with 0 balance -> Fail closed with 402
        ok, err_code, ctx = engine.authenticate_and_meter(
            auth_header_or_key=f"Bearer {raw_key}",
            service="INFERENCE_SCAN",
            charge_usd=PRICE_PER_INFERENCE_CALL_USD
        )
        assert not ok
        assert err_code == "DAX_BILLING_402_INSUFFICIENT_CREDITS"
        assert ctx["http_status"] == 402

        # 3. Deposit credits via simulated Stripe webhook
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "client_reference_id": tenant_id,
                    "amount_total": 5000, # $50.00 in cents
                    "currency": "usd",
                    "payment_intent": "pi_test_stripe_99482"
                }
            }
        }
        res_stripe = engine.process_stripe_webhook(event)
        assert res_stripe["status"] == "SUCCESS"
        assert res_stripe["deposit"]["amount_deposited_usd"] == 50.0

        # 4. Attempt call with funded balance -> Must succeed and deduct exactly $0.0008
        ok, err_code, ctx = engine.authenticate_and_meter(
            auth_header_or_key=f"Bearer {raw_key}",
            service="INFERENCE_SCAN",
            charge_usd=PRICE_PER_INFERENCE_CALL_USD
        )
        assert ok
        assert err_code is None
        assert ctx["call_id"].startswith("tx-")
        assert round(ctx["remaining_balance_usd"], 4) == round(50.0 - 0.0008, 4)

        # 5. Invalid key rejection -> 401 Unauthorized
        ok, err_code, ctx = engine.authenticate_and_meter(
            auth_header_or_key="Bearer dax_live_fake_key_12345",
            service="INFERENCE_SCAN"
        )
        assert not ok
        assert err_code == "DAX_BILLING_401_INVALID_KEY"
        assert ctx["http_status"] == 401

        # 6. Verify telemetry summary
        telem = engine.get_telemetry()
        assert telem["price_per_inference_call_usd"] == 0.0008
        assert telem["all_time_billed_revenue_usd"] == 0.0008
        assert telem["all_time_calls_metered"] == 1

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_depin_compute_broker_bridge():
    """Verify registration, rate card calculation, and idle cycle lease dispatch."""
    bridge = DePINComputeBrokerBridge()

    # 1. Verify hardware rate cards
    rate_h100 = HardwareRateCard.get_rate("Enterprise GPU (NVIDIA H100 / RTX 4090)")
    rate_3090 = HardwareRateCard.get_rate("Consumer Edge (RTX 3090)")
    assert rate_h100 == 2.85
    assert rate_3090 == 0.55

    # 2. Simulate compute ticks leasing idle cycles
    initial_revenue = bridge.gross_revenue_earned_usd
    bridge.simulate_compute_tick(count=10)
    assert bridge.total_jobs_completed >= 10
    assert bridge.gross_revenue_earned_usd > initial_revenue

    # 3. Check telemetry fields
    telem = bridge.get_telemetry()
    assert telem["broker_bridge_status"] == "COMPUTE_BROKER_MARKET_CONNECTED"
    assert telem["total_registered_nodes"] == 50
    assert telem["active_rented_nodes"] > 0
    assert telem["max_cluster_daily_capacity_usd"] > 1000.0
    assert telem["target_scale_1000_usd_day_progress_pct"] > 0.0
    assert len(telem["recent_job_receipts"]) > 0


def test_live_daemon_commercial_endpoints():
    """Verify live HTTP endpoints on daemon port 8088 if daemon is running."""
    import urllib.request
    import urllib.error

    url_telem = "http://127.0.0.1:8088/api/v1/billing/telemetry"
    try:
        req = urllib.request.Request(url_telem)
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode())
            assert data["billing_status"] == "METERED_COMMERCIAL_GATEWAY_ACTIVE"
            assert data["price_per_inference_call_usd"] == 0.0008
    except urllib.error.URLError:
        pytest.skip("Fleet daemon not currently running on 127.0.0.1:8088")
