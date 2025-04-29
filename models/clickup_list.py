
import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ClickUpList(models.Model):
    _name = 'clickup.list'
    _description = 'ClickUp List'

    name = fields.Char('List Name')
    list_id = fields.Char('ClickUp List ID')
    space_id = fields.Many2one('clickup.space', string='ClickUp Space')  # ✅ add space_id
    folder_id = fields.Many2one('clickup.folder', string='ClickUp Folder')  # Optional if you use folders
    team_id = fields.Many2one('clickup.team', string='ClickUp Team')        # ✅ add team_id
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    def action_fetch_lists_from_clickup(self):
        for folder in self:
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise ValueError("No ClickUp token found for this user.")

            headers = {"Authorization": f"Bearer {token.access_token}"}
            url = f"https://api.clickup.com/api/v2/folder/{folder.folder_id}/list"
            
            _logger.info("Fetching ClickUp Lists from Folder ID: %s", folder.folder_id)
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                lists = response.json().get('lists', [])
                for lst in lists:
                    existing = self.env['clickup.list'].sudo().search([('list_id', '=', lst.get('id'))], limit=1)
                    if not existing:
                        self.env['clickup.list'].sudo().create({
                            'name': lst.get('name'),
                            'list_id': lst.get('id'),
                            'folder_id': folder.id,
                            'user_id': self.env.user.id,
                        })
                _logger.info("Saved %s lists from ClickUp", len(lists))
            else:
                raise ValueError("Failed to fetch lists from ClickUp.")
            
    def action_fetch_tasks_from_list(self):
        for rec in self:
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise UserError("No ClickUp token found.")

            url = f"https://api.clickup.com/api/v2/list/{rec.list_id}/task"
            headers = {
                "Authorization": f"Bearer {token.access_token}",
            }

            _logger.info("➡️ Fetching Tasks from List ID: %s", rec.list_id)
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                tasks = response.json().get('tasks', [])
                _logger.info("✅ %s Tasks fetched", len(tasks))

                for task in tasks:
                    task_id = task.get('id')
                    task_name = task.get('name')

                    # Prevent duplicates
                    existing_task = self.env['project.task'].sudo().search([('clickup_task_id', '=', task_id)], limit=1)
                    if not existing_task:
                        self.env['project.task'].sudo().create({
                            'name': task_name,
                            'clickup_task_id': task_id,
                            'activity_user_id': self.env.user.id,       # Assigned user in Odoo
                        })

            else:
                raise UserError(f"Failed to fetch tasks: {response.status_code} - {response.text}")

