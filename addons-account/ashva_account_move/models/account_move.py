import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'



    @api.model
    def _get_invoice_in_payment_state(self):
        # OVERRIDE to enable the 'in_payment' state on invoices.
        return 'in_payment'
    

    def _track_subtype(self, init_values):
        # OVERRIDE to log a different message when an invoice is paid using SDD.
        self.ensure_one()
        if 'state' in init_values and self.state in ('in_payment', 'paid') and self.move_type == 'out_invoice' and self.sdd_mandate_id:
            return self.env.ref('account_sepa_direct_debit.sdd_mt_invoice_paid_with_mandate')
        return super(AccountMove, self)._track_subtype(init_values)

