import aiofiles
from aiofiles.ospath import exists
from blacksheep import Request, Response
from blacksheep.server.controllers import ApiController, post, get, delete
from blake3 import blake3

from iscc_web.options import opts
from iscc_web.api.common import base_url
from iscc_web.api.mixins import FileHandler


class Media(ApiController, FileHandler):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @post()
    async def upload_file(self, request: Request):
        """Upload file"""

        result = await self.handle_upload(request)
        if isinstance(result, Response):
            return result

        media_id = result.media_id

        location_header = f"/api/v1/media/{media_id}".encode("ascii")
        location = f"{base_url(request)}/media/{media_id}"

        return self.created(
            location=location_header, value={"content": location, "media_id": media_id}
        )

    @get("{mid:media_id}")
    async def download_file(self, request: Request, media_id: str):
        """Download file"""
        try:
            meta = await self.read_meta(media_id)
        except FileNotFoundError:
            return self.not_found("File metadata not found")

        if opts.private_files:
            if meta.user != blake3(request.client_ip.encode("ascii")).hexdigest():
                return self.forbidden("Forbidden - Only accessible by original uploader.")

        file_path = (opts.media_path / media_id) / meta.clean_file_name

        if not await exists(file_path):
            return self.not_found("File not found")

        async def provider():
            async with aiofiles.open(file_path, "rb") as infile:
                chunk = await infile.read(opts.io_read_size)
                while chunk:
                    yield chunk
                    chunk = await infile.read(opts.io_read_size)

        return self.file(provider, content_type=meta.content_type, file_name=meta.clean_file_name)

    @delete("{mid:media_id}")
    async def delete_file(self, request: Request, media_id: str):
        """Delete file"""
        try:
            meta = await self.read_meta(media_id)
        except FileNotFoundError:
            return self.not_found("File metadata not found")

        if opts.private_files:
            if meta.user != blake3(request.client_ip.encode("ascii")).hexdigest():
                return self.forbidden("Forbidden - Only accessible by original uploader.")

        try:
            await self.delete_package(media_id)
        except FileNotFoundError:
            return self.not_found("File not found")
        return self.no_content()
