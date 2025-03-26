from disnake import Embed

from config import REUSABLE_EMOJI

__all__ = ["get_pending_embed", "get_success_embed", "get_failed_embed"]


def get_pending_embed(message: str = "Действие выполняется...", /) -> Embed:
    return Embed(
        colour=0x3079d5,
        description=f"{REUSABLE_EMOJI.get('pending')} {message}"
    )


def get_success_embed(message: str, /) -> Embed:
    return Embed(
        colour=0x1fa80c,
        description=f"{REUSABLE_EMOJI.get('success')} {message}"
    )


def get_failed_embed(message: str, /) -> Embed:
    return Embed(
        colour=0xff5353,
        description=f"{REUSABLE_EMOJI.get('fail')} {message}"
    )
