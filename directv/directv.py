"""Asynchronous Python client for DirecTV."""
import asyncio
import json
from socket import gaierror as SocketGIAEroor
from typing import Any, Mapping, Optional

import aiohttp
import async_timeout
from yarl import URL

from .__version__ import __version__
from .const import VALID_REMOTE_KEYS
from .exceptions import DIRECTVAccessRestricted, DIRECTVConnectionError, DIRECTVError
from .models import Device

class DIRECTV:
    """Main class for handling connections with DirecTV servers."""

    _device: Optional[Device] = None

    def __init__(
        self,
        host: str,
        base_path: str = "/",
        password: str = None,
        port: int = 8080,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession = None,
        username: str = None,
        user_agent: str = None,
    ) -> None:
        """Initialize connection with receiver."""
        self._session = session
        self._close_session = False

        self.base_path = base_path
        self.host = host
        self.password = password
        self.port = port
        self.request_timeout = request_timeout
        self.username = username
        self.user_agent = user_agent

        if user_agent is None:
            self.user_agent = f"PythonDirecTV/{__version__}"

    async def _request(
        self,
        uri: str = "",
        method: str = "GET",
        data: Optional[Any] = None,
        params: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Handle a request to a receiver."""
        scheme = "http"

        url = URL.build(
            scheme=scheme, host=self.host, port=self.port, path=self.base_path
        ).join(URL(uri))

        auth = None
        if self.username and self.password:
            auth = aiohttp.BasicAuth(self.username, self.password)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
        }

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method,
                    url,
                    auth=auth,
                    data=data,
                    params=params,
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
            raise DIRECTVConnectionError(
                "Timeout occurred while connecting to receiver."
            ) from exception
        except (aiohttp.ClientError, SocketGIAEroor) as exception:
            raise DIRECTVConnectionError(
                "Error occurred while communicating with receiver."
            ) from exception

        if response.status == 403:
            raise DIRECTVAccessRestricted(
                "Access was restricted while communicating with receiver. Please ensure that external device access is allowed",
                {},
            )

        content_type = response.headers.get("Content-Type")

        if (response.status // 100) in [4, 5]:
            content = await response.read()
            response.close()

            if content_type == "application/json":
                raise DIRECTVError(
                    f"HTTP {response.status}",
                    json.loads(content.decode("utf8"))
                )

            raise DIRECTVError(
                f"HTTP {response.status}",
                {
                    "content-type": content_type,
                    "message": content.decode("utf8"),
                    "status-code": response.status,
                }
            )

        if "application/json" in content_type:
            data = await response.json()
            return data

        return await response.text()

    async def update(self, full_update: bool = False) -> Device:
        """Get all information about the device in a single call."""
        if self._device is None or full_update:
            info = await self._request("info/getVersion")
            if info is None:
                raise DIRECTVError("DirecTV device returned an empty API response")

            locations = await self._request("info/getLocations")
            if locations is None:
                raise DIRECTVError("DirecTV device returned an empty API response")


            self._device = Device({"info": info, "locations": locations})
            return self._device

        self._device.update_from_dict({})
        return self._device

    async def remote(self, key: str, client: str = "0"):
        """Emulate pressing a key on the remote.

        Supported keys: power, poweron, poweroff, format,
        pause, rew, replay, stop, advance, ffwd, record,
        play, guide, active, list, exit, back, menu, info,
        up, down, left, right, select, red, green, yellow,
        blue, chanup, chandown, prev, 0, 1, 2, 3, 4, 5,
        6, 7, 8, 9, dash, enter
        """
        if self._device is None:
            await self.update()

        if self._device is None:
            raise DIRECTVError("Unable to communicate with receiver")

        if not isinstance(key, str) is str:
            raise DIRECTVError("Remote key should be a string")

        if not key.lower() in VALID_REMOTE_KEYS:
            raise DIRECTVError(f"Remote key is invalid: {key}")

        keypress = {
            "key": key,
            "hold": "keyPress",
            "clientAddr": client,
        }

        await self._request("remote/processKey", params=keypress)


    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> "IPP":
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()
