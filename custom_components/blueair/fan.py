"""Support for Blueair fans."""
import logging
from typing import Any, Optional, overload

from homeassistant.components.fan import (
    FanEntity,
    ENTITY_ID_FORMAT, FanEntityFeature,
)

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity, generate_custom_entity_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair fans from config entry."""
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        if device.model != 'foobot':
            entities.extend(
                [
                    BlueairFan(f"{device.device_name}_fan", device,
                               generate_custom_entity_id(ENTITY_ID_FORMAT, "fan",
                                                         hass, device.entry_id)),
                ]
            )
    async_add_entities(entities)


class BlueairFan(BlueairEntity, FanEntity):
    """Controls Fan."""

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the temperature sensor."""
        super().__init__("Fan", name, device, custom_entity_id)
        self._state: float = None

    @property
    def supported_features(self) -> int:
        # If the fan_mode property is supported, enable support for presets
        if self._device.fan_mode_supported:
            return FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        return FanEntityFeature.SET_SPEED

    @property
    def is_on(self) -> int:
        return self._device.is_on

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        if self._device.fan_speed is not None:
            return int(round(self._device.fan_speed * 33.33, 0))
        else:
            return 0

    @property
    def preset_mode(self) -> Optional[str]:
        if self._device.fan_mode_supported:
            return self._device.fan_mode

    @property
    def preset_modes(self) -> Optional[list]:
        if self._device.fan_mode_supported:
            return list([str("auto")])

    async def async_set_percentage(self, percentage: int) -> None:
        """Sets fan speed percentage."""
        if percentage == 100:
            new_speed = "3"
        elif percentage > 50:
            new_speed = "2"
        elif percentage > 20:
            new_speed = "1"
        else:
            new_speed = "0"

        await self._device.set_fan_speed(new_speed)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.set_fan_speed("0")

    @overload
    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._device.set_fan_speed("2")

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs: Any) -> None:
        """Handle turning on the fan."""
        _LOGGER.debug("Turning on fan. percentage:{}, preset_mode:{}".format(percentage, preset_mode))
        # 如果傳遞了 percentage，設置風扇的轉速
        if percentage is not None:
            await self.async_set_percentage(percentage)
        else:
            await self._device.set_fan_speed("2")

        # 如果傳遞了 preset_mode，設置風扇的模式
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self._device.set_fan_mode(preset_mode)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return 3
