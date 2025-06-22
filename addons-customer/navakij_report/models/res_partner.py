import logging
import re

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"


    name_company_partner_eng = fields.Char(string="Name")
    street_eng = fields.Char(string="Address")
    street2_eng = fields.Char(string="Street2")
    city_eng = fields.Char(string="city")
    contact = fields.Char(string="Contact")
    contact_mobile = fields.Char(string="Contact Mobile")
    signature_image = fields.Image(string="Signature Image")