"""Tests for DIRECTV."""
import pytest
from aiohttp import ClientSession
from directv import DIRECTV

from . import load_fixture

HOST = "1.2.3.4"
PORT = 8080

MATCH_HOST = f"{HOST}:{PORT}"


@pytest.mark.asyncio
async def test_update(aresponses):
    """Test DIRECTV response is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/getVersion",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-get-version.json"),
        ),
    )

    aresponses.add(
        MATCH_HOST,
        "/info/getLocations",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-get-locations.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.update()

        assert response.info
        assert response.info.brand == "DirecTV"
        assert response.info.version == "0x4ed7"
        assert response.info.receiver_id == "028877455858"

        assert response.locations
        assert len(response.locations) == 2
        assert response.locations[0].name == "Host"
        assert response.locations[0].address == "0"

        assert response.locations[1].name == "Client"
        assert response.locations[1].address == "2CA17D1CD30X"
