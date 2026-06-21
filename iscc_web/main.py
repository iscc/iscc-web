# -*- coding: utf-8 -*-
import asyncio
import uvicorn
from blacksheep import Application, Route
from blacksheep.server.responses import view_async
from jinja2 import PackageLoader
import pathlib
from iscc_web.vite import register_extensions
from iscc_web.options import opts
from iscc_web.api.pool import Pool
from loguru import logger as log
from iscc_web.cleanup import cleanup_task
from blacksheep.server.rendering.jinja2 import JinjaRenderer
from blacksheep.settings.html import html_settings

__all__ = ["app"]
HERE = pathlib.Path(__file__).parent.absolute()
STATIC = HERE / "static"


app = Application(show_error_details=opts.debug)
if opts.cors_origins:
    # Cross-origin support for frontends hosted on other domains: X-Upload-Filename is required
    # for uploads; Location and Content-Disposition let cross-origin clients read upload
    # locations and download filenames. The service's own origin is always allowed - browsers
    # send an Origin header on same-origin POST/DELETE too, and BlackSheep rejects unlisted
    # origins with 400, which would break the bundled frontend.
    app.use_cors(
        allow_methods="GET POST DELETE",
        allow_headers="Content-Type X-Upload-Filename",
        allow_origins=f"{opts.cors_origins} {opts.site_origin}",
        expose_headers="Location Content-Disposition",
        max_age=300,
    )
renderer = JinjaRenderer(loader=PackageLoader("iscc_web", "templates"), enable_async=True)
register_extensions(renderer.env)
html_settings.use(renderer)
app.serve_files(STATIC, root_path="/static")
app.serve_files(STATIC / "docs", root_path="/docs", extensions={".html", ".yaml"})
app.serve_files(STATIC / "images", root_path="/images")
app.services.add_singleton(Pool)
Route.value_patterns["mid"] = r"[a-v0-9]{13}$"
Route.value_patterns["iscc"] = r"ISCC:[A-Z2-7]{10,73}$"

get = app.router.get


@get("/")
async def index():
    # Inject service config the frontend reads before mount (initial toggle state, storage
    # expiry for the privacy copy, etc.).
    config = {"semanticDefault": opts.ui_semantic_default, "storageExpiry": opts.storage_expiry}
    return await view_async("index", {"config": config})


async def logging_sink(msg):
    print(msg, end="")


@app.on_start
async def configure_logging(application: Application) -> None:
    log.remove()
    fmt = "{level: <10}{time:YYYY-MM-DDTHH:mm:ss} - {function}:{line} - {message}"
    log.add(logging_sink, format=fmt, level=opts.log_level)


@app.on_start
async def configure_cleanup(application):
    if opts.cleanup_interval == 0:
        log.warning("Upload cleanup deactivated", enqueue=True)
    else:
        log.info(f"Install cleanup task with {opts.cleanup_interval} seconds interval", enqueue=True)
        asyncio.get_event_loop().create_task(cleanup_task())


@app.on_stop
async def shutdown(application) -> None:
    log.info("Shutdown initiated. Waiting to finish pool", enqueue=True)
    service = app.services.provider[Pool]
    service.shutdown(wait=True)
    log.info("Pool finished", enqueue=True)
    await log.complete()


def main():
    uvicorn.run(
        "iscc_web.main:app",
        host=opts.site_address.host,
        port=int(opts.site_address.port),
        log_level="debug",
        reload=True if opts.environment == "development" else False,
        server_header=False,
    )


if __name__ == "__main__":
    main()
