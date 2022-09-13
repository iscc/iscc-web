# -*- coding: utf-8 -*-
from pathlib import Path
from pydantic import BaseSettings


HERE = Path(__file__).parent.absolute()


class IsccWebOptions(BaseSettings):

    media_path: Path = HERE.parent.absolute() / "media"
    max_upload_size: int = 1_073_741_824  # 1 GB
    io_read_size: int = 2_097_152  # 2 MB


opts = IsccWebOptions()
