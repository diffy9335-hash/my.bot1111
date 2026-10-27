from datetime import timedelta
import pytest


def setup(tmp_path, monkeypatch):
    from app import core
    monkeypatch.setattr(core, 'DB_PATH', str(tmp_path/'v7.sqlite'))
    core.init_db()
    core.get_user(789)
    with core.connect() as db:
        db.execute('INSERT INTO matches(id,league,home,away,kickoff,status,home_score,away_score,odd_h,odd_d,odd_a,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                   (989, 'Test', 'A', 'B', core.iso(core.utcnow()+timedelta(hours=1)), 'SCHEDULED',
                    None, None, 2.0, 3.0, 4.0, core.iso(core.utcnow())))
    return core


def test_retry_only_charges_once(tmp_path,monkeypatch):
    core=setup(tmp_path,monkeypatch)
    picks=[{'match_id':989,'pick':'H'}]
    first=core.place_slip(789,100,picks,'replay-key-12345')
    again=core.place_slip(789,100,picks,'replay-key-12345')
    assert first['id']==again['id'] and again['duplicate']
    assert core.get_user(789)['balance']==900
    with core.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM ledger WHERE reason='Ставка'").fetchone()[0]==1


def test_retry_key_reuse_different_amount_rejected(tmp_path,monkeypatch):
    core=setup(tmp_path,monkeypatch)
    picks=[{'match_id':989,'pick':'H'}]
    core.place_slip(789,100,picks,'replay-key-12345')
    with pytest.raises(ValueError,match='Ключ запроса'):
        core.place_slip(789,200,picks,'replay-key-12345')


def test_betting_closes_five_minutes_before_kickoff(tmp_path,monkeypatch):
    core=setup(tmp_path,monkeypatch)
    with core.connect() as db:
        db.execute('UPDATE matches SET kickoff=? WHERE id=989',
                   (core.iso(core.utcnow()+timedelta(minutes=4)),))
    with pytest.raises(ValueError,match='нельзя поставить'):
        core.place_slip(789,100,[{'match_id':989,'pick':'H'}],'replay-key-12345')
