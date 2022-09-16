# -*- coding: utf-8 -*-
import asyncio
from blacksheep.server.controllers import ApiController, get
from iscc_web.api.pool import Pool
from iscc_web import opts, FileHandler
import iscc_sdk as idk
from aiofiles.os import path


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

    @staticmethod
    def file_path(media_id: str) -> str:
        """Construct file path for media_id"""
        return (opts.media_path / media_id).as_posix()

    async def file_exists(self, media_id):
        return await path.exists(self.file_path(media_id))
