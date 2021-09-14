FROM python:3.7

COPY src/ app/
WORKDIR /app

RUN pip install -r requirements.txt

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --timeout 360 --threads 8 app:app