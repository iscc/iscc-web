# -*- coding: utf-8 -*-
import base64
import aiofiles
import iscc_core as ic
from blacksheep import Request, Response, file
from blacksheep.server.controllers import Controller, options, post, head, patch, get
from pydantic import BaseModel
from iscc_web.options import opts
from aiofiles.os import path


class FileMeta(BaseModel):
    upload_length: int
    upload_metadata: str

    @property
    def filename(self) -> str:
        return self.decode_metadata().get("filename")

    @property
    def filetype(self) -> str:
        return self.decode_metadata().get("filetype")

    def decode_metadata(self) -> dict:
        pairs = self.upload_metadata.split(",")
        metadata = {}
        for pair in pairs:
            k, v = pair.split()
            v = base64.b64decode(v).decode("utf-8")
            metadata[k] = v
        return metadata


class Tus(Controller):
    async def on_request(self, request: Request):

        # Upload-Offset MUST be a non-negative integer.
        uppload_offset = request.get_first_header(b"Upload-Offset")
        if uppload_offset:
            if int(uppload_offset) < 0:
                return self.bad_request("Upload-Offset must be non-negative")

        # Upload-Length MUST be a non-negative integer.
        uppload_length = request.get_first_header(b"Upload-Length")
        if uppload_length:
            if int(uppload_length) < 0:
                return self.bad_request("Upload-Offset must be non-negative")

        # The Tus-Resumable header MUST be included in every request and response
        # exept for OPTIONS requests.
        if request.method != "OPTIONS":
            tus_resumable = request.get_first_header(b"Tus-Resumable")
            if tus_resumable != b"1.0.0":
                return self.status_code(
                    412, "Precondition Failed - Header Tus-Resumable=1.0.0 required"
                )

        # TODO: X-HTTP-Method-Override MUST be a string which MUST be interpreted as the request's
        # method by the Server, if the header is presented.
        method_override = request.get_first_header(b"X-HTTP-Method-Override")
        if method_override:
            return self.bad_request("X-HTTP-Method-Override not supported")

    async def on_response(self, response: Response):
        response.add_header(b"Tus-Resumable", b"1.0.0")
        response.add_header(b"Tus-Version", b"1.0.0")
        response.add_header(b"Tus-Max-Size", str(opts.max_upload_size).encode("ascii"))
        response.add_header(b"Tus-Extension", b"creation")

    @options("/tus")
    async def tus_options(self):
        return self.no_content()

    @get("/tus/{media_id}")
    async def tus_get(self, media_id: str):
        """Stream file to client"""
        if not await self.file_exists(media_id):
            return self.not_found()

        meta = await self.read_meta(media_id)

        async def provider():
            async with aiofiles.open(self.file_path(media_id), "rb") as infile:
                chunk = await infile.read(opts.io_read_size)
                while chunk:
                    yield chunk
                    chunk = await infile.read(opts.io_read_size)

        return file(provider, content_type=meta.filetype, file_name=meta.filename)

    @post("/tus")
    async def tus_post(self, request: Request):

        upload_length = request.get_first_header(b"Upload-Length")
        if not upload_length:
            return self.bad_request("Header Upload-Length required")
        elif int(upload_length) > opts.max_upload_size:
            return self.status_code(413, "Request entity too large")
        upload_length = int(upload_length)

        upload_metadata = request.get_first_header(b"Upload-Metadata")
        if not upload_metadata:
            return self.bad_request("Header Upload-Metadata required")
        elif b"filename" not in upload_metadata:
            return self.bad_request("Header Upload-Metadata must include filename")
        upload_metadata = upload_metadata.decode("ascii")

        # Create Metadata and Upload file
        media_id = ic.Flake().string.lower()
        meta_obj = FileMeta(
            upload_length=upload_length,
            upload_metadata=upload_metadata,
        )
        await self.write_meta(media_id, meta_obj)
        await self.create_file(media_id)
        response = self.created()
        response.add_header(b"Location", f"/tus/{media_id}".encode("ascii"))
        return response

    @patch("/tus/{media_id}")
    async def tus_patch(self, request: Request, media_id: str):
        """Advance upload"""
        #  MUST use Content-Type: application/offset+octet-stream, otherwise the server SHOULD
        #  return a 415 Unsupported Media Type status
        content_type = request.get_first_header(b"Content-Type")
        if not content_type == b"application/offset+octet-stream":
            return self.status_code(415, "Content-Type must be application/offset+octet-stream")

        # The Upload-Offset header's value MUST be equal to the current offset of the resource.
        # If the offsets do not match, the Server MUST respond with the 409 Conflict
        client_offset = int(request.get_first_header(b"Upload-Offset"))
        server_offset = await self.offset(media_id)
        if client_offset != server_offset:
            return self.status_code(
                409,
                f"Upload-Offset Client={client_offset}, Server={server_offset}",
            )

        # apply the bytes contained in the message at the given offset
        async with aiofiles.open(self.file_path(media_id), "ab") as outf:
            async for chunk in request.stream():
                await outf.write(chunk)

        response = self.no_content()
        new_offset = await self.offset(media_id)
        response.add_header(b"Upload-Offset", str(new_offset).encode("ascii"))
        return response

    @head("/tus/{media_id}")
    async def tus_head(self, media_id: str):
        if not await self.file_exists(media_id):
            response = self.not_found()
            response.add_header(b"Cache-Control", b"no-store")
            return response

        response = self.ok()
        # Server MUST always include the Upload-Offset header in the response for a HEAD request
        upload_offset = await self.offset(media_id)
        response.add_header(b"Upload-Offset", str(upload_offset).encode("ascii"))

        file_meta = await self.read_meta(media_id)
        # Server MUST include the Upload-Length header in the response (if known).
        response.add_header(b"Upload-Length", str(file_meta.upload_length).encode("ascii"))

        # If an upload contains additional metadata, responses to HEAD requests MUST include the
        # Upload-Metadata header and its value as specified by the Client during the creation.
        response.add_header(b"Upload-Metadata", file_meta.upload_metadata.encode("ascii"))

        # Server MUST add the Cache-Control: no-store header to the response
        response.add_header(b"Cache-Control", b"no-store")

        return response

    @staticmethod
    def file_path(media_id: str) -> str:
        """Construct file path for media_id"""
        return (opts.media_path / media_id).as_posix()

    @staticmethod
    def meta_path(media_id: str) -> str:
        """Construct mdatadata path for media_id"""
        return (opts.media_path / f"{media_id}.json").as_posix()

    async def read_meta(self, media_id: str) -> FileMeta:
        """Read file metadata"""
        async with aiofiles.open(self.meta_path(media_id), "rb") as infile:
            data = await infile.read()
        return FileMeta.parse_raw(data)

    async def write_meta(self, media_id: str, file_meta: FileMeta) -> None:
        async with aiofiles.open(self.meta_path(media_id), "w") as infile:
            await infile.write(file_meta.json(indent=2))

    async def create_file(self, media_id: str) -> None:
        async with aiofiles.open(self.file_path(media_id), "ab"):
            pass

    async def file_exists(self, media_id):
        return await path.exists(self.file_path(media_id))

    async def offset(self, media_id: str) -> int:
        """Actual offset of file upload"""
        return await path.getsize(self.file_path(media_id))
