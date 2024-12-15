"""Base entity class for Blueair entities."""
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import DeviceInfo, Entity, generate_entity_id

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class BlueairEntity(Entity):
    """A base class for Blueair entities."""

    _attr_force_update = False
    _attr_should_poll = False

    def __init__(
            self,
            entity_type: str,
            name: str,
            device: BlueairDataUpdateCoordinator,
            custom_entity_id=None,
            **kwargs,
    ) -> None:
        """Init Blueair entity."""
        self._attr_name = f"{name}"
        self._attr_unique_id = f"{device.id}_{entity_type}"

        if custom_entity_id is not None:
            _LOGGER.info(f"Custom entity id {custom_entity_id} on {name}")
            self.entity_id = custom_entity_id

        self._device: BlueairDataUpdateCoordinator = device
        self._state: Any = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""
        connections = {(CONNECTION_NETWORK_MAC, self._device.mac)}
        return {
            "connections": connections,
            "identifiers": {(DOMAIN, self._device.id)},
            "manufacturer": self._device.manufacturer,
            "model": self._device.model,
            "name": self._device.device_name,
        }

    async def async_update(self):
        """Update Blueair entity."""
        await self._device.async_request_refresh()
        self._attr_available = self._device.wifi_working

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(self._device.async_add_listener(self.async_write_ha_state))


def generate_custom_entity_id(entity_id_format: str, device_type: str, hass: HomeAssistant,
                              entry_id=None) -> str | None:
    if entry_id is None:
        return None
    return generate_entity_id(
        entity_id_format,
        f"{entry_id}_{device_type}",
        hass=hass)
