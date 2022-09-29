# -*- coding: utf-8 -*-
import asyncio
import uvicorn
from blacksheep import Application, Route
from blacksheep.server.templating import use_templates
from jinja2 import PackageLoader
import pathlib
from iscc_web.vite import register_extensions
from iscc_web.options import opts
from iscc_web.api.pool import Pool
from loguru import logger as log
from iscc_web.cleanup import cleanup_task

__all__ = ["app"]
HERE = pathlib.Path(__file__).parent.absolute()
STATIC = HERE / "static"


app = Application(show_error_details=opts.debug, debug=opts.debug)
app.serve_files(STATIC, root_path="/static")
app.serve_files(STATIC / "docs", root_path="/docs", extensions={".html", ".yaml"})
app.serve_files(STATIC / "images", root_path="/images")
app.services.add_singleton(Pool)
Route.value_patterns["mid"] = r"[a-v0-9]{13}$"
Route.value_patterns["iscc"] = r"ISCC:[A-Z2-7]{10,73}$"

get = app.router.get

view = use_templates(app, loader=PackageLoader("iscc_web", "templates"), enable_async=True)
register_extensions(app)


@get("/")
async def index():
    return await view("index", {})


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
        log.info(
            f"Install cleanup task with {opts.cleanup_interval} seconds interval", enqueue=True
        )
        asyncio.get_event_loop().create_task(cleanup_task())


@app.on_stop
async def shutdown(application) -> None:
    log.info("Shutdown initiated. Waiting to finish pool", enqueue=True)
    service = app.service_provider[Pool]
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
