"""Config flow for Sungrow Export Limit integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, WATTS_TO_DEKAWATTS
from sungrow_http_config import SungrowHttpConfig

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required("export_limit"): vol.All(int, vol.Range(min=0, max=500000)),
        vol.Optional("mode", default="http"): vol.In(["modbus", "http"]),
    }
)


def validate_connection_to_inverter(host: str, mode: str = "http"):
    """Connect to supplied host."""
    client = SungrowHttpConfig.SungrowHttpConfig(host, mode=mode)

    if not client.connect():
        raise CannotConnect

    return client.getDeviceSerialNumber()


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    # If your PyPI package is not built with async, pass your methods
    # to the executor:

    mode = data.get("mode", "http")
    serial = await hass.async_add_executor_job(
        validate_connection_to_inverter, data["host"], mode
    )

    # Convert the export limit from watts to dekawatts for storage
    # The UI shows watts, but we store dekawatts for the API
    export_limit_watts = data["export_limit"]
    export_limit_dekawatts = int(export_limit_watts * WATTS_TO_DEKAWATTS)

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {
        "title": "Sungrow Export Limit",
        "serial": serial,
        "export_limit": export_limit_dekawatts,  # Store as dekawatts
        "mode": data.get("mode", "http"),
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sungrow Export Limit."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["serial"])
                self._abort_if_unique_id_configured()

                # Create a new data dict with the converted export limit
                entry_data = {
                    "host": user_input["host"],
                    "export_limit": int(user_input["export_limit"] * WATTS_TO_DEKAWATTS),
                    "mode": user_input.get("mode", "http"),
                }

                return self.async_create_entry(title=info["title"], data=entry_data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
