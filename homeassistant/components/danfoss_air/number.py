"""Support for Danfoss Air HRV number entities."""

from __future__ import annotations

import logging

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

FAN_STEP_COMMANDS = {
    1: UpdateCommand.set_fan_step_1,
    2: UpdateCommand.set_fan_step_2,
    3: UpdateCommand.set_fan_step_3,
    4: UpdateCommand.set_fan_step_4,
    5: UpdateCommand.set_fan_step_5,
    6: UpdateCommand.set_fan_step_6,
    7: UpdateCommand.set_fan_step_7,
    8: UpdateCommand.set_fan_step_8,
    9: UpdateCommand.set_fan_step_9,
    10: UpdateCommand.set_fan_step_10,
}


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Danfoss Air HRV number platform."""
    data = hass.data[DOMAIN]

    add_entities([DanfossAirFanStep(data)])


class DanfossAirFanStep(NumberEntity):
    """Representation of a Danfoss Air fan step number entity."""

    _attr_native_min_value = 1
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, data):
        """Initialize the number entity."""
        self._data = data
        self._attr_name = "Danfoss Air Fan Step"
        self._attr_native_value = None

    def set_native_value(self, value: float) -> None:
        """Set the fan step."""
        fan_step = int(value)
        if fan_step not in FAN_STEP_COMMANDS:
            _LOGGER.error("Invalid fan step: %s", fan_step)
            return

        command = FAN_STEP_COMMANDS[fan_step]
        _LOGGER.debug("Setting fan step to %s with command %s", fan_step, command)
        self._data.update_state(command, ReadCommand.fan_step)
        self._attr_native_value = fan_step

    def update(self) -> None:
        """Update the number entity's state."""
        self._data.update()

        fan_step_value = self._data.get_value(ReadCommand.fan_step)
        if fan_step_value is None:
            _LOGGER.debug("Could not get fan step data")
            return

        # The fan_step value might be a percentage or direct step value
        # Convert if necessary
        if isinstance(fan_step_value, (int, float)):
            # If it's a percentage (0-100), convert to step (1-10)
            if fan_step_value > 10:
                self._attr_native_value = max(1, min(10, int(fan_step_value / 10)))
            else:
                self._attr_native_value = int(fan_step_value)
        else:
            _LOGGER.debug("Unexpected fan step value type: %s", type(fan_step_value))
