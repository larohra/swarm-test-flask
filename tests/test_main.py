"""
Tests for the main entry point.
"""
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import pytest

from loadtest.config import Config
from loadtest.metrics import MetricsCollector, RequestResult
from loadtest.reporter import Reporter


class TestRunLoadTest:
    """Test cases for run_load_test function."""
    
    @pytest.mark.asyncio
    async def test_run_load_test_basic(self):
        """Test basic load test execution."""
        from loadtest.__main__ import run_load_test
        from rich.console import Console
        
        # Create config
        config = Config(
            url="http://example.com",
            method="GET",
            requests=5,
            concurrency=2,
            timeout=30
        )
        
        # Mock console
        console = Mock(spec=Console)
        
        # Mock engine
        with patch('loadtest.__main__.Engine') as MockEngine:
            mock_engine = MockEngine.return_value
            
            # Create mock results
            mock_results = [
                RequestResult(
                    status_code=200,
                    response_time=0.1,
                    error=None,
                    timestamp=1000.0
                )
                for _ in range(5)
            ]
            
            mock_engine.run = AsyncMock(return_value=mock_results)
            
            # Run the test
            metrics = await run_load_test(config, console)
            
            # Verify engine was called correctly
            MockEngine.assert_called_once_with(
                url="http://example.com",
                method="GET",
                timeout=30,
                headers={},
                body=None
            )
            mock_engine.run.assert_called_once_with(5, 2)
            
            # Verify metrics were collected
            assert len(metrics.results) == 5
            assert metrics.start_time is not None
            assert metrics.end_time is not None
    
    @pytest.mark.asyncio
    async def test_run_load_test_with_headers_and_body(self):
        """Test load test with custom headers and body."""
        from loadtest.__main__ import run_load_test
        from rich.console import Console
        
        # Create config with headers and body
        config = Config(
            url="http://example.com/api",
            method="POST",
            requests=3,
            concurrency=1,
            timeout=10,
            headers={"Content-Type": "application/json"},
            body='{"test": "data"}'
        )
        
        console = Mock(spec=Console)
        
        with patch('loadtest.__main__.Engine') as MockEngine:
            mock_engine = MockEngine.return_value
            mock_results = [
                RequestResult(status_code=201, response_time=0.2, error=None, timestamp=1000.0)
                for _ in range(3)
            ]
            mock_engine.run = AsyncMock(return_value=mock_results)
            
            metrics = await run_load_test(config, console)
            
            # Verify engine was initialized with correct parameters
            MockEngine.assert_called_once_with(
                url="http://example.com/api",
                method="POST",
                timeout=10,
                headers={"Content-Type": "application/json"},
                body='{"test": "data"}'
            )
            
            assert len(metrics.results) == 3


class TestMain:
    """Test cases for main function."""
    
    def test_main_successful_execution(self):
        """Test successful main execution flow."""
        from loadtest.__main__ import main
        
        # Mock all dependencies
        with patch('loadtest.__main__.cli_command') as mock_cli, \
             patch('loadtest.__main__.run_load_test') as mock_run_test, \
             patch('loadtest.__main__.Reporter') as MockReporter, \
             patch('asyncio.run') as mock_asyncio_run, \
             patch('sys.argv', ['loadtest', '--url', 'http://example.com']):
            
            # Setup mock config
            mock_config = Config(url="http://example.com")
            mock_ctx = MagicMock()
            mock_ctx.obj = {'config': mock_config, 'output': None}
            mock_cli.make_context.return_value = mock_ctx
            
            # Setup mock metrics
            mock_metrics = Mock(spec=MetricsCollector)
            mock_metrics.get_statistics.return_value = {
                'total_requests': 10,
                'successful_requests': 10,
                'failed_requests': 0,
                'error_rate': 0.0,
                'response_times': {},
                'throughput': 10.0,
                'duration': 1.0,
                'status_codes': {200: 10}
            }
            mock_asyncio_run.return_value = mock_metrics
            
            # Setup mock reporter
            mock_reporter = MockReporter.return_value
            
            # Run main
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Verify exit code is 0 (success)
            assert exc_info.value.code == 0
            
            # Verify components were called
            mock_cli.make_context.assert_called_once()
            mock_asyncio_run.assert_called_once()
            mock_reporter.generate_report.assert_called_once()
    
    def test_main_with_failed_requests(self):
        """Test main with failed requests exits with code 1."""
        from loadtest.__main__ import main
        
        with patch('loadtest.__main__.cli_command') as mock_cli, \
             patch('asyncio.run') as mock_asyncio_run, \
             patch('loadtest.__main__.Reporter'), \
             patch('sys.argv', ['loadtest', '--url', 'http://example.com']):
            
            mock_config = Config(url="http://example.com")
            mock_ctx = MagicMock()
            mock_ctx.obj = {'config': mock_config, 'output': None}
            mock_cli.make_context.return_value = mock_ctx
            
            mock_metrics = Mock(spec=MetricsCollector)
            mock_metrics.get_statistics.return_value = {
                'total_requests': 10,
                'successful_requests': 8,
                'failed_requests': 2,
                'error_rate': 20.0,
            }
            mock_asyncio_run.return_value = mock_metrics
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Verify exit code is 1 (failure)
            assert exc_info.value.code == 1
    
    def test_main_with_output_file(self):
        """Test main saves report to output file."""
        from loadtest.__main__ import main
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'report.json')
            
            with patch('loadtest.__main__.cli_command') as mock_cli, \
                 patch('asyncio.run') as mock_asyncio_run, \
                 patch('loadtest.__main__.Reporter'), \
                 patch('sys.argv', ['loadtest', '--url', 'http://example.com']):
                
                mock_config = Config(url="http://example.com")
                mock_ctx = MagicMock()
                mock_ctx.obj = {'config': mock_config, 'output': output_file}
                mock_cli.make_context.return_value = mock_ctx
                
                statistics = {
                    'total_requests': 10,
                    'successful_requests': 10,
                    'failed_requests': 0,
                }
                
                mock_metrics = Mock(spec=MetricsCollector)
                mock_metrics.get_statistics.return_value = statistics
                mock_asyncio_run.return_value = mock_metrics
                
                with pytest.raises(SystemExit):
                    main()
                
                # Verify file was created with statistics
                assert os.path.exists(output_file)
                with open(output_file) as f:
                    saved_data = json.load(f)
                assert saved_data == statistics
    
    def test_main_keyboard_interrupt(self):
        """Test main handles keyboard interrupt gracefully."""
        from loadtest.__main__ import main
        
        with patch('loadtest.__main__.cli_command') as mock_cli, \
             patch('sys.argv', ['loadtest', '--url', 'http://example.com']):
            
            mock_ctx = MagicMock()
            mock_cli.make_context.side_effect = KeyboardInterrupt()
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Verify exit code is 130 (interrupted)
            assert exc_info.value.code == 130
    
    def test_main_handles_general_exception(self):
        """Test main handles general exceptions."""
        from loadtest.__main__ import main
        
        with patch('loadtest.__main__.cli_command') as mock_cli, \
             patch('sys.argv', ['loadtest', '--url', 'http://example.com']):
            
            mock_ctx = MagicMock()
            mock_cli.make_context.side_effect = Exception("Test error")
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Verify exit code is 1 (error)
            assert exc_info.value.code == 1
