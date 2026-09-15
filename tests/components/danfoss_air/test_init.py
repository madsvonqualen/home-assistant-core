"""Tests for the Danfoss Air integration setup."""

from datetime import timedelta
from unittest.mock import MagicMock

from freezegun.api import FrozenDateTimeFactory
import pytest

from homeassistant.const import STATE_OFF, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration

from tests.common import async_fire_time_changed

ENTITY_HUMIDITY = "sensor.danfoss_air_humidity"
ENTITY_AWAY_MODE = "binary_sensor.danfoss_air_away_mode_active"
ENTITY_BOOST = "switch.danfoss_air_boost"
LOST_CONNECTION = "Lost connection to Danfoss Air CCM module"


async def _poll(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, seconds: int
) -> None:
    """Advance time and let every platform poll once."""
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def _refresh(hass: HomeAssistant, freezer: FrozenDateTimeFactory) -> None:
    """Run a throttled hub refresh and a follow-up poll.

    The first poll after the throttle interval refreshes the hub from one
    platform; the second poll lets the other platforms pick up the result.
    """
    await _poll(hass, freezer, 61)
    await _poll(hass, freezer, 31)


async def test_unavailable_when_connection_is_lost(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_danfoss_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that entities go unavailable while the CCM is unreachable and recover."""
    await setup_integration(hass, freezer)
    read_all = mock_danfoss_client.read_all.side_effect

    assert hass.states.get(ENTITY_HUMIDITY).state == "57.25"
    assert hass.states.get(ENTITY_AWAY_MODE).state == STATE_OFF
    assert hass.states.get(ENTITY_BOOST).state == STATE_OFF

    mock_danfoss_client.read_all.side_effect = ConnectionRefusedError
    await _refresh(hass, freezer)

    assert hass.states.get(ENTITY_HUMIDITY).state == STATE_UNAVAILABLE
    assert hass.states.get(ENTITY_AWAY_MODE).state == STATE_UNAVAILABLE
    assert hass.states.get(ENTITY_BOOST).state == STATE_UNAVAILABLE
    assert caplog.text.count(LOST_CONNECTION) == 1

    await _refresh(hass, freezer)

    assert hass.states.get(ENTITY_HUMIDITY).state == STATE_UNAVAILABLE
    assert caplog.text.count(LOST_CONNECTION) == 1

    mock_danfoss_client.read_all.side_effect = read_all
    await _refresh(hass, freezer)

    assert hass.states.get(ENTITY_HUMIDITY).state == "57.25"
    assert hass.states.get(ENTITY_AWAY_MODE).state == STATE_OFF
    assert hass.states.get(ENTITY_BOOST).state == STATE_OFF


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
