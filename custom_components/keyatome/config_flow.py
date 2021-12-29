"""Define a config flow manager for WorldTidesInfoCustom."""

# HA library
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_NAME,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

# component library
from .const import (
    DEFAULT_NAME,
    DOMAIN,
)

KEY_ATOME_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


@config_entries.HANDLERS.register(DOMAIN)
class KeyAtomeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an WorldTidesInfoCustom config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the start of the config flow."""
        if not user_input:
            return self.async_show_form(
                step_id="user", data_schema=KEY_ATOME_DATA_SCHEMA
            )

        config_id = user_input[CONF_USERNAME]
        await self.async_set_unique_id(config_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"KeyAtome ({config_id})",
            data=user_input,
        )
