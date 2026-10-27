from datetime import timedelta
import pytest
from app.core import won_pick, market_odd

@pytest.mark.parametrize('score,expected', [((2,1),{'O25':True,'U25':False,'GG':True,'NG':False}),((0,0),{'O25':False,'U25':True,'GG':False,'NG':True}),((1,1),{'O25':False,'U25':True,'GG':True,'NG':False})])
def test_markets(score,expected):
    for choice,result in expected.items(): assert won_pick(choice,*score)==result

def test_extra_market_settlement(tmp_path,monkeypatch):
    from app import core
    monkeypatch.setattr(core,'DB_PATH',str(tmp_path/'markets.db'))
    core.init_db();core.get_user(777)
    with core.connect() as c:
        c.execute('INSERT INTO matches(id,league,home,away,kickoff,status,home_score,away_score,odd_h,odd_d,odd_a,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(123,'Test','Home','Away',core.iso(core.utcnow()+timedelta(days=1)),'SCHEDULED',None,None,2.1,3.2,3.4,core.iso(core.utcnow())))
    ticket=core.place_slip(777,100,[{'match_id':123,'pick':'GG'}]);assert ticket['potential']==188
    with core.connect() as c:c.execute("UPDATE matches SET status='FINISHED',home_score=2,away_score=1 WHERE id=123")
    assert core.settle()==1
    assert core.get_user(777)['balance']==1088
    with core.connect() as c:assert c.execute('SELECT COUNT(*) FROM notifications').fetchone()[0]==1
    assert core.settle()==0
