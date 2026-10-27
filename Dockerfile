FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 PORT=8000 \
    PYTHONPATH=/usr/src/app \
    DB_PATH=/app/data/football.sqlite3
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY static/ ./static/
COPY run.py ./
RUN python -c "import app, app.main; print('RDG imports OK; files are outside /app mount')" \
 && test -f /usr/src/app/run.py \
 && mkdir -p /app/data
EXPOSE 8000
CMD ["python", "/usr/src/app/run.py"]
