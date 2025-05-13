FROM python:3.11-slim

WORKDIR /opt/app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /opt/app/backend

ENV FLASK_APP=backend.app:create_app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "backend.app:create_app()"]
