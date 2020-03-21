"""Tests for DirecTV Models."""
import directv.models as models

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
  "uniqueId": "6728716739474078694"
}


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
    assert program.program_id == ""
    assert program.program_type == "tvshow"
    assert program.episode_name == "Spaghetti and Clam Sauce"
    assert program.duration == 1791
