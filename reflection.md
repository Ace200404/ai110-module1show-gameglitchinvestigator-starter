# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior         | Actual Behavior      | Console Output / Error |
|-------|---------------------------|----------------------|---------------------------|
|New game| should restart the game    doesn't restart        None
|attempts| should decrease attemps    stopes at 1 but         None
            by 1 until zero           allows one more attempt
|submit  | higher or lower            always says high        None
|inputing  inpuit a diffrent number   reduce attempts by 1    None
the same  
number|
|developer  just the value            [0:40,1:40]
debug shows a dict|


##  Bug Reproduction Logs
| Input       | Expected Behavior         | Actual Behavior      | Console Output / Error |
new attempt      restart the attmepts       nothing happens         None
show hint       higher or lower               noly says higher      None
attempts count    decreases count by 1      shows a message count   None
                  till we hit zero          1 'out of attempts       
---

## 2. How did you use AI as a teammate?

I used **Claude Code (Claude Sonnet 4.6)** running inside VS Code as my AI coding assistant throughout this project.

### Correct AI suggestion — restart bug root cause

**What the AI suggested:** When I described the symptom ("submit does nothing after pressing New Game"), the AI read the app code and pointed to a specific line: the `new_game` handler set `attempts = 0` and called `st.rerun()`, but never reset `st.session_state.status` back to `"playing"`. Because of that, after every win or loss the guard block `if st.session_state.status != "playing": ... st.stop()` fired on every rerender — the submit handler that comes after it was never reached.

**Was it correct?** Yes. The AI's diagnosis was exactly right. It also explained *why* the symptom only appeared after a game ended (not during the first game), which matched what I had observed.

**How I verified it:** I traced the execution order in `app.py` myself: the status guard is at line 90, and the submit handler starts at line 97. Because `st.stop()` exits the script immediately, anything below it is unreachable. Adding `st.session_state.status = "playing"` to the new-game handler fixed it, and the AppTest test `test_submit_works_after_new_game_from_lost` confirmed the submit handler now runs after a restart.

---

### Incorrect / misleading AI suggestion — test timeout

**What the AI suggested:** The AI wrote `test_new_game_resets_status_to_playing` using Streamlit's `AppTest` framework with the default `.run()` call (no timeout argument). On the first test run, this test failed with `RuntimeError: AppTest script run timed out after 3(s)`.

**Was it correct?** The test logic itself was correct — the assertion and the click sequence were right. But the AI did not account for the default 3-second timeout being too tight for the initial cold-start of an AppTest session on this machine. The failure looked like a broken fix when it was actually a timing issue.

**How I verified it:** I re-ran the tests a second time and saw 7/8 passing — the same test consistently timed out. I read the AppTest error traceback, which showed the timeout was on `.run()` not on the assertion. Changing `.run()` to `.run(timeout=10)` on that one test made all 8 pass. The fix to the app was never wrong; only the test needed a longer timeout.

---

## 3. Debugging and testing your fixes

### How I decided a bug was really fixed

For each bug I required two things to be true at the same time: (1) an automated pytest test exercising the exact scenario passed, and (2) I traced through the relevant code path by reading `app.py` to confirm the fix made logical sense, not just that the test happened to pass.

### Tests I ran

I created `tests/test_app_behavior.py` with 8 tests using Streamlit's `AppTest` framework, then ran:

```
python -m pytest tests/test_app_behavior.py -v
```

**First run — 7/8 passed.** The failure was `test_new_game_resets_status_to_playing` timing out (see section 2 above — the test logic was correct but needed a longer timeout).

**Second run after timeout fix — 8/8 passed.** Key tests and what they showed:

| Test | What it showed |
|---|---|
| `test_submit_works_after_new_game_from_lost` | Submit handler is reachable after restart — `st.stop()` no longer blocks it |
| `test_duplicate_guess_does_not_use_attempt` | Attempts counter stays at 2 when the same number is re-submitted |
| `test_duplicate_guess_shows_warning` | A warning containing the guessed number is shown to the user |
| `test_fresh_guess_increments_attempts` | A new number correctly costs one attempt |
| `test_fresh_guess_recorded_in_dict` | After a fresh guess, the number appears in `guessed_numbers` |

### How AI helped with tests

The AI wrote the entire `test_app_behavior.py` file. It chose `streamlit.testing.v1.AppTest` (Streamlit's built-in headless test runner) rather than mocking session state manually, which meant the tests exercise the real app script. I reviewed each test to confirm the widget indices (`button[0]` = Submit, `button[1]` = New Game) matched the actual button order in `app.py`, and that the session-state seeds made sense for each scenario.

---

## 4. What did you learn about Streamlit and state?

Every time a user interacts with a Streamlit widget — clicks a button, types in a text box — Streamlit re-runs the entire Python script from top to bottom, as if the page refreshed. Imagine it like pressing F5 on a webpage every single time you click anything. Because of this, any plain Python variable you set mid-script gets thrown away the moment the script reruns. `st.session_state` is the solution: it's a dictionary that Streamlit preserves across reruns, so values survive the "refresh." The core lesson from this project is that you have to be very deliberate about what goes into session state and, just as importantly, when you reset it. The restart bug was a perfect example — `status` was stored in session state, it changed to `"won"` or `"lost"` at the end of a game, and because the new-game handler never wrote `"playing"` back into it, the game was permanently stuck in a finished state even after clicking New Game.

---

## 5. Looking ahead: your developer habits

**Habit to reuse:** Always verify AI-generated tests by reading them line by line before trusting the pass/fail result. In this project, a test timed out and initially looked like a broken fix — but reading the traceback showed the problem was the test itself (a missing `timeout` argument), not the code under test. That habit of reading the failure message carefully rather than assuming "test failed = code is wrong" saved me from reverting a correct fix.

**What I would do differently:** Next time I work with AI on a debugging task, I would ask it to explain the execution flow *before* suggesting a fix — not just point at the line to change. In this project the AI correctly identified the fix, but I had to ask follow-up questions to understand *why* `st.stop()` caused the submit handler to be unreachable. Getting the explanation first would have made me faster at spotting similar patterns in the future.

**How this project changed my thinking:** AI-generated code looks confident and correct on the surface, but this project showed that it can contain subtle state-management bugs that only appear under specific sequences of user actions (like finishing a game and then restarting). I now treat AI-generated code the same way I would treat code from a new teammate — read it, understand it, and test the edge cases myself rather than assuming it works because it runs without crashing.
