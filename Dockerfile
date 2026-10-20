FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY backend ./backend
COPY main.py .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
