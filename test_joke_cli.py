"""Tests for the joke CLI module."""
import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
import argparse
import joke_cli


class TestJokeCLI(unittest.TestCase):
    """Test cases for the joke CLI."""

    @patch('joke_cli.get_random_joke')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_with_setup_punchline_joke(self, mock_stdout, mock_get_joke):
        """Test main() with a two-part joke (setup/punchline)."""
        # Mock a joke with setup and punchline
        mock_get_joke.return_value = {
            "category": "programming",
            "setup": "Why do programmers prefer dark mode?",
            "punchline": "Because light attracts bugs!"
        }
        
        # Call main
        with patch('sys.argv', ['joke_cli.py']):
            joke_cli.main()
        
        # Verify the joke service was called
        mock_get_joke.assert_called_once()
        
        # Verify output formatting
        output = mock_stdout.getvalue()
        self.assertIn("Why do programmers prefer dark mode?", output)
        self.assertIn("Because light attracts bugs!", output)

    @patch('joke_cli.get_random_joke')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_output_format(self, mock_stdout, mock_get_joke):
        """Test that output is formatted with setup and punchline on separate lines."""
        mock_get_joke.return_value = {
            "category": "dad",
            "setup": "Test setup",
            "punchline": "Test punchline"
        }
        
        with patch('sys.argv', ['joke_cli.py']):
            joke_cli.main()
        
        output = mock_stdout.getvalue()
        lines = output.strip().split('\n')
        
        # Should have at least 2 lines
        self.assertGreaterEqual(len(lines), 2)
        self.assertIn("Test setup", output)
        self.assertIn("Test punchline", output)

    @patch('joke_cli.get_random_joke')
    def test_main_calls_joke_service(self, mock_get_joke):
        """Test that main() calls get_random_joke()."""
        mock_get_joke.return_value = {
            "setup": "Setup",
            "punchline": "Punchline"
        }
        
        with patch('sys.argv', ['joke_cli.py']):
            with patch('sys.stdout', new_callable=StringIO):
                joke_cli.main()
        
        # Verify get_random_joke was called
        mock_get_joke.assert_called_once()

    @patch('sys.argv', ['joke_cli.py', '--help'])
    def test_argument_parser_help(self):
        """Test that argparse is configured with help text."""
        # The --help flag should cause SystemExit
        with self.assertRaises(SystemExit) as cm:
            joke_cli.main()
        
        # Exit code 0 indicates successful help display
        self.assertEqual(cm.exception.code, 0)

    @patch('sys.argv', ['joke_cli.py'])
    @patch('joke_cli.get_random_joke')
    def test_argument_parser_no_args(self, mock_get_joke):
        """Test that CLI works with no arguments."""
        mock_get_joke.return_value = {
            "setup": "Setup",
            "punchline": "Punchline"
        }
        
        with patch('sys.stdout', new_callable=StringIO):
            # Should not raise any exceptions
            try:
                joke_cli.main()
            except SystemExit:
                self.fail("main() raised SystemExit unexpectedly")

    @patch('joke_cli.get_random_joke')
    @patch('sys.stdout', new_callable=StringIO)
    def test_integration_can_execute(self, mock_stdout, mock_get_joke):
        """Integration test: verify the CLI can be executed end-to-end."""
        mock_get_joke.return_value = {
            "category": "general",
            "setup": "What did the ocean say to the beach?",
            "punchline": "Nothing, it just waved!"
        }
        
        with patch('sys.argv', ['joke_cli.py']):
            joke_cli.main()
        
        output = mock_stdout.getvalue()
        
        # Verify expected output format
        self.assertTrue(len(output) > 0, "CLI should produce output")
        self.assertIn("What did the ocean say to the beach?", output)
        self.assertIn("Nothing, it just waved!", output)

    @patch('joke_cli.get_random_joke')
    @patch('sys.stdout', new_callable=StringIO)
    def test_different_jokes(self, mock_stdout, mock_get_joke):
        """Test that CLI handles different jokes correctly."""
        jokes = [
            {
                "category": "programming",
                "setup": "Why do Java developers wear glasses?",
                "punchline": "Because they don't see sharp!"
            },
            {
                "category": "dad",
                "setup": "What do you call a fake noodle?",
                "punchline": "An impasta!"
            }
        ]
        
        for joke in jokes:
            mock_get_joke.return_value = joke
            mock_stdout.truncate(0)
            mock_stdout.seek(0)
            
            with patch('sys.argv', ['joke_cli.py']):
                joke_cli.main()
            
            output = mock_stdout.getvalue()
            self.assertIn(joke['setup'], output)
            self.assertIn(joke['punchline'], output)

    @patch('joke_cli.get_random_joke')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_with_one_liner_joke(self, mock_stdout, mock_get_joke):
        """Test main() with a one-liner joke (single 'joke' field)."""
        # Mock a one-liner joke
        mock_get_joke.return_value = {
            "category": "programming",
            "joke": "There are only 10 types of people in the world: those who understand binary and those who don't."
        }
        
        # Call main
        with patch('sys.argv', ['joke_cli.py']):
            joke_cli.main()
        
        # Verify the joke service was called
        mock_get_joke.assert_called_once()
        
        # Verify output formatting
        output = mock_stdout.getvalue()
        self.assertIn("There are only 10 types of people in the world", output)
        self.assertIn("those who understand binary", output)

    @patch('joke_cli.get_random_joke')
    @patch('sys.stdout', new_callable=StringIO)
    def test_both_joke_formats(self, mock_stdout, mock_get_joke):
        """Test that CLI correctly handles both joke formats."""
        jokes = [
            {
                "category": "programming",
                "setup": "Setup joke",
                "punchline": "Punchline joke"
            },
            {
                "category": "general",
                "joke": "One-liner joke text"
            }
        ]
        
        for joke in jokes:
            mock_get_joke.return_value = joke
            mock_stdout.truncate(0)
            mock_stdout.seek(0)
            
            with patch('sys.argv', ['joke_cli.py']):
                joke_cli.main()
            
            output = mock_stdout.getvalue()
            
            if 'setup' in joke:
                self.assertIn(joke['setup'], output)
                self.assertIn(joke['punchline'], output)
            else:
                self.assertIn(joke['joke'], output)


class TestCLIScript(unittest.TestCase):
    """Test that the CLI can be executed as a script."""

    @patch('joke_cli.main')
    def test_script_execution(self, mock_main):
        """Test that the script calls main() when executed."""
        # This would normally be tested by running the script
        # Since we can't easily test __name__ == "__main__", 
        # we verify the function exists and is callable
        self.assertTrue(callable(joke_cli.main))


if __name__ == '__main__':
    unittest.main()
