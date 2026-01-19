
import streamlit as st
import json
import random
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# --- Page Config & Styling ---
st.set_page_config(
    page_title="Greek Mythology Wordle",
    page_icon="🏛️",
    layout="wide"
)

# Using a pastel theme
PASTEL_GREEN = "#BEEEB8"
PASTEL_YELLOW = "#FDFD96"
PASTEL_RED = "#FFB6B3"
BACKGROUND_COLOR = "#FAF9F6" # Light Cream

st.markdown(f"""
<style>
    body, .stApp, h1, label {{
        color: #212121 !important; /* Force dark text on body, app, h1, and labels */
    }}
    .stApp {{
        background-color: {BACKGROUND_COLOR};
    }}
    .st-emotion-cache-1r4qj8v {{ /* Main content area */
        background-color: white;
        border-radius: 10px;
        padding: 2rem;
    }}
    /* --- Final Button Styling --- */
    /* Base style for all buttons */
    .stButton>button {{
        border: 1px solid #212121 !important;
        background: white !important;
        color: #212121 !important;
        border-radius: 5px;
    }}
    /* Style for button on hover to prevent theme override */
    .stButton>button:hover {{
        background: #f0f0f0 !important; /* Light grey on hover */
        color: #212121 !important;
    }}
    /* Style for button on click to prevent theme override */
    .stButton>button:active {{
        background: #e0e0e0 !important; /* Darker grey on click */
        color: #212121 !important;
        border-color: #212121 !important;
    }}
    /* Target the selectbox to ensure its background is white and text is dark */
    div[data-baseweb="select"] > div {{
        background-color: white !important;
        color: #212121 !important;
    }}
</style>
""", unsafe_allow_html=True)


# --- Data Loading ---
@st.cache_data
def load_mythology_data():
    """Loads mythology data from the JSON file."""
    try:
        with open("mythology.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: mythology.json file not found. Please make sure the data file is in the correct directory.")
        return []

def get_character_by_name(name, data):
    """Fetches a character's full data by their name."""
    for char in data:
        if char["name"].lower() == name.lower():
            return char
    return None

# --- Game Logic ---
def get_hero_of_the_day(data, new_game=False):
    """
    Selects the hero of the day. If new_game is True, picks a new random one,
    otherwise uses the date.
    """
    if not data:
        return None, None

    if new_game:
        # For "Play Again", just pick a random one
        hero = random.choice(data)
    else:
        # Daily hero
        day_of_year = datetime.now().timetuple().tm_yday
        random.seed(day_of_year)
        hero = random.choice(data)

    all_names = sorted([char["name"] for char in data])
    return hero, all_names


def initialize_game_state(all_names, force_reset=False):
    """Initializes or resets the session state for a new game."""
    if "hero_of_the_day" not in st.session_state or force_reset:
        if force_reset:
             st.session_state.hero_of_the_day, _ = get_hero_of_the_day(load_mythology_data(), new_game=True)
        else:
            st.session_state.hero_of_the_day, _ = get_hero_of_the_day(load_mythology_data())

        st.session_state.guesses = []
        st.session_state.game_over = False
        st.session_state.all_names = all_names
        if 'bestiary' not in st.session_state or force_reset:
            st.session_state.bestiary = set()


# --- UI Components ---
def display_header():
    """Displays the main header and game instructions."""
    st.title("🏛️ Greek Mythology Wordle 🏛️")
    st.markdown(
        """
        Guess the **Character of the Day** from Greek Mythology! You have 6 tries.
        After each guess, the tiles will change color to show how close your guess was.
        """
    )
    st.markdown("---")


def display_guess_input(all_names):
    """Displays the input form for the user's guess."""
    if not st.session_state.game_over:
        with st.form(key="guess_form", clear_on_submit=True):
            guess_name = st.selectbox("Select your character:", options=[""] + all_names, key="guess_input")
            submit_button = st.form_submit_button(label="Make a Guess")

        if submit_button and guess_name:
            process_guess(guess_name)
            st.rerun()

def process_guess(guess_name):
    """Processes the user's guess and updates the game state."""
    myth_data = load_mythology_data()
    guess_char = get_character_by_name(guess_name, myth_data)
    hero_of_the_day = st.session_state.hero_of_the_day

    if not guess_char:
        st.warning("Invalid character name. Please choose from the list.")
        return

    st.session_state.guesses.append(guess_char)
    st.session_state.bestiary.add(guess_char["name"])

    if guess_char["name"].lower() == hero_of_the_day["name"].lower():
        st.session_state.game_over = True
        st.balloons()
        st.success(f"**Well done! The character was {hero_of_the_day['name']}!**")
    elif len(st.session_state.guesses) >= 6:
        st.session_state.game_over = True
        st.error(f"**Out of guesses!** The character was **{st.session_state.hero_of_the_day['name']}**.")

def get_color_for_comparison(guess_attr, correct_attr, partial_match_allowed=False):
    """Determines the background color based on attribute comparison."""
    guess_list = guess_attr if isinstance(guess_attr, list) else [guess_attr]
    correct_list = correct_attr if isinstance(correct_attr, list) else [correct_attr]

    if sorted(guess_list) == sorted(correct_list):
        return PASTEL_GREEN
    if partial_match_allowed and any(item in correct_list for item in guess_list):
        return PASTEL_YELLOW
    return PASTEL_RED

def display_guesses_grid():
    """Displays the grid of past guesses with color-coded feedback."""
    if not st.session_state.guesses:
        st.info("Make your first guess to begin!")
        return

    hero_of_the_day = st.session_state.hero_of_the_day
    headers = ["Name", "Gender", "Category", "Status", "Domain", "Symbol", "Roman Equivalent"]

    # Header row
    cols = st.columns(len(headers))
    for col, header in zip(cols, headers):
        col.markdown(f"<div style='text-align: center; font-weight: bold;'>{header}</div>", unsafe_allow_html=True)

    # Guesses
    for guess in reversed(st.session_state.guesses):
        cols = st.columns(len(headers))
        attributes = {
            "Name": guess["name"], "Gender": guess["gender"], "Category": guess["category"],
            "Status": guess["status"], "Domain": guess["domain"], "Symbol": guess["symbol"],
            "Roman Equivalent": guess.get("roman_equivalent", "N/A")
        }
        correct_attributes = {
            "Name": hero_of_the_day["name"], "Gender": hero_of_the_day["gender"], "Category": hero_of_the_day["category"],
            "Status": hero_of_the_day["status"], "Domain": hero_of_the_day["domain"], "Symbol": hero_of_the_day["symbol"],
            "Roman Equivalent": hero_of_the_day.get("roman_equivalent", "N/A")
        }

        for i, header in enumerate(headers):
            is_partial = header in ["Domain", "Symbol"]
            color = get_color_for_comparison(attributes[header], correct_attributes[header], partial_match_allowed=is_partial)
            display_val = ", ".join(attributes[header]) if isinstance(attributes[header], list) else attributes[header]
            cols[i].markdown(
                f"""
                <div style="background-color: {color}; color: #212121; padding: 10px; border-radius: 5px; text-align: center; height: 100%; margin-top: 5px;">
                    {display_val}
                </div>
                """, unsafe_allow_html=True
            )
    st.markdown("---")

def display_bestiary():
    """Displays the collection of unlocked characters in the sidebar."""
    st.sidebar.title("🏺 Bestiary 🏺")
    st.sidebar.info("Characters you have guessed appear here.")
    if st.session_state.bestiary:
        for char_name in sorted(list(st.session_state.bestiary)):
            with st.sidebar.expander(char_name):
                char_data = get_character_by_name(char_name, load_mythology_data())
                if char_data:
                    st.markdown(f"**Category:** {char_data['category']}")
                    st.markdown(f"**Domain:** {', '.join(char_data['domain'])}")
                    st.markdown(f"**Status:** {char_data['status']}")

# --- Visualization ---
def create_power_level_chart(character):
    """Creates a Plotly radar chart for a character's 'power levels'."""
    # Arbitrary stats based on attributes
    roman_equivalent = character.get('roman_equivalent') or ''
    stats = {
        'Strength': len(character.get('parentage', '')) % 10 + 1,
        'Wisdom': len(character.get('domain', [])) * 2,
        'Influence': 10 if character['status'] == 'Olympian' else (5 if character['category'] == 'God' else 3),
        'Combat': len(character.get('symbol', [])) * 2,
        'Mystery': len(roman_equivalent) % 5 + 1
    }
    categories = list(stats.keys())
    values = list(stats.values())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], # Close the loop
        theta=categories + [categories[0]],
        fill='toself',
        name=character['name'],
        line=dict(color='#A7C7E7') # Pastel Blue
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10]),
            bgcolor="#F9F9F9"
        ),
        showlegend=False,
        title=f"Power Chart: {character['name']}",
        template='plotly_dark' if st.checkbox("Dark Mode Chart", False, key="dark_mode") else 'seaborn',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# --- Main Game ---
def main():
    """Main function to run the game."""
    myth_data = load_mythology_data()
    if not myth_data: return

    _, all_names = get_hero_of_the_day(myth_data)
    initialize_game_state(all_names)

    # Main layout
    col1, col2 = st.columns([2, 1])

    with col1:
        display_header()
        display_guess_input(all_names)
        display_guesses_grid()

        if st.session_state.game_over:
            hero = st.session_state.hero_of_the_day
            st.markdown("---")
            st.subheader(f"Stat Chart for {hero['name']}")
            st.plotly_chart(create_power_level_chart(hero), use_container_width=True)

            if st.button("Play Again?"):
                initialize_game_state(all_names, force_reset=True)
                st.rerun()

    with col2:
        # Placeholder for future content or can be merged
        # For now, Bestiary stays in the sidebar
        pass
    
    display_bestiary()

if __name__ == "__main__":
    main()
