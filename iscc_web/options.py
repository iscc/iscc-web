# -*- coding: utf-8 -*-
from pathlib import Path
from pydantic import BaseSettings


HERE = Path(__file__).parent.absolute()


class IsccWebOptions(BaseSettings):

    media_path: Path = HERE.parent.absolute() / "media"
    max_upload_size: int = 104_857_600  # 100 MB


opts = IsccWebOptions()
