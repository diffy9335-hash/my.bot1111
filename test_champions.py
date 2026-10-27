from datetime import datetime, timezone
import pytest
from app import core, seasons

@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(core, 'DB_PATH', str(tmp_path/'champ.sqlite3'))
    core.init_db(); seasons.init_seasons()
    for uid in (11,22,33): core.get_user(uid,str(uid))

def put(uid,status,date):
    with core.connect() as c:
        c.execute('INSERT INTO slips(user_id,stake,combined_odd,status,created_at) VALUES(?,?,?,?,?)',(uid,100,2.0,status,date))

def test_only_finished_season_champion_gets_permanent_badge(db):
    date='2026-11-01T10:00:00+00:00'
    put(11,'won',date); put(22,'cashed_out',date)
    before=seasons.champion_badges([11,22],datetime(2026,11,3,tzinfo=timezone.utc))
    assert before == {}
    after=seasons.champion_badges([11,22],datetime(2027,1,25,tzinfo=timezone.utc))
    assert after == {11:1}
    put(22,'won',date)
    assert seasons.champion_badges([11,22],datetime(2027,1,26,tzinfo=timezone.utc)) == {11:1}

def test_no_badge_for_empty_season(db):
    assert seasons.champion_badges(now=datetime(2027,1,25,tzinfo=timezone.utc)) == {}

def test_multiple_championships_same_user(db):
    put(11,'won','2026-11-01T00:00:00+00:00')
    put(11,'won','2027-02-01T00:00:00+00:00')
    badges=seasons.champion_badges(now=datetime(2027,4,26,tzinfo=timezone.utc))
    assert badges[11]==2
