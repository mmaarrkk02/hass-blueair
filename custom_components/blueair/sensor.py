"""Support for Blueair sensors."""
from homeassistant.components.sensor import (
    SensorEntity, ENTITY_ID_FORMAT, SensorDeviceClass
)
from homeassistant.const import (
    PERCENTAGE, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION, UnitOfTemperature,
)

from .const import DOMAIN
from .device import BlueairDataUpdateCoordinator
from .entity import BlueairEntity, generate_custom_entity_id

NAME_TEMPERATURE = "Temperature"
NAME_HUMIDITY = "Humidity"


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
                    BlueairTemperatureSensor(f"{device.device_name}_temperature", device,
                                             generate_custom_entity_id(ENTITY_ID_FORMAT, "temperature",
                                                                       hass, device.entry_id)),
                    BlueairHumiditySensor(f"{device.device_name}_humidity", device,
                                          generate_custom_entity_id(ENTITY_ID_FORMAT, "humidity",
                                                                    hass, device.entry_id)),
                    BlueairCO2Sensor(f"{device.device_name}_co2", device,
                                     generate_custom_entity_id(ENTITY_ID_FORMAT, "co2",
                                                               hass, device.entry_id)),
                    BlueairVOCSensor(f"{device.device_name}_voc", device,
                                     generate_custom_entity_id(ENTITY_ID_FORMAT, "voc",
                                                               hass, device.entry_id)),
                    BlueairAllPollutionSensor(f"{device.device_name}_all_pollution", device,
                                              generate_custom_entity_id(ENTITY_ID_FORMAT, "all_pollution",
                                                                        hass, device.entry_id)),
                    BlueairPM1Sensor(f"{device.device_name}_pm1", device,
                                     generate_custom_entity_id(ENTITY_ID_FORMAT, "pm1",
                                                               hass, device.entry_id)),
                    BlueairPM10Sensor(f"{device.device_name}_pm10", device,
                                      generate_custom_entity_id(ENTITY_ID_FORMAT, "pm10",
                                                                hass, device.entry_id)),
                    BlueairPM25Sensor(f"{device.device_name}_pm25", device,
                                      generate_custom_entity_id(ENTITY_ID_FORMAT, "pm25",
                                                                hass, device.entry_id)),
                ]
            )
            """The 280i model does not have PM1 and PM10 detection capabilities."""
            if device.model == "classic_280i":
                # Remove items that are instances of a particular type (e.g., list)
                for item in entities[:]:  # Iterate over a copy of the list
                    if isinstance(item, BlueairPM1Sensor) or isinstance(item, BlueairPM10Sensor):
                        entities.remove(item)

    async_add_entities(entities)


class BlueairTemperatureSensor(BlueairEntity, SensorEntity):
    """Monitors the temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the temperature sensor."""
        super().__init__(NAME_TEMPERATURE, name, device, custom_entity_id)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current temperature."""
        if self._device.temperature is None:
            return None
        return round(self._device.temperature, 1)


class BlueairHumiditySensor(BlueairEntity, SensorEntity):
    """Monitors the humidity."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the humidity sensor."""
        super().__init__(NAME_HUMIDITY, name, device, custom_entity_id)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current humidity."""
        if self._device.humidity is None:
            return None
        return round(self._device.humidity, 0)


class BlueairCO2Sensor(BlueairEntity, SensorEntity):
    """Monitors the CO2."""

    _attr_device_class = SensorDeviceClass.CO2
    _attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the CO2 sensor."""
        super().__init__("co2", name, device, custom_entity_id)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current co2."""
        if self._device.co2 is None:
            return None
        return round(self._device.co2, 0)


class BlueairVOCSensor(BlueairEntity, SensorEntity):
    """Monitors the VOC."""

    _attr_device_class = SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS
    _attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the VOC sensor."""
        super().__init__("voc", name, device, custom_entity_id)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current voc."""
        if self._device.voc is None:
            return None

        # Retrieve the raw VOC data (unit: ppb)
        ppb_value = self._device.voc

        # VOC molecular weight (assuming an average value of 120 g/mol)
        molecular_weight = 120

        # Conversion formula
        conversion_factor = molecular_weight / 24.45
        return round(ppb_value * conversion_factor, 1)


class BlueairAllPollutionSensor(BlueairEntity, SensorEntity):
    """Monitors the all pollution."""
    """The API returns the unit for this measurement as as % """
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the all pollution sensor."""
        super().__init__("all_pollution", name, device, custom_entity_id)
        self._state: float = None
        self._attr_icon = "mdi:molecule"

    @property
    def native_value(self) -> float:
        """Return the current all pollution."""
        if self._device.all_pollution is None:
            return None
        return round(self._device.all_pollution, 0)


class BlueairPM1Sensor(BlueairEntity, SensorEntity):
    """Monitors the pm1"""

    _attr_device_class = SensorDeviceClass.PM1
    _attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the pm1 sensor."""
        super().__init__("pm1", name, device, custom_entity_id)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current pm1."""
        if self._device.pm1 is None:
            return None
        return round(self._device.pm1, 0)


class BlueairPM10Sensor(BlueairEntity, SensorEntity):
    """Monitors the pm10"""

    _attr_device_class = SensorDeviceClass.PM10
    _attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the pm10 sensor."""
        super().__init__("pm10", name, device, custom_entity_id)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current pm10."""
        if self._device.pm10 is None:
            return None
        return round(self._device.pm10, 0)


class BlueairPM25Sensor(BlueairEntity, SensorEntity):
    """Monitors the pm25"""

    _attr_device_class = SensorDeviceClass.PM25
    _attr_native_unit_of_measurement = CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

    def __init__(self, name, device, custom_entity_id=None):
        """Initialize the pm25 sensor."""
        super().__init__("pm25", name, device, custom_entity_id)
        self._state: float = None

    @property
    def native_value(self) -> float:
        """Return the current pm25."""
        if self._device.pm25 is None:
            return None
        return round(self._device.pm25, 0)
