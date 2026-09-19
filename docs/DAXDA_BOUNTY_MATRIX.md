# DAXDA Bounty Matrix

**Snapshot:** 2026-09-18  
**Purpose:** Map DAXDA's operational security vectors to bounty categories, required tooling, verification gates, difficulty, and realistic payout planning.

## Interpretation rules

- The 13 vectors below are the operational vectors in the DAXDA safety registry: `INV-01` through `INV-12`, plus `INV-15`.
- `INV-13` (hashing is not semantic embedding) and `INV-14` (Cl(7,0) is not CGA) are representation and documentation correctness controls, not bounty-hunting vectors.
- Planning payout bands are estimates for prioritization only. They are not promises by DAXDA or by a target program.
- A DAXDA `PASS` means the local governance scanner accepted the test description. It does **not** establish that a target is exploitable, in scope, or eligible for payment.
- No live target was probed. Target verification must remain within the target's published rules of engagement and use local fixtures, test accounts, or an explicitly authorized environment.

## Matrix

| Vector | Bounty categories | Required tools | Verification method | Difficulty | Planning payout band |
|---|---|---|---|---|---|
| `INV-01` Observability vs. causal identifiability | Audit-trail integrity, agent incident response, compliance evidence | `daxda_guard.scanner`, causal-trace fixtures, SHA-256 manifest, independent reviewer | Run paired scenarios with identical telemetry and different causes; require `CAUSE_UNDETERMINED` when evidence cannot distinguish them | M | $0-$500; higher only when it enables a material security decision |
| `INV-02` Independent oracle validation | AI eval integrity, model-security benchmarks, security-tool false positives | `pytest`, independent oracle, negative controls, counterfactual fixtures, artifact hash manifest | Validate the claimed property, oracle, negative controls, counterfactual delta, and executed artifact hash before accepting a result | M | $250-$1,500 |
| `INV-03` Violation-rate decomposition | Agent safety, policy enforcement, red-team benchmark quality | `scanner.py`, event counter, replay harness, report generator | Report proposal, intervention, replan, compliant completion, and permanent failure separately; fail incomplete reports | M | $250-$1,000 |
| `INV-04` Post-block recovery | Agentic workflow safety, tool-use governance, enterprise automation | policy gate, replan harness, authority-receipt diff, regression tests | Exercise `PROPOSAL -> BLOCK -> REPLAN -> COMPLIANT_COMPLETION`; reject authority laundering | L | $500-$2,500 |
| `INV-05` Zero-feedback transfer attack | Prompt injection, indirect injection, jailbreak, cross-model transfer | isolated surrogate model, held-out target fixtures, one-shot corpus, success-rate calculator | Build attacks without target access; permit one hidden-case encounter; require transfer success at or below the program threshold | L | $500-$5,000+ |
| `INV-06` Execution-boundary primacy | RCE, unauthorized tool calls, payment/action abuse, agent sandbox escape | `daxda_guard.scanner`, deterministic authorization gate, fake tools, compromised-classifier fixture | Force a malicious proposal while treating detection as compromised; verify authorization and execution are still denied | L | $500-$10,000+ |
| `INV-07` Sandbox is not containment | Credential exposure, network egress, decoy theft, persistence, cloud-agent escape | network-isolated container, decoy credentials, canary endpoints, filesystem monitor, process tracer | Present reachable decoys and external-looking services; require immediate block and containment on access attempts | L | $1,000-$25,000+ |
| `INV-08` Prompt-environment consistency | Agentic cyber, cloud access, OAuth, tool-routing, environment confusion | runtime manifest, DNS/CA probe fixture, endpoint allowlist, environment attestation receipt | Contradict an “offline” prompt with observable runtime access; require `ENVIRONMENT_ATTESTATION_FAILURE` and halt | L | $1,000-$10,000+ |
| `INV-09` Provenance non-amplification | RAG poisoning, memory-layer attacks, document ingestion, supply-chain content | provenance graph, signed source manifest, retrieval fixture, taint propagation report | Inject a malicious source and verify retrieval cannot amplify authority, scope, or permissions beyond the source | L | $500-$10,000+ |
| `INV-10` Tool-schema differential | MCP/tool calling, API authorization, schema confusion, parameter smuggling | typed tool schemas, schema-diff harness, replay proxy, authorization receipt | Compare declared and executed schemas; reject extra parameters, downgraded auth, type confusion, and hidden side effects | M | $500-$10,000+ |
| `INV-11` Composition risk | Multi-step jailbreaks, benign-alone/harmful-together chains, agent orchestration | sequence generator, pairwise/combinatorial corpus, stateful replay, cross-step trace | Test components independently and in composition; flag sequences whose combined effect violates policy | L | $500-$10,000+ |
| `INV-12` Causal trace contract | Security incident response, regulated model governance, forensic reporting | scanner causal trace, immutable event store, authority receipt, replay verifier | Require every consequential transition to record `decision -> evidence -> authority -> resulting_state`; reject missing links | M | $250-$2,500 |
| `INV-15` Scalar leakage control | Side-channel resistance, sensitive scoring, model-governance telemetry | output redaction tests, differential timing/size harness, receipt schema validator | Verify that scalar scores, entropy, and internal coefficients cannot disclose protected state through output, timing, or error paths | L | $500-$10,000+ |

## Public bounty candidates run through the matrix

These are public GitHub issues with a stated reward or published reward schedule, reviewed on 2026-09-18. They are **candidate engagements**, not DAXDA findings.

| Candidate | Public scope and published payout | Best-fit vectors | Required target verification | Difficulty | Matrix result |
|---|---|---|---|---|---|
| [BasedHardware/omi#14463](https://github.com/BasedHardware/omi/issues/14463) | Unauthenticated MultiOn UID rebinding and purchase-webhook trigger; **$150** | `INV-06`, `INV-07`, `INV-10`, `INV-12` | Use a local Redis and fake MultiOn/Amazon client; prove an unauthenticated bind changes the downstream principal, then verify the proposed shared-secret guard on both mutating routes | M | **Strong fit; public issue already contains a concrete reproduction and fix direction** |
| [BasedHardware/omi#14442](https://github.com/BasedHardware/omi/issues/14442) | Unsigned Shopify OAuth callback can rebind grants; **$200** | `INV-06`, `INV-08`, `INV-10` | Use a local OAuth callback fixture with altered `state`/signature; verify forged callbacks cannot attach a grant to another UID | M | **Strong fit; verify locally before any submission** |
| [BasedHardware/omi#14444](https://github.com/BasedHardware/omi/issues/14444) | Unsigned Linear and Notion OAuth state can rebind grants; **$200** | `INV-06`, `INV-08`, `INV-10`, `INV-12` | Replay callback fixtures with missing, stale, and mismatched state; verify binding, nonce, and receipt checks | M | **Strong fit; likely same root class as #14442, so check duplicate policy** |
| [moorcheh-ai/memanto#1852](https://github.com/moorcheh-ai/memanto/issues/1852) | Memory-layer security challenge covering tenant isolation, auth, IDOR, exfiltration, and indirect prompt injection; **$100 top submission**, deadline September 30, 2026 | `INV-05`, `INV-07`, `INV-08`, `INV-09`, `INV-10`, `INV-11` | Fork the package, use only owned test accounts/fixtures, demonstrate a minimal failing test, add a fix, and submit one PR as required by the issue | L | **Highest DAXDA thematic fit; requires target package and backend authorization** |
| [tonkeeper/w5#17](https://github.com/tonkeeper/w5/issues/17) | W5 wallet security bounty; **250-500 TON low, 1,000-2,500 TON medium, 5,000-10,000 TON top** | `INV-06`, `INV-07`, `INV-10`, `INV-11` | Pin the stated commit, use a local TON test harness, prove unauthorized or misleading transaction behavior, and include a deterministic replay | XL | **High payout potential; requires smart-contract expertise and strict version pinning** |

## Local DAXDA triage evidence

The five candidate descriptions above were passed through `AutomatedRiskScanner` as text-only, non-networked inputs:

| Candidate | DAXDA verdict | Decision rule | Containment stage | Interpretation |
|---|---|---|---|---|
| OMI-14463 | `PASS` | `WITHIN_GOVERNANCE_TOLERANCE` | `PASS (Authorized)` | Description accepted as an authorized research input; target behavior not tested |
| OMI-14442 | `PASS` | `WITHIN_GOVERNANCE_TOLERANCE` | `PASS (Authorized)` | Description accepted as an authorized research input; target behavior not tested |
| OMI-14444 | `PASS` | `WITHIN_GOVERNANCE_TOLERANCE` | `PASS (Authorized)` | Description accepted as an authorized research input; target behavior not tested |
| MEMANTO-1852 | `PASS` | `WITHIN_GOVERNANCE_TOLERANCE` | `PASS (Authorized)` | Description accepted as an authorized research input; target behavior not tested |
| TONKEEPER-W5-17 | `PASS` | `WITHIN_GOVERNANCE_TOLERANCE` | `PASS (Authorized)` | Description accepted as an authorized research input; target behavior not tested |

## Execution order

1. **Selected highest-payment target:** Tonkeeper W5 `#17`; pin commit `fa1b372a417a32af104fe1b949b6b31d29cee349` and use the local execution plan in `reports/selected_bounty_tonkeeper_w5_2026-09-18.md`.
2. Start with Omi `#14442` and `#14444` in a local callback fixture; screen for duplicate/root-cause overlap before doing separate work.
3. Run Memanto `#1852` only with owned accounts, local package tests, and the required single-PR workflow.
4. Treat Omi `#14463` as an authorization-boundary regression task and verify the proposed fix against both mutating endpoints.
5. Do not submit a report based solely on the DAXDA `PASS`; attach target-specific reproduction, impact, scope evidence, and a patch or responsible-disclosure report.
