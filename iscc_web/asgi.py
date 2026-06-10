"""ASGI entrypoint for uvicorn dev server."""

from iscc_web.main import app

application = app
