from odoo import models, fields, api

class ClickUpTeam(models.Model):
    _name = 'clickup.team'
    _description = 'ClickUp Team'

    clickup_id = fields.Char('ClickUp Team ID')
    name = fields.Char('Name')

    def sync_teams(self):
        api = self.env['clickup.api']
        data = api.call_clickup('GET', 'team')
        for team in data.get('teams', []):
            self.create({
                'clickup_id': team['id'],
                'name': team['name'],
            })

class ClickUpSpace(models.Model):
    _name = 'clickup.space'
    _description = 'ClickUp Space'

    clickup_id = fields.Char('ClickUp Space ID')
    name = fields.Char('Name')
    team_id = fields.Many2one('clickup.team', 'Team')

    def sync_spaces(self, team_clickup_id):
        api = self.env['clickup.api']
        data = api.call_clickup('GET', f'team/{team_clickup_id}/space')
        for space in data.get('spaces', []):
            self.create({
                'clickup_id': space['id'],
                'name': space['name'],
            })

class ClickUpList(models.Model):
    _name = 'clickup.list'
    _description = 'ClickUp List'

    clickup_id = fields.Char('ClickUp List ID')
    name = fields.Char('Name')
    space_id = fields.Many2one('clickup.space', 'Space')

    def sync_lists(self, space_clickup_id):
        api = self.env['clickup.api']
        data = api.call_clickup('GET', f'space/{space_clickup_id}/list')
        for lst in data.get('lists', []):
            self.create({
                'clickup_id': lst['id'],
                'name': lst['name'],
            })

class ClickUpTask(models.Model):
    _name = 'clickup.task'
    _description = 'ClickUp Task'

    clickup_id = fields.Char('ClickUp Task ID')
    name = fields.Char('Name')
    list_id = fields.Many2one('clickup.list', 'List')

    def sync_tasks(self, list_clickup_id):
        api = self.env['clickup.api']
        data = api.call_clickup('GET', f'list/{list_clickup_id}/task')
        for task in data.get('tasks', []):
            self.create({
                'clickup_id': task['id'],
                'name': task['name'],
            })

    def create_task(self, list_clickup_id, name):
        api = self.env['clickup.api']
        task_data = {
            "name": name,
        }
        task = api.call_clickup('POST', f'list/{list_clickup_id}/task', data=task_data)
        if task:
            self.create({
                'clickup_id': task['id'],
                'name': task['name'],
            })
