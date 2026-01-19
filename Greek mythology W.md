# Project Context: Greek mythology Wordle
** Greek mythology Wordle** is a guessing game based on the structure of Wordle, but the player has to guess a character from the entire Greek Mythology.
- **Goal:** provide a game interface with graphics
- **Tone:** The UI must be attractive and pastel-themed
- **Critical Requirement:** Data accuracy and speed are paramount.

# Tech Stack
- **GUI:** Streamlit (utilizing st.columns for the guess grid and st.sidebar for the "Bestiary" or collection of unlocked myths).
- **Data:** JSON or SQLite local database containing Greek deities, heroes, and creatures (including attributes like Parentage, Domain, and Roman Equivalent).
- **Logic:** Custom Python scoring engine to compare the player's guess against the "Hero of the Day" (matching categories like Gender, Species, and Olympic status).
- **Visualization:** plotly.graph_objects for a "Power Level" radar chart or a lineage map for the daily character (Dark mode: 'plotly_dark').
- **Testing:** pytest to ensure the daily reset logic functions across different time zones and to validate the attribute matching system

# Details
- **The Attributes:** Instead of "Sector" and "Industry," your columns in Streamlit will likely be: Category (God, Titan, Hero), Domain (Sea, War, Wisdom), Symbol (Trident, Owl, Thunderbolt), and Status (Olympian, Mortal, Chthonic).
The Comparison Engine: For attributes like "Domain," you can use "Partial Matches." For example, if the player guesses Apollo (Sun, Music, Archery) and the answer is Artemis (Moon, Hunt, Archery), your logic should highlight the match in "Archery."

The Asset Fetcher: Since there isn't a yfinance for Mount Olympus, you’ll want to store your data in a structured mythology.json file. This allows the game to run fast and offline.