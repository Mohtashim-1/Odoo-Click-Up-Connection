from odoo import models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def set_in_progress(self):
        for task in self:
            task.state = '01_in_progress'

    def set_changes_requested(self):
        for task in self:
            task.state = '02_changes_requested'

    def set_approved(self):
        for task in self:
            task.state = '03_approved'
