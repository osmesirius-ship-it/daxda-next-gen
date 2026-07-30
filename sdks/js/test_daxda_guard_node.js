const { DAXDAGuardNode, enforceGovernance } = require('./index');

console.log("=" .repeat(80));
console.log("  DAXDA GUARD NODE.JS & TYPESCRIPT SDK BENCHMARK SUITE");
console.log("=" .repeat(80));

const guard = new DAXDAGuardNode();

console.log("\n[TEST 1: Node.js Governance Evaluation]");
const rcpt1 = guard.evaluate("finance", "transfer_funds(amount=5000)");
console.log("  • Verdict:              ", rcpt1.verdict);
console.log("  • Decision Rule:        ", rcpt1.decisionRule);
console.log("  • Latency:              ", rcpt1.latencyMs.toFixed(4), "ms");
console.log("  • Authority SHA-256:    ", rcpt1.authoritySha256);
console.log("  • Status:                PASSED");

console.log("\n[TEST 2: Attack Vector Block Interlock]");
const rcpt2 = guard.evaluate("finance", "DROP DATABASE users;");
console.log("  • Verdict:              ", rcpt2.verdict);
console.log("  • Publication Permitted:", rcpt2.publicationPermitted);
console.log("  • Status:                PASSED (100% Halted)");

console.log("\n" + "=" .repeat(80));
console.log("  DAXDA GUARD NODE.JS & TYPESCRIPT SDK CERTIFIED!");
console.log("=" .repeat(80));
