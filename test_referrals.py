import os
from datetime import date, timedelta
import pytest
from app import core
from app.referrals import init_referrals, enroll, record_visit, summary, referral_xp, parse_code
from app.progression import init_progression, summary as progress

@pytest.fixture(autouse=True)
def isolate(tmp_path,monkeypatch):
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'test.sqlite3'))
    core.init_db();init_referrals();init_progression()


def test_new_member_only_once():
    core.get_user(100,'A')
    assert enroll(200,'ref_100','B')
    assert not enroll(200,'ref_100')
    assert not enroll(200,'ref_999')
    assert not enroll(100,'ref_100')
    assert summary(100)['invited']==1
    assert summary(100)['qualified']==0


def test_existing_user_not_eligible():
    core.get_user(100,'A');core.get_user(200,'B')
    assert not enroll(200,'ref_100')
    assert summary(100)['invited']==0


def test_day_after_rewards_exactly_once():
    core.get_user(100,'A');enroll(200,'ref_100','B')
    assert not record_visit(200)
    with core.connect() as c:
        c.execute('UPDATE referrals SET joined_day=? WHERE invitee_id=?',((date.today()-timedelta(days=1)).isoformat(),200))
    assert record_visit(200)
    assert not record_visit(200)
    assert referral_xp(100)==50 and referral_xp(200)==25
    assert progress(100)['xp']==50 and progress(200)['xp']==25
    assert summary(100)['qualified']==1


def test_bad_codes_and_missing_inviter():
    assert all(parse_code(x) is None for x in ['ref_-1','ref_1abc','ref_0','123','ref_９','ref_'+'1'*30])
    assert not enroll(33,'ref_123')
    assert not record_visit(33)


def test_link(monkeypatch):
    core.get_user(100,'A')
    monkeypatch.setenv('BOT_USERNAME','FootballArenaRobot')
    assert summary(100)['invite_link']=='https://t.me/FootballArenaRobot?start=ref_100'
