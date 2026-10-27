from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_help_is_accessible_in_navigation():
    html = (ROOT/'static/index.html').read_text()
    js = (ROOT/'static/app.js').read_text()
    assert 'data-menu-view="help"' in html
    assert "else if(state.view==='help')helpView()" in js
    for phrase in ['Кэшаут', 'Экспрессы', '90 дней', 'жалобы']:
        assert phrase.lower() in js.lower()

def test_windows_launcher_never_exposes_dev_server_publicly():
    bat = (ROOT/'START_WINDOWS.bat').read_text()
    run = (ROOT/'run.py').read_text()
    assert '127.0.0.1' in bat and '?dev=123' in bat
    assert "if dev_auth and host not in" in run
    assert "'127.0.0.1'" in run
