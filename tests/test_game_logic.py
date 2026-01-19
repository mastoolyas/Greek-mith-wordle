
import sys
import os
from datetime import datetime
from unittest.mock import patch
import pytest

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import (
    get_color_for_comparison,
    get_hero_of_the_day,
    load_mythology_data,
    create_power_level_chart, # Import the function to be tested
    PASTEL_GREEN,
    PASTEL_YELLOW,
    PASTEL_RED
)

# --- Test Data ---
MOCK_DATA = [
    {
        "name": "Zeus", "gender": "Male", "category": "God", "status": "Olympian",
        "domain": ["Sky", "Thunder"], "symbol": ["Thunderbolt"], "roman_equivalent": "Jupiter", "parentage": "Cronus and Rhea"
    },
    {
        "name": "Hera", "gender": "Female", "category": "God", "status": "Olympian",
        "domain": ["Marriage", "Women"], "symbol": ["Peacock"], "roman_equivalent": "Juno", "parentage": "Cronus and Rhea"
    },
    {
        "name": "Apollo", "gender": "Male", "category": "God", "status": "Olympian",
        "domain": ["Music", "Archery"], "symbol": ["Lyre", "Bow"], "roman_equivalent": "Apollo", "parentage": "Zeus and Leto"
    },
    {
        "name": "Artemis", "gender": "Female", "category": "God", "status": "Olympian",
        "domain": ["Hunt", "Archery"], "symbol": ["Bow", "Deer"], "roman_equivalent": "Diana", "parentage": "Zeus and Leto"
    },
    {
        "name": "Perseus", "category": "Hero", "domain": ["Quest"], "symbol": ["Medusa's Head"],
        "status": "Mortal", "gender": "Male", "roman_equivalent": None, "parentage": "Zeus and Danae"
    }
]

# --- Tests for Attribute Matching ---

def test_exact_match():
    """Tests exact matches for attributes."""
    assert get_color_for_comparison("Zeus", "Zeus") == PASTEL_GREEN
    assert get_color_for_comparison(["Sky", "Thunder"], ["Sky", "Thunder"]) == PASTEL_GREEN
    assert get_color_for_comparison("Male", "Male") == PASTEL_GREEN

def test_no_match():
    """Tests complete mismatches for attributes."""
    assert get_color_for_comparison("Zeus", "Hera") == PASTEL_RED
    assert get_color_for_comparison(["Sky"], ["Marriage"]) == PASTEL_RED
    assert get_color_for_comparison("Male", "Female") == PASTEL_RED

def test_partial_match_allowed():
    """Tests partial matches where the flag is enabled."""
    assert get_color_for_comparison(["Music", "Archery"], ["Hunt", "Archery"], partial_match_allowed=True) == PASTEL_YELLOW
    assert get_color_for_comparison(["Bow"], ["Bow", "Deer"], partial_match_allowed=True) == PASTEL_YELLOW

def test_partial_match_disallowed():
    """Tests that partial matches are treated as incorrect when the flag is disabled."""
    assert get_color_for_comparison(["Music", "Archery"], ["Hunt", "Archery"], partial_match_allowed=False) == PASTEL_RED

def test_case_insensitivity_should_be_handled_by_logic_not_color():
    """
    This test clarifies that the get_color_for_comparison function itself is case-sensitive,
    and any case-insensitivity should be handled before calling it.
    """
    assert get_color_for_comparison("zeus", "Zeus") == PASTEL_RED

# --- Tests for Daily Reset Logic ---

@patch('app.datetime')
def test_hero_of_the_day_is_consistent_for_same_day(mock_datetime):
    """Tests that the hero of the day is the same when called on the same date."""
    mock_datetime.now.return_value = datetime(2023, 1, 1, 10, 0, 0)
    hero1, _ = get_hero_of_the_day(MOCK_DATA)
    mock_datetime.now.return_value = datetime(2023, 1, 1, 14, 0, 0)
    hero2, _ = get_hero_of_the_day(MOCK_DATA)
    assert hero1 is not None
    assert hero1["name"] == hero2["name"]

@patch('app.datetime')
def test_hero_of_the_day_changes_for_different_days(mock_datetime):
    """Tests that the hero of the day changes across different dates."""
    mock_datetime.now.return_value = datetime(2023, 1, 1)
    hero1, _ = get_hero_of_the_day(MOCK_DATA)
    mock_datetime.now.return_value = datetime(2023, 1, 2)
    hero2, _ = get_hero_of_the_day(MOCK_DATA)
    assert hero1 is not None
    assert hero2 is not None

    import random
    day1_seed = datetime(2023, 1, 1).timetuple().tm_yday
    random.seed(day1_seed)
    seeded_hero1 = random.choice(MOCK_DATA)
    day2_seed = datetime(2023, 1, 2).timetuple().tm_yday
    random.seed(day2_seed)
    seeded_hero2 = random.choice(MOCK_DATA)

    assert seeded_hero1['name'] == hero1['name']
    assert seeded_hero2['name'] == hero2['name']
    assert day1_seed != day2_seed


# --- Test for Data Loading ---

def test_data_loading():
    """Simple test to ensure data loads into a list of dicts."""
    data = load_mythology_data()
    assert isinstance(data, list)
    assert len(data) > 0
    assert isinstance(data[0], dict)
    assert "name" in data[0]

def test_play_again_logic():
    """Tests that the 'Play Again' logic can select a new random hero."""
    hero1, _ = get_hero_of_the_day(MOCK_DATA, new_game=True)
    hero2, _ = get_hero_of_the_day(MOCK_DATA, new_game=True)
    assert hero1 is not None
    assert hero2 is not None

# --- Test for Visualization Logic ---

def test_power_chart_with_none_roman_equivalent():
    """
    Tests that the chart generation does not fail when a character
    has a `None` value for `roman_equivalent`.
    """
    character_with_none = next((c for c in MOCK_DATA if c["name"] == "Perseus"), None)
    assert character_with_none is not None
    
    try:
        # Before the fix, this would raise a TypeError
        fig = create_power_level_chart(character_with_none)
        assert fig is not None # Check that a figure is actually returned
    except TypeError:
        pytest.fail("create_power_level_chart() raised TypeError unexpectedly with None roman_equivalent.")

