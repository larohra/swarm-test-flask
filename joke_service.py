"""Joke service module for retrieving jokes."""
import random


JOKES = [
    {
        "setup": "Why don't scientists trust atoms?",
        "punchline": "Because they make up everything!"
    },
    {
        "setup": "Why did the scarecrow win an award?",
        "punchline": "He was outstanding in his field!"
    },
    {
        "setup": "Why don't eggs tell jokes?",
        "punchline": "They'd crack each other up!"
    },
    {
        "setup": "What do you call a fake noodle?",
        "punchline": "An impasta!"
    },
    {
        "setup": "How do you organize a space party?",
        "punchline": "You planet!"
    }
]


def get_random_joke():
    """Return a random joke from the collection.
    
    Returns:
        dict: A joke dictionary with 'setup' and 'punchline' keys.
    """
    return random.choice(JOKES)
