"""Constants for Key Atome."""
from datetime import timedelta

# Tools
DEBUG_FLAG = False

# Domain name
DOMAIN = "keyatome"

# Config flow
DATA_COORDINATOR = "coordinator"

# Conf atome_linky_number
CONF_ATOME_LINKY_NUMBER = "atome_linky_number"
DEFAULT_ATOME_LINKY_NUMBER = 1

# Sensor default name
DEFAULT_NAME = "Atome"

# sensor name
LOGIN_STAT_NAME_SUFFIX = "_Login_Stat"
LIVE_NAME_SUFFIX = " Live Power"
DAILY_NAME_SUFFIX = " Daily"
WEEKLY_NAME_SUFFIX = " Weekly"
MONTHLY_NAME_SUFFIX = " Monthly"
YEARLY_NAME_SUFFIX = " Yearly"

# device name
DEVICE_NAME_SUFFIX = " Device"
DEVICE_CONF_URL = "https://www.totalenergies.fr/clients"

# Attribution
ATTRIBUTION = "Data provided by TotalEnergies"

# Attribute sensor name
ATTR_PREVIOUS_PERIOD_USAGE = "previous_consumption"
ATTR_PREVIOUS_PERIOD_PRICE = "previous_price"
ATTR_PERIOD_PRICE = "price"

# Max number of retry for pykeyatome
MAX_PYKEYATOME_RETRY = 4

# Scan interval (avoid synchronisation to lower request per seconds on server)
LOGIN_STAT_SCAN_INTERVAL = timedelta(hours=1, minutes=30, seconds=13)
LIVE_SCAN_INTERVAL = timedelta(seconds=30)
DAILY_SCAN_INTERVAL = timedelta(minutes=5, seconds=3)
WEEKLY_SCAN_INTERVAL = timedelta(hours=1, seconds=5)
MONTHLY_SCAN_INTERVAL = timedelta(hours=1, seconds=7)
YEARLY_SCAN_INTERVAL = timedelta(days=1, seconds=11)

# Value used to determine if periodic information are allowed to be reset
# as Dayly is performed every 5 minutes,
# the first request can be done with a result below 2kW
DAYLY_TRUST_MAX_INTERVAL = 2
# as Weekly/Monthly are performed every hour,
# the first request can be done with a result below 20kW
WEEKLY_TRUST_MAX_INTERVAL = 20
MONTHLY_TRUST_MAX_INTERVAL = 20
# as Yearly request is performed once a day,
# the first request can be done with a result below 200kW
YEARLY_TRUST_MAX_INTERVAL = 200


# Type to call py key atome
LIVE_TYPE = "live"
LOGIN_STAT_TYPE = "login_stat"

# Round price
ROUND_PRICE = 2
