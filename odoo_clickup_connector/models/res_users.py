import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    clickup_client_id = fields.Char(string="ClickUp Client ID")
    clickup_client_secret = fields.Char(string="ClickUp Client Secret")
    clickup_redirect_uri = fields.Char(string="Redirect URI", default='http://localhost:8070/clickup/callback')
    clickup_access_token = fields.Char(string="ClickUp Access Token", readonly=True)

    def action_authorize_clickup(self):
        """
        Initiates the ClickUp OAuth flow by redirecting the user to ClickUp's authorization page.
        """
        base_url = 'https://app.clickup.com/api'
        auth_url = f"{base_url}/?client_id={self.clickup_client_id}&redirect_uri={self.clickup_redirect_uri}&scope=task:read&response_type=code"
        
        return {
            'type': 'ir.actions.act_url',
            'url': auth_url,
            'target': 'new'
        }

    def action_clickup_callback(self, authorization_code):
        """
        Handle the callback from ClickUp after authorization.
        Exchange the authorization code for an access token.
        """
        access_token = self.get_clickup_access_token(authorization_code)
        
        if access_token:
            # Store the access token securely
            self.write({'clickup_access_token': access_token})
            return {'type': 'ir.actions.act_window.message', 'title': 'Success', 'message': 'Authorization successful!'}
        else:
            raise UserError("Failed to exchange authorization code for access token.")

    def get_clickup_access_token(self, authorization_code):
        """
        Exchange the authorization code for an access token.
        """
        url = "https://api.clickup.com/api/v2/oauth/token"
        payload = {
            'client_id': self.clickup_client_id,
            'client_secret': self.clickup_client_secret,
            'redirect_uri': self.clickup_redirect_uri,
            'code': authorization_code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            return None
