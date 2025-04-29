from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    clickup_task_id = fields.Char("ClickUp Task ID", readonly=True)
