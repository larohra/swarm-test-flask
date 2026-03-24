"""
Integration tests for the load testing tool.

Tests the load testing tool against the Flask app using end-to-end scenarios.
"""
import asyncio
import json
import multiprocessing
import time
import pytest

from app import app as flask_app, items
from loadtest.config import Config
from loadtest.engine import Engine
from loadtest.metrics import MetricsCollector, RequestResult as MetricsRequestResult


def run_flask_server(port):
    """Run Flask server in a separate process."""
    flask_app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


@pytest.fixture(scope="module")
def test_server():
    """Start Flask server for integration tests."""
    port = 15000
    server_process = multiprocessing.Process(target=run_flask_server, args=(port,))
    server_process.start()
    
    # Give server time to start
    time.sleep(2)
    
    yield f"http://127.0.0.1:{port}"
    
    # Cleanup
    server_process.terminate()
    server_process.join(timeout=5)
    if server_process.is_alive():
        server_process.kill()


@pytest.fixture(autouse=True)
def clear_items_fixture():
    """Clear items list before each test."""
    items.clear()
    yield
    items.clear()


def convert_engine_result_to_metrics(engine_result):
    """Convert engine.RequestResult to metrics.RequestResult."""
    return MetricsRequestResult(
        response_time=engine_result.response_time,
        status_code=engine_result.status_code,
        error=engine_result.error,
        timestamp=engine_result.timestamp
    )


class TestIntegration:
    """Integration test cases for the entire load testing tool."""

    @pytest.mark.asyncio
    async def test_get_requests_load_test(self, test_server):
        """Test GET requests with basic load."""
        config = Config(
            url=f"{test_server}/health",
            method="GET",
            requests=20,
            concurrency=5,
            timeout=10
        )
        
        engine = Engine(
            url=config.url,
            method=config.method,
            timeout=config.timeout,
            headers=config.headers,
            body=config.body
        )
        
        metrics = MetricsCollector()
        metrics.start()
        
        results = await engine.run(config.requests, config.concurrency)
        
        for result in results:
            metrics.add_result(convert_engine_result_to_metrics(result))
        
        metrics.end()
        
        stats = metrics.get_statistics()
        
        # Verify all requests completed
        assert stats['total_requests'] == 20
        assert stats['successful_requests'] == 20
        assert stats['failed_requests'] == 0
        assert stats['error_rate'] == 0.0
        
        # Verify status codes
        assert 200 in stats['status_codes']
        assert stats['status_codes'][200] == 20
        
        # Verify response times are reasonable
        assert stats['response_times']['mean'] < 1.0
        assert stats['response_times']['max'] < 2.0

    @pytest.mark.asyncio
    async def test_post_requests_load_test(self, test_server):
        """Test POST requests with JSON data."""
        config = Config(
            url=f"{test_server}/api/items",
            method="POST",
            requests=10,
            concurrency=3,
            timeout=10,
            headers={"Content-Type": "application/json"},
            body='{"name": "Test Item", "description": "Test Description"}'
        )
        
        engine = Engine(
            url=config.url,
            method=config.method,
            timeout=config.timeout,
            headers=config.headers,
            body=config.body
        )
        
        metrics = MetricsCollector()
        metrics.start()
        
        results = await engine.run(config.requests, config.concurrency)
        
        for result in results:
            metrics.add_result(convert_engine_result_to_metrics(result))
        
        metrics.end()
        
        stats = metrics.get_statistics()
        
        # Verify all requests completed successfully
        assert stats['total_requests'] == 10
        assert stats['successful_requests'] == 10
        assert stats['failed_requests'] == 0
        
        # Verify status codes (201 for created)
        assert 201 in stats['status_codes']
        assert stats['status_codes'][201] == 10

    @pytest.mark.asyncio
    async def test_concurrent_load(self, test_server):
        """Test high concurrency load."""
        config = Config(
            url=f"{test_server}/health",
            method="GET",
            requests=50,
            concurrency=25,
            timeout=10
        )
        
        engine = Engine(
            url=config.url,
            method=config.method,
            timeout=config.timeout,
            headers=config.headers,
            body=config.body
        )
        
        metrics = MetricsCollector()
        metrics.start()
        
        results = await engine.run(config.requests, config.concurrency)
        
        for result in results:
            metrics.add_result(convert_engine_result_to_metrics(result))
        
        metrics.end()
        
        stats = metrics.get_statistics()
        
        # Verify all requests completed
        assert stats['total_requests'] == 50
        assert stats['successful_requests'] == 50
        assert stats['failed_requests'] == 0
        
        # Verify throughput is reasonable with concurrency
        assert stats['throughput'] > 10  # At least 10 requests per second
        assert stats['duration'] < 10  # Should complete in reasonable time

    @pytest.mark.asyncio
    async def test_error_handling_bad_request(self, test_server):
        """Test handling of bad requests that return 400 errors."""
        # POST without required fields should return 400
        config = Config(
            url=f"{test_server}/api/items",
            method="POST",
            requests=5,
            concurrency=2,
            timeout=10,
            headers={"Content-Type": "application/json"},
            body='{"name": "Missing description"}'
        )
        
        engine = Engine(
            url=config.url,
            method=config.method,
            timeout=config.timeout,
            headers=config.headers,
            body=config.body
        )
        
        metrics = MetricsCollector()
        metrics.start()
        
        results = await engine.run(config.requests, config.concurrency)
        
        for result in results:
            metrics.add_result(convert_engine_result_to_metrics(result))
        
        metrics.end()
        
        stats = metrics.get_statistics()
        
        # Verify all requests completed but with errors
        assert stats['total_requests'] == 5
        assert stats['failed_requests'] == 5
        assert stats['successful_requests'] == 0
        assert stats['error_rate'] == 100.0
        
        # Verify 400 status codes
        assert 400 in stats['status_codes']
        assert stats['status_codes'][400] == 5

    @pytest.mark.asyncio
    async def test_error_handling_not_found(self, test_server):
        """Test handling of 404 errors."""
        config = Config(
            url=f"{test_server}/nonexistent",
            method="GET",
            requests=5,
            concurrency=2,
            timeout=10
        )
        
        engine = Engine(
            url=config.url,
            method=config.method,
            timeout=config.timeout,
            headers=config.headers,
            body=config.body
        )
        
        metrics = MetricsCollector()
        metrics.start()
        
        results = await engine.run(config.requests, config.concurrency)
        
        for result in results:
            metrics.add_result(convert_engine_result_to_metrics(result))
        
        metrics.end()
        
        stats = metrics.get_statistics()
        
        # Verify all requests completed but got 404
        assert stats['total_requests'] == 5
        assert stats['failed_requests'] == 5
        
        # Verify 404 status codes
        assert 404 in stats['status_codes']

    @pytest.mark.asyncio
    async def test_mixed_get_and_post(self, test_server):
        """Test mixed GET and POST requests scenarios."""
        # First do some POST requests to populate data
        post_config = Config(
            url=f"{test_server}/api/items",
            method="POST",
            requests=5,
            concurrency=2,
            timeout=10,
            headers={"Content-Type": "application/json"},
            body='{"name": "Item", "description": "Description"}'
        )
        
        post_engine = Engine(
            url=post_config.url,
            method=post_config.method,
            timeout=post_config.timeout,
            headers=post_config.headers,
            body=post_config.body
        )
        
        post_results = await post_engine.run(post_config.requests, post_config.concurrency)
        
        # Then do GET requests to verify data
        get_config = Config(
            url=f"{test_server}/api/items",
            method="GET",
            requests=10,
            concurrency=5,
            timeout=10
        )
        
        get_engine = Engine(
            url=get_config.url,
            method=get_config.method,
            timeout=get_config.timeout,
            headers=get_config.headers,
            body=get_config.body
        )
        
        get_metrics = MetricsCollector()
        get_metrics.start()
        
        get_results = await get_engine.run(get_config.requests, get_config.concurrency)
        
        for result in get_results:
            get_metrics.add_result(convert_engine_result_to_metrics(result))
        
        get_metrics.end()
        
        stats = get_metrics.get_statistics()
        
        # Verify GET requests succeeded
        assert stats['total_requests'] == 10
        assert stats['successful_requests'] == 10
        assert stats['failed_requests'] == 0
        assert 200 in stats['status_codes']

    @pytest.mark.asyncio
    async def test_metrics_collection_accuracy(self, test_server):
        """Test that metrics collection is accurate."""
        config = Config(
            url=f"{test_server}/health",
            method="GET",
            requests=15,
            concurrency=3,
            timeout=10
        )
        
        engine = Engine(
            url=config.url,
            method=config.method,
            timeout=config.timeout
        )
        
        metrics = MetricsCollector()
        metrics.start()
        
        results = await engine.run(config.requests, config.concurrency)
        
        for result in results:
            metrics.add_result(convert_engine_result_to_metrics(result))
        
        metrics.end()
        
        stats = metrics.get_statistics()
        
        # Verify metrics are calculated correctly
        assert stats['total_requests'] == 15
        assert stats['response_times']['min'] > 0
        assert stats['response_times']['max'] >= stats['response_times']['min']
        assert stats['response_times']['mean'] >= stats['response_times']['min']
        assert stats['response_times']['mean'] <= stats['response_times']['max']
        assert stats['response_times']['median'] >= stats['response_times']['min']
        assert stats['response_times']['median'] <= stats['response_times']['max']
        assert stats['response_times']['p95'] >= stats['response_times']['median']
        assert stats['response_times']['p99'] >= stats['response_times']['p95']
        assert stats['duration'] > 0
        assert stats['throughput'] > 0
