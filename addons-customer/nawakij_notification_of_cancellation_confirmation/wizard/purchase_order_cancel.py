import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrderCancel(models.TransientModel):
    _name = 'purchase.order.cancel'

    purchase_id = fields.Many2one('purchase.order')


    def action_cancel(self):
        self.purchase_id.button_cancel(show_wizard=False)
