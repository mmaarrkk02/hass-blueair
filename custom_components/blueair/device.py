"""Blueair device object."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any
from async_timeout import timeout

from . import blueair

API = blueair.BlueAir

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import DOMAIN, LOGGER

_LOGGER = logging.getLogger(__name__)


class BlueairDataUpdateCoordinator(DataUpdateCoordinator):
    """Blueair device object."""

    def __init__(self, hass: HomeAssistant, api_client: API, uuid: str, device_name: str, mac: str = None,
                 entry_id: str = None, is_prefix_device_name=True) -> None:
        """Initialize the device."""
        self.hass: HomeAssistant = hass
        self.api_client: API = api_client
        self._uuid: str = uuid
        self._entry_id: str = entry_id
        _LOGGER.debug(f"Custom entity id {entry_id} on {device_name}")
        self._name: str = device_name
        self.mac = mac
        self._manufacturer: str = "BlueAir"
        self._device_information: dict[str, Any] = {}
        self._datapoint: dict[str, Any] = {}
        self._attribute: dict[str, Any] = {}

        if is_prefix_device_name:
            name = f"{DOMAIN}-{device_name}"
        else:
            name = device_name
        super().__init__(
            hass,
            LOGGER,
            name=name,
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with timeout(10):
                await asyncio.gather(*[self._update_device()])
        except Exception as error:
            raise UpdateFailed(error) from error

    @property
    def id(self) -> str:
        """Return Blueair device id."""
        return self._uuid

    @property
    def entry_id(self) -> str:
        """Return Blueair entry id."""
        return self._entry_id

    @property
    def device_name(self) -> str:
        """Return device name."""
        return self._device_information.get("nickname", f"{self.name}")

    @property
    def manufacturer(self) -> str:
        """Return manufacturer for device."""
        return self._manufacturer

    @property
    def model(self) -> str:
        """Return model for device, or the UUID if it's not known."""
        return self._device_information.get("compatibility", self.id)

    @property
    def temperature(self) -> float | None:
        """Return the current temperature in degrees C."""
        if "temperature" not in self._datapoint:
            return None
        return self._datapoint["temperature"]

    @property
    def humidity(self) -> float | None:
        """Return the current relative humidity percentage."""
        if "humidity" not in self._datapoint:
            return None
        return self._datapoint["humidity"]

    @property
    def co2(self) -> float | None:
        """Return the current co2."""
        if "co2" not in self._datapoint:
            return None
        return self._datapoint["co2"]

    @property
    def voc(self) -> float | None:
        """Return the current voc."""
        if "voc" not in self._datapoint:
            return None
        return self._datapoint["voc"]

    @property
    def pm1(self) -> float | None:
        """Return the current pm1."""
        if "pm1" not in self._datapoint:
            return None
        return self._datapoint["pm1"]

    @property
    def pm10(self) -> float | None:
        """Return the current pm10."""
        if "pm10" not in self._datapoint:
            return None
        return self._datapoint["pm10"]

    @property
    def pm25(self) -> float | None:
        """Return the current pm25."""
        if "pm25" not in self._datapoint:
            return None
        return self._datapoint["pm25"]

    @property
    def all_pollution(self) -> float | None:
        """Return all pollution"""
        if "all_pollution" not in self._datapoint:
            return None
        return self._datapoint["all_pollution"]

    @property
    def fan_speed(self) -> int | None:
        """Return the current fan speed."""
        if "fan_speed" not in self._attribute:
            return None
        return int(self._attribute["fan_speed"])

    @property
    def is_on(self) -> bool():
        """Return the current fan state."""
        if "fan_speed" not in self._attribute:
            return None
        if self._attribute["fan_speed"] == "0":
            return False
        return True

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode"""
        if self._attribute["mode"] == "manual":
            return None
        return self._attribute["mode"]

    @property
    def fan_mode_supported(self) -> bool():
        """Return if fan mode is supported. This function is used to lock out unsupported
         functionality from the UI if the model doesnt support modes"""
        if "mode" in self._attribute:
            return True
        return False

    @property
    def filter_expired(self) -> bool | None:
        """Return the current filter status."""
        if "filter_status" not in self._attribute:
            return None
        return self._attribute["filter_status"] != "OK"

    @property
    def child_lock(self) -> bool | None:
        """Return the current filter status."""
        if "child_lock" not in self._attribute:
            return None
        if isinstance(self._attribute["child_lock"], bool):
            return bool(self._attribute["child_lock"])
        else:
            return self._attribute["child_lock"] == "1"

    @property
    def wifi_working(self) -> bool | None:
        """Return the current filter status."""
        if "wifi_status" not in self._attribute:
            return None
        return self._attribute["wifi_status"] == "1"

    @property
    def brightness(self) -> int | None:
        """Return the current filter status."""
        if "brightness" not in self._attribute:
            return None
        return int(self._attribute["brightness"])

    async def set_brightness(self, brightness) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.set_brightness(self.id, brightness)
        )
        self._attribute["brightness"] = brightness
        await self.async_refresh()

    async def set_fan_speed(self, new_speed) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.set_fan_speed(self.id, new_speed)
        )
        self._attribute["fan_speed"] = new_speed
        await self.async_refresh()

    async def set_fan_mode(self, new_mode) -> None:
        await self.hass.async_add_executor_job(
            lambda: self.api_client.set_fan_mode(self.id, new_mode)
        )
        self._attribute["mode"] = new_mode
        await self.async_refresh()

    async def set_child_lock(self, new_value: bool) -> None:
        if isinstance(self._attribute["child_lock"], bool):
            await self.hass.async_add_executor_job(
                lambda: self.api_client.set_child_lock(self.id, new_value)
            )
            self._attribute["child_lock"] = new_value
            await self.async_refresh()
        else:
            attrValue = "1" if new_value else "0"
            await self.hass.async_add_executor_job(
                lambda: self.api_client.set_child_lock(self.id, attrValue)
            )
            self._attribute["child_lock"] = attrValue
            await self.async_refresh()

    async def _update_device(self, *_) -> None:
        """Update the device information from the API."""
        LOGGER.info(self._name)
        self._device_information = await self.hass.async_add_executor_job(
            lambda: self.api_client.get_info(self._uuid)
        )
        LOGGER.info(f"_device_information: {self._device_information}")
        try:
            # Classics will not have the expected data here
            self._datapoint = await self.hass.async_add_executor_job(
                lambda: self.api_client.get_current_data_point(self._uuid)
            )
        except Exception:
            pass
        LOGGER.info(f"_datapoint: {self._datapoint}")
        self._attribute = await self.hass.async_add_executor_job(
            lambda: self.api_client.get_attributes(self._uuid)
        )
        LOGGER.info(f"_attribute: {self._attribute}")
