from datetime import timedelta
import pytest

def setup_game(tmp_path,monkeypatch):
    import app.core as core
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'cashout.sqlite'))
    core.init_db(); core.get_user(45)
    with core.connect() as c:
        c.execute('INSERT INTO matches(id,league,home,away,kickoff,status,home_score,away_score,odd_h,odd_d,odd_a,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(11,'Test','Home','Away',core.iso(core.utcnow()+timedelta(hours=2)),'SCHEDULED',None,None,2.0,3.2,3.6,core.iso(core.utcnow())))
    return core

def test_single_cashout_exactly_once(tmp_path,monkeypatch):
    core=setup_game(tmp_path,monkeypatch)
    slip=core.place_slip(45,100,[{'match_id':11,'pick':'H'}])
    with core.connect() as c:
        c.execute('UPDATE matches SET status=?,kickoff=?,home_score=?,away_score=?,updated_at=? WHERE id=11',('IN_PLAY',core.iso(core.utcnow()-timedelta(minutes=60)),1,0,core.iso(core.utcnow())))
    q=core.cashout_quote(45,slip['id']); assert q['amount']>0
    assert core.execute_cashout(45,slip['id'],q['amount'])['status']=='cashed_out'
    assert core.get_user(45)['balance']==900+q['amount']
    with pytest.raises(ValueError): core.execute_cashout(45,slip['id'],q['amount'])
    with core.connect() as c: c.execute("UPDATE matches SET status='FINISHED',home_score=2,away_score=0 WHERE id=11")
    assert core.settle()==0
    assert core.get_user(45)['balance']==900+q['amount']

def test_express_no_cashout(tmp_path,monkeypatch):
    core=setup_game(tmp_path,monkeypatch)
    with core.connect() as c:
        c.execute('INSERT INTO matches(id,league,home,away,kickoff,status,home_score,away_score,odd_h,odd_d,odd_a,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(12,'Test','C','D',core.iso(core.utcnow()+timedelta(hours=3)),'SCHEDULED',None,None,2.0,3.2,3.6,core.iso(core.utcnow())))
    slip=core.place_slip(45,100,[{'match_id':11,'pick':'H'},{'match_id':12,'pick':'A'}])
    with pytest.raises(ValueError,match='экспрессов'): core.cashout_quote(45,slip['id'])

def test_stale_score_blocks_cashout(tmp_path,monkeypatch):
    core=setup_game(tmp_path,monkeypatch)
    slip=core.place_slip(45,100,[{'match_id':11,'pick':'H'}])
    with core.connect() as c:
        c.execute('UPDATE matches SET status=?,kickoff=?,home_score=?,away_score=?,updated_at=? WHERE id=11',('IN_PLAY',core.iso(core.utcnow()-timedelta(minutes=60)),0,1,core.iso(core.utcnow()-timedelta(minutes=4))))
    with pytest.raises(ValueError,match='устарели'): core.cashout_quote(45,slip['id'])

def test_losing_pick_quote_decreases(tmp_path,monkeypatch):
    core=setup_game(tmp_path,monkeypatch)
    assert core._live_prob('H',0,1,20)>core._live_prob('H',0,1,60)>core._live_prob('H',0,1,80)
