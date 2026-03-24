"""
Tests for the report generator.
"""

import io
from loadtest.reporter import Reporter
from rich.console import Console


class TestReporter:
    """Test cases for the report generator."""

    def test_reporter_initialization(self):
        """Test Reporter can be initialized."""
        reporter = Reporter()
        assert reporter.console is not None
    
    def test_reporter_with_custom_console(self):
        """Test Reporter can be initialized with custom console."""
        custom_console = Console()
        reporter = Reporter(console=custom_console)
        assert reporter.console is custom_console
    
    def test_generate_report_with_empty_statistics(self):
        """Test generating report with empty statistics."""
        output = io.StringIO()
        console = Console(file=output, width=100, legacy_windows=False)
        reporter = Reporter(console=console)
        
        statistics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'error_rate': 0.0,
            'response_times': {},
            'throughput': 0.0,
            'duration': 0.0,
            'status_codes': {},
        }
        
        reporter.generate_report(statistics)
        
        output_str = output.getvalue()
        assert 'Summary Statistics' in output_str
        assert 'Total Requests: 0' in output_str
    
    def test_generate_report_with_complete_statistics(self):
        """Test generating report with complete statistics."""
        output = io.StringIO()
        console = Console(file=output, width=100, legacy_windows=False)
        reporter = Reporter(console=console)
        
        statistics = {
            'total_requests': 100,
            'successful_requests': 95,
            'failed_requests': 5,
            'error_rate': 5.0,
            'response_times': {
                'min': 0.010,
                'max': 0.500,
                'mean': 0.150,
                'median': 0.120,
                'p95': 0.400,
                'p99': 0.480,
            },
            'throughput': 50.0,
            'duration': 2.0,
            'status_codes': {
                200: 95,
                500: 5,
            },
        }
        
        reporter.generate_report(statistics)
        
        output_str = output.getvalue()
        
        # Check summary section
        assert 'Summary Statistics' in output_str
        assert 'Total Requests: 100' in output_str
        assert 'Successful: 95' in output_str
        assert 'Failed: 5' in output_str
        assert 'Error Rate: 5.00%' in output_str
        assert 'Duration: 2.00s' in output_str
        assert 'Throughput: 50.00 req/s' in output_str
        
        # Check response times section
        assert 'Response Time Statistics' in output_str
        assert 'Minimum' in output_str
        assert 'Mean' in output_str
        assert 'Median' in output_str
        assert '95th Percentile' in output_str
        assert '99th Percentile' in output_str
        assert 'Maximum' in output_str
        
        # Check response times are converted to milliseconds
        assert '10.00' in output_str  # min: 0.010s = 10ms
        assert '500.00' in output_str  # max: 0.500s = 500ms
        
        # Check status codes section
        assert 'Status Code Distribution' in output_str
        assert '200' in output_str
        assert '500' in output_str
        assert '95.0%' in output_str
        assert '5.0%' in output_str
    
    def test_generate_report_with_various_status_codes(self):
        """Test generating report with various status code ranges."""
        output = io.StringIO()
        console = Console(file=output, width=100, legacy_windows=False)
        reporter = Reporter(console=console)
        
        statistics = {
            'total_requests': 100,
            'successful_requests': 70,
            'failed_requests': 30,
            'error_rate': 30.0,
            'response_times': {
                'min': 0.050,
                'max': 1.000,
                'mean': 0.200,
                'median': 0.180,
                'p95': 0.800,
                'p99': 0.950,
            },
            'throughput': 25.0,
            'duration': 4.0,
            'status_codes': {
                200: 50,
                201: 20,
                301: 10,
                404: 15,
                500: 5,
            },
        }
        
        reporter.generate_report(statistics)
        
        output_str = output.getvalue()
        
        # Check all status codes are present
        assert '200' in output_str
        assert '201' in output_str
        assert '301' in output_str
        assert '404' in output_str
        assert '500' in output_str
    
    def test_print_summary(self):
        """Test _print_summary method."""
        output = io.StringIO()
        console = Console(file=output, width=100, legacy_windows=False)
        reporter = Reporter(console=console)
        
        statistics = {
            'total_requests': 50,
            'successful_requests': 48,
            'failed_requests': 2,
            'error_rate': 4.0,
            'throughput': 10.0,
            'duration': 5.0,
        }
        
        reporter._print_summary(statistics)
        
        output_str = output.getvalue()
        assert 'Total Requests: 50' in output_str
        assert 'Successful: 48' in output_str
        assert 'Failed: 2' in output_str
        assert 'Error Rate: 4.00%' in output_str
        assert 'Throughput: 10.00 req/s' in output_str
        assert 'Duration: 5.00s' in output_str
    
    def test_print_response_times(self):
        """Test _print_response_times method."""
        output = io.StringIO()
        console = Console(file=output, width=100, legacy_windows=False)
        reporter = Reporter(console=console)
        
        statistics = {
            'response_times': {
                'min': 0.025,
                'max': 0.750,
                'mean': 0.200,
                'median': 0.180,
                'p95': 0.600,
                'p99': 0.700,
            }
        }
        
        reporter._print_response_times(statistics)
        
        output_str = output.getvalue()
        assert 'Response Time Statistics' in output_str
        assert '25.00' in output_str  # min in ms
        assert '750.00' in output_str  # max in ms
    
    def test_print_status_codes(self):
        """Test _print_status_codes method."""
        output = io.StringIO()
        console = Console(file=output, width=100, legacy_windows=False)
        reporter = Reporter(console=console)
        
        statistics = {
            'status_codes': {
                200: 80,
                404: 15,
                500: 5,
            }
        }
        
        reporter._print_status_codes(statistics)
        
        output_str = output.getvalue()
        assert 'Status Code Distribution' in output_str
        assert '200' in output_str
        assert '404' in output_str
        assert '500' in output_str
        assert '80.0%' in output_str
        assert '15.0%' in output_str
        assert '5.0%' in output_str
    
    def test_print_status_codes_empty(self):
        """Test _print_status_codes with empty status codes."""
        output = io.StringIO()
        console = Console(file=output, width=100, legacy_windows=False)
        reporter = Reporter(console=console)
        
        statistics = {
            'status_codes': {}
        }
        
        reporter._print_status_codes(statistics)
        
        output_str = output.getvalue()
        # Should not print anything if no status codes
        assert 'Status Code Distribution' not in output_str
    
    def test_response_times_with_missing_keys(self):
        """Test response times handling with missing keys."""
        output = io.StringIO()
        console = Console(file=output, width=100, legacy_windows=False)
        reporter = Reporter(console=console)
        
        statistics = {
            'response_times': {
                'min': 0.100,
                # Missing other keys
            }
        }
        
        reporter._print_response_times(statistics)
        
        output_str = output.getvalue()
        assert 'Response Time Statistics' in output_str
        assert '100.00' in output_str  # min value
        assert '0.00' in output_str  # default for missing keys
