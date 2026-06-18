from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Tests targeting the two bugs fixed in check_guess ---

def test_too_high_hint_says_go_lower():
    # Bug: hint said "Go HIGHER!" when guess was above the secret.
    assert check_guess(60, 50) == ("Too High", "📉 Go LOWER!")

def test_too_low_hint_says_go_higher():
    # Bug: hint said "Go LOWER!" when guess was below the secret.
    assert check_guess(40, 50) == ("Too Low", "📈 Go HIGHER!")

def test_string_secret_too_low():
    # Bug: "9" > "10" lexicographically, so check_guess(9, "10") returned "Too High".
    outcome, _ = check_guess(9, "10")
    assert outcome == "Too Low"

def test_string_secret_too_high():
    # Bug: "20" < "9" lexicographically, so check_guess(20, "9") returned "Too Low".
    outcome, _ = check_guess(20, "9")
    assert outcome == "Too High"
