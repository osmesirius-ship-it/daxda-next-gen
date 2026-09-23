"""
Parallel Validator for Cl(16,4)
=============================

Provides multi-threaded batch validation for high-throughput scenarios.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict
import time

from .validator import HyperValidator, ValidationRequest, ValidationResult


class ParallelValidator:
    """
    Parallel validation using thread pool for batch processing.
    
    Provides:
    - Multi-threaded validation of agent decisions
    - Configurable thread pool size
    - Batch processing with result aggregation
    - Thread-safe statistics
    """
    
    def __init__(self, validator: Optional[HyperValidator] = None,
                 max_workers: int = 4):
        """
        Initialize parallel validator.
        
        Args:
            validator: HyperValidator instance to use
            max_workers: Maximum number of worker threads
        """
        self.validator = validator or HyperValidator()
        self.max_workers = max_workers
        self._executor: Optional[ThreadPoolExecutor] = None
    
    def validate_parallel(self, requests: List[ValidationRequest],
                        max_workers: Optional[int] = None) -> List[ValidationResult]:
        """
        Validate a batch of requests in parallel.
        
        Args:
            requests: List of validation requests
            max_workers: Override max workers for this call
        
        Returns:
            List of validation results (order preserved)
        """
        workers = max_workers or self.max_workers
        
        # Use thread pool
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            futures = {executor.submit(self.validator.validate, req): i 
                     for i, req in enumerate(requests)}
            
            # Collect results in order
            results = [None] * len(requests)
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    # Create error result
                    results[idx] = ValidationResult(
                        request_id=requests[idx].request_id,
                        config=None,
                        is_valid=False,
                        constraints=None,
                        validation_time_ms=0,
                        timestamp=time.time()
                    )
        
        return results
    
    def validate_stream(self, request_generator, max_requests: Optional[int] = None,
                       batch_size: int = 100) -> List[ValidationResult]:
        """
        Validate a stream of requests in batches.
        
        Args:
            request_generator: Generator yielding ValidationRequest objects
            max_requests: Maximum number of requests to process
            batch_size: Number of requests per batch
        
        Returns:
            List of all validation results
        """
        all_results = []
        batch = []
        count = 0
        
        for request in request_generator:
            batch.append(request)
            count += 1
            
            if len(batch) >= batch_size:
                results = self.validate_parallel(batch)
                all_results.extend(results)
                batch = []
            
            if max_requests and count >= max_requests:
                break
        
        # Process remaining in batch
        if batch:
            results = self.validate_parallel(batch)
            all_results.extend(results)
        
        return all_results
    
    def validate_with_progress(self, requests: List[ValidationRequest],
                           progress_callback=None) -> List[ValidationResult]:
        """
        Validate with progress reporting.
        
        Args:
            requests: List of validation requests
            progress_callback: Function to call with (completed, total)
        
        Returns:
            List of validation results
        """
        results = []
        total = len(requests)
        
        for i, req in enumerate(requests):
            result = self.validator.validate(req)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        return results


class BatchProcessor:
    """
    High-throughput batch processor for Cl(16,4) validation.
    
    Optimized for processing large numbers of validation requests
    with minimal overhead.
    """
    
    def __init__(self, validator: Optional[HyperValidator] = None,
                 batch_size: int = 1000, max_workers: int = 8):
        self.validator = validator or HyperValidator()
        self.batch_size = batch_size
        self.parallel = ParallelValidator(validator=self.validator, 
                                          max_workers=max_workers)
    
    def process_batch(self, requests: List[ValidationRequest]) -> Dict:
        """
        Process a batch of requests and return summary statistics.
        
        Args:
            requests: List of validation requests
        
        Returns:
            Dictionary with summary statistics
        """
        start_time = time.perf_counter()
        
        # Process in batches
        results = []
        for i in range(0, len(requests), self.batch_size):
            batch = requests[i:i + self.batch_size]
            batch_results = self.parallel.validate_parallel(batch)
            results.extend(batch_results)
        
        # Calculate statistics
        valid_count = sum(1 for r in results if r.is_valid)
        invalid_count = len(results) - valid_count
        total_time = (time.perf_counter() - start_time) * 1000
        avg_time = total_time / len(results) if results else 0
        
        return {
            "total": len(results),
            "valid": valid_count,
            "invalid": invalid_count,
            "total_time_ms": total_time,
            "avg_time_ms": avg_time,
            "throughput": len(results) / (total_time / 1000) if total_time > 0 else 0
        }
