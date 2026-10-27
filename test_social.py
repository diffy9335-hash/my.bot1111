import pytest
from app import core, social

@pytest.fixture
def db(tmp_path,monkeypatch):
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'social.sqlite3'))
    core.init_db();social.init_social()
    core.get_user(101,'Player One');core.get_user(202,'Player Two')
    return None

def test_chat_history_and_public_profile(db):
    msg=social.send(101,'Привет, футбол!')
    result=social.messages()
    assert len(result)==1 and result[0]['id']==msg['id']
    assert result[0]['name']=='Player One'
    assert 'balance' not in social.public_profile(101)
    assert social.messages(after=msg['id'])==[]

def test_chat_rate_limit_and_length(db):
    social.send(101,'Первое')
    with pytest.raises(ValueError,match='5 секунд'): social.send(101,'Ещё одно')
    with pytest.raises(ValueError): social.send(202,'x'*351)
    with pytest.raises(ValueError): social.send(202,'  ')

def test_reports_and_moderation(db):
    mid=social.send(101,'Матч сегодня')['id']
    assert social.report(202,mid)['ok']
    assert len(social.moderation_queue())==1
    assert social.report(202,mid)['ok']  # duplicate report ignored
    assert social.moderation_queue()[0]['reports']==1
    social.mute_player(101,60)
    with pytest.raises(ValueError,match='недоступен'): social.send(101,'Проверка')
    social.remove_message(mid)
    assert social.messages()==[]
    assert social.moderation_queue()==[]
