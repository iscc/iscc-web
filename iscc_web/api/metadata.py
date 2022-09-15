# -*- coding: utf-8 -*-
from blacksheep.server.controllers import ApiController, get
from iscc_web import opts
import iscc_sdk as idk
from aiofiles.os import path


class Metadata(ApiController):
    @classmethod
    def version(cls) -> str:
        return "v1"

    @get("{mid:media_id}")
    async def extract(self, media_id: str):
        """Extract metadata from media"""
        if not await self.file_exists(media_id):
            return self.not_found()
        metadata = idk.extract_metadata(self.file_path(media_id))
        return metadata.json(include={"name", "description", "meta"})

    @staticmethod
    def file_path(media_id: str) -> str:
        """Construct file path for media_id"""
        return (opts.media_path / media_id).as_posix()

    async def file_exists(self, media_id):
        return await path.exists(self.file_path(media_id))
