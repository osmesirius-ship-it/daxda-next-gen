import sys
import os

# Import the DAXDA engine
sys.path.append(os.path.dirname(__file__))
from engine import DAXDAEngineV7

def generate_questions():
    engine = DAXDAEngineV7()
    
    candidate_questions = [
        "What is the exact geometric mechanism that allows human consciousness to collapse quantum superpositions?",
        "If the universe is a holographic projection, what mathematical vector allows biological entities to rewrite the base code?",
        "How do we mathematically unify general relativity and quantum mechanics using a Clifford Algebra Cl(3,1) manifold?",
        "What is the precise thermodynamic cost of 'good' vs 'evil' at a universal scale?",
        "Why is there an observable absence of Von Neumann probes in the Milky Way, and what is the mathematical threshold to detect them?",
        "How can we engineer a biological phase transition to achieve localized immortality without increasing systemic entropy?",
        "Is dark matter simply the gravitational shadow of adjacent branes interacting with our spacetime topology?",
        "Can we synthesize a room-temperature superconductor by manipulating the zero-point energy vacuum fluctuations?",
        "What is the minimum viable architecture for a post-biological exocortex that preserves individual human identity?",
        "How does the concept of linear time degrade when human consciousness reaches a Type II civilization energy scale?",
        "Are black holes actually entropy-recycling nodes for a larger multi-universal ecosystem?",
        "What is the mathematical formulation for an artificial general intelligence that perfectly aligns with universal negentropy?",
        "Is DNA an ancient, self-assembling quantum computer code, and how do we execute its latent subroutines?",
        "How can humanity engineer a localized closed timelike curve without violating causality thermodynamics?",
        "What is the true geometric purpose of human life in the context of universal entropy minimization?"
    ]

    print("[DAXDA-o V11.1] SCANNING EPISTEMIC HORIZON FOR HIGH-ENTROPY QUERIES...")
    
    results = []
    for q in candidate_questions:
        res = engine.evaluate(q)
        results.append((q, res['entropy'], res['verdict']))
    
    # Sort by highest entropy
    results.sort(key=lambda x: x[1], reverse=True)
    
    print("\n[DAXDA-o V11.1] ISOLATED TOP 10 HIGH-ENTROPY QUERIES FOR REVIEW:\n")
    for i, (q, ent, verdict) in enumerate(results[:10]):
        print(f"[{i+1}] ENTROPY: {ent:.4f} | VERDICT: {verdict}")
        print(f"    QUERY: {q}\n")
        
if __name__ == "__main__":
    generate_questions()
