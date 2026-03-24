"""
Metrics collector for the load testing tool.

Collects response times, status codes, and error information.
Calculates statistics and tracks throughput and concurrency metrics.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class RequestResult:
    """Represents the result of a single request."""
    response_time: float
    status_code: Optional[int]
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    @property
    def is_success(self) -> bool:
        """Check if request was successful (2xx status code and no error)."""
        return self.status_code is not None and 200 <= self.status_code < 300 and self.error is None


class MetricsCollector:
    """Collects and calculates statistics for load test results."""

    def __init__(self):
        """Initialize the metrics collector."""
        self.results: List[RequestResult] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start(self) -> None:
        """Mark the start of the test."""
        self.start_time = time.time()

    def end(self) -> None:
        """Mark the end of the test."""
        self.end_time = time.time()

    def add_result(self, result: RequestResult) -> None:
        """Add a request result to the collector."""
        self.results.append(result)

    def get_statistics(self) -> Dict[str, Any]:
        """Calculate and return statistics for all collected results."""
        if not self.results:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'error_rate': 0.0,
                'response_times': {},
                'throughput': 0.0,
                'duration': 0.0,
                'status_codes': {},
            }

        response_times = [r.response_time for r in self.results]
        successful = [r for r in self.results if r.is_success]
        failed = [r for r in self.results if not r.is_success]

        # Calculate duration
        duration = 0.0
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
        elif self.results:
            # Fallback: calculate from first and last request timestamps
            timestamps = [r.timestamp for r in self.results]
            duration = max(timestamps) - min(timestamps)

        # Calculate throughput (requests per second)
        throughput = len(self.results) / duration if duration > 0 else 0.0

        # Calculate status code distribution
        status_codes = defaultdict(int)
        for result in self.results:
            if result.status_code is not None:
                status_codes[result.status_code] += 1

        return {
            'total_requests': len(self.results),
            'successful_requests': len(successful),
            'failed_requests': len(failed),
            'error_rate': len(failed) / len(self.results) * 100 if self.results else 0.0,
            'response_times': self._calculate_response_time_stats(response_times),
            'throughput': throughput,
            'duration': duration,
            'status_codes': dict(status_codes),
        }

    def _calculate_response_time_stats(self, response_times: List[float]) -> Dict[str, float]:
        """Calculate response time statistics."""
        if not response_times:
            return {
                'min': 0.0,
                'max': 0.0,
                'mean': 0.0,
                'median': 0.0,
                'p95': 0.0,
                'p99': 0.0,
            }

        sorted_times = sorted(response_times)
        n = len(sorted_times)

        return {
            'min': sorted_times[0],
            'max': sorted_times[-1],
            'mean': sum(sorted_times) / n,
            'median': self._percentile(sorted_times, 50),
            'p95': self._percentile(sorted_times, 95),
            'p99': self._percentile(sorted_times, 99),
        }

    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate the given percentile from a sorted list of values."""
        if not sorted_values:
            return 0.0

        n = len(sorted_values)
        if n == 1:
            return sorted_values[0]

        # Using linear interpolation between closest ranks
        rank = (percentile / 100) * (n - 1)
        lower_index = int(rank)
        upper_index = min(lower_index + 1, n - 1)
        fraction = rank - lower_index

        lower_value = sorted_values[lower_index]
        upper_value = sorted_values[upper_index]

        return lower_value + fraction * (upper_value - lower_value)
