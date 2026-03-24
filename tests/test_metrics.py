"""
Tests for the metrics collector.
"""

import time
import pytest
from loadtest.metrics import MetricsCollector, RequestResult


class TestRequestResult:
    """Test cases for the RequestResult class."""

    def test_request_result_creation(self):
        """Test creating a request result."""
        result = RequestResult(response_time=0.123, status_code=200)
        assert result.response_time == 0.123
        assert result.status_code == 200
        assert result.error is None
        assert result.timestamp > 0

    def test_request_result_with_error(self):
        """Test creating a request result with an error."""
        result = RequestResult(response_time=0.5, status_code=500, error="Server Error")
        assert result.response_time == 0.5
        assert result.status_code == 500
        assert result.error == "Server Error"

    def test_is_success_for_2xx_status(self):
        """Test that 2xx status codes are considered successful."""
        result_200 = RequestResult(response_time=0.1, status_code=200)
        result_201 = RequestResult(response_time=0.1, status_code=201)
        result_204 = RequestResult(response_time=0.1, status_code=204)

        assert result_200.is_success is True
        assert result_201.is_success is True
        assert result_204.is_success is True

    def test_is_success_for_non_2xx_status(self):
        """Test that non-2xx status codes are not considered successful."""
        result_400 = RequestResult(response_time=0.1, status_code=400)
        result_404 = RequestResult(response_time=0.1, status_code=404)
        result_500 = RequestResult(response_time=0.1, status_code=500)

        assert result_400.is_success is False
        assert result_404.is_success is False
        assert result_500.is_success is False

    def test_is_success_with_error(self):
        """Test that requests with errors are not considered successful."""
        result = RequestResult(response_time=0.1, status_code=200, error="Timeout")
        assert result.is_success is False


class TestMetricsCollector:
    """Test cases for the MetricsCollector class."""

    def test_collector_initialization(self):
        """Test that collector initializes with empty state."""
        collector = MetricsCollector()
        assert collector.results == []
        assert collector.start_time is None
        assert collector.end_time is None

    def test_start_and_end(self):
        """Test starting and ending the collector."""
        collector = MetricsCollector()
        collector.start()
        assert collector.start_time is not None
        start = collector.start_time

        time.sleep(0.01)
        collector.end()
        assert collector.end_time is not None
        assert collector.end_time > start

    def test_add_result(self):
        """Test adding results to the collector."""
        collector = MetricsCollector()
        result1 = RequestResult(response_time=0.1, status_code=200)
        result2 = RequestResult(response_time=0.2, status_code=201)

        collector.add_result(result1)
        assert len(collector.results) == 1

        collector.add_result(result2)
        assert len(collector.results) == 2
        assert collector.results[0] == result1
        assert collector.results[1] == result2

    def test_get_statistics_empty(self):
        """Test statistics for empty collector."""
        collector = MetricsCollector()
        stats = collector.get_statistics()

        assert stats['total_requests'] == 0
        assert stats['successful_requests'] == 0
        assert stats['failed_requests'] == 0
        assert stats['error_rate'] == 0.0
        assert stats['throughput'] == 0.0
        assert stats['duration'] == 0.0
        assert stats['status_codes'] == {}

    def test_get_statistics_single_result(self):
        """Test statistics with a single result."""
        collector = MetricsCollector()
        collector.start()
        time.sleep(0.01)
        collector.add_result(RequestResult(response_time=0.123, status_code=200))
        collector.end()

        stats = collector.get_statistics()

        assert stats['total_requests'] == 1
        assert stats['successful_requests'] == 1
        assert stats['failed_requests'] == 0
        assert stats['error_rate'] == 0.0
        assert stats['response_times']['min'] == 0.123
        assert stats['response_times']['max'] == 0.123
        assert stats['response_times']['mean'] == 0.123
        assert stats['response_times']['median'] == 0.123
        assert stats['throughput'] > 0
        assert stats['status_codes'] == {200: 1}

    def test_get_statistics_multiple_results(self):
        """Test statistics with multiple results."""
        collector = MetricsCollector()
        collector.start()

        # Add various results
        collector.add_result(RequestResult(response_time=0.1, status_code=200))
        collector.add_result(RequestResult(response_time=0.2, status_code=200))
        collector.add_result(RequestResult(response_time=0.3, status_code=201))
        collector.add_result(RequestResult(response_time=0.4, status_code=404))
        collector.add_result(RequestResult(response_time=0.5, status_code=500))

        time.sleep(0.01)
        collector.end()

        stats = collector.get_statistics()

        assert stats['total_requests'] == 5
        assert stats['successful_requests'] == 3
        assert stats['failed_requests'] == 2
        assert stats['error_rate'] == 40.0
        assert stats['response_times']['min'] == 0.1
        assert stats['response_times']['max'] == 0.5
        assert stats['response_times']['mean'] == 0.3
        assert stats['response_times']['median'] == 0.3
        assert stats['throughput'] > 0
        assert stats['status_codes'] == {200: 2, 201: 1, 404: 1, 500: 1}

    def test_response_time_percentiles(self):
        """Test percentile calculations for response times."""
        collector = MetricsCollector()

        # Add 100 results with response times from 0.01 to 1.00
        for i in range(1, 101):
            collector.add_result(RequestResult(response_time=i * 0.01, status_code=200))

        stats = collector.get_statistics()
        response_times = stats['response_times']

        assert response_times['min'] == 0.01
        assert response_times['max'] == 1.00
        assert 0.49 < response_times['median'] < 0.51
        assert 0.94 < response_times['p95'] < 0.96
        assert 0.98 < response_times['p99'] < 1.00

    def test_throughput_calculation(self):
        """Test throughput calculation."""
        collector = MetricsCollector()
        collector.start()

        # Add 10 results
        for _ in range(10):
            collector.add_result(RequestResult(response_time=0.01, status_code=200))

        time.sleep(0.1)
        collector.end()

        stats = collector.get_statistics()
        
        # Throughput should be approximately 10 requests / ~0.1 seconds = ~100 req/s
        # Allow for some variance
        assert stats['throughput'] > 50
        assert stats['throughput'] < 200

    def test_status_code_distribution(self):
        """Test status code distribution tracking."""
        collector = MetricsCollector()

        collector.add_result(RequestResult(response_time=0.1, status_code=200))
        collector.add_result(RequestResult(response_time=0.1, status_code=200))
        collector.add_result(RequestResult(response_time=0.1, status_code=200))
        collector.add_result(RequestResult(response_time=0.1, status_code=201))
        collector.add_result(RequestResult(response_time=0.1, status_code=404))
        collector.add_result(RequestResult(response_time=0.1, status_code=500))
        collector.add_result(RequestResult(response_time=0.1, status_code=500))

        stats = collector.get_statistics()

        assert stats['status_codes'][200] == 3
        assert stats['status_codes'][201] == 1
        assert stats['status_codes'][404] == 1
        assert stats['status_codes'][500] == 2

    def test_error_rate_calculation(self):
        """Test error rate calculation."""
        collector = MetricsCollector()

        # 7 successful, 3 failed
        for _ in range(7):
            collector.add_result(RequestResult(response_time=0.1, status_code=200))
        for _ in range(3):
            collector.add_result(RequestResult(response_time=0.1, status_code=500))

        stats = collector.get_statistics()
        assert stats['error_rate'] == 30.0

    def test_statistics_without_explicit_start_end(self):
        """Test that statistics work even without explicit start/end calls."""
        collector = MetricsCollector()

        # Add results without calling start/end
        collector.add_result(RequestResult(response_time=0.1, status_code=200))
        time.sleep(0.01)
        collector.add_result(RequestResult(response_time=0.2, status_code=200))

        stats = collector.get_statistics()

        # Should still calculate duration from timestamps
        assert stats['total_requests'] == 2
        assert stats['duration'] > 0
        assert stats['throughput'] > 0

    def test_percentile_edge_cases(self):
        """Test percentile calculation with edge cases."""
        collector = MetricsCollector()

        # Single value
        collector.add_result(RequestResult(response_time=0.5, status_code=200))
        stats = collector.get_statistics()
        assert stats['response_times']['p95'] == 0.5
        assert stats['response_times']['p99'] == 0.5

        # Two values
        collector2 = MetricsCollector()
        collector2.add_result(RequestResult(response_time=0.1, status_code=200))
        collector2.add_result(RequestResult(response_time=0.9, status_code=200))
        stats2 = collector2.get_statistics()
        # p95 should be interpolated between 0.1 and 0.9
        assert stats2['response_times']['p95'] > 0.1
        assert stats2['response_times']['p95'] <= 0.9
