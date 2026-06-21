# -*- coding: utf-8 -*-
from typing import Optional

import aiofile
from blacksheep import Request, ContentDispositionType, Response
from blacksheep.server.controllers import APIController, post, get
from iscc_web import opts
from iscc_web.api.mixins import FileHandler
from iscc_web.api.common import base_url
from loguru import logger as log


class Iscc(APIController, FileHandler):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @get("{mid:media_id}")
    async def get_iscc(self, media_id: str):
        """Get previously calculated ISCC-CODE for media file."""
        try:
            async with aiofile.async_open(self.iscc_path(media_id), "rb") as infile:
                content = await infile.read()
        except FileNotFoundError:
            return self.not_found("No ISCC-CODE found.")
        return self.file(
            content,
            content_type="application/json",
            content_disposition=ContentDispositionType.INLINE,
        )

    @post()
    async def create_iscc(self, request: Request, semantic: Optional[bool] = None, granular: Optional[bool] = None):
        """
        Upload and create ISCC-CODE for media asset.

        An omitted `semantic` query param resolves to the backend default (ISCC_WEB_SEMANTIC_DEFAULT,
        off by default); an omitted `granular` param defers to the iscc-sdk default (on unless
        configured otherwise via ISCC_SDK_GRANULAR). Explicit values override per request.
        """

        if semantic is None:
            semantic = opts.semantic_default

        result = await self.handle_upload(request)
        if isinstance(result, Response):
            return result

        package_dir = self.package_dir(result.media_id)
        file_path = package_dir / result.clean_file_name

        log.info(f"Start Processing: {result.media_id}", enqueue=True)
        proc_result = await self.process_iscc(file_path, semantic=semantic, granular=granular)
        log.info(f"Finished Processing: {result.media_id}", enqueue=True)

        if isinstance(proc_result, Response):
            return proc_result

        # Create response
        location_header = f"/api/v1/media/{result.media_id}".encode("ascii")
        location = f"{base_url(request)}/media/{result.media_id}"
        proc_result.media_id = result.media_id
        proc_result.content = location
        return self.created(location=location_header, value=proc_result.model_dump(exclude_none=True, by_alias=True))
