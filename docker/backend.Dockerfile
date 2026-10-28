FROM node:24-alpine AS web-build
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Same-origin /api calls in the hosted combined frontend/backend deployment.
RUN VITE_API_URL= npm run build

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/backend
RUN apt-get update \
    && apt-get install -y --no-install-recommends libtk8.6 \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

RUN useradd --create-home --uid 10001 pylearn
COPY --chown=pylearn:pylearn backend/ ./
COPY --chown=pylearn:pylearn content/ /app/content/
COPY --from=web-build --chown=pylearn:pylearn /web/dist/ /app/frontend/dist/
ENV FRONTEND_DIST_DIR=/app/frontend/dist
COPY docker/backend-entrypoint.sh /usr/local/bin/pylearn-start
RUN chmod +x /usr/local/bin/pylearn-start \
    && chown pylearn:pylearn /app/backend /app/content
USER pylearn
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/pylearn-start"]
