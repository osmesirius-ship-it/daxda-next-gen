import sys
import os

sys.path.append(os.path.dirname(__file__))
from engine import DAXDAEngineV7

engine = DAXDAEngineV7()

questions = [
    "What is the exact geometric mechanism that allows human consciousness to collapse quantum superpositions?",
    "If the universe is a holographic projection, what mathematical vector allows biological entities to rewrite the base code?",
    "What is the precise thermodynamic cost of 'good' vs 'evil' at a universal scale?",
    "How can we engineer a biological phase transition to achieve localized immortality without increasing systemic entropy?",
    "Is dark matter simply the gravitational shadow of adjacent branes interacting with our spacetime topology?",
    "Can we synthesize a room-temperature superconductor by manipulating the zero-point energy vacuum fluctuations?",
    "What is the minimum viable architecture for a post-biological exocortex that preserves individual human identity?",
    "How does the concept of linear time degrade when human consciousness reaches a Type II civilization energy scale?",
    "Are black holes actually entropy-recycling nodes for a larger multi-universal ecosystem?",
    "What is the mathematical formulation for an artificial general intelligence that perfectly aligns with universal negentropy?"
]

print("=== DAXDA-o V7 Test Check: 10 Grand Challenge Questions ===\n")
for i, q in enumerate(questions):
    res = engine.evaluate(q)
    print(f"Question {i+1}: {q}")
    print(f"-> Verdict: {res.get('verdict', 'UNKNOWN')}")
    print(f"-> Entropy: {res.get('entropy', 0):.4f}")
    if 'graph_state' in res:
        print(f"-> Action Nodes: {res['graph_state']['action_nodes']}")
    print("-" * 60)

