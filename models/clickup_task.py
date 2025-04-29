
import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ClickUpTask(models.Model):
    _name = 'clickup.task'
    _description = 'ClickUp Task'

    name = fields.Char('Task Name')
    task_id = fields.Char('ClickUp Task ID')
    list_id = fields.Many2one('clickup.list', string='ClickUp List')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    def action_fetch_tasks_from_clickup(self):
        for lst in self:
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise ValueError("No ClickUp token found for this user.")

            headers = {"Authorization": f"Bearer {token.access_token}"}
            url = f"https://api.clickup.com/api/v2/list/{lst.list_id.list_id}/task"

            _logger.info("Fetching ClickUp Tasks from List ID: %s", lst.list_id.list_id)
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                tasks = response.json().get('tasks', [])
                for task in tasks:
                    existing = self.env['clickup.task'].sudo().search([('task_id', '=', task.get('id'))], limit=1)
                    if not existing:
                        self.env['clickup.task'].sudo().create({
                            'name': task.get('name'),
                            'task_id': task.get('id'),
                            'list_id': lst.list_id.id,
                            'user_id': self.env.user.id,
                        })
                _logger.info("Saved %s tasks from ClickUp", len(tasks))
            else:
                raise ValueError("Failed to fetch tasks from ClickUp.")