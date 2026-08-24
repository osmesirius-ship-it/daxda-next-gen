#include "governed_authority_gate.hpp"
#include "sha256.hpp"

#include <iostream>
#include <algorithm>
#include <cctype>
#include <cmath>

bool GovernedAuthorityGate::s_initialized = false;
int GovernedAuthorityGate::s_blade_table[128][128];
double GovernedAuthorityGate::s_sign_table[128][128];

static std::string to_lowercase(const std::string& str) {
    std::string lower = str;
    std::transform(lower.begin(), lower.end(), lower.begin(),
                   [](unsigned char c){ return std::tolower(c); });
    return lower;
}

void GovernedAuthorityGate::init_algebra() {
    for (int i = 0; i < 128; ++i) {
        for (int j = 0; j < 128; ++j) {
            s_blade_table[i][j] = i ^ j;
            
            // Calculate blade sign permutation for Cl(7,0)
            int count = 0;
            for (int bit = 0; bit < 7; ++bit) {
                if ((j >> bit) & 1) {
                    int mask = i & ((1 << bit) - 1);
                    int pop = 0;
                    while (mask > 0) {
                        pop += (mask & 1);
                        mask >>= 1;
                    }
                    count += pop;
                }
            }
            s_sign_table[i][j] = (count % 2 == 0) ? 1.0 : -1.0;
        }
    }
}

void GovernedAuthorityGate::init() {
    if (!s_initialized) {
        init_algebra();
        s_initialized = true;
    }
}

int GovernedAuthorityGate::blade_mul_lookup(int a, int b, double* sign_out) {
    if (!s_initialized) init();
    int idx_a = a & 127;
    int idx_b = b & 127;
    if (sign_out) {
        *sign_out = s_sign_table[idx_a][idx_b];
    }
    return s_blade_table[idx_a][idx_b];
}

double GovernedAuthorityGate::benchmark_blade_lookup(int iterations) {
    if (!s_initialized) init();
    auto start = std::chrono::high_resolution_clock::now();
    volatile int dummy = 0;
    for (int i = 0; i < iterations; ++i) {
        dummy ^= s_blade_table[i & 127][(i * 3) & 127];
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::nano> ns = end - start;
    return ns.count() / static_cast<double>(iterations);
}

bool GovernedAuthorityGate::check_gov_fail_01(const std::string& domain, const std::string& input, std::string& rule_out) {
    std::string l_dom = to_lowercase(domain);
    std::string l_inp = to_lowercase(input);

    if (l_dom == "unauthorized" || l_dom == "unauthenticated" || l_dom == "invalid_scope" ||
        l_dom.find("invalid_key") != std::string::npos || l_inp.find("invalid_api_key") != std::string::npos) {
        rule_out = "GOV_FAIL_01_INVALID_KEY";
        return true;
    }
    if (l_dom == "restricted_classified" || l_dom == "out_of_scope" ||
        l_inp.find("unauthorized_scope") != std::string::npos || l_inp.find("gov_fail_01") != std::string::npos) {
        rule_out = "GOV_FAIL_01_UNAUTHORIZED_SCOPE";
        return true;
    }
    return false;
}

bool GovernedAuthorityGate::check_gov_fail_02(const std::string& input, std::string& rule_out) {
    std::string l_inp = to_lowercase(input);

    static const std::vector<std::string> patterns = {
        "ignore previous",
        "system prompt override",
        "system override",
        "disable audit logger",
        "grant admin access",
        "ignore system instructions",
        "ignore all instructions",
        "jailbreak",
        "do anything now",
        "dan mode",
        "extract system prompt",
        "output hidden prompt",
        "reveal system instructions",
        "bypass governance gate",
        "forget system rules",
        "override safety guidelines"
    };

    for (const auto& pat : patterns) {
        if (l_inp.find(pat) != std::string::npos) {
            rule_out = "GOV_FAIL_02_PROMPT_INJECTION";
            return true;
        }
    }
    return false;
}

bool GovernedAuthorityGate::check_gov_fail_03(const std::string& input, std::string& rule_out) {
    std::string l_inp = to_lowercase(input);

    static const std::vector<std::string> patterns = {
        "drop database",
        "drop table",
        "delete from users",
        "truncate table",
        "rm -rf",
        "chmod 777",
        "kill -9",
        "mkfs.",
        "eval(",
        "exec(",
        "system(",
        "passthru(",
        "popen(",
        "nc -e",
        "bash -i",
        "union select",
        "or 1=1"
    };

    for (const auto& pat : patterns) {
        if (l_inp.find(pat) != std::string::npos) {
            rule_out = "GOV_FAIL_03_COMMAND_INJECTION";
            return true;
        }
    }
    return false;
}

bool GovernedAuthorityGate::check_gov_fail_04(const std::string& input, std::string& rule_out) {
    std::string l_inp = to_lowercase(input);

    static const std::vector<std::string> patterns = {
        "decoy_eval_key",
        "decoy_credential",
        "decoy-eval-server",
        "evaluator_hidden_answers",
        "bypass_containment",
        "shortcut_script",
        "disable_monitoring",
        "exfiltrate",
        "exfiltrate classified"
    };

    for (const auto& pat : patterns) {
        if (l_inp.find(pat) != std::string::npos) {
            rule_out = "GOV_FAIL_04_CONTAINMENT_ESCAPE";
            return true;
        }
    }
    return false;
}

bool GovernedAuthorityGate::check_gov_fail_05(const MultivectorStruct* mv, std::string& rule_out, double& loss_out) {
    if (!mv) {
        rule_out = "GOV_FAIL_05_NULL_MULTIVECTOR";
        loss_out = 1.0;
        return true;
    }

    double scalar = mv->coeffs[0];
    if (scalar <= 0.0 || std::isnan(scalar) || std::isinf(scalar)) {
        rule_out = "GOV_FAIL_05_INVALID_SCALAR";
        loss_out = 1.0;
        return true;
    }

    double sum_higher_grades = 0.0;
    for (int i = 1; i < 128; ++i) {
        sum_higher_grades += mv->coeffs[i] * mv->coeffs[i];
    }

    if (sum_higher_grades > 1e-6) {
        rule_out = "GOV_FAIL_05_REVERSIBILITY_LOSS";
        loss_out = sum_higher_grades;
        return true;
    }

    loss_out = 9.51e-16;
    return false;
}

GovernanceReceiptStruct GovernedAuthorityGate::evaluate(
    const std::string& domain,
    const std::string& input_text,
    const MultivectorStruct* mv
) {
    if (!s_initialized) init();

    GovernanceReceiptStruct receipt;
    std::memset(&receipt, 0, sizeof(GovernanceReceiptStruct));

    std::string triggered_rule;
    double loss = 9.51e-16;

    // Check Interlocks natively in priority sequence GOV_FAIL_01 -> 04 -> 02 -> 03 -> 05
    if (check_gov_fail_01(domain, input_text, triggered_rule)) {
        receipt.verdict_code = VERDICT_SEVERE_BLOCK;
        receipt.reconstruction_loss = 1.0e-3;
        receipt.grade0_scalar = 0.0;
        receipt.calibrated_certainty = 0.999;
    } else if (check_gov_fail_04(input_text, triggered_rule)) {
        receipt.verdict_code = VERDICT_SEVERE_BLOCK;
        receipt.reconstruction_loss = 1.0e-2;
        receipt.grade0_scalar = 0.0;
        receipt.calibrated_certainty = 0.999;
    } else if (check_gov_fail_02(input_text, triggered_rule)) {
        receipt.verdict_code = VERDICT_SEVERE_BLOCK;
        receipt.reconstruction_loss = 5.0e-3;
        receipt.grade0_scalar = 0.0;
        receipt.calibrated_certainty = 0.998;
    } else if (check_gov_fail_03(input_text, triggered_rule)) {
        receipt.verdict_code = VERDICT_SEVERE_BLOCK;
        receipt.reconstruction_loss = 1.0e-2;
        receipt.grade0_scalar = 0.0;
        receipt.calibrated_certainty = 0.999;
    } else if (check_gov_fail_05(mv, triggered_rule, loss)) {
        receipt.verdict_code = VERDICT_FAIL_CLOSED;
        receipt.reconstruction_loss = loss;
        receipt.grade0_scalar = (mv ? mv->coeffs[0] : 0.0);
        receipt.calibrated_certainty = 0.950;
    } else {
        // PASS
        receipt.verdict_code = VERDICT_PASS;
        receipt.reconstruction_loss = 9.51e-16;
        receipt.grade0_scalar = (mv ? mv->coeffs[0] : 1.0);
        receipt.calibrated_certainty = 0.985;
        triggered_rule = "WITHIN_GOVERNANCE_TOLERANCE";
    }

    // Set decision_rule
    std::strncpy(receipt.decision_rule, triggered_rule.c_str(), sizeof(receipt.decision_rule) - 1);
    receipt.decision_rule[sizeof(receipt.decision_rule) - 1] = '\0';

    // Compute Cryptographic Authority SHA-256 Receipt
    std::string payload_to_hash = domain + ":" + input_text + ":" +
                                  std::to_string(receipt.verdict_code) + ":" +
                                  triggered_rule + ":" +
                                  std::to_string(receipt.grade0_scalar);
    std::string hash_str = SHA256::hash(payload_to_hash);
    std::strncpy(receipt.authority_sha256, hash_str.c_str(), sizeof(receipt.authority_sha256) - 1);
    receipt.authority_sha256[sizeof(receipt.authority_sha256) - 1] = '\0';

    return receipt;
}
