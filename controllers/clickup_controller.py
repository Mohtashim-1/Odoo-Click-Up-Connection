import requests
from odoo import http
from odoo.http import request

class ClickUpController(http.Controller):

    @http.route('/clickup/authorize', type='http', auth='user')
    def clickup_authorize(self, **kwargs):
        user = request.env.user
        if not user.clickup_client_id or not user.clickup_redirect_uri:
            return "Missing ClickUp configuration. Please fill in your Client ID and Redirect URI."

        auth_url = (
            f"https://app.clickup.com/api?client_id={user.clickup_client_id}"
            f"&redirect_uri={user.clickup_redirect_uri}"
        )
        return request.redirect(auth_url)

    @http.route('/clickup/callback', type='http', auth="public", csrf=False)
    def clickup_callback(self, **params):
        code = params.get('code')

        if code:
            user = request.env.user

            # Optional: If you want to immediately exchange code for tokens:
            token_url = "https://api.clickup.com/api/v2/oauth/token"
            payload = {
                "client_id": user.clickup_client_id,
                "client_secret": user.clickup_client_secret,
                "code": code,
                "redirect_uri": user.clickup_redirect_uri,
            }

            response = requests.post(token_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                access_token = data.get('access_token')
                refresh_token = data.get('refresh_token')

                # Save the tokens to a model, e.g., 'clickup.token'
                request.env['clickup.token'].sudo().create({
                    'user_id': user.id,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                })

                return "✅ Authorization Successful! You can close this window."
            else:
                return f"❌ Failed to exchange code: {response.text}"

        else:
            return "❌ Authorization failed: No code received."
