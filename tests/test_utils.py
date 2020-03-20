"""Tests for DirecTV Helpers."""
import directv.utils as utils


def test_combine_channel_number() -> None:
    """Test the merging of channel numbers."""
    assert utils.combine_channel_number(231, 65535) == "231"
    assert utils.combine_channel_number(231, 1) == "231-1"


def test_parse_channel_number() -> None:
    """Test the parsing of channel numbers."""
    assert utils.parse_channel_number("231") == ("231", "65535")
