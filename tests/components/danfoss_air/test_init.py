"""Tests for the Danfoss Air integration setup."""

from freezegun.api import FrozenDateTimeFactory
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration


@pytest.mark.usefixtures("mock_danfoss_client")
@pytest.mark.parametrize(
    ("entity_id", "unique_id"),
    [
        ("binary_sensor.danfoss_air_bypass_active", "bypass_active"),
        ("binary_sensor.danfoss_air_away_mode_active", "away_mode"),
        ("sensor.danfoss_air_exhaust_temperature", "exhaust_temperature"),
        ("sensor.danfoss_air_outdoor_temperature", "outdoor_temperature"),
        ("sensor.danfoss_air_supply_temperature", "supply_temperature"),
        ("sensor.danfoss_air_extract_temperature", "extract_temperature"),
        ("sensor.danfoss_air_remaining_filter", "remaining_filter"),
        ("sensor.danfoss_air_humidity", "humidity"),
        ("sensor.danfoss_air_fan_step", "fan_step"),
        ("sensor.danfoss_air_exhaust_fan_speed", "exhaust_fan_speed"),
        ("sensor.danfoss_air_supply_fan_speed", "supply_fan_speed"),
        ("sensor.danfoss_air_dial_battery", "dial_battery"),
        ("switch.danfoss_air_boost", "boost"),
        ("switch.danfoss_air_bypass", "bypass"),
        ("switch.danfoss_air_automatic_bypass", "automatic_bypass"),
    ],
)
async def test_unique_ids(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    entity_registry: er.EntityRegistry,
    entity_id: str,
    unique_id: str,
) -> None:
    """Test that every entity is registered with a stable unique ID."""
    await setup_integration(hass, freezer)

    entry = entity_registry.async_get(entity_id)
    assert entry is not None
    assert entry.unique_id == unique_id
