# -*- coding: utf-8 -*-
import uvicorn
from blacksheep import Application
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.openapi.ui import ReDocUIProvider
from openapidocs.v3 import Info
import pathlib

__all__ = ["app"]
HERE = pathlib.Path(__file__).parent.absolute()
STATIC = HERE / "static"

app = Application(show_error_details=True, debug=True)
app.serve_files(STATIC, root_path="", fallback_document="index.html")

docs = OpenAPIHandler(info=Info(title="ISCC-WEB API", version="0.0.1"))
docs.ui_providers.append(ReDocUIProvider())
docs.bind_app(app)


def main():
    uvicorn.run(
        "iscc_web.main:app",
        host="localhost",
        port=8000,
        log_level="debug",
        reload=True,
        server_header=False,
    )


if __name__ == "__main__":
    main()
