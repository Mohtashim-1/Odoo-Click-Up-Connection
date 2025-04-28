import requests
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ClickUpTeam(models.Model):
    _name = 'clickup.team'
    _description = 'ClickUp Team'

    name = fields.Char('Team Name')
    team_id = fields.Char('ClickUp Team ID')
    color = fields.Char('Color')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    def action_fetch_teams_from_clickup(self):
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
                # Avoid duplicate insert if team already exists
                existing_team = self.env['clickup.team'].sudo().search([('team_id', '=', team.get('id'))], limit=1)
                if not existing_team:
                    self.env['clickup.team'].sudo().create({
                        'name': team.get('name'),
                        'team_id': team.get('id'),
                        'color': team.get('color'),
                        'user_id': self.env.user.id,
                    })
            _logger.info("✅ %s teams saved in Odoo.", len(teams))
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
            raise ValueError("Failed to fetch teams: %s" % response.text)
