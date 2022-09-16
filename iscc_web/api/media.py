import base64
import binascii
import aiofiles
from blacksheep import Request
from blacksheep.server.controllers import ApiController, post, get, delete
from iscc_web import opts
from iscc_web.api.mixins import FileHandler
from iscc_web.api.models import UploadMeta


class Media(ApiController, FileHandler):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @post()
    async def upload_file(self, request: Request):
        """Upload file"""

        # Get header data
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

        # Create ID
        media_id = self.new_media_id()
        file_meta = UploadMeta(
            file_name=file_name,
            content_type=content_type,
            client_ip=request.client_ip,
        )

        # Save Uploaded data
        await self.write_meta(media_id, file_meta)
        async with aiofiles.open(self.file_path(media_id), "ab") as outf:
            async for chunk in request.stream():
                await outf.write(chunk)

        location = f"/api/v1/media/{media_id}"
        # Todo return UploadResponse
        return self.created(
            location=location.encode("ascii"), value={"url": location, "media_id": media_id}
        )

    @get("{mid:media_id}")
    async def download_file(self, media_id: str):
        """Download file"""
        if not await self.file_exists(media_id):
            return self.not_found()

        meta = await self.read_meta(media_id)

        async def provider():
            async with aiofiles.open(self.file_path(media_id), "rb") as infile:
                chunk = await infile.read(opts.io_read_size)
                while chunk:
                    yield chunk
                    chunk = await infile.read(opts.io_read_size)

        return self.file(provider, content_type=meta.content_type, file_name=meta.file_name)

    @delete("{mid:media_id}")
    async def delete_file(self, media_id: str):
        """Delete file"""
        if not await self.file_exists(media_id):
            return self.not_found()
        await self.delete_files(media_id)
        return self.no_content()
