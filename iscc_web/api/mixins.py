# -*- coding: utf-8 -*-
from iscc_web import opts
from iscc_web.api.models import UploadMeta
import aiofiles
from aiofiles.os import path, remove, rename
import iscc_core as ic
import shutil
from aiofiles.os import wrap

copyfile = wrap(shutil.copyfile)


class FileHandler:
    @staticmethod
    def file_path(media_id: str) -> str:
        """Construct file path for media_id"""
        return (opts.media_path / media_id).as_posix()

    @staticmethod
    def meta_path(media_id: str) -> str:
        """Construct mdatadata path for media_id"""
        return (opts.media_path / f"{media_id}.json").as_posix()

    @staticmethod
    def new_media_id() -> str:
        return ic.Flake().string.lower()

    @staticmethod
    async def move_file(src: str, dst: str):
        """Move file from source to destination"""
        await rename(src, dst)

    @staticmethod
    async def copy_file(src: str, dst: str):
        """Copy file from source to destination"""
        await copyfile(src, dst)

    async def file_exists(self, media_id: str) -> bool:
        return await path.exists(self.file_path(media_id))

    async def delete_files(self, media_id: str) -> None:
        await remove(self.file_path(media_id))
        await remove(self.meta_path(media_id))

    async def write_meta(self, media_id: str, file_meta: UploadMeta) -> None:
        async with aiofiles.open(self.meta_path(media_id), "w") as infile:
            await infile.write(file_meta.json(indent=2))

    async def read_meta(self, media_id: str) -> UploadMeta:
        """Read file metadata"""
        async with aiofiles.open(self.meta_path(media_id), "rb") as infile:
            data = await infile.read()
        return UploadMeta.parse_raw(data)

    async def has_permission(self, client: str, media_id: str):
        """Check if user has permission to access file"""
