import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'


    type_category = fields.Selection([('aluminium', 'Aluminium'), 
                                      ('aluminium sheet', 'Aluminium Sheet'),
                                      ('glass', 'Glass')], string="Category Type")


    


    


