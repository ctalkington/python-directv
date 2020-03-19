"""Models for DirecTV."""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

from .exceptions import DIRECTVError


@dataclass(frozen=True)
class Info:
    """Object holding information from DirecTV."""

    brand: str
    receiver_id: str
    name: str
    version: str

    @staticmethod
    def from_dict(data: dict):
        """Return Info object from DirecTV API response."""
        receiver_id = data.get("receiverId", "")

        return Info(
            brand="DirecTV",
            receiver_id="".join(receiver_id.split(),
            version=data.get("stbSoftwareVersion", "Unknown"),
        )


@dataclass(frozen=True)
class Location:
    """Object holding all information of receiver client location."""

    name: str
    address: str

    @staticmethod
    def from_dict(data: dict):
        """Return Info object from DirecTV API response."""
        return Location(
            name=data.get("locationName"),
            address=data get("clientAddr"),
        )


class Device:
    """Object holding all information of receiver."""

    info: Info
    locations: List[Location] = []

    def __init__(self, data: dict):
        """Initialize an empty DirecTV device class."""
        # Check if all elements are in the passed dict, else raise an Error
        if any(
            k not in data and data[k] is not None
            for k in ["locations", "info"]
        ):
            raise DIRECTVError("DirecTV data is incomplete, cannot construct device object")
        self.update_from_dict(data)

    def update_from_dict(self, data: dict) -> "Device":
        """Return Device object from DirecTV API response."""
        if "info" in data and data["info"]:
            self.info = Info.from_dict(data["info"])

        return self
