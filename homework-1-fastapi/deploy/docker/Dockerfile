# syntax=docker/dockerfile:1
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --- Corporate TLS interception support ----------------------------------
# If a CA cert is placed under deploy/docker/certs/ (gitignored), trust it so
# pip/app can reach PyPI/registries through an SSL-inspection proxy such as
# Cloudflare WARP or Zscaler. No-op when the dir holds no *.crt.
# pip normally validates against its bundled certifi, so we also point it (and
# common tools) at the system bundle, which now includes the corporate CA.
COPY deploy/docker/certs/ /usr/local/share/ca-certificates/
RUN update-ca-certificates || true
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# --- Dependencies + project ----------------------------------------------
# Editable (-e) so a mounted source tree hot-reloads via uvicorn --reload.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir -e .

# --- Runtime files --------------------------------------------------------
COPY alembic.ini ./
COPY migrations ./migrations
COPY scripts ./scripts
COPY deploy/docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Run as non-root
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
ENTRYPOINT ["entrypoint.sh"]
