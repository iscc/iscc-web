FROM python:3.11 AS builder

# Disable stdout/stderr buffering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

# Install taglib
RUN apt-get update && \
  apt-get install --no-install-recommends -y libtag1-dev && \
  rm -rf /var/lib/apt/lists

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/

#
# prod-build
#

FROM builder AS prod-build

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-install-project

RUN /app/.venv/bin/python -m iscc_sdk.install

COPY . /app/

#
# frontend-build
#
FROM node:22-slim AS frontend-build

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

RUN pnpm install

COPY . .

RUN pnpm run build

#
# prod-runtime
#

FROM python:3.11-slim AS prod-runtime

LABEL org.opencontainers.image.source=https://github.com/iscc/iscc-web

RUN apt-get update && apt-get install --no-install-recommends -y libmagic1 libtag1v5-vanilla && rm -rf /var/lib/apt/lists

# Disable stdout/stderr buffering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV=/app/.venv

ENV ISCC_WEB_ENVIRONMENT=production
ENV PORT=8000

COPY --from=prod-build /root/.local/share/iscc-sdk /root/.local/share/iscc-sdk
COPY --from=prod-build /root/.ipfs /root/.ipfs
COPY --from=prod-build /app /app
COPY --from=frontend-build /app/iscc_web/static/dist /app/iscc_web/static/dist

WORKDIR /app

EXPOSE 8000/tcp

CMD ["gunicorn", "iscc_web.main:app", "-k", "uvicorn.workers.UvicornWorker"]
