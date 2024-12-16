"""Support for Blueair Switchs."""
import logging
from typing import Any, Optional

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass, ENTITY_ID_FORMAT,
)


from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity, generate_custom_entity_id


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair switchs from config entry."""
    _LOGGER.debug("Setting up blueair switch")
    devices: list[BlueairDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["devices"]
    entities = []
    for device in devices:
        # Don't add sensors to classic models
        if (
                device.model.startswith("classic") and not device.model.endswith("i")
        ) or device.model == "foobot":
            pass
        else:
            entities.extend(
                [
                    BlueairChildLockSwitchEntity(f"{device.device_name}_child_lock", device,
                                           generate_custom_entity_id(ENTITY_ID_FORMAT, "child_lock",
                                                                     hass, device.entry_id)),
                ]
            )

    _LOGGER.debug(f"blueair switchs {entities}")
    async_add_entities(entities)


class BlueairChildLockSwitchEntity(BlueairEntity, SwitchEntity):
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, name, device, custom_entity_id=None):
        super().__init__("Child Lock", name, device, custom_entity_id)
        self._state: float = None

    @property
    def is_on(self) -> int | None:
        return self._device.child_lock

    async def async_turn_on(self, **kwargs):
        await self._device.set_child_lock(True)

    async def async_turn_off(self, **kwargs):
        await self._device.set_child_lock(False)
