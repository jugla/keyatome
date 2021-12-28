"""Constants for Key Atome."""
from datetime import timedelta

# Domain name
DOMAIN = "keyatome"

# Sensor default name
DEFAULT_NAME = "Atome"

# sensor name
LIVE_NAME_SUFFIX = " Live Power"
DAILY_NAME_SUFFIX = " Daily"
WEEKLY_NAME_SUFFIX = " Weekly"
MONTHLY_NAME_SUFFIX = " Monthly"
YEARLY_NAME_SUFFIX = " Yearly"

# Attribution
ATTRIBUTION = "Data provided by TotalEnergies"

# Attribute sensor name
ATTR_PREVIOUS_PERIOD_USAGE = "previous_consumption"
ATTR_PREVIOUS_PERIOD_PRICE = "previous_price"
ATTR_PERIOD_PRICE = "price"

# Scan interval
LIVE_SCAN_INTERVAL = timedelta(seconds=30)
DAILY_SCAN_INTERVAL = timedelta(seconds=150)
WEEKLY_SCAN_INTERVAL = timedelta(hours=1)
MONTHLY_SCAN_INTERVAL = timedelta(hours=1)
YEARLY_SCAN_INTERVAL = timedelta(days=1)

# Type to call py key atome
LIVE_TYPE = "live"
