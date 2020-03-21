"""Tests for DirecTV Models."""
import directv.models as models
import pytest
from directv import DIRECTVError

DEVICE = {
    "info": {
        "accessCardId": "0021-1495-6572",
        "receiverId": "0288 7745 5858",
        "stbSoftwareVersion": "0x4ed7",
        "systemTime": 1281625203,
        "version": "1.2",
    },
    "locations": [
        {"clientAddr": "0", "locationName": "Host"},
        {"clientAddr": "2CA17D1CD30X", "locationName": "Client"},
    ],
}

PROGRAM = {
    "callsign": "FOODHD",
    "date": "20070324",
    "duration": 1791,
    "episodeTitle": "Spaghetti and Clam Sauce",
    "expiration": "0",
    "expiryTime": 0,
    "isOffAir": False,
    "isPartial": False,
    "isPclocked": 1,
    "isPpv": False,
    "isRecording": False,
    "isViewed": True,
    "isVod": False,
    "keepUntilFull": True,
    "major": 231,
    "minor": 65535,
    "offset": 263,
    "programId": "4405732",
    "rating": "No Rating",
    "recType": 3,
    "startTime": 1278342008,
    "stationId": 3900976,
    "title": "Tyler's Ultimate",
    "uniqueId": "6728716739474078694",
}


def test_device() -> None:
    """Test the Device model."""
    device = models.Device(DEVICE)

    assert device

    assert device.info
    assert device.info.brand == "DirecTV"
    assert device.info.version == "0x4ed7"
    assert device.info.receiver_id == "028877455858"

    assert device.locations
    assert len(device.locations) == 2
    assert device.locations[0].name == "Host"
    assert device.locations[0].address == "0"

    assert device.locations[1].name == "Client"
    assert device.locations[1].address == "2CA17D1CD30X"


def test_device_no_data() -> None:
    """Test the Device model."""
    with pytest.raises(DIRECTVError):
        models.Device({})


def test_program() -> None:
    """Test the Program model."""
    program = models.Program.from_dict(PROGRAM)

    assert program
    assert program.recorded
    assert not program.ondemand
    assert not program.partial
    assert not program.payperview
    assert not program.purchased
    assert not program.recording
    assert program.channel == "231"
    assert program.channel_name == "FOODHD"
    assert program.program_id == "4405732"
    assert program.program_type == "tvshow"
    assert program.title == "Tyler's Ultimate"
    assert program.episode_title == "Spaghetti and Clam Sauce"
    assert program.start_time == ""
    assert program.duration == 1791
    assert program.position == 263
