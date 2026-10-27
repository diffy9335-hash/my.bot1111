from app.game_odds import game_odds

def test_game_prices_stable_and_not_all_identical():
    first = game_odds("Arsenal FC", "Chelsea FC")
    assert first == game_odds("Arsenal FC", "Chelsea FC")
    assert first != game_odds("Bayern Munich", "Mainz 05")
    assert all(1.06 <= value <= 15 for value in first)

def test_swapping_clubs_changes_home_win_probability():
    a = game_odds("Manchester City", "Everton")
    b = game_odds("Everton", "Manchester City")
    assert a[0] < b[0]
