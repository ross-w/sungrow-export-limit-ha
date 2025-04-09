"""Integration to turn on/off the export limit with a switch."""
import logging
import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv

from sungrow_http_config import SungrowHttpConfig

from .const import DOMAIN, WATTS_TO_DEKAWATTS

_LOGGER = logging.getLogger(__name__)

# Define the schema for the configuration flow
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Sungrow export limit platform."""
    pass  # We don't need this for this integration.


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Sungrow export limit from a config entry."""
    host = entry.data[CONF_HOST]
    export_limit = entry.data.get("export_limit", 50)
    mode = entry.data.get("mode", "http")

    # Store data in hass.data for sharing between entities
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "host": host,
        "export_limit": export_limit,
        "mode": mode,
    }

    switch = SungrowExportLimit(hass, entry)
    async_add_entities([switch], update_before_add=True)


class SungrowExportLimit(SwitchEntity):
    """Representation of a Sungrow export limit switch."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self.hass = hass
        self.entry = entry
        self.entry_id = entry.entry_id
        data = hass.data[DOMAIN][entry.entry_id]

        self._host = data["host"]
        self._export_limit = data["export_limit"]
        self._mode = data["mode"]
        self._attr_name = f"Sungrow Export Limit ({self._host})"
        self._attr_unique_id = f"{self._host}_export_limit_switch"
        self._is_on = False
        self._client = SungrowHttpConfig.SungrowHttpConfig(host=self._host, mode=self._mode)

        # Track the number entity's value
        self._current_number_value = self._export_limit

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Listen for changes to the number entity
        self.async_on_remove(
            self.hass.bus.async_listen(
                "state_changed",
                self._async_number_changed,
            )
        )

    async def _async_number_changed(self, event) -> None:
        """Handle number entity state changes."""
        if not event.data or "entity_id" not in event.data:
            return

        entity_id = event.data["entity_id"]
        if not entity_id.endswith(f"{self._host}_export_limit_number"):
            return

        # Update our stored value from the number entity
        if "new_state" in event.data and event.data["new_state"] is not None:
            try:
                self._current_number_value = float(event.data["new_state"].state)
                # Convert to dekawatts for the API
                self._export_limit = int(self._current_number_value * WATTS_TO_DEKAWATTS)

                # If the switch is on, apply the new limit
                if self._is_on:
                    await self.hass.async_add_executor_job(
                        self._client.setExportLimit, self._export_limit
                    )
            except (ValueError, TypeError):
                _LOGGER.warning("Could not parse number value from state")

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch with the current export limit."""
        # Get the current value from the number entity if available
        export_limit = self._export_limit

        await self.hass.async_add_executor_job(self._client.setExportLimit, export_limit)
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch."""
        await self.hass.async_add_executor_job(self._client.unsetExportLimit)
        self._is_on = False
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Get the current state from the switch."""
        # Get the current export limit from the inverter
        el = await self.hass.async_add_executor_job(self._client.getCurrentExportLimit)
        self._is_on = el > 0

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self._is_on

    @property
    def icon(self) -> str:
        """Return the icon to use for the entity."""
        return "mdi:transmission-tower" if self._is_on else "mdi:transmission-tower-off"
