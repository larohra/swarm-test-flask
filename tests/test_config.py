"""
Tests for the configuration manager.
"""
import pytest
from loadtest.config import Config, ConfigError


class TestConfig:
    """Test cases for configuration management."""

    def test_basic_config_with_defaults(self):
        """Test creating config with minimal parameters and defaults."""
        config = Config(url="http://example.com")
        
        assert config.url == "http://example.com"
        assert config.method == "GET"
        assert config.requests == 100
        assert config.concurrency == 10
        assert config.timeout == 30
        assert config.headers == {}
        assert config.body is None
    
    def test_config_with_all_parameters(self):
        """Test creating config with all parameters specified."""
        headers = {"Content-Type": "application/json"}
        body = '{"test": "data"}'
        
        config = Config(
            url="https://api.example.com/endpoint",
            method="POST",
            requests=50,
            concurrency=5,
            timeout=60,
            headers=headers,
            body=body
        )
        
        assert config.url == "https://api.example.com/endpoint"
        assert config.method == "POST"
        assert config.requests == 50
        assert config.concurrency == 5
        assert config.timeout == 60
        assert config.headers == headers
        assert config.body == body
    
    def test_method_case_insensitive(self):
        """Test that HTTP method is normalized to uppercase."""
        config = Config(url="http://example.com", method="post")
        assert config.method == "POST"
        
        config = Config(url="http://example.com", method="GeT")
        assert config.method == "GET"
    
    def test_url_validation_missing(self):
        """Test that missing URL raises ConfigError."""
        with pytest.raises(ConfigError, match="URL is required"):
            Config(url="")
    
    def test_url_validation_no_scheme(self):
        """Test that URL without scheme raises ConfigError."""
        with pytest.raises(ConfigError, match="must include a scheme"):
            Config(url="example.com")
    
    def test_url_validation_invalid_scheme(self):
        """Test that URL with invalid scheme raises ConfigError."""
        with pytest.raises(ConfigError, match="scheme must be http or https"):
            Config(url="ftp://example.com")
    
    def test_url_validation_no_hostname(self):
        """Test that URL without hostname raises ConfigError."""
        with pytest.raises(ConfigError, match="must include a hostname"):
            Config(url="http://")
    
    def test_url_validation_not_string(self):
        """Test that non-string URL raises ConfigError."""
        with pytest.raises(ConfigError, match="URL must be a string"):
            Config(url=12345)
    
    def test_valid_http_methods(self):
        """Test that all valid HTTP methods are accepted."""
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        for method in valid_methods:
            config = Config(url="http://example.com", method=method)
            assert config.method == method.upper()
    
    def test_invalid_http_method(self):
        """Test that invalid HTTP method raises ConfigError."""
        with pytest.raises(ConfigError, match="Invalid HTTP method"):
            Config(url="http://example.com", method="INVALID")
    
    def test_method_not_string(self):
        """Test that non-string method raises ConfigError."""
        with pytest.raises(ConfigError, match="Method must be a string"):
            Config(url="http://example.com", method=123)
    
    def test_requests_validation_positive(self):
        """Test that requests must be positive."""
        with pytest.raises(ConfigError, match="must be greater than 0"):
            Config(url="http://example.com", requests=0)
        
        with pytest.raises(ConfigError, match="must be greater than 0"):
            Config(url="http://example.com", requests=-10)
    
    def test_requests_validation_integer(self):
        """Test that requests must be an integer."""
        with pytest.raises(ConfigError, match="must be an integer"):
            Config(url="http://example.com", requests="100")
        
        with pytest.raises(ConfigError, match="must be an integer"):
            Config(url="http://example.com", requests=10.5)
    
    def test_concurrency_validation_positive(self):
        """Test that concurrency must be positive."""
        with pytest.raises(ConfigError, match="must be greater than 0"):
            Config(url="http://example.com", concurrency=0)
        
        with pytest.raises(ConfigError, match="must be greater than 0"):
            Config(url="http://example.com", concurrency=-5)
    
    def test_concurrency_validation_integer(self):
        """Test that concurrency must be an integer."""
        with pytest.raises(ConfigError, match="must be an integer"):
            Config(url="http://example.com", concurrency="10")
        
        with pytest.raises(ConfigError, match="must be an integer"):
            Config(url="http://example.com", concurrency=5.5)
    
    def test_concurrency_exceeds_requests(self):
        """Test that concurrency cannot exceed total requests."""
        with pytest.raises(ConfigError, match="cannot exceed total requests"):
            Config(url="http://example.com", requests=10, concurrency=20)
    
    def test_concurrency_equal_to_requests(self):
        """Test that concurrency can equal total requests."""
        config = Config(url="http://example.com", requests=10, concurrency=10)
        assert config.concurrency == 10
        assert config.requests == 10
    
    def test_timeout_validation_positive(self):
        """Test that timeout must be positive."""
        with pytest.raises(ConfigError, match="must be greater than 0"):
            Config(url="http://example.com", timeout=0)
        
        with pytest.raises(ConfigError, match="must be greater than 0"):
            Config(url="http://example.com", timeout=-30)
    
    def test_timeout_validation_integer(self):
        """Test that timeout must be an integer."""
        with pytest.raises(ConfigError, match="must be an integer"):
            Config(url="http://example.com", timeout="30")
        
        with pytest.raises(ConfigError, match="must be an integer"):
            Config(url="http://example.com", timeout=30.5)
    
    def test_headers_validation_not_dict(self):
        """Test that headers must be a dictionary."""
        with pytest.raises(ConfigError, match="must be a dictionary"):
            Config(url="http://example.com", headers="invalid")
        
        with pytest.raises(ConfigError, match="must be a dictionary"):
            Config(url="http://example.com", headers=["header1", "header2"])
    
    def test_headers_validation_non_string_key(self):
        """Test that header names must be strings."""
        with pytest.raises(ConfigError, match="Header name must be a string"):
            Config(url="http://example.com", headers={123: "value"})
    
    def test_headers_validation_non_string_value(self):
        """Test that header values must be strings."""
        with pytest.raises(ConfigError, match="Header value must be a string"):
            Config(url="http://example.com", headers={"Content-Type": 123})
    
    def test_headers_empty_dict(self):
        """Test that empty headers dictionary is valid."""
        config = Config(url="http://example.com", headers={})
        assert config.headers == {}
    
    def test_body_validation_string(self):
        """Test that body accepts strings."""
        config = Config(url="http://example.com", body='{"key": "value"}')
        assert config.body == '{"key": "value"}'
    
    def test_body_validation_none(self):
        """Test that body accepts None."""
        config = Config(url="http://example.com", body=None)
        assert config.body is None
    
    def test_body_validation_not_string(self):
        """Test that non-string body raises ConfigError."""
        with pytest.raises(ConfigError, match="Body must be a string or None"):
            Config(url="http://example.com", body={"key": "value"})
        
        with pytest.raises(ConfigError, match="Body must be a string or None"):
            Config(url="http://example.com", body=123)
    
    def test_from_dict_basic(self):
        """Test creating config from dictionary with minimal data."""
        config_dict = {"url": "http://example.com"}
        config = Config.from_dict(config_dict)
        
        assert config.url == "http://example.com"
        assert config.method == "GET"
        assert config.requests == 100
    
    def test_from_dict_complete(self):
        """Test creating config from dictionary with all parameters."""
        config_dict = {
            "url": "https://api.example.com",
            "method": "POST",
            "requests": 50,
            "concurrency": 5,
            "timeout": 60,
            "headers": {"Authorization": "Bearer token"},
            "body": '{"data": "test"}'
        }
        config = Config.from_dict(config_dict)
        
        assert config.url == "https://api.example.com"
        assert config.method == "POST"
        assert config.requests == 50
        assert config.concurrency == 5
        assert config.timeout == 60
        assert config.headers == {"Authorization": "Bearer token"}
        assert config.body == '{"data": "test"}'
    
    def test_from_dict_not_dict(self):
        """Test that from_dict requires a dictionary."""
        with pytest.raises(ConfigError, match="must be a dictionary"):
            Config.from_dict("not a dict")
        
        with pytest.raises(ConfigError, match="must be a dictionary"):
            Config.from_dict([])
    
    def test_from_dict_missing_url(self):
        """Test that from_dict requires URL."""
        with pytest.raises(ConfigError, match="must include 'url'"):
            Config.from_dict({"method": "GET"})
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            url="http://example.com",
            method="POST",
            requests=50,
            concurrency=5,
            timeout=60,
            headers={"Content-Type": "application/json"},
            body='{"test": "data"}'
        )
        
        result = config.to_dict()
        
        assert result == {
            "url": "http://example.com",
            "method": "POST",
            "requests": 50,
            "concurrency": 5,
            "timeout": 60,
            "headers": {"Content-Type": "application/json"},
            "body": '{"test": "data"}'
        }
    
    def test_to_dict_roundtrip(self):
        """Test that to_dict and from_dict are reversible."""
        original = Config(
            url="https://api.example.com/test",
            method="PUT",
            requests=25,
            concurrency=3,
            timeout=45,
            headers={"X-Custom": "header"},
            body="test body"
        )
        
        config_dict = original.to_dict()
        recreated = Config.from_dict(config_dict)
        
        assert recreated.url == original.url
        assert recreated.method == original.method
        assert recreated.requests == original.requests
        assert recreated.concurrency == original.concurrency
        assert recreated.timeout == original.timeout
        assert recreated.headers == original.headers
        assert recreated.body == original.body
    
    def test_repr(self):
        """Test string representation of Config."""
        config = Config(
            url="http://example.com",
            method="GET",
            requests=100
        )
        
        repr_str = repr(config)
        assert "Config(" in repr_str
        assert "url='http://example.com'" in repr_str
        assert "method='GET'" in repr_str
        assert "requests=100" in repr_str


class TestYAMLConfig:
    """Test cases for YAML configuration file loading."""
    
    def test_from_yaml_file_basic(self, tmp_path):
        """Test loading basic YAML config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
""")
        
        config = Config.from_yaml_file(str(config_file))
        assert config.url == "http://example.com"
        assert config.method == "GET"
        assert config.requests == 100
    
    def test_from_yaml_file_complete(self, tmp_path):
        """Test loading complete YAML config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "https://api.example.com/test"
method: "POST"
requests: 50
concurrency: 5
timeout: 60
headers:
  Content-Type: "application/json"
  Authorization: "Bearer token"
body: '{"test": "data"}'
""")
        
        config = Config.from_yaml_file(str(config_file))
        assert config.url == "https://api.example.com/test"
        assert config.method == "POST"
        assert config.requests == 50
        assert config.concurrency == 5
        assert config.timeout == 60
        assert config.headers == {
            "Content-Type": "application/json",
            "Authorization": "Bearer token"
        }
        assert config.body == '{"test": "data"}'
    
    def test_from_yaml_file_not_found(self):
        """Test loading from non-existent file raises error."""
        with pytest.raises(ConfigError, match="Configuration file not found"):
            Config.from_yaml_file("/nonexistent/config.yaml")
    
    def test_from_yaml_file_is_directory(self, tmp_path):
        """Test loading from directory instead of file raises error."""
        with pytest.raises(ConfigError, match="not a file"):
            Config.from_yaml_file(str(tmp_path))
    
    def test_from_yaml_file_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML raises error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: http://example.com
invalid: yaml: syntax: here
  wrong: indentation
""")
        
        with pytest.raises(ConfigError, match="Failed to parse YAML"):
            Config.from_yaml_file(str(config_file))
    
    def test_from_yaml_file_empty(self, tmp_path):
        """Test loading empty YAML file raises error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")
        
        with pytest.raises(ConfigError, match="Configuration file is empty"):
            Config.from_yaml_file(str(config_file))
    
    def test_from_yaml_file_missing_url(self, tmp_path):
        """Test loading YAML without URL raises error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
method: "GET"
requests: 100
""")
        
        with pytest.raises(ConfigError, match="must include 'url'"):
            Config.from_yaml_file(str(config_file))
    
    def test_from_yaml_file_invalid_values(self, tmp_path):
        """Test loading YAML with invalid values raises error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
requests: -10
""")
        
        with pytest.raises(ConfigError, match="must be greater than 0"):
            Config.from_yaml_file(str(config_file))


class TestConfigMerge:
    """Test cases for merging config file with CLI arguments."""
    
    def test_merge_no_overrides(self):
        """Test merging with no CLI overrides keeps file config."""
        file_config = Config(
            url="http://example.com",
            method="POST",
            requests=50
        )
        
        merged = Config.merge(file_config)
        assert merged.url == "http://example.com"
        assert merged.method == "POST"
        assert merged.requests == 50
    
    def test_merge_url_override(self):
        """Test merging with URL override."""
        file_config = Config(url="http://example.com")
        
        merged = Config.merge(file_config, url="http://override.com")
        assert merged.url == "http://override.com"
        assert merged.method == "GET"  # From file defaults
    
    def test_merge_method_override(self):
        """Test merging with method override."""
        file_config = Config(
            url="http://example.com",
            method="GET"
        )
        
        merged = Config.merge(file_config, method="POST")
        assert merged.url == "http://example.com"
        assert merged.method == "POST"
    
    def test_merge_requests_and_concurrency_override(self):
        """Test merging with requests and concurrency overrides."""
        file_config = Config(
            url="http://example.com",
            requests=100,
            concurrency=10
        )
        
        merged = Config.merge(
            file_config,
            requests=200,
            concurrency=20
        )
        assert merged.requests == 200
        assert merged.concurrency == 20
    
    def test_merge_timeout_override(self):
        """Test merging with timeout override."""
        file_config = Config(
            url="http://example.com",
            timeout=30
        )
        
        merged = Config.merge(file_config, timeout=60)
        assert merged.timeout == 60
    
    def test_merge_headers_override(self):
        """Test merging headers - should merge, not replace."""
        file_config = Config(
            url="http://example.com",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer token"
            }
        )
        
        merged = Config.merge(
            file_config,
            headers={"X-Custom": "value"}
        )
        
        # Headers should be merged, not replaced
        assert merged.headers == {
            "Content-Type": "application/json",
            "Authorization": "Bearer token",
            "X-Custom": "value"
        }
    
    def test_merge_headers_override_existing(self):
        """Test that CLI headers override file headers with same key."""
        file_config = Config(
            url="http://example.com",
            headers={"Content-Type": "application/json"}
        )
        
        merged = Config.merge(
            file_config,
            headers={"Content-Type": "text/plain"}
        )
        
        assert merged.headers == {"Content-Type": "text/plain"}
    
    def test_merge_body_override(self):
        """Test merging with body override."""
        file_config = Config(
            url="http://example.com",
            body='{"old": "data"}'
        )
        
        merged = Config.merge(file_config, body='{"new": "data"}')
        assert merged.body == '{"new": "data"}'
    
    def test_merge_multiple_overrides(self):
        """Test merging with multiple CLI overrides."""
        file_config = Config(
            url="http://example.com",
            method="GET",
            requests=100,
            concurrency=10,
            timeout=30
        )
        
        merged = Config.merge(
            file_config,
            method="POST",
            requests=200,
            timeout=60,
            headers={"X-Test": "value"}
        )
        
        assert merged.url == "http://example.com"
        assert merged.method == "POST"
        assert merged.requests == 200
        assert merged.concurrency == 10  # Not overridden
        assert merged.timeout == 60
        assert merged.headers == {"X-Test": "value"}
    
    def test_merge_none_values_ignored(self):
        """Test that None CLI values don't override file config."""
        file_config = Config(
            url="http://example.com",
            method="POST",
            requests=50
        )
        
        merged = Config.merge(
            file_config,
            method=None,
            requests=None,
            timeout=None
        )
        
        # None values should not override file config
        assert merged.method == "POST"
        assert merged.requests == 50
        assert merged.timeout == 30  # File default
    
    def test_merge_validation_errors(self):
        """Test that merge still validates the final config."""
        file_config = Config(
            url="http://example.com",
            requests=10
        )
        
        # Trying to set concurrency higher than requests should fail
        with pytest.raises(ConfigError, match="cannot exceed total requests"):
            Config.merge(file_config, concurrency=20)
