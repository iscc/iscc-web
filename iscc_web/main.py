# -*- coding: utf-8 -*-
import uvicorn
from blacksheep import Application, Route
import pathlib
from iscc_web.api.pool import Pool

__all__ = ["app"]
HERE = pathlib.Path(__file__).parent.absolute()
STATIC = HERE / "static"


app = Application(show_error_details=False, debug=True)
app.serve_files(STATIC)
app.serve_files(STATIC / "docs", root_path="/docs", extensions={".html", ".yaml"})
app.serve_files(STATIC / "images", root_path="/images")
app.services.add_singleton(Pool)
Route.value_patterns["mid"] = r"[a-v0-9]{13}$"
Route.value_patterns["iscc"] = r"ISCC:[A-Z2-7]{10,73}$"


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
