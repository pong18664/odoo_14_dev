import logging
import re

from odoo import api, fields, tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    def action_open_update_tax_wizard(self):
            self.ensure_one()
            return {
                'name': 'Update Taxes',
                'type': 'ir.actions.act_window',
                'res_model': 'update.invoice.tax.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_move_id': self.id,
                },
            }
