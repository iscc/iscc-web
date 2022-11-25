# -*- coding: utf-8 -*-
import asyncio
import base64
import binascii
import os
import requests
from urllib.parse import urlparse
from pathlib import Path
from blacksheep import Request, Response
from blake3 import blake3
from iscc_sdk import IsccMeta
from iscc_web import opts
from iscc_web.api.pool import Pool
from iscc_web.api.models import UploadMeta
import iscc_core as ic
from aiofiles.os import mkdir, rename
import aiofile
from typing import Tuple, Union, Optional
from iscc_web.main import app
import iscc_sdk as idk
from iscc_web.api.common import rmtree, copyfile
from loguru import logger as log


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
        content_length = request.get_first_header(b"Content-Length")
        if content_length:
            cl = int(content_length)
            if cl < 1 or cl > opts.max_upload_size:
                return self.status_code(
                    400, f"Bad Request - Content-Length must be > 0 and < {opts.max_upload_size}"
                )

        file_name_base64 = request.get_first_header(b"X-Upload-Filename")
        if not file_name_base64:
            return self.status_code(400, "Bad Request - Missing header X-Upload-Filename.")
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

    async def download_file(self, url, local_filename):
        try:
            with requests.head(url) as h:
                content_length = h.headers.get("Content-Length")
                if content_length:
                    cl = int(content_length)
                    log.info(
                        f"Content Length: {content_length} (max: {opts.max_upload_size})",
                        enqueue=True,
                    )
                    if cl < 1 or cl > opts.max_upload_size:
                        log.info(f"File too large.", enqueue=True)
                        return self.status_code(
                            400,
                            "Bad Request - Content-Length must be > 0 and <"
                            f" {opts.max_upload_size}",
                        )
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                return None
        except Exception as e:
            return self.status_code(422, str(e))

    async def handle_url(self, request: Request):
        """Download from provided URL and create ISCC-CODE for media asset."""
        data = await request.json()
        if data is None:
            return self.status_code(400, "Missing url in json payload")
        try:
            if data is None:
                return self.status_code(400, "Missing url in json payload")
            url = data["url"]
            if url is None or url == "":
                return self.status_code(400, "Url provided was invalid")
        except Exception as e:
            return self.status_code(400, "Something malformed with the json payload.")

        log.info(f"Requesting iscc code for URL: {url}", enqueue=True)
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)
        log.info(f"Requesting iscc code for FILE: {file_name}", enqueue=True)

        # Create package directory
        media_id, package_dir = await self.create_package()

        # Store file metadata
        user = blake3(request.client_ip.encode("ascii")).hexdigest()
        upload_meta = UploadMeta(
            media_id=media_id,
            file_name=file_name,
            content_type="",
            user=user,
        )
        await self.write_meta(media_id, upload_meta)

        # Store file upload
        file_path = package_dir / upload_meta.clean_file_name

        result = await self.download_file(url, file_path)
        if result is not None:
            log.info(f"RETURNING RESULT", enqueue=True)
            return result

        return upload_meta

    async def process_iscc(self, file_path: Path) -> Union[IsccMeta, Response]:
        """Process an ISCC for file at `file_path`."""

        loop = asyncio.get_event_loop()
        pool = app.service_provider[Pool]
        try:
            iscc_obj = await loop.run_in_executor(pool, idk.code_iscc, file_path.as_posix())
        except Exception as e:
            return self.status_code(422, str(e))

        if iscc_obj is None:
            return self.status_code(422, "ISCC processsing error.")

        # Store ISCC processing result
        result_path = file_path.parent / f"{file_path.parent.name}.iscc.json"
        async with aiofile.async_open(result_path, "wb") as outfile:
            await outfile.write(iscc_obj.json(indent=2).encode("utf-8"))

        return iscc_obj
