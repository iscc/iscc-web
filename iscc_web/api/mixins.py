# -*- coding: utf-8 -*-
import base64
import binascii
from pathlib import Path
from blacksheep import Request, Response
from blake3 import blake3
from iscc_web import opts
from iscc_web.api.models import UploadMeta
import iscc_core as ic
import shutil
from aiofiles.os import wrap, mkdir, rename
import aiofile
from typing import Tuple, Union


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

    @staticmethod
    async def move_file(src: str, dst: str):
        """Move file from source to destination"""
        await rename(src, dst)

    @staticmethod
    async def copy_file(src, dst):
        """Copy file from source to destination"""
        await copyfile(src, dst)

    async def handle_upload(self, request: Request) -> Union[UploadMeta, Response]:
        """
        Handle file upload.

        - Validates header data
        - Creates a new package dir as upload location
        - Stores upload metadata from the header in the package directory
        - Stores the upload file in the package directory
        - Returns either UploadMeta on success or Response on failure
        """
        # Read and check header data
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

        # TODO check Content-Length

        # Create package directory
        media_id, package_dir = await self.create_package()

        # Store file metadata
        user = blake3(request.client_ip.encode("ascii")).hexdigest()
        upload_meta = UploadMeta(
            media_id=media_id,
            file_name=file_name,
            content_type=content_type,
            user=user,
        )
        await self.write_meta(media_id, upload_meta)

        # Store file upload
        file_path = package_dir / upload_meta.clean_file_name
        async with aiofile.async_open(file_path, "wb") as outfile:
            async for chunk in request.stream():
                await outfile.write(chunk)

        return upload_meta
