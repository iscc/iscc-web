# iscc-web - Minimal ISCC Generator Web Application

# Configuration

Configuration is handled by environment variables:

**Backend:**

-   `ISCC_WEB_HOST`: defines on which host the HTTP server will bind to (default: localhost)
-   `ISCC_WEB_PORT`: the port the HTTP server will bind to (default: 8000)
-   `ISCC_WEB_ENVIRONMENT`: `development` or `production` (default: `development`)
-   `ISCC_WEB_PRIVATE_FILES`: restrict file downloads to original uploader (default: true)

The production Dockerfile also supports `PORT` to configure gunicorns default port. (see [gunicorn
docs](https://docs.gunicorn.org/en/stable/settings.html?highlight=PORT#bind) for details)

# Development

Both the backend and frontend servers need to run in parallel.

## Backend

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

## Frontend

Install Node.js with [asdf](https://asdf-vm.com/) or see [.tool-versions](.tool-versions) for the correct version. Packages are managed by
[pnpm](https://pnpm.io/installation).

Run `pnpm install` to install the frontend dependencies.

Run `pnpm run dev` to run the development server.

# Special thanks to the developers of

-   [Blacksheep](https://github.com/Neoteroi/BlackSheep) (see [benchmarks](http://klen.github.io/py-frameworks-bench/))
-   [Schemathesis](https://github.com/schemathesis/schemathesis)
