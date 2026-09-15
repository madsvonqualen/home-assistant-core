"""Support for Danfoss Air HRV."""

from datetime import timedelta
import logging

import probatio
from pydanfossair.commands import ReadCommand
from pydanfossair.danfossclient import DanfossClient

from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]
DOMAIN = "danfoss_air"

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

CONFIG_SCHEMA = probatio.Schema(
    {DOMAIN: probatio.Schema({probatio.Required(CONF_HOST): cv.string})},
    extra=probatio.ALLOW_EXTRA,
)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Danfoss Air component."""
    conf = config[DOMAIN]

    hass.data[DOMAIN] = DanfossAir(conf[CONF_HOST])

    for platform in PLATFORMS:
        discovery.load_platform(hass, platform, DOMAIN, {}, config)

    return True


class DanfossAir:
    """Handle all communication with Danfoss Air CCM unit."""

    def __init__(self, host):
        """Initialize the Danfoss Air CCM connection."""
        self._data = {}
        self.available = False

        self._client = DanfossClient(host)

    def get_value(self, item):
        """Get value for sensor."""
        return self._data.get(item)

    def update_state(self, command, state_command):
        """Send update command to Danfoss Air CCM."""
        self._data[state_command] = self._client.command(command)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Use the data from Danfoss Air API."""
        _LOGGER.debug("Fetching data from Danfoss Air CCM module")

        try:
            data = self._client.read_all()
        except OSError as err:
            if self.available:
                _LOGGER.warning("Lost connection to Danfoss Air CCM module: %s", err)
            self.available = False
            return

        data[ReadCommand.humidity] = round(data[ReadCommand.humidity], 2)
        data[ReadCommand.filterPercent] = round(data[ReadCommand.filterPercent], 2)

        self._data = data
        if not self.available:
            _LOGGER.info("Connected to Danfoss Air CCM module")
        self.available = True

        _LOGGER.debug("Done fetching data from Danfoss Air CCM module")
