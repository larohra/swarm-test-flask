"""Command-line interface for displaying jokes."""
import argparse
from joke_service import get_random_joke


def main():
    """Main entry point for the joke CLI.
    
    Parses command-line arguments and displays a random joke.
    """
    parser = argparse.ArgumentParser(
        description="Display a random joke from the command line"
    )
    parser.parse_args()
    
    # Get and display a random joke
    joke = get_random_joke()
    print(f"{joke['setup']}")
    print(f"{joke['punchline']}")


if __name__ == "__main__":
    main()
