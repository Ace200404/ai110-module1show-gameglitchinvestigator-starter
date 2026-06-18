# AI Interactions Log

---

## Agent Workflow (SF8)

**What task did you give the agent?**

I used Claude Code (Claude Sonnet 4.6) in agent mode inside VS Code. I described two problems:
1. "After pressing New Game, typing a number and clicking Submit does nothing — no hint, no attempt decrement."
2. "Implement a dict so a user can't enter the same number twice in a game round without wasting an attempt."

**What did the agent do?**

The agent read `app.py` and `logic_utils.py` autonomously, then:
- Identified that `st.session_state.status` was never reset to `"playing"` in the `new_game` handler, causing `st.stop()` to block the submit handler on every rerender after a win or loss
- Added `st.session_state.status = "playing"`, `st.session_state.guessed_numbers = {}`, and `st.session_state.history = []` to the `new_game` handler
- Added a `guessed_numbers` dict to session state initialization
- Moved the `st.session_state.attempts += 1` increment below a duplicate-check guard so repeated guesses never cost an attempt
- Added the duplicate number to `guessed_numbers` after each valid unique guess
- Added `guessed_numbers` to the Developer Debug Info panel
- Created `tests/test_app_behavior.py` with 8 Streamlit `AppTest`-based tests covering both fixes

**What did you have to verify or fix manually?**

One of the 8 generated tests (`test_new_game_resets_status_to_playing`) failed on the first run with a 3-second `AppTest` timeout. I read the traceback myself, confirmed the test logic was correct but the default timeout was too tight for a cold-start on my machine, and changed `.run()` to `.run(timeout=10)` on that one test. The fix to the app itself was never wrong.

---

## Test Generation (SF7)

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Submit after New Game from a lost game | "make testers for the restart fix" | `test_submit_works_after_new_game_from_lost` — seeds `status="lost"`, clicks New Game, then Submit, asserts `attempts > 0` | Yes (after timeout fix on a related test) | Directly confirms the `st.stop()` guard is no longer blocking the handler |
| Duplicate guess does not cost an attempt | "implement a dict so a user can't enter the same number twice" | `test_duplicate_guess_does_not_use_attempt` — seeds `guessed_numbers={42: "Too High"}` and `attempts=2`, submits 42, asserts `attempts == 2` | Yes | Proves the attempt increment was correctly moved below the duplicate check |
| Duplicate guess shows a warning | Same session | `test_duplicate_guess_shows_warning` — same setup, asserts a warning widget containing "42" is present | Yes | Confirms user feedback is shown so they know why no attempt was used |
| Fresh guess recorded in dict | Same session | `test_fresh_guess_recorded_in_dict` — seeds empty dict, submits 1, asserts `1 in guessed_numbers` | Yes | Confirms the dict is actually populated so future duplicate checks will work |
| String secret comparison (e.g. "9" vs "10") | Pre-existing tests in test_game_logic.py | `test_string_secret_too_low` / `test_string_secret_too_high` — call `check_guess(9, "10")` and `check_guess(20, "9")` | Yes | Catches the lexicographic sort bug where `"9" > "10"` would give the wrong outcome |

---

## Linting & Style (SF9)

> Not attempted.

---

## Model Comparison (SF11)

> Not attempted.
