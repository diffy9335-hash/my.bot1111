@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .env (copy .env.example .env >nul & echo Создан .env. Проверь настройки.)
if not exist .venv (py -3 -m venv .venv || goto :error)
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt || goto :error
set HOST=127.0.0.1
set DEV_AUTH=true
start "Football Arena API" cmd /k "cd /d "%~dp0" && call .venv\Scripts\activate.bat && set HOST=127.0.0.1 && set DEV_AUTH=true && python run.py"
timeout /t 4 >nul
start "" "http://127.0.0.1:8000/?dev=123"
echo Локальный тест запущен. Бот в Telegram запускается отдельно с настоящим BOT_TOKEN.
pause
exit /b 0
:error
echo Не удалось запустить. Установи Python 3.11+ и проверь интернет.
pause
exit /b 1
