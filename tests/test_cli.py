"""
Tests for the CLI interface with YAML config support.
"""
import pytest
from click.testing import CliRunner

from loadtest.cli import cli
from loadtest.config import Config


class TestCLI:
    """Test cases for CLI interface."""
    
    def test_cli_with_url_only(self):
        """Test CLI with only URL argument."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--url', 'http://example.com'])
        
        # Should not error
        assert result.exit_code == 0
    
    def test_cli_with_all_arguments(self):
        """Test CLI with all arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--method', 'POST',
            '--requests', '50',
            '--concurrency', '5',
            '--timeout', '60',
            '--header', 'Content-Type: application/json',
            '--data', '{"test": "data"}'
        ])
        
        assert result.exit_code == 0
    
    def test_cli_missing_url_and_config(self):
        """Test CLI fails when both URL and config are missing."""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        
        assert result.exit_code != 0
        assert "Either --config file or --url must be provided" in result.output
    
    def test_cli_invalid_url(self):
        """Test CLI with invalid URL."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--url', 'invalid-url'])
        
        assert result.exit_code != 0
        assert "URL must include a scheme" in result.output
    
    def test_cli_invalid_header_format(self):
        """Test CLI with invalid header format."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--header', 'InvalidHeaderFormat'
        ])
        
        assert result.exit_code != 0
        assert "Invalid header format" in result.output


class TestCLIWithYAMLConfig:
    """Test cases for CLI with YAML config file."""
    
    def test_cli_with_config_file(self, tmp_path):
        """Test CLI with YAML config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
method: "GET"
requests: 100
concurrency: 10
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--config', str(config_file)])
        
        assert result.exit_code == 0
    
    def test_cli_config_with_url_override(self, tmp_path):
        """Test CLI config file with URL override."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
method: "GET"
requests: 100
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--config', str(config_file),
            '--url', 'http://override.com'
        ])
        
        assert result.exit_code == 0
    
    def test_cli_config_with_method_override(self, tmp_path):
        """Test CLI config file with method override."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
method: "GET"
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--config', str(config_file),
            '--method', 'POST'
        ])
        
        assert result.exit_code == 0
    
    def test_cli_config_with_requests_override(self, tmp_path):
        """Test CLI config file with requests override."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
requests: 100
concurrency: 10
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--config', str(config_file),
            '--requests', '200',
            '--concurrency', '20'
        ])
        
        assert result.exit_code == 0
    
    def test_cli_config_with_header_override(self, tmp_path):
        """Test CLI config file with header override."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
headers:
  Content-Type: "application/json"
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--config', str(config_file),
            '--header', 'X-Custom: value'
        ])
        
        assert result.exit_code == 0
    
    def test_cli_config_with_multiple_overrides(self, tmp_path):
        """Test CLI config file with multiple overrides."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
method: "GET"
requests: 100
concurrency: 10
timeout: 30
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--config', str(config_file),
            '--method', 'POST',
            '--requests', '200',
            '--timeout', '60'
        ])
        
        assert result.exit_code == 0
    
    def test_cli_config_file_not_found(self):
        """Test CLI with non-existent config file."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--config', '/nonexistent/config.yaml'])
        
        # Click should fail with exists=True check before reaching our code
        assert result.exit_code != 0
    
    def test_cli_config_invalid_yaml(self, tmp_path):
        """Test CLI with invalid YAML config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: http://example.com
invalid: yaml: syntax
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--config', str(config_file)])
        
        assert result.exit_code != 0
        assert "Failed to parse YAML" in result.output
    
    def test_cli_config_missing_url(self, tmp_path):
        """Test CLI with config file missing URL."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
method: "GET"
requests: 100
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--config', str(config_file)])
        
        assert result.exit_code != 0
        assert "must include 'url'" in result.output
    
    def test_cli_config_empty_file(self, tmp_path):
        """Test CLI with empty config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--config', str(config_file)])
        
        assert result.exit_code != 0
        assert "Configuration file is empty" in result.output
    
    def test_cli_config_with_validation_error_override(self, tmp_path):
        """Test CLI config with override that causes validation error."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
url: "http://example.com"
requests: 10
concurrency: 5
""")
        
        runner = CliRunner()
        # Try to override concurrency to exceed requests
        result = runner.invoke(cli, [
            '--config', str(config_file),
            '--concurrency', '20'
        ])
        
        assert result.exit_code != 0
        assert "cannot exceed total requests" in result.output


class TestCLIHeadersParsing:
    """Test cases for header parsing in CLI."""
    
    def test_single_header(self):
        """Test parsing a single header."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--header', 'Content-Type: application/json'
        ])
        
        assert result.exit_code == 0
    
    def test_multiple_headers(self):
        """Test parsing multiple headers."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--header', 'Content-Type: application/json',
            '--header', 'Authorization: Bearer token'
        ])
        
        assert result.exit_code == 0
    
    def test_header_with_spaces(self):
        """Test parsing header with spaces in value."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--header', 'User-Agent: My Custom Agent 1.0'
        ])
        
        assert result.exit_code == 0
    
    def test_header_missing_colon(self):
        """Test invalid header without colon."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--header', 'InvalidHeader'
        ])
        
        assert result.exit_code != 0
        assert "Invalid header format" in result.output
    
    def test_header_empty_name(self):
        """Test invalid header with empty name."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--header', ': value'
        ])
        
        assert result.exit_code != 0
        assert "Header name cannot be empty" in result.output
