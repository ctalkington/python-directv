"""Helpers for DirecTV."""
from typing import Tuple


def parse_channel_number(channel: str) -> Tuple[str, str]:
    """Convert a channel number into its major and minor."""
    try:
        major, minor = channel.split("-")
    except ValueError:
        major = channel
        minor = "65535"

    return major, minor


def combine_channel_number(major: int, minor: int) -> str:
    """Create a combined channel number from its major and minor."""
    if minor == 65535:
        return str(major)

    return "%d-%d" % (major, minor)
