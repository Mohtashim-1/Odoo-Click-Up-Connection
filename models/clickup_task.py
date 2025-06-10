
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

    # def action_fetch_tasks_from_clickup(self):
    #     for lst in self:
    #         token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
    #         if not token:
    #             raise ValueError("No ClickUp token found for this user.")

    #         headers = {"Authorization": f"Bearer {token.access_token}"}
    #         url = f"https://api.clickup.com/api/v2/list/{lst.list_id.list_id}/task"

    #         _logger.info("Fetching ClickUp Tasks from List ID: %s", lst.list_id.list_id)
    #         response = requests.get(url, headers=headers)

    #         if response.status_code == 200:
    #             tasks = response.json().get('tasks', [])
    #             for task in tasks:
    #                 existing = self.env['clickup.task'].sudo().search([('task_id', '=', task.get('id'))], limit=1)
    #                 if not existing:
    #                     self.env['clickup.task'].sudo().create({
    #                         'name': task.get('name'),
    #                         'task_id': task.get('id'),
    #                         'list_id': lst.list_id.id,
    #                         'user_id': self.env.user.id,
    #                     })
    #             _logger.info("Saved %s tasks from ClickUp", len(tasks))
    #         else:
    #             raise ValueError("Failed to fetch tasks from ClickUp.")

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
                created_count = 0

                for lst in lists:
                    list_id = lst.get('id')
                    list_name = lst.get('name')

                    existing = self.env['clickup.list'].sudo().search([('list_id', '=', list_id)], limit=1)
                    if not existing:
                        # 🔍 Check if a project with the same name already exists
                        project = self.env['project.project'].sudo().search([('name', '=', list_name)], limit=1)
                        if not project:
                            project = self.env['project.project'].sudo().create({
                                'name': list_name,
                                'user_id': self.env.user.id,
                            })

                        # 📝 Create ClickUp List and link it to the project
                        self.env['clickup.list'].sudo().create({
                            'name': list_name,
                            'list_id': list_id,
                            'folder_id': folder.id,
                            'space_id': folder.space_id.id,
                            'team_id': folder.team_id.id,
                            'user_id': self.env.user.id,
                            'project_id': project.id,
                        })

                        created_count += 1

                _logger.info("✅ Saved %s new lists from ClickUp", created_count)
            else:
                raise ValueError(f"Failed to fetch lists from ClickUp: {response.status_code} - {response.text}")
