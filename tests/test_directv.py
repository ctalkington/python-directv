"""Tests for DIRECTV."""
import asyncio

import pytest
from aiohttp import ClientSession
from directv import DIRECTV
from directv.exceptions import DIRECTVConnectionError, DIRECTVError

from . import load_fixture

HOST = "1.2.3.4"
PORT = 8080

MATCH_HOST = f"{HOST}:{PORT}"
NON_STANDARD_PORT = 3333


@pytest.mark.asyncio
async def test_directv_request(aresponses):
    """Test DIRECTV response is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/getVersion",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv.info()
        assert response["status-code"] == 0


@pytest.mark.asyncio
async def test_internal_session(aresponses):
    """Test DIRECTV response is handled correctly."""
    aresponses.add(
        MATCH_HOST,
        "/info/getVersion",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )

    async with DIRECTV(HOST) as dtv:
        response = await dtv.info()
        assert response["status-code"] == 0


@pytest.mark.asyncio
async def test_request_port(aresponses):
    """Test the DIRECTV server running on non-standard port."""
    aresponses.add(
        f"{HOST}:{NON_STANDARD_PORT}",
        "/info/getVersion",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )

    async with ClientSession() as session:
        ipp = IPP(
            host=HOST,
            port=NON_STANDARD_PORT,
            session=session,
        )
        response = await dtv.info()
        assert response["status-code"] == 0


@pytest.mark.asyncio
async def test_timeout(aresponses):
    """Test request timeout from the DIRECTV server."""
    # Faking a timeout by sleeping
    async def response_handler(_):
        await asyncio.sleep(2)
        return aresponses.Response(body="Timeout!")

    aresponses.add(
        MATCH_HOST, "/info/getVersion", "GET", response_handler,
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session, request_timeout=1)
        with pytest.raises(DIRECTVConnectionError):
            assert await dtv.info()


@pytest.mark.asyncio
async def test_client_error():
    """Test http client error."""
    async with ClientSession() as session:
        dtv = DIRECTV("#", session=session)
        with pytest.raises(DIRECTVConnectionError):
            assert await dtv.info()


@pytest.mark.asyncio
async def test_http_error404(aresponses):
    """Test HTTP 404 response handling."""
    aresponses.add(
        MATCH_HOST,
        "/info/getVersion",
        "GET",
        aresponses.Response(text="Not Found!", status=404),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        with pytest.raises(DIRECTVError):
            assert await dtv.info()


@pytest.mark.asyncio
async def test_unexpected_response(aresponses):
    """Test unexpected response handling."""
    aresponses.add(
        MATCH_HOST,
        "/info/getVersion",
        "GET",
        aresponses.Response(text="Surprise!", status=200),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        with pytest.raises(DIRECTVError):
            assert await dtv.info()
