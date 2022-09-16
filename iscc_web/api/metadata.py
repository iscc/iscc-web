# -*- coding: utf-8 -*-
import asyncio
from blacksheep.server.controllers import ApiController, get, post

from iscc_web.api.schema import Metadata
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
        return metadata.json(include={"name", "description", "meta"})

    @post("mid:media_id")
    async def embed(self, media_id: str, metadata: Metadata):
        """Embed metadata in media file"""
        if not await self.file_exists(media_id):
            return self.not_found()
        idk.embed_metadata()
