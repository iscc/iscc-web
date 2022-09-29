# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field, AnyHttpUrl


HERE = Path(__file__).parent.absolute()


class IsccWebOptions(BaseSettings):
    class Config:
        env_prefix = "ISCC_WEB_"
        env_file_encoding = "utf-8"

    environment: str = "development"
    site_address: AnyHttpUrl = "http://localhost:8000"
    media_path: Path = HERE.parent.absolute() / "media"
    max_workers: Optional[int] = Field(
        None, description="Max number of iscc worker processes (defaults to CPU count)"
    )
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
    sentry_dsn: Optional[str] = Field(default="", description="Sentry DSN for error reporting")

    @property
    def debug(self):
        return self.environment == "development"


opts = IsccWebOptions()

if opts.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=opts.sentry_dsn,
        environment=opts.environment,
        traces_sample_rate=0,
    )
