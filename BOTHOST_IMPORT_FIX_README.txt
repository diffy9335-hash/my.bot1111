RDG v3.2 Bothost /app bind-mount fix (2026-10-27)

Bothost may mount a host directory over /app at container START, masking code
stored in /app during the Docker build. This caused both errors:
- ModuleNotFoundError: No module named 'app'
- python: can't open file '/app/run.py'

FIX: Dockerfile now keeps application code in /usr/src/app (OUTSIDE /app).
CMD calls /usr/src/app/run.py; PYTHONPATH=/usr/src/app.
DB_PATH=/app/data/football.sqlite3 uses Bothost's persistent storage folder.

In Bothost choose stack "Dockerfile", upload this ZIP with files AT ZIP ROOT,
trigger a FULL NEW BUILD. Do not select automatic Python stack.
Set BOT_TOKEN, FOOTBALL_API_KEY, PUBLIC_URL and other secrets using host environment variables.
Do not expose BOT_TOKEN or your existing sqlite database publicly.

IMPORTANT: This container only launches the FastAPI web server. The bot itself
needs a separately configured process (python -m app.bot) or a carefully managed
multi-process deployment. The web startup alone does not launch bot polling.

If a new error occurs, use container runtime logs, not build logs.
