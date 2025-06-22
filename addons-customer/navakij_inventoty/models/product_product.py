import logging
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.product'


    custom_reference = fields.Char(string='Custom Reference', copy=False)