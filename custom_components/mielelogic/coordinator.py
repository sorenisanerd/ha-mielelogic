import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    AUTH_URL,
    API_URL_TEMPLATE,
    BASE_HEADERS,
    CLIENT_ID,
    DOMAIN,
    UPDATE_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class MieleLogicCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._entry = entry
        self._token: str | None = entry.data.get("token")
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    async def _authenticate(self) -> None:
        session = async_get_clientsession(self.hass)
        data = {
            "grant_type": "password",
            "username": self._entry.data["username"],
            "password": self._entry.data["password"],
            "client_id": CLIENT_ID,
            "scope": "DA",
            "noexpire": "1",
        }
        headers = {**BASE_HEADERS, "Content-Type": "application/x-www-form-urlencoded"}
        async with session.post(AUTH_URL, data=data, headers=headers) as resp:
            if resp.status >= 400:
                body = await resp.text()
                raise UpdateFailed(f"Authentication failed ({resp.status}): {body}")
            json_data = await resp.json()
            self._token = json_data["access_token"]
            self.hass.config_entries.async_update_entry(
                self._entry, data={**self._entry.data, "token": self._token}
            )

    async def _async_update_data(self) -> dict:
        if not self._token:
            await self._authenticate()

        session = async_get_clientsession(self.hass)
        url = API_URL_TEMPLATE.format(
            country=self._entry.data["country"],
            laundry_id=self._entry.data["laundry_id"],
        )

        for attempt in range(2):
            headers = {**BASE_HEADERS, "Authorization": f"Bearer {self._token}"}
            async with session.get(url, headers=headers) as resp:
                if resp.status in (401, 402, 403) and attempt == 0:
                    _LOGGER.debug("Token expired, re-authenticating")
                    await self._authenticate()
                    continue
                if resp.status >= 500:
                    raise UpdateFailed(f"MieleLogic server error ({resp.status})")
                if resp.status >= 400:
                    raise UpdateFailed(f"MieleLogic API error ({resp.status})")
                return await resp.json()

        raise UpdateFailed("Failed to fetch data after re-authentication")
