"""Tests for the Danfoss Air sensor platform."""

from freezegun.api import FrozenDateTimeFactory
import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration


@pytest.mark.usefixtures("mock_danfoss_client")
@pytest.mark.parametrize(
    "entity_id",
    [
        "sensor.danfoss_air_exhaust_temperature",
        "sensor.danfoss_air_outdoor_temperature",
        "sensor.danfoss_air_supply_temperature",
        "sensor.danfoss_air_extract_temperature",
        "sensor.danfoss_air_remaining_filter",
        "sensor.danfoss_air_humidity",
        "sensor.danfoss_air_fan_step",
        "sensor.danfoss_air_exhaust_fan_speed",
        "sensor.danfoss_air_supply_fan_speed",
        "sensor.danfoss_air_dial_battery",
    ],
)
async def test_sensor_state(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    entity_id: str,
) -> None:
    """Test the sensor states, attributes and registry entries."""
    await setup_integration(hass, freezer)

    assert hass.states.get(entity_id) == snapshot
    assert entity_registry.async_get(entity_id) == snapshot
