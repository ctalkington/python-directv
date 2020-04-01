"""Tests for DIRECTV."""
from typing import List

import pytest
from aiohttp import ClientSession
from directv import DIRECTV, DIRECTVError
from directv.models import Info, Program, State

from . import load_fixture

HOST = "1.2.3.4"
PORT = 8080

MATCH_HOST = f"{HOST}:{PORT}"


@pytest.mark.asyncio
async def test_update(aresponses):
    """Test update is handled correctly."""
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

        assert response
        assert isinstance(response.info, Info)
        assert isinstance(response.locations, List)

        response = await dtv.update()

        assert response
        assert response.info


@pytest.mark.asyncio
async def test_remote(aresponses):
    """Test remote is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/remote/processKey",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("remote-process-key.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        await dtv.remote("info")


@pytest.mark.asyncio
async def test_remote_invalid_key():
    """Test remote with invalid key is handled correctly."""
    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        with pytest.raises(DIRECTVError):
            await dtv.remote("super")


@pytest.mark.asyncio
async def test_state(aresponses):
    """Test active state is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode.json"),
        ),
    )

    aresponses.add(
        MATCH_HOST,
        "/tv/getTuned",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("tv-get-tuned.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.state()

        assert response
        assert isinstance(response, State)
        assert response.available
        assert not response.standby

        assert isinstance(response.program, Program)


@pytest.mark.asyncio
async def test_state_error_mode(aresponses):
    """Test state with generic mode error is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=500,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode-error.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.state()

        assert response
        assert isinstance(response, State)
        assert not response.available
        assert response.standby
        assert response.authorized

        assert response.program is None


@pytest.mark.asyncio
async def test_state_error_tuned(aresponses):
    """Test state with generic tuned error is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode.json"),
        ),
    )

    aresponses.add(
        MATCH_HOST,
        "/tv/getTuned",
        "GET",
        aresponses.Response(
            status=500,
            headers={"Content-Type": "application/json"},
            text=load_fixture("tv-get-tuned-error.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.state()

        assert response
        assert isinstance(response, State)
        assert not response.available
        assert not response.standby
        assert response.authorized

        assert response.program is None


@pytest.mark.asyncio
async def test_state_restricted_mode(aresponses):
    """Test standby state is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=403,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode-restricted.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.state()

        assert response
        assert isinstance(response, State)
        assert not response.available
        assert response.standby
        assert not response.authorized

        assert response.program is None


@pytest.mark.asyncio
async def test_state_restricted_tuned(aresponses):
    """Test standby state is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode.json"),
        ),
    )

    aresponses.add(
        MATCH_HOST,
        "/tv/getTuned",
        "GET",
        aresponses.Response(
            status=403,
            headers={"Content-Type": "application/json"},
            text=load_fixture("tv-get-tuned-restricted.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.state()

        assert response
        assert isinstance(response, State)
        assert response.available
        assert not response.standby
        assert not response.authorized

        assert response.program is None


@pytest.mark.asyncio
async def test_state_standby(aresponses):
    """Test restricted state is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode-standby.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.state()

        assert response
        assert isinstance(response, State)
        assert response.available
        assert response.standby

        assert response.program is None


@pytest.mark.asyncio
async def test_status(aresponses):
    """Test active state is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.status()

        assert response == "active"


@pytest.mark.asyncio
async def test_status_access_restricted(aresponses):
    """Test unauthorized state is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=403,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode-restricted.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.status()

        assert response == "unauthorized"


@pytest.mark.asyncio
async def test_status_standby(aresponses):
    """Test standby status is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode-standby.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.status()

        assert response == "standby"


@pytest.mark.asyncio
async def test_status_unavailable(aresponses):
    """Test unavailable status is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/mode",
        "GET",
        aresponses.Response(
            status=500,
            headers={"Content-Type": "application/json"},
            text=load_fixture("info-mode-error.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.status()

        assert response == "unavailable"


@pytest.mark.asyncio
async def test_tune(aresponses):
    """Test tune is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/tv/tune",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("tv-tune.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        await dtv.tune("231")


@pytest.mark.asyncio
async def test_tuned(aresponses):
    """Test tuned is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/tv/getTuned",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixture("tv-get-tuned.json"),
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.tuned()

        assert response
        assert isinstance(response, Program)
