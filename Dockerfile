FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SECRET_KEY=build-only-dummy
RUN python manage.py collectstatic --no-input

CMD exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --timeout 120