import pytest
from datetime import datetime,timezone,timedelta
from app import core, seasons, community

@pytest.fixture
def db(tmp_path,monkeypatch):
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'community.sqlite3'))
    core.init_db(); seasons.init_seasons();community.init_community()
    core.get_user(101,'Первый');core.get_user(202,'Второй')
    core.seed_demo()

def test_feed_follow_and_reactions(db):
    match=next(m for m in core.get_matches() if m['status']=='SCHEDULED')
    result=community.create_post(101,match['id'],'H','Полагаю, хозяева победят')
    post_id=result['id']
    assert len(community.feed(202))==1
    assert community.feed(202,'following')==[]
    seasons.follow(202,101)
    assert len(community.feed(202,'following'))==1
    community.like(202,post_id);community.like(202,post_id)
    assert community.feed(202)[0]['likes']==1
    with pytest.raises(ValueError): community.create_post(101,match['id'],'H','Второй прогноз')
    with pytest.raises(ValueError): community.report_post(101,post_id)
    assert community.report_post(202,post_id)['ok']
    assert len(community.reports())==1
    community.remove_post(post_id)
    assert community.feed(202)==[]

def test_notification_owner_and_deduplication(db):
    community.notify(101,'season','Сезон начался','season1')
    community.notify(101,'season','Сезон начался','season1')
    notes=community.get_notifications(101)
    assert len(notes)==1
    assert community.get_notifications(202)==[]
    with pytest.raises(ValueError):community.mark_read(202,notes[0]['id'])
    assert community.mark_read(101,notes[0]['id'])['ok']

def test_snapshot_and_personal_rank(db):
    now=datetime(2026,11,5,12,tzinfo=timezone.utc)
    assert community.save_daily_snapshot(now)==2
    assert community.save_daily_snapshot(now)==2
    d=community.dashboard(101,now=now+timedelta(days=1))
    assert d['remaining_days']>0
    assert d['previous_rank']==1
    assert d['rank_change']==0

def test_audit_only_flags_no_penalty(db):
    now=datetime(2026,11,3,12,tzinfo=timezone.utc)
    with core.connect() as c:
        c.executemany('INSERT INTO slips(user_id,stake,combined_odd,status,created_at) VALUES(?,?,?,?,?)',
                      [(101,10,2,'lost',now.isoformat()) for _ in range(151)])
    assert community.ranking_audit(now)==1
    assert community.ranking_audit(now)==1
    assert len(community.audit_queue())==1
    assert core.get_user(101,'Первый')['balance']==1000

def test_maintenance_idempotent(db):
    community.community_maintenance()
    n=len(community.get_notifications(101))
    community.community_maintenance()
    assert len(community.get_notifications(101))==n
