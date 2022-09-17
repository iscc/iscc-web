# -*- coding: utf-8 -*-
from pathlib import Path
from iscc_web import opts
from iscc_web.api.models import UploadMeta
import iscc_core as ic
import shutil
from aiofiles.os import wrap, mkdir, rename
import aiofile
from typing import Tuple

copyfile = wrap(shutil.copyfile)
rmtree = wrap(shutil.rmtree)


class FileHandler:
    @staticmethod
    def new_media_id() -> str:
        return ic.Flake().string.lower()

    @staticmethod
    def package_dir(media_id: str) -> Path:
        """Path to folder for a single media asset and its metadata."""
        return opts.media_path / media_id

    async def create_package(self) -> Tuple[str, Path]:
        """Create new media package folder"""
        media_id = self.new_media_id()
        package_path = self.package_dir(media_id=media_id)
        await mkdir(self.package_dir(media_id))
        # TODO set permission mode
        return media_id, package_path

    async def delete_package(self, media_id: str) -> None:
        """Delete entire package folder"""
        await rmtree(self.package_dir(media_id))

    def meta_path(self, media_id: str) -> Path:
        """Path to json file with file upload metadata."""
        return self.package_dir(media_id) / f"{media_id}.meta.json"

    async def file_path(self, media_id: str) -> Path:
        """Path to media file. Reads and constructs path from upload metadata."""
        meta = await self.read_meta(media_id)
        return self.package_dir(media_id) / meta.clean_file_name

    def iscc_path(self, media_id: str) -> Path:
        """Path to json file with iscc metadata."""
        return self.package_dir(media_id) / f"{media_id}.iscc.json"

    async def write_meta(self, media_id: str, file_meta: UploadMeta) -> None:
        """Write file metadata."""
        async with aiofile.async_open(self.meta_path(media_id), "wb") as infile:
            await infile.write(file_meta.json(indent=2).encode("utf-8"))

    async def read_meta(self, media_id) -> UploadMeta:
        """Read file metadata."""
        async with aiofile.async_open(self.meta_path(media_id), "rb") as infile:
            data = await infile.read()
        return UploadMeta.parse_raw(data)

    # async def has_permission(self, client: str, media_id: str) -> bool:
    #     """Check if user has permission to access file"""
    #     meta = await self.read_meta(media_id)
    #     if meta.client_ip == client:
    #         return True
    #     return False

    @staticmethod
    async def move_file(src: str, dst: str):
        """Move file from source to destination"""
        await rename(src, dst)

    @staticmethod
    async def copy_file(src, dst):
        """Copy file from source to destination"""
        await copyfile(src, dst)
