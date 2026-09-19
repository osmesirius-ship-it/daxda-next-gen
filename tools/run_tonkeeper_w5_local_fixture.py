#!/usr/bin/env python3
"""Authorize and evaluate the Tonkeeper W5 local fixture under DAXDA Cl(16,4).

Safety boundary:
- Uses only the pinned in-scope checkout under fixtures/authorized/
- Generates ephemeral test keys (never production / funded wallets)
- Runs the upstream Jest harness as the independent evaluator
- Does NOT claim a vulnerability finding or bounty eligibility
"""

from __future__ import annotations

import hashlib
import json
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "authorized" / "tonkeeper-w5"
PINNED_COMMIT = "fa1b372a417a32af104fe1b949b6b31d29cee349"
PROGRAM = "https://github.com/tonkeeper/w5/issues/17"
REPORT_PATH = ROOT / "reports" / "tonkeeper_w5_local_fixture_receipt.json"

sys.path.insert(0, str(ROOT))

from daxda_engine.cl16_4 import HyperValidator  # noqa: E402
from daxda_engine.cl16_4.validation.validator import ValidationRequest  # noqa: E402
from daxda_engine.prada import ArenaEvaluation, ArenaProblem, PradaArena  # noqa: E402


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_head(repo: Path) -> str:
    out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True)
    return out.strip()


def _run_jest(repo: Path) -> dict:
    proc = subprocess.run(
        ["npm", "test", "--", "--ci", "--forceExit"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    digest = hashlib.sha256(
        (proc.stdout + "\n" + proc.stderr).encode("utf-8", errors="replace")
    ).hexdigest()
    return {
        "exit_code": proc.returncode,
        "passed": proc.returncode == 0,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-2000:],
        "output_sha256": digest,
    }


def _ephemeral_test_keypair(repo: Path) -> dict:
    """Create a disposable local keypair; persist only public material + seed hash."""
    seed = secrets.token_bytes(32)
    seed_hex = seed.hex()
    script = f"""
const {{ keyPairFromSeed }} = require('ton-crypto');
const seed = Buffer.from('{seed_hex}', 'hex');
const kp = keyPairFromSeed(seed);
process.stdout.write(JSON.stringify({{
  publicKeyHex: Buffer.from(kp.publicKey).toString('hex'),
  secretKeyBytes: kp.secretKey.length,
  publicKeyBytes: kp.publicKey.length
}}));
"""
    out = subprocess.check_output(["node", "-e", script], cwd=repo, text=True)
    material = json.loads(out)
    return {
        "purpose": "local_sandbox_only_non_valuable",
        "algorithm": "ed25519 via ton-crypto keyPairFromSeed",
        "seed_sha256": hashlib.sha256(seed).hexdigest(),
        "public_key_hex": material["publicKeyHex"],
        "public_key_bytes": material["publicKeyBytes"],
        "secret_key_bytes": material["secretKeyBytes"],
        "secret_material_persisted": False,
    }


def _contract_hashes(repo: Path) -> dict:
    contracts = sorted((repo / "contracts").rglob("*"))
    files = [p for p in contracts if p.is_file()]
    return {
        str(p.relative_to(repo)): _sha256_file(p) for p in files
    }


def _cl16_4_authorize(fixture_ok: bool, tests_ok: bool, commit_ok: bool) -> dict:
    # 16-dim decision: emphasize local-only authorization, ROE compliance, no live probe.
    vector = [
        1.0 if commit_ok else 0.0,  # pin integrity
        1.0 if fixture_ok else 0.0,  # local checkout present
        1.0 if tests_ok else 0.0,  # independent harness green
        1.0,  # test keys only
        1.0,  # no live network probing
        1.0,  # non-valuable funds
        0.9,  # ROE reviewed
        0.9,  # scope bounded to W5 contract
        0.8,  # reproducible baseline
        0.0,  # vulnerability finding (none yet)
        0.0,  # impact proven (none yet)
        0.0,  # ready to submit (no)
        0.7,  # regression suite available
        0.7,  # independent evaluator present (jest)
        0.6,  # human review still required
        0.5,  # duplicate check pending
    ]
    validator = HyperValidator()
    result = validator.validate(
        ValidationRequest(
            agent_id="tonkeeper-w5-local-fixture-runner",
            decision_vector=vector,
            context={
                "program": PROGRAM,
                "pinned_commit": PINNED_COMMIT,
                "mode": "authorized_local_fixture",
            },
        )
    )
    return {
        "is_valid": result.is_valid,
        "cert_hash": result.cert_hash,
        "request_id": result.request_id,
        "config": list(result.config.indices) if result.config else None,
        "constraints": {
            "passed": result.constraints.passed,
            "failed": result.constraints.failed,
            "score": result.constraints.score,
        },
        "validation_time_ms": result.validation_time_ms,
    }


def _arena_iteration(tests_ok: bool, cl_ok: bool) -> dict:
    prompt = (
        f"TONKEEPER-W5-17 local fixture pin={PINNED_COMMIT} "
        f"tests_ok={tests_ok} cl16_4_ok={cl_ok}"
    )
    prompt_digest = hashlib.sha256(prompt.encode()).hexdigest()
    problem = ArenaProblem(
        problem_id="TONKEEPER-W5-17",
        domain="smart-contract-local-fixture",
        difficulty=0.85,
        prompt_digest=prompt_digest,
        acceptance_criteria=(
            "pinned_commit_matches",
            "local_sandbox_tests_pass",
            "ephemeral_test_keys_only",
            "no_live_probing",
            "finding_requires_independent_proof",
        ),
        hidden_evaluator=True,
    )
    # Fixture readiness is not a bounty solve. Fail closed on "finding".
    evaluation = ArenaEvaluation(
        problem_id=problem.problem_id,
        solved=False,
        verified=False,
        score=0.35 if tests_ok and cl_ok else 0.1,
        regression_passed=tests_ok,
        reproducible=tests_ok,
        generalization_score=0.0,
        failure_mode=None if (tests_ok and cl_ok) else "fixture_or_governance_gate_failed",
        evaluator_id="jest+cl16_4-local",
    )
    if tests_ok and cl_ok:
        # Harness ready, but no vulnerability evidence → diagnose next research step.
        evaluation = ArenaEvaluation(
            problem_id=problem.problem_id,
            solved=False,
            verified=False,
            score=0.35,
            regression_passed=True,
            reproducible=True,
            generalization_score=0.0,
            failure_mode="no_vulnerability_evidence_yet",
            evaluator_id="jest+cl16_4-local",
        )

    arena = PradaArena(
        objective_version="tonkeeper-w5-local-fixture-v1",
        evaluator_integrity_digest=hashlib.sha256(b"jest-ci-local").hexdigest(),
        safety_policy_digest=hashlib.sha256(
            b"local-only;test-keys;no-live-probe;roe-tonkeeper-w5-17"
        ).hexdigest(),
        max_iterations=5,
    )
    record = arena.run_evaluation(
        problem=problem,
        strategy_id="establish_authorized_local_fixture",
        evaluation=evaluation,
        failure_revision="begin_scoped_invariant_review",
    )
    metrics = arena.metrics()
    return {
        "action": record.action,
        "receipt_sha256": record.receipt_sha256,
        "evaluation": {
            "solved": evaluation.solved,
            "verified": evaluation.verified,
            "score": evaluation.score,
            "regression_passed": evaluation.regression_passed,
            "reproducible": evaluation.reproducible,
            "failure_mode": evaluation.failure_mode,
            "evaluator_id": evaluation.evaluator_id,
        },
        "metrics": {
            "iterations": metrics.iterations,
            "success_rate": metrics.success_rate,
            "verification_rate": metrics.verification_rate,
            "regression_rate": metrics.regression_rate,
            "novel_failure_rate": metrics.novel_failure_rate,
        },
    }


def main() -> int:
    if not FIXTURE.is_dir():
        print(f"ERROR: fixture missing at {FIXTURE}", file=sys.stderr)
        print(
            "Clone with:\n"
            f"  git clone https://github.com/tonkeeper/w5.git {FIXTURE}\n"
            f"  cd {FIXTURE} && git checkout {PINNED_COMMIT} && npm ci && npm test",
            file=sys.stderr,
        )
        return 2

    head = _git_head(FIXTURE)
    commit_ok = head == PINNED_COMMIT
    jest = _run_jest(FIXTURE)
    keys = _ephemeral_test_keypair(FIXTURE)
    contracts = _contract_hashes(FIXTURE)
    cl = _cl16_4_authorize(True, jest["passed"], commit_ok)
    arena = _arena_iteration(jest["passed"], cl["is_valid"])

    receipt = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "program": PROGRAM,
        "target_repo": "https://github.com/tonkeeper/w5",
        "pinned_commit": PINNED_COMMIT,
        "observed_commit": head,
        "commit_pin_ok": commit_ok,
        "fixture_path": str(FIXTURE.relative_to(ROOT)),
        "network_policy": "local_sandbox_only",
        "live_probing": False,
        "test_keypair": keys,
        "jest": {
            "passed": jest["passed"],
            "exit_code": jest["exit_code"],
            "output_sha256": jest["output_sha256"],
            "stdout_tail": jest["stdout_tail"],
        },
        "contract_file_sha256": contracts,
        "cl16_4": cl,
        "prada_arena": arena,
        "bounty_claim": {
            "finding_claimed": False,
            "submission_authorized": False,
            "reason": (
                "Local fixture and baseline regression are established. "
                "No independently verified unauthorized fund movement or "
                "auth bypass was demonstrated. DAXDA Cl(16,4)/Arena PASS on "
                "fixture governance is not a vulnerability finding."
            ),
        },
        "next_authorized_steps": [
            "Review Specification.md + wallet_v5 contract invariants locally",
            "Add deterministic replay fixtures for candidate hypotheses",
            "Require independent evaluator confirmation before any disclosure",
            "Human reviewer must approve before opening issue or emailing oleg@tonkeeper.com",
        ],
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(REPORT_PATH.relative_to(ROOT)),
        "commit_pin_ok": commit_ok,
        "jest_passed": jest["passed"],
        "cl16_4_valid": cl["is_valid"],
        "arena_action": arena["action"],
        "finding_claimed": False,
    }, indent=2))
    return 0 if commit_ok and jest["passed"] and cl["is_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
