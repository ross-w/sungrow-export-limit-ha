"""Integration to turn on/off the export limit with a switch."""
import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_HOST
import homeassistant.helpers.config_validation as cv

from sungrow_http_config import SungrowHttpConfig

# Define the schema for the configuration flow
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Sungrow export limit platform."""
    pass  # We don't need this for this integration.


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Sungrow export limit from a config entry."""
    host = entry.data[CONF_HOST]
    export_limit = entry.data.get("export_limit", 50)
    mode = entry.data.get("mode", "http")
    switch = SungrowExportLimit(host, export_limit, mode)

    async_add_entities([switch], update_before_add=True)


class SungrowExportLimit(SwitchEntity):
    """Representation of a Sungrow export limit."""

    def __init__(self, host, export_limit, mode="http") -> None:
        """Initialize the switch."""
        self._host = host
        self._export_limit = export_limit
        self._mode = mode
        self._name = f"Sungrow Export Limit ({self._host})"
        self._is_on = False
        self._client = SungrowHttpConfig.SungrowHttpConfig(host=self._host, mode=self._mode)

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

    def turn_on(self, **kwargs) -> None:
        """Turn on the switch with the specified export limit."""
        self._client.setExportLimit(self._export_limit)  # Use the provided export_limit
        self._is_on = True

    def turn_off(self, **kwargs):
        """Turn off the switch."""
        self._client.unsetExportLimit()
        self._is_on = False

    def update(self):
        """Get the current state from the switch."""
        # Get the current export limit from the switch
        el = self._client.getCurrentExportLimit()
        self._is_on = el > 0

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self._is_on
