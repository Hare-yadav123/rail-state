FROM python:3.13.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn backendapi.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]