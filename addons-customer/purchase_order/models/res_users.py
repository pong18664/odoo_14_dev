import logging
import re


from odoo import api, fields,tools, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'


    signature_image = fields.Image(string="Signature Image")

    


