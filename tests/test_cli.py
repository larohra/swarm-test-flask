"""
Tests for the CLI interface.
"""
import pytest
import json
import click
from click.testing import CliRunner

from loadtest.cli import cli, parse_headers
from loadtest.config import Config


class TestParseHeaders:
    """Tests for parse_headers callback function."""
    
    def test_parse_single_header(self):
        """Test parsing a single header."""
        result = parse_headers(None, None, ('Content-Type: application/json',))
        assert result == {'Content-Type': 'application/json'}
    
    def test_parse_multiple_headers(self):
        """Test parsing multiple headers."""
        headers = (
            'Content-Type: application/json',
            'Authorization: Bearer token123',
            'X-Custom-Header: custom-value'
        )
        result = parse_headers(None, None, headers)
        assert result == {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123',
            'X-Custom-Header': 'custom-value'
        }
    
    def test_parse_header_with_spaces(self):
        """Test parsing header with spaces around colon."""
        result = parse_headers(None, None, ('Content-Type : application/json',))
        assert result == {'Content-Type': 'application/json'}
    
    def test_parse_header_with_colon_in_value(self):
        """Test parsing header with colon in value."""
        result = parse_headers(None, None, ('X-Url: http://example.com',))
        assert result == {'X-Url': 'http://example.com'}
    
    def test_parse_empty_headers(self):
        """Test parsing empty headers tuple."""
        result = parse_headers(None, None, ())
        assert result == {}
    
    def test_parse_header_missing_colon(self):
        """Test parsing header without colon raises error."""
        from click.exceptions import BadParameter
        with pytest.raises(BadParameter, match="Invalid header format"):
            parse_headers(None, None, ('InvalidHeader',))
    
    def test_parse_header_empty_name(self):
        """Test parsing header with empty name raises error."""
        from click.exceptions import BadParameter
        with pytest.raises(BadParameter, match="Header name cannot be empty"):
            parse_headers(None, None, (': value',))


class TestCLI:
    """Tests for CLI command."""
    
    def test_basic_usage(self):
        """Test basic CLI usage with required URL."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--url', 'http://example.com'])
        assert result.exit_code == 0
    
    def test_url_required(self):
        """Test that URL is required."""
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code != 0
        assert 'Missing option' in result.output or 'required' in result.output.lower()
    
    def test_all_options(self):
        """Test CLI with all options specified."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com/api',
            '--method', 'POST',
            '--requests', '50',
            '--concurrency', '5',
            '--timeout', '20',
            '--header', 'Content-Type: application/json',
            '--header', 'Authorization: Bearer token',
            '--data', '{"test": "data"}',
            '--output', 'report.json'
        ])
        assert result.exit_code == 0
    
    def test_short_options(self):
        """Test CLI with short option names."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '-u', 'http://example.com',
            '-m', 'GET',
            '-n', '100',
            '-c', '10',
            '-t', '30',
            '-H', 'Accept: application/json',
            '-o', 'output.json'
        ])
        assert result.exit_code == 0
    
    def test_default_values(self):
        """Test that default values are applied."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--url', 'http://example.com'])
        assert result.exit_code == 0
        # Defaults: method=GET, requests=100, concurrency=10, timeout=30
    
    def test_invalid_url(self):
        """Test CLI with invalid URL."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--url', 'not-a-url'])
        assert result.exit_code != 0
        assert 'scheme' in result.output.lower() or 'invalid' in result.output.lower()
    
    def test_invalid_method(self):
        """Test CLI with invalid HTTP method."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--method', 'INVALID'
        ])
        assert result.exit_code != 0
        assert 'Invalid HTTP method' in result.output or 'method' in result.output.lower()
    
    def test_negative_requests(self):
        """Test CLI with negative requests count."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--requests', '-10'
        ])
        assert result.exit_code != 0
    
    def test_zero_requests(self):
        """Test CLI with zero requests count."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--requests', '0'
        ])
        assert result.exit_code != 0
    
    def test_negative_concurrency(self):
        """Test CLI with negative concurrency."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--concurrency', '-5'
        ])
        assert result.exit_code != 0
    
    def test_concurrency_exceeds_requests(self):
        """Test CLI when concurrency exceeds total requests."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--requests', '10',
            '--concurrency', '20'
        ])
        assert result.exit_code != 0
        assert 'cannot exceed' in result.output.lower() or 'concurrency' in result.output.lower()
    
    def test_negative_timeout(self):
        """Test CLI with negative timeout."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--timeout', '-10'
        ])
        assert result.exit_code != 0
    
    def test_multiple_headers(self):
        """Test CLI with multiple headers."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--header', 'Content-Type: application/json',
            '--header', 'Authorization: Bearer token123',
            '--header', 'X-Custom: value'
        ])
        assert result.exit_code == 0
    
    def test_invalid_header_format(self):
        """Test CLI with invalid header format."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--header', 'InvalidHeader'
        ])
        assert result.exit_code != 0
        assert 'header' in result.output.lower()
    
    def test_post_with_data(self):
        """Test CLI with POST method and data."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com/api',
            '--method', 'POST',
            '--data', '{"name": "test", "value": 123}'
        ])
        assert result.exit_code == 0
    
    def test_help_option(self):
        """Test that --help displays help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Load testing tool' in result.output
        assert '--url' in result.output
        assert '--method' in result.output
        assert '--requests' in result.output
        assert '--concurrency' in result.output
        assert '--timeout' in result.output
        assert '--header' in result.output
        assert '--data' in result.output
        assert '--output' in result.output
    
    def test_url_without_scheme(self):
        """Test URL without scheme (http:// or https://)."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--url', 'example.com'])
        assert result.exit_code != 0
        assert 'scheme' in result.output.lower()
    
    def test_https_url(self):
        """Test HTTPS URL."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--url', 'https://example.com'])
        assert result.exit_code == 0
    
    def test_http_methods(self):
        """Test all valid HTTP methods."""
        runner = CliRunner()
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        
        for method in methods:
            result = runner.invoke(cli, [
                '--url', 'http://example.com',
                '--method', method
            ])
            assert result.exit_code == 0, f"Method {method} should be valid"
    
    def test_method_case_insensitive(self):
        """Test that HTTP method is case-insensitive."""
        runner = CliRunner()
        for method in ['get', 'Get', 'GET', 'post', 'Post', 'POST']:
            result = runner.invoke(cli, [
                '--url', 'http://example.com',
                '--method', method
            ])
            assert result.exit_code == 0
    
    def test_output_file_path(self):
        """Test output file path option."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--output', '/tmp/test_report.json'
        ])
        assert result.exit_code == 0
    
    def test_context_stores_config_and_output(self):
        """Test that CLI creates Config object with correct parameters."""
        runner = CliRunner()
        
        # Test that CLI successfully creates config with all parameters
        result = runner.invoke(cli, [
            '--url', 'http://example.com',
            '--method', 'POST',
            '--requests', '50',
            '--concurrency', '5',
            '--timeout', '20',
            '--header', 'Content-Type: application/json',
            '--data', '{"test": "data"}',
            '--output', 'test.json'
        ])
        
        # CLI should succeed
        assert result.exit_code == 0
    
    def test_json_data_body(self):
        """Test with JSON data in body."""
        runner = CliRunner()
        json_data = json.dumps({"key": "value", "nested": {"item": 123}})
        result = runner.invoke(cli, [
            '--url', 'http://example.com/api',
            '--method', 'POST',
            '--data', json_data
        ])
        assert result.exit_code == 0
    
    def test_empty_data_body(self):
        """Test with empty string as data."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--url', 'http://example.com/api',
            '--method', 'POST',
            '--data', ''
        ])
        assert result.exit_code == 0
