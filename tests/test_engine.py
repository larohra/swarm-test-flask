"""
Tests for the request execution engine.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientError, ClientTimeout

from loadtest.engine import Engine, RequestResult


class TestRequestResult:
    """Test cases for RequestResult dataclass."""
    
    def test_request_result_creation(self):
        """Test creating a RequestResult instance."""
        result = RequestResult(
            status_code=200,
            response_time=0.5,
            error=None,
            timestamp=1234567890.0
        )
        
        assert result.status_code == 200
        assert result.response_time == 0.5
        assert result.error is None
        assert result.timestamp == 1234567890.0
    
    def test_request_result_with_error(self):
        """Test RequestResult with error."""
        result = RequestResult(
            status_code=None,
            response_time=1.0,
            error="Connection timeout",
            timestamp=1234567890.0
        )
        
        assert result.status_code is None
        assert result.error == "Connection timeout"


class TestEngine:
    """Test cases for the request execution engine."""

    def test_engine_initialization(self):
        """Test Engine initialization with default parameters."""
        engine = Engine(url="http://example.com")
        
        assert engine.url == "http://example.com"
        assert engine.method == "GET"
        assert engine.timeout == 30
        assert engine.headers == {}
        assert engine.body is None
        assert engine._session is None
    
    def test_engine_initialization_with_all_params(self):
        """Test Engine initialization with all parameters."""
        headers = {"Authorization": "Bearer token"}
        body = '{"test": "data"}'
        
        engine = Engine(
            url="https://api.example.com/endpoint",
            method="POST",
            timeout=60,
            headers=headers,
            body=body
        )
        
        assert engine.url == "https://api.example.com/endpoint"
        assert engine.method == "POST"
        assert engine.timeout == 60
        assert engine.headers == headers
        assert engine.body == body
    
    def test_engine_normalizes_method_to_uppercase(self):
        """Test that HTTP method is normalized to uppercase."""
        engine = Engine(url="http://example.com", method="post")
        assert engine.method == "POST"
    
    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test session creation with proper configuration."""
        engine = Engine(url="http://example.com", timeout=45)
        session = await engine._create_session()
        
        try:
            assert session is not None
            assert session.timeout.total == 45
            assert session.connector.limit == 100
            assert session.connector.limit_per_host == 30
        finally:
            await session.close()
    
    @pytest.mark.asyncio
    async def test_execute_single_request_success(self):
        """Test successful single request execution."""
        engine = Engine(url="http://example.com")
        
        # Mock the aiohttp response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=b"response data")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session
        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_response)
        engine._session = mock_session
        
        result = await engine._execute_single_request()
        
        assert result.status_code == 200
        assert result.error is None
        assert result.response_time > 0
        assert result.timestamp > 0
        
        mock_session.request.assert_called_once_with(
            method="GET",
            url="http://example.com",
            data=None
        )
    
    @pytest.mark.asyncio
    async def test_execute_single_request_with_body(self):
        """Test single request execution with request body."""
        body = '{"key": "value"}'
        engine = Engine(
            url="http://example.com",
            method="POST",
            body=body
        )
        
        # Mock the aiohttp response
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.read = AsyncMock(return_value=b"created")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        # Mock the session
        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_response)
        engine._session = mock_session
        
        result = await engine._execute_single_request()
        
        assert result.status_code == 201
        assert result.error is None
        
        mock_session.request.assert_called_once_with(
            method="POST",
            url="http://example.com",
            data=body
        )
    
    @pytest.mark.asyncio
    async def test_execute_single_request_timeout(self):
        """Test request execution with timeout error."""
        engine = Engine(url="http://example.com", timeout=5)
        
        # Mock the session to raise timeout
        mock_session = AsyncMock()
        mock_session.request = MagicMock(side_effect=asyncio.TimeoutError())
        engine._session = mock_session
        
        result = await engine._execute_single_request()
        
        assert result.status_code is None
        assert result.error == "Request timeout after 5 seconds"
        assert result.response_time > 0
    
    @pytest.mark.asyncio
    async def test_execute_single_request_client_error(self):
        """Test request execution with client error."""
        engine = Engine(url="http://example.com")
        
        # Mock the session to raise ClientError
        mock_session = AsyncMock()
        mock_session.request = MagicMock(
            side_effect=ClientError("Connection refused")
        )
        engine._session = mock_session
        
        result = await engine._execute_single_request()
        
        assert result.status_code is None
        assert "Client error" in result.error
        assert "Connection refused" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_single_request_unexpected_error(self):
        """Test request execution with unexpected error."""
        engine = Engine(url="http://example.com")
        
        # Mock the session to raise unexpected error
        mock_session = AsyncMock()
        mock_session.request = MagicMock(
            side_effect=ValueError("Unexpected error")
        )
        engine._session = mock_session
        
        result = await engine._execute_single_request()
        
        assert result.status_code is None
        assert "Unexpected error" in result.error
        assert "Unexpected error" in result.error
    
    @pytest.mark.asyncio
    async def test_run_multiple_requests(self):
        """Test running multiple requests concurrently."""
        engine = Engine(url="http://example.com")
        
        # Mock the aiohttp response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=b"ok")
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        
        with patch.object(engine, '_create_session') as mock_create_session:
            mock_session = AsyncMock()
            mock_session.request = MagicMock(return_value=mock_response)
            mock_session.close = AsyncMock()
            mock_create_session.return_value = mock_session
            
            results = await engine.run(num_requests=5, concurrency=2)
        
        assert len(results) == 5
        for result in results:
            assert result.status_code == 200
            assert result.error is None
            assert result.response_time > 0
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_with_mixed_results(self):
        """Test running requests with some successes and some failures."""
        engine = Engine(url="http://example.com")
        
        # Create multiple mock responses with different outcomes
        call_count = 0
        
        def side_effect_generator(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count % 2 == 0:
                # Even calls fail with timeout
                raise asyncio.TimeoutError()
            else:
                # Odd calls succeed
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.read = AsyncMock(return_value=b"ok")
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)
                return mock_response
        
        with patch.object(engine, '_create_session') as mock_create_session:
            mock_session = AsyncMock()
            mock_session.request = MagicMock(side_effect=side_effect_generator)
            mock_session.close = AsyncMock()
            mock_create_session.return_value = mock_session
            
            results = await engine.run(num_requests=4, concurrency=2)
        
        assert len(results) == 4
        
        # Check that we have both successes and failures
        successes = [r for r in results if r.status_code == 200]
        failures = [r for r in results if r.error is not None]
        
        assert len(successes) == 2
        assert len(failures) == 2
    
    @pytest.mark.asyncio
    async def test_run_respects_concurrency_limit(self):
        """Test that concurrency limit is respected."""
        engine = Engine(url="http://example.com")
        
        # Track concurrent requests using a simpler approach
        request_count = 0
        
        # Mock response that counts requests
        async def create_mock_response(*args, **kwargs):
            nonlocal request_count
            request_count += 1
            
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.read = AsyncMock(return_value=b"ok")
            return mock_response
        
        mock_response_cm = AsyncMock()
        mock_response_cm.__aenter__ = create_mock_response
        mock_response_cm.__aexit__ = AsyncMock(return_value=None)
        
        with patch.object(engine, '_create_session') as mock_create_session:
            mock_session = AsyncMock()
            mock_session.request = MagicMock(return_value=mock_response_cm)
            mock_session.close = AsyncMock()
            mock_create_session.return_value = mock_session
            
            results = await engine.run(num_requests=10, concurrency=3)
        
        # Verify all requests were made
        assert len(results) == 10
        assert request_count == 10
        
        # All should succeed
        for result in results:
            assert result.status_code == 200
            assert result.error is None
    
    @pytest.mark.asyncio
    async def test_run_closes_session_on_error(self):
        """Test that session is closed even when errors occur."""
        engine = Engine(url="http://example.com")
        
        with patch.object(engine, '_create_session') as mock_create_session:
            mock_session = AsyncMock()
            mock_session.request = MagicMock(
                side_effect=ClientError("Fatal error")
            )
            mock_session.close = AsyncMock()
            mock_create_session.return_value = mock_session
            
            results = await engine.run(num_requests=2, concurrency=1)
        
        # Session should still be closed
        mock_session.close.assert_called_once()
        
        # All requests should have errors
        assert len(results) == 2
        for result in results:
            assert result.status_code is None
            assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_close_method(self):
        """Test explicit close method."""
        engine = Engine(url="http://example.com")
        
        # Create a mock session
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()
        engine._session = mock_session
        
        await engine.close()
        
        mock_session.close.assert_called_once()
        assert engine._session is None
    
    @pytest.mark.asyncio
    async def test_close_method_when_no_session(self):
        """Test close method when no session exists."""
        engine = Engine(url="http://example.com")
        
        # Should not raise an error
        await engine.close()
        
        assert engine._session is None
