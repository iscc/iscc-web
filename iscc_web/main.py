# -*- coding: utf-8 -*-
import uvicorn
from blacksheep import Application, Route
from blacksheep.server.templating import use_templates
from jinja2 import PackageLoader
import pathlib
from .vite import register_extensions
from .options import opts
from iscc_web.api.pool import Pool

__all__ = ["app"]
HERE = pathlib.Path(__file__).parent.absolute()
STATIC = HERE / "static"


app = Application(show_error_details=False, debug=True)
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


def main():
    uvicorn.run(
        "iscc_web.main:app",
        host=opts.host,
        port=int(opts.port),
        log_level="debug",
        reload=True if opts.environment == "development" else False,
        server_header=False,
    )


if __name__ == "__main__":
    main()
