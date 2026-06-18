import os
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")


# --- New Game restart fix ---

def test_new_game_resets_status_to_playing():
    """After losing, pressing New Game must flip status back to 'playing'."""
    at = AppTest.from_file(APP_PATH).run(timeout=10)
    at.session_state["status"] = "lost"
    at.button[1].click().run(timeout=10)
    assert at.session_state["status"] == "playing"


def test_new_game_resets_status_after_win():
    """After winning, pressing New Game must flip status back to 'playing'."""
    at = AppTest.from_file(APP_PATH).run()
    at.session_state["status"] = "won"
    at.button[1].click().run()
    assert at.session_state["status"] == "playing"


def test_new_game_clears_guessed_numbers():
    """New Game must wipe the guessed_numbers dict for the fresh round."""
    at = AppTest.from_file(APP_PATH).run()
    at.session_state["guessed_numbers"] = {5: "Too Low", 20: "Too High"}
    at.button[1].click().run()
    assert at.session_state["guessed_numbers"] == {}


def test_submit_works_after_new_game_from_lost():
    """Submit should be reachable (not blocked by st.stop) after restarting a lost game."""
    at = AppTest.from_file(APP_PATH).run()
    at.session_state["status"] = "lost"
    at.session_state["secret"] = 99
    # Restart
    at.button[1].click().run()
    # Now submit a guess in the new game
    at.text_input[0].set_value("1")
    at.button[0].click().run()
    # Attempt was processed — not still 0
    assert at.session_state["attempts"] > 0


# --- Duplicate number tracking ---

def test_duplicate_guess_does_not_use_attempt():
    """Re-submitting a number already guessed this round must not burn an attempt."""
    at = AppTest.from_file(APP_PATH).run()
    at.session_state["guessed_numbers"] = {42: "Too High"}
    at.session_state["attempts"] = 2
    at.text_input[0].set_value("42")
    at.button[0].click().run()
    assert at.session_state["attempts"] == 2


def test_duplicate_guess_shows_warning():
    """Re-submitting a duplicate should surface a warning message to the user."""
    at = AppTest.from_file(APP_PATH).run()
    at.session_state["guessed_numbers"] = {42: "Too High"}
    at.session_state["attempts"] = 2
    at.text_input[0].set_value("42")
    at.button[0].click().run()
    assert any("42" in w.value for w in at.warning)


def test_fresh_guess_increments_attempts():
    """A number not yet guessed this round must increment the attempt counter."""
    at = AppTest.from_file(APP_PATH).run()
    at.session_state["guessed_numbers"] = {}
    at.session_state["attempts"] = 0
    at.session_state["secret"] = 99
    at.text_input[0].set_value("1")
    at.button[0].click().run()
    assert at.session_state["attempts"] == 1


def test_fresh_guess_recorded_in_dict():
    """After a fresh guess, the number and its outcome appear in guessed_numbers."""
    at = AppTest.from_file(APP_PATH).run()
    at.session_state["guessed_numbers"] = {}
    at.session_state["attempts"] = 0
    at.session_state["secret"] = 99
    at.text_input[0].set_value("1")
    at.button[0].click().run()
    assert 1 in at.session_state["guessed_numbers"]
