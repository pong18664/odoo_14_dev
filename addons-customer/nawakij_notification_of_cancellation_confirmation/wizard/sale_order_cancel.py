import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrderCancel(models.TransientModel):
    _inherit = 'sale.order.cancel'


    def action_cancel(self):
        return self.order_id.with_context({'disable_cancel_warning': True}).action_cancel(confirm_cancel=True)
    
