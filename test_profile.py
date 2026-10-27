import importlib

def test_profile_is_scoped_and_empty_counts(tmp_path, monkeypatch):
    monkeypatch.setenv('DB_PATH',str(tmp_path/'profile.sqlite'))
    import app.core as core
    importlib.reload(core)
    core.init_db()
    core.get_user(111,'Алексей')
    core.get_user(222,'Другой')
    result=core.profile_summary(111)
    assert result['user']['id']==111
    assert result['user']['name']=='Алексей'
    assert result['stats']['win_rate']==0
    assert result['stats']['total']==0
    assert result['transactions']==[]
    assert 'Другой' not in str(result)
