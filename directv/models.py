"""Models for DirecTV."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from .exceptions import DIRECTVError
from .utils import combine_channel_number


@dataclass(frozen=True)
class Info:
    """Object holding information from DirecTV."""

    brand: str
    receiver_id: str
    version: str

    @staticmethod
    def from_dict(data: dict):
        """Return Info object from DirecTV API response."""
        receiver_id = data.get("receiverId", "")

        return Info(
            brand="DirecTV",
            receiver_id="".join(receiver_id.split()),
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
            name=data.get("locationName", "Receiver"),
            address=data.get("clientAddr", ""),
        )


@dataclass(frozen=True)
class Program:
    """Object holding all information of playing program."""

    channel: str
    channel_name: str
    ondemand: bool
    recorded: bool
    recording: bool
    program_id: int
    program_type: str
    duration: int
    episode_title: str
    partial: bool
    payperview: bool
    position: int
    purchased: bool
    rating: str
    start_time: datetime
    unique_id: int

    @staticmethod
    def from_dict(data: dict):
        """Return Info object from DirecTV API response."""
        major = data.get("major")
        minor = data.get("minor")
        episode_title = data.get("episodeTitle", None)
        program_type = "tvshow" if episode_title is not None else "movie"
        start_time = data.get("startTime", None)
        if start_time:
            start_time = datetime.fromtimestamp(start_time, timezone.utc)
        unique_id = data.get("uniqueId"), None)

        return Program(
            channel=combine_channel_number(major, minor),
            channel_name=data.get("callsign", None),
            program_id=data.get("programId", None),
            program_type=program_type,
            duration=data.get("duration", 0),
            episode_title=episode_title,
            ondemand=data.get("isVod", False),
            partial=data.get("isPartial", False),
            payperview=data.get("isPpv", False),
            position=data.get("offset", 0),
            purchased=data.get("isPurchased", False),
            rating=data.get("rating", None),
            recorded=(unique_id is not None),
            recording=data.get("isRecording", False),
            start_time=start_time,
            unique_id=unique_id,
        )


@dataclass(frozen=True)
class State:
    """Object holding all information of a single receiver client state."""

    authorized: bool
    available: bool
    standby: bool
    program: Optional[Program]


class Device:
    """Object holding all information of receiver."""

    info: Info
    locations: List[Location] = []

    def __init__(self, data: dict):
        """Initialize an empty DirecTV device class."""
        # Check if all elements are in the passed dict, else raise an Error
        if any(k not in data and data[k] is not None for k in ["locations", "info"]):
            raise DIRECTVError(
                "DirecTV data is incomplete, cannot construct device object"
            )
        self.update_from_dict(data)

    def update_from_dict(self, data: dict) -> "Device":
        """Return Device object from DirecTV API response."""
        if "info" in data and data["info"]:
            self.info = Info.from_dict(data["info"])

        if "locations" in data and data["locations"]:
            locations = [Location.from_dict(location) for location in data["locations"]]
            self.locations = locations

        return self
