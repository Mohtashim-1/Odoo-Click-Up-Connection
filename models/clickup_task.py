import requests
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ClickUpTask(models.Model):
    _name = 'clickup.task'
    _description = 'ClickUp Task'

    name = fields.Char('Task Name')
    task_id = fields.Char('ClickUp Task ID')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    def action_fetch_teams(self):
        token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        if not token:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('No ClickUp token found for this user.'),
                    'type': 'danger'
                }
            }

        headers = {
            "Authorization": f"Bearer {token.access_token}"
        }

        url = "https://api.clickup.com/api/v2/team"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            _logger.info("✅ ClickUp Teams: %s", data)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Fetched team: %s' % data['teams'][0]['name']),
                    'type': 'success'
                }
            }
        else:
            _logger.error("❌ Failed to fetch teams: %s", response.text)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Failed to fetch teams.'),
                    'type': 'danger'
                }
            }
            
    
    @api.model
    def fetch_and_store_teams(self):
        token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        if not token:
            raise ValueError("No ClickUp token found for this user.")

        headers = {
            "Authorization": f"Bearer {token.access_token}"
        }
        url = "https://api.clickup.com/api/v2/team"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            teams = response.json().get('teams', [])
            for team in teams:
                self.env['clickup.team'].sudo().create({
                    'name': team.get('name'),
                    'team_id': team.get('id'),
                    'color': team.get('color'),
                    'user_id': self.env.user.id,
                })
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Teams saved successfully!'),
                    'type': 'success'
                }
            }
        else:
            _logger.error("❌ Failed to fetch teams: %s", response.text)
            raise ValueError("Failed to fetch teams.")

