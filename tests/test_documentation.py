"""
Tests for documentation examples and sample configurations.

Ensures that examples in README.md and sample configurations are valid and work correctly.
"""
import os
import pytest
import yaml
from pathlib import Path

from loadtest.config import Config, ConfigError


class TestSampleConfiguration:
    """Test that sample configuration files are valid."""
    
    def test_sample_config_exists(self):
        """Test that sample_config.yaml exists."""
        sample_config_path = Path(__file__).parent.parent / "examples" / "sample_config.yaml"
        assert sample_config_path.exists(), "examples/sample_config.yaml should exist"
    
    def test_sample_config_is_valid_yaml(self):
        """Test that sample_config.yaml is valid YAML."""
        sample_config_path = Path(__file__).parent.parent / "examples" / "sample_config.yaml"
        
        with open(sample_config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Should be a dictionary
        assert isinstance(config_data, dict), "Sample config should be a dictionary"
        
        # Should have required fields
        assert 'url' in config_data, "Sample config should have 'url' field"
    
    def test_sample_config_default_values_create_valid_config(self):
        """Test that the default active configuration in sample_config.yaml is valid."""
        sample_config_path = Path(__file__).parent.parent / "examples" / "sample_config.yaml"
        
        with open(sample_config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Create Config object from the sample
        config = Config.from_dict(config_data)
        
        # Verify it has valid values
        assert config.url == "http://localhost:5000/health"
        assert config.method == "GET"
        assert config.requests == 100
        assert config.concurrency == 10
        assert config.timeout == 30
        assert config.headers == {}
        assert config.body is None


class TestDocumentationExamples:
    """Test examples from README.md to ensure they are valid."""
    
    def test_basic_health_check_config(self):
        """Test Example 1: Basic health check configuration."""
        config = Config(
            url="http://localhost:5000/health",
            requests=200,
            concurrency=20
        )
        
        assert config.url == "http://localhost:5000/health"
        assert config.method == "GET"  # Default
        assert config.requests == 200
        assert config.concurrency == 20
    
    def test_api_with_authentication_config(self):
        """Test Example 2: API endpoint with authentication."""
        config = Config(
            url="https://api.example.com/v1/users",
            method="GET",
            headers={
                "Authorization": "Bearer eyJhbGc...",
                "Accept": "application/json"
            },
            requests=100,
            concurrency=10
        )
        
        assert config.url == "https://api.example.com/v1/users"
        assert config.method == "GET"
        assert "Authorization" in config.headers
        assert "Accept" in config.headers
    
    def test_post_with_json_body_config(self):
        """Test Example 3: POST request with JSON body."""
        config = Config(
            url="http://localhost:5000/api/items",
            method="POST",
            headers={"Content-Type": "application/json"},
            body='{"name": "Load Test Item", "description": "Created during load test"}',
            requests=50,
            concurrency=5
        )
        
        assert config.method == "POST"
        assert config.headers["Content-Type"] == "application/json"
        assert config.body is not None
        assert "name" in config.body
    
    def test_high_concurrency_stress_test_config(self):
        """Test Example 4: High concurrency stress test."""
        config = Config(
            url="http://localhost:5000/health",
            requests=1000,
            concurrency=100,
            timeout=60
        )
        
        assert config.requests == 1000
        assert config.concurrency == 100
        assert config.timeout == 60
    
    def test_put_request_config(self):
        """Test Example 6: PUT request to update resources."""
        config = Config(
            url="http://localhost:5000/api/items/1",
            method="PUT",
            headers={"Content-Type": "application/json"},
            body='{"name": "Updated Name", "description": "Updated Description"}',
            requests=30,
            concurrency=3
        )
        
        assert config.method == "PUT"
        assert config.requests == 30
        assert config.concurrency == 3
    
    def test_delete_request_config(self):
        """Test Example 7: DELETE request."""
        config = Config(
            url="http://localhost:5000/api/items/1",
            method="DELETE",
            requests=10,
            concurrency=2
        )
        
        assert config.method == "DELETE"
        assert config.requests == 10
        assert config.concurrency == 2


class TestConfigurationFileFormat:
    """Test various configuration file formats mentioned in documentation."""
    
    def test_config_with_all_fields(self):
        """Test a complete configuration with all fields."""
        config_dict = {
            'url': 'http://localhost:5000/api/items',
            'method': 'POST',
            'requests': 200,
            'concurrency': 20,
            'timeout': 30,
            'headers': {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer your-token-here'
            },
            'body': '{"name": "test", "description": "test item"}'
        }
        
        config = Config.from_dict(config_dict)
        
        assert config.url == config_dict['url']
        assert config.method == config_dict['method']
        assert config.requests == config_dict['requests']
        assert config.concurrency == config_dict['concurrency']
        assert config.timeout == config_dict['timeout']
        assert config.headers == config_dict['headers']
        assert config.body == config_dict['body']
    
    def test_minimal_config(self):
        """Test minimal configuration with only required field."""
        config_dict = {
            'url': 'http://localhost:5000/health'
        }
        
        config = Config.from_dict(config_dict)
        
        # Should use defaults for other fields
        assert config.url == 'http://localhost:5000/health'
        assert config.method == 'GET'
        assert config.requests == 100
        assert config.concurrency == 10
        assert config.timeout == 30
        assert config.headers == {}
        assert config.body is None


class TestReadmeExamples:
    """Validate that code snippets from README are correct."""
    
    def test_url_must_include_scheme(self):
        """Test that URLs without scheme are rejected as shown in troubleshooting."""
        # This should work
        config1 = Config(url="http://localhost:5000/health")
        assert config1.url == "http://localhost:5000/health"
        
        # This should fail (URL without scheme gets parsed as scheme:path by urlparse)
        with pytest.raises(ConfigError, match="URL scheme must be http or https"):
            Config(url="localhost:5000/health")
    
    def test_concurrency_cannot_exceed_requests(self):
        """Test that concurrency > requests is rejected as shown in troubleshooting."""
        # This should work
        config1 = Config(
            url="http://localhost:5000/health",
            requests=100,
            concurrency=10
        )
        assert config1.concurrency == 10
        
        # This should fail
        with pytest.raises(ConfigError, match="cannot exceed total requests"):
            Config(
                url="http://localhost:5000/health",
                requests=10,
                concurrency=100
            )
    
    def test_supported_http_methods(self):
        """Test all HTTP methods listed in documentation are supported."""
        url = "http://localhost:5000/api/items"
        supported_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        for method in supported_methods:
            config = Config(url=url, method=method)
            assert config.method == method
    
    def test_http_and_https_schemes_supported(self):
        """Test that both http and https schemes are supported."""
        # HTTP should work
        config1 = Config(url="http://example.com")
        assert config1.url == "http://example.com"
        
        # HTTPS should work
        config2 = Config(url="https://example.com")
        assert config2.url == "https://example.com"
        
        # Other schemes should fail
        with pytest.raises(ConfigError, match="URL scheme must be http or https"):
            Config(url="ftp://example.com")


class TestCLIOptionsDocumentation:
    """Test that CLI options match the documentation."""
    
    def test_default_values_match_documentation(self):
        """Test that default values in Config match what's documented in README."""
        # Create a config with only URL (all other fields should use defaults)
        config = Config(url="http://localhost:5000/health")
        
        # Verify defaults match README CLI Options table
        assert config.method == "GET", "Default method should be GET"
        assert config.requests == 100, "Default requests should be 100"
        assert config.concurrency == 10, "Default concurrency should be 10"
        assert config.timeout == 30, "Default timeout should be 30"
        assert config.headers == {}, "Default headers should be empty dict"
        assert config.body is None, "Default body should be None"


class TestExampleJSONOutput:
    """Test that the example JSON output structure in README is accurate."""
    
    def test_json_output_structure(self):
        """Test that statistics structure matches example in README."""
        from loadtest.metrics import MetricsCollector, RequestResult
        
        # Create a metrics collector and add some results
        metrics = MetricsCollector()
        metrics.start()
        
        # Add some sample results
        for i in range(10):
            result = RequestResult(
                response_time=0.1 + i * 0.01,
                status_code=200 if i < 9 else 500
            )
            metrics.add_result(result)
        
        metrics.end()
        
        # Get statistics
        stats = metrics.get_statistics()
        
        # Verify structure matches example in README
        assert 'total_requests' in stats
        assert 'successful_requests' in stats
        assert 'failed_requests' in stats
        assert 'error_rate' in stats
        assert 'response_times' in stats
        assert 'throughput' in stats
        assert 'duration' in stats
        assert 'status_codes' in stats
        
        # Verify response_times structure
        response_times = stats['response_times']
        assert 'min' in response_times
        assert 'max' in response_times
        assert 'mean' in response_times
        assert 'median' in response_times
        assert 'p95' in response_times
        assert 'p99' in response_times
        
        # Verify types
        assert isinstance(stats['total_requests'], int)
        assert isinstance(stats['successful_requests'], int)
        assert isinstance(stats['failed_requests'], int)
        assert isinstance(stats['error_rate'], float)
        assert isinstance(stats['throughput'], float)
        assert isinstance(stats['duration'], float)
        assert isinstance(stats['status_codes'], dict)
