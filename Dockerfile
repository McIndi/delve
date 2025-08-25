# Stage 1: Frontend build
FROM node:24-bookworm-slim AS frontend
WORKDIR /app
COPY package.json ./
COPY webpack.config.js ./
COPY frontend ./frontend
# Install git (needed for npm install)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN npm install
RUN npx webpack --config webpack.config.js

# Stage 2: Python builder
FROM python:3.13.7-slim-bookworm AS builder
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . .
COPY --from=frontend /app/staticfiles ./staticfiles
RUN python manage.py collectstatic --no-input

# Stage 3: Runtime
FROM python:3.13.7-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd -m appuser
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app
RUN mkdir -p /app/log \
 && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["python", "manage.py", "serve"]