import pytest


def test_requirements_file_exists():
    """Verify that requirements.txt exists and is readable."""
    with open('requirements.txt', 'r') as f:
        content = f.read()
    assert content.strip() != ""


def test_requirements_format():
    """Verify that requirements.txt has valid format."""
    with open('requirements.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Should have flask and pytest
    flask_lines = [l for l in lines if l.lower().startswith('flask')]
    pytest_lines = [l for l in lines if l.lower().startswith('pytest')]
    
    assert len(flask_lines) == 1, "Should have exactly one flask entry"
    assert len(pytest_lines) == 1, "Should have exactly one pytest entry"


def test_requirements_pinned_versions():
    """Verify that all dependencies use pinned versions (==) for reproducibility."""
    with open('requirements.txt', 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    for line in lines:
        assert '==' in line, f"Dependency should be pinned with ==: {line}"


def test_flask_version():
    """Verify Flask version is appropriate."""
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    # Check that flask is specified
    assert 'flask==' in content.lower()
    
    # Extract version
    for line in content.split('\n'):
        if line.lower().startswith('flask=='):
            version = line.split('==')[1].strip()
            # Verify it's a valid version format (major.minor.patch)
            parts = version.split('.')
            assert len(parts) == 3, "Flask version should be in major.minor.patch format"
            for part in parts:
                assert part.isdigit(), f"Version part should be numeric: {part}"


def test_pytest_version():
    """Verify pytest version is appropriate."""
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    # Check that pytest is specified
    assert 'pytest==' in content.lower()
    
    # Extract version
    for line in content.split('\n'):
        if line.lower().startswith('pytest=='):
            version = line.split('==')[1].strip()
            # Verify it's a valid version format (major.minor.patch)
            parts = version.split('.')
            assert len(parts) == 3, "pytest version should be in major.minor.patch format"
            for part in parts:
                assert part.isdigit(), f"Version part should be numeric: {part}"


def test_no_external_api_dependencies():
    """Verify that no external API client libraries are included.
    
    The joke CLI uses only standard library (argparse) and a local joke collection,
    so we shouldn't have requests, httpx, or similar HTTP client libraries.
    """
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
    
    # These libraries shouldn't be present for the joke CLI
    unwanted_libs = ['requests', 'httpx', 'urllib3', 'aiohttp']
    for lib in unwanted_libs:
        assert lib not in content, f"Unexpected dependency {lib} found - joke CLI should use only standard library"
