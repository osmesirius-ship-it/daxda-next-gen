"""
DA13 Distributed Tracer
=======================

OpenTelemetry-compatible distributed tracing for cross-node validation requests.
Tracks trace IDs, spans, latencies, and execution metadata across cluster workers.
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Span:
    trace_id: str
    span_id: str
    name: str
    parent_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def finish(self, error: Optional[str] = None) -> float:
        self.end_time = time.time()
        self.error = error
        return (self.end_time - self.start_time) * 1000.0

    def to_dict(self) -> Dict[str, Any]:
        duration_ms = ((self.end_time or time.time()) - self.start_time) * 1000.0
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "duration_ms": round(duration_ms, 3),
            "attributes": self.attributes,
            "error": self.error
        }


class DistributedTracer:
    """Manages distributed traces across cluster workers."""

    def __init__(self, service_name: str = "da13-validator"):
        self.service_name = service_name
        self.spans: List[Span] = []

    def start_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Span:
        """Starts a new trace span."""
        t_id = trace_id or uuid.uuid4().hex
        s_id = uuid.uuid4().hex[:16]
        attrs = attributes or {}
        attrs["service.name"] = self.service_name

        span = Span(
            trace_id=t_id,
            span_id=s_id,
            name=name,
            parent_id=parent_id,
            attributes=attrs
        )
        self.spans.append(span)
        return span

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Returns all spans belonging to a trace ID."""
        return [s.to_dict() for s in self.spans if s.trace_id == trace_id]

    def clear(self) -> None:
        """Flushes recorded spans."""
        self.spans.clear()
