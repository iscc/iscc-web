# ISCC - Generator Microservice

[![Tests](https://github.com/iscc/iscc-web/actions/workflows/test-backend.yaml/badge.svg)](https://github.com/iscc/iscc-web/actions/workflows/test-backend.yaml)

## About `iscc-web`

`iscc-web` is a microservice for generating **International Standard Content Codes**
([ISCC](https://iscc.codes)) for media files. A public instance of this service is available at
https://iscc.io

## Overview

<img align="left" width="200" src="docs/iscc-web-rest-api.jpg?raw=true">

**REST API**

The microservice provides a REST API for generating ISCCs. The endpoints support file
upload/download, metadata extraction/embedding and ISCC processing.<br>

Files uploaded for processing are automatically deleted after a configurable timeout.
An interactive API documentation is available at [/docs](https://iscc.io/docs)<br><br>

<img align="left" width="200" src="docs/iscc-web-vue-frontend.jpg?raw=true">

**Demo Frontend**

The service also hosts a [Vue.js](https://vuejs.org/) based demo frontend that shows how to
upload media files, geneerate ISCCs, embed metadata, and compare ISCCs.<br><br><br>

## Configuration

Configuration is handled by environment variables:

**Backend:**

-   `ISCC_WEB_ENVIRONMENT`: `development` or `production` (default: `development`).
-   `ISCC_WEB_SITE_ADDRESS`: public site address (default: http://localhost:8000).
-   `ISCC_WEB_PRIVATE_FILES`: restrict file downloads to original uploader (default: true).
-   `ISCC_WEB_MAX_UPLOAD_SIZE`: max file size per file upload in bytes (default: 1073741824).
-   `ISCC_WEB_STORAGE_EXPIRY`: delete uploaded files after x seconds (default 3600).
-   `ISCC_WEB_CLEANUP_INTERVAL`: interval in seconds to run file cleanup task. Use 0 to deactivate (default: 600).
-   `ISCC_WEB_LOG_LEVEL`: set log level (default: `DEBUG`).
-   `ISCC_WEB_IO_READ_SIZE`: file read chunk size (default: 2097152).
-   `ISCC_WEB_SENTRY_DSN`: optional sentry dsn for error reporting (default: emtpy string).


The production Dockerfile also supports `PORT` to configure gunicorns default port. (see [gunicorn
docs](https://docs.gunicorn.org/en/stable/settings.html?highlight=PORT#bind) for details)

## Development

Both the backend and frontend servers need to run in parallel.

### Backend

Having a [Python](https://python.org) 3.8+ environment with [Poetry](https://python-poetry.org/) do:

```shell
git clone https://github.com/iscc/iscc-web.git
cd iscc-web
poetry install
iscc-web
```

Access the app at http://localhost:8000
Api documentation is at /docs

Before committing any changes run code formatting and tests with:

```
poe all
```

### Frontend

Install Node.js with [asdf](https://asdf-vm.com/) or see [.tool-versions](.tool-versions) for the correct version. Packages are managed by
[pnpm](https://pnpm.io/installation).

Run `pnpm install` to install the frontend dependencies.

Run `pnpm run dev` to run the development server.

# Special thanks to the developers of

-   [Blacksheep](https://github.com/Neoteroi/BlackSheep) (see [benchmarks](http://klen.github.io/py-frameworks-bench/))
-   [Schemathesis](https://github.com/schemathesis/schemathesis)


## Deployment

There are many options to deploy a Python [ASGI](https://asgi.readthedocs.io/en/latest/) application.
Here is a simple docker-compose based standalone deployment with automatic SSL/TLS configuration.
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
```.env
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

You can also configure iscc-core and iscc-sdk dependencies. For example to activate generation
of granular fingerprints (currently only implemented for text) add the following to your .env:

```.env
ISCC_SDK_GRANULAR=true
```

For available environment variables see:

- https://sdk.iscc.codes/options/
- https://core.iscc.codes/options/options/

### docker-compose.yaml

```yaml
version: "3.8"

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
      - "80:80"
      - "443:443"
      - "443:443/udp"
    depends_on:
      - app
```

Make sure you have a DNS entry pointing to your servers IP and set the correct
`ISCC_WEB_SITE_ADDRESS` in your `.env` file. You should also change `ISCC_WEB_SITE_EMAIL`.

### Start the app
`docker-compose up -d`

### Watch logs
`docker-compose logs -f`

### Update to the latest docker image
```shell
docker-compose pull
docker-compose up -d
```
