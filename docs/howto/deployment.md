---
icon: lucide/server
description: Deploy iscc-web in production with Docker Compose and Caddy. Covers the ghcr.io image and its tags, TLS termination, resource sizing, and updates.
---

# Deployment

`iscc-web` is a standard Python [ASGI](https://asgi.readthedocs.io/en/latest/) application, so
there are many ways to deploy it. This guide shows a simple standalone Docker Compose setup with
[Caddy](https://caddyserver.com/) as a TLS-terminating reverse proxy with automatic certificate
management.

## The Docker image

Production images are published to the GitHub Container Registry as
[`ghcr.io/iscc/iscc-web`](https://github.com/iscc/iscc-web/pkgs/container/iscc-web):

- Built on `python:3.13-slim` and served by gunicorn with uvicorn workers.
- Listens on port `8000`. Gunicorn reads the `PORT` environment variable for its default bind
    address (see the [gunicorn docs](https://docs.gunicorn.org/en/stable/settings.html#bind)),
    so set `PORT` to change the container port.
- The `iscc-sdk` content-processing binaries (ffmpeg, ffprobe, fpcalc) and the iscc-sct /
    iscc-sci ONNX models for the experimental semantic codes are downloaded at image build time,
    so containers start warm — no first-request downloads.
- `ISCC_WEB_ENVIRONMENT=production` is preset in the image.

### Image tags

| Tag     | Example                           | Published                                 |
| ------- | --------------------------------- | ----------------------------------------- |
| `main`  | `ghcr.io/iscc/iscc-web:main`      | On every push to `main` after CI passes   |
| `X.Y.Z` | `ghcr.io/iscc/iscc-web:0.3.1`     | On GitHub releases — immutable            |
| `X.Y`   | `ghcr.io/iscc/iscc-web:0.3`       | On GitHub releases — tracks latest patch  |
| `*-gpu` | `ghcr.io/iscc/iscc-web:0.3.1-gpu` | GPU variant of each tag above (see below) |

No `:latest` tag is published. Pin a semver tag for reproducible deployments, or use `:main` to
follow the development branch.

### GPU image (opt-in)

Every tag from 0.3.1 onward also ships a `-gpu` variant (`:0.3.1-gpu`, `:0.3-gpu`, `:main-gpu`)
built on the `nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04` base with the CUDA build of
onnxruntime. It runs
the experimental semantic codes (iscc-sct text, iscc-sci image) on an NVIDIA GPU instead of the
CPU. The default (non-`-gpu`) image is what most deployments want — only reach for `-gpu` if you
serve semantic codes at volume.

The GPU image needs an NVIDIA driver, the
[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/),
and the container started with GPU access (`docker run --gpus all …`, or a Compose `deploy.resources`
device reservation). On a host without a usable GPU it still runs but falls back to CPU inference —
with no benefit over the much smaller default image (the CUDA base is ~3 GB).

GPU deployment specifics (Compose device reservation, worker sizing, on-box verification) live in
the [`iscc-infra`](https://github.com/iscc/iscc-infra) repository rather than being duplicated here.

## Deploy with Docker Compose

You need a server with Docker installed and a DNS entry pointing your domain to the server's IP.
Create these three files on your server:

### Caddyfile

```
{
  email {$ISCC_WEB_SITE_EMAIL}
}

{$ISCC_WEB_SITE_ADDRESS} {
  reverse_proxy app:8000
}
```

### .env

```ini
ISCC_WEB_ENVIRONMENT=production
ISCC_WEB_SITE_EMAIL=admin@example.com
ISCC_WEB_SITE_ADDRESS=https://example.com
ISCC_WEB_PRIVATE_FILES=true
ISCC_WEB_MAX_UPLOAD_SIZE=1073741824
ISCC_WEB_STORAGE_EXPIRY=3600
ISCC_WEB_CLEANUP_INTERVAL=600
ISCC_WEB_LOG_LEVEL=INFO
ISCC_WEB_IO_READ_SIZE=2097152
FORWARDED_ALLOW_IPS=*
```

Set `ISCC_WEB_SITE_ADDRESS` to your domain and `ISCC_WEB_SITE_EMAIL` to a real address — Caddy
uses it for the TLS certificate registration. See [Configuration](configuration.md) for the full
option reference, including the ISCC processing defaults (`ISCC_SDK_*`, `ISCC_SCT_*`,
`ISCC_SCI_*`).

### docker-compose.yaml

```yaml
volumes:
  caddy-config:
  caddy-data:

services:
  app:
    image: ghcr.io/iscc/iscc-web:main
    init: true
    env_file: .env
  caddy:
    image: caddy:2.6.1-alpine
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy-config:/config
      - caddy-data:/data
    ports:
      - 80:80
      - 443:443
      - 443:443/udp
    depends_on:
      - app
```

The app container does not need a volume: uploads are stored inside the container and deleted
automatically after `ISCC_WEB_STORAGE_EXPIRY` seconds, so the media storage is transient by
design.

## Start the service

```shell
docker compose up -d
```

Caddy obtains and renews the TLS certificate automatically once your DNS entry resolves to the
server.

## Watch logs

```shell
docker compose logs -f
```

## Update to the latest image

```shell
docker compose pull
docker compose up -d
```

With the `:main` tag this pulls whatever was last pushed to the main branch. If you pinned a
semver tag, change the tag in `docker-compose.yaml` first.

## Forwarded client IPs

With `ISCC_WEB_PRIVATE_FILES=true` (the default), the uploader of a file is identified by a hash
of the client IP, and only that uploader may download, embed into, or delete the file. The
application must therefore see the real client IP, not the proxy's.

`FORWARDED_ALLOW_IPS=*` in the `.env` example tells gunicorn/uvicorn to trust `X-Forwarded-For`
headers from any upstream. That is appropriate here because the app port is only reachable
through Caddy on the internal Compose network.

!!! warning

    If forwarded headers are not trusted, every request appears to originate from the proxy's
    IP — all clients then share one identity, and any client can download or delete any upload.
    Conversely, never set `FORWARDED_ALLOW_IPS=*` on a service whose application port is
    directly reachable from the internet, since clients could then spoof their IP via headers.

## Resource sizing

CPU-bound ISCC processing runs in a pool of worker processes. `ISCC_WEB_MAX_WORKERS` caps the
pool size and defaults to the CPU count. Each worker lazy-loads the iscc-sdk toolchain and — when
semantic features are requested — the iscc-sct/iscc-sci ONNX models, which can take several
hundred MB of RAM per worker. Lower `ISCC_WEB_MAX_WORKERS` on memory-constrained hosts.

Also budget for uploads: files up to `ISCC_WEB_MAX_UPLOAD_SIZE` (default 1 GB) are kept on disk
inside the container until the cleanup task removes them after `ISCC_WEB_STORAGE_EXPIRY` seconds.
