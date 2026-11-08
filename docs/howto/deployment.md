---
icon: lucide/server
description: Deploy iscc-web in production with Docker Compose behind a reverse proxy. Covers the ghcr.io image and its tags, what the reverse proxy must do, resource sizing, and updates.
---

# Deployment

`iscc-web` is a standard Python [ASGI](https://asgi.readthedocs.io/en/latest/) application, so
there are many ways to deploy it. This guide runs the Docker image with Docker Compose behind a
reverse proxy that terminates TLS - any reverse proxy or load balancer that meets the
[requirements below](#reverse-proxy) works. To limit who can use your instance, see
[Restrict access](restrict-access.md).

## The Docker image

Production images are published to the GitHub Container Registry as
[`ghcr.io/iscc/iscc-web`](https://github.com/iscc/iscc-web/pkgs/container/iscc-web):

- Built on `python:3.14-slim` (Debian trixie, base images pinned by digest) and served by
    gunicorn with uvicorn workers.
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

You need a server with Docker installed and a reverse proxy that serves your domain over HTTPS.
Create these two files on your server:

### .env

```ini
ISCC_WEB_ENVIRONMENT=production
ISCC_WEB_SITE_ADDRESS=https://example.com
ISCC_WEB_PRIVATE_FILES=true
ISCC_WEB_MAX_UPLOAD_SIZE=1073741824
ISCC_WEB_STORAGE_EXPIRY=3600
ISCC_WEB_CLEANUP_INTERVAL=600
ISCC_WEB_LOG_LEVEL=INFO
ISCC_WEB_IO_READ_SIZE=2097152
FORWARDED_ALLOW_IPS=*
```

Set `ISCC_WEB_SITE_ADDRESS` to the public address of your instance. See
[Configuration](configuration.md) for the full option reference, including the ISCC processing
defaults (`ISCC_SDK_*`, `ISCC_SCT_*`, `ISCC_SCI_*`).

### docker-compose.yaml

```yaml
services:
  app:
    image: ghcr.io/iscc/iscc-web:main
    init: true
    restart: unless-stopped
    env_file: .env
    ports:
      - 127.0.0.1:8000:8000
```

The port is published on the loopback interface only, so a reverse proxy on the same host can
reach the app but the internet cannot. If your reverse proxy runs as a container, add it to this
Compose file instead, drop the `ports` entry and point the proxy at `app:8000`.

The app container does not need a volume: uploads are stored inside the container and deleted
automatically after `ISCC_WEB_STORAGE_EXPIRY` seconds, so the media storage is transient by
design.

## Reverse proxy

The reverse proxy in front of the app must:

- **Terminate TLS** and serve the instance at the root of its domain or subdomain (see
    [Hostname and path](restrict-access.md#hostname-and-path)).
- **Keep the original `Host` header and set `X-Forwarded-Proto`.** The service builds the URLs in
    its `Location` response headers from the host and scheme of the request.
- **Set `X-Forwarded-For` to the address of the connecting client, replacing any value the client
    sent.** The service identifies uploaders by this address. Many proxies append to an incoming
    header by default, which lets clients choose the address the service sees (see
    [Forwarded client IPs](#forwarded-client-ips)).
- **Accept request bodies up to `ISCC_WEB_MAX_UPLOAD_SIZE`** (1 GB by default). Many proxies cap
    request bodies at a few megabytes unless configured otherwise.
- **Allow long responses.** Processing a large audio or video file can take minutes, longer than
    the read or response timeouts many proxies apply by default.

## Start the service

```shell
docker compose up -d
```

The container reports `healthy` in `docker compose ps` once it is ready to serve requests (see
[Health check](#health-check)).

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
headers from any upstream and to take the client IP from the leftmost address in the header. That
is safe only when both of these hold:

- The app port is only reachable from the reverse proxy - published on the loopback interface, or
    on an internal Compose network.
- The proxy replaces `X-Forwarded-For` instead of appending to it, so the header holds a single
    address the client cannot choose.

If your proxy can only append, set `FORWARDED_ALLOW_IPS` to the network the app sees the proxy
connect from instead of `*` - the subnet of the app's Compose network (`docker network inspect`
shows it), which also covers the gateway address that connections from the host arrive from. The
service then takes the rightmost address outside that network, which is the one your proxy
appended.

!!! warning

    If forwarded headers are not trusted, every request appears to originate from the proxy's
    IP — all clients then share one identity, and any client can download or delete any upload.
    Conversely, with `FORWARDED_ALLOW_IPS=*` clients can spoof their IP through the header -
    and with it the uploader identity - if the application port is directly reachable from the
    internet or the proxy appends to an `X-Forwarded-For` header the client sent.

## Health check

Both images declare a Docker `HEALTHCHECK` that probes
[`GET /health`](../reference/rest-api.md#get-health) with the image's own Python. The endpoint
answers `503` until the ONNX models are loaded in all ISCC workers, and on the GPU image also when
the models fell back to CPU (for example after an NVIDIA driver update broke CUDA). The container
reports `healthy` once the endpoint answers `200`; `docker compose ps` shows the state.

The check probes every 30 seconds (every 5 seconds during a 120-second start period, where failed
probes do not count) and marks the container `unhealthy` after three consecutive failures. External
monitors can poll the same endpoint — it answers from cached state and stays fast while workers are
busy.

## Resource sizing

CPU-bound ISCC processing runs in a pool of worker processes. `ISCC_WEB_MAX_WORKERS` caps the
pool size and defaults to the CPU count. All workers start with the service and load the
iscc-sdk toolchain and the iscc-sct/iscc-sci ONNX models up front — roughly 1 GB of RAM per
worker on CPU. Set `ISCC_WEB_MAX_WORKERS` explicitly on many-core or memory-constrained hosts.

Also budget for uploads: files up to `ISCC_WEB_MAX_UPLOAD_SIZE` (default 1 GB) are kept on disk
inside the container until the cleanup task removes them after `ISCC_WEB_STORAGE_EXPIRY` seconds.

## Several instances

Each instance keeps its uploads in its own local storage. Requests that refer to an earlier upload
by its `media_id` only work on the instance that received the upload:

- `GET /api/v1/iscc/{media_id}`
- `GET /api/v1/media/{media_id}` and `DELETE /api/v1/media/{media_id}`
- `GET /api/v1/metadata/{media_id}` and `POST /api/v1/metadata/{media_id}`

Deployments with more than one instance therefore need a load balancer with **session affinity**
("sticky sessions"), which routes all requests of a client to the same instance. Requests without a
`media_id` (`POST /api/v1/iscc`, `GET /api/v1/explain/{iscc}`, `POST /api/v1/simprint`) work on any
instance.

Base the affinity on the client IP address (often called IP hash or source IP affinity): it maps
each client to one instance and works for browsers and scripts alike. If the load balancer itself
runs behind another proxy, base it on the forwarded client IP rather than the address of the
connecting proxy. Cookie-based affinity is an alternative for browser-only use, but clients that do
not keep cookies, such as most scripts, would not stick to an instance. When instances are added or
removed, some clients are mapped to a different instance and can no longer reach their earlier
uploads; they have to upload again.

Each instance loads its own worker pool and models, so size the host for the combined memory (see
[Resource sizing](#resource-sizing)).
