import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import AUTH_URL, API_URL_TEMPLATE, BASE_HEADERS, CLIENT_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        vol.Optional("laundry_id", default="3326"): str,
        vol.Optional("country", default="DA"): str,
    }
)


class MieleLogicConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                token = await self._authenticate(user_input)
                await self._validate_laundry(token, user_input)
            except ValueError as err:
                errors["base"] = str(err)
            except Exception:
                _LOGGER.exception("Unexpected error during setup")
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{user_input['country']}_{user_input['laundry_id']}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"MieleLogic {user_input['laundry_id']}",
                    data={**user_input, "token": token},
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )

    async def _authenticate(self, user_input: dict) -> str:
        session = async_get_clientsession(self.hass)
        data = {
            "grant_type": "password",
            "username": user_input["username"].replace(" ", ""),
            "password": user_input["password"],
            "client_id": CLIENT_ID,
            "scope": "DA",
            "noexpire": "1",
        }
        headers = {**BASE_HEADERS, "Content-Type": "application/x-www-form-urlencoded"}
        async with session.post(AUTH_URL, data=data, headers=headers) as resp:
            if resp.status >= 500:
                raise ValueError("cannot_connect")
            if resp.status >= 400:
                body = await resp.json(content_type=None)
                if body.get("error_description") == "login.err.bad_credentials":
                    raise ValueError("invalid_auth")
                raise ValueError("cannot_connect")
            body = await resp.json()
            return body["access_token"]

    async def _validate_laundry(self, token: str, user_input: dict) -> None:
        session = async_get_clientsession(self.hass)
        url = API_URL_TEMPLATE.format(
            country=user_input["country"],
            laundry_id=user_input["laundry_id"],
        )
        headers = {**BASE_HEADERS, "Authorization": f"Bearer {token}"}
        async with session.get(url, headers=headers) as resp:
            if resp.status >= 400:
                raise ValueError("invalid_laundry")
