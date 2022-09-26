"""Common helper functions"""
from blacksheep import Request
import shutil
from aiofiles.os import wrap

__all__ = [
    "copyfile",
    "rmtree",
    "base_url",
]


copyfile = wrap(shutil.copyfile)
rmtree = wrap(shutil.rmtree)


def base_url(r: Request) -> str:
    """Build base_url from Request"""
    return f"{r.scheme}://{r.host}/api/v1"
