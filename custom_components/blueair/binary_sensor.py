from __future__ import annotations

from homeassistant.helpers.entity import generate_entity_id

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity, generate_custom_entity_id

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity, ENTITY_ID_FORMAT
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Blueair sensors from config entry."""
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
                    BlueairFilterExpiredSensor(f"{device.device_name}_filter_expired", device,
                                               generate_custom_entity_id(ENTITY_ID_FORMAT, "filter_expired",
                                                                         hass, device.entry_id)),
                    BlueairChildLockSensor(f"{device.device_name}_child_lock", device,
                                           generate_custom_entity_id(ENTITY_ID_FORMAT, "child_lock",
                                                                     hass, device.entry_id)),
                    BlueairOnlineSensor(f"{device.device_name}_online", device,
                                        generate_custom_entity_id(ENTITY_ID_FORMAT, "online",
                                                                  hass, device.entry_id)),
                ]
            )
    async_add_entities(entities)


class BlueairFilterExpiredSensor(BlueairEntity, BinarySensorEntity):
    """Monitors the status of the Filter"""

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the filter_status sensor."""
        super().__init__("filter_expired", name, device, custom_entity_id)
        self._state: bool = None
        self._attr_icon = "mdi:air-filter"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        """Return the current filter_status."""
        return self._device.filter_expired


class BlueairChildLockSensor(BlueairEntity, BinarySensorEntity):

    def __init__(self, name, device, custom_entity_id=None):
        super().__init__("child_Lock", name, device, custom_entity_id)
        self._state: bool = None
        self._attr_icon = "mdi:account-child-outline"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self._device.child_lock


class BlueairOnlineSensor(BlueairEntity, BinarySensorEntity):
    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the online sensor."""
        super().__init__("online", name, device, custom_entity_id)
        self._state: bool = None
        self._attr_icon = "mdi:wifi-check"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY,

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self._device.wifi_working

    @property
    def icon(self) -> str | None:
        if self.is_on:
            return self._attr_icon
        else:
            return "mdi:wifi-strength-outline"
