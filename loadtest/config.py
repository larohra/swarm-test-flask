"""
Configuration manager for the load testing tool.

Parses CLI arguments and configuration files, validates test parameters,
and manages default values and test scenarios.
"""
import json
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


class Config:
    """Configuration manager for load testing parameters.
    
    Handles default values, validation, and parsing of test parameters including:
    - URL: Target endpoint URL
    - Method: HTTP method (GET, POST, PUT, DELETE, etc.)
    - Requests: Number of requests to send
    - Concurrency: Number of concurrent requests
    - Timeout: Request timeout in seconds
    - Headers: Custom HTTP headers
    - Body: Request body (for POST/PUT requests)
    """
    
    # Default values
    DEFAULT_METHOD = "GET"
    DEFAULT_REQUESTS = 100
    DEFAULT_CONCURRENCY = 10
    DEFAULT_TIMEOUT = 30
    
    def __init__(
        self,
        url: str,
        method: Optional[str] = None,
        requests: Optional[int] = None,
        concurrency: Optional[int] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None
    ):
        """Initialize configuration with validation.
        
        Args:
            url: Target URL for load testing
            method: HTTP method (default: GET)
            requests: Number of requests to send (default: 100)
            concurrency: Number of concurrent requests (default: 10)
            timeout: Request timeout in seconds (default: 30)
            headers: Custom HTTP headers dictionary
            body: Request body as string
            
        Raises:
            ConfigError: If any parameter is invalid
        """
        self.url = self._validate_url(url)
        self.method = self._validate_method(method if method is not None else self.DEFAULT_METHOD)
        self.requests = self._validate_requests(requests if requests is not None else self.DEFAULT_REQUESTS)
        self.concurrency = self._validate_concurrency(
            concurrency if concurrency is not None else self.DEFAULT_CONCURRENCY,
            self.requests
        )
        self.timeout = self._validate_timeout(timeout if timeout is not None else self.DEFAULT_TIMEOUT)
        self.headers = self._validate_headers(headers if headers is not None else {})
        self.body = self._validate_body(body)
    
    def _validate_url(self, url: str) -> str:
        """Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            Validated URL string
            
        Raises:
            ConfigError: If URL is invalid
        """
        if not url:
            raise ConfigError("URL is required")
        
        if not isinstance(url, str):
            raise ConfigError("URL must be a string")
        
        parsed = urlparse(url)
        if not parsed.scheme:
            raise ConfigError("URL must include a scheme (http:// or https://)")
        
        if parsed.scheme not in ("http", "https"):
            raise ConfigError("URL scheme must be http or https")
        
        if not parsed.netloc:
            raise ConfigError("URL must include a hostname")
        
        return url
    
    def _validate_method(self, method: str) -> str:
        """Validate HTTP method.
        
        Args:
            method: HTTP method string
            
        Returns:
            Validated method in uppercase
            
        Raises:
            ConfigError: If method is invalid
        """
        if not isinstance(method, str):
            raise ConfigError("Method must be a string")
        
        method = method.upper()
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        
        if method not in valid_methods:
            raise ConfigError(
                f"Invalid HTTP method '{method}'. "
                f"Must be one of: {', '.join(sorted(valid_methods))}"
            )
        
        return method
    
    def _validate_requests(self, requests: int) -> int:
        """Validate number of requests.
        
        Args:
            requests: Number of requests
            
        Returns:
            Validated requests count
            
        Raises:
            ConfigError: If requests count is invalid
        """
        if not isinstance(requests, int):
            raise ConfigError("Requests must be an integer")
        
        if requests <= 0:
            raise ConfigError("Requests must be greater than 0")
        
        return requests
    
    def _validate_concurrency(self, concurrency: int, requests: int) -> int:
        """Validate concurrency level.
        
        Args:
            concurrency: Concurrency level
            requests: Total number of requests
            
        Returns:
            Validated concurrency level
            
        Raises:
            ConfigError: If concurrency is invalid
        """
        if not isinstance(concurrency, int):
            raise ConfigError("Concurrency must be an integer")
        
        if concurrency <= 0:
            raise ConfigError("Concurrency must be greater than 0")
        
        if concurrency > requests:
            raise ConfigError(
                f"Concurrency ({concurrency}) cannot exceed total requests ({requests})"
            )
        
        return concurrency
    
    def _validate_timeout(self, timeout: int) -> int:
        """Validate timeout value.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Validated timeout
            
        Raises:
            ConfigError: If timeout is invalid
        """
        if not isinstance(timeout, int):
            raise ConfigError("Timeout must be an integer")
        
        if timeout <= 0:
            raise ConfigError("Timeout must be greater than 0")
        
        return timeout
    
    def _validate_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Validate headers dictionary.
        
        Args:
            headers: Headers dictionary
            
        Returns:
            Validated headers dictionary
            
        Raises:
            ConfigError: If headers are invalid
        """
        if not isinstance(headers, dict):
            raise ConfigError("Headers must be a dictionary")
        
        for key, value in headers.items():
            if not isinstance(key, str):
                raise ConfigError(f"Header name must be a string, got {type(key).__name__}")
            if not isinstance(value, str):
                raise ConfigError(f"Header value must be a string, got {type(value).__name__}")
        
        return headers
    
    def _validate_body(self, body: Optional[str]) -> Optional[str]:
        """Validate request body.
        
        Args:
            body: Request body string or None
            
        Returns:
            Validated body
            
        Raises:
            ConfigError: If body is invalid
        """
        if body is None:
            return None
        
        if not isinstance(body, str):
            raise ConfigError("Body must be a string or None")
        
        return body
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create Config instance from dictionary.
        
        Args:
            config_dict: Dictionary containing configuration parameters
            
        Returns:
            Config instance
            
        Raises:
            ConfigError: If configuration is invalid
        """
        if not isinstance(config_dict, dict):
            raise ConfigError("Configuration must be a dictionary")
        
        if "url" not in config_dict:
            raise ConfigError("Configuration must include 'url'")
        
        return cls(
            url=config_dict.get("url"),
            method=config_dict.get("method"),
            requests=config_dict.get("requests"),
            concurrency=config_dict.get("concurrency"),
            timeout=config_dict.get("timeout"),
            headers=config_dict.get("headers"),
            body=config_dict.get("body")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "url": self.url,
            "method": self.method,
            "requests": self.requests,
            "concurrency": self.concurrency,
            "timeout": self.timeout,
            "headers": self.headers,
            "body": self.body
        }
    
    def __repr__(self) -> str:
        """String representation of Config."""
        return (
            f"Config(url={self.url!r}, method={self.method!r}, "
            f"requests={self.requests}, concurrency={self.concurrency}, "
            f"timeout={self.timeout}, headers={self.headers!r}, body={self.body!r})"
        )
