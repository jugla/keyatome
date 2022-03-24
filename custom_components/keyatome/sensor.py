"""Linky Key Atome."""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from pykeyatome.client import (
    DAILY_PERIOD_TYPE,
    MONTHLY_PERIOD_TYPE,
    WEEKLY_PERIOD_TYPE,
    YEARLY_PERIOD_TYPE,
    AtomeClient,
)

from .const import (
    ATTR_PERIOD_PRICE,
    ATTR_PREVIOUS_PERIOD_PRICE,
    ATTR_PREVIOUS_PERIOD_USAGE,
    ATTRIBUTION,
    CONF_ATOME_LINKY_NUMBER,
    DAILY_NAME_SUFFIX,
    DAILY_SCAN_INTERVAL,
    DATA_COORDINATOR,
    DEBUG_FLAG,
    DEFAULT_ATOME_LINKY_NUMBER,
    DEFAULT_NAME,
    DEVICE_CONF_URL,
    DEVICE_NAME_SUFFIX,
    DOMAIN,
    LIVE_NAME_SUFFIX,
    LIVE_SCAN_INTERVAL,
    LIVE_TYPE,
    LOGIN_STAT_NAME_SUFFIX,
    LOGIN_STAT_SCAN_INTERVAL,
    LOGIN_STAT_TYPE,
    MONTHLY_NAME_SUFFIX,
    MONTHLY_SCAN_INTERVAL,
    ROUND_PRICE,
    WEEKLY_NAME_SUFFIX,
    WEEKLY_SCAN_INTERVAL,
    YEARLY_NAME_SUFFIX,
    YEARLY_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(
            CONF_ATOME_LINKY_NUMBER, default=DEFAULT_ATOME_LINKY_NUMBER
        ): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def format_receive_value(value):
    """Format if pb then return None."""
    if value is None or value == STATE_UNKNOWN or value == STATE_UNAVAILABLE:
        return None
    return float(value)


async def async_create_period_coordinator(
    hass, atome_client, name, sensor_type, scan_interval
):
    """Create coordinator for period data."""
    atome_period_end_point = AtomePeriodServerEndPoint(atome_client, name, sensor_type)

    async def async_period_update_data():
        data = await hass.async_add_executor_job(atome_period_end_point.retrieve_data)
        return data

    period_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_period_update_data,
        update_interval=scan_interval,
    )
    await period_coordinator.async_refresh()
    return period_coordinator


async def async_create_live_coordinator(hass, atome_client, name):
    """Create coordinator for live data."""
    atome_live_end_point = AtomeLiveServerEndPoint(atome_client, name)

    async def async_live_update_data():
        data = await hass.async_add_executor_job(atome_live_end_point.retrieve_data)
        return data

    live_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_live_update_data,
        update_interval=LIVE_SCAN_INTERVAL,
    )
    await live_coordinator.async_refresh()
    return live_coordinator


async def async_create_login_stat_coordinator(
    hass, atome_client, name, atome_linky_number
):
    """Create coordinator for login stat data."""
    atome_login_stat_end_point = AtomeLoginStatServerEndPoint(
        atome_client, name, atome_linky_number
    )

    async def async_login_stat_update_data():
        data = await hass.async_add_executor_job(
            atome_login_stat_end_point.retrieve_data
        )
        return data

    login_stat_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_login_stat_update_data,
        update_interval=LOGIN_STAT_SCAN_INTERVAL,
    )
    await login_stat_coordinator.async_refresh()
    return login_stat_coordinator


async def create_coordinators_and_sensors(
    hass, username, password, atome_linky_number, sensor_root_name
):
    """Create all coordinators and all instantiation for sensor."""
    if atome_linky_number == 1:
        sensor_root_name_linky = sensor_root_name
    else:
        sensor_root_name_linky = (
            sensor_root_name + "_linky" + str(atome_linky_number) + "_"
        )
    # Create name for sensor
    login_stat_sensor_name = sensor_root_name_linky + LOGIN_STAT_NAME_SUFFIX
    live_sensor_name = sensor_root_name_linky + LIVE_NAME_SUFFIX
    daily_sensor_name = sensor_root_name_linky + DAILY_NAME_SUFFIX
    monthly_sensor_name = sensor_root_name_linky + MONTHLY_NAME_SUFFIX
    weekly_sensor_name = sensor_root_name_linky + WEEKLY_NAME_SUFFIX
    yearly_sensor_name = sensor_root_name_linky + YEARLY_NAME_SUFFIX

    # Create name for device
    atome_device_name = sensor_root_name_linky + DEVICE_NAME_SUFFIX

    # Perform login
    atome_client = AtomeClient(username, password, atome_linky_number)
    login_value = await hass.async_add_executor_job(atome_client.login)
    if login_value is None:
        _LOGGER.error("No login available for atome server")
        return
    if DEBUG_FLAG:
        _LOGGER.debug("login value is %s", login_value)
    user_reference = atome_client.get_user_reference()
    _LOGGER.debug("login user reference is %s", user_reference)

    # Login Stat Data
    login_stat_coordinator = await async_create_login_stat_coordinator(
        hass, atome_client, login_stat_sensor_name, atome_linky_number
    )

    # Live Data
    live_coordinator = await async_create_live_coordinator(
        hass, atome_client, live_sensor_name
    )

    # Periodic Data
    daily_coordinator = await async_create_period_coordinator(
        hass, atome_client, daily_sensor_name, DAILY_PERIOD_TYPE, DAILY_SCAN_INTERVAL
    )
    weekly_coordinator = await async_create_period_coordinator(
        hass, atome_client, weekly_sensor_name, WEEKLY_PERIOD_TYPE, WEEKLY_SCAN_INTERVAL
    )
    monthly_coordinator = await async_create_period_coordinator(
        hass,
        atome_client,
        monthly_sensor_name,
        MONTHLY_PERIOD_TYPE,
        MONTHLY_SCAN_INTERVAL,
    )
    yearly_coordinator = await async_create_period_coordinator(
        hass, atome_client, yearly_sensor_name, YEARLY_PERIOD_TYPE, YEARLY_SCAN_INTERVAL
    )

    # declaration of all sensors
    sensors = [
        AtomeLoginStatSensor(
            login_stat_coordinator,
            login_stat_sensor_name,
            user_reference,
            atome_device_name,
            atome_linky_number,
        ),
        AtomeLiveSensor(
            live_coordinator, live_sensor_name, user_reference, atome_device_name
        ),
        AtomePeriodSensor(
            daily_coordinator,
            daily_sensor_name,
            user_reference,
            atome_device_name,
            DAILY_PERIOD_TYPE,
        ),
        AtomePeriodSensor(
            weekly_coordinator,
            weekly_sensor_name,
            user_reference,
            atome_device_name,
            WEEKLY_PERIOD_TYPE,
        ),
        AtomePeriodSensor(
            monthly_coordinator,
            monthly_sensor_name,
            user_reference,
            atome_device_name,
            MONTHLY_PERIOD_TYPE,
        ),
        AtomePeriodSensor(
            yearly_coordinator,
            yearly_sensor_name,
            user_reference,
            atome_device_name,
            YEARLY_PERIOD_TYPE,
        ),
    ]

    return sensors


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Atome sensor."""
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    atome_linky_number = config.get(CONF_ATOME_LINKY_NUMBER, DEFAULT_ATOME_LINKY_NUMBER)
    sensor_root_name = config.get(CONF_NAME, DEFAULT_NAME)

    sensors = await create_coordinators_and_sensors(
        hass, username, password, atome_linky_number, sensor_root_name
    )

    async_add_entities(sensors, True)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up KeyAtome sensors based on a config entry."""
    # Example of code if needed
    # coordinator = hass.data[DOMAIN][DATA_COORDINATOR][config_entry.entry_id]
    # unique_id = config_entry.unique_id

    config = config_entry.data

    # Get data from config flow
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    atome_linky_number = config.get(CONF_ATOME_LINKY_NUMBER, DEFAULT_ATOME_LINKY_NUMBER)
    sensor_root_name = config.get(CONF_NAME, DEFAULT_NAME)

    sensors = await create_coordinators_and_sensors(
        hass, username, password, atome_linky_number, sensor_root_name
    )

    async_add_entities(sensors, True)


class AtomeGenericServerEndPoint:
    """Basic class to retrieve data from server."""

    def __init__(self, atome_client, name, period_type):
        """Initialize the data."""
        self._atome_client = atome_client
        self._name = name
        self._period_type = period_type


class AtomeLoginStatData:
    """Class used to store Login Stat Data."""

    def __init__(self):
        """Initialize the data."""
        self.user_id = None
        self.user_ref = None
        self.list_user_ref = ""


class AtomeLoginStatServerEndPoint(AtomeGenericServerEndPoint):
    """Class used to retrieve Login Stat Data."""

    def __init__(self, atome_client, name, atome_linky_number):
        """Initialize the data."""
        super().__init__(atome_client, name, LOGIN_STAT_TYPE)
        self._login_stat_data = AtomeLoginStatData()
        self._atome_linky_number = atome_linky_number

    def _retrieve_login_stat(self):
        """Retrieve Live data."""
        values = self._atome_client.login()
        error_flag = False
        try:
            self._login_stat_data.user_id = str(values["id"])
            self._login_stat_data.user_ref = values["subscriptions"][
                (self._atome_linky_number - 1)
            ]["reference"]

            self._login_stat_data.list_user_ref = ""
            for i in range(len(values["subscriptions"])):
                self._login_stat_data.list_user_ref = (
                    self._login_stat_data.list_user_ref
                    + ", "
                    + str(values["subscriptions"][i]["reference"])
                )

            _LOGGER.debug(
                "Updating Atome Login data. ID: %s, REF: %s",
                self._login_stat_data.user_id,
                self._login_stat_data.user_ref,
            )
        except:
            _LOGGER.error("Login Stat Data : Missing values in values: %s", values)
            error_flag = True
        return not error_flag

    def retrieve_data(self):
        """Return current power value."""
        _LOGGER.debug("Login Stat Data : Perform login")
        self._login_stat_data = AtomeLoginStatData()
        self._retrieve_login_stat()
        return self._login_stat_data


class AtomeLiveData:
    """Class used to store Live Data."""

    def __init__(self):
        """Initialize the data."""
        self.live_power = None
        self.subscribed_power = None
        self.is_connected = None


class AtomeLiveServerEndPoint(AtomeGenericServerEndPoint):
    """Class used to retrieve Live Data."""

    def __init__(self, atome_client, name):
        """Initialize the data."""
        super().__init__(atome_client, name, LIVE_TYPE)
        self._live_data = AtomeLiveData()

    def _retrieve_live(self, retry_flag):
        """Retrieve Live data."""
        values = self._atome_client.get_live()
        if (
            values is not None
            and (values.get("last") is not None)
            and (values.get("subscribed") is not None)
            and (values.get("isConnected") is not None)
        ):
            self._live_data.live_power = values["last"]
            self._live_data.subscribed_power = values["subscribed"]
            self._live_data.is_connected = values["isConnected"]
            _LOGGER.debug(
                "Updating Atome live data. Got: %f, isConnected: %s, subscribed: %d",
                self._live_data.live_power,
                self._live_data.is_connected,
                self._live_data.subscribed_power,
            )
            return True
        if retry_flag:
            _LOGGER.error("Live Data : Missing last value in values: %s", values)
        else:
            _LOGGER.warning("Live Data : Missing last value in values: %s", values)
        return False

    def retrieve_data(self):
        """Return current power value."""
        _LOGGER.debug("Live Data : Update Usage")
        self._live_data = AtomeLiveData()
        if not self._retrieve_live(False):
            _LOGGER.debug("Perform Reconnect during live request")
            self._atome_client.login()
            self._retrieve_live(True)
        return self._live_data


class AtomePeriodData:
    """Class used to store period Data."""

    def __init__(self):
        """Initialize the data."""
        self.usage = None
        self.price = None


class AtomePeriodServerEndPoint(AtomeGenericServerEndPoint):
    """Class used to retrieve Period Data."""

    def __init__(self, atome_client, name, period_type):
        """Initialize the data."""
        super().__init__(atome_client, name, period_type)
        self._period_data = AtomePeriodData()

    def _retrieve_period_usage(self, retry_flag):
        """Return current daily/weekly/monthly/yearly power usage."""
        values = self._atome_client.get_consumption(self._period_type)
        if (
            (values is not None)
            and (values.get("total") is not None)
            and (values.get("price") is not None)
        ):
            self._period_data.usage = values["total"] / 1000
            self._period_data.price = round(values["price"], ROUND_PRICE)
            _LOGGER.debug(
                "Updating Atome %s data. Got: %f",
                self._period_type,
                self._period_data.usage,
            )
            return True

        if retry_flag:
            _LOGGER.error(
                "%s : Missing total value in values: %s", self._period_type, values
            )
        else:
            _LOGGER.warning(
                "%s : Missing total value in values: %s", self._period_type, values
            )
        return False

    def retrieve_data(self):
        """Return current daily/weekly/monthly/yearly power usage with one retry."""
        self._period_data = AtomePeriodData()
        if not self._retrieve_period_usage(False):
            _LOGGER.debug("Perform Reconnect during %s", self._period_type)
            self._atome_client.login()
            self._retrieve_period_usage(True)
        return self._period_data


class AtomeGenericSensor(CoordinatorEntity, SensorEntity):
    """Basic class to store atome client."""

    def __init__(
        self, coordinator, name, user_reference, atome_device_name, period_type
    ):
        """Initialize the data."""
        super().__init__(coordinator)
        self._name = name
        self._period_type = period_type
        self._user_reference = user_reference
        self._atome_device_name = atome_device_name

        self._attr_name = self._name
        self._attr_unique_id = self._name + self._user_reference

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def update() -> None:
            """Update the state."""
            self.update_from_latest_data()
            self.async_write_ha_state()

        self.async_on_remove(self.coordinator.async_add_listener(update))

        self.update_from_latest_data()

    @callback
    def update_from_latest_data(self) -> None:
        """Update the entity from the latest data."""
        raise NotImplementedError

    @property
    def device_info(self):
        """Device info for KeyAtome Server."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._user_reference)},
            manufacturer="AtomeLinkyTotalEnergies",
            name=self._atome_device_name,
            model="AtomeLinky",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=DEVICE_CONF_URL,
        )


class AtomeLoginStatSensor(AtomeGenericSensor):
    """Class used to retrieve Login Stat Data."""

    def __init__(
        self, coordinator, name, user_reference, atome_device_name, atome_linky_number
    ):
        """Initialize the data."""
        super().__init__(
            coordinator, name, user_reference, atome_device_name, LOGIN_STAT_TYPE
        )
        self._login_stat_data = None
        self._atome_linky_number = atome_linky_number

        # HA attributes
        # self._attr_native_unit_of_measurement = "id"
        # self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        self._attr_icon = "mdi:account"

    @property
    def extra_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {ATTR_ATTRIBUTION: ATTRIBUTION}
        attr["user_id"] = self._login_stat_data.user_id
        attr["user_reference"] = self._login_stat_data.user_ref
        attr["linky_number_within_account"] = self._atome_linky_number
        attr["list_user_reference"] = self._login_stat_data.list_user_ref
        return attr

    @property
    def native_value(self):
        """Return the state of this device."""
        _LOGGER.debug("Login Stat Data : display")
        return self._login_stat_data.user_ref

    def update_from_latest_data(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Async Update Login Stat sensor %s", self._name)
        self._login_stat_data = self.coordinator.data


class AtomeLiveSensor(AtomeGenericSensor):
    """Class used to retrieve Live Data."""

    def __init__(self, coordinator, name, user_reference, atome_device_name):
        """Initialize the data."""
        super().__init__(
            coordinator, name, user_reference, atome_device_name, LIVE_TYPE
        )
        self._live_data = None

        # HA attributes
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_native_unit_of_measurement = POWER_WATT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def extra_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {ATTR_ATTRIBUTION: ATTRIBUTION}
        attr["subscribed_power"] = self._live_data.subscribed_power
        attr["is_connected"] = self._live_data.is_connected
        return attr

    @property
    def native_value(self):
        """Return the state of this device."""
        _LOGGER.debug("Live Data : display")
        return self._live_data.live_power

    def update_from_latest_data(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Async Live Data Update sensor %s", self._name)
        self._live_data = self.coordinator.data


class AtomePeriodSensor(RestoreEntity, AtomeGenericSensor):
    """Class used to retrieve Period Data."""

    def __init__(
        self, coordinator, name, user_reference, atome_device_name, period_type
    ):
        """Initialize the data."""
        super().__init__(
            coordinator, name, user_reference, atome_device_name, period_type
        )
        self._period_data = AtomePeriodData()
        self._previous_period_data = AtomePeriodData()
        # last valid period data
        self._last_valid_period_data = AtomePeriodData()

        # HA attributes
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    async def async_added_to_hass(self):
        """Handle added to Hass."""
        # restore from previous run
        state_recorded = await self.async_get_last_state()
        if state_recorded:
            self._period_data.usage = format_receive_value(state_recorded.state)
            self._period_data.price = format_receive_value(
                state_recorded.attributes.get(ATTR_PERIOD_PRICE)
            )
            self._previous_period_data.usage = format_receive_value(
                state_recorded.attributes.get(ATTR_PREVIOUS_PERIOD_USAGE)
            )
            self._previous_period_data.price = format_receive_value(
                state_recorded.attributes.get(ATTR_PREVIOUS_PERIOD_PRICE)
            )
            if self._period_data.usage:
                self._last_valid_period_data = self._period_data
        await super().async_added_to_hass()

    @property
    def extra_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {ATTR_ATTRIBUTION: ATTRIBUTION}
        attr[ATTR_PERIOD_PRICE] = self._period_data.price
        attr[ATTR_PREVIOUS_PERIOD_USAGE] = self._previous_period_data.usage
        attr[ATTR_PREVIOUS_PERIOD_PRICE] = self._previous_period_data.price
        return attr

    @property
    def native_value(self):
        """Return the state of this device."""
        return self._period_data.usage

    def update_from_latest_data(self):
        """Fetch new state data for this sensor."""
        _LOGGER.debug("Async Period Update sensor %s", self._name)
        new_period_data = self.coordinator.data
        # compute value below which it will be a valid reset (decrease)
        if self._period_type == DAILY_PERIOD_TYPE:
            period_type_min_margin = 1.0
        elif (
            self._period_type == WEEKLY_PERIOD_TYPE
            or self._period_type == MONTHLY_PERIOD_TYPE
        ):
            period_type_min_margin = 10
        else:
            period_type_min_margin = 100

        # compute consistency
        if new_period_data.usage and self._last_valid_period_data.usage:
            _LOGGER.debug(
                "Check consistecy period %s : New %s ; Current %s",
                self._name,
                new_period_data.usage,
                self._last_valid_period_data.usage,
            )
            if (new_period_data.usage > period_type_min_margin) and (
                (new_period_data.usage < self._last_valid_period_data.usage)
            ):
                # reset received value : none value
                new_period_data = AtomePeriodData()
                _LOGGER.error("Period are strictly increasing except reset to zero")

        # compute last previous data
        if new_period_data.usage and self._last_valid_period_data.usage:
            _LOGGER.debug(
                "Check period %s : New %s ; Current %s",
                self._name,
                new_period_data.usage,
                self._last_valid_period_data.usage,
            )
            # Take a margin to avoid storage of previous data
            if (new_period_data.usage < period_type_min_margin) and (
                (new_period_data.usage - self._last_valid_period_data.usage) < (-1.0)
            ):
                _LOGGER.debug(
                    "Previous period %s becomes %s",
                    self._name,
                    self._last_valid_period_data.usage,
                )
                self._previous_period_data = self._last_valid_period_data
        self._period_data = new_period_data
        if new_period_data.usage:
            self._last_valid_period_data = new_period_data
