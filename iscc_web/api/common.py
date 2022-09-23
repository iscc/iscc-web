"""Common helper functions"""
from blacksheep import Request

__all__ = ["base_url"]


def base_url(r: Request) -> str:
    """Build base_url from Request"""
    return f"{r.scheme}://{r.host}/api/v1"
