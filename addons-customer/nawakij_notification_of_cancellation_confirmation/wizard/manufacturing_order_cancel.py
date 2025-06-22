import logging
import re

from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class ManufacturingOrderCancel(models.TransientModel):
    _name = 'manufacturing.order.cancel'

    mrp_production_id = fields.Many2one('mrp.production')


    def action_cancel(self):
        self.mrp_production_id.action_cancel(show_wizard=False)
