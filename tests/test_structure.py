"""
Tests for the package structure and basic functionality.
"""
import os
import sys


class TestPackageStructure:
    """Test cases for package structure."""

    def test_loadtest_package_exists(self):
        """Test that loadtest package can be imported."""
        import loadtest
        assert loadtest is not None

    def test_loadtest_version(self):
        """Test that loadtest package has a version."""
        import loadtest
        assert hasattr(loadtest, '__version__')
        assert loadtest.__version__ == "0.1.0"

    def test_all_modules_exist(self):
        """Test that all required modules exist."""
        import loadtest
        from loadtest import cli, config, engine, metrics, reporter
        from loadtest import __main__
        
        assert cli is not None
        assert config is not None
        assert engine is not None
        assert metrics is not None
        assert reporter is not None
        assert __main__ is not None

    def test_directory_structure(self):
        """Test that all required directories exist."""
        assert os.path.isdir('loadtest')
        assert os.path.isdir('tests')
        assert os.path.isdir('examples')

    def test_init_files_exist(self):
        """Test that __init__.py files exist."""
        assert os.path.isfile('loadtest/__init__.py')
        assert os.path.isfile('tests/__init__.py')

    def test_main_modules_exist(self):
        """Test that all main module files exist."""
        modules = [
            'loadtest/__main__.py',
            'loadtest/cli.py',
            'loadtest/config.py',
            'loadtest/engine.py',
            'loadtest/metrics.py',
            'loadtest/reporter.py',
        ]
        for module in modules:
            assert os.path.isfile(module), f"{module} should exist"

    def test_test_files_exist(self):
        """Test that all test files exist."""
        test_files = [
            'tests/test_config.py',
            'tests/test_engine.py',
            'tests/test_metrics.py',
            'tests/test_reporter.py',
            'tests/test_integration.py',
        ]
        for test_file in test_files:
            assert os.path.isfile(test_file), f"{test_file} should exist"

    def test_example_config_exists(self):
        """Test that example config file exists."""
        assert os.path.isfile('examples/sample_config.yaml')

    def test_requirements_updated(self):
        """Test that requirements.txt has all necessary dependencies."""
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        required_packages = [
            'aiohttp',
            'click',
            'rich',
            'pytest-asyncio',
            'pyyaml',
        ]
        
        for package in required_packages:
            assert package in requirements.lower(), f"{package} should be in requirements.txt"
