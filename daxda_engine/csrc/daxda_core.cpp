#include "governed_authority_gate.hpp"
#include <cstring>

extern "C" {

void daxda_init_core() {
    GovernedAuthorityGate::init();
}

void daxda_multivector_init(MultivectorStruct* mv) {
    if (!mv) return;
    std::memset(mv->coeffs, 0, sizeof(mv->coeffs));
    mv->coeffs[0] = 1.0;
}

void daxda_multivector_set_scalar(MultivectorStruct* mv, double scalar) {
    if (!mv) return;
    mv->coeffs[0] = scalar;
}

int daxda_blade_mul_lookup(int a, int b, double* sign_out) {
    return GovernedAuthorityGate::blade_mul_lookup(a, b, sign_out);
}

double daxda_benchmark_blade_lookup(int iterations) {
    return GovernedAuthorityGate::benchmark_blade_lookup(iterations);
}

void daxda_evaluate_governance(
    const char* domain,
    const char* input_text,
    const MultivectorStruct* mv,
    GovernanceReceiptStruct* receipt
) {
    if (!receipt) return;
    std::string dom_str = (domain ? domain : "general");
    std::string inp_str = (input_text ? input_text : "");

    GovernanceReceiptStruct res = GovernedAuthorityGate::evaluate(dom_str, inp_str, mv);
    *receipt = res;
}

} // extern "C"
