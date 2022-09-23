FROM python:3.9 AS builder

ARG POETRY_VERSION=1.2.1

# Disable stdout/stderr buffering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

# Disable some obvious pip functionality
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=1

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_PATH=/venvs

# Install taglib
RUN apt-get update && \
  apt-get install --no-install-recommends -y libtag1-dev && \
  rm -rf /var/lib/apt/lists

# Install Poetry
# hadolint ignore=DL3013
RUN pip install -U pip wheel setuptools && \
  pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

#
# prod-build
#

FROM builder AS prod-build

# Create virtualenv and install dependencies
# hadolint ignore=SC1091
RUN python -m venv /venv && . /venv/bin/activate && poetry install --only=main --no-root

RUN /venv/bin/python -m iscc_sdk.install

COPY . /app/

#
# frontend-build
#
FROM node:16.17.0 AS frontend-build

RUN npm install -g pnpm

WORKDIR /app

COPY package.json pnpm-lock.yaml ./

RUN pnpm install

COPY . .

RUN pnpm run build

#
# prod-runtime
#

FROM python:3.9-slim AS prod-runtime

LABEL org.opencontainers.image.source=https://github.com/iscc/iscc-web

RUN apt-get update && apt-get install --no-install-recommends -y libmagic1 libtag1v5-vanilla && rm -rf /var/lib/apt/lists

# Disable stdout/stderr buggering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV=/venv

ENV ISCC_WEB_ENVIRONMENT=production
ENV PORT=8000

COPY --from=prod-build /root/.local/share/iscc-sdk /root/.local/share/iscc-sdk
COPY --from=prod-build /root/.ipfs /root/.ipfs
COPY --from=prod-build /app /app
COPY --from=prod-build /venv /venv
COPY --from=frontend-build /app/iscc_web/static/dist /app/iscc_web/static/dist

WORKDIR /app

EXPOSE 8000/tcp

CMD ["gunicorn", "iscc_web.main:app", "-k", "uvicorn.workers.UvicornWorker"]
