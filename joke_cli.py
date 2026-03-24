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
    
    # Handle both joke formats: setup/punchline or single joke
    if 'setup' in joke and 'punchline' in joke:
        print(f"{joke['setup']}")
        print(f"{joke['punchline']}")
    elif 'joke' in joke:
        print(f"{joke['joke']}")
    else:
        print("Error: Invalid joke format")


if __name__ == "__main__":
    main()
