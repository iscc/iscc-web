# -*- coding: utf-8 -*-
import uvicorn
from blacksheep import Application
import pathlib

__all__ = ["app"]
HERE = pathlib.Path(__file__).parent.absolute()
STATIC = HERE / "static"

app = Application(show_error_details=True, debug=True)
app.serve_files(STATIC, root_path="", fallback_document="index.html")


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
