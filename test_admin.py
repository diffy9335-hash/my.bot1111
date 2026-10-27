import pytest
from datetime import timedelta

def test_admin_ledger_and_limits(tmp_path,monkeypatch):
    from app import core
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'admin.sqlite3'))
    core.init_db();core.get_user(77,'Player')
    assert core.admin_adjust_balance(77,150,1,'Test grant')['balance']==1150
    assert core.admin_adjust_balance(77,-50,1,'Correction')['balance']==1100
    assert len(core.admin_recent_activity())==2
    assert core.admin_players()[0]['balance']==1100
    with pytest.raises(ValueError):core.admin_adjust_balance(77,-2000,1,'Too much')
    assert core.get_user(77)['balance']==1100

def test_admin_rejects_invalid_request(tmp_path,monkeypatch):
    from app import core
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'test.sqlite3'))
    core.init_db();core.get_user(1)
    for val in (0,100001,-100001):
        with pytest.raises(ValueError):core.admin_adjust_balance(1,val,5,'Test')
    with pytest.raises(ValueError):core.admin_adjust_balance(1,100,5,'')
