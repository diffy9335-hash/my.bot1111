import importlib
from datetime import timedelta

def test_balance_daily_lifetime_private(tmp_path,monkeypatch):
    monkeypatch.setenv('DB_PATH',str(tmp_path/'wallet.sqlite3'))
    import app.core as core
    importlib.reload(core)
    core.init_db()
    core.get_user(1,'Первый')
    core.get_user(2,'Второй')
    now=core.utcnow()
    with core.connect() as c:
        for i,(uid,amt,when) in enumerate([(1,-100,now),(1,250,now),(1,50,now-timedelta(days=1)),(2,999,now)]):
            c.execute('INSERT INTO ledger(user_id,amount,reason,ref,created_at) VALUES(?,?,?,?,?)',(uid,amt,'Тест',f'entry{i}',core.iso(when)))
        c.execute('UPDATE users SET balance=1200 WHERE id=1')
    h=core.balance_history(1,7)
    assert h['today']['received']==250 and h['today']['spent']==100 and h['today']['net']==150
    assert h['lifetime']['received']==300 and h['lifetime']['spent']==100
    assert h['lifetime']['net']==200 and h['lifetime']['starting_balance']==1000
    assert h['daily'][1]['net']==50 and len(h['daily'])==7
    assert all(r['received']!=999 for r in h['daily'])

def test_history_validates_period(tmp_path,monkeypatch):
    monkeypatch.setenv('DB_PATH',str(tmp_path/'wallet2.sqlite3'))
    import app.core as core
    importlib.reload(core)
    core.init_db();core.get_user(3)
    try: core.balance_history(3,999)
    except ValueError: pass
    else: assert False
    assert core.balance_history(3)['lifetime']['net']==0
