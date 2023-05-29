from typing import Any, Callable, Dict, Optional
from homeassistant.helpers.entity import (
    Entity,
    DeviceInfo
)
import requests
from ..const import (
    DOMAIN
)

class StakingRewardsPosition(Entity):
    """Staking Reward"""
    def __init__(self, api, wallet, delegated_position_key, data, icon):
        super().__init__()
        self.api = api
        self.wallet = wallet
        self.delegated_position_key = delegated_position_key
        #self.data = data
        self.path = ['rewards', delegated_position_key]
        self.attributes = data
        self._available = True
        self._icon = icon
        self._unique_id = 'helium.staking.reward.position.'+self.attributes['delegated_position_key']
        self.uom = self.attributes['delegated_sub_dao'].upper()

        title = str(self.attributes['hnt_amount'])+' HNT '+self.attributes['lockup_type'].upper()+' '+self.attributes['duration_string']
        self._name = 'Helium Staking Wallet '+wallet[:4]+' '+title
        self.device_unique_id = "helium.staking.rewards."+wallet[:4]
        self.device_name = "Helium Staking Wallet "+wallet[:4]
        #self.device_name_user = "Helium Staking for Wallet "+wallet[:4]

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def icon(self) -> str | None:
        return self._icon
    
    @property
    def should_poll(self):
        return True

    @property
    def unit_of_measurement(self):
        return self.uom

    @property
    def extra_state_attributes(self):
        return self.attributes

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.device_unique_id)
            },
            name=self.device_name,
            manufacturer='Helium'
        )

    async def async_update(self):
        try:
            response = await self.api.get_data('staking-rewards/'+str(self.wallet))
            if response.status_code != 200:
                return
            
            value = response.json()
            for key in self.path:
                value = value[key]
            
            #value = int(value)
            #value = round(value / (10 ** 6),2)
            self._state = round(float(value['unclaimed_rewards']),2)
            self.attributes = value
            self._available = True

        except (requests.exceptions.RequestException):
            self._available = False
            _LOGGER.exception("Error retrieving wallet balance from backend")
