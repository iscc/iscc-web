# -*- coding: utf-8 -*-
import iscc_web as iw
import blacksheep as bs
import uvicorn
from aiofiles.os import path


app = bs.Application()


@app.router.get()
async def home():
    return f"Hello, World!"


# TUS protocol handlers


@app.router.options("/tus")
async def tus_options():
    response = bs.no_content()
    response.add_header(b"Tus-Resumable", b"1.0.0")
    response.add_header(b"Tus-Version", b"1.0.0")
    response.add_header(b"Tus-Max-Size", b"1073741824")
    response.add_header(b"Tus-Extension", b"creation")
    return response


@app.router.head("/tus/{media_id}")
async def tus_head(media_id: str):
    if not await path.exists(iw.opts.media_path / media_id):
        response = bs.not_found()
        response.add_header(b"Cache-Control", b"no-store")
        return response


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
