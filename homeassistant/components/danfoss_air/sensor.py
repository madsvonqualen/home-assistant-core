"""Support for the for Danfoss Air HRV sensors."""

from dataclasses import dataclass
import logging

from pydanfossair.commands import ReadCommand

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class DanfossAirSensorEntityDescription(SensorEntityDescription):
    """Describes a Danfoss Air sensor entity."""

    command: ReadCommand


SENSOR_TYPES: tuple[DanfossAirSensorEntityDescription, ...] = (
    DanfossAirSensorEntityDescription(
        key="exhaust_temperature",
        name="Danfoss Air Exhaust Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        command=ReadCommand.exhaustTemperature,
    ),
    DanfossAirSensorEntityDescription(
        key="outdoor_temperature",
        name="Danfoss Air Outdoor Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        command=ReadCommand.outdoorTemperature,
    ),
    DanfossAirSensorEntityDescription(
        key="supply_temperature",
        name="Danfoss Air Supply Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        command=ReadCommand.supplyTemperature,
    ),
    DanfossAirSensorEntityDescription(
        key="extract_temperature",
        name="Danfoss Air Extract Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        command=ReadCommand.extractTemperature,
    ),
    DanfossAirSensorEntityDescription(
        key="remaining_filter",
        name="Danfoss Air Remaining Filter",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
        command=ReadCommand.filterPercent,
    ),
    DanfossAirSensorEntityDescription(
        key="humidity",
        name="Danfoss Air Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        command=ReadCommand.humidity,
    ),
    DanfossAirSensorEntityDescription(
        key="fan_step",
        name="Danfoss Air Fan Step",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        command=ReadCommand.fan_step,
    ),
    DanfossAirSensorEntityDescription(
        key="exhaust_fan_speed",
        name="Danfoss Air Exhaust Fan Speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        command=ReadCommand.exhaust_fan_speed,
    ),
    DanfossAirSensorEntityDescription(
        key="supply_fan_speed",
        name="Danfoss Air Supply Fan Speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        command=ReadCommand.supply_fan_speed,
    ),
    DanfossAirSensorEntityDescription(
        key="dial_battery",
        name="Danfoss Air Dial Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
        command=ReadCommand.battery_percent,
    ),
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the available Danfoss Air sensors etc."""
    data = hass.data[DOMAIN]

    add_entities((DanfossAir(data, description) for description in SENSOR_TYPES), True)


class DanfossAir(SensorEntity):
    """Representation of a Sensor."""

    entity_description: DanfossAirSensorEntityDescription

    def __init__(self, data, description: DanfossAirSensorEntityDescription) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._data = data
        self._attr_unique_id = description.key

    def update(self) -> None:
        """Update the new state of the sensor.

        This is done through the DanfossAir object that does the actual
        communication with the Air CCM.
        """
        self._data.update()
        self._attr_available = self._data.available

        self._attr_native_value = self._data.get_value(self.entity_description.command)
        if self._attr_native_value is None:
            _LOGGER.debug("Could not get data for %s", self.entity_description.key)
