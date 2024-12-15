"""Config flow for blueair integration."""
import logging
from collections import OrderedDict
from typing import Optional, Any, Dict, List, Mapping

import voluptuous as vol

from . import blueair

from homeassistant import config_entries, core, exceptions, data_entry_flow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOGGER, CONF_CUSTOM_DEVICE_ID, DATA_ENTRY_ID, DATA_USER_ACCOUNT, CONF_PREFIX_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

"""Handle a config flow for blueair."""

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for blueair."""

    VERSION = 1
    MINOR_VERSION = 2

    enabled_custom_prefix_device_id = False

    def __init__(self):
        self._entry_ids: Optional[Dict[str, Any]] = None
        self._user_account: Optional[Dict[str, Any]] = None
        self.__devices: Optional[List[Dict[str, Any]]] = None
        self.client: Optional[blueair.BlueAir] = None

    async def validate_input(self, data):
        """Validate the user input allows us to connect.
        Data has the keys from DATA_SCHEMA with values provided by the user.
        """

        session = async_get_clientsession(self.hass)
        try:
            self.client = await self.hass.async_add_executor_job(
                lambda: blueair.BlueAir(
                    username=data[CONF_USERNAME],
                    password=data[CONF_PASSWORD]
                )
            )
            LOGGER.debug(f"Connecting as {data[CONF_USERNAME]}")
        except KeyError as e:
            raise InvalidAuth(f"BlueAir authorization failed")
        except Exception as e:
            raise CannotConnect()

        # return {"title": f"BlueAir {data[CONF_USERNAME]}"}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME])
            if self.client is None or not self.client.is_authenticated:
                try:
                    self._user_account = user_input
                    await self.validate_input(user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception as e:
                    _LOGGER.exception("Unexpected exception", exc_info=e)
                    errors["base"] = "unknown"

            if not len(errors):
                self.__devices = await self.hass.async_add_executor_job(lambda: self.client.get_devices())
                if user_input[CONF_CUSTOM_DEVICE_ID]:
                    return await self.async_step_custom_entry_id()
                else:
                    return self._async_create_entry()

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_CUSTOM_DEVICE_ID, default=(
                        user_input[CONF_CUSTOM_DEVICE_ID] if user_input is not None else False)): bool,
                    vol.Required(CONF_PREFIX_DEVICE_NAME, default=(
                        user_input[CONF_PREFIX_DEVICE_NAME] if user_input is not None else True)): bool
                }),
            errors=errors
        )

    def _async_create_entry(self) -> data_entry_flow.FlowResult:
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=f"BlueAir {self.unique_id}",
                                       data={DATA_USER_ACCOUNT: self._user_account, DATA_ENTRY_ID: self._entry_ids})

    async def async_step_custom_entry_id(self, user_input: Dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            self._entry_ids = {}
            for device_entry in self.__devices:
                entry_id = user_input[f"{device_entry['name']}-{device_entry['uuid']}"]
                if entry_id is not None:
                    self._entry_ids[device_entry['uuid']] = entry_id
            return self._async_create_entry()

        _LOGGER.debug(f"Device count: {len(self.__devices)}")
        if len(self.__devices) == 0:
            return self.async_abort(reason="no_devices")

        fields: OrderedDict[vol.Marker, Any] = OrderedDict()
        for device_entry in self.__devices:
            fields[vol.Optional(f"{device_entry['name']}-{device_entry['uuid']}")] = str

        return self.async_show_form(
            step_id="custom_entry_id",
            data_schema=vol.Schema(fields),
            errors=errors,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate we can't authenticate."""
