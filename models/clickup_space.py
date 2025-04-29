import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ClickUpSpace(models.Model):
    _name = 'clickup.space'
    _description = 'ClickUp Space'

    name = fields.Char('Space Name')
    space_id = fields.Char('ClickUp Space ID')
    team_id = fields.Many2one('clickup.team', string='ClickUp Team')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    def action_fetch_spaces_from_clickup(self):
        for team in self:
            # Find OAuth Token
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise ValueError("❌ No ClickUp token found for this user.")

            headers = {
                "Authorization": f"Bearer {token.access_token}"
            }

            # Correct URL for fetching Spaces from ClickUp
            clickup_team_id = team.team_id.team_id  # Important: team_id.team_id
            url = f"https://api.clickup.com/api/v2/team/{clickup_team_id}/space"

            _logger.info("➡️ Fetching ClickUp Spaces for Team ID: %s", clickup_team_id)
            _logger.info("➡️ URL: %s", url)

            # Call ClickUp API
            response = requests.get(url, headers=headers)

            # Always log full response first
            _logger.info("📦 ClickUp Spaces Fetch Status: %s", response.status_code)
            _logger.info("📦 ClickUp Spaces Fetch Response: %s", response.text)

            if response.status_code == 200:
                spaces = response.json().get('spaces', [])
                _logger.info("✅ %s spaces received from ClickUp", len(spaces))

                for space in spaces:
                    # Prevent duplicate spaces in Odoo
                    existing = self.env['clickup.space'].sudo().search([('space_id', '=', space.get('id'))], limit=1)
                    if not existing:
                        self.env['clickup.space'].sudo().create({
                            'name': space.get('name'),
                            'space_id': space.get('id'),
                            'team_id': team.team_id.id,
                            'user_id': self.env.user.id,
                        })
                _logger.info("✅ Saved %s spaces in Odoo", len(spaces))

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Spaces fetched and saved successfully.'),
                        'type': 'success',
                        'sticky': False,
                    }
                }

            else:
                # If ClickUp gave error response
                raise ValueError(_("❌ Failed to fetch spaces from ClickUp. Please check Odoo logs for details."))


    def action_fetch_lists_from_clickup(self):
        for space in self:
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise ValueError("❌ No ClickUp token found for this user.")

            headers = {
                "Authorization": f"Bearer {token.access_token}"
            }

            url = f"https://api.clickup.com/api/v2/space/{space.space_id}/list"
            _logger.info("➡️ Fetching ClickUp Lists from Space ID: %s", space.space_id)
            _logger.info("➡️ URL: %s", url)

            response = requests.get(url, headers=headers)
            _logger.info("📦 ClickUp Lists Fetch Status: %s", response.status_code)
            _logger.info("📦 ClickUp Lists Fetch Response: %s", response.text)

            if response.status_code == 200:
                lists = response.json().get('lists', [])
                for lst in lists:
                    if lst.get('id') and lst.get('name'):
                        existing = self.env['clickup.list'].sudo().search([('list_id', '=', lst.get('id'))], limit=1)
                        if not existing:
                            self.env['clickup.list'].sudo().create({
                                'name': lst.get('name'),
                                'list_id': lst.get('id'),
                                'space_id': space.id,
                                'user_id': self.env.user.id,
                            })

                _logger.info("✅ %s lists saved for space %s", len(lists), space.name)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Lists fetched and saved successfully.'),
                        'type': 'success',
                    }
                }
            else:
                raise ValueError("❌ Failed to fetch lists from ClickUp. Check logs.")
            
    def action_fetch_folders_from_space(self):
        for rec in self:
            if not rec.space_id:
                raise UserError("Space ID is missing.")

            # Fetch token properly
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise UserError("❌ No ClickUp token found for this user.")

            url = f"https://api.clickup.com/api/v2/space/{rec.space_id}/folder"
            headers = {
                "Authorization": f"Bearer {token.access_token}",
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                folders_data = response.json().get('folders', [])
                for folder in folders_data:
                    existing_folder = self.env['clickup.folder'].sudo().search([
                        ('folder_id', '=', folder.get('id'))
                    ], limit=1)

                    if not existing_folder:
                        self.env['clickup.folder'].sudo().create({
                            'name': folder.get('name'),
                            'folder_id': folder.get('id'),
                            'space_id': rec.id,
                            'user_id': self.env.user.id,
                        })
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Folders fetched and saved successfully.'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(f"Failed to fetch folders. Status Code: {response.status_code} - {response.text}")