import pytest
from datetime import datetime,timezone,timedelta
from app import core, seasons

@pytest.fixture
def db(tmp_path,monkeypatch):
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'season.sqlite3'))
    core.init_db();seasons.init_seasons()
    for uid in (11,22,33):core.get_user(uid,str(uid))
    return None

def test_windows_90_days():
    _,start,end=seasons.season_window(datetime(2026,10,26,tzinfo=timezone.utc))
    assert (end-start).days==90
    number,nextstart,_=seasons.season_window(end)
    assert number==2 and nextstart==end

def test_subscribe_once_and_unsubscribe(db):
    assert seasons.follow(11,22)['followers']==1
    assert seasons.follow(11,22)['followers']==1
    assert seasons.follow_stats(22,11)['subscribed']
    assert len(seasons.subscriptions(11))==1
    assert seasons.unfollow(11,22)['followers']==0
    assert seasons.unfollow(11,22)['followers']==0
    with pytest.raises(ValueError):seasons.follow(11,11)
    with pytest.raises(ValueError):seasons.follow(11,999)

def test_ranking_personal_place_when_outside_top(db):
    now=datetime(2026,11,1,tzinfo=timezone.utc)
    with core.connect() as c:
        for uid,status in [(11,'won'),(22,'cashed_out'),(33,'lost')]:
            c.execute('INSERT INTO slips(user_id,stake,combined_odd,status,created_at) VALUES(?,?,?,?,?)',
                      (uid,10,2,status,now.isoformat(timespec='seconds')))
    r=seasons.standings(33,limit=1,now=now)
    assert r['top'][0]['id']==11 and r['top'][0]['points']==3
    assert r['me']['rank']==3 and r['me']['points']==0
    assert len(r['top'])==1

def test_old_season_does_not_count(db):
    now=datetime(2027,2,1,tzinfo=timezone.utc)
    with core.connect() as c:
        c.execute('INSERT INTO slips(user_id,stake,combined_odd,status,created_at) VALUES(?,?,?,?,?)',
                  (11,10,2,'won','2026-11-01T00:00:00+00:00'))
    assert seasons.standings(11,now=now)['me']['points']==0
