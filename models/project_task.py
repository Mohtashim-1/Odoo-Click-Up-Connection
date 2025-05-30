from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    clickup_task_id = fields.Char('ClickUp Task ID', index=True)
    crm_lead_id = fields.Many2one('crm.lead', string='Linked Lead')


    def set_in_progress(self):
        for task in self:
            task.state = '01_in_progress'

    def set_changes_requested(self):
        for task in self:
            task.state = '02_changes_requested'

    def set_approved(self):
        for task in self:
            task.state = '03_approved'

    def action_convert_to_lead(self):
        for task in self:
            if task.crm_lead_id:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'crm.lead',
                    'res_id': task.crm_lead_id.id,
                    'view_mode': 'form',
                    'target': 'current',
                }

            lead = self.env['crm.lead'].create({
                'name': task.name,
                'description': task.description,
                'user_id': task.user_ids and task.user_ids[0].id or self.env.user.id,
            })
            task.crm_lead_id = lead.id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'crm.lead',
                'res_id': lead.id,
                'view_mode': 'form',
                'target': 'current',
            }

