# -*- coding: utf-8 -*-
import uvicorn
from blacksheep import Application, Route
import pathlib

__all__ = ["app"]
HERE = pathlib.Path(__file__).parent.absolute()
STATIC = HERE / "static"

app = Application(show_error_details=True, debug=True)
app.serve_files(
    STATIC,
    root_path="",
    extensions={".html", ".yaml", ".ico", ".js", ".css"},
)
app.serve_files(STATIC / "docs", root_path="/docs", extensions={".html", ".yaml"})

app.serve_files(STATIC / "redocs", root_path="/redocs", extensions={".html"})


Route.value_patterns["mid"] = r"[0-9a-q]+=*"


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
