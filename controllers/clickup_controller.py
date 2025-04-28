import requests
from odoo import http
from odoo.http import request
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


# @http.route('/clickup/callback', type='http', auth='public', csrf=False)
# def clickup_callback(self, **kwargs):
#     code = kwargs.get('code')
#     user = request.env.user
#     if not code:
#         return "Authorization failed. No code received."

#     token_url = "https://api.clickup.com/api/v2/oauth/token"
#     payload = {
#         "client_id": user.clickup_client_id,
#         "client_secret": user.clickup_client_secret,
#         "code": code,
#         "redirect_uri": user.clickup_redirect_uri,
#     }

#     response = requests.post(token_url, json=payload)
#     if response.status_code == 200:
#         data = response.json()
#         access_token = data.get('access_token')
#         refresh_token = data.get('refresh_token')

#         request.env['clickup.token'].sudo().create({
#             'user_id': user.id,
#             'access_token': access_token,
#             'refresh_token': refresh_token,
#         })

#         return "✅ ClickUp Authorization Successful!"
#     else:
#         return f"Failed to exchange code: {response.text}"

@http.route('/clickup/callback', type='http', auth="public", website=True)
def clickup_callback(self, **params):
    authorization_code = params.get('code')
    
    if authorization_code:
        user = request.env.user
        user.action_clickup_callback(authorization_code)
        return request.render('clickup_connector.clickup_authorization_success')
    else:
        return request.render('clickup_connector.clickup_authorization_failure')