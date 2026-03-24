"""Tests for the joke CLI module."""
import pytest
from unittest.mock import patch
from io import StringIO
import joke_cli
from joke_service import get_random_joke


def test_get_random_joke_returns_joke():
    """Test that get_random_joke returns a joke with setup and punchline."""
    joke = get_random_joke()
    assert isinstance(joke, dict)
    assert "setup" in joke
    assert "punchline" in joke
    assert isinstance(joke["setup"], str)
    assert isinstance(joke["punchline"], str)
    assert len(joke["setup"]) > 0
    assert len(joke["punchline"]) > 0


def test_main_displays_joke():
    """Test that main() displays a joke with setup and punchline."""
    test_joke = {
        "setup": "Test setup?",
        "punchline": "Test punchline!"
    }
    
    with patch("sys.argv", ["joke_cli.py"]):
        with patch("joke_cli.get_random_joke", return_value=test_joke):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                joke_cli.main()
                output = mock_stdout.getvalue()
                assert "Test setup?" in output
                assert "Test punchline!" in output


def test_main_calls_get_random_joke():
    """Test that main() calls get_random_joke."""
    test_joke = {
        "setup": "Why test?",
        "punchline": "To ensure quality!"
    }
    
    with patch("sys.argv", ["joke_cli.py"]):
        with patch("joke_cli.get_random_joke", return_value=test_joke) as mock_get_joke:
            with patch("sys.stdout", new_callable=StringIO):
                joke_cli.main()
                mock_get_joke.assert_called_once()


def test_cli_accepts_no_arguments():
    """Test that the CLI can be run without arguments."""
    with patch("sys.argv", ["joke_cli.py"]):
        with patch("joke_cli.get_random_joke", return_value={"setup": "Q", "punchline": "A"}):
            with patch("sys.stdout", new_callable=StringIO):
                # Should not raise an exception
                joke_cli.main()


def test_main_output_format():
    """Test that main() outputs setup and punchline on separate lines."""
    test_joke = {
        "setup": "Setup line",
        "punchline": "Punchline line"
    }
    
    with patch("sys.argv", ["joke_cli.py"]):
        with patch("joke_cli.get_random_joke", return_value=test_joke):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                joke_cli.main()
                output = mock_stdout.getvalue()
                lines = output.strip().split("\n")
                assert len(lines) == 2
                assert lines[0] == "Setup line"
                assert lines[1] == "Punchline line"
