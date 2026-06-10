FROM python:3.13-slim AS builder

# Disable stdout/stderr buffering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

# libexpat is required by the exiv2 wheel's bundled native library
RUN apt-get update && \
  apt-get install --no-install-recommends -y libexpat1 && \
  rm -rf /var/lib/apt/lists

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/

#
# prod-build
#

FROM builder AS prod-build

# Install dependencies into /app/.venv
RUN uv sync --frozen --no-dev --no-install-project

# Fetch content processing tools (ffmpeg, ffprobe, fpcalc) into /root/.local/share/iscc-sdk
RUN /app/.venv/bin/iscc-sdk install

COPY . /app/

#
# frontend-build
#
FROM node:16.17.0 AS frontend-build

# pnpm 7 matches pnpm-lock.yaml (lockfileVersion 5.4) and still supports Node 16;
# unpinned installs now resolve to pnpm >=10 which requires Node >=22.
RUN npm install -g pnpm@7

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

RUN pnpm install

COPY . .

RUN pnpm run build

#
# prod-runtime
#

FROM python:3.13-slim AS prod-runtime

LABEL org.opencontainers.image.source=https://github.com/iscc/iscc-web

# libexpat is required by the exiv2 wheel's bundled native library
RUN apt-get update && \
  apt-get install --no-install-recommends -y libexpat1 && \
  rm -rf /var/lib/apt/lists

# Disable stdout/stderr buffering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV=/app/.venv

ENV ISCC_WEB_ENVIRONMENT=production
ENV PORT=8000

COPY --from=prod-build /root/.local/share/iscc-sdk /root/.local/share/iscc-sdk
COPY --from=prod-build /app /app
COPY --from=frontend-build /app/iscc_web/static/dist /app/iscc_web/static/dist

WORKDIR /app

EXPOSE 8000/tcp

CMD ["gunicorn", "iscc_web.main:app", "-k", "uvicorn_worker.UvicornWorker"]
