"""The blueair integration."""
import asyncio
import logging
from typing import Any, Dict, Optional

from . import blueair

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CLIENT, DOMAIN, DATA_USER_ACCOUNT, DATA_ENTRY_ID, CONF_PREFIX_DEVICE_NAME, CONF_CUSTOM_DEVICE_ID
from .device import BlueairDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["binary_sensor", "fan", "sensor", "light", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up blueair from a config entry."""
    session = async_get_clientsession(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    await async_migrate_entry(hass, entry)

    user_account = entry.data[DATA_USER_ACCOUNT]

    try:
        client = await hass.async_add_executor_job(
            lambda: blueair.BlueAir(
                username=user_account[CONF_USERNAME], password=user_account[CONF_PASSWORD]
            )
        )
        hass.data[DOMAIN][entry.entry_id][CLIENT] = client
    except KeyError as e:
        raise Unauthorized(f"BlueAir authorizarion failed")

    entry_ids: Dict[str, Any] = entry.data.get(DATA_ENTRY_ID)
    _LOGGER.debug(f"entry_ids: {entry_ids}")
    devices = await hass.async_add_executor_job(lambda: client.get_devices())
    hass.data[DOMAIN][entry.entry_id]["devices"] = coordinators = []

    for device in devices:
        entry_id = entry_ids.get(device["uuid"]) if entry_ids else None
        _LOGGER.debug(f"entry_id: {entry_id} on device uuid: {device['uuid']}")
        coordinators.append(
            BlueairDataUpdateCoordinator(hass, client, device["uuid"], device["name"], device["mac"],
                                         entry_id, user_account.get(CONF_PREFIX_DEVICE_NAME)))

    _LOGGER.debug(f"BlueAir Devices {devices}")

    tasks = [
        device.async_refresh()
        for device in hass.data[DOMAIN][entry.entry_id]["devices"]
    ]
    await asyncio.gather(*tasks)

    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except AttributeError:
        hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating configuration from version %s.%s", config_entry.version, config_entry.minor_version)

    if config_entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    if config_entry.version == 1:
        if config_entry.minor_version < 2:
            user_account: Dict[str, Any] = {CONF_USERNAME: config_entry.data[CONF_USERNAME],
                                            CONF_PASSWORD: config_entry.data[CONF_PASSWORD],
                                            CONF_PREFIX_DEVICE_NAME: True,
                                            CONF_CUSTOM_DEVICE_ID: False}
            entry_ids: Optional[Dict[str, Any]] = None

            hass.config_entries.async_update_entry(
                config_entry,
                data={
                    DATA_USER_ACCOUNT: user_account,
                    DATA_ENTRY_ID: entry_ids,
                },
                version=1,
                minor_version=2
            )

    _LOGGER.debug("Migration to configuration version %s.%s successful", config_entry.version,
                  config_entry.minor_version)

    return True
