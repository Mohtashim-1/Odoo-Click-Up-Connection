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
    space_id = fields.Many2one('clickup.space', string='ClickUp Space')
    folder_id = fields.Many2one('clickup.folder', string='ClickUp Folder')
    team_id = fields.Many2one('clickup.team', string='ClickUp Team')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    project_id = fields.Many2one('project.project', string='Project')

    def _fetch_tasks_with_token(self, access_token):
        for rec in self:
            headers = {"Authorization": f"Bearer {access_token}"}
            url = f"https://api.clickup.com/api/v2/list/{rec.list_id}/task"

            _logger.info("📥 Fetching Tasks from List ID: %s", rec.list_id)
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise UserError(f"❌ Failed to fetch tasks: {response.status_code} - {response.text}")

            tasks = response.json().get('tasks', [])
            _logger.info("✅ %s Tasks fetched", len(tasks))

            for task in tasks:
                task_id = task.get('id')
                task_name = task.get('name')

                existing_task = self.env['project.task'].sudo().search([('clickup_task_id', '=', task_id)], limit=1)
                if existing_task:
                    _logger.info("🔁 Skipping existing task: %s", task_name)
                    continue

                self.env['project.task'].sudo().create({
                    'name': task_name,
                    'clickup_task_id': task_id,
                    'project_id': rec.project_id.id,
                    'activity_user_id': rec.user_id.id,
                })
                _logger.info("✅ Created Task: %s", task_name)


    @api.model
    def cron_fetch_clickup_tasks(self):
        _logger.info("🔁 Running scheduled task fetch from ClickUp")
        all_lists = self.sudo().search([])
        for rec in all_lists:
            try:
                token = self.env['clickup.token'].sudo().search([('user_id', '=', rec.user_id.id)], limit=1)
                if not token:
                    _logger.warning(f"⚠️ No ClickUp token found for user {rec.user_id.name} (List: {rec.name})")
                    continue
                rec.sudo()._fetch_tasks_with_token(token.access_token)
            except Exception as e:
                _logger.error(f"❌ Error fetching tasks for list {rec.name}: {str(e)}")


    @api.model
    def create(self, vals):
        # Auto-create project if not given
        if not vals.get('project_id') and vals.get('name'):
            project = self.env['project.project'].sudo().search([('name', '=', vals['name'])], limit=1)
            if not project:
                project = self.env['project.project'].sudo().create({
                    'name': vals['name'],
                    'user_id': self.env.user.id,
                })
            vals['project_id'] = project.id

        return super(ClickUpList, self).create(vals)

    def action_fetch_lists_from_clickup(self):
        for folder in self:
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise UserError("❌ No ClickUp token found for this user.")

            folder_api_id = folder.folder_id.folder_id
            headers = {"Authorization": f"Bearer {token.access_token}"}
            url = f"https://api.clickup.com/api/v2/folder/{folder_api_id}/list"

            _logger.info("📥 Fetching ClickUp Lists from Folder ID: %s", folder_api_id)
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise UserError(f"❌ Failed to fetch lists from ClickUp: {response.status_code} - {response.text}")

            lists = response.json().get('lists', [])
            created_count = 0

            for lst in lists:
                list_id = lst.get('id')
                list_name = lst.get('name')

                existing = self.env['clickup.list'].sudo().search([('list_id', '=', list_id)], limit=1)
                if existing:
                    _logger.info("🔁 Skipping existing list: %s", list_name)
                    continue

                # Check or create linked project
                project = self.env['project.project'].sudo().search([('name', '=', list_name)], limit=1)
                if not project:
                    project = self.env['project.project'].sudo().create({
                        'name': list_name,
                        'user_id': self.env.user.id,
                    })
                    _logger.info("✅ Created Project: %s", project.name)

                # Create ClickUp List record
                self.env['clickup.list'].sudo().create({
                    'name': list_name,
                    'list_id': list_id,
                    'folder_id': folder.id,
                    'space_id': folder.space_id.id,
                    'team_id': folder.team_id.id,
                    'user_id': self.env.user.id,
                    'project_id': project.id,
                })
                _logger.info("✅ Created ClickUp List: %s", list_name)
                created_count += 1

            _logger.info("🎉 Created %s new lists and projects from ClickUp", created_count)

    def action_fetch_tasks_from_list(self):
        for rec in self:
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise UserError("No ClickUp token found.")

            url = f"https://api.clickup.com/api/v2/list/{rec.list_id}/task"
            headers = {"Authorization": f"Bearer {token.access_token}"}

            _logger.info("📥 Fetching Tasks from List ID: %s", rec.list_id)
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise UserError(f"❌ Failed to fetch tasks: {response.status_code} - {response.text}")

            tasks = response.json().get('tasks', [])
            _logger.info("✅ %s Tasks fetched", len(tasks))

            for task in tasks:
                task_id = task.get('id')
                task_name = task.get('name')

                existing_task = self.env['project.task'].sudo().search([('clickup_task_id', '=', task_id)], limit=1)
                if existing_task:
                    _logger.info("🔁 Skipping existing task: %s", task_name)
                    continue

                self.env['project.task'].sudo().create({
                    'name': task_name,
                    'clickup_task_id': task_id,
                    'project_id': rec.project_id.id,
                    'activity_user_id': self.env.user.id,
                })
                _logger.info("✅ Created Task: %s", task_name)
