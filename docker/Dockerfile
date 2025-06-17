FROM python:3.11-slim
WORKDIR /opt/app

# dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# código
COPY backend /opt/app/backend

# nuevo FLASK_APP
ENV FLASK_APP=backend.app:create_app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "backend.app:create_app()"]
