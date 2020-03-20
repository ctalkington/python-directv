"""Tests for DIRECTV."""
import asyncio

import pytest
from aiohttp import ClientSession
from directv import DIRECTV

from . Import load_fixture

HOST = "1.2.3.4"
PORT = 8080

MATCH_HOST = f"{HOST}:{PORT}"
NON_STANDARD_PORT = 3333


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
        assert response.info.version == ""
        assert response.info.receiver_id == ""
        
