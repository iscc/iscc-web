FROM python:3.14.10-slim-trixie@sha256:af8a5aa14780025dbfbcfbc81bd8a91ebd87711dd5b0f48ed71090949dd7cb1d AS builder

# Disable stdout/stderr buffering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

# libexpat is required by the exiv2 wheel's bundled native library
RUN apt-get update && \
  apt-get install --no-install-recommends -y libexpat1 && \
  rm -rf /var/lib/apt/lists

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/

#
# prod-build
#

FROM builder AS prod-build

# Install dependencies into /app/.venv. --extra cpu pulls the CPU onnxruntime variant of
# iscc-sct/iscc-sci (post-split, no extra means no onnxruntime at all). The GPU image uses
# --extra gpu in its own stage; the two onnxruntime variants must never co-resolve.
RUN uv sync --frozen --no-dev --no-install-project --extra cpu

# Fetch content processing tools (ffmpeg, ffprobe, fpcalc) into /root/.local/share/iscc-sdk
RUN /app/.venv/bin/iscc-sdk install

# Pre-download semantic-code ONNX models so containers start warm (no first-request download)
RUN /app/.venv/bin/python -c "import iscc_sct.utils, iscc_sci.utils; iscc_sct.utils.get_model(); iscc_sci.utils.get_model()"

COPY . /app/

#
# frontend-build
#
FROM node:26.13.0-trixie-slim@sha256:5adad64f9a1fca2d51972caa65983634c8a774eb300d72b20f7f2a0f60368072 AS frontend-build

# Match the packageManager field in package.json
RUN npm install -g pnpm@12.18.0

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm run build

#
# prod-runtime
#

FROM python:3.14.10-slim-trixie@sha256:af8a5aa14780025dbfbcfbc81bd8a91ebd87711dd5b0f48ed71090949dd7cb1d AS prod-runtime

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
COPY --from=prod-build /root/.local/share/iscc-sct /root/.local/share/iscc-sct
COPY --from=prod-build /root/.local/share/iscc-sci /root/.local/share/iscc-sci
COPY --from=prod-build /app /app
COPY --from=frontend-build /app/iscc_web/static/dist /app/iscc_web/static/dist

WORKDIR /app

EXPOSE 8000/tcp

# Build metadata reported by GET /health: the same values as the OCI version/revision labels (CI passes
# them as build args), empty for local builds. Declared late so a new revision only rebuilds this layer.
ARG VERSION=""
ARG REVISION=""
ENV ISCC_WEB_BUILD_VERSION=${VERSION} ISCC_WEB_BUILD_REVISION=${REVISION}

# Readiness probe with the image's own Python (no curl needed). GET /health answers 503 until the ONNX
# models are loaded in all ISCC workers; failed probes within the start period do not count.
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --start-interval=5s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request as r; r.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT', '8000'), timeout=4)"]

CMD ["gunicorn", "iscc_web.main:app", "-k", "uvicorn_worker.UvicornWorker"]

#
# prod-runtime-gpu (opt-in CUDA variant)
#
# Single combined build+runtime stage on the CUDA base: a multi-stage split saves almost nothing
# on a ~3 GB base and would force copying a uv-managed Python across stages (fragile venv symlinks).
# This stage is NOT the default — Docker builds the last stage when no target is given, so every
# CPU build invocation must pass `target: prod-runtime` (see release.yml / ci.yml). NVIDIA driver +
# nvidia-container-toolkit + `--gpus all` are needed for GPU; without them it falls back to CPU.
#
FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04@sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356 AS prod-runtime-gpu

LABEL org.opencontainers.image.source=https://github.com/iscc/iscc-web

# ca-certificates: the CUDA base ships none (the python slim base does); the model/tool fetch below plus
# runtime HTTPS (Sentry, URL fetches) need TLS trust. libexpat1: the exiv2 wheel's native lib.
RUN apt-get update && \
  apt-get install --no-install-recommends -y libexpat1 ca-certificates && \
  rm -rf /var/lib/apt/lists

# Disable stdout/stderr buffering, can cause issues with Docker logs
ENV PYTHONUNBUFFERED=1

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV=/app/.venv

ENV ISCC_WEB_ENVIRONMENT=production
ENV PORT=8000

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock .python-version /app/

# The CUDA base ships system Python 3.12; install the uv-managed CPython pinned in .python-version,
# which uv sync then picks up as well.
RUN uv python install

# Install dependencies into /app/.venv with the GPU onnxruntime variant.
RUN uv sync --frozen --no-dev --no-install-project --extra gpu

# Fetch content processing tools (ffmpeg, ffprobe, fpcalc) into /root/.local/share/iscc-sdk
RUN /app/.venv/bin/iscc-sdk install

# Bake semantic-code ONNX models so containers start warm AND prove the GPU image's imports resolve
# in the final image (the build host has no GPU; get_model() only downloads — no CUDA session).
RUN /app/.venv/bin/python -c "import iscc_sct.utils, iscc_sci.utils; iscc_sct.utils.get_model(); iscc_sci.utils.get_model()"

COPY . /app/
COPY --from=frontend-build /app/iscc_web/static/dist /app/iscc_web/static/dist

EXPOSE 8000/tcp

# Build metadata reported by GET /health: the same values as the OCI version/revision labels (CI passes
# them as build args), empty for local builds. Declared late so a new revision only rebuilds this layer.
ARG VERSION=""
ARG REVISION=""
ENV ISCC_WEB_BUILD_VERSION=${VERSION} ISCC_WEB_BUILD_REVISION=${REVISION}

# Readiness probe with the image's own Python (no curl needed). GET /health answers 503 until the ONNX
# models are loaded in all ISCC workers; failed probes within the start period do not count.
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --start-interval=5s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request as r; r.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT', '8000'), timeout=4)"]

CMD ["gunicorn", "iscc_web.main:app", "-k", "uvicorn_worker.UvicornWorker"]
