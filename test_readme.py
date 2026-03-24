"""Tests for README.md documentation."""
import os


def test_readme_exists():
    """Test that README.md exists."""
    assert os.path.exists("README.md"), "README.md should exist"


def test_readme_has_joke_cli_section():
    """Test that README.md includes documentation for the Joke CLI."""
    with open("README.md", "r") as f:
        content = f.read()
    
    # Check for main sections
    assert "## Joke CLI" in content, "README should have a Joke CLI section"
    assert "## Flask API" in content, "README should preserve Flask API section"
    
    # Check for important subsections
    assert "### Overview" in content, "README should have an Overview subsection"
    assert "### Installation" in content, "README should have an Installation subsection"
    assert "### Usage" in content, "README should have a Usage subsection"
    assert "### Example Output" in content, "README should have an Example Output subsection"
    assert "### Joke Categories" in content, "README should have a Joke Categories subsection"
    assert "### Command-Line Options" in content, "README should have a Command-Line Options subsection"


def test_readme_includes_usage_examples():
    """Test that README.md includes usage examples."""
    with open("README.md", "r") as f:
        content = f.read()
    
    # Check for command examples
    assert "python3 joke_cli.py" in content, "README should include the CLI command"
    assert "pip install -r requirements.txt" in content, "README should include installation command"


def test_readme_documents_joke_categories():
    """Test that README.md documents the joke categories."""
    with open("README.md", "r") as f:
        content = f.read()
    
    # Check for documented categories
    assert "Programming" in content, "README should mention Programming category"
    assert "Dad" in content, "README should mention Dad category"
    assert "General" in content, "README should mention General category"


def test_readme_shows_example_output():
    """Test that README.md shows example output for both joke formats."""
    with open("README.md", "r") as f:
        content = f.read()
    
    # Check for both joke formats
    assert "Two-part jokes" in content or "setup and punchline" in content, \
        "README should document two-part joke format"
    assert "One-liner" in content, "README should document one-liner joke format"


def test_readme_preserves_flask_api_content():
    """Test that README.md preserves existing Flask API documentation."""
    with open("README.md", "r") as f:
        content = f.read()
    
    # Ensure Flask API section still exists
    assert "Flask API" in content, "README should preserve Flask API documentation"
