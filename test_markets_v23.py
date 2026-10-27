from datetime import timedelta

def test_new_market_results_and_push():
    from app.core import MARKET_NAMES, GAME_MARKET_ODDS, won_pick, pushed_pick
    assert set(GAME_MARKET_ODDS).issubset(MARKET_NAMES)
    assert won_pick('O15', 1, 1)
    assert not won_pick('U15', 1, 1)
    assert won_pick('IH15O', 2, 0)
    assert won_pick('IA15U', 2, 1)
    assert pushed_pick('F1M1', 2, 1)
    assert pushed_pick('F2P1', 2, 1)
    assert not won_pick('F1M1', 2, 1)
    assert won_pick('F1M1', 3, 1)
    assert won_pick('F2P1', 1, 1)


def test_handicap_push_refunds_once(tmp_path, monkeypatch):
    import app.core as core
    monkeypatch.setattr(core, 'DB_PATH', str(tmp_path / 'push.sqlite'))
    core.init_db()
    core.get_user(974)
    with core.connect() as c:
        c.execute('''INSERT INTO matches(id,league,home,away,kickoff,status,home_score,away_score,odd_h,odd_d,odd_a,updated_at)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
          (4001,'Test','Red','Blue',core.iso(core.utcnow()+timedelta(days=1)), 'SCHEDULED',None,None,2.0,3.0,4.0,core.iso(core.utcnow())))
    slip=core.place_slip(974,100,[{'match_id':4001,'pick':'F1M1'}])
    with core.connect() as c:
        c.execute('UPDATE matches SET status=?,home_score=?,away_score=? WHERE id=?',('FINISHED',2,1,4001))
    core.settle()
    core.settle()
    with core.connect() as c:
        row=c.execute('SELECT status,payout FROM slips WHERE id=?',(slip['id'],)).fetchone()
        balance=c.execute('SELECT balance FROM users WHERE id=?',(974,)).fetchone()[0]
    assert row['status']=='void' and row['payout']==100
    assert balance==1000
