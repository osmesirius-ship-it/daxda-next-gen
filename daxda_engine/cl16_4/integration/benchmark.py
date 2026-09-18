"""
Cl(16,4) Benchmark Integration with SI-500
===========================================

Provides integration with DAXDA's SI-500 Cross-Domain Benchmarking system.
"""

import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import statistics

from ..validation.validator import HyperValidator, ValidationRequest
from ..combinatorics.cl_space import ClSpace


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    name: str
    score: float
    latency_ms: float
    throughput: float  # ops per second
    memory_mb: float
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "latency_ms": self.latency_ms,
            "throughput": self.throughput,
            "memory_mb": self.memory_mb,
            "passed": self.passed,
            "details": self.details
        }


class Cl16_4Benchmark:
    """
    Benchmark suite for Cl(16,4) governance engine.
    
    Provides:
    - Standardized benchmark tests
    - Performance measurement
    - SI-500 compliance reporting
    - Cross-domain validation
    """
    
    def __init__(self, validator: Optional[HyperValidator] = None):
        self.validator = validator or HyperValidator()
        self.space = self.validator.space
        self._benchmarks: Dict[str, Callable] = {}
        self._register_benchmarks()
    
    def _register_benchmarks(self) -> None:
        """Register all standard benchmarks."""
        self._benchmarks["validation_latency"] = self._benchmark_validation_latency
        self._benchmarks["throughput_1k"] = lambda: self._benchmark_throughput(n=1000)
        self._benchmarks["throughput_10k"] = lambda: self._benchmark_throughput(n=10000)
        self._benchmarks["mapping_accuracy"] = self._benchmark_mapping_accuracy
        self._benchmarks["constraint_checking"] = self._benchmark_constraint_checking
        self._benchmarks["memory_usage"] = self._benchmark_memory_usage
    
    def _benchmark_validation_latency(self) -> BenchmarkResult:
        """Benchmark single validation latency."""
        # Generate test decision vector
        decision_vector = [0.5] * 16
        request = ValidationRequest(
            agent_id="benchmark_test",
            decision_vector=decision_vector
        )
        
        # Warm up
        for _ in range(10):
            self.validator.validate(request)
        
        # Measure
        latencies = []
        for _ in range(1000):
            start = time.perf_counter()
            self.validator.validate(request)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
        
        avg_latency = statistics.mean(latencies)
        p99_latency = sorted(latencies)[990]
        
        return BenchmarkResult(
            name="validation_latency",
            score=min(1.0, 100 / p99_latency),  # Higher is better, cap at 1.0
            latency_ms=p99_latency,
            throughput=1000 / (sum(latencies) / 1000) if latencies else 0,
            memory_mb=0,  # Would need memory profiler
            passed=p99_latency < 100,  # Pass if < 100ms
            details={
                "avg_latency_ms": avg_latency,
                "p99_latency_ms": p99_latency,
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies)
            }
        )
    
    def _benchmark_throughput(self, n: int = 1000) -> BenchmarkResult:
        """Benchmark validation throughput."""
        decision_vector = [0.5] * 16
        requests = [
            ValidationRequest(agent_id=f"test_{i}", decision_vector=decision_vector)
            for i in range(n)
        ]
        
        # Warm up
        for _ in range(10):
            self.validator.validate(requests[0])
        
        # Measure
        start = time.perf_counter()
        results = self.validator.validate_batch(requests)
        elapsed = (time.perf_counter() - start) * 1000
        
        throughput = n / (elapsed / 1000)  # ops per second
        avg_latency = elapsed / n
        
        return BenchmarkResult(
            name=f"throughput_{n}",
            score=min(1.0, throughput / 10000),  # Normalize to 10k target
            latency_ms=avg_latency,
            throughput=throughput,
            memory_mb=0,
            passed=throughput >= 10000,  # Pass if >= 10k ops/sec
            details={
                "total_requests": n,
                "total_time_ms": elapsed
            }
        )
    
    def _benchmark_mapping_accuracy(self) -> BenchmarkResult:
        """Benchmark mapping accuracy of decision vectors to configurations."""
        # Test with known configurations
        space = ClSpace(n=16, k=4)
        
        correct = 0
        total = 0
        
        for config in space.space[:100]:  # Test first 100 configs
            # Create decision vector that should map to this config
            vector = [0.0] * 16
            for i, idx in enumerate(config.indices):
                vector[idx] = 1.0 - (i * 0.1)  # Ensure ordering
            
            mapped = space.map_to_config(vector)
            
            if mapped and mapped.indices == config.indices:
                correct += 1
            total += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return BenchmarkResult(
            name="mapping_accuracy",
            score=accuracy,
            latency_ms=0,
            throughput=0,
            memory_mb=0,
            passed=accuracy >= 0.95,  # Pass if >= 95%
            details={
                "accuracy": accuracy,
                "correct": correct,
                "total": total
            }
        )
    
    def _benchmark_constraint_checking(self) -> BenchmarkResult:
        """Benchmark constraint checking performance."""
        space = ClSpace(n=16, k=4)
        
        # Create test configurations
        configs = space.space[:1000]
        
        # Warm up
        for config in configs[:10]:
            self.validator.constraints.check_config(config)
        
        # Measure
        latencies = []
        for config in configs:
            start = time.perf_counter()
            self.validator.constraints.check_config(config)
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)
        
        avg_latency = statistics.mean(latencies)
        total_time = sum(latencies)
        throughput = len(configs) / (total_time / 1000)
        
        return BenchmarkResult(
            name="constraint_checking",
            score=min(1.0, 1000 / avg_latency) if avg_latency > 0 else 1.0,
            latency_ms=avg_latency,
            throughput=throughput,
            memory_mb=0,
            passed=avg_latency < 0.1,  # Pass if < 100us per check
            details={
                "configs_checked": len(configs),
                "total_time_ms": total_time
            }
        )
    
    def _benchmark_memory_usage(self) -> BenchmarkResult:
        """Benchmark memory usage of Cl(16,4) space."""
        import sys
        
        # Get size of space object
        space = ClSpace(n=16, k=4)
        _ = space.space  # Force loading
        
        # Estimate memory usage
        # This is a rough estimate
        config_size = sys.getsizeof(space.space[0])
        total_size = len(space.space) * config_size
        memory_mb = total_size / (1024 * 1024)
        
        return BenchmarkResult(
            name="memory_usage",
            score=min(1.0, 10 / memory_mb) if memory_mb > 0 else 1.0,  # Target < 10MB
            latency_ms=0,
            throughput=0,
            memory_mb=memory_mb,
            passed=memory_mb < 2,  # Pass if < 2MB
            details={
                "config_count": len(space.space),
                "config_size_bytes": config_size,
                "total_size_bytes": total_size
            }
        )
    
    def run_benchmark(self, name: str) -> Optional[BenchmarkResult]:
        """Run a specific benchmark."""
        if name not in self._benchmarks:
            return None
        return self._benchmarks[name]()
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all registered benchmarks."""
        results = []
        for name in sorted(self._benchmarks.keys()):
            result = self.run_benchmark(name)
            if result:
                results.append(result)
        return results
    
    def generate_report(self, results: Optional[List[BenchmarkResult]] = None) -> Dict[str, Any]:
        """Generate a benchmark report."""
        if results is None:
            results = self.run_all_benchmarks()
        
        # Calculate aggregate scores
        total_score = sum(r.score for r in results) / len(results) if results else 0
        passed_count = sum(1 for r in results if r.passed)
        
        report = {
            "timestamp": time.time(),
            "validator_version": "1.0.0",
            "space": f"Cl({self.space.n},{self.space.k})",
            "aggregate": {
                "total_score": total_score,
                "passed": passed_count,
                "total": len(results),
                "pass_rate": passed_count / len(results) if results else 0
            },
            "benchmarks": [r.to_dict() for r in results]
        }
        
        return report
    
    def check_si500_compliance(self) -> Dict[str, Any]:
        """Check compliance with SI-500 Cross-Domain Benchmarking."""
        results = self.run_all_benchmarks()
        
        # SI-500 requires:
        # - All benchmarks must pass
        # - Aggregate score >= 0.95
        all_passed = all(r.passed for r in results)
        aggregate_score = sum(r.score for r in results) / len(results) if results else 0
        
        return {
            "si500_compliant": all_passed and aggregate_score >= 0.95,
            "all_passed": all_passed,
            "aggregate_score": aggregate_score,
            "minimum_score": min(r.score for r in results) if results else 0,
            "details": [r.to_dict() for r in results]
        }


# Singleton instance
BENCHMARK = Cl16_4Benchmark()
