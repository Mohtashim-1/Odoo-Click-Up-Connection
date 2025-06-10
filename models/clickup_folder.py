import requests
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ClickUpFolder(models.Model):
    _name = 'clickup.folder'
    _description = 'ClickUp Folder'

    name = fields.Char('Folder Name')
    folder_id = fields.Char('ClickUp Folder ID')
    space_id = fields.Many2one('clickup.space', string='ClickUp Space')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    def action_fetch_folders_from_clickup(self):
        for space in self:
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise ValueError("No ClickUp token found for this user.")

            headers = {"Authorization": f"Bearer {token.access_token}"}
            url = f"https://api.clickup.com/api/v2/space/{space.space_id}/folder"
            
            _logger.info("Fetching ClickUp Folders from Space ID: %s", space.space_id)
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                folders = response.json().get('folders', [])
                for folder in folders:
                    existing = self.env['clickup.folder'].sudo().search([('folder_id', '=', folder.get('id'))], limit=1)
                    if not existing:
                        self.env['clickup.folder'].sudo().create({
                            'name': folder.get('name'),
                            'folder_id': folder.get('id'),
                            'space_id': space.id,
                            'user_id': self.env.user.id,
                        })
                _logger.info("Saved %s folders from ClickUp", len(folders))
            else:
                raise ValueError("Failed to fetch folders from ClickUp.")
            
    def action_fetch_lists_from_folder(self):
        for folder in self:
            if not folder.folder_id:
                continue  # skip if no folder_id

            # Get token
            token = self.env['clickup.token'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
            if not token:
                raise UserError("❌ No ClickUp token found for this user.")

            headers = {
                "Authorization": f"Bearer {token.access_token}"
            }

            url = f"https://api.clickup.com/api/v2/folder/{folder.folder_id}/list"

            _logger.info("➡️ Fetching Lists from Folder ID: %s", folder.folder_id)
            _logger.info("➡️ URL: %s", url)

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                lists_data = response.json().get('lists', [])
                _logger.info("✅ %s Lists fetched", len(lists_data))

                for lst in lists_data:
                    existing_list = self.env['clickup.list'].sudo().search([('list_id', '=', lst.get('id'))], limit=1)
                    if not existing_list:
                        self.env['clickup.list'].sudo().create({
                            'name': lst.get('name'),
                            'list_id': lst.get('id'),
                            'folder_id': folder.id,
                            'user_id': self.env.user.id,
                        })
            else:
                raise UserError(f"❌ Failed to fetch Lists: {response.text}")
