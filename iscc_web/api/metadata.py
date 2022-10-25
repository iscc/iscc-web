import asyncio
from blake3 import blake3
from aiofiles.ospath import exists
from blacksheep import Response, Request
from blacksheep.server.controllers import ApiController, get, post
from iscc_web.api.common import base_url
from iscc_web.api.schema import InlineMetadata
from iscc_web.api.pool import Pool
from iscc_web.api.mixins import FileHandler
from iscc_web.options import opts
import iscc_sdk as idk


class Metadata(ApiController, FileHandler):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @get("{mid:media_id}")
    async def extract(self, media_id: str, pool: Pool):
        """Extract metadata from media"""
        try:
            file_path = await self.file_path(media_id)
        except FileNotFoundError:
            return self.not_found("File metadata not found")

        if not await exists(file_path):
            return self.not_found("File not found")

        loop = asyncio.get_event_loop()
        metadata = await loop.run_in_executor(pool, idk.extract_metadata, file_path)
        cleaned = metadata.dict(
            include={
                "name",
                "description",
                "meta",
                "creator",
                "license",
                "acquire",
                "credit",
                "rights",
            }
        )
        obj = InlineMetadata(**cleaned)
        return self.json(obj.dict(exclude_none=True))

    @post("{mid:media_id}")
    async def embed(self, request: Request, media_id: str, meta: InlineMetadata, pool: Pool):
        """Embed metadata in media file."""
        try:
            upload_meta = await self.read_meta(media_id)
        except FileNotFoundError:
            return self.not_found("File metadata not found")

        if opts.private_files:
            if upload_meta.user != blake3(request.client_ip.encode("ascii")).hexdigest():
                return self.forbidden("Forbidden - Only accessible by original uploader.")

        file_path = self.package_dir(media_id) / upload_meta.clean_file_name
        if not await exists(file_path):
            return self.not_found("File not found")

        # Embed metadata
        loop = asyncio.get_event_loop()
        try:
            genfile = await loop.run_in_executor(pool, idk.embed_metadata, file_path, meta)
        except Exception as e:
            return self.status_code(422, f"Unprocessable Entity - Failed to embed metadata {e}")

        if genfile is None:
            return self.status_code(422, f"Unprocessable Entity - Failed to embed metadata.")

        # Move to new media file
        new_media_id, media_dir = await self.create_package()
        new_file_path = media_dir / upload_meta.clean_file_name
        await self.move_file(genfile, new_file_path)

        # Store upload metadata for new file
        upload_meta.media_id = new_media_id
        await self.write_meta(new_media_id, upload_meta)

        # Process ISCC for new media file
        proc_result = await self.process_iscc(new_file_path)
        if isinstance(proc_result, Response):
            return proc_result

        # Create response
        location = f"{base_url(request)}/media/{new_media_id}"
        location_header = f"/api/v1/media/{new_media_id}".encode("ascii")
        proc_result.media_id = new_media_id
        proc_result.content = location
        return self.created(location=location_header, value=proc_result.dict(skip_defaults=False))
