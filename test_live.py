import os
from datetime import timedelta
from app import core

def test_live_score_event_snapshots(tmp_path, monkeypatch):
    monkeypatch.setattr(core, 'DB_PATH', str(tmp_path/'live.sqlite3'))
    core.init_db()
    now=core.utcnow()
    with core.connect() as c:
        c.execute("INSERT INTO matches(id,league,home,away,kickoff,status,home_score,away_score,odd_h,odd_d,odd_a,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (123,'Test League','A','B',core.iso(now-timedelta(minutes=23)),'IN_PLAY',1,0,2.1,3.1,3.1,core.iso(now)))
        c.execute("INSERT INTO match_events(match_id,kind,home_score,away_score,occurred_at,source) VALUES(?,?,?,?,?,?)",(123,'score_changed',1,0,core.iso(now),'test snapshot'))
    data=core.get_live_center()
    assert len(data['matches'])==1
    assert data['matches'][0]['events'][0]['kind']=='score_changed'
    assert data['matches'][0]['fresh'] is True
    assert data['minute_is_estimate'] is True

def test_old_live_feed_marked_stale(tmp_path, monkeypatch):
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'old.sqlite3'))
    core.init_db()
    now=core.utcnow()
    with core.connect() as c:
        c.execute("INSERT INTO matches(id,league,home,away,kickoff,status,home_score,away_score,odd_h,odd_d,odd_a,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (2,'Test','A','B',core.iso(now-timedelta(minutes=20)),'IN_PLAY',0,1,2,3,4,core.iso(now-timedelta(minutes=5))))
    assert core.get_live_center()['matches'][0]['fresh'] is False
