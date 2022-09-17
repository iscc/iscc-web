# -*- coding: utf-8 -*-
from pydantic import BaseModel
from pathvalidate import sanitize_filename


class UploadMeta(BaseModel):
    file_name: str
    content_type: str
    client_ip: str

    @property
    def clean_file_name(self):
        return sanitize_filename(self.file_name)
