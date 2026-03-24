import pytest
from joke_service import get_random_joke, JOKES


def test_get_random_joke_returns_dict():
    """Test that get_random_joke returns a dictionary"""
    joke = get_random_joke()
    assert isinstance(joke, dict)


def test_joke_has_category():
    """Test that every joke has a category"""
    joke = get_random_joke()
    assert "category" in joke
    assert joke["category"] in ["programming", "dad", "general"]


def test_joke_has_required_fields():
    """Test that joke has either setup/punchline or joke field"""
    joke = get_random_joke()
    has_setup_punchline = "setup" in joke and "punchline" in joke
    has_joke = "joke" in joke
    assert has_setup_punchline or has_joke


def test_jokes_collection_has_minimum_jokes():
    """Test that there are at least 10 jokes in the collection"""
    assert len(JOKES) >= 10


def test_jokes_collection_has_various_categories():
    """Test that jokes collection includes various categories"""
    categories = {joke["category"] for joke in JOKES}
    assert "programming" in categories
    assert "dad" in categories
    assert "general" in categories


def test_all_jokes_have_category():
    """Test that all jokes in the collection have a category"""
    for joke in JOKES:
        assert "category" in joke


def test_all_jokes_have_content():
    """Test that all jokes have either setup/punchline or joke field"""
    for joke in JOKES:
        has_setup_punchline = "setup" in joke and "punchline" in joke
        has_joke = "joke" in joke
        assert has_setup_punchline or has_joke


def test_setup_punchline_jokes_have_both_fields():
    """Test that jokes with setup also have punchline and vice versa"""
    for joke in JOKES:
        if "setup" in joke:
            assert "punchline" in joke
        if "punchline" in joke:
            assert "setup" in joke


def test_joke_fields_are_non_empty_strings():
    """Test that all joke text fields are non-empty strings"""
    for joke in JOKES:
        if "setup" in joke:
            assert isinstance(joke["setup"], str)
            assert len(joke["setup"]) > 0
        if "punchline" in joke:
            assert isinstance(joke["punchline"], str)
            assert len(joke["punchline"]) > 0
        if "joke" in joke:
            assert isinstance(joke["joke"], str)
            assert len(joke["joke"]) > 0


def test_get_random_joke_returns_from_collection():
    """Test that get_random_joke returns a joke from the JOKES collection"""
    joke = get_random_joke()
    assert joke in JOKES


def test_get_random_joke_can_return_different_jokes():
    """Test that get_random_joke can return different jokes (randomness check)"""
    jokes_returned = {id(get_random_joke()) for _ in range(50)}
    # With 15 jokes and 50 calls, we should get at least 2 different jokes
    assert len(jokes_returned) > 1


def test_programming_jokes_exist():
    """Test that there are programming jokes in the collection"""
    programming_jokes = [j for j in JOKES if j["category"] == "programming"]
    assert len(programming_jokes) > 0


def test_dad_jokes_exist():
    """Test that there are dad jokes in the collection"""
    dad_jokes = [j for j in JOKES if j["category"] == "dad"]
    assert len(dad_jokes) > 0


def test_general_jokes_exist():
    """Test that there are general jokes in the collection"""
    general_jokes = [j for j in JOKES if j["category"] == "general"]
    assert len(general_jokes) > 0
