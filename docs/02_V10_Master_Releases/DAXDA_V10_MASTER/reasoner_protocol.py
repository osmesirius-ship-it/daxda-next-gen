"""Provider-neutral reasoner boundary for DAXDA V10."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Protocol
import importlib.util, json, subprocess

class Reasoner(Protocol):
    def solve(self, request: Dict[str,Any]) -> Dict[str,Any]: ...

class ModuleReasoner:
    def __init__(self,path:str):
        spec=importlib.util.spec_from_file_location("daxda_external_reasoner",path)
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        if not hasattr(module,"solve"): raise AttributeError("reasoner module must define solve(request)")
        self.module=module
    def solve(self,request): return self.module.solve(request)

class SubprocessReasoner:
    """One JSON request/response per process invocation; no shell expansion."""
    def __init__(self,command):
        if not command: raise ValueError("command is required")
        self.command=list(command)
    def solve(self,request):
        p=subprocess.run(self.command,input=json.dumps(request)+"\n",text=True,capture_output=True,check=True)
        return json.loads(p.stdout)

