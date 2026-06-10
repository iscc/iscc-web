# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


HERE = Path(__file__).parent.absolute()


class IsccWebOptions(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ISCC_WEB_", env_file_encoding="utf-8")

    environment: str = "development"
    site_address: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")
    media_path: Path = HERE.parent.absolute() / "media"
    max_workers: Optional[int] = Field(
        None,
        description="Max number of iscc worker processes (defaults to CPU count). Each worker lazy-loads "
        "iscc-sdk and, for semantic features, the iscc-sct/iscc-sci ONNX models - several hundred MB of "
        "RAM per worker.",
    )
    max_upload_size: int = 1_073_741_824  # 1 GB
    io_read_size: int = 2_097_152  # 2 MB
    private_files: bool = Field(True, description="Restrict file downloads/deletions to original uploader")
    storage_expiry: int = Field(3600, description="Number of seconds after which uploaded files are deleted")
    cleanup_interval: int = Field(600, description="Interval in seconds for running file cleanup. Use 0 to deactivate")
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
