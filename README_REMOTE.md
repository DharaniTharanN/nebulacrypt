# PDF Encryption System - Remote Deployment Guide

This guide allows you to run the PDF Encryption System on any machine using pre-built Docker images.

## 1. Pull the Images
Run these commands to download the latest images from Docker Hub:

```bash
docker pull dharanitharan03/aartha-ai-backend:latest
docker pull dharanitharan03/aartha-ai-frontend:latest
```

## 2. Create the Configuration
Create a file named `docker-compose.yml` and paste the following content:

```yaml
services:
  backend:
    image: dharanitharan03/aartha-ai-backend:latest
    container_name: django_backend
    restart: always
    environment:
      - SECRET_KEY=django-insecure-docker-setup
      - DEBUG=True
      - ALLOWED_HOSTS=*
      - FRONTEND_URL=http://localhost
      - POPPLER_PATH=
    ports:
      - "8000:8000"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - db_data:/app/data

  frontend:
    image: dharanitharan03/aartha-ai-frontend:latest
    container_name: vite_frontend
    restart: always
    ports:
      - "80:80"
    volumes:
      - static_volume:/usr/share/nginx/html/static:ro
      - media_volume:/usr/share/nginx/html/media:ro
    depends_on:
      - backend

volumes:
  static_volume:
  media_volume:
  db_data:
```

## 3. Start the System
In the same folder as your `docker-compose.yml`, run:

```bash
docker-compose up -d
```

## 4. Create Admin User
Initialize your admin account:

```bash
docker-compose exec backend python manage.py createsuperuser
```

The system will be available at: http://localhost
