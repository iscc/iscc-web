import base64
import binascii
import aiofiles
import iscc_core as ic
from blacksheep import Request
from blacksheep.server.controllers import ApiController, post, get, delete
from pydantic import BaseModel
from iscc_web.options import opts
from aiofiles.os import path, remove


class FileMeta(BaseModel):

    file_name: str
    content_type: str


class Media(ApiController):
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

        content_type = request.content_type().decode("ascii")

        # Create ID
        media_id = ic.Flake().string.lower()
        file_meta = FileMeta(content_type=content_type, file_name=file_name)

        # Save Uploaded data
        await self.write_meta(media_id, file_meta)
        async with aiofiles.open(self.file_path(media_id), "ab") as outf:
            async for chunk in request.stream():
                await outf.write(chunk)

        location = f"/api/v1/media/{media_id}"
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

        await remove(self.file_path(media_id))
        await remove(self.meta_path(media_id))
        return self.no_content()

    @staticmethod
    def file_path(media_id: str) -> str:
        """Construct file path for media_id"""
        return (opts.media_path / media_id).as_posix()

    @staticmethod
    def meta_path(media_id: str) -> str:
        """Construct mdatadata path for media_id"""
        return (opts.media_path / f"{media_id}.json").as_posix()

    async def file_exists(self, media_id):
        return await path.exists(self.file_path(media_id))

    async def write_meta(self, media_id: str, file_meta: FileMeta) -> None:
        async with aiofiles.open(self.meta_path(media_id), "w") as infile:
            await infile.write(file_meta.json(indent=2))

    async def read_meta(self, media_id: str) -> FileMeta:
        """Read file metadata"""
        async with aiofiles.open(self.meta_path(media_id), "rb") as infile:
            data = await infile.read()
        return FileMeta.parse_raw(data)
