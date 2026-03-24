import random

JOKES = [
    # Programming jokes
    {
        "category": "programming",
        "setup": "Why do programmers prefer dark mode?",
        "punchline": "Because light attracts bugs!"
    },
    {
        "category": "programming",
        "setup": "How many programmers does it take to change a light bulb?",
        "punchline": "None. It's a hardware problem."
    },
    {
        "category": "programming",
        "joke": "There are only 10 types of people in the world: those who understand binary and those who don't."
    },
    {
        "category": "programming",
        "setup": "Why do Java developers wear glasses?",
        "punchline": "Because they don't see sharp!"
    },
    {
        "category": "programming",
        "joke": "A SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'"
    },
    
    # Dad jokes
    {
        "category": "dad",
        "setup": "What do you call a fake noodle?",
        "punchline": "An impasta!"
    },
    {
        "category": "dad",
        "setup": "Why don't eggs tell jokes?",
        "punchline": "They'd crack each other up!"
    },
    {
        "category": "dad",
        "setup": "What do you call a bear with no teeth?",
        "punchline": "A gummy bear!"
    },
    {
        "category": "dad",
        "setup": "Why did the scarecrow win an award?",
        "punchline": "Because he was outstanding in his field!"
    },
    
    # General humor
    {
        "category": "general",
        "setup": "What do you call a fish with no eyes?",
        "punchline": "A fsh!"
    },
    {
        "category": "general",
        "setup": "Why don't scientists trust atoms?",
        "punchline": "Because they make up everything!"
    },
    {
        "category": "general",
        "joke": "I told my wife she was drawing her eyebrows too high. She looked surprised."
    },
    {
        "category": "general",
        "setup": "What did the ocean say to the beach?",
        "punchline": "Nothing, it just waved!"
    },
    {
        "category": "general",
        "setup": "Why can't a bicycle stand up by itself?",
        "punchline": "It's two tired!"
    },
    {
        "category": "general",
        "setup": "What do you call cheese that isn't yours?",
        "punchline": "Nacho cheese!"
    }
]


def get_random_joke():
    """
    Returns a random joke from the collection.
    
    Returns:
        dict: A dictionary containing either:
            - 'setup' and 'punchline' keys for two-part jokes, or
            - 'joke' key for one-liner jokes
            All jokes include a 'category' key.
    """
    return random.choice(JOKES)
