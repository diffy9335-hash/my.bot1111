import os, sys, tempfile, importlib, time, json, hmac, hashlib
from datetime import timedelta

def test_auth_signature():
    from app.core import validate_init_data
    token='123:ABC'; user=json.dumps({'id':44,'first_name':'Test'},separators=(',',':'))
    from urllib.parse import urlencode
    vals={'auth_date':str(int(time.time())),'user':user}
    check='\n'.join(f'{k}={v}' for k,v in sorted(vals.items()))
    secret=hmac.new(b'WebAppData',token.encode(),'sha256').digest()
    sig=hmac.new(secret,check.encode(),'sha256').hexdigest()
    assert validate_init_data(urlencode({**vals,'hash':sig}),token)['id']==44

def test_auth_with_telegram_ed25519_signature_field():
    """New Telegram clients provide both hash and signature in initData."""
    from app.core import validate_init_data
    from urllib.parse import urlencode
    token = '123:ABC'
    vals = {
        'auth_date': str(int(time.time())),
        'query_id': 'AA123',
        'signature': 'base64url-signature',
        'user': json.dumps({'id': 44, 'first_name': 'Test'}, separators=(',', ':')),
    }
    check = '\n'.join(f'{k}={v}' for k, v in sorted(vals.items()))
    secret = hmac.new(b'WebAppData', token.encode(), hashlib.sha256).digest()
    digest = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    assert validate_init_data(urlencode({**vals, 'hash': digest}), token)['id'] == 44
    # The signature field is authenticated too: changing it must fail.
    import pytest
    with pytest.raises(ValueError, match='Неверная подпись'):
        validate_init_data(urlencode({**vals, 'signature': 'changed', 'hash': digest}), token)

def test_slip_and_settlement(tmp_path,monkeypatch):
    monkeypatch.setattr('app.core.DB_PATH',str(tmp_path/'test.db'))
    from app.core import init_db,get_user,connect,place_slip,settle,iso,utcnow
    init_db(); get_user(123)
    with connect() as c:
        c.execute('INSERT INTO matches(id,league,home,away,kickoff,status,home_score,away_score,odd_h,odd_d,odd_a,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(1,'Test','A','B',iso(utcnow()+timedelta(days=1)),'SCHEDULED',None,None,2.0,3.2,3.6,iso(utcnow())))
    s=place_slip(123,100,[{'match_id':1,'pick':'H'}]); assert s['potential']==200
    assert get_user(123)['balance']==900
    with connect() as c: c.execute("UPDATE matches SET status='FINISHED',home_score=2,away_score=0 WHERE id=1")
    assert settle()==1
    assert settle()==0
    assert get_user(123)['balance']==1100
