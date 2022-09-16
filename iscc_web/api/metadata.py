import asyncio
from blacksheep.server.controllers import ApiController, get, post
from iscc_web.api.schema import InlineMetadata
from iscc_web.api.pool import Pool
from iscc_web import FileHandler
import iscc_sdk as idk


class Metadata(ApiController, FileHandler):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @get("{media_id}")
    async def extract(self, media_id: str, pool: Pool):
        """Extract metadata from media"""
        if not await self.file_exists(media_id):
            return self.not_found()

        file_path = self.file_path(media_id)
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

    @post("{media_id}")
    async def embed(self, media_id: str, meta: InlineMetadata, pool: Pool):
        """Embed metadata in media file.

        TODO: Can only be called by original uploader
        TODO: Should return a list of actually embedded fields
        TODO: use aiofile (real async file access)
        """
        if not await self.file_exists(media_id):
            return self.not_found()
        # embed metadata
        infile = self.file_path(media_id)
        loop = asyncio.get_event_loop()
        genfile = await loop.run_in_executor(pool.executor, idk.embed_metadata, infile, meta)

        # move to new media file
        new_media_id = self.new_media_id()
        outfile = self.file_path(new_media_id)
        await self.move_file(genfile, outfile)

        # copy upload metadata
        src, dst = self.meta_path(media_id), self.meta_path(new_media_id)
        await self.copy_file(src, dst)

        location = f"/api/v1/media/{new_media_id}"
        return self.created(location=location, value={"url": location, "media_id": new_media_id})
