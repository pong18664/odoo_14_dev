import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"


    name_company_eng = fields.Char(string="Name")
    street_eng = fields.Char(string="Address")
    street2_eng = fields.Char(string="Street2")
    city_eng = fields.Char(string="city")
    image = fields.Image(string="Image")