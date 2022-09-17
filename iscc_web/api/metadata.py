import asyncio

from aiofiles.ospath import exists
from blacksheep.server.controllers import ApiController, get, post
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
        metadata = await loop.run_in_executor(pool.executor, idk.extract_metadata, file_path)
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
    async def embed(self, media_id: str, meta: InlineMetadata, pool: Pool):
        """Embed metadata in media file.

        TODO: Can only be called by original uploader
        TODO: Should return a list of actually embedded fields
        """
        try:
            file_path = await self.file_path(media_id)
        except FileNotFoundError:
            return self.not_found("File metadata not found")

        if not await exists(file_path):
            return self.not_found("File not found")

        # embed metadata
        loop = asyncio.get_event_loop()
        genfile = await loop.run_in_executor(pool.executor, idk.embed_metadata, file_path, meta)

        # move to new media file
        new_media_id, media_dir = await self.create_package()
        outfile = media_dir / file_path.name
        await self.move_file(genfile, outfile)

        # copy upload metadata
        src, dst = self.meta_path(media_id), self.meta_path(new_media_id)
        await self.copy_file(src, dst)
        location = f"{opts.base_url}/media/{new_media_id}"
        location_header = f"/api/v1/media/{new_media_id}".encode("ascii")
        return self.created(
            location=location_header, value={"content": location, "media_id": new_media_id}
        )
