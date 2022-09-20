# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


HERE = Path(__file__).parent.absolute()


class IsccWebOptions(BaseSettings):
    class Config:
        env_prefix = "ISCC_WEB_"
        env_file_encoding = "utf-8"

    environment: str = "development"
    scheme: str = "http"
    host: str = "localhost"
    port: str = "8000"
    media_path: Path = HERE.parent.absolute() / "media"
    max_upload_size: int = 1_073_741_824  # 1 GB
    io_read_size: int = 2_097_152  # 2 MB

    @property
    def base_url(self):
        url = f"{self.scheme}://{self.host}"
        if self.port:
            url = f"{url}:{self.port}"
        url = f"{url}/api/v1"
        return url


opts = IsccWebOptions()
