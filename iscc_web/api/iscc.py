# -*- coding: utf-8 -*-
import asyncio
import base64
import binascii
from subprocess import CalledProcessError

import aiofile
from blacksheep import Request, ContentDispositionType
from blacksheep.server.controllers import ApiController, post, get
from iscc_web.options import opts
from iscc_web.api.models import UploadMeta
from iscc_web.api.pool import Pool
from iscc_web.api.mixins import FileHandler
import iscc_sdk as idk


class Iscc_Code(ApiController, FileHandler):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @get("{mid:media_id}")
    async def get_iscc_code(self, media_id: str):
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
    async def create_iscc_code(self, request: Request, pool: Pool):
        """Upload and create ISCC-CODE for media asset."""

        # Read and check header data
        file_name_base64 = request.get_single_header(b"X-Upload-Filename")
        try:
            file_name_data = base64.b64decode(file_name_base64, validate=True)
        except binascii.Error:
            return self.status_code(400, "Bad Request - X-Upload-Filename is not base64.")

        try:
            file_name = file_name_data.decode("utf-8", "strict")
        except UnicodeDecodeError:
            return self.status_code(400, "Bad Request - X-Uploaded-Filename is not UTF-8 encoded")

        if not file_name:
            return self.status_code(400, "Bad Request - X-Upload-Filename is empty")

        try:
            content_type = request.content_type().decode("ascii")
        except AttributeError:
            content_type = ""

        # TODO check Content-Length

        # Create package directory
        media_id, package_dir = await self.create_package()

        # Store file metadata
        ip = request.client_ip
        file_meta_obj = UploadMeta(file_name=file_name, content_type=content_type, client_ip=ip)
        await self.write_meta(media_id, file_meta_obj)

        # Store file upload
        file_path = package_dir / file_meta_obj.clean_file_name
        async with aiofile.async_open(file_path, "wb") as outfile:
            async for chunk in request.stream():
                await outfile.write(chunk)

        # Process ISCC
        loop = asyncio.get_event_loop()
        try:
            iscc_obj = await loop.run_in_executor(
                pool.executor, idk.code_iscc, file_path.as_posix()
            )
        except CalledProcessError:
            return self.status_code(422, "ISCC processsing error.")
        except idk.IsccUnsupportedMediatype:
            return self.status_code(422, "ISCC unsupported mediatype.")

        # Store ISCC processing result
        result_path = package_dir / f"{media_id}.iscc.json"
        async with aiofile.async_open(result_path, "wb") as outfile:
            await outfile.write(iscc_obj.json(indent=2).encode("utf-8"))

        # Create response
        location_header = f"/api/v1/media/{media_id}".encode("ascii")
        location = f"{opts.base_url}/media/{media_id}"
        iscc_obj.media_id = media_id
        iscc_obj.content = location
        return self.created(location=location_header, value=iscc_obj.dict(skip_defaults=False))
