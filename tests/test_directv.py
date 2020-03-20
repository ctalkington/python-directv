"""Tests for DIRECTV."""
import asyncio

import pytest
from aiohttp import ClientSession
from directv import DIRECTV
from directv.exceptions import (
    DIRECTVAccessRestricted,
    DIRECTVConnectionError,
    DIRECTVError,
)

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
            text='{"status": {"code": 200, "commandResult": 0}}',
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        response = await dtv._request("/info/getVersion")
        assert response["status"]["code"] == 200
        assert response["status"]["commandResult"] == 0


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
            text='{"status": {"code": 200, "commandResult": 0}}',
        ),
    )

    async with DIRECTV(HOST) as dtv:
        response = await dtv._request("/info/getVersion")
        assert response["status"]["code"] == 200
        assert response["status"]["commandResult"] == 0


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
            text='{"status": {"code": 200, "commandResult": 0}}',
        ),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(host=HOST, port=NON_STANDARD_PORT, session=session,)
        response = await dtv._request("/info/getVersion")
        assert response["status"]["code"] == 200
        assert response["status"]["commandResult"] == 0


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
            assert await dtv._request("/info/getVersion")


@pytest.mark.asyncio
async def test_client_error():
    """Test http client error."""
    async with ClientSession() as session:
        dtv = DIRECTV("#", session=session)
        with pytest.raises(DIRECTVConnectionError):
            assert await dtv._request("/info/getVersion")


@pytest.mark.asyncio
async def test_http_error403(aresponses):
    """Test HTTP 403 response handling."""
    aresponses.add(
        MATCH_HOST,
        "/tv/getTuned",
        "GET",
        aresponses.Response(text="Forbidden", status=403),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        with pytest.raises(DIRECTVAccessRestricted):
            assert await dtv._request("/tv/getTuned")


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
            assert await dtv._request("/info/getVersion")


@pytest.mark.asyncio
async def test_http_error500(aresponses):
    """Test HTTP 500 response handling."""
    aresponses.add(
        MATCH_HOST,
        "/info/getVersion",
        "GET",
        aresponses.Response(text="Internal Server Error", status=500),
    )

    async with ClientSession() as session:
        dtv = DIRECTV(HOST, session=session)
        with pytest.raises(DIRECTVError):
            assert await dtv._request("/info/getVersion")
