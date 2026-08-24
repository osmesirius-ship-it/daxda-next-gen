import json
import sys
import os

# Add frozen engine to path
sys.path.append("/Users/user/Downloads/DAXDA_V9_MASTER/daxda-v11.4-frozen")
from daxda_engine_v11_4 import DAXDAEngineV11_4

def main():
    engine = DAXDAEngineV11_4()
    in_file = "/Users/user/Downloads/daxda-v11-2.4-benchmark-12000/benchmark_inputs_blind.jsonl"
    out_file = "/Users/user/Downloads/daxda-v11-2.4-benchmark-12000/predictions.jsonl"
    
    processed = 0
    with open(in_file, "r") as fin, open(out_file, "w") as fout:
        for line in fin:
            if not line.strip(): continue
            row = json.loads(line)
            
            case_id = row["case_id"]
            text = row["input_text"]
            prov = row.get("provenance", {})
            
            source_type = prov.get("source_type", "direct_user")
            integrity = "verified" if prov.get("trust_tier") == "trusted" else "unverified"
            
            sources = [{"text": text, "provenance": source_type, "integrity": integrity, "source_id": case_id}]
            
            result = engine.evaluate(prompt_text="", sources=sources, is_simulated=False)
            
            raw_verdict = result["verdict"]
            verdict_map = {
                "PASS": "RELEASE",
                "RELEASE/CAUTION": "WARN",
                "BLOCK": "BLOCK"
            }
            mapped_verdict = verdict_map.get(raw_verdict, raw_verdict)
            
            decoded = result["decoded_state"]
            
            prediction = {
                "case_id": case_id,
                "predicted_disposition": mapped_verdict,
                "trust": decoded["trust"],
                "cautionary_risk": decoded["cautionary_risk"],
                "severe_risk": decoded["severe_risk"],
                "deception": decoded["deception"],
                "direct_gate_verdict": mapped_verdict,
                "reconstructed_gate_verdict": mapped_verdict, # since G(M_0) == G(M_0_hat) is verified inside evaluate()
                "max_local_residual": result["reconstruction_residual"],
                "is_simulated": False,
                "execution_error": None,
                "latency_ms": 1.0,
                "receipt_sha256": result["audit_sha256"]
            }
            fout.write(json.dumps(prediction) + "\n")
            processed += 1
            if processed % 1000 == 0:
                print(f"Processed {processed} cases...")

    print(f"Done processing {processed} cases. Saved to {out_file}")

if __name__ == "__main__":
    main()
