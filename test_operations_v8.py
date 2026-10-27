import sqlite3
from app import core
from app import operations as ops

def test_sync_records_and_status(tmp_path,monkeypatch):
    path=tmp_path/'db.sqlite3'
    monkeypatch.setattr(core,'DB_PATH',str(path))
    monkeypatch.setattr(ops,'DB_PATH',str(path))
    core.init_db();ops.init_operations()
    ops.record_sync(core.iso(core.utcnow()),result={'mode':'demo','updated':3,'settled':1})
    ops.record_sync(core.iso(core.utcnow()),error='bad gateway')
    report=ops.operations_overview()
    assert report['latest']['ok']==0
    assert report['last_success_at']
    assert report['recent_runs'][1]['updated']==3

def test_backup_consistent_and_retention(tmp_path,monkeypatch):
    path=tmp_path/'db.sqlite3'; backups=tmp_path/'backups'
    monkeypatch.setattr(core,'DB_PATH',str(path))
    monkeypatch.setattr(ops,'DB_PATH',str(path))
    core.init_db();ops.init_operations(); core.get_user(42,'test')
    first=ops.create_backup(backups,keep=1)
    assert first['verified']
    assert sqlite3.connect(first['file']).execute('select balance from users where id=42').fetchone()[0]==1000
    core.get_user(43,'new')
    second=ops.create_backup(backups,keep=1)
    assert len(list(backups.glob('football-*.sqlite3')))==1
    assert sqlite3.connect(second['file']).execute('select count(*) from users').fetchone()[0]==2
