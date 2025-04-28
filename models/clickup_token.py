from odoo import models, fields

class ClickUpToken(models.Model):
    _name = "clickup.token"
    _description = "ClickUp Token Storage"

    user_id = fields.Many2one('res.users', string="User", required=True)
    access_token = fields.Char("Access Token", required=True)
    refresh_token = fields.Char("Refresh Token")
