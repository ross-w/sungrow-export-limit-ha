"""Number entity for Sungrow Export Limit integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from sungrow_http_config import SungrowHttpConfig

from .const import DOMAIN, WATTS_TO_DEKAWATTS, DEKAWATTS_TO_WATTS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Sungrow export limit number entity from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    host = data["host"]
    export_limit = data["export_limit"]
    mode = data["mode"]

    # Convert the export limit from dekawatts to watts for display
    export_limit_watts = export_limit * DEKAWATTS_TO_WATTS

    number = SungrowExportLimitNumber(hass, entry)
    async_add_entities([number], update_before_add=True)


class SungrowExportLimitNumber(NumberEntity):
    """Representation of a Sungrow export limit number entity."""

    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 10  # 1 dekawatt = 10 watts (minimum valid export limit)
    _attr_native_max_value = 50000  # 5000 dekawatts = 50,000 watts
    _attr_native_step = 10  # 10 watt steps (1 dekawatt)

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the number entity."""
        self.hass = hass
        self.entry = entry
        self.entry_id = entry.entry_id
        data = hass.data[DOMAIN][entry.entry_id]
        
        self._host = data["host"]
        self._export_limit = data["export_limit"]
        self._mode = data["mode"]
        
        # Convert the export limit from dekawatts to watts for display
        self._export_limit_watts = self._export_limit * DEKAWATTS_TO_WATTS
        
        self._attr_unique_id = f"{self._host}_export_limit_number"
        self._attr_name = f"Sungrow Export Limit Value ({self._host})"
        self._client = SungrowHttpConfig.SungrowHttpConfig(host=self._host, mode=self._mode)
        self._is_switch_on = False

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Listen for changes to the switch entity
        self.async_on_remove(
            self.hass.bus.async_listen(
                "state_changed",
                self._async_switch_changed,
            )
        )

    async def _async_switch_changed(self, event) -> None:
        """Handle switch entity state changes."""
        if not event.data or "entity_id" not in event.data:
            return
            
        entity_id = event.data["entity_id"]
        if not entity_id.endswith(f"{self._host}_export_limit_switch"):
            return
            
        # Update our switch state
        if "new_state" in event.data and event.data["new_state"] is not None:
            self._is_switch_on = event.data["new_state"].state == "on"
            self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set the export limit value in watts."""
        # Convert watts to dekawatts for the API
        dekawatts = int(value * WATTS_TO_DEKAWATTS)
        
        # Store the new value
        self._export_limit_watts = value
        
        # Only apply the new limit if the switch is on
        if self._is_switch_on:
            await self.hass.async_add_executor_job(self._client.setExportLimit, dekawatts)
        
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update the current export limit value."""
        # Get the current export limit from the inverter
        current_limit_dekawatts = await self.hass.async_add_executor_job(
            self._client.getCurrentExportLimit
        )
        
        # Convert dekawatts to watts for display
        if current_limit_dekawatts > 0:
            self._export_limit_watts = current_limit_dekawatts * DEKAWATTS_TO_WATTS
            self._is_switch_on = True
        else:
            # If the export limit is 0, the switch is off
            # But we keep the last known value in the number entity
            self._is_switch_on = False

    @property
    def native_value(self) -> float:
        """Return the current export limit value in watts."""
        return self._export_limit_watts

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # The number entity is always available, even when the switch is off
        return True
        
    @property
    def icon(self) -> str:
        """Return the icon to use for the entity."""
        return "mdi:transmission-tower-export"
