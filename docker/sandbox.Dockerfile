FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLBACKEND=Agg
RUN pip install --no-cache-dir 'numpy>=1.26' 'pandas>=2.2,<3.1' 'matplotlib>=3.8'
RUN apt-get update && apt-get install -y --no-install-recommends libtk8.6 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /work
USER 65534:65534
# This image contains no edT code, database credentials, API keys or content.
