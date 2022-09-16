# -*- coding: utf-8 -*-
from pydantic import BaseModel


class UploadMeta(BaseModel):
    file_name: str
    content_type: str
    client_ip: str
