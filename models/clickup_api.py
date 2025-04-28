import requests
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ClickUpAPI(models.AbstractModel):
    _name = 'clickup.api'
    _description = 'ClickUp API Helper'

    base_url = "https://api.clickup.com/api/v2/"
    api_token = "SAT1XCT78ENCX2HK78XZOB819NSK4WEN0XG3GJDLOLGY68OLDGKL06T6IJNWD3IJ:RR608XC7RGUWPK87LK9BZ2W3A5CBR5YF"
    # client secret : client id 
    def _headers(self):
        return {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }

    def call_clickup(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}{endpoint}"
        _logger.info(f"Calling ClickUp: {method} {url}")
        response = requests.request(
            method=method,
            url=url,
            headers=self._headers(),
            json=data,
            params=params
        )
        if response.ok:
            return response.json()
        else:
            _logger.error(f"ClickUp API error: {response.text}")
            response.raise_for_status()
