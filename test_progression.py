import pytest
from app import core, progression

@pytest.fixture
def database(tmp_path, monkeypatch):
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'test.db'))
    core.init_db(); progression.init_progression()
    core.get_user(123,'Игрок')
    return 123

def test_quest_once_and_xp(database):
    before=progression.summary(database)
    assert before['level']==1 and before['xp']==0
    after=progression.claim(database,'visit')
    assert after['xp']==15
    with pytest.raises(ValueError,match='уже получена'):
        progression.claim(database,'visit')
    assert core.get_user(database)['balance']==1000

def test_unfinished_quests(database):
    with pytest.raises(ValueError,match='не выполнено'):
        progression.claim(database,'prediction')
    core.daily_bonus(database)
    after=progression.claim(database,'bonus')
    assert after['xp']==20
    assert core.get_user(database)['balance']==1200

def test_achievements_from_real_slips(database):
    assert not next(a for a in progression.summary(database)['achievements'] if a['id']=='first')['unlocked']
    core.seed_demo()
    match=next(m for m in core.get_matches() if m['id']==-1)
    core.place_slip(database,10,[{'match_id':match['id'],'pick':'H'}])
    data=progression.summary(database)
    assert data['xp']==20
    assert next(a for a in data['achievements'] if a['id']=='first')['unlocked']
