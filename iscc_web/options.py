# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


HERE = Path(__file__).parent.absolute()

# Service defaults for iscc-sdk / iscc-sct / iscc-sci options. Applied as environment defaults
# before those libraries are imported (their pydantic-settings read the process environment at
# import time) and inherited by pool worker processes. `setdefault` keeps explicitly set
# environment variables authoritative.
ISCC_LIB_ENV_DEFAULTS = {
    "ISCC_SDK_EXPERIMENTAL": "false",
    "ISCC_SDK_GRANULAR": "true",
    "ISCC_SDK_BYTE_OFFSETS": "true",
    "ISCC_SDK_ADD_UNITS": "true",
    "ISCC_SDK_BITS": "256",
    "ISCC_SDK_WIDE": "true",
    "ISCC_SDK_FALLBACK": "true",
    "ISCC_SCT_BITS": "256",
    "ISCC_SCT_BITS_GRANULAR": "256",
    # Granular semantic text simprints always carry 256-bit fingerprints with byte-based
    # offsets and sizes. The SDK does not forward options to the semantic-code functions,
    # so these must be configured globally (simprints are stripped from results when
    # granular output is off - see `code_iscc` in api/mixins.py).
    "ISCC_SCT_SIMPRINTS": "true",
    "ISCC_SCT_OFFSETS": "true",
    "ISCC_SCT_SIZES": "true",
    "ISCC_SCT_BYTE_OFFSETS": "true",
    "ISCC_SCI_BITS": "256",
}
for _key, _value in ISCC_LIB_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)


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
    cors_origins: str = Field(
        "",
        description="Origins allowed for cross-origin API requests, space or comma separated "
        "(use '*' to allow any origin). Empty string disables CORS support.",
    )
    storage_expiry: int = Field(3600, description="Number of seconds after which uploaded files are deleted")
    cleanup_interval: int = Field(600, description="Interval in seconds for running file cleanup. Use 0 to deactivate")
    log_level: str = Field("DEBUG", description="Set logging level")
    sentry_dsn: Optional[str] = Field(default="", description="Sentry DSN for error reporting")

    @property
    def debug(self):
        return self.environment == "development"

    @property
    def site_origin(self):
        """Site address as a browser Origin string (scheme://host, default ports omitted)."""
        url = self.site_address
        default_port = {"http": 80, "https": 443}[url.scheme]
        origin = f"{url.scheme}://{url.host}"
        return origin if url.port in (None, default_port) else f"{origin}:{url.port}"


opts = IsccWebOptions()

if opts.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=opts.sentry_dsn,
        environment=opts.environment,
        traces_sample_rate=0,
    )
