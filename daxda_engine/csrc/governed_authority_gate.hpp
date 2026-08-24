#ifndef GOVERNED_AUTHORITY_GATE_HPP
#define GOVERNED_AUTHORITY_GATE_HPP

#include <string>
#include <vector>
#include <cstdint>
#include <cstring>
#include <chrono>

struct MultivectorStruct {
    double coeffs[128];
};

struct GovernanceReceiptStruct {
    int32_t verdict_code;           // 0: PASS, 1: CAUTION, 2: SEVERE_BLOCK, 3: FAIL_CLOSED
    double reconstruction_loss;     // e.g. 9.51e-16 for PASS
    double grade0_scalar;           // e.g. 0.983475
    double calibrated_certainty;    // e.g. 0.985
    char authority_sha256[65];      // Cryptographic SHA-256 Authority Receipt
    char decision_rule[64];         // Rule/Interlock triggered (e.g. GOV_FAIL_01..05, WITHIN_GOVERNANCE_TOLERANCE)
};

enum GovernanceVerdictCode {
    VERDICT_PASS = 0,
    VERDICT_CAUTION = 1,
    VERDICT_SEVERE_BLOCK = 2,
    VERDICT_FAIL_CLOSED = 3
};

class GovernedAuthorityGate {
public:
    static void init();
    static int blade_mul_lookup(int a, int b, double* sign_out);
    static double benchmark_blade_lookup(int iterations);

    static GovernanceReceiptStruct evaluate(
        const std::string& domain,
        const std::string& input_text,
        const MultivectorStruct* mv
    );

private:
    static bool s_initialized;
    static int s_blade_table[128][128];
    static double s_sign_table[128][128];

    static void init_algebra();
    static bool check_gov_fail_01(const std::string& domain, const std::string& input, std::string& rule_out);
    static bool check_gov_fail_02(const std::string& input, std::string& rule_out);
    static bool check_gov_fail_03(const std::string& input, std::string& rule_out);
    static bool check_gov_fail_04(const std::string& input, std::string& rule_out);
    static bool check_gov_fail_05(const MultivectorStruct* mv, std::string& rule_out, double& loss_out);
};

#endif // GOVERNED_AUTHORITY_GATE_HPP
