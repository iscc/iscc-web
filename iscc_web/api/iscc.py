# -*- coding: utf-8 -*-
import asyncio
from subprocess import CalledProcessError
import aiofile
from blacksheep import Request, ContentDispositionType, Response
from blacksheep.server.controllers import ApiController, post, get
from iscc_web.options import opts
from iscc_web.api.pool import Pool
from iscc_web.api.mixins import FileHandler
import iscc_sdk as idk


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
    async def create_iscc(self, request: Request, pool: Pool):
        """Upload and create ISCC-CODE for media asset."""

        result = await self.handle_upload(request)
        if isinstance(result, Response):
            return result

        package_dir = self.package_dir(result.media_id)
        file_path = package_dir / result.clean_file_name

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
        result_path = package_dir / f"{result.media_id}.iscc.json"
        async with aiofile.async_open(result_path, "wb") as outfile:
            await outfile.write(iscc_obj.json(indent=2).encode("utf-8"))

        # Create response
        location_header = f"/api/v1/media/{result.media_id}".encode("ascii")
        location = f"{opts.base_url}/media/{result.media_id}"
        iscc_obj.media_id = result.media_id
        iscc_obj.content = location
        return self.created(location=location_header, value=iscc_obj.dict(skip_defaults=False))
