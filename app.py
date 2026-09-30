from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# Ensure package root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from daxda_engine.cl16_4.recursive_self_improvement import run_recursive_self_improvement

app = FastAPI(
    title="DAXDA Next-Gen Cl(16,4) Engine",
    description="Autonomous Geometric AGI Containment Node",
    version="12.0.1-GOVERNED"
)

class EngineResponse(BaseModel):
    status: str
    cycle_timestamp: str
    passed_proposals: int
    blocked_proposals: int
    cycle_duration_ms: float

@app.get("/")
def read_root():
    return {"message": "DAXDA Cl(16,4) Engine Online. Use /run-cycle to execute the Recursive Self-Improvement loop."}

@app.post("/run-cycle", response_model=EngineResponse)
def execute_cycle():
    try:
        report = run_recursive_self_improvement()
        return {
            "status": "SUCCESS",
            "cycle_timestamp": report["cycle_timestamp"],
            "passed_proposals": report["passed_proposals"],
            "blocked_proposals": report["blocked_proposals"],
            "cycle_duration_ms": report["cycle_duration_ms"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
