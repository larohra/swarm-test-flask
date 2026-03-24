import pytest
from joke_service import get_random_joke, JOKES


def test_get_random_joke_returns_valid_structure():
    """Test that get_random_joke() returns a valid joke structure"""
    joke = get_random_joke()
    
    # Should return a dictionary
    assert isinstance(joke, dict), "Joke should be a dictionary"
    
    # Should have a category
    assert "category" in joke, "Joke should have a category field"
    
    # Should have either setup/punchline or joke field
    has_setup_punchline = "setup" in joke and "punchline" in joke
    has_joke = "joke" in joke
    assert has_setup_punchline or has_joke, "Joke should have either setup/punchline or joke field"


def test_jokes_are_non_empty():
    """Test that jokes are non-empty"""
    joke = get_random_joke()
    
    # Category should be non-empty
    assert isinstance(joke["category"], str), "Category should be a string"
    assert len(joke["category"]) > 0, "Category should not be empty"
    
    # Content fields should be non-empty
    if "setup" in joke:
        assert isinstance(joke["setup"], str), "Setup should be a string"
        assert len(joke["setup"]) > 0, "Setup should not be empty"
        
    if "punchline" in joke:
        assert isinstance(joke["punchline"], str), "Punchline should be a string"
        assert len(joke["punchline"]) > 0, "Punchline should not be empty"
        
    if "joke" in joke:
        assert isinstance(joke["joke"], str), "Joke should be a string"
        assert len(joke["joke"]) > 0, "Joke should not be empty"


def test_multiple_calls_can_return_different_jokes():
    """Test that multiple calls to get_random_joke() can return different jokes"""
    # Make multiple calls to get_random_joke
    jokes = [get_random_joke() for _ in range(50)]
    
    # Convert to set of joke IDs to check uniqueness
    # Using id() to check if we get different joke objects
    unique_jokes = set()
    for joke in jokes:
        # Create a unique identifier for each joke
        if "joke" in joke:
            unique_jokes.add(joke["joke"])
        else:
            unique_jokes.add((joke["setup"], joke["punchline"]))
    
    # With 15+ jokes and 50 calls, we should get at least 2 different jokes
    assert len(unique_jokes) > 1, "Multiple calls should return different jokes"


def test_joke_data_structure_consistency():
    """Test that all jokes in the collection have consistent data structure"""
    # Test that all jokes have required fields
    for joke in JOKES:
        # Every joke must be a dictionary
        assert isinstance(joke, dict), "Each joke should be a dictionary"
        
        # Every joke must have a category
        assert "category" in joke, f"Joke missing category: {joke}"
        assert isinstance(joke["category"], str), "Category should be a string"
        assert len(joke["category"]) > 0, "Category should not be empty"
        
        # Every joke must have either setup/punchline or joke field
        has_setup_punchline = "setup" in joke and "punchline" in joke
        has_joke = "joke" in joke
        assert has_setup_punchline or has_joke, f"Joke must have either setup/punchline or joke field: {joke}"
        
        # If it has setup, it must have punchline (and vice versa)
        if "setup" in joke:
            assert "punchline" in joke, f"Joke with setup must have punchline: {joke}"
            assert isinstance(joke["setup"], str), "Setup should be a string"
            assert len(joke["setup"]) > 0, "Setup should not be empty"
            
        if "punchline" in joke:
            assert "setup" in joke, f"Joke with punchline must have setup: {joke}"
            assert isinstance(joke["punchline"], str), "Punchline should be a string"
            assert len(joke["punchline"]) > 0, "Punchline should not be empty"
            
        # If it has a joke field, verify it's valid
        if "joke" in joke:
            assert isinstance(joke["joke"], str), "Joke should be a string"
            assert len(joke["joke"]) > 0, "Joke should not be empty"


def test_get_random_joke_returns_from_collection():
    """Test that get_random_joke() returns a joke from the JOKES collection"""
    joke = get_random_joke()
    assert joke in JOKES, "Returned joke should be from the JOKES collection"
