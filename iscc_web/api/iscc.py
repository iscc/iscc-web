# -*- coding: utf-8 -*-
import aiofile
import requests
from blacksheep import Request, ContentDispositionType, Response
from blacksheep.server.controllers import ApiController, post, get
from iscc_web.api.pool import Pool
from iscc_web.api.mixins import FileHandler
from iscc_web.api.common import base_url
from loguru import logger as log


class Iscc(ApiController, FileHandler):
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
    async def create_iscc(self, request: Request):
        """Upload and create ISCC-CODE for media asset."""

        file_name_base64 = request.get_first_header(b"X-Upload-Filename")
        if not file_name_base64:
            result = await self.handle_url(request)
            if isinstance(result, Response):
                return result
        else:
            result = await self.handle_upload(request)
            if isinstance(result, Response):
                return result

        package_dir = self.package_dir(result.media_id)
        file_path = package_dir / result.clean_file_name

        log.info(f"Start Processing: {result.media_id}", enqueue=True)
        proc_result = await self.process_iscc(file_path)
        log.info(f"Finished Processing: {result.media_id}", enqueue=True)

        if isinstance(proc_result, Response):
            return proc_result

        # Create response
        location_header = f"/api/v1/media/{result.media_id}".encode("ascii")
        location = f"{base_url(request)}/media/{result.media_id}"
        proc_result.media_id = result.media_id
        proc_result.content = location
        return self.created(location=location_header, value=proc_result.dict(skip_defaults=False))
