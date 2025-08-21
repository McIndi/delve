# Stage 1: Frontend build
FROM node:20-bullseye-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
COPY webpack.config.js ./
COPY frontend ./frontend
# Install and build the frontend bundle into staticfiles
RUN npm install
RUN npx webpack --config webpack.config.js

# Stage 2: Python builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . .
# Bring in the prebuilt frontend assets
COPY --from=frontend /app/staticfiles ./staticfiles
# Collect static files for Django (keeps parity with README/ZIP build)
RUN python manage.py collectstatic --no-input

# Stage 3: Runtime
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Non-root user
RUN useradd -m appuser
WORKDIR /app
# Copy installed packages and app code
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app
USER appuser
EXPOSE 8000
# Use the existing CherryPy management command
CMD ["python", "manage.py", "serve"]
