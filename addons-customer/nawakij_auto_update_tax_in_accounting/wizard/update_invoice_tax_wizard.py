import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class UpdateInvoiceTaxWizard(models.TransientModel):
    _name = 'update.invoice.tax.wizard'
    _description = 'Wizard to update taxes on invoice lines'

    account_tax_id = fields.Many2one("account.tax", string="Tax", required=True)
    move_id = fields.Many2one("account.move", string="Invoice", required=True)

    def action_confirm(self):
        # function สำหรับอัพเดท tax ใน invoice lines
        for line in self.move_id.invoice_line_ids:
            line.tax_ids = [(6, 0, [self.account_tax_id.id])]  # Replace all tax_ids
        self.move_id._onchange_invoice_line_ids() # test function
        return {'type': 'ir.actions.act_window_close'}