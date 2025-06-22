import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class StockLocation(models.Model):
    _inherit = 'stock.location'


    show_location = fields.Boolean(string="Show Location", default=True)
                                                                    