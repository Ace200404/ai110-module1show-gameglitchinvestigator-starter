# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Purpose:** A number-guessing game where the player tries to identify a hidden secret number within a limited number of attempts. The difficulty setting controls the number range and attempt limit. After each guess the game gives a "Too High" or "Too Low" hint and tracks a running score.

**Bugs found:**

| # | Bug | Symptom |
|---|-----|---------|
| 1 | `status` never reset on New Game | After winning or losing, pressing New Game restarted the counter display but made Submit completely unresponsive — `st.stop()` blocked the handler on every rerun |
| 2 | No duplicate-guess protection | Typing the same number twice wasted an attempt with no feedback |
| 3 | Hint always said "Go HIGHER!" | `check_guess` had the Too High / Too Low messages swapped |
| 4 | String-vs-int comparison on even attempts | On even attempt numbers `secret` was cast to `str`, making numeric comparison unreliable (e.g. `"9" > "10"` lexicographically) |
| 5 | `attempts` initialised at 1, not 0 | The first guess was counted as attempt 2, skewing the attempt-limit display |

**Fixes applied:**

- `app.py` — added `st.session_state.status = "playing"` to the New Game handler so `st.stop()` is no longer triggered after a restart
- `app.py` — added `guessed_numbers` dict; duplicate submissions now show a warning and cost no attempt
- `logic_utils.py` — swapped the "Too High" / "Too Low" hint messages in `check_guess`
- `logic_utils.py` — `check_guess` now always converts `secret` to `int` before comparing, eliminating string-sort errors
- `tests/test_game_logic.py` — added edge-case tests for the hint messages and the string-secret comparison
- `tests/test_app_behavior.py` — added 8 AppTest-based tests covering the restart and duplicate-guess fixes

## 📸 Demo Walkthrough

*(Normal difficulty — secret number is 63, attempt limit is 8, range 1–100)*

1. **Game loads.** The sidebar shows "Range: 1 to 100" and "Attempts allowed: 8". The info bar reads "Attempts left: 8".
2. **User types `40` and clicks Submit.** Hint displays "📈 Go HIGHER!" — attempt counter drops to 7.
3. **User types `40` again (accidentally).** Game shows: *"You already guessed 40 this round (result: Too Low). Try a different number — no attempt used."* Attempts remain at 7.
4. **User types `75` and clicks Submit.** Hint shows "📉 Go LOWER!" — attempts left: 6.
5. **User types `60` and clicks Submit.** Hint shows "📈 Go HIGHER!" — attempts left: 5.
6. **User types `63` and clicks Submit.** Balloons appear, success banner reads *"You won! The secret was 63. Final score: 60"*.
7. **User clicks New Game.** Status resets to "playing", `guessed_numbers` clears, attempts resets to 0 — a fresh game starts immediately with Submit fully functional.

## 🧪 Test Results

```
$ python -m pytest tests/ -v
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.1.0, pluggy-1.6.0
rootdir: ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.11.0, langsmith-0.7.30
collecting ... collected 15 items

tests/test_app_behavior.py::test_new_game_resets_status_to_playing PASSED [  6%]
tests/test_app_behavior.py::test_new_game_resets_status_after_win PASSED [ 13%]
tests/test_app_behavior.py::test_new_game_clears_guessed_numbers PASSED  [ 20%]
tests/test_app_behavior.py::test_submit_works_after_new_game_from_lost PASSED [ 26%]
tests/test_app_behavior.py::test_duplicate_guess_does_not_use_attempt PASSED [ 33%]
tests/test_app_behavior.py::test_duplicate_guess_shows_warning PASSED    [ 40%]
tests/test_app_behavior.py::test_fresh_guess_increments_attempts PASSED  [ 46%]
tests/test_app_behavior.py::test_fresh_guess_recorded_in_dict PASSED     [ 53%]
tests/test_game_logic.py::test_winning_guess PASSED                      [ 60%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 66%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 73%]
tests/test_game_logic.py::test_too_high_hint_says_go_lower PASSED        [ 80%]
tests/test_game_logic.py::test_too_low_hint_says_go_higher PASSED        [ 86%]
tests/test_game_logic.py::test_string_secret_too_low PASSED              [ 93%]
tests/test_game_logic.py::test_string_secret_too_high PASSED             [100%]

============================= 15 passed in 1.18s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
