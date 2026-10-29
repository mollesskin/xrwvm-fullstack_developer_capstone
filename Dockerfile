FROM node:20-alpine AS frontend
WORKDIR /app
COPY server/frontend/package*.json ./
RUN npm ci
COPY server/frontend/ ./
RUN npm run build

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_DEBUG=0
WORKDIR /app
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ ./
COPY --from=frontend /app/build ./frontend/build
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["sh", "entrypoint.sh"]
