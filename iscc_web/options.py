# -*- coding: utf-8 -*-
from pathlib import Path
from pydantic import BaseSettings, Field


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
    private_files: bool = Field(
        True, description="Restrict file downloads/deletions to original uploader"
    )
    storage_expiry: int = Field(
        3600, description="Number of seconds after which uploaded files are deleted"
    )
    cleanup_interval: int = Field(
        600, description="Interval in seconds for running file cleanup. Use 0 to deactivate"
    )
    log_level: str = Field("DEBUG", description="Set logging level")


opts = IsccWebOptions()
