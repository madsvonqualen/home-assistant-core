"""Support for Danfoss Air HRV select entities."""

import logging

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

OPERATION_MODE_DEMAND = "demand"
OPERATION_MODE_PROGRAM = "program"
OPERATION_MODE_MANUAL = "manual"

OPERATION_MODES = [
    OPERATION_MODE_DEMAND,
    OPERATION_MODE_PROGRAM,
    OPERATION_MODE_MANUAL,
]

OPERATION_MODE_TO_COMMAND = {
    OPERATION_MODE_DEMAND: UpdateCommand.operation_mode_demand,
    OPERATION_MODE_PROGRAM: UpdateCommand.operation_mode_program,
    OPERATION_MODE_MANUAL: UpdateCommand.operation_mode_manual,
}


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Danfoss Air HRV select platform."""
    data = hass.data[DOMAIN]

    add_entities([DanfossAirOperationMode(data)])


class DanfossAirOperationMode(SelectEntity):
    """Representation of a Danfoss Air operation mode select."""

    _attr_options = OPERATION_MODES

    def __init__(self, data):
        """Initialize the select entity."""
        self._data = data
        self._attr_name = "Danfoss Air Operation Mode"
        self._attr_current_option = None
        self._attr_unique_id = f"{data.host}-operation_mode"

    @property
    def current_option(self) -> str | None:
        """Return the current operation mode."""
        return self._attr_current_option

    def select_option(self, option: str) -> None:
        """Set the operation mode."""
        if option not in OPERATION_MODE_TO_COMMAND:
            _LOGGER.error("Invalid operation mode: %s", option)
            return

        command = OPERATION_MODE_TO_COMMAND[option]
        _LOGGER.debug("Setting operation mode to %s with command %s", option, command)
        self._data.update_state(command, ReadCommand.operation_mode)
        self._attr_current_option = option

    def update(self) -> None:
        """Update the select entity's state."""
        self._data.update()
        self._attr_available = self._data.available

        mode_value = self._data.get_value(ReadCommand.operation_mode)
        if mode_value is None:
            _LOGGER.debug("Could not get operation mode data")
            return

        # Map the returned value to operation mode string
        # The API returns the mode as a string or value
        if isinstance(mode_value, str):
            mode_lower = mode_value.lower()
            if mode_lower in OPERATION_MODES:
                self._attr_current_option = mode_lower
            else:
                _LOGGER.debug("Unknown operation mode value: %s", mode_value)
        else:
            _LOGGER.debug("Operation mode value type: %s", type(mode_value))
