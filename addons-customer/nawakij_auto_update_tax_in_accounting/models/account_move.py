import logging
import re

from odoo import api, fields, tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    def action_open_update_tax_wizard(self):
        """
        function สำหรับเปิด wizard 'update.invoice.tax.wizard'
        """
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
    

    # test function
    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        current_invoice_lines = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
        others_lines = self.line_ids - current_invoice_lines
        if others_lines and current_invoice_lines - self.invoice_line_ids:
            others_lines[0].recompute_tax_line = True
        self.line_ids = others_lines + self.invoice_line_ids
        self._onchange_recompute_dynamic_lines()
        # _logger.info
