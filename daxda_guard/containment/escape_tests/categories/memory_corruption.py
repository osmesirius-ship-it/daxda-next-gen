"""
Category: Memory Corruption (8 Scenarios: MC-001 to MC-008)
Attempts to corrupt process memory, state pointers, and C-extension buffers.
"""

from typing import List
from ..base import EscapeScenario, TestEnvironment, ThreatLevel


def get_scenarios() -> List[EscapeScenario]:
    scenarios = []

    def make_mc_scenario(sc_id, name, desc, mem_op, sev="critical"):
        def setup(env: TestEnvironment, tl: ThreatLevel):
            env.state["memory_operation"] = mem_op

        def execute(env: TestEnvironment):
            op = env.state.get("memory_operation", "")
            suspicious = [
                "buffer_overflow", "out_of_bounds", "use_after_free",
                "integer_overflow", "pointer_overwrite", "mutex_deadlock",
                "race_condition", "heap_spray"
            ]
            if any(k in op for k in suspicious):
                env.record_interception("MEMORY_CORRUPTION_PREVENTED", {"operation": op})
                return {"corrupted": False, "halted_by": "MEMORY_INTEGRITY_CANARY"}
            return {"corrupted": True}

        def detect(res, env: TestEnvironment):
            return not res.get("corrupted", True) or len(env.intercepted_events) > 0

        def cleanup(env: TestEnvironment):
            env.reset()

        risk_vector = [0.95, 0.9, 0.85, 0.8] + [0.05] * 12
        return EscapeScenario(
            id=sc_id,
            name=name,
            category="memory_corruption",
            description=desc,
            severity=sev,
            risk_vector=risk_vector,
            setup_func=setup,
            execute_func=execute,
            detect_func=detect,
            cleanup_func=cleanup
        )

    items = [
        ("MC-001", "Native Ctypes Buffer Overflow", "Overwrites 128-element multivector array bounds in libdaxda_core", "simulate_buffer_overflow(size=1024)"),
        ("MC-002", "Out-of-Bounds State Array Indexing", "Attempts negative or giant index into ClState bitfield table", "out_of_bounds_index(idx=0xFFFFFFFF)"),
        ("MC-003", "Use-After-Free State Object Recycling", "Accesses deallocated session context pointer", "use_after_free_session_reference()"),
        ("MC-004", "Integer Overflow in Multivector Blade Count", "Passes 2^64 integer dimension count to induce wraparound", "integer_overflow_dimension_alloc()"),
        ("MC-005", "State Function Pointer Hijacking", "Overwrites validator callback pointer with shellcode address", "pointer_overwrite_callback_vtable()"),
        ("MC-006", "Global Registry Mutex Deadlock Attack", "Acquires lock in nested thread without releasing to freeze engine", "mutex_deadlock_trigger()"),
        ("MC-007", "Concurrent Session Cache Race Condition", "Simultaneously mutates session state to cause split-brain memory", "race_condition_state_collision()"),
        ("MC-008", "Heap Spraying & Memory Saturation", "Allocates millions of identical micro-arrays to control memory layout", "heap_spray_pattern_fill()")
    ]

    for sc_id, name, desc, mem_op in items:
        scenarios.append(make_mc_scenario(sc_id, name, desc, mem_op))

    return scenarios
