"""
Request execution engine for the load testing tool.

Manages concurrent request execution using asyncio, handles connection pooling,
and tracks individual request metrics.
"""
import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import aiohttp


@dataclass
class RequestResult:
    """Result of a single HTTP request.
    
    Attributes:
        status_code: HTTP status code (or None if request failed)
        response_time: Time taken for the request in seconds
        error: Error message if request failed (None if successful)
        timestamp: Unix timestamp when request was made
    """
    status_code: Optional[int]
    response_time: float
    error: Optional[str]
    timestamp: float


class Engine:
    """Async HTTP request engine with connection pooling and error handling.
    
    Manages concurrent execution of HTTP requests using aiohttp and asyncio.
    Provides connection pooling, timeout handling, and detailed error capture.
    """
    
    def __init__(
        self,
        url: str,
        method: str = "GET",
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None
    ):
        """Initialize the request engine.
        
        Args:
            url: Target URL for requests
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            timeout: Request timeout in seconds
            headers: Optional HTTP headers dictionary
            body: Optional request body as string
        """
        self.url = url
        self.method = method.upper()
        self.timeout = timeout
        self.headers = headers or {}
        self.body = body
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create aiohttp client session with connection pooling.
        
        Returns:
            Configured ClientSession instance
        """
        # Configure timeout
        timeout_config = aiohttp.ClientTimeout(total=self.timeout)
        
        # Create connector with connection pooling
        connector = aiohttp.TCPConnector(
            limit=100,  # Maximum number of connections
            limit_per_host=30,  # Maximum connections per host
            ttl_dns_cache=300  # DNS cache TTL in seconds
        )
        
        return aiohttp.ClientSession(
            timeout=timeout_config,
            connector=connector,
            headers=self.headers
        )
    
    async def _execute_single_request(self) -> RequestResult:
        """Execute a single HTTP request and return the result.
        
        Returns:
            RequestResult containing status code, response time, and error info
        """
        start_time = time.time()
        timestamp = start_time
        status_code = None
        error = None
        
        try:
            # Ensure session exists
            if self._session is None:
                self._session = await self._create_session()
            
            # Execute request
            async with self._session.request(
                method=self.method,
                url=self.url,
                data=self.body
            ) as response:
                status_code = response.status
                # Read response to ensure request completes
                await response.read()
                
        except asyncio.TimeoutError:
            error = f"Request timeout after {self.timeout} seconds"
        except aiohttp.ClientError as e:
            error = f"Client error: {str(e)}"
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
        
        response_time = time.time() - start_time
        
        return RequestResult(
            status_code=status_code,
            response_time=response_time,
            error=error,
            timestamp=timestamp
        )
    
    async def run(self, num_requests: int, concurrency: int) -> List[RequestResult]:
        """Execute multiple concurrent HTTP requests.
        
        Args:
            num_requests: Total number of requests to execute
            concurrency: Number of concurrent requests to maintain
            
        Returns:
            List of RequestResult objects, one per request
        """
        results: List[RequestResult] = []
        
        try:
            # Create session
            self._session = await self._create_session()
            
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(concurrency)
            
            async def bounded_request() -> RequestResult:
                """Execute request with concurrency limit."""
                async with semaphore:
                    return await self._execute_single_request()
            
            # Create all request tasks
            tasks = [bounded_request() for _ in range(num_requests)]
            
            # Execute all tasks concurrently and collect results
            results = await asyncio.gather(*tasks)
            
        finally:
            # Always close the session
            if self._session is not None:
                await self._session.close()
                self._session = None
        
        return results
    
    async def close(self):
        """Close the HTTP session and cleanup resources."""
        if self._session is not None:
            await self._session.close()
            self._session = None
